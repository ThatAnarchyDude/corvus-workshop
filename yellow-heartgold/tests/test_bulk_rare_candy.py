"""Execute batch hooks in Thumb with native-service doubles."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_rom import PROJECT
from bulk_rare_candy import patch

class BulkCandyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        cls.report = patch(cls.rom)
        cls.state = int(cls.report['state'], 16)

    def machine(self):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x02000000, 0x400000)
        cpu.mem_map(0x01ff8000, 0x8000)
        cpu.mem_map(0x027e0000, 0x1000)
        for section in self.rom.loadArm9().sections:
            cpu.mem_write(section.ramAddress, bytes(section.data))
        cpu.reg_write(UC_ARM_REG_SP, 0x023f0000)
        cpu.reg_write(UC_ARM_REG_LR, 0x023e0001)
        return cpu

    def execute(self, cpu, routine):
        cpu.emu_start(int(self.report['routines'][routine],16)|1, 0x023e0000, count=10000)
        self.assertEqual(cpu.reg_read(UC_ARM_REG_PC), 0x023e0000)
        return cpu.reg_read(UC_ARM_REG_R0)

    def apply(self, start=5, requested=3, remaining=94, phase=2):
        cpu=self.machine();mon=0x02301000;bag=0x02302000;party=0x02303000
        cpu.mem_write(self.state,struct.pack('<6I',phase,requested,0,0,0,bag))
        cpu.mem_write(0x023f0000,struct.pack('<2I',1,12))
        for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(party,50,0,0)):
            cpu.reg_write(reg,value)
        calls=[];level=start;stock=remaining
        def hook(c,a,s,u):
            nonlocal level,stock
            r=[c.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if a==0x02074644:self.assertEqual(r[:2],[party,0]);result=mon
            elif a==0x0206e540:self.assertEqual(r[:2],[mon,161]);result=level
            elif a==0x02078550:self.assertEqual(r[:3],[bag,50,12]);result=stock
            elif a==0x02078434:
                self.assertEqual(r,[bag,50,1,12]);result=int(stock>0)
                if result:stock-=1;calls.append('take')
            elif a==0x020908ac:
                self.assertEqual(r,[party,50,0,0])
                self.assertEqual(bytes(c.mem_read(c.reg_read(UC_ARM_REG_SP),8)),struct.pack('<2I',1,12))
                level+=1;calls.append('use');result=1
            else:return
            c.reg_write(UC_ARM_REG_R0,result);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook);self.execute(cpu,'apply')
        return level,stock,calls,struct.unpack('<6I',cpu.mem_read(self.state,24))

    def test_three_candies_apply_before_move_processing(self):
        level,stock,calls,state=self.apply()
        self.assertEqual((level,stock),(8,92))
        self.assertEqual(calls,['use','take','use','take','use'])
        self.assertEqual(state[:4],(3,3,6,8))

    def test_level_cap_does_not_spend_unused_candies(self):
        self.assertEqual(self.apply(start=98,requested=95)[:2],(100,93))

    def test_inventory_cap_includes_first_already_consumed_candy(self):
        self.assertEqual(self.apply(requested=95,remaining=1)[:2],(7,0))

    def test_one_candy_and_ordinary_unselected_use(self):
        for options in ({'requested':1},{'phase':0}):
            self.assertEqual(self.apply(**options)[:3],(6,94,['use']))

    def test_scan_retains_move_replacement_cursor_and_scans_intermediate_levels(self):
        cpu=self.machine();mon=0x02301000;index=0x02302000;move=0x02302004
        cpu.mem_write(self.state,struct.pack('<6I',3,5,15,19,mon,0))
        visits=[]
        def hook(c,a,s,u):
            if a!=0x02071534:return
            scan=struct.unpack('<I',c.mem_read(self.state+8,4))[0]
            i=struct.unpack('<I',c.mem_read(index,4))[0]
            visits.append((scan,i))
            # Two move choices at level 15, then another at 19.
            result=65534 if scan==15 and i<2 else 75 if scan==19 and i==0 else 0
            if result:c.mem_write(index,struct.pack('<I',i+1))
            c.reg_write(UC_ARM_REG_R0,result);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        results=[]
        for _ in range(4):
            cpu.reg_write(UC_ARM_REG_SP,0x023f0000);cpu.reg_write(UC_ARM_REG_LR,0x023e0001)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(mon,index,move)):cpu.reg_write(reg,value)
            results.append(self.execute(cpu,'learn_moves'))
        self.assertEqual(results,[65534,65534,75,0])
        self.assertEqual(visits,[(15,0),(15,1),(15,2),(16,0),(17,0),(18,0),(19,0),(19,1)])

    def test_only_active_batch_mon_uses_scan_level(self):
        for phase,matched,expected in ((3,True,6),(0,True,8),(3,False,8)):
            cpu=self.machine();mon=0x02301000
            cpu.mem_write(self.state,struct.pack('<6I',phase,3,6,8,mon,0))
            cpu.reg_write(UC_ARM_REG_R0,mon if matched else mon+4);cpu.reg_write(UC_ARM_REG_R1,161)
            def hook(c,a,s,u):
                if a==0x0206e540:c.reg_write(UC_ARM_REG_R0,8);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            self.assertEqual(self.execute(cpu,'learn_level'),expected)

    def test_real_native_learnset_scan_preserves_intermediate_moves(self):
        import ndspy.narc
        cpu=self.machine();mon=0x02301000;index=0x02302000;move=0x02302004;buffer=0x02303000
        cpu.mem_write(self.state,struct.pack('<6I',3,5,15,19,mon,0))
        arc=ndspy.narc.NARC(self.rom.files[self.rom.filenames.idOf('a/0/3/3')])
        learnset=bytes(arc.files[1]);learned=[]
        def hook(c,a,s,u):
            r=[c.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
            if a==0x0201aa8c:result=buffer
            elif a==0x0206e540:result={5:1,112:0,161:19}[r[1]]
            elif a==0x02071fc8:
                self.assertEqual(r[:2],[1,0]);c.mem_write(r[2],learnset);result=0
            elif a==0x0207137c:
                self.assertEqual(r[0],mon);learned.append(r[1]);result=r[1]
            elif a==0x0201ab0c:result=0
            else:return
            c.reg_write(UC_ARM_REG_R0,result);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        results=[]
        for _ in range(8):
            cpu.reg_write(UC_ARM_REG_SP,0x023f0000);cpu.reg_write(UC_ARM_REG_LR,0x023e0001)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(mon,index,move)):cpu.reg_write(reg,value)
            result=self.execute(cpu,'learn_moves');results.append(result)
            if result==0:break
        expected=[entry&511 for entry, in struct.iter_unpack('<H',learnset) if entry!=65535 and 15<=entry>>9<=19]
        self.assertGreater(len(expected),0)
        self.assertEqual(learned,expected)
        self.assertEqual(results,expected+[0])

    def test_party_exit_clears_batch_except_move_replacement_transition(self):
        for action,expected in ((0,0),(5,3),(9,0)):
            cpu=self.machine();manager=0x02301000;stateptr=0x02302000;menu=0x02303000;args=0x02305000
            cpu.mem_write(self.state,struct.pack('<I',3))
            cpu.mem_write(menu+0x654,struct.pack('<I',args))
            cpu.mem_write(args+0x27,bytes([action]))
            cpu.reg_write(UC_ARM_REG_R0,manager);cpu.reg_write(UC_ARM_REG_R1,stateptr)
            def hook(c,a,s,u):
                if a==0x02079034:c.mem_write(stateptr,struct.pack('<I',32));result=0
                elif a==0x02007290:result=menu
                else:return
                c.reg_write(UC_ARM_REG_R0,result);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            self.assertEqual(self.execute(cpu,'party_cleanup'),0)
            self.assertEqual(struct.unpack('<I',cpu.mem_read(self.state,4))[0],expected)

    def picker(self, item=50, stock=5, action=None):
        cpu=self.machine();ctx=0x02301000;view=0x02303000;bag=0x02304000
        cpu.mem_write(ctx+0x234,struct.pack('<2I',view,bag))
        cpu.mem_write(ctx+0x314,struct.pack('<I',0x02305000))
        cpu.mem_write(view+0x66,struct.pack('<H',item))
        calls=[]
        services={0x021fff24,0x021fd574,0x02200300,0x021fedec,0x021ff7c4,0x021ff29c,
                  0x02200428,0x021ff834,0x021fed3c,0x02026380,0x021fd788}
        def hook(c,a,s,u):
            r=[c.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if a==0x02078550:self.assertEqual(r[:3],[bag,50,6]);result=stock
            elif a==0x0200bba0:result=0x02306000
            elif a==0x021fb688:calls.append(('use',));c.emu_stop();return
            elif a==0x021fbfc8:calls.append(('cancel_native',));c.emu_stop();return
            elif a in services:calls.append((hex(a),));result=0
            else:return
            c.reg_write(UC_ARM_REG_R0,result);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        cpu.reg_write(UC_ARM_REG_R0,ctx)
        if item==50:
            self.execute(cpu,'picker')
            self.assertEqual(struct.unpack('<2H',cpu.mem_read(ctx+0x680,4)),(1,stock))
            self.assertEqual(struct.unpack('<I',cpu.mem_read(ctx+0x314,4))[0],0x02306000)
            if action:
                cpu.mem_write(ctx+0x680,struct.pack('<H',3))
                cpu.reg_write(UC_ARM_REG_R0,ctx);cpu.reg_write(UC_ARM_REG_SP,0x023f0000);cpu.reg_write(UC_ARM_REG_LR,0x023e0001)
                cpu.emu_start(int(self.report['routines'][action],16)|1,0x023e0000,count=10000)
                self.assertEqual(struct.unpack('<I',cpu.mem_read(ctx+0x314,4))[0],0x02305000)
        else:
            cpu.emu_start(int(self.report['routines']['picker'],16)|1,0x023e0000,count=10000)
        return calls,struct.unpack('<6I',cpu.mem_read(self.state,24))

    def test_quantity_picker_works_even_with_one_candy(self):
        self.assertEqual(self.picker(stock=1)[1][0],1)

    def test_quantity_cancel_clears_request_and_restores_label(self):
        calls,state=self.picker(action='cancel')
        self.assertEqual(state[0],0)
        self.assertEqual(calls[-1],('cancel_native',))
        self.assertFalse(any(c[0]=='use' for c in calls))

    def test_quantity_confirm_goes_to_use_not_toss(self):
        calls,state=self.picker(action='confirm')
        self.assertEqual(state[:2],(2,3))
        self.assertEqual(calls[-1],('use',))
        self.assertFalse(any(c[0]==hex(0x021feea4) for c in calls))

    def test_potion_use_bypasses_quantity_picker(self):
        calls,state=self.picker(item=17)
        self.assertEqual(state[0],0)
        self.assertEqual(calls,[('use',)])

if __name__=='__main__':unittest.main()
