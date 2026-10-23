"""Protect Yellow progression while aligning the native northern approach."""
import sys,json,struct,unittest
from pathlib import Path
from collections import deque
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route5_connected import patch_connected_probe
from route5_compact_layout import compact_layout
class NorthAccess(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text());snapshot=json.dumps(cls.source,sort_keys=True)
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-native-trees-ledges-v2/private-terrain.nds'));cls.after=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'));cls.report=patch_connected_probe(cls.after,cls.source,diagnostic=True,native_trees=True,visible_ledges=True,north_access=True);assert json.dumps(cls.source,sort_keys=True)==snapshot
 def test_only_two_boundary_permissions_and_rendered_tree_change(self):
  fid=self.before.filenames.idOf('a/0/6/5')
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i!=fid:self.assertEqual(a,b)
  self.assertEqual(self.before.arm9,self.after.arm9);self.assertEqual(self.before.arm7,self.after.arm7)
  a=ndspy.narc.NARC(self.before.files[fid]);b=ndspy.narc.NARC(self.after.files[fid]);lid=self.report['route_land'];self.assertEqual(len(a.files),len(b.files))
  for i,(x,y) in enumerate(zip(a.files,b.files)):
   if i not in (691,692,693):self.assertEqual(x,y)
  x,y=a.files[lid],b.files[lid];xp,xo,xm,xb,_=struct.unpack_from('<5I',x);yp,yo,ym,yb,_=struct.unpack_from('<5I',y);px=struct.unpack_from('<1024H',x,20);py=struct.unpack_from('<1024H',y,20)
  self.assertEqual([i for i in range(1024) if px[i]!=py[i]],[15,24]);self.assertEqual([py[15],py[24]],[0x400,0x400]);self.assertEqual(x[20+xp:20+xp+xo],y[20+yp:20+yp+yo]);self.assertEqual(x[20+xp+xo+xm:],y[20+yp+yo+ym:]);self.assertEqual(self.report['native_tree_count'],48)
  self.assertEqual(sum(v&0x80ff==2 for v in py),48);self.assertEqual(sum(v&0x80ff==0x803b for v in py),40)
 def test_side_stair_reaches_daycare_without_opening_south_gate(self):
  p=compact_layout(self.source);walk={(c['x'],c['y']) for c in p['cells'] if c['walkable']}|{(5,0),(14,0)};jumps={tuple(e['start']):tuple(e['landing']) for e in p['one_way_ledges']};seen={(2,0)};q=deque(seen)
  while q:
   x,z=q.popleft()
   for a in [(x-1,z),(x+1,z),(x,z-1),(x,z+1)]+([jumps[(x,z)]] if (x,z) in jumps else []):
    if a in walk and a not in seen:seen.add(a);q.append(a)
  self.assertIn((10,19),seen);self.assertIn((17,25),seen);self.assertNotIn((10,30),seen)
 def test_reproduces_new_private_probe(self):
  self.assertEqual(self.after.save(),(PROJECT/'build/0027-native-north-access-v1/private-terrain.nds').read_bytes())
if __name__=='__main__':unittest.main()
