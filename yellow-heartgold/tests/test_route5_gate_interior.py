"""Scope and roadblock checks for the private Yellow-sized native gate."""
import hashlib,json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from opening import events_decode
from route5_gate_interior import patch_small_gate
from viridian_tutorial import TABLE
class SmallGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-north-cliff-v2/private-terrain.nds'))
  cls.after=ndspy.rom.NintendoDSRom(cls.before.save())
  cls.topology=json.loads((PROJECT/'build/0027-yellow-gate-topology-v1/topology.json').read_text())
  cls.report=patch_small_gate(cls.after,cls.topology,diagnostic=True)
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
 def test_preserves_johto_all_other_maps_and_guard_code(self):
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  for offset in (4,16):allowed.update(range(TABLE+391*24+offset,TABLE+391*24+offset+2))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  self.assertEqual(len(a.sections),len(b.sections))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm7,self.after.arm7);self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable)
  ids={self.before.filenames.idOf(p) for p in ('a/0/4/1','a/0/6/5','a/0/3/2')}
  for i,(x,y) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(x,y)
 def test_all_original_resources_remain_exact(self):
  for p in ('a/0/4/1','a/0/6/5','a/0/3/2'):
   a=self.arc(self.before,p).files;b=self.arc(self.after,p).files
   self.assertEqual(b[:len(a)],a);self.assertEqual(len(b),len(a)+1)
 def test_four_returns_and_guard_corridor(self):
  g=events_decode(self.arc(self.after,'a/0/3/2').files[self.report['event']])
  self.assertEqual([struct.unpack('<4HI',w) for w in g[2]],[(3,5,13,2,0),(3,0,13,0,0),(4,5,13,2,0),(4,0,13,0,0)])
  self.assertEqual(struct.unpack_from('<2H',g[1][0],24),(1,3))
  self.assertEqual(struct.unpack('<Hhh5H',g[3][0]),(2,3,3,2,1,0,0,0))
  raw=self.arc(self.after,'a/0/6/5').files[self.report['land']];perms=struct.unpack_from('<1024H',raw,20)
  for c in self.topology['cells']:self.assertEqual(not bool(perms[c['y']*32+c['x']]&0x8000),c['walkable'])
  self.assertTrue(all(p==0x8000 for i,p in enumerate(perms) if i%32>=8 or i//32>=6))
 def test_native_flat_plane_and_exact_diagnostic_probe(self):
  before=self.arc(self.before,'a/0/6/5').files[242];after=self.arc(self.after,'a/0/6/5').files[self.report['land']]
  def collider(raw):ps,os,ms,bs,_=struct.unpack_from('<5I',raw);return raw[20+ps+os+ms:]
  a=collider(before);b=collider(after);self.assertEqual(a[:16],b[:16]);self.assertEqual(a[32:],b[32:])
  self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256((PROJECT/'build/0027-small-gate-v1/private-small-gate.nds').read_bytes()).hexdigest())
  with self.assertRaises(ValueError):patch_small_gate(self.before,self.topology)
 def test_double_sided_probe_only_changes_appended_visual_model(self):
  r=ndspy.rom.NintendoDSRom(self.before.save());report=patch_small_gate(r,self.topology,diagnostic=True,two_sided=True)
  a=self.arc(self.after,'a/0/6/5').files[report['land']];b=self.arc(r,'a/0/6/5').files[report['land']]
  ps,os,ms,bs,_=struct.unpack_from('<5I',a);self.assertEqual(a[:20+ps+os],b[:20+ps+os]);self.assertEqual(a[-bs:],b[-bs:])
  for p in ('a/0/4/1','a/0/3/2'):self.assertEqual(self.arc(r,p).files,self.arc(self.after,p).files)
  self.assertEqual(hashlib.sha256(r.save()).hexdigest(),hashlib.sha256((PROJECT/'build/0027-small-gate-v2/private-small-gate.nds').read_bytes()).hexdigest())
 def test_flat_color_fix_keeps_native_materials_and_gameplay_exact(self):
  colored=ndspy.rom.NintendoDSRom(self.before.save());report=patch_small_gate(colored,self.topology,diagnostic=True,two_sided=True,flat_vertex_colors=True)
  prior=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-small-gate-v2/private-small-gate.nds'))
  raw_a=self.arc(prior,'a/0/6/5').files[report['land']];raw_b=self.arc(colored,'a/0/6/5').files[report['land']]
  ps,os,ms,bs,_=struct.unpack_from('<5I',raw_a);self.assertEqual(raw_a[20:20+ps+os],raw_b[20:20+ps+os]);self.assertEqual(raw_a[-bs:],raw_b[-bs:])
  def materials(raw):
   ps,os,ms,bs,_=struct.unpack_from('<5I',raw);b=raw[20+ps+os:20+ps+os+ms];base=struct.unpack_from('<I',b,16)[0]+48;mo,so=struct.unpack_from('<2I',b,base+8);return b[base+mo:base+so]
  self.assertEqual(materials(raw_a),materials(raw_b))
  for p in ('a/0/4/1','a/0/3/2'):self.assertEqual(self.arc(prior,p).files,self.arc(colored,p).files)
  self.assertEqual(hashlib.sha256(colored.save()).hexdigest(),hashlib.sha256((PROJECT/'build/0027-small-gate-v6-colors/private-small-gate.nds').read_bytes()).hexdigest())
 def test_yellow_northern_anchors_and_no_johto_changes(self):
  r=ndspy.rom.NintendoDSRom(self.before.save());report=patch_small_gate(r,self.topology,diagnostic=True,two_sided=True,flat_vertex_colors=True,yellow_anchors=True)
  d=r.loadArm9().sections[0].data;g=events_decode(self.arc(r,'a/0/3/2').files[report['event']]);self.assertEqual(struct.unpack('<4HI',g[2][1]),(3,0,13,1,0));self.assertEqual(struct.unpack('<4HI',g[2][3]),(4,0,13,0,0))
  outside=events_decode(self.arc(r,'a/0/3/2').files[struct.unpack_from('<H',d,TABLE+13*24+16)[0]]);self.assertEqual([struct.unpack('<4HI',w) for w in outside[2][:2]],[(1300,186,391,3,0),(1299,186,391,1,0)])
  before=self.before.loadArm9();after=r.loadArm9();allowed=set(range(before.codeSettingsOffs+20,before.codeSettingsOffs+24))
  for m,o in ((391,4),(391,16),(13,16)):allowed.update(range(TABLE+m*24+o,TABLE+m*24+o+2))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(before.sections[0].data,after.sections[0].data)) if x!=y))
  ids={self.before.filenames.idOf(p) for p in ('a/0/4/1','a/0/6/5','a/0/3/2')}
  for i,(x,y) in enumerate(zip(self.before.files,r.files)):
   if i not in ids:self.assertEqual(x,y)
  for p in ('a/0/4/1','a/0/6/5','a/0/3/2'):
   a=self.arc(self.before,p).files;b=self.arc(r,p).files;self.assertEqual(a,b[:len(a)])
  self.assertEqual(hashlib.sha256(r.save()).hexdigest(),hashlib.sha256((PROJECT/'build/0027-small-gate-v7-anchors/private-small-gate.nds').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
