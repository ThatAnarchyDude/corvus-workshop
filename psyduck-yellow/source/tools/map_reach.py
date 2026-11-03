"""TEST ONLY: shortest walk between two tiles of one map (collision, actors and bg events as walls, same-map warp pads as edges: stepping on a pad lands you on its partner).
Usage (from yellow-heartgold, PYTHONPATH=tools): map_reach.py <rom> <map> <sx> <sz> <tx> <tz>"""
import collections
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import events_decode
import map_dump as gd


def reach(rom, mid, start, target, pads=True, actors_block=True):
    rec = gd.record(rom, mid)
    free, attr, _ = gd.free_tiles(rom, rec)
    ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    g = events_decode(ev.files[struct.unpack_from('<H', rec, 16)[0]])
    warps = [struct.unpack_from('<4H', w) for w in g[2]]
    actor_tiles = {tuple(struct.unpack_from('<2H', a, 24)) for a in g[1]}
    bg_tiles = {tuple(struct.unpack_from('<2i', b, 4)) for b in g[0]}
    block = set(actor_tiles) if actors_block else set()
    block |= bg_tiles
    pad = {}
    if pads:
        for i, (x, z, dm, an) in enumerate(warps):
            if dm == mid and an < len(warps):
                pad[(x, z)] = warps[an][:2]
    prev, q = {start: None}, collections.deque([start])
    while q:
        p = q.popleft()
        if p == target:
            break
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (p[0] + dx, p[1] + dz)
            if n not in free or (n in block and n != target):
                continue
            n = pad.get(n, n)                 # stepping on a pad lands you on its partner (no re-trigger on arrival)
            if n not in prev:
                prev[n] = p
                q.append(n)
    if target not in prev:
        return None, len(prev)
    path, p = [], target
    while p is not None:
        path.append(p)
        p = prev[p]
    return path[::-1], len(prev)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    mid, sx, sz, tx, tz = (int(a) for a in sys.argv[2:7])
    for pads in (False, True):
        path, n = reach(rom, mid, (sx, sz), (tx, tz), pads=pads)
        print('pads=%s: reached %d tiles; target %s' % (pads, n, 'UNREACHABLE' if path is None else 'in %d steps' % (len(path) - 1)))
        if path:
            print('  ', path)
