"""Verify shortening retains all functional source features and gate progression."""
import unittest,sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from route5_compact_layout import compact_layout,REMOVE_ROWS,BUILDING_ROWS
from build_rom import PROJECT
class CompactLayout(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.source=json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text());cls.compact=compact_layout(cls.source)
 def test_complete_grid_and_source_not_mutated(self):
  before=copy.deepcopy(self.source);out=compact_layout(self.source);self.assertEqual(self.source,before);self.assertEqual(out['dimensions'],[20,32]);self.assertEqual(len(out['cells']),640);self.assertEqual({(c['x'],c['y']) for c in out['cells']},{(x,y) for x in range(20) for y in range(32)})
 def test_all_grass_and_ledges_retained(self):
  self.assertEqual(sum(c['collision_tile']==82 for c in self.compact['cells']),48);self.assertEqual(len(self.compact['one_way_ledges']),40)
  for old,new in zip(self.source['one_way_ledges'],self.compact['one_way_ledges']):
   self.assertEqual(old['ledge'][0],new['ledge'][0]);self.assertEqual(new['start'],[new['ledge'][0],new['ledge'][1]-1]);self.assertEqual(new['landing'],[new['ledge'][0],new['ledge'][1]+1])
 def test_buildings_and_door_progression_retained(self):
  self.assertFalse(set(REMOVE_ROWS)&BUILDING_ROWS);self.assertEqual([w['position'] for w in self.compact['warps']],[[10,26],[9,26],[10,30],[17,24],[10,18]])
  self.assertEqual([w['reachable_from_north'] for w in self.compact['warps']],[True,True,False,True,True]);self.assertEqual(self.compact['sign_position'],[17,26])
  original={(c['x'],c['y']):c for c in self.source['cells']}
  for c in self.compact['cells']:self.assertEqual(c['collision_tile'],original[tuple(c['source_position'])]['collision_tile'])
 def test_refuse_removal_of_functional_features(self):
  p=copy.deepcopy(self.source);next(c for c in p['cells'] if c['y']==2)['collision_tile']=82
  with self.assertRaises(ValueError):compact_layout(p)
  p=copy.deepcopy(self.source);p['one_way_ledges'][0]['ledge'][1]=14
  with self.assertRaises(ValueError):compact_layout(p)
  p=copy.deepcopy(self.source);p['warps'][0]['position'][1]=34
  with self.assertRaises(ValueError):compact_layout(p)
if __name__=='__main__':unittest.main()
