"""Yellow cave floors (Mt. Moon, ...) rebuilt as HeartGold 3D maps: floor, sloped rock walls, boulders, collision from Yellow's walk grid, warps as inert blocks + rings.

Same method as the Pokemon Tower (yellow_floor.py / yellow_3d.py / yellow_imd.py) generalised: any pret/pokeyellow .blk + blockset + tileset, any size (a 2x scale floor of up to 3x3 chunks),
textures chosen from an existing HeartGold area bank. Yellow step (x, y) = SCALE x SCALE tiles at global tile (OX + SCALE*x, OZ + SCALE*y).
Warp behaviour tags (tested): 101 fires going down only, 107 going left only, 110 from any direction; each stair block is inert and ringed with 110 tiles; arrival events one step outside.
"""
import struct
from collections import deque
from pathlib import Path
import ndspy.narc
import ndspy.texture
from PIL import Image
import map_header_extension as ext
import yellow_3d
import yellow_imd

CAVERN_COLL = {0x05, 0x15, 0x18, 0x1a, 0x20, 0x21, 0x22, 0x2a, 0x2d, 0x30}      # Cavern_Coll (pokeyellow data/tilesets/collision_tile_ids.asm)
FACILITY_COLL = {0x01, 0x10, 0x11, 0x13, 0x1b, 0x20, 0x21, 0x22, 0x30, 0x31, 0x32, 0x42, 0x43, 0x48, 0x52, 0x55, 0x58, 0x5e}      # Facility_Coll (same file)
SCALE = 2
CHUNK = 32
ROCK_MIN = 3          # a blocked piece smaller than this many steps, not touching the edge, is a boulder; anything bigger is rock wall
STATE = {}            # map name -> dict(tk=..., ring=[...], arrival={...}, geometry stats)


def load(ref, name, W, H, tileset='cavern', coll=CAVERN_COLL, edits=None):
    """edits: {(block x, block y): block id} applied to the .blk before it is read (e.g. a gate block replaced by plain floor)."""
    ref = Path(ref)
    blk = bytearray((ref / f'maps/{name}.blk').read_bytes())
    assert len(blk) == W * H, (name, len(blk), W * H)
    for (ex, ey), block in (edits or {}).items():
        blk[ey * W + ex] = block
    bst = (ref / f'gfx/blocksets/{tileset}.bst').read_bytes()
    grid = [[0] * (W * 4) for _ in range(H * 4)]
    for by in range(H):
        for bx in range(W):
            block = blk[by * W + bx]
            for ty in range(4):
                for tx in range(4):
                    grid[by * 4 + ty][bx * 4 + tx] = bst[block * 16 + ty * 4 + tx]
    walk = [[grid[2 * sy + 1][2 * sx] in coll for sx in range(W * 2)] for sy in range(H * 2)]
    return grid, walk


def classify(walk, keep):
    """step -> 'floor' | 'wall' | 'stone'. Blocked pieces touching the room's edge, or with ROCK_MIN or more steps, are wall; small enclosed bits are boulders."""
    h, w = len(walk), len(walk[0])
    free = lambda x, y: 0 <= x < w and 0 <= y < h and (walk[y][x] or (x, y) in keep)
    kinds, seen = {}, set()
    for y in range(h):
        for x in range(w):
            if free(x, y):
                kinds[(x, y)] = 'floor'
    for y in range(h):
        for x in range(w):
            if (x, y) in kinds or (x, y) in seen:
                continue
            comp, queue, edge = [], deque([(x, y)]), False
            seen.add((x, y))
            while queue:
                px, py = queue.popleft()
                comp.append((px, py))
                if px in (0, w - 1) or py in (0, h - 1):
                    edge = True
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (px + dx, py + dy)
                    if 0 <= n[0] < w and 0 <= n[1] < h and n not in kinds and n not in seen:
                        seen.add(n)
                        queue.append(n)
            k = 'wall' if edge or len(comp) >= ROCK_MIN else 'stone'
            for c in comp:
                kinds[c] = k
    return kinds


def tile_grid(kinds):
    out = {}
    for (sx, sy), k in kinds.items():
        for dx in range(SCALE):
            for dz in range(SCALE):
                out[(sx * SCALE + dx, sy * SCALE + dz)] = k
    return out


def install(rom, ref, name, ext_map, W, H, warps, OX, OZ, CX, CZ, tex_src_area, tex_spec, mats, diffuse, depth=2, tileset='cavern', coll=None, extra_floor=(), edits=None):
    """Rebuild the floor of header record `ext_map` (already installed) from Yellow map `name` (W x H blocks) laid out in a CX x CZ chunk matrix.
    warps: Yellow warp steps [(x, y)]. tex_spec: [(texture name, palette name, new name)] x4 = floor, wall face, wall top, boulder. Returns a report dict; per-map state in STATE[name]."""
    grid, walk = load(ref, name, W, H, tileset, coll or CAVERN_COLL, edits)
    keep = set(warps) | set(extra_floor)       # steps forced open: warps, and objects that stand on furniture in Yellow
    kinds = classify(walk, keep)
    tk = tile_grid(kinds)
    areas = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/2')])
    banks = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/4')])
    mats_n = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')])
    lands = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    data = bytearray(o.data)
    rec = ext.table_address(rom) - o.ramAddress + 24 * (ext_map - ext.NATIVE_COUNT)
    old_area, old_matrix = data[rec + 1], struct.unpack_from('<H', data, rec + 4)[0]
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[tex_src_area], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)

    def grab(tname, pname, new):
        t = tx[tname]
        assert int(t.format) in (2, 3), (tname, t.format)
        return dict(name=new, fmt=int(t.format), w=t.width, h=t.height, pixels=bytes(t.data1), palette=[(c.r, c.g, c.b) for c in pl[pname].colors])
    textures = [grab(*s) for s in tex_spec]
    # warp blocks, ring tiles and arrival tiles (same scheme as the Tower)
    block_of, all_block, ring, arrival, warp_type = {}, set(), [], {}, {}
    for wi, (sx, sy) in enumerate(warps):
        block_of[wi] = {(sx * SCALE + dx, sy * SCALE + dz) for dx in range(SCALE) for dz in range(SCALE)}
        all_block |= block_of[wi]
    for wi, (sx, sy) in enumerate(warps):
        block = block_of[wi]
        x_lo, x_hi, z_lo, z_hi = sx * SCALE, sx * SCALE + SCALE - 1, sy * SCALE, sy * SCALE + SCALE - 1
        sides = {'N': [(x, z_lo - 1) for x in range(x_lo, x_hi + 1)], 'S': [(x, z_hi + 1) for x in range(x_lo, x_hi + 1)],
                 'W': [(x_lo - 1, z) for z in range(z_lo, z_hi + 1)], 'E': [(x_hi + 1, z) for z in range(z_lo, z_hi + 1)]}
        open_sides = [k for k, cs in sides.items() if any(tk.get(c) == 'floor' and c not in all_block for c in cs)]
        for t in block:
            warp_type[t] = 0
        placed = None
        for side in open_sides:
            u = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}[side]
            cands = [(c[0] + u[0], c[1] + u[1]) for c in sides[side]]
            cands = [c for c in cands if tk.get(c) == 'floor' and c not in all_block]
            if cands:
                placed = cands[len(cands) // 2]
                break
        if placed is None:     # tight alcove: land on the block itself
            placed = min(block)
        arrival[wi] = (OX + placed[0], OZ + placed[1])
        for side in open_sides:
            for c in sides[side]:
                if tk.get(c) == 'floor' and c not in all_block and c not in warp_type:
                    warp_type[c] = 110
                    ring.append((OX + c[0], OZ + c[1], 110, wi))
    cells = {}
    for (a, b), k in tk.items():
        cells[(OX + a, OZ + b)] = None if k in ('wall', 'stone') else warp_type.get((a, b), 0)
    chunk_land, quad_counts = [], []
    yellow_3d.VISIBLE_DEPTH = depth
    for cz in range(CZ):
        for cx in range(CX):
            perm = bytearray()
            for lz in range(CHUNK):
                for lx in range(CHUNK):
                    v = cells.get((cx * CHUNK + lx, cz * CHUNK + lz), None)
                    perm += bytes([0, 0x80]) if v is None else (bytes([8, 0x0a]) if v == 0 else bytes([v, 0]))     # plain floor = behaviour 8 / flag 0x0a, the native cave tile that rolls wild encounters (plain 0 never does)
            kc = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items() if (OX + a) // CHUNK == cx and (OZ + b) // CHUNK == cz}
            full = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items()}
            quads = yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)
            if not any(quads.values()):
                quads['floor'] = [((3.9, -0.5, 3.9, 0, 0, 0, 1, 0), (3.9, -0.5, 3.95, 0, 1, 0, 1, 0), (3.95, -0.5, 3.95, 1, 1, 0, 1, 0), (3.95, -0.5, 3.9, 1, 0, 0, 1, 0))]
            quad_counts.append(sum(len(v) for v in quads.values()))
            text = yellow_imd.imd_multi(textures, mats, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H)
            model, _ = yellow_imd.convert(text, f'{name}c{cx}{cz}')
            bdhc = bytes(lands.files[437])[-66:]
            land = struct.pack('<4I', 2048, 0, len(model), len(bdhc)) + bytes.fromhex('34120000') + bytes(perm) + model + bdhc
            chunk_land.append(len(lands.files))
            lands.files.append(land)
    dummy = {m[2]: [((0, 0, 0, 0, 0, 0, 1, 0), (0, 0, 0.01, 0, 1, 0, 1, 0), (0.01, 0, 0.01, 1, 1, 0, 1, 0), (0.01, 0, 0, 1, 0, 0, 1, 0))] for m in mats}
    _, texture_bank = yellow_imd.convert(yellow_imd.imd_multi(textures, mats, dummy, -4.0, -4.0, 4.0, 4.0, 0.1), f'{name}tex')
    area = bytearray(areas.files[old_area])
    new_bank = len(banks.files)
    banks.files.append(texture_bank)
    struct.pack_into('<H', area, 2, new_bank)
    new_area = len(areas.files)
    assert new_area < 256
    areas.files.append(bytes(area))
    old = bytes(mats_n.files[old_matrix])
    w0, h0, hd, ht, n = old[:5]
    head5 = bytes([CX, CZ, hd, ht, n]) + old[5:5 + n]
    off = 5 + n
    header_ids = old[off:off + 2 * hd] * (CX * CZ) if hd else b''
    heights = old[off + 2 * hd:off + 2 * hd + ht] * (CX * CZ) if ht else b''
    mid = len(mats_n.files)
    mats_n.files.append(head5 + header_ids + heights + b''.join(struct.pack('<H', i) for i in chunk_land))
    data[rec + 1] = new_area
    struct.pack_into('<H', data, rec + 4, mid)
    o.data = data
    rom.files[o.fileID] = o.save(compress=False)
    for p, a in (('a/0/4/2', areas), ('a/0/4/4', banks), ('a/0/4/1', mats_n), ('a/0/6/5', lands)):
        rom.files[rom.filenames.idOf(p)] = a.save()
    STATE[name] = dict(tk=tk, ring=ring, arrival=arrival, kinds=kinds, OX=OX, OZ=OZ)
    return dict(name=name, map=ext_map, area=new_area, bank=new_bank, matrix=mid, chunks=(CX, CZ), quads_per_chunk=quad_counts,
                walkable_steps=sum(map(sum, walk)), steps=(W * 2, H * 2))


def place(name, x, y):
    """Global tile for something standing on Yellow step (x, y): the tile of its block with the most open floor around it (clear to the north first)."""
    st = STATE[name]
    kinds, OX, OZ = st['tk'], st['OX'], st['OZ']
    best = None
    for dz in (1, 0):
        for dx in (0, 1):
            tx, tz = SCALE * x + dx, SCALE * y + dz
            fl = lambda a, b: kinds.get((a, b)) == 'floor'
            score = (fl(tx, tz - 1) + fl(tx, tz - 2), sum(fl(tx + i, tz + j) for i in (-1, 0, 1) for j in (-1, 0, 1)), dz)
            if fl(tx, tz) and (best is None or score > best[0]):
                best = (score, tx, tz)
    assert best, (name, x, y)
    return OX + best[1], OZ + best[2]
