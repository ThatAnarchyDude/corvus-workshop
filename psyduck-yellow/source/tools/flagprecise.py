"""Precise flag usage: a flag counts as used only where a script has set/clear/check-flag (opcodes 30/31/32) with it, or an actor's hide-flag field (offset 8) holds it.
(freeflags.py counts ANY two matching bytes, so it overstates usage; this one can miss exotic uses - opcodes taking flags in other forms.) Usage: flagprecise.py <rom> [lo hi]"""
import struct, sys
import ndspy.narc, ndspy.rom
from opening import events_decode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
lo, hi = (int(sys.argv[2], 0), int(sys.argv[3], 0)) if len(sys.argv) > 3 else (0x550, 0xB00)
used = {}
for i, raw in enumerate(ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files):
    b = bytes(raw)
    for at in range(len(b) - 3):
        op, v = struct.unpack_from('<HH', b, at)
        if op in (30, 31, 32) and lo <= v < hi: used.setdefault(v, set()).add(('s', i))
for i, raw in enumerate(ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files):
    try: g = events_decode(raw)
    except Exception: continue
    for a in g[1]:
        v = struct.unpack_from('<H', a, 8)[0]
        if lo <= v < hi: used.setdefault(v, set()).add(('e', i))
ntr = len(ndspy.narc.NARC(rom.getFileByName('a/0/5/5')).files)
free = [v for v in range(lo, hi) if v not in used and not (0 < v - 0x550 < ntr)]
print(len(used), 'flags precisely used;', len(free), 'free outside trainer range:')
print(' '.join(hex(v) for v in free))
