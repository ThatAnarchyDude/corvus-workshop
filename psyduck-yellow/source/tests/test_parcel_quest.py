"""Execute quest bytecode and its Thumb Dex gate with native API stubs."""
import json
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
import ndspy.narc
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from parcel_quest import (PROJECT, PARCEL_STATE, SHOES_STATE, CLERK_STATE,
                         BALLS_GIVEN, QUEST_INIT, PARCEL_ITEM, SHOES_ITEM, oak_parcel,
                         cashier_escort, mom_scene, dex_gate, town_reload, walking_paths)
from escort import ball_choice


class QuestRun:
    def __init__(self, code, *, variables=None, flags=None, bag=None, full=False, x=1040):
        self.code=code;self.at=0;self.variables=dict(variables or {})
        self.flags=set(flags or []);self.bag=dict(bag or {})
        self.full=full;self.x=x;self.cmp=0;self.commands=[];self.messages=[]
    def read(self,fmt='H'):
        value=struct.unpack_from('<'+fmt,self.code,self.at)[0]
        self.at+=struct.calcsize('<'+fmt);return value
    def run(self):
        v=self.variables
        for _ in range(1000):
            op=self.read();self.commands.append(op)
            if op==2:return self
            if op in (1,50,53,77,79,82,95,96,97,104,175,282,291,293):continue
            if op in (190,191,45):
                value=self.read('B')
                if op==45:self.messages.append(value)
                continue
            if op==17:
                left,right=self.read(),self.read();a=v.get(left,0)
                self.cmp=(a>right)-(a<right);continue
            if op in (22,28):
                condition=self.read('B') if op==28 else None;distance=self.read('i')
                if condition is None or [self.cmp<0,self.cmp==0,self.cmp>0,
                    self.cmp<=0,self.cmp>=0,self.cmp!=0][condition]:self.at+=distance
                continue
            if op in (30,31,32):
                flag=self.read()
                if op==30:self.flags.add(flag)
                elif op==31:self.flags.discard(flag)
                else:self.cmp=0 if flag in self.flags else 1
                continue
            if op==41:
                target,value=self.read(),self.read();v[target]=value;continue
            if op==105:
                v[self.read()]=self.x;v[self.read()]=358;continue
            if op in (20,73,78,80,81,100,101):self.read();continue
            if op==94:self.read();self.read('i');continue
            if op==174:
                for _ in range(4):self.read()
                continue
            if op==176:
                for _ in range(5):self.read()
                continue
            if op==477:self.read('B');v[self.read()]=1;continue
            if op==669:
                item=self.read();v[self.read()]=self.bag.get(item,0);continue
            if op in (125,126):
                item,qty,result=self.read(),self.read(),self.read();old=self.bag.get(item,0)
                ok=not self.full if op==125 else old>=qty;v[result]=int(ok)
                if ok:self.bag[item]=old+qty if op==125 else old-qty
                continue
            raise AssertionError((op,self.at-2))
        raise AssertionError('Quest failed to terminate')


class ParcelChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=PROJECT/'build/yellow-heartgold-prototype-006.nds'
        cls.paths=walking_paths(ndspy.rom.NintendoDSRom.fromFile(str(source)))
    def test_center_override_targets_the_native_pc_metatile(self):
        from opening import events_decode
        rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-007.nds'))
        arm=rom.loadArm9().sections[0].data;header=0xF6BE0+501*24
        event=struct.unpack_from('<H',arm,header+16)[0]
        groups=events_decode(ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')]).files[event])
        pc=groups[0][-1]
        self.assertEqual(struct.unpack('<HHiiiH2x',pc),(11,0,11,12,0,0))
        matrices=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')])
        matrix=matrices.files[struct.unpack_from('<H',arm,header+4)[0]]
        land=struct.unpack_from('<H',matrix,len(matrix)-2)[0]
        raw=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')]).files[land]
        self.assertEqual(struct.unpack_from('<H',raw,20+2*(12*32+11))[0]&255,0x83)
        self.assertEqual(struct.unpack_from('<2i',groups[0][0],4),(4,8))

    def test_state_fits_native_save_and_does_not_overlap_pc(self):
        states=[PARCEL_STATE,SHOES_STATE,CLERK_STATE]
        self.assertEqual(len(set(states)),3)
        self.assertTrue(all(0x4000<=v<0x4170 for v in states))
        self.assertTrue(all(v not in range(0x4152,0x4169) for v in states))
    def test_shoes_granted_once_and_full_bag_can_retry(self):
        code=mom_scene(20,self.paths['mom'])
        full=QuestRun(code,flags=[0x6A],full=True).run()
        self.assertNotIn(293,full.commands)
        self.assertNotIn(SHOES_STATE,full.variables)
        got=QuestRun(code,flags=[0x6A]).run()
        self.assertEqual(got.bag,{SHOES_ITEM:1})
        self.assertEqual(got.variables[SHOES_STATE],1)
        again=QuestRun(code,flags=got.flags,variables=got.variables,bag=got.bag).run()
        self.assertEqual(again.bag,got.bag)
        self.assertNotIn(125,again.commands)
    def test_cashier_escorts_before_explanation_and_never_gives_dex(self):
        for x in (1036,1037):
            run=QuestRun(cashier_escort(self.paths['cashier']),variables={SHOES_STATE:1},x=x).run()
            self.assertEqual(run.bag,{PARCEL_ITEM:1})
            self.assertEqual(run.variables[PARCEL_STATE],1)
            self.assertEqual(run.variables[CLERK_STATE],2)
            self.assertLess(run.commands.index(176),run.commands.index(125))
            self.assertNotIn(291,run.commands)
            self.assertNotIn(477,run.commands)
    def test_parcel_delivery_required_then_grants_national_dex_once(self):
        code=oak_parcel(40)
        empty=QuestRun(code,flags=[0x6A]).run()
        self.assertNotIn(291,empty.commands)
        got=QuestRun(code,flags=[0x6A],bag={PARCEL_ITEM:1},variables={PARCEL_STATE:1}).run()
        self.assertEqual(got.bag[PARCEL_ITEM],0)
        self.assertEqual(got.variables[PARCEL_STATE],2)
        self.assertIn(0x6B,got.flags)
        self.assertIn(477,got.commands)
        second=QuestRun(code,flags=got.flags,variables=got.variables,bag=got.bag).run()
        self.assertNotIn(291,second.commands)
        self.assertEqual(second.bag[4],5)
        third=QuestRun(code,flags=second.flags,variables=second.variables,bag=second.bag).run()
        self.assertEqual(third.bag[4],5)
    def test_import_initializes_only_quest_state(self):
        old={SHOES_STATE:1,PARCEL_STATE:1,CLERK_STATE:9,0x4153:37}
        run=QuestRun(dex_gate(),variables=old).run()
        self.assertEqual(run.variables[SHOES_STATE],0)
        self.assertEqual(run.variables[PARCEL_STATE],0)
        self.assertEqual(run.variables[CLERK_STATE],0)
        self.assertEqual(run.variables[0x4153],37)
        self.assertIn(QUEST_INIT,run.flags)

    def test_old_pallet_save_gets_mom_without_duplicating_existing_actors(self):
        migrated=QuestRun(town_reload(),flags=[0x6A]).run()
        self.assertIn(100,migrated.commands)
        regular=QuestRun(town_reload(),flags=[0x6A,QUEST_INIT]).run()
        self.assertNotIn(100,regular.commands)
        no_starter=QuestRun(town_reload()).run()
        self.assertNotIn(100,no_starter.commands)

    def test_dex_gate_preserves_completed_quest(self):
        self.assertNotIn(1,QuestRun(dex_gate(),variables={PARCEL_STATE:2},flags=[0x6B,QUEST_INIT]).run().commands)
        early=QuestRun(dex_gate(),flags=[0x6B]).run()
        self.assertNotIn(0x6B,early.flags)
        self.assertIn(1,early.commands)
    def test_starter_choices_do_not_grant_dex(self):
        # Decode assembled commands rather than searching potentially overlapping bytes.
        for i in range(3):
            self.assertLess(len(ball_choice(i,grant_dex=False)),len(ball_choice(i)))
    def test_escort_paths_keep_player_one_tile_behind(self):
        for route in self.paths['cashier'].values():
            path=route['escort']
            self.assertEqual(path[-1],(1042,253))
            self.assertEqual(path[-2],(1042,254))
            self.assertTrue(all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(path,path[1:])))


class NativeDexGateChecks(unittest.TestCase):
    def test_mode_four_hides_access_preserving_records_and_native_modes(self):
        rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-007.nds'))
        main=rom.loadArm9();report=json.loads((PROJECT/'build/parcel-report.json').read_text())
        for mode in [0,1,2,3,4]:
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x120000);cpu.mem_map(0x02300000,0x20000)
            for section in main.sections[:2]:cpu.mem_write(section.ramAddress,bytes(section.data))
            ctx,fs,save,dex=0x02300000,0x02301000,0x02302000,0x02303000
            cpu.mem_write(ctx+128,struct.pack('<I',fs));cpu.mem_write(fs+12,struct.pack('<I',save))
            before=bytes((i%251) for i in range(0x338));cpu.mem_write(dex,before)
            calls=[]
            def hook(uc,address,size,_):
                if address==0x020FF000:uc.emu_stop();return
                if address==0x01FF8620:
                    calls.append(('fallback',uc.reg_read(UC_ARM_REG_R0)));uc.emu_stop();return
                if address==0x020403AC:result=mode
                elif address==0x0202A634:
                    self.assertEqual(uc.reg_read(UC_ARM_REG_R0),save);result=dex
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(UC_ARM_REG_SP,0x0231F000);cpu.reg_write(UC_ARM_REG_LR,0x020FF001);cpu.reg_write(UC_ARM_REG_R0,ctx)
            cpu.reg_write(UC_ARM_REG_R4,44);cpu.reg_write(UC_ARM_REG_R5,55)
            cpu.emu_start(int(report['dex_gate_hook'],16)|1,0x020FF000,count=1000)
            after=bytes(cpu.mem_read(dex,len(before)))
            self.assertEqual(after,before[:-2]+b'\0\0' if mode==4 else before)
            self.assertEqual(calls,[] if mode==4 else [('fallback',ctx)])
            self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x0231F000)
            self.assertEqual(cpu.reg_read(UC_ARM_REG_R4),44);self.assertEqual(cpu.reg_read(UC_ARM_REG_R5),55)


if __name__=='__main__':unittest.main()
