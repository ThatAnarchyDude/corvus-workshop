import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from route6_yellow_reference import trainer_reference
SOURCE=Path('/mnt/c/Users/thata/Desktop/The Lab/Psyduck Yellow Stuff/Project Recovery/pokeyellow-master/pokeyellow-master')

@unittest.skipUnless(SOURCE.exists(),'Requires local read-only Yellow reference source')
class Route6YellowReference(unittest.TestCase):
    def test_six_source_teams_and_vision(self):
        r=trainer_reference(SOURCE);t=r['trainers']
        self.assertEqual([[(m['species'],m['level']) for m in e['team']] for e in t],
                         [[(70,16)],[(104,20)],[(13,16),(10,16),(13,16)],[(21,16),(20,16)],[(16,16)]*3,[(12,20)]])
        self.assertEqual([e['vision'] for e in t],[0,0,4,3,3,3])
        self.assertEqual(t[0]['team'][0]['moves'],[22,74,35,77])
        self.assertEqual(t[-1]['team'][0]['moves'],[77,78,79,48])
        self.assertEqual(t[1]['team'][0]['moves'],[45,125,39,29])
        self.assertEqual(t[0]['messages']['BattleText'],"I'm doing this out of love. Leave me alone!")
        self.assertIn('data/trainers/parties.asm',r['source_sha256'])

if __name__=='__main__':unittest.main()
