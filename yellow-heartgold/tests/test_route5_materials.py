"""Native texture bindings and preservation checks for the private Route 5 probe."""
import unittest,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from ndspy import _common
from route5_materials import patch_probe_materials,native_materials
from viridian_tutorial import TABLE
from build_rom import PROJECT
class MaterialProbe(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-route5-door-probe-v1/route5-door-probe.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch_probe_materials(cls.after,diagnostic=True)
 def test_original_archives_code_and_johto_are_preserved(self):
  paths=('a/0/4/1','a/0/6/5');ids={self.before.filenames.idOf(p) for p in paths}
  for p in paths:
   a=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf(p)]);b=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf(p)]);self.assertEqual(a.files,b.files[:len(a.files)])
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(a,b)
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(TABLE+13*24+4,TABLE+13*24+6))|set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
 def test_permissions_height_props_and_native_materials_preserved(self):
  a=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf('a/0/6/5')]);b=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')]);mat=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf('a/0/4/1')]);d=self.before.loadArm9().sections[0].data;oldids=struct.unpack_from('<2H',mat.files[struct.unpack_from('<H',d,TABLE+13*24+4)[0]],5)
  expected,bindings,count=native_materials(a)
  for oldid,newid in zip(oldids,self.report['lands']):
   raw=a.files[oldid];new=b.files[newid];ps,os,ms,bs,_=struct.unpack_from('<5I',raw);nps,nos,nms,nbs,_=struct.unpack_from('<5I',new)
   self.assertEqual((ps,os,bs),(nps,nos,nbs));self.assertEqual(raw[20:20+ps+os],new[20:20+nps+nos]);self.assertEqual(raw[20+ps+os+ms:],new[20+nps+nos+nms:])
   model=new[20+nps+nos:20+nps+nos+nms];base=struct.unpack_from('<I',model,16)[0]+48;sbc,mo,so,en=struct.unpack_from('<4I',model,base+4)
   self.assertEqual(model[base+mo:base+so],expected);self.assertEqual(model[base+24],count);self.assertEqual(model[base+25],3)
   sb=model[base+sbc:base+mo];self.assertEqual([sb[9],sb[21],sb[33]],[bindings[n][0] for n in ('grass01gs','egrass','cliff01gs')])
   self.assertEqual(struct.unpack_from('<I',model,base)[0],len(model)-base)
 def test_reproduces_native_tested_rom(self):
  target=PROJECT/'build/0027-route5-native-materials-v1/route5-native-materials-probe.nds'
  self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256(target.read_bytes()).hexdigest())
 def test_implicit_unfinished_graphics_rejected(self):
  with self.assertRaises(ValueError):patch_probe_materials(self.before)
if __name__=='__main__':unittest.main()
