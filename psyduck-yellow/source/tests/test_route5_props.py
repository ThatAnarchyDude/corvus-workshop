"""Measured native prop anchors and preservation of Route 5 permissions/doors."""
import unittest,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from route5_props import patch_probe_props
from viridian_tutorial import TABLE
from build_rom import PROJECT
class NativeProps(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-route5-native-materials-v1/route5-native-materials-probe.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch_probe_props(cls.after,diagnostic=True)
 def test_native_pivots_preserve_measured_door_and_sign_offsets(self):
  arc=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')]);raw=arc.files[self.report['lands'][0]];self.assertEqual(struct.unpack_from('<I',raw,4)[0],96)
  rows=[struct.unpack_from('<12i',raw,2068+i*48) for i in range(2)]
  self.assertEqual(rows,[(290,524288,0,688128,0,0,0,4096,4096,4096,0,0),(31,491520,0,884736,0,0,0,4096,4096,4096,0,0)])
  x,z=rows[0][1]/65536+16,rows[0][3]/65536+16;self.assertEqual((x-1,z+.5),(23,27))
  x,z=rows[1][1]/65536+16,rows[1][3]/65536+16;self.assertEqual((x-.5,z-.5),(23,29))
  self.assertEqual(struct.unpack_from('<I',arc.files[self.report['lands'][1]],4)[0],0)
 def test_only_kanto_matrix_pointer_changes_and_every_original_member_remains(self):
  paths=('a/0/4/1','a/0/6/5');ids={self.before.filenames.idOf(p) for p in paths}
  for p in paths:
   a=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf(p)]);b=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf(p)]);self.assertEqual(a.files,b.files[:len(a.files)])
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(a,b)
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(TABLE+13*24+4,TABLE+13*24+6))|set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
 def test_permissions_models_and_height_data_unchanged(self):
  a=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf('a/0/6/5')]);b=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')]);mat=ndspy.narc.NARC(self.before.files[self.before.filenames.idOf('a/0/4/1')]);d=self.before.loadArm9().sections[0].data;oldids=struct.unpack_from('<2H',mat.files[struct.unpack_from('<H',d,TABLE+13*24+4)[0]],5)
  for oldid,newid in zip(oldids,self.report['lands']):
   raw=a.files[oldid];new=b.files[newid];ps,os,ms,bs,magic=struct.unpack_from('<5I',raw);nps,nos,nms,nbs,nmagic=struct.unpack_from('<5I',new)
   self.assertEqual((ps,ms,bs,magic),(nps,nms,nbs,nmagic));self.assertEqual(raw[20:20+ps],new[20:20+nps]);self.assertEqual(raw[20+ps+os:],new[20+nps+nos:])
 def test_mirrored_house_door_leaf_center_matches_yellow_warp(self):
  rom=ndspy.rom.NintendoDSRom(self.before.save());report=patch_probe_props(rom,diagnostic=True,scenery=True);arc=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')]);raw=arc.files[report['lands'][0]]
  ps,os=struct.unpack_from('<2I',raw);props={struct.unpack_from('<I',raw,at)[0]:struct.unpack_from('<12i',raw,at) for at in range(20+ps,20+ps+os,48)}
  house=props[276];door=props[286];self.assertEqual(house[7:10],(-4096,4096,5120));self.assertEqual(door[7:10],(-4096,4096,5120))
  x=16+door[1]/65536-.6875*door[7]/4096;z=16+door[3]/65536+.0625*door[9]/4096;self.assertEqual((x,z),(16.5,21.5))
  lower=arc.files[report['lands'][1]];self.assertEqual(struct.unpack_from('<I',lower,4)[0],48);gate=struct.unpack_from('<12i',lower,2068);self.assertEqual(gate[0],246)
  pivotz=48+gate[3]/65536;self.assertEqual((pivotz-6*gate[9]/4096,pivotz+2*gate[9]/4096),(29,33))
 def test_reproduces_native_tested_probe_and_requires_diagnostic(self):
  target=PROJECT/'build/0027-route5-native-props-v1/route5-native-props-probe.nds';self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256(target.read_bytes()).hexdigest())
  with self.assertRaises(ValueError):patch_probe_props(self.before)
if __name__=='__main__':unittest.main()
