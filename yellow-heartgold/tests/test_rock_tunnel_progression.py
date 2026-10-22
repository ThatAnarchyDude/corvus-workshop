import sys,struct,json,unittest
from pathlib import Path
from collections import deque
sys.path.insert(0,'yellow-heartgold/tools')
import ndspy.rom,ndspy.narc
from opening import events_decode
from viridian_tutorial import TABLE
from forest_progression import SLOT_MAP
class TunnelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  root=Path('yellow-heartgold/build');cls.old=ndspy.rom.NintendoDSRom.fromFile(str(root/'0036-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0036.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(root/'0037-rock-tunnel-v2/private-rock-tunnel.nds'));cls.report=json.loads((root/'0037-rock-tunnel-v2/report.json').read_text())['maps'];cls.refs={n:json.loads((root/('0035-route10-audit-v1/'+n+'.json')).read_text()) for n in ('RockTunnel1F','RockTunnelB1F')}
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
 def test_all_fifteen_yellow_teams_and_moves(self):
  expected=[[(74,19),(66,19),(74,19),(74,19)],[(95,20),(95,20),(74,20)],[(74,21),(75,21)],[(104,23),(79,23)],[(69,22),(35,22)],[(52,20),(43,20),(16,20)],[(16,19),(19,19),(19,19),(69,19)],[(39,21),(16,21),(52,21)],[(74,21),(74,21),(75,21)],[(79,20),(79,20),(79,20)],[(4,22),(104,22)],[(74,25)],[(43,22),(1,22)],[(66,20),(95,20)],[(79,25)]]
  entries=[t for m in self.report for t in m['trainers']];self.assertEqual(len(entries),15)
  for t,team in zip(entries,expected):
   rows=list(struct.iter_unpack('<BB3H4H',self.arc(self.new,'a/0/5/6')[t['id']]))
   self.assertEqual([(r[3],r[2]) for r in rows],team);self.assertEqual([list(r[5:]) for r in rows],[p['moves'] for p in t['team']])
 def test_actors_reachable_from_native_ladders_without_blocking_connections(self):
  for report in self.report:
   m=report['map'];old=events_decode(self.arc(self.old,'a/0/3/2')[report['original_event']]);new=events_decode(self.arc(self.new,'a/0/3/2')[report['event']]);self.assertEqual(old[0],new[0]);self.assertEqual(old[2:],new[2:])
   for a in old[1]:self.assertIn(a,new[1])
   grid=Path(f'yellow-heartgold/build/0035-route10-audit-v1/{m}-grid.txt').read_text().splitlines();floor={(x,y) for x in range(5,49) for y in range(5,38) if grid[y][x]=='.'};warps={tuple(struct.unpack_from('<2H',w)) for w in old[2]};blocked={tuple(struct.unpack_from('<2H',a,24)) for a in old[1]}
   def reach(start,blocks):
    q=deque([start]);seen={start}
    while q:
     x,y=q.popleft()
     for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
      if p in floor and p not in blocks and p not in seen:seen.add(p);q.append(p)
    return seen
   accessible=set().union(*(reach(p,blocked) for p in warps if p in floor));positions={tuple(p) for p in report['positions']};self.assertTrue(positions<=accessible)
   for p in warps&floor:self.assertEqual(reach(p,blocked)&warps,reach(p,blocked|positions)&warps)
   ids=[struct.unpack_from('<H',a)[0] for a in new[1]];self.assertEqual(len(ids),len(set(ids)))
   scripts=[struct.unpack_from('<H',a,10)[0]-2999 for a in new[1] if 3000<=struct.unpack_from('<H',a,10)[0]<4000];self.assertCountEqual(scripts,[t['id'] for t in report['trainers']])
 def test_yellow_grass_all_periods_and_special_replacements(self):
  for report in self.report:
   ref=self.refs[report['name']];slots=[ref['grass'][i] for i in SLOT_MAP];row=self.arc(self.new,'a/0/3/7')[report['wild']];self.assertEqual(row[:6],bytes([15,0,0,0,0,0]));self.assertEqual(row[8:20],bytes(p['level'] for p in slots))
   for i in range(3):self.assertEqual(struct.unpack_from('<12H',row,20+24*i),tuple(p['species'] for p in slots))
   for at in (0x5C,0x60,0x64,0x68,0xBC):self.assertEqual(struct.unpack_from('<2H',row,at),(slots[0]['species'],slots[1]['species']))
 def test_unrelated_files_old_archive_entries_and_headers_preserved(self):
  paths=('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1','a/0/3/2','a/0/3/7');allowed={self.old.filenames.idOf(p) for p in paths}
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in allowed:self.assertEqual(a,b,f'file{i}')
  for p in ('a/0/1/2','a/0/3/2','a/0/3/7','a/0/5/5','a/0/5/6'):a=self.arc(self.old,p);self.assertEqual(self.arc(self.new,p)[:len(a)],a)
  a=self.old.loadArm9();b=self.new.loadArm9();expected=bytearray(a.sections[0].data);ranges=[(a.codeSettingsOffs+20,4)]
  for report in self.report:ranges.extend([(TABLE+report['map']*24,1),(TABLE+report['map']*24+16,2)]+[(at+2,2) for at in report['common_sites']])
  for at,size in ranges:expected[at:at+size]=b.sections[0].data[at:at+size]
  self.assertEqual(expected,b.sections[0].data)
if __name__=='__main__':unittest.main()
