"""Walk a map in the emulator and record which tiles the player can really stand on (ground truth for placement).

Usage: DS_ROM=<fixture rom already transported to the start tile> DS_OUT=<dir with matching .dsv> explore.py <out.json> [max_moves]
Tiles are event coordinates (the same ones actors/warps/triggers use). Warps are recorded as ('warp', tile, dir).
Run it on a ROM whose target map has no actors or triggers, so no battle or dialogue interrupts the walk.
"""
import ctypes as C
import json
import os
import struct
import sys
import ds_session as d

X, Z = 0x1da6f6, 0x1da6fe
DIRS = {'U': (4, 0, -1, 'D'), 'D': (5, 0, 1, 'U'), 'L': (6, -1, 0, 'R'), 'R': (7, 1, 0, 'L')}
HOLD, SETTLE = 10, 12   # a 10-frame press is one tile (longer presses walk two); a turn needs a second press


def pos():
    r = d.ram()
    return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]


def snapshot():
    n = d.core.retro_serialize_size()
    buf = C.create_string_buffer(n)
    assert d.core.retro_serialize(buf, n)
    return buf


def restore(buf):
    assert d.core.retro_unserialize(buf, len(buf))


def step(name):
    before = pos()
    for _ in range(2):
        d.run(HOLD, DIRS[name][0])
        d.run(SETTLE)
        after = pos()
        if after != before:
            return after
    return before


def main(out, limit=3000, prepare=None):
    d.boot()
    for _ in range(int(os.environ.get('DISMISS', 0))):    # arrival scripts (e.g. a healing NPC) hold input until dismissed
        d.run(6, 8)
        d.run(40)
    if prepare:
        prepare()
    start = pos()
    base = snapshot()
    seen, blocked, warps = {start}, set(), []
    path = []                       # moves from the snapshot to the current tile
    moves = 0
    stack = [(start, [k for k in 'UDLR'])]

    def go_back_to(route):
        restore(base)
        for m in route:
            step(m)

    while stack and moves < limit:
        tile, todo = stack[-1]
        if not todo:
            stack.pop()
            if path:
                last = path.pop()
                back = DIRS[last][3]
                before = pos()
                after = step(back)
                moves += 1
                if after != stack[-1][0]:                    # one-way or drifted: resync
                    go_back_to(path)
            continue
        m = todo.pop()
        dx, dz = DIRS[m][1], DIRS[m][2]
        target = (tile[0] + dx, tile[1] + dz)
        if target in seen or (tile, m) in blocked:
            continue
        after = step(m)
        moves += 1
        if after == tile:
            blocked.add((tile, m))
            continue
        if after != target:                                   # warp, transition or scripted move
            warps.append((tile, m, after))
            go_back_to(path)
            continue
        seen.add(after)
        path.append(m)
        stack.append((after, [k for k in 'UDLR']))
    json.dump(dict(start=start, tiles=sorted(seen), warps=warps, moves=moves, complete=not stack), open(out, 'w'))
    print('tiles', len(seen), 'warps', len(warps), 'moves', moves, 'complete', not stack)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3000)
