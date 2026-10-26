"""Automated climb of the rebuilt Pokemon Tower: Lavender -> 1F -> ... -> 7F -> Mr. Fuji (test fixture save, strong Pokemon). Logs progress to stdout."""
import sys, struct, collections
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
import ndspy.rom, ndspy.narc
import yellow_floor as yf, yellow_3d as g3, yellow_tower as yt
import map_header_extension as ext
from opening import events_decode
REF = '/tmp/claude-1000/-home-thatanarchydude-code-corvus-workshop/3e4d4996-5a1f-42bc-83eb-6fb9d56c43f0/scratchpad/ref-pokeyellow'
OUT = d.root
X, Z = 0x1da6f6, 0x1da6fe
UP, DOWN, LEFT, RIGHT, A, B = 4, 5, 6, 7, 8, 0
KEY = {(0, -1): UP, (0, 1): DOWN, (-1, 0): LEFT, (1, 0): RIGHT}

def pos():
    r = d.ram(); return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]

def bottom_is_menu():
    d.shot('_p.png')
    from PIL import Image
    im = Image.open(OUT / '_p.png').convert('RGB')
    r, gg, b = im.getpixel((20, 300))
    return gg > 150 and r < 90 and b < 150

def top_image():
    from PIL import Image
    d.shot('_t.png')
    return Image.open(OUT / '_t.png').convert('L').crop((0, 0, 256, 192))

def image_diff(a, b):
    from PIL import ImageChops
    diff = ImageChops.difference(a, b).point(lambda v: 255 if v > 40 else 0)
    return sum(1 for v in diff.getdata() if v) / (256 * 192)

def dialog_active():
    from PIL import Image
    im = Image.open(OUT / '_p.png').convert('RGB')
    return sum(min(im.getpixel((x, 151))) > 235 for x in (30, 60, 100, 150, 200, 230)) >= 5

# ---- floor data from the finished ROM + Yellow
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); recs = ext.records(rom)
DATA = {f: yt.parse(REF, f) for f in range(1, 8)}
free, actors, warps = {}, {}, {}
for f in range(1, 8):
    blk, bst, sheet = yf.load(REF, f); grid = yf.tiles(blk, bst); walk = yf.walk_grid(grid)
    keep = {(w[0], w[1]) for w in DATA[f]['warps']}
    tk = yf.tile_grid(g3.classify(walk, keep), 0, 0)
    free[f] = {(yf.OX + a, yf.OZ + b) for (a, b), k in tk.items() if k == 'floor'}
    g = events_decode(ev.files[struct.unpack_from('<H', recs[f - 1], 16)[0]])
    actors[f] = {struct.unpack_from('<2H', a, 24) for a in g[1] if not (f == 7 and struct.unpack_from('<H', a, 2)[0] in (221, 222))}
    if f == 7:
        fuji = [struct.unpack_from('<2H', a, 24) for a in g[1] if struct.unpack_from('<H', a, 2)[0] == 317][0]
    warps[f] = [struct.unpack_from('<4H', w) for w in g[2]]

mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
TYPE_DIR = {101: (0, 1), 110: None, 106: (1, 0), 107: (-1, 0)}      # None = fires from any direction
def entry_dir(f, x, z):
    mat = bytes(mats.files[struct.unpack_from('<H', recs[f - 1], 4)[0]]); w, h, hd, ht, n = mat[:5]
    ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    land = bytes(lands.files[ids[(z // 32) * w + x // 32]]); o = 16 + 4 + ((z % 32) * 32 + (x % 32)) * 2
    return TYPE_DIR.get(land[o], (0, -1))        # plain tiles fire when walked onto going up

def bfs_warp(f, start, ups, extra=()):
    """Path (list of tiles) that ends by stepping onto a tile of `ups` in the direction that tile needs."""
    blocked = actors[f] | set(extra) | {t for t, dst in tile_dest[f].items() if t not in ups}        # a player would not walk through the other stairs' ring
    need = {t: entry_dir(f, *t) for t in ups}
    prev = {(start, None): None}; q = collections.deque([(start, None)])
    while q:
        st = q.popleft(); p = st[0]
        for dx, dz in KEY:
            n = (p[0] + dx, p[1] + dz)
            if n not in free[f] or n in blocked:
                continue
            ns = (n, (dx, dz))
            if ns in prev:
                continue
            prev[ns] = st
            if n in need and (need[n] is None or need[n] == (dx, dz)):
                path = []; cur = ns
                while cur is not None:
                    path.append(cur[0]); cur = prev[cur]
                return path[::-1][1:]
            q.append(ns)
    return None

def bfs(f, start, goals, extra=()):
    blocked = actors[f] | set(extra)
    prev = {start: None}; q = collections.deque([start])
    while q:
        p = q.popleft()
        if p in goals:
            path = []
            while prev[p] is not None:
                path.append(p); p = prev[p]
            return path[::-1]
        for dx, dz in KEY:
            n = (p[0] + dx, p[1] + dz)
            if n in free[f] and n not in blocked and n not in prev:
                prev[n] = p; q.append(n)
    return None

def mash(n=1):
    for _ in range(n):
        d.run(6, A); d.run(24)

def battle():
    """Fight until the bottom screen is the field menu again. Mewtwo: Mist / Psystrike (top right) / Recover / Future Sight (bottom right)."""
    for i in range(150):
        if bottom_is_menu():
            return i
        d.touch = (128, 270); d.run(6); d.touch = None; d.run(40)
        d.touch = (190, 240) if i % 3 != 2 else (190, 300); d.run(6); d.touch = None; d.run(60)
        d.run(6, A); d.run(30); d.run(6, A); d.run(30)
    return -1

SEEN_INVALID = [False]
def invalid(p):
    return p[0] < 8 or p[1] > 1000

def step(dx, dz):
    p0 = pos()
    for attempt in range(3):
        d.run(12, KEY[(dx, dz)])
        for _ in range(7):
            d.run(2)
            if invalid(pos()):
                SEEN_INVALID[0] = True
        p1 = pos()
        if p1 != p0:
            return p1
    return pos()

def walk_to(f, goals, label, limit=500, ups=None):
    """Walk on floor f to `goals` (tiles) or, when `ups` is given, until stepping onto one of those warp tiles the right way fires a floor change."""
    temp = {}
    for turn in range(limit):
        p = pos()
        if ups is None and p in goals:
            return True
        if invalid(p):
            if not bottom_is_menu():
                print(label, 'battle during transition, rounds', battle(), flush=True)
            else:
                d.run(40); mash(1)
            continue
        temp = {t: e for t, e in temp.items() if e > turn}
        path = bfs_warp(f, p, ups, temp) if ups is not None else bfs(f, p, goals, temp)
        if path is None:
            print(label, 'NO PATH from', p, flush=True); return False
        nxt = path[0]
        SEEN_INVALID[0] = False
        q = step(nxt[0] - p[0], nxt[1] - p[1])
        if q != p and nxt in tile_dest[f] and tile_dest[f][nxt] != 53:        # stepped onto a warp tile: did the floor change?
            seen = SEEN_INVALID[0]
            img0 = top_image()
            for _ in range(45):
                if invalid(pos()):
                    seen = True
                d.run(4)
            if not bottom_is_menu():
                print(label, 'battle at the stairs, rounds', battle(), flush=True)
                seen = False
            else:
                for _ in range(60):
                    if not invalid(pos()):
                        break
                    d.run(30)
                if seen or image_diff(img0, top_image()) > 0.30:
                    d.run(60)
                    return ('warp', tile_dest[f][nxt])
        if invalid(q) or SEEN_INVALID[0]:
            fought = False
            for _ in range(80):
                if not bottom_is_menu():
                    print(label, 'battle during step, rounds', battle(), flush=True); SEEN_INVALID[0] = False; fought = True
                    q = pos()
                    if not invalid(q):
                        break
                    continue
                d.run(40)
                q = pos()
                if not invalid(q):
                    break
        if q == p:
            handled = False
            if not bottom_is_menu():
                print(label, 'battle at', p, 'rounds', battle(), flush=True); handled = True
            else:
                n = 0
                mash(2)
                while dialog_active() and n < 60:
                    mash(1); n += 1; bottom_is_menu()
                if n:
                    print(label, 'dialogue at', p, 'pressed A', n, flush=True); handled = True
            if pos() == p and not handled:
                temp[nxt] = turn + 12
                d.shot(f'stuck_{label}.png')
    return False

tile_dest = {f: {(w[0], w[1]): w[2] for w in warps[f]} for f in warps}

def goal_block(f, wi):
    """All tiles of the 2x2 warp block of Yellow warp index wi on floor f."""
    return {(w[0], w[1]) for w in warps[f][4 * wi:4 * wi + 4]}

d.boot()
print('start', pos(), flush=True)
d.shot('00_start.png')
# the Radio Tower script should carry us to 1F
d.run(300)
print('after entrance', pos(), flush=True)
floor = 1
for _ in range(20):
    if floor >= 7:
        break
    ups = {(w[0], w[1]) for w in warps[floor] if w[2] == 540 + floor}      # every warp tile (block and ring) that leads one floor up
    r = walk_to(floor, None, f'{floor}F', ups=ups)
    if isinstance(r, tuple):
        newf = r[1] - 539
        print(f'{floor}F -> warp to map {r[1]} = floor {newf}', pos(), flush=True)
        floor = newf
        d.shot(f'{floor:02d}_arrive_{floor}F.png')
    else:
        d.shot(f'fail_{floor}F.png'); print('FAILED on', floor, pos(), flush=True); break
print('done route, now', floor, pos(), flush=True)
if floor == 7:
    goals = {(fuji[0], fuji[1] + 1)}
    r = walk_to(7, goals, '7F-fuji')
    print('7F to Fuji ->', r, pos(), 'fuji at', fuji, flush=True)
    d.shot('90_before_fuji.png')
    d.run(12, UP); d.run(20)
    for i in range(14):
        mash(1); d.shot(f'91_fuji_{i:02d}.png')
    print('end', pos(), flush=True)
