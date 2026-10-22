"""Read-only Yellow source references for the smaller Kanto gate interior."""
import hashlib,json,sys,unittest
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from yellow_layout_reference import read_layout
from yellow_walk_topology import topology
SOURCE=next((p for p in (
 Path('/mnt/c/Users/thata/Desktop/The Lab/Psyduck Yellow Stuff/Project Recovery/pokeyellow-master/pokeyellow-master'),
 Path('C:/Users/thata/Desktop/The Lab/Psyduck Yellow Stuff/Project Recovery/pokeyellow-master/pokeyellow-master')) if p.exists()),None)
@unittest.skipIf(SOURCE is None,'Read-only Yellow source unavailable')
class GateReference(unittest.TestCase):
 def test_overworld_references_remain_exact(self):
  old=json.loads((PROJECT/'build/0026-route5-yellow-reference/layout.json').read_text())
  actual,_=read_layout(SOURCE,'Route5');self.assertEqual(actual,old)
  old=json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text())
  actual,_=topology(SOURCE,'Route5');self.assertEqual(actual,old)
 def test_gate_uses_its_declared_tileset_and_dimensions(self):
  layout,image=read_layout(SOURCE,'Route5Gate')
  self.assertEqual(layout['blocks'],[4,3]);self.assertEqual(layout['logical_tiles'],[8,6])
  self.assertEqual(image.size,(128,96));self.assertEqual(len(layout['cells']),48)
  self.assertIn('gfx/blocksets/gate.bst',layout['source_sha256'])
  self.assertIn('gfx/tilesets/gate.png',layout['source_sha256'])
  self.assertNotIn('gfx/blocksets/overworld.bst',layout['source_sha256'])
  self.assertIn('object_event  1,  3, SPRITE_GUARD',layout['events_source'])
 def test_gate_collision_and_warp_semantics(self):
  data,_=topology(SOURCE,'Route5Gate')
  self.assertEqual(data['passable_tiles'],[1,18,20,26,28,55,56,59,60,94])
  self.assertEqual((data['walkable_count'],data['north_reachable_count']),(22,16))
  self.assertEqual(data['one_way_ledges'],[])
  self.assertEqual([w['position'] for w in data['warps']],[[3,5],[4,5],[3,0],[4,0]])
  self.assertEqual([w['entry'] for w in data['warps']],[3,3,2,1])
  self.assertTrue(all(w['walkable'] for w in data['warps']))
 def test_guard_trigger_is_a_complete_cut_in_the_corridor(self):
  data,_=topology(SOURCE,'Route5Gate')
  walk={(c['x'],c['y']) for c in data['cells'] if c['walkable']}
  triggers={(3,3),(4,3)}
  def reachable(blocked):
   found={(3,0),(4,0)};queue=deque(found)
   while queue:
    x,y=queue.popleft()
    for q in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
     if q in walk and q not in blocked and q not in found:found.add(q);queue.append(q)
   return found
  self.assertTrue({(3,5),(4,5)}<=reachable(set()))
  self.assertFalse({(3,5),(4,5)}&reachable(triggers))
 def test_readers_preserve_source_and_reject_path_traversal(self):
  data,_=topology(SOURCE,'Route5Gate')
  for path,checksum in data['source_sha256'].items():
   self.assertEqual(hashlib.sha256((SOURCE/path).read_bytes()).hexdigest(),checksum)
  with self.assertRaises(ValueError):read_layout(SOURCE,'../Route5Gate')
if __name__=='__main__':unittest.main()
