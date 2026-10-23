import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom
from build_rom import PROJECT
from kanto_surf_badge import patch,SURF_BADGE_SITE
from viridian_tutorial import TABLE
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *

class KantoSurfBadge(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0029-route6-connected-v3/private-connected-route6.nds'))
  cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after);cls.main=cls.after.loadArm9()
 def test_only_badge_call_sites_and_appended_code_change(self):
  fid=self.report['shore_overlay_file']
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i!=fid:self.assertEqual(a,b)
  a=self.before.loadArm9();b=self.main;allowed=set(range(SURF_BADGE_SITE-0x2000000,SURF_BADGE_SITE-0x2000000+4))
  delta=len(b.sections[1].data)-len(a.sections[1].data)
  for p in (a.codeSettingsOffs,a.codeSettingsOffs+4):self.assertEqual(struct.unpack_from('<I',b.sections[0].data,p)[0],struct.unpack_from('<I',a.sections[0].data,p)[0]+delta)
  allowed.update(range(a.codeSettingsOffs,a.codeSettingsOffs+8))
  allowed.update(range(0xD2C68,0xD2C6C));allowed.update(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
  self.assertFalse([i for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y and i not in allowed])
  self.assertEqual(a.sections[1].data,b.sections[1].data[:len(a.sections[1].data)])
  old=self.before.loadArm9Overlays();new=self.after.loadArm9Overlays()
  for oid in old:
   if oid!=1:self.assertEqual(old[oid].data,new[oid].data)
   else:
    at=int(self.report['shore_site'],16)-old[oid].ramAddress
    self.assertEqual(old[oid].data[:at],new[oid].data[:at]);self.assertEqual(old[oid].data[at+4:],new[oid].data[at+4:])
 def test_arm9_supported_instruction_widths(self):
  c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);section=self.main.sections[1]
  for name in ('hook','shore_hook'):
   addr=int(self.report[name],16);at=addr-section.ramAddress
   for ins in c.disasm(bytes(section.data[at:]),addr):
    if ins.mnemonic=='nop':break
    self.assertEqual(ins.size,2,(hex(ins.address),ins.mnemonic))
 def test_every_map_soul_and_fog_combination_at_both_native_calls(self):
  d=self.main.sections[0].data;profile=0x23F3000
  for mid in range(540):
   kanto=bool(d[TABLE+mid*24+20]&1)
   for fog,soul in ((False,False),(True,False),(False,True),(True,True)):
    c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x2000000,0x400000);c.mem_map(0x1ff8000,0x8000)
    for s in self.main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
    c.mem_write(profile+26,bytes([8 if fog else 0]));c.mem_write(profile+31,bytes([16 if soul else 0]))
    c.mem_write(0x23f1000,struct.pack('<2I',mid,0x23f2000))
    c.mem_write(0x23f2020,struct.pack('<I',0x23f2100));c.mem_write(0x23f2100,struct.pack('<I',mid))
    for name in ('hook','shore_hook'):
     c.reg_write(UC_ARM_REG_R0,profile);c.reg_write(UC_ARM_REG_R1,3);c.reg_write(UC_ARM_REG_R4,0x23f1000);c.reg_write(UC_ARM_REG_R5,0x23f2000);c.reg_write(UC_ARM_REG_SP,0x23f0000);c.reg_write(UC_ARM_REG_LR,0x23ff001)
     c.emu_start(int(self.report[name],16)|1,0x23ff000,count=10000)
     self.assertEqual(bool(c.reg_read(UC_ARM_REG_R0)),soul or fog,(mid,name,fog,soul))
     self.assertEqual(c.reg_read(UC_ARM_REG_R4),0x23f1000);self.assertEqual(c.reg_read(UC_ARM_REG_R5),0x23f2000);self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000)
if __name__=='__main__':unittest.main()