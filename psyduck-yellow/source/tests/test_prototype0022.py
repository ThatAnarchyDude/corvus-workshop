import sys,struct,unittest,os
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from opening import Script
from player_pc import script,SLOTS,INIT,EVOLUTION_INIT
from test_player_pc_storage import StorageRun
from test_prototype0021 import run
from pewter_gym import brock_script

class Checkpoint(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0022_ROM','build/0022-development-4.nds')));cls.main=cls.rom.loadArm9()
 def test_brock_reward_is_not_repeated_after_recovered_marker(self):
  result=run(brock_script(753,752),badge=True,flags={0xB22},bag={115:2})
  self.assertEqual(result['bag'],{115:2});self.assertEqual(result['messages'],[7])
 def test_compiler_rejects_persistent_overflow(self):
  for op in (30,31,32):
   with self.assertRaises(ValueError):Script().emit(op,0xB60)
 def test_friendship_pc_migration_and_repeat(self):
  for already in (False,True):
   test=StorageRun([1],variables={INIT:1,EVOLUTION_INIT:7},flags={0xB3B,0xA8C} if already else {0xB3B})
   test.code=script(evolution_items=True,shiny_charm=True,friendship_charm=True);test.run()
   stored=[(test.variables.get(i,0),test.variables.get(q,0)) for i,q in SLOTS]
   self.assertEqual(stored.count((121,1)),0 if already else 1)
   self.assertIn(0xA8C,test.flags)
 def test_friendship_pc_full_keeps_existing_storage_and_retries(self):
  v={INIT:1,EVOLUTION_INIT:7}
  for (i,q) in SLOTS:v[i]=50;v[q]=95
  test=StorageRun([1],variables=v,flags={0xB3B});test.code=script(evolution_items=True,shiny_charm=True,friendship_charm=True);test.run()
  self.assertNotIn(0xA8C,test.flags)
  for i,q in SLOTS:self.assertEqual((test.variables[i],test.variables[q]),(50,95))
 def test_passive_friendship_skips_eggs_and_already_maximum(self):
  for owned in (False,True):
   c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
   for s in self.main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
   blocks={1:0x02310000,2:0x02311000,3:0x02320000,4:0x02330000,6:0x02340000}
   c.mem_write(blocks[4]+0x431,bytes([8]));c.mem_write(blocks[2]+4,struct.pack('<I',3))
   if owned:c.mem_write(blocks[3]+660,struct.pack('<HH',121,1))
   values=[20,255,0];eggs=[False,False,True];changes=[]
   def hook(c,a,size,_):
    r0,r1,r2=[c.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if a==0x020272C8:result=blocks[r1]
    elif a==0x02074644:result=0x02350000+236*r1
    elif a==0x0206E540:
     index=(r0-0x02350000)//236;result=int(eggs[index]) if r1==76 else values[index]
    elif a==0x0206EC40:
     self.assertEqual(r1,9);value=struct.unpack('<I',c.mem_read(r2,4))[0];changes.append(((r0-0x02350000)//236,value));result=0
    else:return
    c.reg_write(UC_ARM_REG_R0,result);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
   c.hook_add(UC_HOOK_CODE,hook);c.reg_write(UC_ARM_REG_SP,0x023F8000);c.reg_write(UC_ARM_REG_LR,0x023FF001);c.reg_write(UC_ARM_REG_R0,0x02300000)
   c.emu_start(0x020503D1,0x023FF000,count=10000)
   self.assertEqual(changes,[(0,255)] if owned else []);self.assertEqual(c.reg_read(UC_ARM_REG_R0),blocks[4])
 def test_trainer_card_initializes_kanto_page_for_either_previous_region(self):
  o=self.rom.loadArm9Overlays()[51]
  for previous in (0,1):
   c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x021E5000,0x10000);c.mem_map(0x02300000,0x10000);c.mem_write(o.ramAddress,bytes(o.data))
   work,args=0x02300000,0x02308000;c.mem_write(work+0xE8,struct.pack('<I',args));c.mem_write(args+0x33,bytes([previous]));c.reg_write(UC_ARM_REG_R4,work)
   c.emu_start(0x021E5B97,0x021E5BDC,count=100)
   self.assertEqual(c.mem_read(work+0x343A,1)[0]&1,1)

if __name__=='__main__':unittest.main()
