"""Private city connections preserve original terrain and existing story events."""
import unittest,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from route5_connections import patch_probe_connections,LINKS
from opening import events_decode
from parcel_quest import split_bank
from viridian_tutorial import TABLE
from build_rom import PROJECT
class CityLinks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-integrated-route5-guards-v1/integrated-route5-guards-private.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch_probe_connections(cls.after,diagnostic=True)
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
 def test_original_story_scripts_and_events_retained(self):
  a=self.before.loadArm9().sections[0].data;b=self.after.loadArm9().sections[0].data
  for m in (13,52,59):
   before=events_decode(self.arc(self.before,'a/0/3/2').files[struct.unpack_from('<H',a,TABLE+m*24+16)[0]]);after=events_decode(self.arc(self.after,'a/0/3/2').files[struct.unpack_from('<H',b,TABLE+m*24+16)[0]])
   for group in (0,1,2):self.assertEqual(before[group],after[group])
   self.assertEqual(before[3],after[3][:len(before[3])])
   oldbank=split_bank(self.arc(self.before,'a/0/1/2').files[struct.unpack_from('<H',a,TABLE+m*24+6)[0]]);newbank=split_bank(self.arc(self.after,'a/0/1/2').files[struct.unpack_from('<H',b,TABLE+m*24+6)[0]]);self.assertEqual([bytes(v).rstrip(b'\0') for v in oldbank],[bytes(v).rstrip(b'\0') for v in newbank[:len(oldbank)]])
   added=after[3][len(before[3]):];self.assertEqual(len(added),sum(v[0]==m for v in LINKS))
   for v in added:self.assertEqual(struct.unpack_from('<2H',v,12),(0,0))
 def test_main_matrix_every_original_archive_and_johto_code_preserved(self):
  paths=('a/0/1/2','a/0/3/2');ids={self.before.filenames.idOf(p) for p in paths}
  for p in paths:self.assertEqual(self.arc(self.before,p).files,self.arc(self.after,p).files[:len(self.arc(self.before,p).files)])
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(a,b)
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  for m in (13,52,59):allowed.update(range(TABLE+m*24+6,TABLE+m*24+8));allowed.update(range(TABLE+m*24+16,TABLE+m*24+18))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
 def test_new_probe_reproduced_and_diagnostic_required(self):
  target=PROJECT/'build/0027-route5-city-links-v2/route5-city-links-private.nds';self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256(target.read_bytes()).hexdigest())
  with self.assertRaises(ValueError):patch_probe_connections(self.before)
if __name__=='__main__':unittest.main()
