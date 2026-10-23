import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from ss_anne_topology import extract
SOURCE=Path('/mnt/c/Users/thata/Desktop/The Lab/Psyduck Yellow Stuff/Project Recovery/pokeyellow-master/pokeyellow-master/data/maps/objects')

class TopologyTests(unittest.TestCase):
    def copy_source(self, target):
        for source in SOURCE.glob('SSAnne*.asm'):
            (target/source.name).write_bytes(source.read_bytes())
    def test_cabins_and_double_doors(self):
        report=extract(SOURCE)
        self.assertEqual(report['cabin_count'],17)
        self.assertEqual(report['logical_room_count'],24)
        self.assertFalse(report['native_walkability_verified'])
        edges=report['directed_internal_doorways']
        self.assertEqual(len({e['source'] for e in edges if e['source'].startswith('SS_ANNE_2F_ROOMS:')}),6)
    def test_invalid_destination_anchor_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); self.copy_source(root)
            path=root/'SSAnne1F.asm'
            path.write_text(path.read_text().replace('SS_ANNE_1F_ROOMS, 1','SS_ANNE_1F_ROOMS, 99'))
            with self.assertRaises(AssertionError): extract(root)
    def test_cabin_return_to_wrong_cabin_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); self.copy_source(root)
            path=root/'SSAnne1FRooms.asm'
            path.write_text(path.read_text().replace('SS_ANNE_1F, 3','SS_ANNE_1F, 4'))
            with self.assertRaises(AssertionError): extract(root)

if __name__=='__main__': unittest.main()
