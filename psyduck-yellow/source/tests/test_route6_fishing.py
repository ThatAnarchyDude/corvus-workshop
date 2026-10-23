import sys,struct,unittest,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route6_fishing import patch,WEIGHTS,GOOD,SUPER
from viridian_tutorial import TABLE
from unicorn import *
from unicorn.arm_const import *

class Route6Fishing(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0029-global-surf-badge-v1/private-connected-route6.nds'))
  cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after);cls.main=cls.after.loadArm9();cls.ov=cls.after.loadArm9Overlays()[2];cls.hooks={v['name']:int(v['hook'],16) for v in cls.report['hooks']}
 def cpu(self):
  c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x2000000,0x400000);c.mem_map(0x1ff8000,0x8000)
  for s in self.main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
  c.mem_write(self.ov.ramAddress,bytes(self.ov.data));c.reg_write(UC_ARM_REG_SP,0x23f0000);c.reg_write(UC_ARM_REG_LR,0x23ff001)
  return c
 def test_archive_and_code_boundaries(self):
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in (self.report['overlay_file'],self.report['encounter_file']):self.assertEqual(a,b)
  a=ndspy.narc.NARC(self.before.files[self.report['encounter_file']]);b=ndspy.narc.NARC(self.after.files[self.report['encounter_file']]);self.assertEqual(a.files,b.files[:len(a.files)])
  old=self.before.loadArm9Overlays();new=self.after.loadArm9Overlays()
  allowed={p for v in self.report['hooks'] for p in range(int(v['site'],16)-old[2].ramAddress,int(v['site'],16)-old[2].ramAddress+4)}
  for oid in old:
   if oid!=2:self.assertEqual(old[oid].data,new[oid].data)
   else:self.assertFalse([i for i,(x,y) in enumerate(zip(old[oid].data,new[oid].data)) if x!=y and i not in allowed])
  a=self.before.loadArm9();b=self.main;delta=len(b.sections[1].data)-len(a.sections[1].data)
  allowed={TABLE+14*24};allowed.update(range(0xD2C68,0xD2C6C));allowed.update(range(a.codeSettingsOffs,a.codeSettingsOffs+8));allowed.update(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
  self.assertFalse([i for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y and i not in allowed])
  self.assertEqual(a.sections[1].data,b.sections[1].data[:len(a.sections[1].data)])
 def test_marker_only_route6_super_rod_and_native_abi(self):
  for mid in range(540):
   for rod in range(3):
    c=self.cpu();c.mem_write(0x23f1020,struct.pack('<I',0x23f1100));c.mem_write(0x23f1100,struct.pack('<I',mid));c.mem_write(0x23f0000,struct.pack('<3I',0x111,rod,0x333))
    values={UC_ARM_REG_R0:0x23f1000,UC_ARM_REG_R1:0x456,UC_ARM_REG_R2:0x789,UC_ARM_REG_R3:0xabc,UC_ARM_REG_R4:0xdef,UC_ARM_REG_R5:0x123}
    for reg,v in values.items():c.reg_write(reg,v)
    c.emu_start(self.hooks['super_marker']|1,0x2247514,count=1000)
    self.assertEqual(struct.unpack('<3I',c.mem_read(0x23f0000,12)),(0x111,3 if mid==14 and rod==2 else rod,0x333))
    for reg,v in values.items():self.assertEqual(c.reg_read(reg),v)
    self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000);self.assertEqual(c.reg_read(UC_ARM_REG_LR),0x23ff001)
 def test_exact_native_distributions(self):
  for rod in range(4):
   counts=collections.Counter()
   for roll in range(256 if rod==3 else 100):
    c=self.cpu()
    def rng(uc,a,size,user):uc.reg_write(UC_ARM_REG_R0,roll);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    c.hook_add(UC_HOOK_CODE,rng,begin=0x201fd44,end=0x201fd44)
    c.reg_write(UC_ARM_REG_R0,rod);c.emu_start(self.hooks['slot_selector']|1,0x23ff000,count=10000);slot=c.reg_read(UC_ARM_REG_R0);counts[slot]+=1
    self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000)
   self.assertEqual([counts[i] for i in range(4 if rod==3 else 5)],[64]*4 if rod==3 else list(WEIGHTS))
  self.assertEqual(sum(w for w,(s,l) in zip(WEIGHTS,GOOD) if s==118),50)
  self.assertEqual([l for s,l in SUPER[:4]],[5,10,15,20])
 def test_swarm_only_route6_bypasses_substitution(self):
  for mid in (14,13,59,60,38):
   c=self.cpu();c.mem_write(0x23f1020,struct.pack('<I',0x23f1100));c.mem_write(0x23f1100,struct.pack('<I',mid))
   values={UC_ARM_REG_R0:0x23f1000,UC_ARM_REG_R1:2,UC_ARM_REG_R2:0x123,UC_ARM_REG_R3:0x456,UC_ARM_REG_R4:0x789}
   for reg,v in values.items():c.reg_write(reg,v)
   c.emu_start(self.hooks['swarm']|1,0x23ff000 if mid==14 else 0x2246bd8,count=1000)
   for reg,v in values.items():self.assertEqual(c.reg_read(reg),v)
   self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000)
 def test_native_night_replacements_preserve_yellow_rod_tables(self):
  arc=ndspy.narc.NARC(self.after.files[self.report['encounter_file']]);raw=arc.files[self.report['wild']]
  for rod,at in ((1,0x94),(2,0xA8)):
   for tod in (0,3,4):
    c=self.cpu();table=0x23f2000;slots=0x23f3000;c.mem_write(table,raw)
    data=b''.join(struct.pack('<IHH',sp,hi,lo) for lo,hi,sp in [struct.unpack_from('<BBH',raw,at+4*i) for i in range(5)])
    c.mem_write(slots,data)
    def time(uc,a,size,user):uc.reg_write(UC_ARM_REG_R0,tod);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    c.hook_add(UC_HOOK_CODE,time,begin=0x201481c,end=0x201481c)
    c.reg_write(UC_ARM_REG_R0,table);c.reg_write(UC_ARM_REG_R1,rod);c.reg_write(UC_ARM_REG_R2,slots)
    c.emu_start(0x2246ad5,0x23ff000,count=1000)
    self.assertEqual(bytes(c.mem_read(slots,40)),data)
if __name__=='__main__':unittest.main()