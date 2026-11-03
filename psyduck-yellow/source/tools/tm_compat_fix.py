"""TMs and HMs work for the starter species and every other species above hg-engine's old limit (owner report 2026-10-29: starter Eevee/Psyduck could not learn any TM or HM).

Cause (read in hg-engine's GetMonMachineMoveCompat, found in overlay 129 at 0x023DB1A4): the function returns FALSE when species > MAX_SPECIES_INCLUDING_FORMS, a literal 1534 at 0x023DB208.
The starter species start at 1561 (the compatibility table a/0/2/8 file 14 does have their rows), so every one of them got "can't learn". Level-up learning has no such test.
Fix: the literal becomes 1582, the last species id of the expanded tables (1583 rows).

Usage: tm_compat_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.rom

OV = 129
LITERAL_AT = 0x023DB208
OLD, NEW = 1534, 1582
CHECK_AT = 0x023DB1C4            # cmp r5, r3 ; bhi (return 0)
CHECK = bytes.fromhex('9d42')


def patch(rom):
    ovs = rom.loadArm9Overlays()
    o = ovs[OV]
    data = bytearray(o.data)
    assert not o.compressed or True
    at = LITERAL_AT - o.ramAddress
    assert struct.unpack_from('<I', data, at)[0] == OLD, 'literal moved'
    assert bytes(data[CHECK_AT - o.ramAddress:CHECK_AT - o.ramAddress + 2]) == CHECK, 'compare moved'
    struct.pack_into('<I', data, at, NEW)
    o.data = data
    rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
    print('wrote', sys.argv[2])
