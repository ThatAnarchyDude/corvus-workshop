"""List persistent flags (not already a trainer's defeat flag) in [lo, hi) that appear in no script bank and no actor/bg/warp/trigger row of any event file (candidates for new flags). Usage: freeflags.py <rom> [lo hi]"""
import struct, sys
import ndspy.narc, ndspy.rom
from opening import events_decode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
lo, hi = (int(sys.argv[2], 0), int(sys.argv[3], 0)) if len(sys.argv) > 3 else (0x900, 0xAA0)
used = set()
def scan(b):
    for i in range(len(b) - 1):
        v = b[i] | (b[i + 1] << 8)
        if lo <= v < hi: used.add(v)
for raw in ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files: scan(bytes(raw))
for raw in ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files:
    try:
        for grp in events_decode(raw):
            for row in grp: scan(bytes(row))
    except Exception: scan(bytes(raw))
ntr = len(ndspy.narc.NARC(rom.getFileByName('a/0/5/5')).files)
free = [v for v in range(lo, hi) if v not in used and not (0 < v - 0x550 < ntr)]       # a flag 0x550 + id is also the defeat flag of trainer record `id`
print(len(free), 'free of', hi - lo)
print(' '.join(hex(v) for v in free))
