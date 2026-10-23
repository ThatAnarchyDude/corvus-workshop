"""Scope and geometry checks for the compact connected Kanto map."""
import unittest,sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from route5_connected import patch_connected_probe,matrix_offset,DOORS
from opening import events_decode
from viridian_tutorial import TABLE
from build_rom import PROJECT
class ConnectedRoute(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());source=json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text());cls.report=patch_connected_probe(cls.after,source,diagnostic=True)
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
 def test_main_matrix_changes_only_two_kanto_land_references(self):
  a=self.arc(self.before,'a/0/4/1').files[0];b=self.arc(self.after,'a/0/4/1').files[0];allowed=set()
  for x,z in ((40,5),(40,6)):at=matrix_offset(a,x,z);allowed.update((at,at+1))
  self.assertEqual(len(a),len(b));self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a,b)) if x!=y))
  d=self.after.loadArm9().sections[0].data;self.assertEqual(struct.unpack_from('<H',d,TABLE+13*24+4)[0],0);self.assertEqual(d[TABLE+13*24+1],13)
  for m in (52,59):self.assertEqual(self.before.loadArm9().sections[0].data[TABLE+m*24:TABLE+(m+1)*24],d[TABLE+m*24:TABLE+(m+1)*24])
 def test_world_coordinate_doors_and_original_interior_actors(self):
  a=self.before.loadArm9().sections[0].data;b=self.after.loadArm9().sections[0].data
  g=events_decode(self.arc(self.after,'a/0/3/2').files[struct.unpack_from('<H',b,TABLE+13*24+16)[0]])
  self.assertEqual([struct.unpack('<4HI',w) for w in g[2]],[(1300,186,391,1,0),(1299,186,391,1,0),(1300,190,391,0,0),(1307,184,469,0,0),(1300,178,517,0,0)]);self.assertFalse(g[3])
  for m in (391,469,517):
   before=events_decode(self.arc(self.before,'a/0/3/2').files[struct.unpack_from('<H',a,TABLE+m*24+16)[0]]);after=events_decode(self.arc(self.after,'a/0/3/2').files[struct.unpack_from('<H',b,TABLE+m*24+16)[0]])
   for i in (0,1,3):self.assertEqual(before[i],after[i])
 def test_grass_ledges_height_and_saffron_corridor(self):
  a=self.arc(self.after,'a/0/6/5');raw=a.files[self.report['route_land']];ps,os,ms,bs,_=struct.unpack_from('<5I',raw);p=struct.unpack_from('<1024H',raw,20)
  self.assertEqual(sum(v&0x80ff==2 for v in p),48);self.assertEqual(sum(v&0x80ff==0x803b for v in p),40)
  self.assertEqual(struct.unpack_from('<i',raw,20+ps+os+ms+44)[0],-131072)
  for x,z,_,_,behavior in DOORS:self.assertEqual(p[z*32+x+10],behavior|0x400)
  city=a.files[self.report['saffron_land']]
  for z in range(8):
   for x in (20,21):self.assertEqual(struct.unpack_from('<H',city,20+2*(z*32+x))[0],0x400)
 def test_no_johto_header_or_executable_changes(self):
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  for m in (13,391,469,517):allowed.update(range(TABLE+m*24+16,TABLE+m*24+18))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
  areas=self.arc(self.after,'a/0/4/2');d=b.sections[0].data
  for m in range(540):
   if struct.unpack_from('<H',areas.files[d[TABLE+m*24+1]])[0]==12:self.assertTrue(d[TABLE+m*24+20]&1)
 def test_original_archive_members_preserved_except_scoped_kanto_tables(self):
  paths=('a/0/4/0','a/0/4/2','a/0/4/3','a/0/4/1','a/0/6/5','a/1/0/7','a/0/7/0','a/0/3/2');ids={self.before.filenames.idOf(p) for p in paths}|{self.before.filenames.idOf('fielddata/build_model/bm_field_matshp.dat')}
  for p in paths:
   a=self.arc(self.before,p).files;b=self.arc(self.after,p).files
   for i,member in enumerate(a):
    if (p,i) not in (('a/0/4/1',0),('a/0/4/3',12)):self.assertEqual(member,b[i])
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(a,b)
  original=self.arc(self.before,'a/0/4/3').files[12];updated=self.arc(self.after,'a/0/4/3').files[12];self.assertEqual(original[2:],updated[2:len(original)]);self.assertEqual(len(updated),len(original)+6)
  fid=self.before.filenames.idOf('fielddata/build_model/bm_field_matshp.dat');a=self.before.files[fid];b=self.after.files[fid];count,shapes=struct.unpack_from('<2H',a);newcount,newshapes=struct.unpack_from('<2H',b);self.assertEqual((newcount,newshapes),(count+3,shapes));self.assertEqual(a[4:4+4*count],b[4:4+4*count]);self.assertEqual(a[4+4*count:],b[4+4*newcount:])
 def test_reproduces_native_probe_and_requires_diagnostic(self):
  target=PROJECT/'build/0027-connected-route5-v1/connected-route5-private.nds';self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256(target.read_bytes()).hexdigest())
  with self.assertRaises(ValueError):patch_connected_probe(self.before,{})
if __name__=='__main__':unittest.main()
