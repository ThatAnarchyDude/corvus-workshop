"""Verify guard integration retains Route 5 scenery and both exterior returns."""
import unittest,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from saffron_gates import patch,GATES
from opening import events_decode
from viridian_tutorial import TABLE
from build_rom import PROJECT
class IntegratedRoute5(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-route5-native-scenery-v5/route5-native-scenery-probe.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after)
 def test_guard_integration_retains_both_new_route5_returns(self):
  d=self.after.loadArm9().sections[0].data;arc=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/3/2')]);events=events_decode(arc.files[struct.unpack_from('<H',d,TABLE+391*24+16)[0]])
  self.assertEqual([struct.unpack_from('<2H',v,4) for v in events[2]],[(13,2),(13,0)])
  self.assertEqual(struct.unpack_from('<2H',events[3][0],12),(0,0))
 def test_only_four_kanto_guard_headers_and_appended_event_resources_change(self):
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  for m,_,_ in GATES:allowed.update(range(TABLE+m*24,TABLE+(m+1)*24))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  paths=('a/0/1/2','a/0/2/7','a/0/3/2');ids={self.before.filenames.idOf(p) for p in paths}
  for p in paths:
   old=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf(p)]);new=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf(p)]);self.assertEqual(old.files,new.files[:len(old.files)])
  for i,(x,y) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(x,y)
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
 def test_reproduces_native_integrated_probe(self):
  target=PROJECT/'build/0027-integrated-route5-guards-v1/integrated-route5-guards-private.nds';self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
