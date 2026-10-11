"""Execute the table selector and verify other maps and wild data stay intact."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_LR
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon_encounters import patch, GET_TABLE
from mtmoon import patch as patch_cave
from mtmoon_story import patch as patch_story
from mtmoon_center import patch as patch_center
from bulk_rare_candy import patch as patch_candy
from mtmoon_tms import patch as patch_tms
from mtmoon_items import patch as patch_items
from mtmoon_rockets import patch as patch_rockets


class MtMoonEncounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        for apply in (patch_cave,patch_story,patch_center,patch_candy,patch_tms,patch_items,patch_rockets):
            apply(cls.old)
        cls.new = ndspy.rom.NintendoDSRom(cls.old.save())
        cls.report = patch(cls.new)
        cls.sections = [(s.ramAddress, bytes(s.data)) for s in cls.new.loadArm9().sections[:2]]

    def selector(self, map_id, z, location=True, avatar=True, obj=True):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x01FF8000, 0x8000)
        cpu.mem_map(0x02000000, 0x400000)
        for address, data in self.sections:
            cpu.mem_write(address, data)
        fs, events, loc, player, mon = 0x02300000, 0x02301000, 0x02302000, 0x02303000, 0x02304000
        def word(at, value): cpu.mem_write(at, struct.pack('<I', value))
        word(fs+0x14, events)
        word(fs+0x20, loc if location else 0)
        word(loc, map_id)
        word(fs+0x40, player if avatar else 0)
        word(player+0x30, mon if obj else 0)
        word(mon+0x6C, z)
        cpu.reg_write(UC_ARM_REG_R0, fs)
        cpu.reg_write(UC_ARM_REG_LR, 0x023F0001)
        cpu.emu_start(GET_TABLE|1, 0x023F0000, count=100)
        return cpu.reg_read(UC_ARM_REG_R0)

    def test_only_live_fossil_corridor_selects_deep_table(self):
        for map_id in range(540):
            for z in (0, 19, 20, 23, 31):
                wanted = int(self.report['table'],16) if map_id==107 and z>=20 else 0x02301920
                self.assertEqual(self.selector(map_id,z), wanted, (map_id,z))
        for missing in ('location','avatar','obj'):
            self.assertEqual(self.selector(107,22,**{missing:False}),0x02301920)

    def test_all_periods_have_yellow_b2f_species_and_levels(self):
        section = self.new.loadArm9().sections[1]
        at = int(self.report['table'],16)-section.ramAddress
        table = section.data[at:at+196]
        slots = self.report['slots']
        self.assertEqual(table[8:20],bytes(p['level'] for p in slots))
        for period in range(3):
            self.assertEqual(struct.unpack_from('<12H',table,20+24*period),tuple(p['species'] for p in slots))
        self.assertIn(35,[p['species'] for p in slots])

    def test_archives_save_format_and_other_arm9_bytes_preserved(self):
        self.assertEqual(self.old.files,self.new.files)
        before,after = [bytearray(r.loadArm9().sections[0].data) for r in (self.old,self.new)]
        at=GET_TABLE-0x02000000
        after[at:at+8]=before[at:at+8]
        after[0xD2C68:0xD2C6C]=before[0xD2C68:0xD2C6C]
        # ndspy regenerates the autoload-table bounds and compressed-data end.
        settings=self.old.loadArm9().codeSettingsOffs
        for offset in (settings, settings+4, settings+20):
            after[offset:offset+4]=before[offset:offset+4]
        self.assertEqual(before,after)
        main=self.new.loadArm9()
        self.assertEqual(struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0],main.sections[1].ramAddress+len(main.sections[1].data))
