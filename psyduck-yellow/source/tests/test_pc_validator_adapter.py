import sys,unittest,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from blue_properties_shared import assemble
import test_pc_native_save_functions as native
from test_pc_native_save_functions import SAVE,BUFFER
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC
from test_pc_storage_layout import legacy,reseal
from pc_storage_layout import *
ADDRESS=0x01FFCD64
class AdapterTests(native.NativeSaveTests):
 @classmethod
 def setUpClass(cls):
  super().setUpClass();cls.code=assemble((Path(__file__).resolve().parents[1]/'asm/pc-general-validate.s').read_text(),ADDRESS)
 def adapter(self,c,args):
  c.mem_write(ADDRESS,self.code);return self.execute(c,ADDRESS,args)
 def test_budget_and_legacy_migration_match_reference_exactly(self):
  self.assertLessEqual(len(self.code),260)
  for count in (0,42,0xFFFFFFFF):
   data=legacy(count);c=self.machine(EXPANDED_SIZE,data);self.assertEqual(self.adapter(c,(SAVE,BUFFER,0)),1)
   self.assertEqual(bytes(c.mem_read(BUFFER,len(data))),normalize_general(data)[0]);self.assertEqual(struct.unpack('<I',c.mem_read(SAVE+0x232BC,4))[0],EXPANDED_SIZE)
 def test_new_valid_and_unknown_schema(self):
  data=bytearray(normalize_general(legacy())[0]);c=self.machine(EXPANDED_SIZE,data);self.assertEqual(self.adapter(c,(SAVE,BUFFER,0)),1);self.assertEqual(bytes(c.mem_read(BUFFER,len(data))),data)
  data[TAIL+4]=2;reseal(data);c=self.machine(EXPANDED_SIZE,data);self.assertEqual(self.adapter(c,(SAVE,BUFFER,0)),0)
 def test_invalid_legacy_is_read_only_and_restores_spec(self):
  data=legacy();data[100]^=1;c=self.machine(EXPANDED_SIZE,data);self.assertEqual(self.adapter(c,(SAVE,BUFFER,0)),0);self.assertEqual(bytes(c.mem_read(BUFFER,len(data))),data);self.assertEqual(struct.unpack('<I',c.mem_read(SAVE+0x232BC,4))[0],EXPANDED_SIZE)
 def test_legacy_spec_delegates_without_migration(self):
  data=legacy();c=self.machine(LEGACY_SIZE,data);self.assertEqual(self.adapter(c,(SAVE,BUFFER,0)),1);self.assertEqual(bytes(c.mem_read(BUFFER,len(data))),data)
 def test_storage_validation_delegates_without_changing_any_data(self):
  data=(native.ROOT/'yellow-heartgold/build/0030-live-old-rod-v1/old-rod-private-fixture.dsv').read_bytes()[:0x40000]
  c=self.machine(EXPANDED_SIZE,data);self.assertEqual(self.adapter(c,(SAVE,BUFFER,1)),1);self.assertEqual(bytes(c.mem_read(BUFFER,len(data))),data)
 def test_native_cached_footer_reads_migrated_counter(self):
  data=legacy(42);c=self.machine(EXPANDED_SIZE,data);c.mem_write(ADDRESS,self.code)
  def redirect(cpu,address,size,user):
   if address==0x020276A8:
    cpu.reg_write(UC_ARM_REG_LR,0x020276AD);cpu.reg_write(UC_ARM_REG_PC,ADDRESS|1)
  c.hook_add(UC_HOOK_CODE,redirect);check=SAVE+0x30000
  self.execute(c,0x0202768C,(check,SAVE,BUFFER,0));self.assertEqual(struct.unpack('<II',c.mem_read(check,8)),(1,42));self.assertEqual(bytes(c.mem_read(BUFFER,len(data))),normalize_general(data)[0])
if __name__=='__main__':unittest.main()
