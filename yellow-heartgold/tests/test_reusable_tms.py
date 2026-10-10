"""Execute native teaching: move/PP updates survive while no TM is removed."""
import struct,sys,unittest
from pathlib import Path
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from reusable_tms import patch,LEARN_MOVE,TAKE_ITEM

class ReusableTMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-015.nds'))
        cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-015.nds'))
        patch(cls.new)

    def test_native_teaching_keeps_each_tm_and_hm_and_updates_move_and_pp(self):
        for item,move,hm in ((115,117,False),(328,264,False),(361,351,False),(419,433,False),(420,15,True)):
            with self.subTest(item=item):
                c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x02000000,0x400000)
                c.mem_map(0x01FF8000,0x8000);c.mem_map(0x027E0000,0x1000)
                for s in self.new.loadArm9().sections:c.mem_write(s.ramAddress,bytes(s.data))
                party,args,mon,stop=0x02300000,0x02302000,0x02303000,0x023E0000
                c.mem_write(party+0x654,struct.pack('<I',args))
                c.mem_write(args+0x28,struct.pack('<2H',item,move))
                written={};removed=[];friendship=[]
                def hook(cpu,address,size,data):
                    r0=cpu.reg_read(UC_ARM_REG_R0)
                    if address==0x0206EC40:
                        key=cpu.reg_read(UC_ARM_REG_R1);p=cpu.reg_read(UC_ARM_REG_R2)
                        written[key]=struct.unpack('<I',cpu.mem_read(p,4))[0]
                    elif address==0x0207332C:cpu.reg_write(UC_ARM_REG_R0,20)
                    elif address==0x02078024:cpu.reg_write(UC_ARM_REG_R0,int(hm))
                    elif address==TAKE_ITEM:removed.append(item)
                    elif address==0x020828EC:cpu.reg_write(UC_ARM_REG_R0,140)
                    elif address==0x0206FE90:friendship.append(cpu.reg_read(UC_ARM_REG_R1))
                    elif address!=0x02097F0C:return
                    cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
                c.hook_add(UC_HOOK_CODE,hook)
                c.reg_write(UC_ARM_REG_R0,party);c.reg_write(UC_ARM_REG_R1,mon);c.reg_write(UC_ARM_REG_R2,2)
                c.reg_write(UC_ARM_REG_SP,0x023F0000);c.reg_write(UC_ARM_REG_LR,stop|1)
                c.emu_start(LEARN_MOVE|1,stop,count=1000)
                self.assertEqual(c.reg_read(UC_ARM_REG_PC),stop)
                self.assertEqual(written,{56:move,64:0,60:20})
                self.assertEqual(removed,[]);self.assertEqual(friendship,[4])

    def test_only_teaching_consumption_changes_and_other_item_paths_remain(self):
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        self.assertEqual([i for i,(x,y) in enumerate(zip(a,b)) if x!=y],list(range(0x825B4,0x825B8)))
        self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
        self.assertEqual(self.old.arm7,self.new.arm7)

if __name__=='__main__':unittest.main()
