"""Route 25's mid-route Camper (x1367,z38, facing down) saw the player one tile too early: he walked out before the player was past the tree to the right of the path, then
stood in the gap afterwards and blocked it (owner report, 2026-10-24). His sight range goes from 3 tiles to 2.

Usage: camper_vision.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import events_decode, events_encode
from viridian_tutorial import TABLE

ROUTE25, X, Z, OLD, NEW = 29, 1367, 38, 3, 2


def patch(rom):
    d = rom.loadArm9().sections[0].data
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    eid = struct.unpack_from('<H', d, TABLE + ROUTE25 * 24 + 16)[0]
    g = events_decode(events.files[eid])
    hits = [i for i, a in enumerate(g[1]) if struct.unpack_from('<2H', a, 24) == (X, Z) and struct.unpack_from('<H', a, 14)[0] == OLD]
    assert len(hits) == 1, hits
    a = bytearray(g[1][hits[0]])
    struct.pack_into('<H', a, 14, NEW)
    g[1][hits[0]] = bytes(a)
    events.files[eid] = events_encode(g)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    return dict(event=eid, actor=hits[0], vision=(OLD, NEW))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
