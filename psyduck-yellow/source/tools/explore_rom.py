"""TEST-ONLY: copy a ROM with the given maps' actors parked at (0,0) and triggers removed and the player transported onto it.

Usage: explore_rom.py <in.nds> <out.nds> <map> <x> <y> [more maps to clear]   (fixture save; never part of a release)
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode, events_encode
import test_transport


def event_id(rom, map_id):
    if map_id >= ext.NATIVE_COUNT:
        return struct.unpack_from('<H', ext.records(rom)[map_id - ext.NATIVE_COUNT], 16)[0]
    return struct.unpack_from('<H', ext.native_record(rom, map_id), 16)[0]


if __name__ == '__main__':
    src, dst, m, x, y = sys.argv[1:6]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    for park in [int(m)] + [int(v) for v in sys.argv[6:]]:       # extra maps to clear, e.g. ones reached by warp
        eid = event_id(rom, park)
        g = events_decode(events.files[eid])
        g[3] = []
        g[1] = [bytearray(a) for a in g[1]]
        for a in g[1]:          # native scripts reference actors by id, so park them instead of deleting
            struct.pack_into('<2H', a, 24, 0, 0)
        events.files[eid] = events_encode(g)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    test_transport.install(rom, int(m), int(x), int(y), 1)
    rom.saveToFile(dst)
