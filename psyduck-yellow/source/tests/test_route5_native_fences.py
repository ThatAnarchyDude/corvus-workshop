"""Native fence artwork must not change collision, event or original assets."""
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from ndspy import _common
from build_rom import PROJECT
from route5_connected import patch_connected_probe
class NativeFences(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-native-north-access-v1/private-terrain.nds'));cls.after=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'));cls.report=patch_connected_probe(cls.after,json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text()),diagnostic=True,native_trees=True,visible_ledges=True,north_access=True,native_fences=True)
 def test_art_only_preserves_all_gameplay_resources(self):
  fid=self.before.filenames.idOf('a/0/6/5')
  self.assertEqual(self.before.arm9,self.after.arm9);self.assertEqual(self.before.arm7,self.after.arm7)
  for i,(x,y) in enumerate(zip(self.before.files,self.after.files)):
   if i!=fid:self.assertEqual(x,y)
  a=ndspy.narc.NARC(self.before.files[fid]);b=ndspy.narc.NARC(self.after.files[fid]);self.assertEqual(len(a.files),len(b.files))
  for x,y in zip(a.files,b.files):
   xp,xo,xm,xb,xt=struct.unpack_from('<5I',x);yp,yo,ym,yb,yt=struct.unpack_from('<5I',y);self.assertEqual((xp,xo,xb,xt),(yp,yo,yb,yt));self.assertEqual(x[20:20+xp+xo],y[20:20+yp+yo]);self.assertEqual(x[20+xp+xo+xm:],y[20+yp+yo+ym:])
 def test_fence_mesh_has_valid_fifth_node_and_native_material(self):
  self.assertEqual(self.report['native_fence_count'],64);self.assertEqual(self.report['native_tree_count'],48)
  a=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')]);raw=a.files[self.report['route_land']];ps,os,ms,_,_=struct.unpack_from('<5I',raw);b=raw[20+ps+os:20+ps+os+ms];mdlo=struct.unpack_from('<I',b,16)[0];base=mdlo+struct.unpack('<I',_common.loadInfoBlock(b,mdlo+8,4)[0][3])[0]
  self.assertEqual((b[base+23],b[base+25]),(5,5));self.assertEqual(len(_common.loadInfoBlock(b,base+64,4)),5)
  sbc,mat=struct.unpack_from('<2I',b,base+4);commands=b[base+sbc:base+mat];self.assertIn(bytes([4,15,11,5,4,43]),commands)
 def test_reproduces_private_probe(self):
  self.assertEqual(self.after.save(),(PROJECT/'build/0027-native-fences-v1/private-terrain.nds').read_bytes())
if __name__=='__main__':unittest.main()
