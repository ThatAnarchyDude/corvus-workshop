import sys,struct,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from opening import events_decode
from viridian_tutorial import TABLE
from forest_progression import SLOT_MAP
from prototype import decode_messages
class Route9Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0033-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0033.nds'))
  cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0034-route9-v1/private-route9.nds'))
  cls.report=json.loads((PROJECT/'build/0034-route9-v1/report.json').read_text())
  cls.ref=json.loads((PROJECT/'build/0034-route-audit-v1/yellow-route9-reference.json').read_text())
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
 def test_all_nine_yellow_teams_and_moves(self):
  teams=[[(43,18),(69,18),(43,18),(69,18)],[(27,24)],[(19,19),(50,19),(23,19),(27,19)],[(52,23)],[(66,20),(95,20)],[(74,20),(66,20),(74,20)],[(15,19),(15,19)],[(74,21),(95,21)],[(10,20),(13,20),(48,20)]]
  for entry,expected in zip(self.report['trainers'],teams):
   tid=entry['id'];data=self.arc(self.new,'a/0/5/6')[tid];rows=list(struct.iter_unpack('<BB3H4H',data))
   self.assertEqual([(r[3],r[2]) for r in rows],expected);self.assertEqual([list(r[5:]) for r in rows],[m['moves'] for m in entry['team']]);self.assertLess(tid,1000)
  aj=self.arc(self.new,'a/0/5/6')[self.report['trainers'][1]['id']];self.assertEqual(struct.unpack('<BB3H4H',aj)[5:],(10,28,163,40))
 def test_actors_gate_and_native_transitions_preserved(self):
  d=self.old.loadArm9().sections[0].data;eid=struct.unpack_from('<H',d,TABLE+17*24+16)[0]
  a=events_decode(self.arc(self.old,'a/0/3/2')[eid]);b=events_decode(self.arc(self.new,'a/0/3/2')[self.report['event']])
  self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:]);actors={struct.unpack_from('<H',r)[0]:r for r in b[1]};self.assertEqual(len(actors),len(b[1]))
  for i,t in enumerate(self.report['trainers']):
   row=actors[i];self.assertEqual(struct.unpack_from('<H',row,10)[0],3000+t['id']-1);self.assertEqual(struct.unpack_from('<2H',row,24),tuple(self.report['positions'][i]));self.assertEqual(struct.unpack_from('<H',row,14)[0],t['vision'])
  for obj,x in ((9,1347),(10,1348)):
   row=actors[obj];self.assertEqual(struct.unpack_from('<H',row,2)[0],86);self.assertEqual(struct.unpack_from('<H',row,10)[0],10000);self.assertEqual(struct.unpack_from('<2H',row,24),(x,143))
 def test_yellow_encounters_all_times_and_original_tables_kept(self):
  old=self.arc(self.old,'a/0/3/7');new=self.arc(self.new,'a/0/3/7');self.assertEqual(new[:len(old)],old)
  row=new[self.report['wild']];self.assertEqual(row[:6],bytes([15,0,0,0,0,0]));slots=[self.ref['grass'][i] for i in SLOT_MAP]
  self.assertEqual(row[8:20],bytes(s['level'] for s in slots))
  for period in range(3):self.assertEqual(struct.unpack_from('<12H',row,20+24*period),tuple(s['species'] for s in slots))
 def test_unrelated_files_and_map_headers_preserved(self):
  paths=('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1','a/0/3/2','a/0/3/7');ids={self.old.filenames.idOf(p) for p in paths}
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in ids:self.assertEqual(a,b,f'file {i}')
  old=self.old.loadArm9();new=self.new.loadArm9()
  for i,(a,b) in enumerate(zip(old.sections,new.sections)):
   if i:self.assertEqual(a.data,b.data)
   else:
    expected=bytearray(a.data);meta=old.codeSettingsOffs+20;expected[meta:meta+4]=b.data[meta:meta+4]
    for at,size in [(TABLE+17*24,1),(TABLE+17*24+16,2)]+[(at+2,2) for at in self.report['common_sites']]:expected[at:at+size]=b.data[at:at+size]
    self.assertEqual(expected,b.data)
  for p in ('a/0/3/2','a/0/1/2','a/0/5/5','a/0/5/6'):
   a=self.arc(self.old,p);b=self.arc(self.new,p);self.assertEqual(b[:len(a)],a)
if __name__=='__main__':unittest.main()
