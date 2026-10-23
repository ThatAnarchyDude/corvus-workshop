"""Protect collision and resource scope when enabling native Route 5 trees."""
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route5_connected import patch_connected_probe
from ndspy import _common
class NativeTrees(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.plain=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-connected-route5-v1/connected-route5-private.nds'))
  cls.trees=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'))
  cls.report=patch_connected_probe(cls.trees,json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text()),diagnostic=True,native_trees=True,visible_ledges=getattr(cls,"visible_ledges",False))
 def test_all_yellow_tree_positions_rendered(self):
  self.assertEqual(self.report['native_tree_count'],49)
  arc=ndspy.narc.NARC(self.trees.files[self.trees.filenames.idOf('a/0/6/5')]);raw=arc.files[self.report['route_land']];ps,os,ms,_,_=struct.unpack_from('<5I',raw);bmd=raw[20+ps+os:20+ps+os+ms];mdlo=struct.unpack_from('<I',bmd,16)[0];base=mdlo+struct.unpack('<I',_common.loadInfoBlock(bmd,mdlo+8,4)[0][3])[0]
  self.assertEqual(bmd[base+25],4) # Three original terrain meshes plus canopy.
 def test_permissions_props_collision_and_all_other_resources_identical(self):
  fid=self.plain.filenames.idOf('a/0/6/5')
  for i,(a,b) in enumerate(zip(self.plain.files,self.trees.files)):
   if i!=fid:self.assertEqual(a,b)
  self.assertEqual(self.plain.arm9,self.trees.arm9);self.assertEqual(self.plain.arm7,self.trees.arm7)
  a=ndspy.narc.NARC(self.plain.files[fid]);b=ndspy.narc.NARC(self.trees.files[fid]);self.assertEqual(len(a.files),len(b.files))
  for old,new in zip(a.files,b.files):
   ps,os,ms,bs,magic=struct.unpack_from('<5I',old);nps,nos,nms,nbs,nmagic=struct.unpack_from('<5I',new)
   self.assertEqual((ps,os,bs,magic),(nps,nos,nbs,nmagic));self.assertEqual(old[20:20+ps+os],new[20:20+nps+nos]);self.assertEqual(old[20+ps+os+ms:],new[20+nps+nos+nms:])
 def test_private_probe_reproduced(self):
  target=PROJECT/('build/0027-native-trees-ledges-v2/private-terrain.nds' if getattr(self,'visible_ledges',False) else 'build/0027-native-trees-connected-v1/connected-native-trees-private.nds');self.assertEqual(self.trees.save(),target.read_bytes())
class NativeTreesWithLedgedWalls(NativeTrees):
 visible_ledges=True

if __name__=='__main__':unittest.main()
