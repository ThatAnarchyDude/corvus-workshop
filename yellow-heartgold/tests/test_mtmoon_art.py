"""Native art registration, renderer data and isolated trainer-class execution."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
import ndspy.narc
import ndspy.texture
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon import patch as cave
from mtmoon_story import patch as story
from mtmoon_center import patch as center
from bulk_rare_candy import patch as candy
from mtmoon_tms import patch as tms
from mtmoon_items import patch as items
from mtmoon_rockets import patch as rockets
from mtmoon_encounters import patch as encounters
from mtmoon_art import patch,CLASS,SPRITES,GENDER,PAYOUT,INTRO,battle_image
from prototype import decode_messages
from opening import events_decode,encode_text
from parcel_quest import PH
from viridian_tutorial import TABLE


class MtMoonArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        for apply in (cave,story,center,candy,tms,items,rockets,encounters):apply(cls.old)
        cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)
        cls.sections={key:[(s.ramAddress,bytes(s.data)) for s in rom.loadArm9().sections[:2]] for key,rom in [('old',cls.old),('new',cls.new)]}
        cls.overlays={key:rom.loadArm9Overlays()[12] for key,rom in [('old',cls.old),('new',cls.new)]}

    def arc(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def cpu(self,key):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x400000)
        for address,data in self.sections[key]:cpu.mem_write(address,data)
        o=self.overlays[key];cpu.mem_write(o.ramAddress,bytes(o.data));return cpu

    def test_gender_and_money_hooks_preserve_all_other_classes(self):
        for key in ('old','new'):
            cpu=self.cpu(key);values=[]
            for trainer_class in range(256):
                cpu.reg_write(UC_ARM_REG_R0,trainer_class);cpu.reg_write(UC_ARM_REG_LR,0x023F0001)
                cpu.emu_start(GENDER|1,0x023F0000,count=80);values.append(cpu.reg_read(UC_ARM_REG_R0))
            if key=='old':old=values
            else:self.assertEqual(values,old[:129]+[0]+old[130:])
        for trainer_class in range(256):
            cpu=self.cpu('new');cpu.mem_write(0x023E0000,bytes([0,trainer_class]))
            cpu.reg_write(UC_ARM_REG_R0,0x023E0000);cpu.reg_write(UC_ARM_REG_R3,0xDEADBEEF)
            cpu.emu_start(PAYOUT|1,PAYOUT+4,count=80)
            self.assertEqual(cpu.reg_read(UC_ARM_REG_R2),55 if trainer_class==CLASS else trainer_class)
            self.assertEqual(cpu.reg_read(UC_ARM_REG_R1),0x0226C4C4)
            self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),0x023E0000);self.assertEqual(cpu.reg_read(UC_ARM_REG_R3),0xDEADBEEF)

    def test_original_models_trainers_and_class_names_preserved(self):
        for path in ('a/0/8/1','a/0/5/8'):
            before,after=self.arc(self.old,path),self.arc(self.new,path)
            self.assertEqual(before,after[:len(before)])
        before,after=self.arc(self.old,'a/0/5/5'),self.arc(self.new,'a/0/5/5')
        row=bytearray(before[777]);row[1]=CLASS
        self.assertEqual(after[777],bytes(row));after[777]=before[777];self.assertEqual(before,after)
        for bank in (730,731):
            before,after=[decode_messages(self.arc(r,'a/0/2/7')[bank])[1] for r in (self.old,self.new)]
            self.assertEqual(before,after[:len(before)]);self.assertEqual(len(after),130)
            self.assertEqual(after[129],decode_messages(encode_text(['JESSIE & JAMES'],PH))[1][0])
        names=decode_messages(self.arc(self.new,'a/0/2/7')[729])[1]
        self.assertEqual(names[777],[0xFFFF])
        for path in ('a/0/4/1','a/0/6/5','a/0/5/6','a/0/3/7'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(path)],self.new.files[self.new.filenames.idOf(path)])

    def test_rocket_music_and_transition_preserve_every_other_class(self):
        results={}
        for key in ('old','new'):
            cpu=self.cpu(key);values=[]
            for trainer_class in range(256):
                cpu.reg_write(UC_ARM_REG_R0,trainer_class);cpu.reg_write(UC_ARM_REG_LR,0x023F0001)
                cpu.emu_start(INTRO|1,0x023F0000,count=600);values.append(cpu.reg_read(UC_ARM_REG_R0))
            results[key]=values
        self.assertEqual(results['new'],results['old'][:129]+[29]+results['old'][130:])
        self.assertEqual(results['new'][129],results['old'][55])

    def test_actor_lookup_and_native_textures_are_complete(self):
        models=self.arc(self.new,'a/0/8/1')
        for name,record in self.report['actor_models'].items():
            tex=ndspy.texture.NSBTX(models[record['model']])
            self.assertEqual(len(tex.textures),16 if name in ('jessie','james') else 1)
            self.assertEqual(len(tex.palettes[0][1].colors),16)
            for _,texture in tex.textures:
                self.assertTrue(texture.isColor0Transparent)
                self.assertEqual(len(texture.data1),texture.width*texture.height//2)
                self.assertTrue(any(texture.data1))
        main=self.new.loadArm9();address=int(self.report['lookup'],16);at=address-main.sections[1].ramAddress
        data=main.sections[1].data;rows=[]
        while struct.unpack_from('<H',data,at)[0]!=65535:rows.append(struct.unpack_from('<3H',data,at));at+=6
        for record in self.report['actor_models'].values():self.assertIn((record['sprite'],record['model'],0),rows)
        d=main.sections[0].data;eid=struct.unpack_from('<H',d,TABLE+107*24+16)[0]
        actors={struct.unpack_from('<H',r)[0]:struct.unpack_from('<H',r,2)[0] for r in events_decode(self.arc(self.new,'a/0/3/2')[eid])[1]}
        self.assertEqual([actors[i] for i in (22,23,30,31)],[94,93,91,92])

    def test_battle_sprite_raw_and_encrypted_frames_share_palette(self):
        pixels,words=battle_image();self.assertEqual(len(pixels),6400);self.assertEqual(len(words),16)
        resources=self.arc(self.new,'a/0/5/8');base=CLASS*5
        self.assertEqual(len(resources[base][48:]),3200)
        self.assertEqual(struct.unpack('<16H',resources[base+1][40:72]),tuple(words))
        values=list(struct.unpack('<3200H',resources[base+4][48:]));seed=values[0]
        for n in range(3200):values[n]^=seed&65535;seed=(seed*1103515245+24691)&0xFFFFFFFF
        raw=struct.pack('<3200H',*values);actual=bytes(v for byte in raw for v in (byte&15,byte>>4))
        self.assertEqual(actual,b''.join(pixels[y*80:y*80+80]*2 for y in range(80)))
