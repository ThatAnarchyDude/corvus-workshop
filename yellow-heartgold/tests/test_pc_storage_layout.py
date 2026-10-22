import sys,struct,binascii,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from pc_storage_layout import *

def legacy(count=7):
 b=bytearray((n*17+9)&255 for n in range(0x11000))
 struct.pack_into('<IIIHH',b,TAIL,count,LEGACY_SIZE,NATIVE_MAGIC,0,binascii.crc_hqx(b[:TAIL],65535))
 return b

def reseal(b):
 struct.pack_into('<H',b,EXPANDED_SIZE-2,binascii.crc_hqx(b[:NEW_FOOTER],65535))

class LayoutTests(unittest.TestCase):
 def test_migration_preserves_native_data_and_storage(self):
  for count in (0,1,0xFFFFFFFE,0xFFFFFFFF):
   original=legacy(count);snapshot=bytes(original);out,report=normalize_general(original)
   self.assertEqual(bytes(original),snapshot);self.assertEqual(out[:TAIL],snapshot[:TAIL]);self.assertEqual(out[EXPANDED_SIZE:],snapshot[EXPANDED_SIZE:]);self.assertEqual(len(out),len(snapshot));self.assertEqual(report['count'],count);self.assertTrue(report['migrated']);self.assertTrue(native_valid(out,EXPANDED_SIZE));self.assertFalse(native_valid(out,LEGACY_SIZE))
 def test_new_layout_is_idempotent_and_keeps_all_physical_slots(self):
  b=bytearray(normalize_general(legacy())[0]);struct.pack_into('<HH',b,TAIL+16+49*4,4,999);reseal(b)
  out,report=normalize_general(b);self.assertEqual(out,b);self.assertFalse(report['migrated']);self.assertEqual(struct.unpack_from('<HH',out,TAIL+16+49*4),(4,999))
 def test_corrupt_legacy_or_new_data_never_migrates(self):
  for expanded in (False,True):
   source=normalize_general(legacy())[0] if expanded else legacy()
   for at in (0,100,TAIL-1,(NEW_FOOTER if expanded else TAIL)+8):
    b=bytearray(source);b[at]^=1
    with self.assertRaises(ValueError):normalize_general(b)
 def test_unknown_schema_and_bad_stacks_rejected_even_with_valid_native_crc(self):
  for offset,value in ((TAIL+4,2),(TAIL+8,1),(TAIL+16+2,1)):
   b=bytearray(normalize_general(legacy())[0]);struct.pack_into('<H',b,offset,value);reseal(b)
   with self.assertRaises(ValueError):normalize_general(b)
  b=bytearray(normalize_general(legacy())[0]);struct.pack_into('<HH',b,TAIL+16,4,1000);reseal(b)
  with self.assertRaises(ValueError):normalize_general(b)
 def test_kanto_badge_capacity_every_mask(self):
  for mask in range(256):self.assertEqual(capacity(mask),20+5*bin(mask).count('1'))
  for mask in (-1,256,65535):
   with self.assertRaises(ValueError):capacity(mask)
if __name__=='__main__':unittest.main()
