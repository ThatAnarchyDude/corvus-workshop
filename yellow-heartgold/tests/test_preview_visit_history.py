import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import ndspy.rom
from preview_visit_history import patch,SITE,OFFSET
from unicorn import *
from unicorn.arm_const import *
class PreviewHistory(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile("yellow-heartgold/build/0029-seam-texture-union-v4/private-seam-textures.nds")
  cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new);cls.main=cls.new.loadArm9()
  d=cls.main.sections[0].data;table=struct.unpack_from("<I",d,0x6a384)[0]-0x2000000
  cls.maps=[struct.unpack_from("<I",d,table+i*60)[0] for i in range(25)]
 def cpu(self):
  c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x2000000,0x400000);c.mem_map(0x1ff8000,0x8000)
  for s in self.main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
  clock={"date":(26,10,13,2),"phase":0,"save_calls":0}
  c.mem_write(0x23e000c,struct.pack("<I",0x23e0800));c.mem_write(0x23e1000,b"\xa5"*0x2e0);c.mem_write(0x23e1000+OFFSET,bytes(16))
  def save(uc,a,size,user):
   self.assertEqual(uc.reg_read(UC_ARM_REG_R0),0x23e0800);self.assertEqual(uc.reg_read(UC_ARM_REG_R1),9)
   clock["save_calls"]+=1;uc.reg_write(UC_ARM_REG_R0,0x23e1000);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def date(uc,a,size,user):
   uc.mem_write(uc.reg_read(UC_ARM_REG_R0),struct.pack("<4I",*clock["date"]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def phase(uc,a,size,user):
   uc.reg_write(UC_ARM_REG_R0,clock["phase"]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for a,fn in [(0x20272c8,save),(0x2014780,date),(0x201481c,phase)]:c.hook_add(UC_HOOK_CODE,fn,begin=a,end=a)
  return c,clock
 def call(self,c,mid):
  c.reg_write(UC_ARM_REG_R0,mid);c.reg_write(UC_ARM_REG_R4,44);c.reg_write(UC_ARM_REG_R5,0x23e0000);c.reg_write(UC_ARM_REG_R6,66);c.reg_write(UC_ARM_REG_R7,77)
  c.reg_write(UC_ARM_REG_SP,0x23f0000);c.reg_write(UC_ARM_REG_LR,0x23ff001)
  c.emu_start(int(self.report["hook"],16)|1,0x23ff000,count=1000)
  for reg,v in [(UC_ARM_REG_R4,44),(UC_ARM_REG_R5,0x23e0000),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77),(UC_ARM_REG_SP,0x23f0000)]:self.assertEqual(c.reg_read(reg),v)
  block=bytes(c.mem_read(0x23e1000,0x2e0));self.assertEqual(block[:OFFSET],b"\xa5"*OFFSET);self.assertEqual(block[OFFSET+12:OFFSET+16],bytes(4));self.assertEqual(block[OFFSET+16:],b"\xa5"*(0x2e0-OFFSET-16))
  return c.reg_read(UC_ARM_REG_R0)
 def test_every_native_preview_and_period(self):
  c,clock=self.cpu()
  for phase in range(4):
   clock["phase"]=phase
   seen=set()
   for i,mid in enumerate(self.maps):
    key=self.report["history_keys"][i];self.assertEqual(self.call(c,mid),255 if key in seen else i);self.assertEqual(self.call(c,mid),255);seen.add(key)
  clock["phase"]=4;clock["date"]=(26,10,14,3)
  for mid in self.maps:self.assertEqual(self.call(c,mid),255)
  clock["date"]=(26,10,15,4)
  seen=set()
  for i,mid in enumerate(self.maps):
   key=self.report["history_keys"][i];self.assertEqual(self.call(c,mid),255 if key in seen else i);seen.add(key)
 def test_nonpreview_entries_and_persisted_history(self):
  c,clock=self.cpu()
  for mid in range(540):
   if mid not in self.maps:self.assertEqual(self.call(c,mid),255)
  self.assertEqual(clock["save_calls"],0)
  self.assertEqual(self.call(c,self.maps[0]),0)
  persisted=bytes(c.mem_read(0x23e1000+OFFSET,16));fresh,fclock=self.cpu();fresh.mem_write(0x23e1000+OFFSET,persisted)
  self.assertEqual(self.call(fresh,self.maps[0]),255);self.assertEqual(self.call(fresh,self.maps[1]),1)
  fclock["phase"]=1;self.assertEqual(self.call(fresh,self.maps[0]),0)
  fclock["phase"]=0;self.assertEqual(self.call(fresh,self.maps[0]),0)
 def test_continuous_night_calendar_edges(self):
  for before,after in [((26,10,13,2),(26,10,14,3)),((26,10,31,0),(26,11,1,1)),((26,12,31,0),(27,1,1,1)),((25,2,28,0),(25,3,1,1)),((24,2,29,0),(24,3,1,1))]:
   c,clock=self.cpu();clock["phase"]=3;clock["date"]=before;self.assertEqual(self.call(c,self.maps[0]),0)
   clock["phase"]=4;clock["date"]=after;self.assertEqual(self.call(c,self.maps[0]),255)
 def test_ds_supported_instructions(self):
  from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
  start=int(self.report["hook"],16);s=self.main.sections[1];raw=bytes(s.data[start-s.ramAddress:start-s.ramAddress+self.report["code_bytes"]])
  reached_return=False
  for ins in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(raw,start):
   self.assertFalse(ins.mnemonic.endswith(".w"),(hex(ins.address),ins.mnemonic))
   self.assertTrue(ins.size==2 or ins.mnemonic=="bl",(hex(ins.address),ins.mnemonic,ins.size))
   if ins.mnemonic=="pop" and "pc" in ins.op_str:reached_return=True;break
  self.assertTrue(reached_return)
 def test_preservation(self):
  self.assertEqual(self.old.files,self.new.files);self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
  a=self.old.loadArm9();b=self.main
  allowed=set(range(SITE-0x2000000,SITE-0x2000000+4))|set(range(0xd2c68,0xd2c6c))|set(range(a.codeSettingsOffs,a.codeSettingsOffs+8))|set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  self.assertFalse([i for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y and i not in allowed])
  self.assertEqual(a.sections[1].data,b.sections[1].data[:len(a.sections[1].data)])
if __name__=="__main__":unittest.main()