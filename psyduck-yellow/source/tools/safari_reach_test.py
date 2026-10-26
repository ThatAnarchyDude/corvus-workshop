"""TEST ONLY: reachability in the rebuilt Victory Road (barrier rocks and boulders ignored, ring warps followed). argv: rom"""
import struct, sys, collections
import ndspy.rom, ndspy.narc
import map_header_extension as ext
from opening import events_decode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5')); ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
ids = (583, 584, 585, 586); free, warps, actors = {}, {}, {}
for m in ids:
    r = ext.records(rom)[m - ext.NATIVE_COUNT]
    mat = bytes(mats.files[struct.unpack_from('<H', r, 4)[0]]); w, h, hd, ht, n = mat[:5]
    lid = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht)); fr = set()
    for cz in range(h):
        for cx in range(w):
            land = bytes(lands.files[lid[cz * w + cx]]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
            perm = land[16 + bgs:16 + bgs + 2048]
            for lz in range(32):
                for lx in range(32):
                    if not perm[(lz * 32 + lx) * 2 + 1] & 0x80: fr.add((cx * 32 + lx, cz * 32 + lz))
    free[m] = fr
    g = events_decode(ev.files[struct.unpack_from('<H', r, 16)[0]])
    warps[m] = [struct.unpack_from('<4H', x) for x in g[2]]
    actors[m] = [(struct.unpack_from('<H', a, 2)[0], tuple(struct.unpack_from('<2H', a, 24))) for a in g[1]]
start = (583, warps[583][0][:2]); seen = {start}; q = collections.deque([start]); out58 = out299 = False
ringdest = {}
for m in ids:
    for (x, z, dm, an) in warps[m]:
        if (dm != m) or True:
            ringdest[(m, (x, z))] = (dm, an)
while q:
    m, p = q.popleft()
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (p[0] + dx, p[1] + dz)
        if n not in free[m]: continue
        d = ringdest.get((m, n))
        if d and not (d[0] == m and d[1] == warps[m].index(next(w for w in warps[m] if w[:2] == n)) ):
            if d[0] == 56: out58 = True; continue
            if d[0] == -1: out299 = True; continue
            if d[0] in ids:
                s = (d[0], warps[d[0]][d[1]][:2])
                if s not in seen: seen.add(s); q.append(s)
            continue
        if (m, n) not in seen: seen.add((m, n)); q.append((m, n))
for m in ids:
    for sp, pos in actors[m]:
        if sp in (85, 84): continue
        near = any((m, (pos[0] + dx, pos[1] + dz)) in seen for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if not near: print('floor', m, 'sprite', sp, pos, 'UNREACHABLE')
print('Fuchsia exit reachable:', out58, '| back to Route 23 gate reachable:', out299, '| tiles reached', len(seen))
