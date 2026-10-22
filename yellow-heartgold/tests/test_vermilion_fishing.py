"""Native ABI, exact distributions, night-table compatibility and scoped ROM edits."""
import sys,json,struct,unittest,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from unicorn import *
from unicorn.arm_const import *
from build_rom import PROJECT
from viridian_tutorial import TABLE
from vermilion_fishing import bl_target,SUPER
from route6_fishing import WEIGHTS,GOOD
class VermilionFishing(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0030-old-rod-v1/private-old-rod.nds'));cls.b=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0030-vermilion-fishing-v1/private-vermilion-fishing.nds'));cls.report=json.loads((PROJECT/'build/0030-vermilion-fishing-v1/report.json').read_text());cls.hooks={v['name']:int(v['hook'],16) for v in cls.report['hooks']};cls.main=cls.b.loadArm9();cls.ov=cls.b.loadArm9Overlays()[2];cls.baseline_main=cls.a.loadArm9();cls.baseline_ov=cls.a.loadArm9Overlays()[2]
 def cpu(self,before=False):
  c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x2000000,0x400000);c.mem_map(0x1ff8000,0x8000)
  main=self.baseline_main if before else self.main;ov=self.baseline_ov if before else self.ov
  for s in main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
  c.mem_write(ov.ramAddress,bytes(ov.data));c.reg_write(UC_ARM_REG_SP,0x23f0000);c.reg_write(UC_ARM_REG_LR,0x23ff001);return c
 def test_marker_abi_and_scope_for_all_maps(self):
  for mid in range(540):
   for rod in range(3):
    c=self.cpu();c.mem_write(0x23f1020,struct.pack('<I',0x23f1100));c.mem_write(0x23f1100,struct.pack('<I',mid));c.mem_write(0x23f0000,struct.pack('<3I',0x111,rod,0x333));regs={UC_ARM_REG_R0:0x23f1000,UC_ARM_REG_R1:0x456,UC_ARM_REG_R2:0x789,UC_ARM_REG_R3:0xABC,UC_ARM_REG_R4:0xDEF,UC_ARM_REG_R5:0x123}
    for k,v in regs.items():c.reg_write(k,v)
    c.emu_start(self.hooks['super_marker']|1,0x2247514,count=1000);self.assertEqual(struct.unpack('<3I',c.mem_read(0x23f0000,12)),(0x111,3 if mid in (14,54) and rod==2 else rod,0x333))
    for k,v in regs.items():self.assertEqual(c.reg_read(k),v)
    self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000)
 def test_swarm_scope_and_abi_for_all_maps(self):
  for mid in range(540):
   c=self.cpu();c.mem_write(0x23f1020,struct.pack('<I',0x23f1100));c.mem_write(0x23f1100,struct.pack('<I',mid));regs={UC_ARM_REG_R0:0x23f1000,UC_ARM_REG_R1:2,UC_ARM_REG_R2:0x123,UC_ARM_REG_R3:0x456,UC_ARM_REG_R4:0x789}
   for k,v in regs.items():c.reg_write(k,v)
   c.emu_start(self.hooks['swarm']|1,0x23ff000 if mid in (14,54) else 0x2246BD8,count=1000)
   for k,v in regs.items():self.assertEqual(c.reg_read(k),v)
   self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000)
 def night_result(self,raw,rod,tod,before=False):
  c=self.cpu(before);at=(0x94 if rod==1 else 0xA8);data=b''.join(struct.pack('<IHH',sp,hi,lo) for lo,hi,sp in [struct.unpack_from('<BBH',raw,at+4*i) for i in range(5)]);c.mem_write(0x23f2000,bytes(raw));c.mem_write(0x23f3000,data)
  def time(uc,a,size,user):uc.reg_write(UC_ARM_REG_R0,tod);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  c.hook_add(UC_HOOK_CODE,time,begin=0x201481c,end=0x201481c);c.reg_write(UC_ARM_REG_R0,0x23f2000);c.reg_write(UC_ARM_REG_R1,rod);c.reg_write(UC_ARM_REG_R2,0x23f3000);c.reg_write(UC_ARM_REG_R3,0x123)
  c.emu_start(0x2246AD5 if before else self.hooks['night']|1,0x23ff000,count=1000);self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000);return bytes(c.mem_read(0x23f3000,40)),data
 def test_night_preserves_all_original_tables_and_new_table(self):
  arc=ndspy.narc.NARC(self.b.files[self.report['encounter_file']])
  for raw in arc.files[:-1]:
   if len(raw)!=196:continue
   for rod in (1,2):
    for tod in (0,3,4):self.assertEqual(self.night_result(raw,rod,tod)[0],self.night_result(raw,rod,tod,True)[0])
  for rod in (1,2):
   for tod in range(5):
    result,data=self.night_result(arc.files[-1],rod,tod);self.assertEqual(result,data)
 def test_exact_distributions_use_existing_native_selector(self):
  selector=bl_target(self.ov.data,0x2247CCC,self.ov.ramAddress);counts=collections.Counter()
  for roll in range(256):
   c=self.cpu()
   def rng(uc,a,size,user):uc.reg_write(UC_ARM_REG_R0,roll);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   c.hook_add(UC_HOOK_CODE,rng,begin=0x201FD44,end=0x201FD44);c.reg_write(UC_ARM_REG_R0,3);c.emu_start(selector|1,0x23ff000,count=1000);counts[c.reg_read(UC_ARM_REG_R0)]+=1
  self.assertEqual([counts[i] for i in range(4)],[64]*4);self.assertEqual(SUPER[:4],((72,15),(72,20),(72,10),(116,5)));self.assertEqual(sum(w for w,(sp,lv) in zip(WEIGHTS,GOOD) if sp==118),50)
 def test_resource_and_existing_code_boundaries(self):
  for i,(a,b) in enumerate(zip(self.a.files,self.b.files)):
   if i not in (self.report['overlay_file'],self.report['encounter_file']):self.assertEqual(a,b,i)
  arcA=ndspy.narc.NARC(self.a.files[self.report['encounter_file']]);arcB=ndspy.narc.NARC(self.b.files[self.report['encounter_file']]);self.assertEqual(arcA.files,arcB.files[:-1]);a=self.a.loadArm9();b=self.main;self.assertEqual(a.sections[1].data,b.sections[1].data[:len(a.sections[1].data)]);self.assertLess(len(b.sections[1].data),32768)
  for mid in range(540):
   x=a.sections[0].data[TABLE+mid*24:TABLE+(mid+1)*24];y=b.sections[0].data[TABLE+mid*24:TABLE+(mid+1)*24]
   self.assertEqual(x[1:] if mid==54 else x,y[1:] if mid==54 else y)
  old=self.a.loadArm9Overlays()[2].data;new=self.ov.data;allowed={i for v in self.report['hooks'] for i in range(int(v['site'],16)-self.ov.ramAddress,int(v['site'],16)-self.ov.ramAddress+4)}
  self.assertEqual(len(old),len(new));self.assertTrue(all(x==y for i,(x,y) in enumerate(zip(old,new)) if i not in allowed))
if __name__=='__main__':unittest.main()