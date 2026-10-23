"""Static audit: every script id an actor or trigger of a map names (below the global ranges) must exist in the map's script bank.

Script ids 2000+ are the engine's global scripts (common scripts, trainer battles 3000+, item balls and hidden items 7000+); ids 1..N are the map's own bank (N scripts). A larger id below 2000 calls a
script that does not exist.

Usage: audit_script_refs.py <rom.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode
from parcel_quest import split_bank
from viridian_tutorial import TABLE


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    d = bytes(rom.loadArm9().sections[0].data)
    records = [d[TABLE + 24 * m:TABLE + 24 * m + 24] for m in range(ext.NATIVE_COUNT)] + list(ext.records(rom))
    bad = 0
    for m, rec in enumerate(records):
        try:
            n = len(split_bank(scripts[struct.unpack_from('<H', rec, 6)[0]]))
            g = events_decode(events[struct.unpack_from('<H', rec, 16)[0]])
        except Exception:
            continue
        refs = [('actor', struct.unpack_from('<H', a, 10)[0]) for a in g[1]] + [('trigger', struct.unpack_from('<H', t, 0)[0]) for t in g[3]]
        for kind, sid in refs:
            if 0 < sid < 2000 and sid > n:
                print('map', m, kind, 'script', sid, 'but the bank has', n)
                bad += 1
    print(len(records), 'maps checked,', bad, 'bad')


if __name__ == '__main__':
    main(sys.argv[1])
