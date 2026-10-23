"""Validate the source grid, native permissions and Kanto-only terrain boundary."""
import unittest,json,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route5_terrain import patch_probe
from viridian_tutorial import TABLE
class TerrainProbe(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.layout=json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text())
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'))
  cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch_probe(cls.after,cls.layout,diagnostic=True)
 def test_compiler_reproduces_native_tested_probe(self):
  expected=hashlib.sha256((PROJECT/'build/0027-route5-terrain-probe-v3/route5-terrain-probe.nds').read_bytes()).hexdigest()
  self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),expected)
 def test_only_kanto_header_and_verified_compression_metadata_change(self):
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(TABLE+13*24,TABLE+14*24))|set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  self.assertEqual(len(a.sections[0].data),len(b.sections[0].data))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm7,self.after.arm7);self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable)
  paths=('a/0/4/1','a/0/6/5','a/0/3/2');ids={self.before.filenames.idOf(p) for p in paths}
  for p in paths:
   old=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf(p)]);new=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf(p)])
   self.assertEqual(new.files[:len(old.files)],old.files)
  for i,(x,y) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(x,y)
 def test_all_grass_ledges_and_padding_permissions(self):
  arc=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')]);grids=[struct.unpack_from('<1024H',arc.files[i],20) for i in self.report['lands']]
  def cell(x,y):return grids[y//32][y%32*32+x]
  self.assertEqual(sum(v==2 for g in grids for v in g),48)
  self.assertEqual(sum(v==0x803B for g in grids for v in g),40)
  self.assertEqual(cell(16,2),0);self.assertEqual(cell(16,3),0x803B);self.assertEqual(cell(16,4),2)
  self.assertEqual(cell(16,34),0)
  for y in range(64):
   for x in range(32):
    if x<6 or x>=26 or y>=36:self.assertEqual(cell(x,y),0x8000)
 def test_incomplete_grid_and_implicit_diagnostic_are_rejected(self):
  with self.assertRaises(ValueError):patch_probe(self.before,self.layout)
  bad=dict(self.layout,cells=self.layout['cells'][:-1])
  with self.assertRaises(ValueError):patch_probe(self.before,bad,diagnostic=True)
if __name__=='__main__':unittest.main()
