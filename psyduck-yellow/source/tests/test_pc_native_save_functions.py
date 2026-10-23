"""Execute unmodified candidate Thumb save routines; no ROM/save writes."""
import sys,struct,json,binascii,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from pc_storage_layout import *
from test_pc_storage_layout import legacy
ROOT=Path(__file__).resolve().parents[2]
SAVE=0x02300000;BUFFER=0x02400000;STACK=0x0250F000;STOP=0x02600000;HEADERS=0x02510000

class NativeSaveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.main=ndspy.rom.NintendoDSRom.fromFile(str(ROOT/'yellow-heartgold/build/0031-blue-optional-all-v1/private-blue-optional.nds')).loadArm9()
 def machine(self,size=LEGACY_SIZE,data=None):
  c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for address,length in ((0x01FF0000,0x10000),(0x02000000,0x300000),(SAVE,0x40000),(BUFFER,0x40000),(0x02500000,0x20000),(STOP,0x1000)):c.mem_map(address,length)
  for sec in self.main.sections[:1]:
   if sec.data:c.mem_write(sec.ramAddress,bytes(sec.data))
  c.mem_write(SAVE+0x232B4,struct.pack('<4BII',0,0,16,0,0,size)+struct.pack('<4BII',1,16,19,0,0xF700,0x12310))
  if data is not None:c.mem_write(BUFFER,bytes(data))
  def hook(cpu,address,n,user):
   if address==0x0202551C:raise AssertionError('Native assertion')
   if address==0x0201FF98:
    at=cpu.reg_read(UC_ARM_REG_R0);length=cpu.reg_read(UC_ARM_REG_R1);cpu.reg_write(UC_ARM_REG_R0,binascii.crc_hqx(bytes(cpu.mem_read(at,length)),65535));cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
  c.hook_add(UC_HOOK_CODE,hook);return c
 def execute(self,c,address,args):
  for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):c.reg_write(reg,value)
  for reg,value in ((UC_ARM_REG_R4,44),(UC_ARM_REG_R5,55),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77),(UC_ARM_REG_SP,STACK),(UC_ARM_REG_LR,STOP|1)):c.reg_write(reg,value)
  c.emu_start(address|1,STOP,count=20000)
  self.assertEqual(c.reg_read(UC_ARM_REG_PC),STOP)
  for reg,value in ((UC_ARM_REG_R4,44),(UC_ARM_REG_R5,55),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77),(UC_ARM_REG_SP,STACK)):self.assertEqual(c.reg_read(reg),value)
  return c.reg_read(UC_ARM_REG_R0)
 def test_native_footer_pointer_tracks_actual_spec_size(self):
  for size in (LEGACY_SIZE,EXPANDED_SIZE):
   c=self.machine(size);self.assertEqual(self.execute(c,0x020275F4,(SAVE,BUFFER,0)),BUFFER+size-16)
 def test_native_validation_accepts_each_layout_only_with_matching_spec(self):
  old=legacy(42);new=normalize_general(old)[0]
  for size,data,valid in ((LEGACY_SIZE,old,1),(EXPANDED_SIZE,new,1),(LEGACY_SIZE,new,0),(EXPANDED_SIZE,old,0)):
   c=self.machine(size,data);self.assertEqual(self.execute(c,0x0202761C,(SAVE,BUFFER,0)),valid)
 def test_native_validation_rejects_corruption(self):
  for size in (LEGACY_SIZE,EXPANDED_SIZE):
   for at in (0,100,size-12,size-8,size-4,size-2):
    data=bytearray(normalize_general(legacy())[0] if size==EXPANDED_SIZE else legacy());data[at]^=1;c=self.machine(size,data)
    self.assertEqual(self.execute(c,0x0202761C,(SAVE,BUFFER,0)),0)
 def test_native_cached_count_read_requires_new_footer_before_return(self):
  data=normalize_general(legacy(0xFFFFFFFF))[0];c=self.machine(EXPANDED_SIZE,data);check=SAVE+0x30000
  self.execute(c,0x0202768C,(check,SAVE,BUFFER,0));self.assertEqual(struct.unpack('<II',c.mem_read(check,8)),(1,0xFFFFFFFF))
 def test_native_slot_specs_match_source_layout(self):
  audit=json.loads((ROOT/'private/pc-storage-layout-agent-v1/native-layout.json').read_text());c=self.machine();blob=bytearray()
  for row in audit['all_native_substructures']:blob.extend(struct.pack('<IIIHH',row['id'],row['size_with_crc'],row['offset'],0,row['block']))
  c.mem_write(HEADERS,bytes(blob));specs=SAVE+0x30000;self.execute(c,0x02027EFC,(specs,HEADERS))
  values=[struct.unpack('<4BII',c.mem_read(specs+12*i,12)) for i in range(2)]
  self.assertEqual(values,[(0,0,16,0,0,LEGACY_SIZE),(1,16,19,0,0xF700,0x12310)])
if __name__=='__main__':unittest.main()
