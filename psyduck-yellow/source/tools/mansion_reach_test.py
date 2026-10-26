"""TEST ONLY: is the Mansion solvable as built? State = (map, tile, switch). Moves: 4-neighbour steps over open tiles; closed gate blocks are refused; ring warps and holes teleport;
standing under a statue (facing up) toggles the switch. Goals: every item ball reachable (a free tile next to it), and a way back out to Cinnabar.
argv: rom"""
import struct, sys, collections
import ndspy.rom, ndspy.narc
import map_header_extension as ext
import mansion_yellow as my
from opening import events_decode
from parcel_quest import split_bank
OX, OZ, SC = 18, 20, 2
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
records = ext.records(rom)
ids = {f: 575 + f - 1 for f in (1, 2, 3, 4)}
free, warps, trig, balls, bank = {}, {}, {}, {}, {}
for f, m in ids.items():
    r = records[m - ext.NATIVE_COUNT]
    mat = bytes(mats.files[struct.unpack_from('<H', r, 4)[0]]); w, h, hd, ht, n = mat[:5]
    lid = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht)); fr = set()
    for cz in range(h):
        for cx in range(w):
            land = bytes(lands.files[lid[cz * w + cx]]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
            perm = land[16 + bgs:16 + bgs + 2048]
            for lz in range(32):
                for lx in range(32):
                    if not perm[(lz * 32 + lx) * 2 + 1] & 0x80: fr.add((cx * 32 + lx, cz * 32 + lz))
    free[f] = fr
    g = events_decode(ev.files[struct.unpack_from('<H', r, 16)[0]])
    warps[f] = [struct.unpack_from('<4H', x) for x in g[2]]
    trig[f] = [struct.unpack_from('<Hhh5H', x) for x in g[3]]
    balls[f] = [(struct.unpack_from('<2H', a, 24), struct.unpack_from('<H', a, 8)[0]) for a in g[1] if struct.unpack_from('<H', a, 2)[0] == 87]
    bank[f] = split_bank(scripts.files[struct.unpack_from('<H', r, 6)[0]])
inv = {m: f for f, m in ids.items()}
# gates
gates = collections.defaultdict(list)
for f in ids:
    for by, bx, closed in my.GATES[f]:
        gates[f].append((OX + SC * 2 * bx, OZ + SC * 2 * by, closed))
def closed_at(f, p, sw):
    return any(x <= p[0] < x + 4 and z <= p[1] < z + 4 and c == sw for x, z, c in gates[f])
# holes: parse the 176 teleports of the 3F scripts, in trigger order
holes = {}
for t in trig[3]:
    entry, x, z, w, h = t[:5]
    if (w, h) != (SC, SC): continue
    code = bytes(bank[3][entry - 1])
    i = code.find(struct.pack('<H', 176)); dm, _, dx, dz, _ = struct.unpack_from('<5H', code, i + 2)
    for a in range(w):
        for b in range(h): holes[(x + a, z + b)] = (inv[dm], (dx, dz))
statues = {f: {(OX + SC * x + a, OZ + SC * y + 2) for x, y in my.STATUES[f] for a in range(SC)} for f in ids}
def arrival(f, anchor): return warps[f][anchor][:2]
ring = {}
for f in ids:
    for (x, z, dm, anchor) in warps[f]:
        if dm in inv and not (dm == ids[f] and False):
            if (x, z) not in ring and not (dm == ids[f]): ring[(f, (x, z))] = (inv[dm], anchor)
exit_ring = {(f, (x, z)) for f in ids for (x, z, dm, anchor) in warps[f] if dm == my.CINNABAR}
start = (1, tuple(warps[1][[k for k, w in enumerate(warps[1]) if w[2] == ids[1] and False][0] if False else 0][:2]))
# the arrival used by Cinnabar's door: the first LAST_MAP warp's arrival row
import re
from mtmoon_yellow import parse
src = sys.argv[2] if len(sys.argv) > 2 else None
NOSW = len(sys.argv) > 3 and sys.argv[3] == "noswitch"
seen, q = set(), collections.deque()
begin = None
for k, w in enumerate(warps[1]):
    if w[2] == ids[1] and w[3] == k: pass
# arrival rows are the first len(Yellow warps) rows; Yellow 1F: warps 0-3 and 6-7 are exits
st = (1, warps[1][0][:2], 0)
q.append(st); seen.add(st)
reached_balls, got_out = set(), False
while q:
    f, p, sw = q.popleft()
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (p[0] + dx, p[1] + dz)
        if n not in free[f] or closed_at(f, n, sw): continue
        nf, np_, nsw = f, n, sw
        if (f, n) in exit_ring: got_out = True; continue
        if (f, n) in ring: nf, anchor = ring[(f, n)]; np_ = arrival(nf, anchor)
        elif n in holes: nf, np_ = holes[n]
        s = (nf, np_, nsw)
        if s not in seen: seen.add(s); q.append(s)
    if p in statues[f] and not NOSW:
        s = (f, p, 1 - sw)
        if s not in seen: seen.add(s); q.append(s)
for f in ids:
    for (bx, bz), flag in balls[f]:
        near = any((f, (bx + dx, bz + dz), sw) in seen for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) for sw in (0, 1))
        print('floor', f, 'ball', (bx, bz), hex(flag), 'reachable' if near else 'UNREACHABLE')
print('exit to Cinnabar reachable:', got_out, '| states', len(seen))
