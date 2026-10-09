"""Validate the intro's Nitro resources, isolated edits, and sound hook ABI."""
import json
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
import ndspy.fnt
import ndspy.narc
import ndspy.lz10
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from intro_polish import PROJECT, anim_decode, extract_blue, eevee_art

@unittest.skipUnless((PROJECT/'build/intro-polish-report.json').exists(), 'Requires local intro build')
class IntroChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-008.nds'))
        cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-009.nds'))
        cls.report=json.loads((PROJECT/'build/intro-polish-report.json').read_text())
    def archive(self,rom,path):
        return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files
    def test_gameplay_and_johto_are_unchanged(self):
        expected={self.old.filenames.idOf(x) for x in ['a/1/2/0']};expected.add(53)
        self.assertEqual({i for i,(a,b) in enumerate(zip(self.old.files,self.new.files)) if a!=b},expected)
        self.assertEqual(self.old.arm9,self.new.arm9);self.assertEqual(self.old.arm7,self.new.arm7)
        self.assertEqual(ndspy.fnt.save(self.old.filenames),ndspy.fnt.save(self.new.filenames))
    def test_full_blue_art_preserved_and_keyboard_unchanged(self):
        art,palette=extract_blue(PROJECT/'build/firered-source.gba')
        arc=self.archive(self.new,'a/1/2/0');char,pal=self.report['overlay']['blue_pic_ids']
        self.assertEqual(arc[char][48:],bytes(1024)+art+bytes(1024))
        self.assertEqual(arc[pal][40:72],palette)
        file=self.old.filenames.idOf('a/0/3/1')
        self.assertEqual(self.old.files[file],self.new.files[file])
    def test_ball_and_original_animations_survive(self):
        old=self.archive(self.old,'a/1/2/0');new=self.archive(self.new,'a/1/2/0')
        self.assertEqual(new[64][48:48+4480],old[64][48:])
        _,_,offset=struct.unpack_from('<HHI',old[65],48+16*2);ball=old[65][96+offset:96+offset+6]
        count=struct.unpack_from('<H',new[65],24)[0];_,_,offset=struct.unpack_from('<HHI',new[65],48+8*2)
        self.assertEqual(new[65][48+count*8+offset:48+count*8+offset+6],ball)
        a,b=anim_decode(old[66]),anim_decode(new[66])
        for i in [0,1,3]:self.assertEqual(a[i],b[i])
        self.assertEqual(b[2][2],1);self.assertEqual(sum(t for _,t in b[2][3]),40)
    def test_shiny_palette_is_native_and_starters_unchanged(self):
        _,palette=eevee_art(self.old);old=self.archive(self.old,'a/1/2/0');new=self.archive(self.new,'a/1/2/0')
        self.assertEqual(new[63][40:68],palette[:28]);self.assertEqual(new[63][72:],old[63][72:])
    def test_cry_and_sparkle_hook_preserves_stack_and_registers(self):
        overlay=self.new.loadArm9Overlays()[53];cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        cpu.mem_map(0x02000000,0x400000);cpu.mem_write(overlay.ramAddress,bytes(overlay.data))
        for at in [0x02006218,0x0200604C]:cpu.mem_write(at,b'\x70\x47')
        calls=[];stop=0x023F0000
        def hook(c,at,size,data):
            if at in [0x02006218,0x0200604C]:calls.append((at,c.reg_read(UC_ARM_REG_R0),c.reg_read(UC_ARM_REG_R1)))
            if at==stop:c.emu_stop()
        cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_R0,133);cpu.reg_write(UC_ARM_REG_R1,0)
        cpu.reg_write(UC_ARM_REG_R4,0x12345678);cpu.reg_write(UC_ARM_REG_SP,0x023E0000);cpu.reg_write(UC_ARM_REG_LR,stop|1)
        cpu.emu_start(int(self.report['overlay']['release_helper'],16)|1,stop+2,count=100)
        self.assertEqual(calls,[(0x02006218,133,0),(0x0200604C,1808,0)])
        self.assertEqual(cpu.reg_read(UC_ARM_REG_R4),0x12345678);self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x023E0000)
    def test_rival_prompt_cancel_rename_and_confirmation_paths(self):
        overlay=self.new.loadArm9Overlays()[53];start=int(self.report['overlay']['rival_helper'],16)
        native=[0x021E66E8,0x021E611C,0x020263AC,0x0200724C,0x021E6F9C,0x021E80B8]
        for state,phase,cancel,cursor,printed,want_state,want_phase in [
            (103,0,0,0,0,103,3),(103,3,0,0,1,131,1),
            (131,1,0,0,0,132,1),(132,1,1,0,0,131,1),
            (132,1,0,0,0,97,1),(99,1,0,0,0,100,2),
            (99,1,0,1,0,131,1),(100,2,0,0,0,100,4),
            (17,0,0,0,0,17,0)]:
            with self.subTest(state=state,phase=phase,cancel=cancel,cursor=cursor):
                cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x02000000,0x400000)
                cpu.mem_write(overlay.ramAddress,bytes(overlay.data));ctx,args,stop=0x02300000,0x02301000,0x023F0000
                cpu.mem_write(ctx+12,struct.pack('<2I',state,phase));cpu.mem_write(ctx+0x124,struct.pack('<I',args))
                cpu.mem_write(args+20,struct.pack('<I',cancel));cpu.mem_write(ctx+0x163,bytes([cursor]))
                for at in native:cpu.mem_write(at,b'\x70\x47')
                calls=[]
                def hook(c,at,size,data):
                    if at==stop:c.emu_stop();return
                    if at not in native:return
                    calls.append((at,c.reg_read(UC_ARM_REG_R0),c.reg_read(UC_ARM_REG_R1)))
                    if at==0x021E611C:c.reg_write(UC_ARM_REG_R0,printed)
                    elif at==0x0200724C:c.reg_write(UC_ARM_REG_R0,0x02303000)
                    elif at==0x021E6F9C and struct.unpack('<I',c.mem_read(ctx+12,4))[0]==96:
                        c.mem_write(ctx+12,struct.pack('<I',97))
                cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_R0,ctx)
                cpu.reg_write(UC_ARM_REG_SP,0x023E0000);cpu.reg_write(UC_ARM_REG_LR,stop|1)
                cpu.emu_start(start|1,stop+2,count=500)
                self.assertEqual(struct.unpack('<2I',cpu.mem_read(ctx+12,8)),(want_state,want_phase))
                self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x023E0000)
                if state==132 and not cancel:
                    self.assertEqual(struct.unpack('<I',cpu.mem_read(ctx+0x170,4))[0],64)
                    self.assertIn((0x021E80B8,ctx,3),calls)
                if state==100:self.assertIn((0x021E66E8,ctx,1),calls)
