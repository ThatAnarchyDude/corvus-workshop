import sys,struct,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from opening import events_decode
from viridian_tutorial import TABLE
from forest_progression import SLOT_MAP
class Route10Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0034-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0034.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0035-route10-v1/private-route10.nds'));cls.report=json.loads((PROJECT/'build/0035-route10-v1/report.json').read_text());cls.ref=json.loads((PROJECT/'build/0035-route10-audit-v1/Route10.json').read_text())
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
 def test_exact_yellow_teams_and_explicit_moves(self):
  expected=[[(111,30),(108,30)],[(74,21),(95,21)],[(104,20),(79,20)],[(39,20),(35,20)],[(95,19),(75,19)],[(16,21),(17,21)]]
  for t,team in zip(self.report['trainers'],expected):
   rows=list(struct.iter_unpack('<BB3H4H',self.arc(self.new,'a/0/5/6')[t['id']]))
   self.assertEqual([(r[3],r[2]) for r in rows],team);self.assertEqual([list(r[5:]) for r in rows],[p['moves'] for p in t['team']])
 def test_north_south_dispatch_and_warps_preserved(self):
  alltrainers=[]
  for m in self.report['maps']:
   a=events_decode(self.arc(self.old,'a/0/3/2')[m['original_event']]);b=events_decode(self.arc(self.new,'a/0/3/2')[m['event']]);self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:]);ids=[struct.unpack_from('<H',p)[0] for p in b[1]];self.assertEqual(len(ids),len(set(ids)))
   for p in a[1]:
    if not 3000<=struct.unpack_from('<H',p,10)[0]<4000:self.assertIn(p,b[1])
   for p in b[1]:
    script=struct.unpack_from('<H',p,10)[0]
    if 3000<=script<4000:alltrainers.append(script-2999)
  self.assertCountEqual(alltrainers,[t['id'] for t in self.report['trainers']]);self.assertEqual([m for m,x,y in self.report['positions']],[18,388,388,18,388,388])
 def test_yellow_grass_all_times_without_surf_grants(self):
  row=self.arc(self.new,'a/0/3/7')[self.report['wild']];slots=[self.ref['grass'][i] for i in SLOT_MAP];self.assertEqual(row[:6],bytes([15,0,0,0,0,0]));self.assertEqual(row[8:20],bytes(p['level'] for p in slots))
  for i in range(3):self.assertEqual(struct.unpack_from('<12H',row,20+24*i),tuple(p['species'] for p in slots))
 def test_unrelated_maps_code_and_existing_archive_entries_preserved(self):
  paths=('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1','a/0/3/2','a/0/3/7');allowed={self.old.filenames.idOf(p) for p in paths}
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in allowed:self.assertEqual(a,b,f'file{i}')
  for p in ('a/0/1/2','a/0/3/2','a/0/3/7','a/0/5/5','a/0/5/6'):a=self.arc(self.old,p);self.assertEqual(self.arc(self.new,p)[:len(a)],a)
  a=self.old.loadArm9();b=self.new.loadArm9();expected=bytearray(a.sections[0].data)
  for at,size in [(a.codeSettingsOffs+20,4),(TABLE+18*24,1),(TABLE+18*24+16,2),(TABLE+388*24+16,2)]+[(at+2,2) for at in self.report['common_sites']]:expected[at:at+size]=b.sections[0].data[at:at+size]
  self.assertEqual(expected,b.sections[0].data)
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
if __name__=='__main__':unittest.main()
