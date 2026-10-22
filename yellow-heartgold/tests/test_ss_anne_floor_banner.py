import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from ss_anne_banner import SITE
from ss_anne_floors import banner_code as assemble
from viridian_tutorial import TABLE
SOURCE=Path(__file__).resolve().parents[1]/'build/0030-ship-passages-v1/private-ship-passages.nds'
class BannerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  r=ndspy.rom.NintendoDSRom.fromFile(str(SOURCE));cls.headers=r.loadArm9().sections[0].data
  native=ndspy.rom.NintendoDSRom.fromFile(str(SOURCE.parents[1]/'0030-ship-world-map-v1/private-ship-world-map.nds'));ov=native.loadArm9Overlays()[1];at=SITE-ov.ramAddress;cls.original=bytes(ov.data[at:at+64]);cls.updated=assemble()
 def run_code(self,code,mid,icon,building):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x02000000,0x400000);uc.mem_write(SITE,code)
  uc.mem_write(0x02020000+32,struct.pack('<I',0x02020100));uc.mem_write(0x02020100,struct.pack('<I',mid))
  uc.mem_write(0x02020000+4,struct.pack('<I',0x02020200));uc.mem_write(0x02020200+8,struct.pack('<I',0x02020300))
  uc.reg_write(UC_ARM_REG_R0,0x02020000);uc.reg_write(UC_ARM_REG_SP,0x02030000);uc.reg_write(UC_ARM_REG_LR,0x02010001)
  for reg,value in ((UC_ARM_REG_R4,0x44),(UC_ARM_REG_R5,0x55),(UC_ARM_REG_R6,0x66),(UC_ARM_REG_R7,0x77)):uc.reg_write(reg,value)
  drawn=[];section=self.headers[TABLE+mid*24+18]
  def hook(u,addr,size,user):
   if addr==0x02010000:u.emu_stop();return
   if addr in (0x0203B388,0x0203B58C,0x0203B36C):
    self.assertEqual(u.reg_read(UC_ARM_REG_R0),mid)
    u.reg_write(UC_ARM_REG_R0,{0x0203B388:icon,0x0203B58C:building,0x0203B36C:section}[addr]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   elif addr==0x021EFA3C:
    drawn.append(tuple(u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
    u.reg_write(UC_ARM_REG_R0,0x1234);u.reg_write(UC_ARM_REG_R1,0x5678);u.reg_write(UC_ARM_REG_R2,0x9abc)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  uc.hook_add(UC_HOOK_CODE,hook);uc.emu_start(SITE|1,0,count=150)
  self.assertEqual(uc.reg_read(UC_ARM_REG_SP),0x02030000)
  for reg,value in ((UC_ARM_REG_R4,0x44),(UC_ARM_REG_R5,0x55),(UC_ARM_REG_R6,0x66),(UC_ARM_REG_R7,0x77)):self.assertEqual(uc.reg_read(reg),value)
  return drawn
 def test_all_540_native_map_behaviors_and_abi(self):
  for mid in range(540):
   at=TABLE+mid*24;icon=self.headers[at+19]&15;flags=struct.unpack_from('<I',self.headers,at+20)[0]
   building=int(((flags>>8)&15) in (4,5))
   old=self.run_code(self.original,mid,icon,building);new=self.run_code(self.updated,mid,icon,building)
   if self.headers[TABLE+mid*24+18]==235:self.assertEqual(new,[(0x02020300,235,8)])
   else:self.assertEqual(old,new,mid)
 def test_zero_icon_and_building_boundaries(self):
  for mid in (0,253,254,255,256,257,258,259,260,261,262,539):
   for icon in (0,1,9,15):
    for building in (0,1):
     old=self.run_code(self.original,mid,icon,building);new=self.run_code(self.updated,mid,icon,building)
     if self.headers[TABLE+mid*24+18]==235 and icon and building:self.assertEqual(len(new),1)
     else:self.assertEqual(old,new)
if __name__=='__main__':unittest.main()


