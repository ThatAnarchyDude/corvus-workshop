"""Execute native TM lookup hooks and check compatibility and item metadata."""
import struct
import sys
import unittest
from pathlib import Path

import ndspy.narc
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R3, UC_ARM_REG_R7, UC_ARM_REG_LR

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from yellow_tms import patch, ITEM_TABLE, MOVE_ENTRY, INDEX_ENTRY


class YellowTMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ndspy.rom.NintendoDSRom.fromFile(
            str(PROJECT/'build/yellow-heartgold-prototype-014.nds'))
        cls.before = list(cls.rom.files)
        cls.original = cls.rom.loadArm9()
        cls.report = patch(cls.rom)
        cls.main = cls.rom.loadArm9()

    def cpu(self, main):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x01FF8000, 0x8000)
        cpu.mem_map(0x02000000, 0x400000)
        for section in main.sections[:2]:
            cpu.mem_write(section.ramAddress, bytes(section.data))
        return cpu

    def lookup(self, cpu, site, item):
        cpu.reg_write(UC_ARM_REG_R0, item)
        cpu.reg_write(UC_ARM_REG_LR, 0x023E0001)
        cpu.emu_start(site | 1, 0x023E0000, count=100)
        return cpu.reg_read(UC_ARM_REG_R0)

    def test_native_lookups_preserve_all_original_items_and_add_bide(self):
        old, new = self.cpu(self.original), self.cpu(self.main)
        for site in (MOVE_ENTRY, INDEX_ENTRY):
            for item in range(537):
                wanted = (117 if site == MOVE_ENTRY else 100) if item == 115 else self.lookup(old, site, item)
                self.assertEqual(self.lookup(new, site, item), wanted, (site, item))
        self.assertEqual(self.lookup(new, MOVE_ENTRY, 361), 351)  # Shock Wave remains TM34.

    def test_yellow_compatibility_uses_only_unused_bit_and_preserves_other_personal_data(self):
        fid = self.rom.filenames.idOf('a/0/0/2')
        before = ndspy.narc.NARC(self.before[fid]).files
        after = ndspy.narc.NARC(self.rom.files[fid]).files
        for species, (a, b) in enumerate(zip(before, after)):
            expected = bytearray(a)
            if species in self.report['compatible_species']:
                expected[40] |= 16
            self.assertEqual(b, bytes(expected))
        for species in (54, 55, 133, 175):
            self.assertTrue(after[species][40] & 16)
        for species in (10, 11, 13, 14, 129, 132):
            self.assertFalse(after[species][40] & 16)

    def test_reward_reuses_native_single_use_tm_metadata_and_preserves_existing_item_records(self):
        fid = self.rom.filenames.idOf('a/0/1/7')
        before = ndspy.narc.NARC(self.before[fid]).files
        after = ndspy.narc.NARC(self.rom.files[fid]).files
        self.assertEqual(after[:len(before)], before)
        d = self.main.sections[0].data
        source = struct.unpack_from('<H', d, ITEM_TABLE+361*8)[0]
        new = struct.unpack_from('<H', d, ITEM_TABLE+115*8)[0]
        self.assertEqual(after[new][2:], before[source][2:])
        self.assertEqual(after[new][:2], bytes(2))

    def test_bag_number_and_quantity_paths_use_tm34_without_changing_stored_item(self):
        for i, entry in enumerate(self.report['display_hooks']):
            cpu = self.cpu(self.main)
            for item in (115,328,361,420,427):
                cpu.mem_write(0x02301000,struct.pack('<HH',item,1))
                cpu.reg_write(UC_ARM_REG_R0,105 if i==0 else 82)
                cpu.reg_write(UC_ARM_REG_R3,0x02301000)
                cpu.reg_write(UC_ARM_REG_R7,0x02301000 if i==0 else 0)
                cpu.reg_write(UC_ARM_REG_LR,0x023E0001)
                cpu.emu_start(int(entry['hook'],16)|1,0x023E0000,count=100)
                self.assertEqual(cpu.reg_read(UC_ARM_REG_R1),361 if item==115 else item)
                self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),420 if i==0 else 328)
                self.assertEqual(bytes(cpu.mem_read(0x02301000,4)),struct.pack('<HH',item,1))


if __name__ == '__main__':
    unittest.main()
