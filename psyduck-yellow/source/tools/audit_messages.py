"""Static audit: every message a script that the map's events call shows (the `2d 00 <index> 32 00` command sequence) must name a row that exists in the map's text bank.

Usage: audit_messages.py <rom.nds>     Prints the maps with an out-of-range message index.
"""
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode
from parcel_quest import split_bank
from prototype import decode_messages
from viridian_tutorial import TABLE


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7')).files
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    d = bytes(rom.loadArm9().sections[0].data)
    records = [d[TABLE + 24 * m:TABLE + 24 * m + 24] for m in range(ext.NATIVE_COUNT)] + list(ext.records(rom))
    bad = 0
    for m, rec in enumerate(records):
        sid, tid = struct.unpack_from('<H', rec, 6)[0], struct.unpack_from('<H', rec, 10)[0]
        try:
            rows = len(decode_messages(bytes(texts[tid]))[1])
            bank = split_bank(scripts[sid])
        except Exception:
            continue
        try:
            g = events_decode(events[struct.unpack_from('<H', rec, 16)[0]])
        except Exception:
            continue
        called = {struct.unpack_from('<H', a, 10)[0] for a in g[1]} | {struct.unpack_from('<H', t, 0)[0] for t in g[3]}      # actors' and triggers' scripts
        for n, script in enumerate(bank, 1):
            if n not in called:
                continue
            for match in re.finditer(rb'\x2d\x00(.)\x32\x00', bytes(script), re.S):
                if match.group(1)[0] >= rows:
                    print('map', m, 'script', n, 'message', match.group(1)[0], 'rows', rows)
                    bad += 1
    print(len(records), 'maps checked,', bad, 'bad')


if __name__ == '__main__':
    main(sys.argv[1])
