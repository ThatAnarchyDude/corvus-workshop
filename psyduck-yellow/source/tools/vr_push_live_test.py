"""TEST ONLY (live, needs ds_repl.py running on a fixture at map 580 (18,44) with Machop L29, FIXTURE_BADGES=8,9,10,11,12 and the 1F trainers' defeat flags 0x926,0x927, wild rate zeroed): faces the first boulder, uses Strength, pushes it onto the 1F switch, then walks east through the barrier. Passed on 0110. Usage: PYTHONPATH=tools vr_push_live_test.py <workdir> <rom for the map data>"""
import collections
import json
import os
import sys
import time
from vr_free import load
from vr_solve import solve, DIRS

W, ROM = sys.argv[1], sys.argv[2]


def send(steps):
    out = os.path.join(W, 'out.json')
    if os.path.exists(out):
        os.remove(out)
    json.dump(steps, open(os.path.join(W, 'cmd.tmp'), 'w'))
    os.replace(os.path.join(W, 'cmd.tmp'), os.path.join(W, 'cmd.json'))
    for _ in range(2400):
        if os.path.exists(out):
            time.sleep(0.1)
            return json.load(open(out))
        time.sleep(0.5)
    raise SystemExit('TIMEOUT')


def route(free, blocked, start, goal):
    prev = {start: None}
    q = collections.deque([start])
    while q:
        c = q.popleft()
        if c == goal:
            break
        for name, (dx, dz) in DIRS.items():
            n = (c[0] + dx, c[1] + dz)
            if n in free and n not in blocked and n not in prev:
                prev[n] = (c, name)
                q.append(n)
    if goal not in prev:
        return None
    out, c = [], goal
    while prev[c]:
        c, name = prev[c]
        out.append(name)
    return out[::-1]


import struct
free, actors, g = load(ROM, 580)
warps = {tuple(struct.unpack_from('<2H', w, 0)) for w in g[2]}
free = free - warps                                   # never plan through a warp tile (they leave the map)
actors = [a for a in actors if not 3000 <= a[2] < 4100]
rocks = {a[4] for a in actors if a[1] == 85}
boulders = [a[4] for a in actors if a[1] == 84 and a[2] == 10002]
others = {a[4] for a in actors if a[4] != boulders[0]}
start = tuple(send(['pos'])[0][1:])
assert start == (18, 44), start
send(['up'] + ['a', 'wait 150'] * 6)                 # face the boulder and use Strength (6 presses close the dialogs)
goals = {(42, 38), (43, 38), (42, 39), (43, 39)}
path = solve(free, others, start, boulders[0], goals)
assert path, 'no plan'
# replay the plan: push = two taps (the first only turns), free step = one tap; checkpoints every 8 path steps
p, b = start, boulders[0]
steps, expect = [], []
for i, d in enumerate(path):
    dx, dz = DIRS[d]
    n = (p[0] + dx, p[1] + dz)
    if n == b:
        steps += [d, d]
        b = (b[0] + dx, b[1] + dz)
    else:
        steps.append(d)
    p = n
    if (i + 1) % 8 == 0 or i == len(path) - 1:
        steps.append('pos')
        expect.append(p)
print('plan: %d path steps, %d taps, ends player %s boulder %s' % (len(path), len(steps), p, b), flush=True)
res = send(steps + ['wait 250', 'pos', 'tshot pushed'])
got = [tuple(r[1:]) for r in res]
for i, (e, gpos) in enumerate(zip(expect + [p], got)):
    print('checkpoint %d: expected %s got %s %s' % (i, e, gpos, '' if e == gpos else '<-- MISMATCH'), flush=True)
assert got[-1] == p, 'push plan desync'
blocked = (others | {b}) - rocks                      # the barrier rocks should be hidden now
keys = route(free, blocked, p, (25, 37))
assert keys, 'no route back to the barrier'
res = send(keys + ['pos'])
print('back at the barrier:', tuple(res[-1][1:]), flush=True)
res = send(['right', 'right', 'right', 'right', 'right', 'pos', 'tshot through'])
end = tuple(res[-1][1:])
print('walking east from (25,37) ends at', end)
print('PASS: the barrier opened' if end[0] >= 29 else 'FAIL: the barrier did not open')
