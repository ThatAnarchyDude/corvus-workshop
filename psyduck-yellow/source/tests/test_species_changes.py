"""Verify the species edit leaves other species, stats and moves untouched."""
import sys
import unittest
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_rom import PROJECT
from species_changes import patch, PERSONAL_ARCHIVE


class SpeciesChangesTests(unittest.TestCase):
    def test_golduck_water_psychic_is_the_only_species_or_file_change(self):
        rom = ndspy.rom.NintendoDSRom.fromFile(
            str(PROJECT / 'build/yellow-heartgold-prototype-014.nds'))
        originals = list(rom.files)
        fid = rom.filenames.idOf(PERSONAL_ARCHIVE)
        before = ndspy.narc.NARC(originals[fid]).files
        report = patch(rom)
        after = ndspy.narc.NARC(rom.files[fid]).files
        self.assertEqual([i for i, (a, b) in enumerate(zip(originals, rom.files))
                          if a != b], [fid])
        self.assertEqual(len(before), len(after))
        for species, (a, b) in enumerate(zip(before, after)):
            self.assertEqual(b, a[:7] + bytes([14]) + a[8:] if species == 55 else a)
        self.assertEqual(after[54][6:8], bytes([11, 11]))
        self.assertEqual(after[55][6:8], bytes([11, 14]))
        self.assertTrue(report['move_changes_deferred_until_after_kanto'])
        once = rom.files[fid]
        patch(rom)
        self.assertEqual(rom.files[fid], once)


if __name__ == '__main__':
    unittest.main()
