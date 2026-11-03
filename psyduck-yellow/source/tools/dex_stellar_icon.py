"""Pokedex type icon for the Stellar type (crash found 2026-11-01, Data Abort at 0x021F2228 on Novareon's National Pokedex entry).

The Pokedex info page (overlay 18, function 0x021F21FC) loads each type's icon through a table at 0x021FBE10 (type id -> NARC member; code at 0x021F967C, literal at 0x021F9684).
The table has 18 words (types 0-17); Stellar (type 19, Novareon) reads past its end (zero), so the load returned null and the next instruction read [null + 0x14].
(An in-place edit of words 18-19 broke the page: they belong to the next variable.)
Fix: a 20-word copy of the table lives in overlay 129 (resident) with Stellar and the unused id 18 using the Normal icon (member 36) until Stellar has an icon of its own; the literal points at it.
Usage: dex_stellar_icon.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.rom

TABLE, LITERAL = 0x021FBE10, 0x021F9684
NEW_TABLE = 0x023DEC00                    # inside the dead dex_fix region (0x023DEB08-0x023DF060), after dex_new_eeveelutions's routines
NORMAL_ICON = 36


def patch(rom):
    ovs = rom.loadArm9Overlays()
    o18, perm = ovs[18], ovs[129]
    o18.data, perm.data = bytearray(o18.data), bytearray(perm.data)
    assert struct.unpack_from('<I', o18.data, LITERAL - o18.ramAddress)[0] == TABLE
    old = struct.unpack_from('<18I', o18.data, TABLE - o18.ramAddress)
    assert old[0] == NORMAL_ICON and old[17] == 48, old
    at = NEW_TABLE - perm.ramAddress
    assert not any(perm.data[at:at + 80]), 'the new table space is not free'
    struct.pack_into('<20I', perm.data, at, *old, NORMAL_ICON, NORMAL_ICON)
    struct.pack_into('<I', o18.data, LITERAL - o18.ramAddress, NEW_TABLE)
    for o in (o18, perm):
        rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
