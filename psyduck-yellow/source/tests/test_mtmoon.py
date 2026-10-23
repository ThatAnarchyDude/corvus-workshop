"""Unpublished Mt. Moon balance and preservation checks."""
import struct
import sys
import unittest
from collections import Counter
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_rom import PROJECT, sha
from mtmoon import DATA, INPUT_SHA, patch
from opening import events_decode
from forest_progression import HG_WEIGHTS
from prototype import decode_messages
from viridian_tutorial import TABLE
from parcel_quest import split_bank


class MtMoonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = PROJECT / 'build/yellow-heartgold-prototype-0017.nds'
        assert sha(path.read_bytes()) == INPUT_SHA
        cls.old = ndspy.rom.NintendoDSRom.fromFile(str(path))
        cls.new = ndspy.rom.NintendoDSRom.fromFile(str(path))
        cls.report = patch(cls.new)

    def arc(self, rom, path):
        return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def test_yellow_teams_levels_and_moves(self):
        expected = [[(74, 10), (74, 10), (95, 10)],
                    [(19, 10), (19, 10), (41, 10)], [(43, 11), (69, 11)],
                    [(81, 11), (100, 11)], [(35, 14)], [(13, 11), (14, 11)],
                    [(10, 10), (11, 10), (10, 10)],
                    [(27, 11), (19, 11), (41, 11)],
                    [(41, 12), (23, 12)], [(19, 13), (41, 13)]]
        parties = self.arc(self.new, 'a/0/5/6')
        for entry, team in zip(self.report['trainers'], expected):
            rows = list(struct.iter_unpack('<BB3H4H', parties[entry['id']]))
            self.assertEqual([(r[3], r[2]) for r in rows], team)
            self.assertEqual([r[5:] for r in rows], [tuple(p['moves']) for p in entry['team']])
        # Magnemite cannot silently inherit HG's early SonicBoom/ThunderShock.
        nerd = self.report['trainers'][3]
        rows = list(struct.iter_unpack('<BB3H4H', parties[nerd['id']]))
        self.assertEqual(rows[0][5:], (33, 0, 0, 0))

    def test_native_trainer_dispatch_and_dialogue(self):
        texts = self.arc(self.new, 'a/0/2/7')
        names = decode_messages(texts[729])[1]
        table = self.arc(self.new, 'a/0/5/7')[0]
        offsets = self.arc(self.new, 'a/1/3/1')[0]
        for entry in self.report['trainers']:
            self.assertEqual(names[entry['id']], [0xFFFF])
            at = struct.unpack_from('<H', offsets, 2 * entry['id'])[0]
            self.assertEqual(list(struct.iter_unpack('<2H', table[at:at+12])),
                             [(entry['id'], i) for i in range(3)])

    def test_wild_weighted_tables_match_yellow_all_times(self):
        wild = self.arc(self.new, 'a/0/3/7')
        for entry in self.report['maps']:
            row = wild[entry['wild']]
            self.assertEqual(row[:6], bytes([10, 0, 0, 0, 0, 0]))
            expected = Counter()
            slots = DATA['wild_slots'][entry['yellow_encounter_floor']]
            for p, weight in zip(slots, (20, 20, 15, 10, 10, 10, 5, 5, 4, 1)):
                expected[(p['level'], p['species'])] += weight
            for period in range(3):
                actual = Counter()
                for level, species, weight in zip(row[8:20], struct.unpack_from('<12H', row, 20 + 24*period), HG_WEIGHTS):
                    actual[(level, species)] += weight
                self.assertEqual(actual, expected)

    def test_actors_stand_on_native_walkable_tiles_and_keep_warps(self):
        matrices = self.arc(self.new, 'a/0/4/1')
        lands = self.arc(self.new, 'a/0/6/5')
        events = self.arc(self.new, 'a/0/3/2')
        d = self.new.loadArm9().sections[0].data
        for entry in self.report['maps']:
            groups = events_decode(events[entry['event']])
            original = events_decode(events[entry['originals']['event']])
            self.assertEqual(groups[2], original[2])
            self.assertEqual(groups[3], [])
            matrixid = struct.unpack_from('<H', d, TABLE + 24*entry['map'] + 4)[0]
            matrix = matrices[matrixid]
            landid = struct.unpack_from('<H', matrix, 5 + matrix[4])[0]
            for row in groups[1]:
                x, z = struct.unpack_from('<2H', row, 24)
                permission = struct.unpack_from('<H', lands[landid], 20 + 2*(32*z+x))[0]
                self.assertFalse(permission & 0x8000)
                if struct.unpack_from('<H', row, 2)[0] != 87:
                    self.assertEqual(struct.unpack_from('<H', row, 6)[0], 1)
                    self.assertEqual(struct.unpack_from('<H', row, 14)[0], 3)
                self.assertNotEqual(struct.unpack_from('<H', row, 2)[0], 148)

    def test_yellow_visible_pickups_are_once_only_with_full_bag_retry(self):
        self.assertEqual([p['item'] for p in DATA['pickups']], [17, 81, 50, 78, 17])
        entry = next(e for e in self.report['maps'] if e['map'] == 107)
        groups = events_decode(self.arc(self.new, 'a/0/3/2')[entry['event']])
        bank = split_bank(self.arc(self.new, 'a/0/1/2')[entry['script']])
        for item in DATA['pickups']:
            row = next(r for r in groups[1] if struct.unpack_from('<H', r)[0] == item['actor'])
            self.assertEqual(struct.unpack_from('<2H', row, 2), (87, 0))
            self.assertEqual(struct.unpack_from('<H', row, 8)[0], item['flag'])
            script = bank[struct.unpack_from('<H', row, 10)[0]-1]
            check = struct.pack('<2H', 32, item['flag'])
            give = struct.pack('<4H', 125, item['item'], 1, 0x800C)
            commit = struct.pack('<2H', 30, item['flag'])
            self.assertLess(script.index(check), script.index(give))
            self.assertLess(script.index(give), script.index(commit))
            self.assertIn(struct.pack('<2H', 101, item['actor']), script)

    def test_previous_maps_archives_and_code_preserved(self):
        oldd = self.old.loadArm9().sections[0].data
        newd = self.new.loadArm9().sections[0].data
        for mapid in range(540):
            if mapid not in (107, 448):
                self.assertEqual(oldd[TABLE+24*mapid:TABLE+24*(mapid+1)],
                                 newd[TABLE+24*mapid:TABLE+24*(mapid+1)])
        for path in ('a/0/1/2', 'a/0/3/2', 'a/0/5/5', 'a/0/5/6', 'a/0/3/7'):
            a, b = self.arc(self.old, path), self.arc(self.new, path)
            self.assertEqual(a, b[:len(a)])
        for path in ('a/0/4/1', 'a/0/6/5', 'a/1/4/8', 'a/0/4/2', 'a/0/4/3', 'a/1/0/8', 'a/0/8/1'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(path)],
                             self.new.files[self.new.filenames.idOf(path)])
        self.assertEqual(self.old.arm7, self.new.arm7)
        self.assertEqual(bytes(self.old.loadArm9().sections[1].data),
                         bytes(self.new.loadArm9().sections[1].data))


if __name__ == '__main__':
    unittest.main()
