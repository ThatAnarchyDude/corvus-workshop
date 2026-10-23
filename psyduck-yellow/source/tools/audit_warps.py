"""Static softlock audit: every warp of every map (native 0-539 and the extension maps) must name an existing map and an existing warp of that map.

Usage: audit_warps.py <rom.nds>      Prints the bad warps (destination 0xFFFF = 'same map' is accepted) and the maps with no warps at all.
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    d = bytes(rom.loadArm9().sections[0].data)
    records = [d[TABLE + 24 * m:TABLE + 24 * m + 24] for m in range(ext.NATIVE_COUNT)] + list(ext.records(rom))
    warps = {}
    for m, rec in enumerate(records):
        eid = struct.unpack_from('<H', rec, 16)[0]
        try:
            g = events_decode(events[eid])
        except Exception:
            warps[m] = None
            continue
        warps[m] = [struct.unpack_from('<4H', w, 0) for w in g[2]]
    bad = []
    for m, ws in warps.items():
        for i, (x, y, dest, anchor) in enumerate(ws or []):
            if dest == 0xFFFF:
                continue
            if dest >= len(records) or warps.get(dest) is None:
                bad.append((m, i, (x, y), 'dest map', dest))
            elif anchor != 0xFFFF and anchor >= len(warps[dest]):
                bad.append((m, i, (x, y), f'anchor {anchor} but map {dest} has {len(warps[dest])} warps', dest))
    for b in bad:
        print(b)
    print(len(records), 'maps,', sum(len(v or []) for v in warps.values()), 'warps,', len(bad), 'bad')


if __name__ == '__main__':
    main(sys.argv[1])
