"""Cave warp tiles with visible art, for floors built by cave_floor.py (found 2026-11-02: cave_floor.py made every warp an inert 2x2 block drawn as plain floor, ringed by 110-behaviour tiles that fire from any
direction, so ladders were invisible and a warp fired over a strip of tiles around the block).
Per floor this rewrites, in an already built ROM:
 - the warp block itself fires (tile behaviour 110 on its 2x2 tiles, one warp event per tile) and the ring tiles become plain floor again (behaviour 8 / flag 0x0a, rolls wild encounters);
 - arrival tiles move from two steps outside the block to the tile next to it;
 - a native ladder model (building 69 'dun_stairup' or 70 'dun_stairdw', the models HeartGold's own caves use, listed by area building set 68) is placed on every floor-changing warp.
Exits to the outside (no ladder) keep their plain block. The regenerated chunk models are checked byte for byte against the stored ones first, so the walk grid that comes back out of the collision data is the one
cave_floor.install used.

Library: patch_floor(rom, spec). Callers (mtmoon_ladders.py ...) build the spec. Usage of the Mt. Moon caller: mtmoon_ladders.py <in.nds> <out.nds> <pokeyellow source>"""
import struct
import ndspy.narc
import ndspy.texture
import cave_floor as cf
import map_header_extension as ext
import yellow_3d
import yellow_imd
from opening import events_decode, events_encode

CHUNK = cf.CHUNK
SCALE = cf.SCALE
LADDER_UP, LADDER_DOWN = 69, 70                          # a/0/4/0 building models dun_stairup / dun_stairdw
BUILDING_TAIL = bytes.fromhex('0000000000000000000000000010000000100000001000000000000000000000')      # the 32 bytes every native building entry carries after its id and position
WARP_TILE = 110
PLAIN = bytes([8, 0x0a])
LADDER_Y = 0.0
TILE = yellow_3d.TILE
PAD_Y, PIT_Y = 0.02, 0.035                                # flat marker quads sit just above the floor (y = 0)


def _quad(x0, z0, x1, z1, y):
    return ((x0, y, z0, 0, 0, 0, 1, 0), (x0, y, z1, 0, 1, 0, 1, 0), (x1, y, z1, 1, 1, 0, 1, 0), (x1, y, z0, 1, 0, 0, 1, 0))


def marker_quads(lx, lz, kind):
    """Flat art under a ladder, for the 2x2 tiles whose local origin tile is (lx, lz): a dark pit (down) or a pale pad (up), the same existing cave materials Victory Road's markers use."""
    x0, z0 = -4.0 + lx * TILE, -4.0 + lz * TILE
    x1, z1 = x0 + 2 * TILE, z0 + 2 * TILE
    if kind == 'down':
        m, g = 0.08 * TILE, 0.25 * TILE
        return {'stone_top': [_quad(x0 + m, z0 + m, x1 - m, z1 - m, PAD_Y)], 'wall_slope': [_quad(x0 + g, z0 + g, x1 - g, z1 - g, PIT_Y)]}
    m = 0.06 * TILE
    return {'wall_top': [_quad(x0 + m, z0 + m, x1 - m, z1 - m, PAD_Y)]}


def parse(land):
    perm_size, buildings, model_size, bdhc_size = struct.unpack_from('<4I', land, 0)
    assert land[16:20] == bytes.fromhex('34120000')
    at = 20
    perm = land[at:at + perm_size]
    blds = land[at + perm_size:at + perm_size + buildings]
    model = land[at + perm_size + buildings:at + perm_size + buildings + model_size]
    bdhc = land[at + perm_size + buildings + model_size:]
    assert len(bdhc) == bdhc_size and len(blds) == buildings
    return perm, blds, model, bdhc


def pack(perm, blds, model, bdhc):
    return struct.pack('<4I', len(perm), len(blds), len(model), len(bdhc)) + bytes.fromhex('34120000') + perm + blds + model + bdhc


def fx(v):
    """(fraction u16, position s16) halves of a 16.16 fixed point value, in the order a building entry stores them."""
    raw = round(v * 65536)
    return raw & 0xFFFF, raw >> 16


def building(model_id, x, y, z):
    xf, xp = fx(x)
    yf, yp = fx(y)
    zf, zp = fx(z)
    return struct.pack('<IHhHhHh', model_id, xf, xp, yf, yp, zf, zp) + BUILDING_TAIL


def sides_of(block, step):
    xs = [t[0] for t in block]
    zs = [t[1] for t in block]
    x_lo, x_hi, z_lo, z_hi = min(xs), max(xs), min(zs), max(zs)
    return {'N': [(x, z_lo - 1) for x in range(x_lo, x_hi + 1)], 'S': [(x, z_hi + 1) for x in range(x_lo, x_hi + 1)],
            'W': [(x_lo - 1, z) for z in range(z_lo, z_hi + 1)], 'E': [(x_hi + 1, z) for z in range(z_lo, z_hi + 1)]}


def patch_floor(rom, spec):
    """spec: dict(map, name, W, H, CX, CZ, OX, OZ, area (texture source area), tex, mats, warps=[(step x, step y, dest map, dest anchor, kind)], kind in 'up' | 'down' | None).
    Returns a report dict."""
    mapid, OX, OZ, CX, CZ = spec['map'], spec['OX'], spec['OZ'], spec['CX'], spec['CZ']
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    sets = ndspy.narc.NARC(rom.getFileByName('a/0/4/3'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    rec = ext.records(rom)[mapid - ext.NATIVE_COUNT]
    area = rec[1]
    building_set = struct.unpack_from('<%dH' % (len(sets.files[struct.unpack_from('<H', areas.files[area], 0)[0]]) // 2), sets.files[struct.unpack_from('<H', areas.files[area], 0)[0]])
    assert LADDER_UP in building_set and LADDER_DOWN in building_set, (spec['name'], building_set)
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[spec['area']], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)

    def grab(tname, pname, new):
        t = tx[tname]
        return dict(name=new, fmt=int(t.format), w=t.width, h=t.height, pixels=bytes(t.data1), palette=[(c.r, c.g, c.b) for c in pl[pname].colors])
    textures = [grab(*s) for s in spec['tex']]
    yellow_3d.VISIBLE_DEPTH = 2
    mat = bytes(mats_n.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    land_ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    parts = {(i % w, i // w): list(parse(bytes(lands.files[lid]))) for i, lid in enumerate(land_ids)}
    W, H = spec['W'], spec['H']
    walk = []
    for sy in range(H * 2):
        row = []
        for sx in range(W * 2):
            gx, gz = OX + SCALE * sx, OZ + SCALE * sy
            row.append(not parts[(gx // CHUNK, gz // CHUNK)][0][((gz % CHUNK) * CHUNK + gx % CHUNK) * 2 + 1] & 0x80)
        walk.append(row)
    steps = [(x, y) for x, y, *_ in spec['warps']]
    tk = cf.tile_grid(cf.classify(walk, set(steps) | set(spec.get('extra_floor', ()))))
    # the regenerated chunk models must equal the stored ones: the walk grid is then the one cave_floor.install used
    geo = {}
    for (cx, cz), (perm, blds, old_model, bdhc) in parts.items():
        kc = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items() if (OX + a) // CHUNK == cx and (OZ + b) // CHUNK == cz}
        full = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items()}
        quads = yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)
        if not any(quads.values()):
            continue
        for gx, gz, kind in spec.get('markers', ()):               # flat art an earlier patch already put on this chunk (Victory Road's switch pads and hole)
            if (gx // CHUNK, gz // CHUNK) == (cx, cz):
                for key, more in spec['marker_fn'](gx - cx * CHUNK, gz - cz * CHUNK, kind).items():
                    quads[key].extend(more)
        plain, _ = yellow_imd.convert(yellow_imd.imd_multi(textures, spec['mats'], quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f"{spec['name']}c{cx}{cz}")
        assert plain == old_model, (spec['name'], cx, cz, 'the regenerated chunk differs from the stored one')
        geo[(cx, cz)] = quads
    # blocks, old (two steps out) and new (next to the block) arrival tiles, exactly as cave_floor.install chose them
    blocks, all_block = [], set()
    for sx, sy in steps:
        b = {(sx * SCALE + dx, sy * SCALE + dz) for dx in range(SCALE) for dz in range(SCALE)}
        blocks.append(b)
        all_block |= b
    old_arrival, new_arrival = [], []
    for b in blocks:
        sides = sides_of(b, SCALE)
        open_sides = [k for k, cs in sides.items() if any(tk.get(c) == 'floor' and c not in all_block for c in cs)]
        beyond = adjacent = None
        for side in open_sides:
            u = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}[side]
            cands = [(c[0] + u[0], c[1] + u[1]) for c in sides[side]]
            cands = [c for c in cands if tk.get(c) == 'floor' and c not in all_block]
            if cands:
                beyond = cands[len(cands) // 2]
                near = [c for c in sides[side] if tk.get(c) == 'floor' and c not in all_block]
                adjacent = near[len(near) // 2]
                break
        if beyond is None:
            beyond = adjacent = min(b)
        old_arrival.append((OX + beyond[0], OZ + beyond[1]))
        new_arrival.append((OX + adjacent[0], OZ + adjacent[1]))
    # events: arrival entries first (index = warp number), then one entry per block tile
    eid = struct.unpack_from('<H', rec, 16)[0]
    g = events_decode(bytes(events.files[eid]))
    old = [struct.unpack_from('<4H', e, 0) for e in g[2]]
    assert [(a[0], a[1]) for a in old[:len(steps)]] == old_arrival, (spec['name'], old[:len(steps)], old_arrival)
    new = []
    for i, (ax, az) in enumerate(new_arrival):
        new.append(struct.pack('<4H', ax, az, mapid, i) + bytes(4))
    for (sx, sy, dmap, anchor, kind), b in zip(spec['warps'], blocks):
        for a, c in sorted(b):
            new.append(struct.pack('<4H', OX + a, OZ + c, dmap, anchor) + bytes(4))
    g[2] = new
    events.files[eid] = events_encode(g)
    # collision data: ring tiles back to plain floor, block tiles fire. The 110 tiles of the floor must be exactly the ring cave_floor.install made (nothing else on the floor uses 110).
    ring = set()
    for b in blocks:
        for side, cs in sides_of(b, SCALE).items():
            ring |= {c for c in cs if tk.get(c) == 'floor' and c not in all_block}
    found = {(a, c) for (a, c) in tk if parts[((OX + a) // CHUNK, (OZ + c) // CHUNK)][0][(((OZ + c) % CHUNK) * CHUNK + (OX + a) % CHUNK) * 2] == WARP_TILE}
    assert found == ring, (spec['name'], sorted(found ^ ring)[:8])
    for perm_parts in parts.values():
        perm = bytearray(perm_parts[0])
        for i in range(0, len(perm), 2):
            if perm[i] == WARP_TILE:
                perm[i:i + 2] = PLAIN
        perm_parts[0] = perm
    for b in blocks:
        for a, c in b:
            gx, gz = OX + a, OZ + c
            perm = parts[(gx // CHUNK, gz // CHUNK)][0]
            at = ((gz % CHUNK) * CHUNK + gx % CHUNK) * 2
            perm[at:at + 2] = bytes([WARP_TILE, 0])
    # ladders
    placed, touched = [], set()
    for (sx, sy, dmap, anchor, kind), b in zip(spec['warps'], blocks):
        if kind is None:
            continue
        gx0, gz0 = OX + min(a for a, _ in b), OZ + min(c for _, c in b)
        cx, cz = gx0 // CHUNK, gz0 // CHUNK
        assert (gx0 + 1) // CHUNK == cx and (gz0 + 1) // CHUNK == cz
        x, z = gx0 - cx * CHUNK + SCALE / 2 - CHUNK / 2, gz0 - cz * CHUNK + SCALE / 2 - CHUNK / 2
        parts[(cx, cz)][1] = bytes(parts[(cx, cz)][1]) + building(LADDER_DOWN if kind == 'down' else LADDER_UP, x, LADDER_Y, z)
        for key, quads in marker_quads(gx0 - cx * CHUNK, gz0 - cz * CHUNK, kind).items():
            geo[(cx, cz)].setdefault(key, []).extend(quads)
        touched.add((cx, cz))
        placed.append((kind, (gx0, gz0)))
    for cx, cz in touched:
        parts[(cx, cz)][2], _ = yellow_imd.convert(yellow_imd.imd_multi(textures, spec['mats'], geo[(cx, cz)], -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f"{spec['name']}c{cx}{cz}")
    for (cx, cz), (perm, blds, model, bdhc) in parts.items():
        lands.files[land_ids[cz * w + cx]] = pack(bytes(perm), bytes(blds), model, bdhc)
    rom.setFileByName('a/0/6/5', lands.save())
    rom.setFileByName('a/0/3/2', events.save())
    return dict(name=spec['name'], warps=len(steps), ladders=placed, arrivals=new_arrival, events=(len(old), len(new)))


# ---- second pass: art on the exits to the outside (found 2026-11-02: the owner could not see where to leave a cave either) ----
EXIT_KEY = 'exit_light'


def _exit_texture():
    """An 8x8 palette16 texture: a soft daylight glow, bright pale yellow in the middle and amber at the edge."""
    pixels = bytearray()
    for y in range(8):
        row = [3 - min(x, 7 - x, y, 7 - y) for x in range(8)]
        row = [3 - v for v in row]                                    # ring 3 (centre) -> palette 0 (brightest), ring 0 (edge) -> palette 3
        pixels += bytes(row[i] | row[i + 1] << 4 for i in range(0, 8, 2))
    return dict(name='ExitLight', fmt=3, w=8, h=8, pixels=bytes(pixels), palette=[(31, 31, 28), (31, 30, 20), (30, 27, 14), (26, 22, 10)])


def patch_exits(rom, spec):
    """Second pass on a floor already patched by patch_floor: a bright glowing pad on the 2x2 tiles of every exit to the outside (warps with kind None). The texture is added to the floor's area texture bank and only the
    chunks holding an exit are regenerated. Same spec as patch_floor (plus markers/marker_fn for Victory Road's switch art). Verifies that the stored chunk models and the stored texture bank are reproduced first."""
    OX, OZ = spec['OX'], spec['OZ']
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    rec = ext.records(rom)[spec['map'] - ext.NATIVE_COUNT]
    bank_id = struct.unpack_from('<H', areas.files[rec[1]], 2)[0]
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[spec['area']], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)

    def grab(tname, pname, new):
        t = tx[tname]
        return dict(name=new, fmt=int(t.format), w=t.width, h=t.height, pixels=bytes(t.data1), palette=[(c.r, c.g, c.b) for c in pl[pname].colors])
    textures = [grab(*s) for s in spec['tex']]
    mats = list(spec['mats'])
    yellow_3d.VISIBLE_DEPTH = 2
    mat = bytes(mats_n.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    land_ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    parts = {(i % w, i // w): list(parse(bytes(lands.files[lid]))) for i, lid in enumerate(land_ids)}
    walk = []
    for sy in range(spec['H'] * 2):
        walk.append([not parts[((OX + SCALE * sx) // CHUNK, (OZ + SCALE * sy) // CHUNK)][0][(((OZ + SCALE * sy) % CHUNK) * CHUNK + (OX + SCALE * sx) % CHUNK) * 2 + 1] & 0x80 for sx in range(spec['W'] * 2)])
    steps = [(x, y) for x, y, *_ in spec['warps']]
    tk = cf.tile_grid(cf.classify(walk, set(steps) | set(spec.get('extra_floor', ()))))
    ladders = [(OX + SCALE * sx, OZ + SCALE * sy, kind) for (sx, sy, _, _, kind) in spec['warps'] if kind is not None]
    exits = [(OX + SCALE * sx, OZ + SCALE * sy) for (sx, sy, _, _, kind) in spec['warps'] if kind is None]

    def stored_art(cx, cz, quads):
        for gx, gz, kind in spec.get('markers', ()):
            if (gx // CHUNK, gz // CHUNK) == (cx, cz):
                for key, more in spec['marker_fn'](gx - cx * CHUNK, gz - cz * CHUNK, kind).items():
                    quads[key].extend(more)
        for gx, gz, kind in ladders:
            if (gx // CHUNK, gz // CHUNK) == (cx, cz):
                for key, more in marker_quads(gx - cx * CHUNK, gz - cz * CHUNK, kind).items():
                    quads[key].extend(more)
        return quads

    def chunk_quads(cx, cz):
        kc = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items() if (OX + a) // CHUNK == cx and (OZ + b) // CHUNK == cz}
        full = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items()}
        return yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)

    def model(quads, cx, cz, texs, ms):
        return yellow_imd.convert(yellow_imd.imd_multi(texs, ms, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f"{spec['name']}c{cx}{cz}")[0]
    for (cx, cz), (perm, blds, old_model, bdhc) in parts.items():
        quads = chunk_quads(cx, cz)
        if any(quads.values()):
            assert model(stored_art(cx, cz, quads), cx, cz, textures, mats) == old_model, (spec['name'], cx, cz, 'the regenerated chunk differs from the stored one')
    dummy = {m[2]: [((0, 0, 0, 0, 0, 0, 1, 0), (0, 0, 0.01, 0, 1, 0, 1, 0), (0.01, 0, 0.01, 1, 1, 0, 1, 0), (0.01, 0, 0, 1, 0, 0, 1, 0))] for m in mats}

    def bank(texs, ms):
        return yellow_imd.convert(yellow_imd.imd_multi(texs, ms, {m[2]: dummy[m[2]] if m[2] in dummy else dummy[mats[0][2]] for m in ms}, -4.0, -4.0, 4.0, 4.0, 0.1), f"{spec['name']}tex")[1]
    assert bank(textures, mats) == bytes(banks.files[bank_id]), (spec['name'], 'the regenerated texture bank differs from the stored one')
    textures5, mats5 = textures + [_exit_texture()], mats + [('exit_light', len(textures), EXIT_KEY)]
    touched, drawn = {}, []
    for gx, gz in exits:
        cx, cz = gx // CHUNK, gz // CHUNK
        assert (gx + 1) // CHUNK == cx and (gz + 1) // CHUNK == cz
        assert all(tk.get((gx - OX + dx, gz - OZ + dz)) == 'floor' for dx in range(SCALE) for dz in range(SCALE)), (spec['name'], gx, gz)
        x0, z0 = -4.0 + (gx - cx * CHUNK) * TILE, -4.0 + (gz - cz * CHUNK) * TILE
        touched.setdefault((cx, cz), []).append(_quad(x0, z0, x0 + SCALE * TILE, z0 + SCALE * TILE, PAD_Y))
        drawn.append((gx, gz))
    dummy[EXIT_KEY] = dummy[mats[0][2]]
    for (cx, cz), pads in touched.items():
        quads = stored_art(cx, cz, chunk_quads(cx, cz))
        quads[EXIT_KEY] = pads
        parts[(cx, cz)][2] = model(quads, cx, cz, textures5, mats5)
        lands.files[land_ids[cz * w + cx]] = pack(bytes(parts[(cx, cz)][0]), bytes(parts[(cx, cz)][1]), parts[(cx, cz)][2], parts[(cx, cz)][3])
    banks.files[bank_id] = bank(textures5, mats5)
    rom.setFileByName('a/0/6/5', lands.save())
    rom.setFileByName('a/0/4/4', banks.save())
    return dict(name=spec['name'], exits=drawn, chunks=sorted(touched))
