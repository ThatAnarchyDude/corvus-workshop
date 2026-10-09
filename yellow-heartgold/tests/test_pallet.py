"""Protect original content and validate Pallet integration boundaries."""
import struct
import sys
import unittest
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import pallet


class PalletChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = ndspy.rom.NintendoDSRom(pallet.BASE.read_bytes())
        cls.built = ndspy.rom.NintendoDSRom(
            (pallet.PROJECT / 'build/yellow-heartgold-prototype-002.nds').read_bytes())

    def archive(self, rom, path):
        return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)])

    def test_original_event_records_preserved_including_all_kanto(self):
        old = self.archive(self.original, 'a/0/3/2')
        new = self.archive(self.built, 'a/0/3/2')
        self.assertEqual(new.files[:len(old.files)], old.files)
        self.assertEqual(len(new.files), len(old.files) + 4)

    def test_original_scripts_preserved_except_existing_johto_prototype_changes(self):
        old = self.archive(self.original, 'a/0/1/2')
        new = self.archive(self.built, 'a/0/1/2')
        changed = [i for i, payload in enumerate(old.files) if new.files[i] != payload]
        self.assertEqual(changed, [843, 850])
        self.assertEqual(len(new.files), len(old.files) + 8)

    def test_original_messages_preserved_except_shared_starter_ui(self):
        old = self.archive(self.original, 'a/0/2/7')
        new = self.archive(self.built, 'a/0/2/7')
        changed = [i for i, payload in enumerate(old.files) if new.files[i] != payload]
        self.assertEqual(changed, [190])

    def test_opening_map_bindings_use_appended_assets(self):
        original = bytes(self.original.loadArm9().sections[0].data)
        built = bytes(self.built.loadArm9().sections[0].data)
        table = original.index(struct.pack('<3H', 740, 513, 451)) - 6 - 505 * 24
        counts = [len(self.archive(self.original, path).files)
                  for path in ['a/0/1/2', 'a/0/2/7', 'a/0/3/2']]
        for _, map_id, *_ in pallet.MAPS:
            script, header, text = struct.unpack_from('<3H', built, table + map_id * 24 + 6)
            event, = struct.unpack_from('<H', built, table + map_id * 24 + 16)
            self.assertGreaterEqual(script, counts[0])
            self.assertGreaterEqual(header, counts[0])
            self.assertGreaterEqual(text, counts[1])
            self.assertGreaterEqual(event, counts[2])
        self.assertIn(struct.pack('<5i', 506, -1, 6, 6, 1), built)
        self.assertNotIn(struct.pack('<5i', 64, -1, 6, 6, 1), built)


if __name__ == '__main__':
    unittest.main()
