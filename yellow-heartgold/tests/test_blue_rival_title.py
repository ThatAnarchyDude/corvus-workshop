import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from blue_rival_title import code,READ_MESSAGE,FLAG_BYTE_OFFSET,LABEL_INDEX
class BlueTitleTests(unittest.TestCase):
 def execute(self,trainer_class,clear=False,present=True):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x200000);cpu.mem_map(0x02300000,0x20000)
  address=0x01FFCD2C;save_pointer=0x021D2228;save=0x02310000;state=0x02300000
  cpu.mem_write(address,code(address,save_pointer));cpu.mem_write(save_pointer,struct.pack('<I',save if present else 0));cpu.mem_write(state+FLAG_BYTE_OFFSET,bytes([0x83|(16 if clear else 0)]))
  def hook(uc,at,size,_):
   if at==0x020503D0:
    self.assertEqual(uc.reg_read(UC_ARM_REG_R0),save);self.assertEqual(uc.reg_read(UC_ARM_REG_SP)%8,0);uc.reg_write(UC_ARM_REG_R0,state);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_SP,0x0231F000);cpu.reg_write(UC_ARM_REG_LR,0x020FF001)
  cpu.reg_write(UC_ARM_REG_R0,0x12345678);cpu.reg_write(UC_ARM_REG_R1,trainer_class);cpu.reg_write(UC_ARM_REG_R2,0x87654321)
  for reg in (UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7):cpu.reg_write(reg,0x11000000+reg)
  cpu.emu_start(address|1,READ_MESSAGE,count=1000);self.assertEqual(cpu.reg_read(UC_ARM_REG_PC),READ_MESSAGE);self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x0231F000);self.assertEqual(cpu.reg_read(UC_ARM_REG_LR),0x020FF001);self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),0x12345678);self.assertEqual(cpu.reg_read(UC_ARM_REG_R2),0x87654321)
  for reg in (UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7):self.assertEqual(cpu.reg_read(reg),0x11000000+reg)
  self.assertEqual(cpu.mem_read(state+FLAG_BYTE_OFFSET,1),bytes([0x83|(16 if clear else 0)]));return cpu.reg_read(UC_ARM_REG_R1)
 def test_blue_before_and_after_hall_of_fame(self):
  self.assertEqual(self.execute(110),LABEL_INDEX);self.assertEqual(self.execute(110,True),110)
 def test_every_other_class_and_null_save_remain_native(self):
  for trainer_class in range(140):
   for clear in (False,True):
    if trainer_class!=110:self.assertEqual(self.execute(trainer_class,clear),trainer_class)
   self.assertEqual(self.execute(trainer_class,present=False),trainer_class)
if __name__=='__main__':unittest.main()
