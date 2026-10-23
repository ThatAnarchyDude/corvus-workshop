"""Native opening saves legitimately have no Pokemon before starter selection."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from live_core import field_metrics
from build_rom import PROJECT
class OpeningMetrics(unittest.TestCase):
 def test_real_fresh_first_floor_continue_and_walking(self):
  m=field_metrics((PROJECT/'build/0026-first-floor-continue-20261013-v1/ram.bin').read_bytes())
  self.assertEqual(m['map_id'],503);self.assertEqual(m['party_count'],0);self.assertEqual(m['player'],dict(x=9,y=4,height=0))
 def test_invalid_party_count_still_rejected(self):
  ram=bytearray((PROJECT/'build/0026-first-floor-continue-20261013-v1/ram.bin').read_bytes());m=field_metrics(ram);fs=int(m['field_system'],16)-0x2000000
  save=struct.unpack_from('<I',ram,fs+12)[0]-0x2000000;_,_,off=struct.unpack_from('<3I',ram,save+0x23014+2*16);struct.pack_into('<I',ram,save+16+off+4,7)
  self.assertIsNone(field_metrics(ram,hint=fs))
if __name__=='__main__':unittest.main()
