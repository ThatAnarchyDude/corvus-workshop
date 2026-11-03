"""Psyduck evolves by the Moon Stone ONLY, and so does the starter Psyduck (owner decision 2026-10-29, complaint 2026-11-01).
Found 2026-11-01: the stone-shortcut table exists twice, in the ARM9 ITCM (0x940; psyduck_evolution.py changed Psyduck's row to the Moon Stone) and in overlay 129 at 0x5A12 (still Water Stone), and the game consults both, so Psyduck could evolve with either stone.
Fixes: (1) overlay-129 copy of Psyduck's row -> Moon Stone (item 81); (2) starter Psyduck (1563) had NO evolution row: it gets (method 7 = use item, 81 Moon Stone) -> Golduck (55).
INTERIM: the target is the normal Golduck (55) until the starter Golduck species exists (Stage D); then the row points at it.
Usage: psyduck_evolution_fix.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom

OV, AT = 129, 0x5A12
MOON_STONE, WATER_STONE, PSYDUCK, GOLDUCK, STARTER_PSYDUCK = 81, 84, 54, 55, 1563


def patch(rom):
    ovs = rom.loadArm9Overlays()
    o = ovs[OV]
    data = bytearray(o.data)
    at = AT
    assert struct.unpack_from('<3H', data, at) == (PSYDUCK, WATER_STONE, GOLDUCK), 'overlay-129 rule moved'
    struct.pack_into('<3H', data, at, PSYDUCK, MOON_STONE, GOLDUCK)
    o.data = data
    rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    eid = rom.filenames.idOf('a/0/3/4')
    ev = ndspy.narc.NARC(rom.files[eid])
    row = bytearray(ev.files[STARTER_PSYDUCK])
    assert bytes(row) == bytes(len(row)), 'starter Psyduck already has an evolution row'
    struct.pack_into('<3H', row, 0, 7, MOON_STONE, GOLDUCK)
    ev.files[STARTER_PSYDUCK] = bytes(row)
    rom.files[eid] = ev.save()


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
    print('wrote', sys.argv[2])
