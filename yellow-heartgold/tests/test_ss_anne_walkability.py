import sys,unittest,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from ss_anne_walkability import audit,terrain
BUILD=Path(__file__).resolve().parents[1]/'build'
class ShipWalkabilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.current=ndspy.rom.NintendoDSRom.fromFile(str(BUILD/'0030-ship-door-faces-v1/private-ship-door-faces.nds'))
 def test_all_seventeen_cabins_and_captain_reachable(self):
  result=audit(self.current)
  self.assertEqual(result['cabins_by_map'],{259:6,260:6,261:5})
  self.assertFalse(result['unreachable_components'])
  self.assertFalse(result['door_facing_mismatches'])
  self.assertEqual(result['reachable_components'],27)
 def test_disconnected_prior_candidate_detected(self):
  result=audit(ndspy.rom.NintendoDSRom.fromFile(str(BUILD/'0030-colored-rockets-v1/private-colored-rockets.nds')))
  self.assertIn((254,1),result['unreachable_components'])
  self.assertLess(result['reachable_components'],result['logical_components'])
 def test_old_connection_faces_are_detected(self):
  result=audit(ndspy.rom.NintendoDSRom.fromFile(str(BUILD/'0030-ship-passages-v1/private-ship-passages.nds')))
  self.assertEqual(len(result['door_facing_mismatches']),4)
 def test_normal_loader_variable_land_header(self):
  lands=ndspy.narc.NARC(self.current.files[self.current.filenames.idOf('a/0/6/5')])
  for mid,extra in ((643,0),(644,32),(650,0),(651,48)):
   raw=lands.files[mid];self.assertEqual(struct.unpack_from('<I',raw,16)[0]>>16,extra)
   values=terrain(raw);self.assertEqual(len(values),1024)
   self.assertEqual(values[9*32+10],struct.unpack_from('<H',raw,20+extra+2*(9*32+10))[0])
if __name__=='__main__':unittest.main()

