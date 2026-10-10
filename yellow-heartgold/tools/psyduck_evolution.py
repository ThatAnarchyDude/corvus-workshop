"""Replace Psyduck's level/Water Stone evolutions with Moon Stone only.

Apply to a cumulative development build without editing the historical 006
builder or its immutable release. Other species' evolution rules are retained.
"""
import struct
import ndspy.narc
from evolution_testing import RULES

SPECIES = 54
TARGET = 55
MOON_STONE = 81
EVO_STONE = 7


def patch(rom):
    main = rom.loadArm9()
    itcm = main.sections[1].data = bytearray(main.sections[1].data)
    old_rules = b''.join(struct.pack('<3H', *rule) for rule in RULES) + bytes(6)
    assert itcm.count(old_rules) == 1
    at = itcm.index(old_rules)
    # Remove the prototype-006 Water Stone shortcut in both native item
    # eligibility and execution contexts; keep the other shortcuts intact.
    struct.pack_into('<H', itcm, at + 2, MOON_STONE)
    rom.arm9 = main.save(compress=True)
    file_id = rom.filenames.idOf('a/0/3/4')
    tables = ndspy.narc.NARC(rom.files[file_id])
    assert len(tables.files[SPECIES]) == 44  # seven entries plus archive alignment
    assert struct.unpack_from('<3H', tables.files[SPECIES]) == (4, 33, TARGET)
    tables.files[SPECIES] = struct.pack('<3H', EVO_STONE, MOON_STONE, TARGET) + bytes(38)
    rom.files[file_id] = tables.save()
    return dict(species=SPECIES,target=TARGET,item=MOON_STONE,
                moon_stone_only=True,level_up_removed=True,water_stone_removed=True,
                item_rule_address=hex(main.sections[1].ramAddress + at))
