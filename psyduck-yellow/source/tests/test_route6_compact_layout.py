import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from route6_compact_layout import compact_layout

class Route6CompactLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=PROJECT/'build/0029-route6-foundation-v1'
        cls.source=json.loads((root/'yellow-topology.json').read_text());cls.trainers=json.loads((root/'trainer-reference.json').read_text())['trainers']
    def test_functional_features_and_water_regions_preserved(self):
        out=compact_layout(self.source,self.trainers)
        self.assertEqual(out['dimensions'],[20,32]);self.assertEqual(len(out['cells']),640)
        self.assertEqual(sum(c['collision_tile']==82 for c in out['cells']),sum(c['collision_tile']==82 for c in self.source['cells']))
        self.assertEqual(len(out['one_way_ledges']),len(self.source['one_way_ledges']))
        self.assertEqual(len(out['warps']),4);self.assertEqual(len(out['trainers']),6)
        self.assertEqual(len(out['water_region_sizes']['original']),2);self.assertEqual(len(out['water_region_sizes']['compact']),2)
        for t in out['trainers']:
            c=next(c for c in out['cells'] if [c['x'],c['y']]==t['position']);self.assertTrue(c['walkable'])
        self.assertEqual(out['trainers'][0]['position'][1],out['trainers'][1]['position'][1])
        self.assertEqual(out['trainers'][3]['position'][1]-out['trainers'][4]['position'][1],1)
    def test_nonrepeated_functional_row_rejected_and_input_unchanged(self):
        original=copy.deepcopy(self.source);compact_layout(self.source,self.trainers);self.assertEqual(self.source,original)
        bad=copy.deepcopy(self.source);next(c for c in bad['cells'] if c['x']==0 and c['y']==9)['collision_tile']=82
        with self.assertRaises(ValueError):compact_layout(bad,self.trainers)

if __name__=='__main__':unittest.main()
