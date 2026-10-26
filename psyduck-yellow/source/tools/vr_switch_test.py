"""TEST ONLY: Victory Road switch logic without a Strength Pokemon. Builds a copy where a step trigger next to the player's start walks boulder #1 of a floor onto the switch (a scripted NPC walk along a BFS path);
the frame script must then see it and hide the barrier's rocks. argv: in out floor(1-3) switch-index. Prints the player start, trigger cell and the rock positions."""
import struct, sys, collections
import ndspy.rom, ndspy.narc
import map_header_extension as ext
import victoryroad_yellow as vr
from opening import Script, end, events_decode, events_encode, script_bank
from parcel_quest import split_bank
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); floor = int(sys.argv[3]); k = int(sys.argv[4])
mid = 579 + floor + 0   # 580..582
mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
r = bytearray(ext.records(rom)[mid - ext.NATIVE_COUNT])
mat = bytes(mats.files[struct.unpack_from('<H', r, 4)[0]]); w, h, hd, ht, n = mat[:5]
lid = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht)); free = set()
for cz in range(h):
    for cx in range(w):
        land = bytes(lands.files[lid[cz * w + cx]]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
        perm = land[16 + bgs:16 + bgs + 2048]
        for lz in range(32):
            for lx in range(32):
                if not perm[(lz * 32 + lx) * 2 + 1] & 0x80: free.add((cx * 32 + lx, cz * 32 + lz))
g = events_decode(events.files[struct.unpack_from('<H', r, 16)[0]])
boulders = [(struct.unpack_from('<H', a, 0)[0], tuple(struct.unpack_from('<2H', a, 24))) for a in g[1] if struct.unpack_from('<H', a, 2)[0] == 85]
rocks = [tuple(struct.unpack_from('<2H', a, 24)) for a in g[1] if struct.unpack_from('<H', a, 2)[0] == 84]
g[1] = [a for a in g[1] if not 3000 <= struct.unpack_from('<H', a, 10)[0] < 4100]       # test copy: no trainers (their sight lines interrupt the walk)
blocked = {tuple(struct.unpack_from('<2H', a, 24)) for a in g[1]}
st = vr.SWITCHES[floor][k]
sx, sy = st[1]; target = (vr.OX + 2 * sx, vr.OZ + 2 * sy)
obj, start = boulders[0]
prev = {start: None}; q = collections.deque([start])
while q:
    c = q.popleft()
    if c == target: break
    for dx, dz, code in ((0, -1, 12), (0, 1, 13), (-1, 0, 14), (1, 0, 15)):
        nx = (c[0] + dx, c[1] + dz)
        if nx in free and nx not in prev and (nx not in blocked or nx == target): prev[nx] = (c, code); q.append(nx)
assert target in prev, 'no path'
path = []; c = target
while prev[c]: c, code = prev[c]; path.append(code)
path.reverse()
s = Script().emit(96).movement(vr.__dict__.get('x', obj) if False else obj, 'walk').emit(95)
end(s); s.moves('walk', [(code, 1) for code in path])
sid = struct.unpack_from('<H', r, 6)[0]
bank = split_bank(scripts.files[sid]); bank.append(s.finish()); entry = len(bank)
scripts.files.append(script_bank(bank)); nb = len(scripts.files) - 1
# player start: next to the first rock of this switch's barrier, trigger one step further from the rocks
tr = rocks[0] if k == 0 else rocks[-1]
cand = [(tr[0] + dx, tr[1] + dz) for dx, dz in ((0, 2), (0, -2), (2, 0), (-2, 0)) if (tr[0] + dx, tr[1] + dz) in free and (tr[0] + dx, tr[1] + dz) not in blocked]
pstart = cand[0]
KEYS = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
away = [(d, (pstart[0] + d[0], pstart[1] + d[1])) for d in KEYS if (pstart[0] + d[0], pstart[1] + d[1]) in free and (pstart[0] + d[0], pstart[1] + d[1]) not in blocked
        and abs(pstart[0] + d[0] - tr[0]) + abs(pstart[1] + d[1] - tr[1]) >= abs(pstart[0] - tr[0]) + abs(pstart[1] - tr[1])]
d, trig = away[0]
key = KEYS[d]
g[3].append(struct.pack('<Hhh5H', entry, trig[0], trig[1], 1, 1, 0, 0, vr.DUMMY_VAR))
events.files.append(events_encode(g))
rec_all = ndspy.rom.NintendoDSRom  # noqa
ovs = rom.loadArm9Overlays({ext.OV}); o = ovs[ext.OV]; ovd = bytearray(o.data)
at = ext.table_address(rom) - o.ramAddress + 24 * (mid - ext.NATIVE_COUNT)
struct.pack_into('<H', ovd, at + 6, nb); struct.pack_into('<H', ovd, at + 16, len(events.files) - 1); ovd[at] = 255       # test copy: no wild encounters
o.data = ovd; rom.files[o.fileID] = o.save(compress=False)
rom.setFileByName('a/0/1/2', scripts.save()); rom.setFileByName('a/0/3/2', events.save())
rom.saveToFile(sys.argv[2])
def route(a, b, avoid):
    pv = {a: None}; qq = collections.deque([a])
    while qq:
        c = qq.popleft()
        if c == b: break
        for dx, dz in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx = (c[0] + dx, c[1] + dz)
            if nx in free and nx not in pv and nx not in avoid: pv[nx] = c; qq.append(nx)
    assert b in pv, (a, b)
    out = []; c = b
    while pv[c]: out.append((c[0] - pv[c][0], c[1] - pv[c][1])); c = pv[c]
    return [KEYS[d_] for d_ in reversed(out)]
ring = (target[0] - 1, target[1])                                  # a free tile beside the switch, west side
if ring not in free: ring = (target[0], target[1] - 1)
walls = blocked | {target}
steps = ['wait 500', 'shot before_rocks', key, 'wait 1200'] + route(trig, ring, walls) + ['wait 200', 'shot at_switch'] + route(ring, pstart, walls) + ['wait 100', 'shot at_rocks', 'pos']
import json; json.dump(steps, open(sys.argv[5], 'w'))
print('map', mid, 'boulder', obj, start, '-> switch', target, 'steps', len(path), '| rocks', rocks, '| player start', pstart, 'trigger', trig, 'press', key)
