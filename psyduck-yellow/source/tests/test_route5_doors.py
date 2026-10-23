"""Check Yellow door coordinates, native return anchors and Kanto-only edits."""
import unittest,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from route5_doors import patch_probe_doors,DOORS
from opening import events_decode
from viridian_tutorial import TABLE
from build_rom import PROJECT
class DoorProbe(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-route5-terrain-probe-v3/route5-terrain-probe.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch_probe_doors(cls.after,diagnostic=True)
 def groups(self,rom,m):
  d=rom.loadArm9().sections[0].data;eid=struct.unpack_from('<H',d,TABLE+m*24+16)[0];arc=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')]);return events_decode(arc.files[eid])
 def test_exterior_coordinates_and_destination_anchors(self):
  rows=[struct.unpack('<4HI',v) for v in self.groups(self.after,13)[2]]
  self.assertEqual(rows,[(16,29,391,1,0),(15,29,391,1,0),(16,33,391,0,0),(23,27,469,0,0),(16,21,517,0,0)])
  bg=self.groups(self.after,13)[0][0];self.assertEqual(struct.unpack('<HHiiiH2x',bg),(1,0,23,29,0,4))
 def test_returns_and_untouched_interior_actors(self):
  for m,pairs in ((517,{0:4}),(469,{0:3}),(391,{0:2,1:0})):
   before=self.groups(self.before,m);after=self.groups(self.after,m)
   for group in (0,1,3):self.assertEqual(after[group],before[group])
   for index,row in enumerate(after[2]):
    if index in pairs:self.assertEqual(struct.unpack_from('<2H',row,4),(13,pairs[index]))
    else:self.assertEqual(row,before[2][index])
 def test_native_door_permissions_and_original_archive_preservation(self):
  arc=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')])
  for _,x,z,_,_,behavior in DOORS:self.assertEqual(struct.unpack_from('<H',arc.files[self.report['lands'][z//32]],20+2*(z%32*32+x))[0],behavior)
  paths=('a/0/4/1','a/0/6/5','a/0/3/2');ids={self.before.filenames.idOf(p) for p in paths}
  for path in paths:
   a=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf(path)]);b=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf(path)]);self.assertEqual(a.files,b.files[:len(a.files)])
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(a,b)
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  for m in (13,391,469,517):allowed.update(range(TABLE+m*24,TABLE+(m+1)*24))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
 def test_compiler_reproduces_native_tested_door_probe(self):
  self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256((PROJECT/'build/0027-route5-door-probe-v1/route5-door-probe.nds').read_bytes()).hexdigest())
 def test_implicit_diagnostic_is_rejected(self):
  with self.assertRaises(ValueError):patch_probe_doors(self.before)
if __name__=='__main__':unittest.main()
