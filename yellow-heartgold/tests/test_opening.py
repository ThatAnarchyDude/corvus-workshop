"""Acceptance boundaries for the bounded Yellow opening."""
import struct
import sys
import unittest
from collections import defaultdict
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import opening
from prototype import decode_messages


class OpeningChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = ndspy.rom.NintendoDSRom(opening.INPUT.read_bytes())
        cls.rom = ndspy.rom.NintendoDSRom(
            (opening.PROJECT / 'build/yellow-heartgold-prototype-003.nds').read_bytes())
        base = ndspy.rom.NintendoDSRom(opening.BASE.read_bytes())
        main = bytes(base.loadArm9().sections[0].data)
        cls.table = main.index(struct.pack('<3H', 740, 513, 451)) - 6 - 505 * 24

    def archive(self, rom, path):
        return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)])

    def active_events(self, map_id):
        main = self.rom.loadArm9().sections[0].data
        index, = struct.unpack_from('<H', main, self.table + map_id * 24 + 16)
        return opening.events_decode(self.archive(self.rom, 'a/0/3/2').files[index])

    def test_all_existing_events_and_scripts_remain_intact(self):
        for path in ['a/0/1/2', 'a/0/3/2', 'a/0/5/5', 'a/0/5/6']:
            prior = self.archive(self.prior, path)
            new = self.archive(self.rom, path)
            self.assertEqual(new.files[:len(prior.files)], prior.files)

    def test_route_one_has_two_non_battle_npcs_and_cannot_launch_a_trainer(self):
        _, objects, _, coords = self.active_events(9)
        self.assertEqual(len(objects), 2)
        self.assertEqual([struct.unpack_from('<H', row, 6)[0] for row in objects], [0, 0])
        self.assertEqual([struct.unpack_from('<H', row, 10)[0] for row in objects], [1, 2])
        boundary, = coords
        self.assertEqual(struct.unpack('<Hhh5H', boundary),
                         (4, 1024, opening.ROUTE_GATE_Z, 32, 1, 0, 0, 0x416D))

    def test_yellow_route_one_encounter_probabilities_match_for_all_times(self):
        data = self.archive(self.rom, 'a/0/3/7').files[111]
        levels = data[8:20]
        weights = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
        expected = {(3, 16):30, (4, 16):20, (2, 19):15, (3, 19):10,
                    (2, 16):10, (5, 16):5, (4, 19):5, (6, 16):4, (7, 16):1}
        for period in range(3):
            mons = struct.unpack_from('<12H', data, 20 + period * 24)
            actual = defaultdict(int)
            for level, mon, weight in zip(levels, mons, weights):
                actual[(level, mon)] += weight
            self.assertEqual(dict(actual), expected)

    def test_boundary_is_immediately_north_of_the_entrance_grass(self):
        matrix = self.archive(self.rom, 'a/0/4/1').files[0]
        width, height, has_headers, has_altitudes, name_length = matrix[:5]
        count = width * height
        at = 5 + name_length + (2 * count if has_headers else 0)
        at += count if has_altitudes else 0
        models = struct.unpack_from(f'<{count}H', matrix, at)
        model = models[10 * width + 32]
        land = self.archive(self.rom, 'a/0/6/5').files[model]
        self.assertEqual(struct.unpack_from('<I', land, 16)[0], 0x1234)
        tiles = struct.unpack_from('<1024H', land, 20)
        for x in range(1038, 1042):
            self.assertEqual(tiles[(opening.ROUTE_GATE_Z % 32) * 32 + x % 32], 0)
            for z in range(opening.ROUTE_GATE_Z + 1, 352):
                self.assertEqual(tiles[(z % 32) * 32 + x % 32], 2)

    def test_intercept_and_rival_triggers_are_saved_and_one_time(self):
        town = self.active_events(49)
        lab = self.active_events(505)
        self.assertEqual(struct.unpack('<Hhh5H', town[3][0]), (8, 1024, 352, 32, 1, 0, 0, opening.OAK_STATE))
        self.assertEqual(struct.unpack('<Hhh5H', lab[3][0]), (13, 7, 12, 3, 1, 0, 1, opening.RIVAL_STATE))
        self.assertNotEqual(opening.OAK_STATE, opening.RIVAL_STATE)

    def test_new_rival_parties_are_level_five_with_usable_starters(self):
        prior = self.archive(self.prior, 'a/0/5/6')
        parties = self.archive(self.rom, 'a/0/5/6')
        self.assertEqual(len(parties.files), len(prior.files) + 3)
        for party, species in zip(parties.files[len(prior.files):], [25, 133, 175]):
            self.assertEqual(struct.unpack_from('<2H', party, 2), (5, species))
        trainers = self.archive(self.rom, 'a/0/5/5')
        self.assertEqual([row[1] for row in trainers.files[-3:]], [23, 23, 23])

    def test_old_dialogue_preserved_when_new_trainer_names_appended(self):
        old = self.archive(self.prior, 'a/0/2/7')
        new = self.archive(self.rom, 'a/0/2/7')
        for i, message in enumerate(old.files):
            if i not in (219, 729):
                self.assertEqual(new.files[i], message)
        self.assertEqual(decode_messages(new.files[729])[1][:738], decode_messages(old.files[729])[1])
        self.assertEqual(decode_messages(new.files[219])[1][:63], decode_messages(old.files[219])[1])


if __name__ == '__main__':
    unittest.main()
