"""Automated walk through the rebuilt Mt. Moon (test only): Route 3 side -> 1F -> ... -> Route 4 exit, using only the ROM's own data. argv: rom, start_map, goal_map."""
import sys, struct, collections
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
import ndspy.rom, ndspy.narc
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE
OUT = d.root
X, Z = 0x1da6f6, 0x1da6fe
UP, DOWN, LEFT, RIGHT, A, B = 4, 5, 6, 7, 8, 0
KEY = {(0, -1): UP, (0, 1): DOWN, (-1, 0): LEFT, (1, 0): RIGHT}
MAPS = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else [555, 556, 557]
START, GOAL = int(sys.argv[2]), int(sys.argv[3])

def pos():
    r = d.ram(); return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]
def invalid(p): return p[0] < 8 or p[1] > 4000
def bottom_is_menu():
    d.shot('_p.png')
    from PIL import Image
    r, g, b = Image.open(OUT / '_p.png').convert('RGB').getpixel((20, 300))
    return g > 150 and r < 90 and b < 150
def dialog_active():
    from PIL import Image
    im = Image.open(OUT / '_p.png').convert('RGB')
    return sum(min(im.getpixel((x, 151))) > 235 for x in (30, 60, 100, 150, 200, 230)) >= 5
def top_image():
    from PIL import Image
    d.shot('_t.png'); return Image.open(OUT / '_t.png').convert('L').crop((0, 0, 256, 192))
def image_diff(a, b):
    from PIL import ImageChops
    diff = ImageChops.difference(a, b).point(lambda v: 255 if v > 40 else 0)
    return sum(1 for v in diff.getdata() if v) / (256 * 192)
def mash(n=1):
    for _ in range(n): d.run(6, A); d.run(24)
def battle():
    for i in range(150):
        if bottom_is_menu(): return i
        d.touch = (128, 270); d.run(6); d.touch = None; d.run(40)
        d.touch = (190, 240) if i % 3 != 2 else (190, 300); d.run(6); d.touch = None; d.run(60)
        d.run(6, A); d.run(30); d.run(6, A); d.run(30)
    return -1

rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
dd = rom.loadArm9().sections[0].data; recs_ext = ext.records(rom)
def rec(m): return bytes(dd[TABLE + m * 24:TABLE + m * 24 + 24]) if m < 540 else recs_ext[m - 540]
free, actors, warps = {}, {}, {}
for m in set(MAPS) | {START}:
    r = rec(m); mat = bytes(mats.files[struct.unpack_from('<H', r, 4)[0]]); w, h, hd, ht, n = mat[:5]
    ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht)); fr = set()
    for cz in range(h):
        for cx in range(w):
            land = bytes(lands.files[ids[cz * w + cx]]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
            perm = land[16 + bgs:16 + bgs + 2048]
            for lz in range(32):
                for lx in range(32):
                    if not perm[(lz * 32 + lx) * 2 + 1] & 0x80: fr.add((cx * 32 + lx, cz * 32 + lz))
    g = events_decode(ev.files[struct.unpack_from('<H', r, 16)[0]])
    free[m] = fr; actors[m] = {struct.unpack_from('<2H', a, 24) for a in g[1]}; warps[m] = [struct.unpack_from('<4H', x) for x in g[2]]
def arrival(m, anchor):
    w = warps.get(m)
    return (w[anchor][0], w[anchor][1]) if w and anchor < len(w) else None
def search(start_m, start_t):
    prev = {(start_m, start_t): None}; q = collections.deque([(start_m, start_t)])
    while q:
        st = q.popleft(); m, t = st
        if m == GOAL: 
            path = []
            while st is not None: path.append(st); st = prev[st]
            return path[::-1]
        for dx, dz in KEY:
            n = (t[0] + dx, t[1] + dz)
            if n not in free[m] or n in actors[m]: continue
            nxt = (m, n)
            for (wx, wz, dm, da) in warps[m]:
                if (wx, wz) == n and dm != m:
                    a = arrival(dm, da) if dm != GOAL else (0, 0)
                    nxt = (dm, a) if a else None
                    break
            if nxt and nxt not in prev: prev[nxt] = st; q.append(nxt)
    return None

SEEN = [False]
def step(dx, dz):
    p0 = pos()
    for _ in range(3):
        d.run(12, KEY[(dx, dz)])
        for _ in range(7):
            d.run(2)
            if invalid(pos()): SEEN[0] = True
        p1 = pos()
        if p1 != p0: return p1
    return pos()


d.boot(); cur = START; print('start', pos(), flush=True)
def settle(label):
    for _ in range(40):
        if not bottom_is_menu(): print(label, 'battle', battle(), flush=True); continue
        n = 0
        while dialog_active() and n < 80: mash(1); n += 1; bottom_is_menu()
        if n: print(label, 'dialogue pressed A', n, flush=True); continue
        break
def goto(target, label):
    for turn in range(300):
        p = pos()
        if invalid(p): settle(label); continue
        if p == target: return True
        prev = {p: None}; q = collections.deque([p]); found = None
        while q:
            t = q.popleft()
            if t == target: found = t; break
            for dx, dz in KEY:
                n = (t[0] + dx, t[1] + dz)
                if n in free[cur] and n not in actors[cur] and n not in prev: prev[n] = t; q.append(n)
        if not found: print(label, 'NO PATH', p, '->', target, flush=True); return False
        path = []; t = found
        while t != p: path.append(t); t = prev[t]
        nx = path[-1]; q2 = step(nx[0] - p[0], nx[1] - p[1]); settle(label)
    return False
# 1. walk into the boss trigger
fossil = [struct.unpack_from('<2H', a, 24) for a in events_decode(ev.files[struct.unpack_from('<H', rec(cur), 16)[0]])[1] if struct.unpack_from('<H', a, 2)[0] in (93, 94)]
print('fossil actors', fossil, flush=True)
for t in ((34, 31), (34, 30), (34, 29), (34, 28)):
    if t in free[cur]: goto(t, 'to boss'); 
settle('boss'); d.shot('s1_after_boss.png'); print('after boss', pos(), flush=True)
# 2. take a fossil: stand south of the first one
fx, fz = fossil[0]
for cand in ((fx, fz + 1), (fx + 1, fz + 1), (fx - 1, fz + 1), (fx, fz + 2)):
    if cand in free[cur] and goto(cand, 'to fossil'): break
print('at', pos(), flush=True)
d.run(12, UP); d.run(20); settle('fossil face')
d.run(6, A); d.run(40); d.shot('s2_fossil_prompt.png'); [(d.run(6, A), d.run(70), d.shot('f%d.png' % i)) for i in range(6)]; settle('fossil'); d.shot('s3_after_fossil.png'); print('after fossil', pos(), flush=True)
# 3. step out of the fossil area: the ambush should fire
for _ in range(8):
    p = pos(); step(0, 1); settle('ambush')
d.shot('s4_after_ambush.png'); print('end', pos(), flush=True)
