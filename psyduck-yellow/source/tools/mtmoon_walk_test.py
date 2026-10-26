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
    d.shot('_p.png')
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
        d.touch = ((64, 240), (190, 240), (64, 300), (190, 300))[i % 4]; d.run(6); d.touch = None; d.run(60)
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

d.boot(); cur = START; print('start', pos(), flush=True); d.shot('00_start.png')
fights = 0
for turn in range(2500):
    p = pos()
    if invalid(p):
        if not bottom_is_menu(): print('battle (transition)', battle(), flush=True)
        else: d.run(40); mash(1)
        continue
    path = search(cur, p)
    if path is None: print('NO PATH on map', cur, 'from', p); d.shot('nopath.png'); break
    if len(path) == 1: break
    nm, nt = path[1]
    t0 = path[0][1]
    if nm != cur:                                   # the next node is across a warp: step onto the warp tile
        wt = next((wx, wz) for (wx, wz, dm, da) in warps[cur] if dm == nm and (nm == GOAL or arrival(dm, da) == nt) and abs(wx - p[0]) + abs(wz - p[1]) == 1)
        dx, dz = wt[0] - p[0], wt[1] - p[1]
        # warp tile may be several steps away only if BFS joined it; here path[1] is the arrival so step toward wt
        assert abs(dx) + abs(dz) == 1, (cur, p, wt)
    else:
        dx, dz = nt[0] - p[0], nt[1] - p[1]
    SEEN[0] = False; img0 = top_image()
    q = step(dx, dz)
    if nm != cur:
        for _ in range(50):
            if SEEN[0] or invalid(pos()): SEEN[0] = True
            d.run(4)
        for _ in range(150):
            if not bottom_is_menu(): print('battle on arrival', battle(), flush=True)
            elif not invalid(pos()): break
            else: d.run(30)
        d.run(100)
        q2 = pos()
        if SEEN[0] or image_diff(img0, top_image()) > 0.30 or q2 == nt:
            print(f'warp {cur} -> {nm}  arrived {pos()} (expected {nt})', flush=True); cur = nm; d.shot(f'map{nm}_arrive.png'); continue
    if invalid(q) or SEEN[0]:
        for _ in range(80):
            if not bottom_is_menu(): print('battle during step', battle(), flush=True); fights += 1
            else: d.run(40)
            q = pos()
            if not invalid(q): break
        continue
    if q == p:
        n = 0; mash(2)
        while dialog_active() and n < 60: mash(1); n += 1; bottom_is_menu()
        if not bottom_is_menu(): print('battle at', p, battle(), flush=True); fights += 1
        elif n: print('dialogue at', p, n, flush=True)
        else:
            actors[cur].add((p[0] + dx, p[1] + dz)); print('blocked at', p, '->', (p[0] + dx, p[1] + dz), 'marking blocked', flush=True)
print('end map', cur, pos(), 'goal', GOAL, flush=True)
