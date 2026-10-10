"""Execute progression paths and selective ARM hooks for prototype 010."""
import json
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
import ndspy.narc
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4, UC_ARM_REG_SP, UC_ARM_REG_LR
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from viridian_tutorial import (PROJECT, old_man, oak_parcel, DEX_HIDE, TUTORIAL_DONE,
                              BLOCKER_HIDE, PASSED_HIDE, props_init, CITY_MIGRATED)
from parcel_quest import PARCEL_STATE, BALLS_GIVEN
from test_parcel_quest import QuestRun
from prototype import decode_messages
from opening import events_decode, command
from parcel_quest import split_bank

class EventRun(QuestRun):
    def __init__(self,*a,z=7,**kw):
        super().__init__(*a,**kw);self.z=z;self.tutorials=0;self.visited=[]
    def read(self,fmt='H'):
        if self.variables.get(0x4001)==358:self.variables[0x4001]=self.z
        at=self.at;value=super().read(fmt);self.visited.append((at,value))
        if fmt=='H' and value==251:self.tutorials+=1;return 1
        return value

class ProgressionTests(unittest.TestCase):
    def test_coffee_blocks_until_parcel_and_dex_are_both_complete(self):
        for parcel,flags in [(0,set()),(1,set()),(2,set()),(1,{0x6B})]:
            r=EventRun(old_man(12),variables={PARCEL_STATE:parcel},flags=flags).run()
            self.assertEqual(r.tutorials,0);self.assertEqual(r.messages,[12]);self.assertNotIn(TUTORIAL_DONE,r.flags)
    def test_demo_runs_once_and_leaves_the_old_man_beside_the_path(self):
        r=EventRun(old_man(12),variables={PARCEL_STATE:2},flags={0x6B}).run()
        self.assertEqual(r.tutorials,1);self.assertIn(TUTORIAL_DONE,r.flags);self.assertIn(BLOCKER_HIDE,r.flags);self.assertNotIn(PASSED_HIDE,r.flags)
        r=EventRun(old_man(12),variables=r.variables,flags=r.flags).run()
        self.assertEqual(r.tutorials,0);self.assertEqual(r.messages,[])
    def test_talking_after_demo_gives_advice_without_replaying(self):
        r=EventRun(old_man(12,interaction=True),flags={TUTORIAL_DONE}).run()
        self.assertEqual(r.tutorials,0);self.assertEqual(r.messages,[16])
    def test_props_remain_until_oak_collects_them_and_then_dex_is_granted(self):
        for x,z in [(8,7),(7,6),(9,6),(8,5)]:
            r=EventRun(oak_parcel(35,52),variables={PARCEL_STATE:1},flags={0x6A},bag={459:1},x=x,z=z).run()
            self.assertEqual(r.variables[PARCEL_STATE],2);self.assertEqual(r.bag[459],0);self.assertIn(DEX_HIDE,r.flags);self.assertIn(0x6B,r.flags)
            grant=r.commands.index(291);self.assertEqual(r.commands[grant-5:grant],[101,101,94,95,104])
            movements=[value for at,value in r.visited if at>=2 and r.code[at-2:at]==command(94)]
            self.assertEqual(255 in movements,(x,z)==(8,5))
    def test_no_parcel_does_not_hide_props_or_grant_dex(self):
        r=EventRun(oak_parcel(35,52),flags={0x6A}).run()
        self.assertNotIn(DEX_HIDE,r.flags);self.assertNotIn(0x6B,r.flags);self.assertNotIn(291,r.commands)
    def test_ball_gift_remains_one_time_and_full_bag_retries(self):
        code=oak_parcel(35,52)
        r=EventRun(code,variables={PARCEL_STATE:2},flags={0x6A},full=True).run();self.assertNotIn(BALLS_GIVEN,r.flags)
        r=EventRun(code,variables={PARCEL_STATE:2},flags={0x6A}).run();self.assertEqual(r.bag[4],5)
        r=EventRun(code,variables=r.variables,flags=r.flags,bag=r.bag).run();self.assertEqual(r.bag[4],5)

@unittest.skipUnless((PROJECT/'build/viridian-tutorial-report.json').exists(),'Requires local prototype 010')
class BinaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-009.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-010.nds'))
        cls.report=json.loads((PROJECT/'build/viridian-tutorial-report.json').read_text());cls.main=cls.new.loadArm9()
    def archive(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files
    def test_original_map_models_scripts_and_johto_art_are_preserved(self):
        for p in ['a/0/8/1','a/0/0/6','a/0/1/2','a/0/3/2']:
            a,b=self.archive(self.old,p),self.archive(self.new,p);self.assertEqual(a,b[:len(a)])
        a,b=self.archive(self.old,'a/0/2/7'),self.archive(self.new,'a/0/2/7')
        for i,v in enumerate(a):
            if i!=445:self.assertEqual(v,b[i])
        self.assertEqual(decode_messages(a[445])[1],decode_messages(b[445])[1][:2])
        self.assertEqual(self.old.loadArm9Overlays()[53].data,self.new.loadArm9Overlays()[53].data)
        self.assertEqual(self.old.arm7,self.new.arm7)
    def test_only_lab_and_viridian_headers_change(self):
        a=self.old.loadArm9().sections[0].data;b=self.main.sections[0].data
        for m in range(540):
            if m not in [50,505]:self.assertEqual(a[0xF6BE0+m*24:0xF6BE0+(m+1)*24],b[0xF6BE0+m*24:0xF6BE0+(m+1)*24])
    def test_ball_message_change_does_not_change_blue_dialogue(self):
        old=self.old.loadArm9().sections[0].data;new=self.main.sections[0].data
        for r,d in [(self.old,old),(self.new,new)]:
            sid,_,tid=struct.unpack_from('<3H',d,0xF6BE0+505*24+6);bank=split_bank(self.archive(r,'a/0/1/2')[sid]);msg=decode_messages(self.archive(r,'a/0/2/7')[tid])[1]
            if r is self.old:before_msg=msg[19];before_rival=bank[11]
            else:
                self.assertEqual(msg[19],before_msg);self.assertEqual(bank[11],before_rival)
                for i in [15,16,17]:self.assertNotIn(command(45)+bytes([19]),bank[i])
    def execute(self,which,enabled,r0=1,r1=0):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x400000)
        cpu.mem_write(self.main.sections[1].ramAddress,bytes(self.main.sections[1].data));cpu.mem_write(int(self.report['hooks']['mode_flag'],16),struct.pack('<I',enabled))
        native=0x0207280C if which=='back_hook' else 0x0200BB6C;cpu.mem_write(native,b'\x70\x47');calls=[];stop=0x023F0000
        def hook(c,at,size,data):
            if at==stop:c.emu_stop()
            elif at==native:
                calls.append((c.reg_read(UC_ARM_REG_R0),c.reg_read(UC_ARM_REG_R1)))
                if which=='back_hook':c.reg_write(UC_ARM_REG_R0,9)
        cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_R0,r0);cpu.reg_write(UC_ARM_REG_R1,r1);cpu.reg_write(UC_ARM_REG_R4,0x12345678);cpu.reg_write(UC_ARM_REG_SP,0x023E0000);cpu.reg_write(UC_ARM_REG_LR,stop|1)
        cpu.emu_start(int(self.report['hooks'][which],16)|1,stop+2,count=100)
        self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x023E0000);self.assertEqual(cpu.reg_read(UC_ARM_REG_R4),0x12345678)
        return cpu.reg_read(UC_ARM_REG_R0),calls
    def test_back_hook_preserves_johto_and_uses_old_man_only_when_enabled(self):
        self.assertEqual(self.execute('back_hook',0),(9,[(1,0)]))
        self.assertEqual(self.execute('back_hook',1),(17,[]))
    def test_name_hook_preserves_original_tutorial_names(self):
        for index in [0,1]:
            self.assertEqual(self.execute('name_hook',0,r1=index)[1],[(1,index)])
            self.assertEqual(self.execute('name_hook',1,r1=index)[1],[(1,2)])
    def test_dummy_dispatch_sets_clears_and_limits_the_demo_mode(self):
        for mode in [0,2,5,6,7]:
            with self.subTest(mode=mode):
                cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x400000)
                cpu.mem_write(self.main.sections[1].ramAddress,bytes(self.main.sections[1].data))
                flag=int(self.report['hooks']['mode_flag'],16);cpu.mem_write(flag,struct.pack('<I',1))
                ctx,fs,obj0,obj1,stop=0x02300000,0x02301000,0x02302000,0x02303000,0x023F0000
                cpu.mem_write(ctx+128,struct.pack('<I',fs));previous=int(self.report['hooks']['previous_dummy'],16)&~1
                for at in [0x020403AC,0x02041C70]:cpu.mem_write(at,b'\x70\x47')
                cpu.mem_write(previous,b'\x00\x20\x70\x47')
                calls=[]
                def hook(c,at,size,data):
                    if at==stop:c.emu_stop()
                    elif at==0x020403AC:c.reg_write(UC_ARM_REG_R0,mode)
                    elif at==previous:calls.append(('delegate',c.reg_read(UC_ARM_REG_R0)))
                    elif at==0x02041C70:
                        ident=c.reg_read(UC_ARM_REG_R1);calls.append(('object',ident));c.reg_write(UC_ARM_REG_R0,{10:obj0,11:obj1}.get(ident,0))
                cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_R0,ctx);cpu.reg_write(UC_ARM_REG_SP,0x023E0000);cpu.reg_write(UC_ARM_REG_LR,stop|1)
                cpu.emu_start(int(self.report['hooks']['dummy'],16)|1,stop+2,count=400)
                self.assertEqual(struct.unpack('<I',cpu.mem_read(flag,4))[0],0 if mode==6 else 1)
                self.assertEqual(('delegate',ctx) in calls,mode in [0,2])
                self.assertEqual([v for k,v in calls if k=='object'],[10,11] if mode in [2,7] else [])
                if mode in [2,7]:
                    for obj in [obj0,obj1]:self.assertEqual(struct.unpack('<I',cpu.mem_read(obj+140,4))[0],0x10000)
                self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x023E0000)
