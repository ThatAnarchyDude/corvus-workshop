"""Yellow's Pokemon Tower floors as real HeartGold floor models with matching collision (stage 1: floor art + walkable grid for one floor).

Source of truth is pret/pokeyellow (maps/PokemonTower<N>F.blk, gfx/blocksets/cemetery.bst, gfx/tilesets/cemetery.png, Cemetery_Coll passable tiles).
Each floor becomes: one 2-bit texture rendered from Yellow's own tiles (512x512, 1 texel per Game Boy pixel), a single textured quad model, a 32x32 walk/block grid
and a flat height file. The floor sits at chunk tiles OX..OX+19, OZ..OZ+17 (a Yellow step = 2x2 Game Boy tiles = 1 HeartGold tile).
"""
import math
import struct
from pathlib import Path
from PIL import Image
from title_models import info, container, single_block, fifo

COLL = {0x01, 0x10, 0x13, 0x1b, 0x22, 0x42, 0x52}          # Cemetery_Coll: tile ids the player can walk on (bottom-left tile of a step)
SHADES = {0: 3, 85: 2, 170: 1, 255: 0}                         # png grey -> palette slot (0 lightest)
PALETTE = [(24, 22, 28), (17, 14, 22), (9, 7, 14), (2, 1, 5)]  # 5-bit RGB, violet stone
OX, OZ = 12, 14                                                  # Yellow step (0,0) lands on chunk tile (OX, OZ)
ORIG_MODEL = False
STYLE = '3d'
SCALE = 2           # HeartGold tiles per Yellow step: the room is 40x36 tiles, so each floor is a 2x2 grid of 32x32 chunks
CHUNKS = 2
WARPS = {1: [(10, 17), (11, 17), (18, 9)]}   # Yellow warp steps per floor (kept walkable)
PLAIN = False
TEMPLATE = None
SIZE = 512
W, H = 10, 9                                                   # blocks


def load(ref, floor):
    ref = Path(ref)
    blk = (ref / f'maps/PokemonTower{floor}F.blk').read_bytes()
    bst = (ref / 'gfx/blocksets/cemetery.bst').read_bytes()
    sheet = Image.open(ref / 'gfx/tilesets/cemetery.png').convert('L')
    return blk, bst, sheet


def tiles(blk, bst):
    """40x36 grid of 8x8 tile ids from the 10x9 block map."""
    grid = [[0] * (W * 4) for _ in range(H * 4)]
    for by in range(H):
        for bx in range(W):
            block = blk[by * W + bx]
            for ty in range(4):
                for tx in range(4):
                    grid[by * 4 + ty][bx * 4 + tx] = bst[block * 16 + ty * 4 + tx]
    return grid


def image(grid, sheet):
    img = Image.new('P', (512, 512), 3)                        # unused area = darkest
    for ty, row in enumerate(grid):
        for tx, t in enumerate(row):
            sx, sy = (t % 16) * 8, (t // 16) * 8
            tile = sheet.crop((sx, sy, sx + 8, sy + 8))
            img.paste(Image.frombytes('P', (8, 8), bytes(SHADES[v] for v in tile.tobytes())), (tx * 8, ty * 8))
    return img


def pack_2bpp(img):
    px = img.tobytes()
    return bytes(sum(px[i + k] << (2 * k) for k in range(4)) for i in range(0, len(px), 4))


def walk_grid(grid):
    """Per Yellow step: True when walkable. Step (sx, sy) -> bottom-left tile (2sx, 2sy+1)."""
    return [[grid[2 * sy + 1][2 * sx] in COLL for sx in range(W * 2)] for sy in range(H * 2)]


EXIT_TYPE = 101      # tile behaviour byte HeartGold uses on its own exit mats (the most common one on native warp tiles); stairs work with 0
ARRIVAL = {}         # floor -> {Yellow warp index: (global tile x, z)}: where the player lands, one step outside the ring
RING = {}            # floor -> [(global tile x, z, behaviour, Yellow warp index)]: extra warp tiles on the open sides of each warp block
TK = {}              # floor -> {(room tile x, z): kind} filled by install(), used to keep people off the walls
EXITS = {}           # floor -> Yellow steps whose warp leaves the building


def permissions(walk, exits=()):
    cells = [0x8000] * 1024
    for sy, row in enumerate(walk):
        for sx, ok in enumerate(row):
            if ok:
                cells[(OZ + sy) * 32 + OX + sx] = 0
    for sx, sy in exits:
        cells[(OZ + sy) * 32 + OX + sx] = EXIT_TYPE
    return struct.pack('<1024H', *cells)


def quad_model(texname, u1, v1):
    """Single-quad BMD0 (two triangles) over the Yellow floor, textured by name from the area's texture bank."""
    scale = 64
    CODE = SIZE.bit_length() - 4
    x0, z0 = (OX - 16) * 16 / scale, (OZ - 16) * 16 / scale
    x1, z1 = x0 + 20 * 16 / scale, z0 + 18 * 16 / scale
    def vtx(x, z, s, t):
        return [(0x22, [(round(s * 16) & 0xffff) | (round(t * 16) << 16)]),
                (0x20, [0x7fff]),
                (0x23, [round(x * 4096) & 0xffff | (0 << 16), round(z * 4096) & 0xffff])]
    # triangle list: (x0,z0) (x1,z0) (x1,z1) and (x0,z0) (x1,z1) (x0,z1); y = 0
    cmds = [(0x29, [(31 << 16) | 0xc0]), (0x2a, [0]), (0x40, [0])]
    for (x, z, s, t) in ((x0, z0, 0, 0), (x1, z0, u1, 0), (x1, z1, u1, v1), (x0, z0, 0, 0), (x1, z1, u1, v1), (x0, z1, 0, v1)):
        cmds += vtx(x, z, s, t)
    cmds.append((0x41, []))
    shape = fifo(cmds)
    names = ['body']
    node_dict = info(names, [struct.pack('<I', 0)])
    node_dict = info(names, [struct.pack('<I', len(node_dict))])
    nodes = struct.pack('<HH3i', 6, 0, 0, 0, 0)
    sbc = bytearray([0x26, 0, 0, 0, 0, 2, 0, 1, 4, 0, 0x0b, 5, 0, 0x2b, 1])
    sbc.extend(b'\0' * (-len(sbc) % 4))
    empty = info([], [])
    matdict = info(['paint'], [struct.pack('<I', 128)])
    mapping = info([texname], [struct.pack('<HBB', 4 + 40 + 2 * 40, 1, 0)])
    material = struct.pack('<HH6I2H2H2I', 0, 44, 0x7fff | 0x8000 | (0x7fff << 16), 0,
                           (31 << 16) | 0xc0, 0xffffffff, (2 << 26) | (CODE << 20) | (CODE << 23) | (3 << 16),
                           0xffffffff, 0, 0x11cf, SIZE, SIZE, 4096, 4096)
    mats = struct.pack('<HH', 4 + len(matdict), 4 + len(matdict) + len(mapping)) + matdict + mapping + mapping + b'\0' * 4
    assert len(mats) == struct.unpack_from('<I', matdict, 20)[0]
    mats += material
    shdict = info(['part0'], [struct.pack('<I', 0)])
    at = len(shdict)
    shdict = info(['part0'], [struct.pack('<I', at)])
    piece = struct.pack('<HHIII', 0, 16, 1, 16, len(shape)) + shape
    offsets = [64 + len(node_dict) + len(nodes)]
    offsets.append(offsets[0] + len(sbc))
    offsets.append(offsets[1] + len(mats))
    offsets.append(offsets[2] + len(shdict) + len(piece))
    header = struct.pack('<5I8B2i4H6h2i', offsets[-1], *offsets, 0, 0, 0, 1, 1, 1, 1, 0,
                         scale * 4096, round(4096 / scale), 6, 1, 2, 0, -12288, -1024, -12288, 24576, 2048, 24576, scale * 4096, round(4096 / scale))
    mdl = header + node_dict + nodes + bytes(sbc) + mats + shdict + piece
    return container(b'BMD0', [single_block(b'MDL0', 'ytower', mdl)], 2)


def tile_grid(kinds, h, w):
    """Expand the step grid (kinds[(sx, sy)]) to a SCALE-times bigger tile grid: dict (tx, tz) -> kind, local to the room (0,0 = room's top-left tile)."""
    out = {}
    for (sx, sy), k in kinds.items():
        for dx in range(SCALE):
            for dz in range(SCALE):
                out[(sx * SCALE + dx, sy * SCALE + dz)] = k
    return out


def install(rom, ref, floor, ext_map):
    import copy
    import ndspy.narc
    import ndspy.texture
    import map_header_extension as ext
    import yellow_3d
    import yellow_imd
    blk, bst, sheet = load(ref, floor)
    grid = tiles(blk, bst)
    areas = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/2')])
    banks = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/4')])
    mats = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')])
    lands = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    data = bytearray(o.data)
    rec = ext.table_address(rom) - o.ramAddress + 24 * (ext_map - ext.NATIVE_COUNT)
    old_area, old_matrix = data[rec + 1], struct.unpack_from('<H', data, rec + 4)[0]
    # textures: HeartGold's own violet Bell Tower textures (area 112 = tower_look.py's bank)
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[112], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)

    def grab(tex_name, pal_name, new):
        t = tx[tex_name]
        assert int(t.format) in (2, 3), (tex_name, t.format)
        return dict(name=new, fmt=int(t.format), w=t.width, h=t.height, pixels=bytes(t.data1), palette=[(c.r, c.g, c.b) for c in pl[pal_name].colors])
    textures = [grab('cliff01gs', 'cliff01', 'TowFloor'), grab('d15_wall01', 'd15_wall01_pl', 'TowWall'), grab('d15_genkan', 'd15_genkan_pl', 'TowStone')]
    mats_ = [('floor', 0, 'floor'), ('wall_top', 2, 'wall_top', (23, 17)), ('wall_slope', 0, 'wall_slope', (17, 12)), ('stone_top', 2, 'stone_top', (29, 24)), ('stone_side', 2, 'stone_side', (22, 16))]
    walk = walk_grid(grid)
    keep = set(WARPS.get(floor, []))
    kinds = yellow_3d.classify(walk, keep)
    tk = tile_grid(kinds, len(walk), len(walk[0]))
    TK[floor] = tk
    # permissions per chunk, geometry per chunk
    # Warp tiles carry a behaviour byte that says which way you must be walking to trigger them (read off HeartGold's own warps):
    # tested: 101 fires going down only, 107 going left only, 110 from any direction; 0, 94, 95 and 105 do not fire going up. Each Yellow warp block is tagged for the side it is entered from.
    ENTRY = {'N': 110, 'S': 110, 'W': 110, 'E': 110}                 # side of the block the player comes from -> behaviour
    warp_type = {}
    RING[floor] = []
    blocks = {}
    for wi, (sx, sy) in enumerate(WARPS.get(floor, [])):
        blocks[wi] = {(sx * SCALE + dx, sy * SCALE + dz) for dx in range(SCALE) for dz in range(SCALE)}
    all_block = set().union(*blocks.values()) if blocks else set()
    for wi, (sx, sy) in enumerate(WARPS.get(floor, [])):
        block = blocks[wi]
        x_lo, x_hi, z_lo, z_hi = sx * SCALE, sx * SCALE + SCALE - 1, sy * SCALE, sy * SCALE + SCALE - 1
        sides = {'N': [(x, z_lo - 1) for x in range(x_lo, x_hi + 1)], 'S': [(x, z_hi + 1) for x in range(x_lo, x_hi + 1)],
                 'W': [(x_lo - 1, z) for z in range(z_lo, z_hi + 1)], 'E': [(x_hi + 1, z) for z in range(z_lo, z_hi + 1)]}
        open_sides = [k for k, cells_ in sides.items() if any(tk.get(c) == 'floor' and c not in all_block for c in cells_)]
        for t in block:
            warp_type[t] = 0                 # inert: you arrive on the block, and stepping around inside it must not fire the way back
        ARRIVAL.setdefault(floor, {})
        placed = None
        for side in open_sides:                  # arrival: two tiles out from the block on its first open side, off every warp tile
            u = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}[side]
            cands = [(c[0] + u[0], c[1] + u[1]) for c in sides[side]]
            cands = [c for c in cands if tk.get(c) == 'floor' and c not in all_block]
            if cands:
                placed = cands[len(cands) // 2]
                break
        ARRIVAL[floor][wi] = (OX + placed[0], OZ + placed[1]) if placed else (OX + min(block)[0], OZ + min(block)[1])
        for side in open_sides:                  # a ring tile per open side: stepping onto it in the matching direction fires the warp
            for c in sides[side]:
                if tk.get(c) == 'floor' and c not in all_block and c not in warp_type:
                    warp_type[c] = ENTRY[side]
                    RING[floor].append((OX + c[0], OZ + c[1], ENTRY[side], wi))
    cells = {}
    for (tx_, tz_), k in tk.items():
        gx, gz = OX + tx_, OZ + tz_
        cells[(gx, gz)] = warp_type.get((tx_, tz_), 0)
        if k == 'wall' or k == 'stone':
            cells[(gx, gz)] = None
    chunk_land = []
    texture_bank = None
    for cz in range(CHUNKS):
        for cx in range(CHUNKS):
            perm = bytearray()
            for lz in range(32):
                for lx in range(32):
                    v = cells.get((cx * 32 + lx, cz * 32 + lz), None)
                    perm += bytes([0, 0x80]) if v is None else bytes([v, 0])
            kinds_c = {}
            for (tx_, tz_), k in tk.items():
                gx, gz = OX + tx_, OZ + tz_
                if gx // 32 == cx and gz // 32 == cz:
                    kinds_c[(gx - cx * 32, gz - cz * 32)] = k
            full = {(OX + tx_ - cx * 32, OZ + tz_ - cz * 32): k for (tx_, tz_), k in tk.items()}      # neighbours across chunk edges
            quads = yellow_3d.geometry_sloped(kinds_c, full, -4.0, -4.0)
            if not any(quads.values()):
                quads['floor'] = [((3.9, -0.5, 3.9, 0, 0, 0, 1, 0), (3.9, -0.5, 3.95, 0, 1, 0, 1, 0), (3.95, -0.5, 3.95, 1, 1, 0, 1, 0), (3.95, -0.5, 3.9, 1, 0, 0, 1, 0))]
            imd_text = yellow_imd.imd_multi(textures, mats_, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H)
            model, nsbtx = yellow_imd.convert(imd_text, f'LavTowF{floor}c{cx}{cz}')
            bdhc = bytes(lands.files[437])[-66:]
            land = struct.pack('<4I', 2048, 0, len(model), len(bdhc)) + bytes.fromhex('34120000') + bytes(perm) + model + bdhc
            chunk_land.append(len(lands.files))
            lands.files.append(land)
    # texture bank holding all three textures (the per-chunk converter output only keeps textures a chunk uses)
    dummy = {m[2]: [((0, 0, 0, 0, 0, 0, 1, 0), (0, 0, 0.01, 0, 1, 0, 1, 0), (0.01, 0, 0.01, 1, 1, 0, 1, 0), (0.01, 0, 0, 1, 0, 0, 1, 0))] for m in mats_}
    _, texture_bank = yellow_imd.convert(yellow_imd.imd_multi(textures, mats_, dummy, -4.0, -4.0, 4.0, 4.0, 0.1), f'LavTowF{floor}tex')
    area = bytearray(areas.files[old_area])
    new_bank = len(banks.files)
    banks.files.append(texture_bank)
    struct.pack_into('<H', area, 2, new_bank)
    new_area = len(areas.files)
    assert new_area < 256
    areas.files.append(bytes(area))
    # matrix: CHUNKS x CHUNKS, same flags as the floor's old 1x1 matrix; land ids row-major
    old = bytes(mats.files[old_matrix])
    w, h, hd, ht, n = old[:5]
    assert (w, h) == (1, 1)
    head5 = bytes([CHUNKS, CHUNKS, hd, ht, n]) + old[5:5 + n]
    off = 5 + n
    header_ids = old[off:off + 2 * hd] * (CHUNKS * CHUNKS) if hd else b''
    heights = old[off + 2 * hd:off + 2 * hd + ht] * (CHUNKS * CHUNKS) if ht else b''
    new_matrix = head5 + header_ids + heights + b''.join(struct.pack('<H', i) for i in chunk_land)
    # NB: native matrices store [headers][heights][lands] cell by cell per flag; copied the same way
    mid = len(mats.files)
    mats.files.append(new_matrix)
    data[rec + 1] = new_area
    struct.pack_into('<H', data, rec + 4, mid)
    o.data = data
    rom.files[o.fileID] = o.save(compress=False)
    for p, a in (('a/0/4/2', areas), ('a/0/4/4', banks), ('a/0/4/1', mats), ('a/0/6/5', lands)):
        rom.files[rom.filenames.idOf(p)] = a.save()
    return dict(floor=floor, map=ext_map, area=new_area, bank=new_bank, matrix=mid, lands=chunk_land, walkable_steps=sum(map(sum, walk)))


if __name__ == '__main__':
    import sys
    import ndspy.rom
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(install(rom, sys.argv[3], 1, 540))
    rom.saveToFile(sys.argv[2])
