"""Audit: persistent flags that a script or actor uses and that are also the defeat flag (0x550 + id) of a trainer record that exists. Usage: flagaudit.py <rom>"""
import struct, sys
import ndspy.narc, ndspy.rom
from opening import events_decode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
n = len(ndspy.narc.NARC(rom.getFileByName('a/0/5/5')).files)
lo, hi = 0x550 + 1, 0x550 + n
where = {}
def scan(b, tag):
    for i in range(len(b) - 1):
        v = b[i] | (b[i + 1] << 8)
        if lo <= v < hi: where.setdefault(v, set()).add(tag)
for i, raw in enumerate(ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files): scan(bytes(raw), ('script', i))
for i, raw in enumerate(ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files):
    try:
        for g in events_decode(raw):
            for row in g: scan(bytes(row), ('event', i))
    except Exception: pass
print(len(where), 'values in the trainer-flag range appear in scripts/actors (many are ids/coordinates by chance)')
import collections
c = collections.Counter(v >> 8 for v in where)
print({hex(k): v for k, v in sorted(c.items())})
