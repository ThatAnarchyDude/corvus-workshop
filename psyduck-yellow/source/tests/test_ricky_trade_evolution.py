import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import ndspy.rom
from ricky_trade_evolution import patch,SITE,ORIGINAL
from unicorn import *
from unicorn.arm_const import *
class RickyEvolution(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile("yellow-heartgold/build/0029-underground-ricky-v3/private-ricky-trade.nds")
  cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new);cls.main=cls.new.loadArm9()
 def execute(self,mapid=469,trade=9,state=4,species=67,target=68,done=False):
  c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x2000000,0x400000);c.mem_map(0x1ff8000,0x8000)
  for s in self.main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
  task,fs,env,work,location=0x23f1000,0x23f1100,0x23f1200,0x23f1300,0x23f1400
  for a,v in [(fs+12,0x23f1500),(fs+32,location),(env,work),(env+4,state),(env+8,3),(work+12,trade),(location,mapid),(env+12,0x23f1800)]:c.mem_write(a,struct.pack("<I",v))
  calls=[]
  def stub(uc,a,size,user):
   regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   result=0
   if a==0x205064c:result=fs
   elif a==0x2050650:result=env
   elif a==0x2074644:result=0x23f1700
   elif a==0x206e540:result=species
   elif a==0x2070e34:
    result=target;sp=uc.reg_read(UC_ARM_REG_SP);ptr=struct.unpack("<I",uc.mem_read(sp,4))[0];uc.mem_write(ptr,struct.pack("<I",5))
   elif a==0x2075a7c:
    args=struct.unpack("<7I",uc.mem_read(uc.reg_read(UC_ARM_REG_SP),28));calls.append((a,regs,args));result=0x23f1800
   elif a==0x2075d3c:result=int(done)
   elif a==ORIGINAL:result=99
   else:result=a
   if a!=0x2075a7c:calls.append((a,regs))
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  stubs=[0x205064c,0x2050650,0x2074904,0x2074644,0x206e540,0x2070e34,0x201a910,0x2028ea8,0x2088288,0x202a634,0x207879c,0x202cf54,0x2075a7c,0x2075d3c,0x2075d4c,0x201a9c4,ORIGINAL]
  for a in stubs:c.hook_add(UC_HOOK_CODE,stub,begin=a,end=a)
  c.reg_write(UC_ARM_REG_R0,task);c.reg_write(UC_ARM_REG_SP,0x23f0000);c.reg_write(UC_ARM_REG_LR,0x23ff001)
  for reg,v in [(UC_ARM_REG_R4,44),(UC_ARM_REG_R5,55),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77)]:c.reg_write(reg,v)
  c.emu_start(int(self.report["hook"],16)|1,0x23ff000,count=1000)
  self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x23f0000)
  for reg,v in [(UC_ARM_REG_R4,44),(UC_ARM_REG_R5,55),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77)]:self.assertEqual(c.reg_read(reg),v)
  return c.reg_read(UC_ARM_REG_R0),struct.unpack("<I",c.mem_read(env+4,4))[0],calls
 def test_scope(self):
  for mid in range(540):
   if mid==469:continue
   result,state,calls=self.execute(mapid=mid);self.assertEqual((result,state),(99,4));self.assertEqual(calls[-1][0],ORIGINAL)
  for trade in range(13):
   if trade!=9:self.assertEqual(self.execute(trade=trade)[:2],(99,4))
  for state in range(7):
   if state!=4:self.assertEqual(self.execute(state=state)[:2],(99,state))
  self.assertEqual(self.execute(species=66)[:2],(99,4));self.assertEqual(self.execute(target=0)[:2],(99,4))
 def test_native_launch_and_cleanup(self):
  result,state,calls=self.execute();self.assertEqual((result,state),(0,7))
  evo=next(x for x in calls if x[0]==0x2075a7c)
  self.assertEqual(evo[1][:3],[0,0x23f1700,68]);self.assertEqual(evo[2][4:],(5,4,26))
  self.assertNotIn(ORIGINAL,[x[0] for x in calls])
  self.assertEqual(self.execute(state=7,done=False)[:2],(0,7))
  result,state,calls=self.execute(state=7,done=True);self.assertEqual((result,state),(99,4));self.assertEqual([x[0] for x in calls][-3:],[0x2075d4c,0x201a9c4,ORIGINAL])
 def test_preservation(self):
  self.assertEqual(self.old.files,self.new.files);self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
  a=self.old.loadArm9();b=self.main
  allowed=set(range(SITE-0x2000000,SITE-0x2000000+4))|set(range(0xd2c68,0xd2c6c))|set(range(a.codeSettingsOffs,a.codeSettingsOffs+8))|set(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
  self.assertFalse([i for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y and i not in allowed])
  self.assertEqual(a.sections[1].data,b.sections[1].data[:len(a.sections[1].data)])
if __name__=="__main__":unittest.main()