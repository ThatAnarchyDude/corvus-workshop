import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from ss_anne_world_map import patch,CLONES
from viridian_tutorial import TABLE
SOURCE=Path(__file__).resolve().parents[1]/'build/0030-ship-name-v1/private-ship-name.nds'
class ShipWorldMapTests(unittest.TestCase):
 def setUp(self):self.rom=ndspy.rom.NintendoDSRom.fromFile(str(SOURCE))
 def test_explicit_anchor_preserves_all_existing_maps_and_assets(self):
  before=self.rom.loadArm9().sections[0].data;files=list(self.rom.files)
  result=patch(self.rom);after=self.rom.loadArm9().sections[0].data
  self.assertEqual(result['main_matrix_location'],54)
  self.assertEqual(files,self.rom.files)
  for mid in range(540):
   at=TABLE+mid*24
   if mid not in CLONES:self.assertEqual(before[at:at+24],after[at:at+24])
   else:
    word=struct.unpack_from('<H',after,at+2)[0]
    self.assertEqual(((word>>4)&63,(word>>10)&63),(40,9))
    self.assertEqual(word&15,before[at+2]&15)
    self.assertEqual(before[at+4:at+24],after[at+4:at+24])
 def test_rejects_changed_reference_coordinates(self):
  main=self.rom.loadArm9();main.sections[0].data=bytearray(main.sections[0].data)
  struct.pack_into('<H',main.sections[0].data,TABLE+358*24+2,15)
  self.rom.arm9=main.save(compress=True)
  with self.assertRaises(AssertionError):patch(self.rom)
 def test_rejects_main_matrix_location_mismatch(self):
  fid=self.rom.filenames.idOf('a/0/4/1');arc=ndspy.narc.NARC(self.rom.files[fid]);raw=bytearray(arc.files[0])
  at=5+raw[4]+2*(9*raw[0]+40);struct.pack_into('<H',raw,at,53)
  arc.files[0]=raw;self.rom.files[fid]=arc.save()
  with self.assertRaises(AssertionError):patch(self.rom)
if __name__=='__main__':unittest.main()
