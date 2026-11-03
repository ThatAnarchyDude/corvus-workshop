"""Viridian Forest's two gatehouses (maps 419 south, 420 north): the two NPCs stood inside the counters (owner report 2026-10-29).
The room is a 5-wide floor (x 3..7) with blocked counter columns at x 2 and x 8 (z 6..9) and a blocked wall row at z 5. Yellow's coordinates put the left NPC at (2,5) (on the wall above the left counter)
and the right NPC at (8,8) (on the right counter itself). They now stand on the free floor tiles in front of the counters: left (3,6) facing east, right (7,8) facing west; the walking line x = 5 stays clear.
Usage: gatehouse_npc_fix.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import events_decode, events_encode
from viridian_tutorial import TABLE

MOVES = {0: ((2, 5), (3, 6)), 1: ((8, 8), (7, 8))}      # actor index -> (old x,z, new x,z)


def patch(rom):
    d = bytes(rom.loadArm9().sections[0].data)
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    for m in (419, 420):
        eid = struct.unpack_from('<H', d, TABLE + 24 * m + 16)[0]
        groups = events_decode(events.files[eid])
        for i, (old, new) in MOVES.items():
            row = bytearray(groups[1][i])
            assert struct.unpack_from('<2H', row, 24) == old, (m, i, struct.unpack_from('<2H', row, 24))
            struct.pack_into('<2H', row, 24, *new)
            groups[1][i] = bytes(row)
        events.files[eid] = events_encode(groups)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
    print('wrote', sys.argv[2])
