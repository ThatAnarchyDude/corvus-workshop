"""Warp markers for the rebuilt facility floors: Rocket Hideout (maps 560-563), Silph Co. (564-574), Pokemon Mansion (575-578). Found 2026-11-02: like the caves, every warp there was a plain, unmarked floor block
ringed by firing tiles, so stairs, teleport pads and elevator doors were invisible (the owner: "it was very difficult to get through Mt. Moon when I could not tell where the warp tiles were").
Per floor this (1) makes only the 2x2 block fire (behaviour 110 + one warp event per block tile; the ring goes back to plain floor), (2) moves each arrival next to its block, (3) draws a flat marker on the block:
 up stairs = blue pad with a white up arrow, down stairs = orange pad with a down arrow, Silph teleport pad = cyan/magenta rings, elevator doors = the Celadon department store's own 'ele_ent' elevator panel texture,
 exits to the outside = the glowing yellow pad of cave_ladders.patch_exits.
Destinations are read from the floor's own ring warp events (nothing is recomputed from Yellow except where each block stands and what kind it is). Hideout elevator doors on B1F/B2F are triggers (Lift Key check): the
trigger moves from the ring onto the block. The stored chunk models and texture bank are regenerated and compared first, so the patch only runs on a floor it reproduces byte for byte.
Usage: facility_markers.py <in.nds> <out.nds> <pokeyellow source> [hideout|silph|mansion|all]"""
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
import ndspy.texture
import cave_floor as cf
import cave_ladders as cl
import hideout_yellow as hy
import map_header_extension as ext
import mansion_yellow as mansion
import silph_yellow as silph
import yellow_3d
import yellow_imd
from mtmoon_yellow import parse
from opening import events_decode, events_encode

SCALE, CHUNK = cf.SCALE, cf.CHUNK
CELADON_AREA = 39                                              # the Celadon / Silph template area: its bank holds 'ele_ent'
ELEV_TRIGGER_VAR = hy.ELEV_VAR


def _pack4(grid):
    return bytes(grid[y][x] | grid[y][x + 1] << 4 for y in range(16) for x in range(0, 16, 2))


def _arrow(name, palette, up):
    grid = [[1] * 16 for _ in range(16)]
    for i in range(16):
        for x, y in ((i, 0), (i, 15), (0, i), (15, i)):
            grid[y][x] = 0
        for x, y in ((i, 1), (i, 14), (1, i), (14, i)):
            if grid[y][x] == 1:
                grid[y][x] = 3
    rows = [(r, 7 - (r - 3), 8 + (r - 3)) for r in range(3, 9)] + [(r, 6, 9) for r in range(9, 13)]
    for r, lo, hi in rows:
        for x in range(lo, hi + 1):
            grid[r if up else 15 - r][x] = 2
    return dict(name=name, fmt=3, w=16, h=16, pixels=_pack4(grid), palette=palette)


def _rings():
    ring_color = [3, 3, 3, 1, 2, 0, 1, 0]
    grid = [[ring_color[int(max(abs(x - 7.5), abs(y - 7.5)))] for x in range(16)] for y in range(16)]
    return dict(name='WarpPad', fmt=3, w=16, h=16, pixels=_pack4(grid), palette=[(6, 2, 12), (22, 6, 28), (14, 28, 31), (31, 31, 31)])


def marker_textures(rom):
    """The extra textures every patched floor's bank gets, in a fixed order: [StairUp, StairDown, WarpPad, ElevEnt, ExitLight]."""
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[CELADON_AREA], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)
    e = tx['ele_ent']
    elevator = dict(name='ElevEnt', fmt=int(e.format), w=e.width, h=e.height, pixels=bytes(e.data1), palette=[(c.r, c.g, c.b) for c in pl['ele_ent_pl'].colors])
    return [_arrow('StairUp', [(2, 4, 12), (8, 16, 31), (31, 31, 31), (4, 9, 22)], True), _arrow('StairDown', [(14, 5, 0), (31, 19, 3), (31, 31, 31), (23, 11, 1)], False), _rings(), elevator, cl._exit_texture()]


KIND_TEXTURE = {'up': 0, 'down': 1, 'pad': 2, 'elevator': 3, 'exit': 4}


def patch_floor(rom, spec, extras):
    """spec: dict(map, name, W, H, CX, CZ, OX, OZ, area, tex, mats, warps=[(step x, step y, kind)]) in the floor's warp-arrival order; kind in up/down/pad/elevator/exit."""
    mapid, OX, OZ = spec['map'], spec['OX'], spec['OZ']
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    rec = ext.records(rom)[mapid - ext.NATIVE_COUNT]
    bank_id = struct.unpack_from('<H', areas.files[rec[1]], 2)[0]
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[spec['area']], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)
    textures = [dict(name=new, fmt=int(tx[t].format), w=tx[t].width, h=tx[t].height, pixels=bytes(tx[t].data1), palette=[(c.r, c.g, c.b) for c in pl[p].colors]) for t, p, new in spec['tex']]
    mats = list(spec['mats'])
    yellow_3d.VISIBLE_DEPTH = 2
    mat = bytes(mats_n.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    land_ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    parts = {(i % w, i // w): list(cl.parse(bytes(lands.files[lid]))) for i, lid in enumerate(land_ids)}
    walk = [[not parts[((OX + SCALE * sx) // CHUNK, (OZ + SCALE * sy) // CHUNK)][0][(((OZ + SCALE * sy) % CHUNK) * CHUNK + (OX + SCALE * sx) % CHUNK) * 2 + 1] & 0x80 for sx in range(spec['W'] * 2)] for sy in range(spec['H'] * 2)]
    steps = [(x, y) for x, y, _ in spec['warps']]
    tk = cf.tile_grid(cf.classify(walk, set()))

    def chunk_quads(cx, cz):
        kc = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items() if (OX + a) // CHUNK == cx and (OZ + b) // CHUNK == cz}
        full = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items()}
        return yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)

    def model(quads, cx, cz, texs, ms):
        return yellow_imd.convert(yellow_imd.imd_multi(texs, ms, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f"{spec['name']}c{cx}{cz}")[0]
    for (cx, cz), (perm, blds, old_model, bdhc) in parts.items():
        quads = chunk_quads(cx, cz)
        if any(quads.values()):
            assert model(quads, cx, cz, textures, mats) == old_model, (spec['name'], cx, cz, 'the regenerated chunk differs from the stored one')
    dummy = {m[2]: [((0, 0, 0, 0, 0, 0, 1, 0), (0, 0, 0.01, 0, 1, 0, 1, 0), (0.01, 0, 0.01, 1, 1, 0, 1, 0), (0.01, 0, 0, 1, 0, 0, 1, 0))] for m in mats}

    def bank(texs, ms):
        return yellow_imd.convert(yellow_imd.imd_multi(texs, ms, {m[2]: dummy[mats[0][2]] for m in ms}, -4.0, -4.0, 4.0, 4.0, 0.1), f"{spec['name']}tex")[1]
    assert bank(textures, mats) == bytes(banks.files[bank_id]), (spec['name'], 'the regenerated texture bank differs from the stored one')
    # blocks and the old ring, exactly as cave_floor.install made them (first warp to claim a tile owns it)
    blocks, all_block = [], set()
    for sx, sy in steps:
        b = {(sx * SCALE + dx, sy * SCALE + dz) for dx in range(SCALE) for dz in range(SCALE)}
        blocks.append(b)
        all_block |= b
    claimed, owner, old_arrival, new_arrival = set(), {}, [], []
    for wi, b in enumerate(blocks):
        sides = cl.sides_of(b, SCALE)
        open_sides = [k for k, cs in sides.items() if any(tk.get(c) == 'floor' and c not in all_block for c in cs)]
        claimed |= b
        beyond = adjacent = None
        for side in open_sides:
            u = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}[side]
            cands = [c for c in ((c[0] + u[0], c[1] + u[1]) for c in sides[side]) if tk.get(c) == 'floor' and c not in all_block]
            if cands:
                beyond = cands[len(cands) // 2]
                near = [c for c in sides[side] if tk.get(c) == 'floor' and c not in all_block]
                adjacent = near[len(near) // 2]
                break
        if beyond is None:
            beyond = adjacent = min(b)
        old_arrival.append((OX + beyond[0], OZ + beyond[1]))
        new_arrival.append((OX + adjacent[0], OZ + adjacent[1]))
        for side in open_sides:
            for c in sides[side]:
                if tk.get(c) == 'floor' and c not in all_block and c not in claimed:
                    claimed.add(c)
                    owner[c] = wi
    found = {(a, c) for (a, c) in tk if parts[((OX + a) // CHUNK, (OZ + c) // CHUNK)][0][(((OZ + c) % CHUNK) * CHUNK + (OX + a) % CHUNK) * 2] == cl.WARP_TILE}
    assert found == set(owner), (spec['name'], sorted(found ^ set(owner))[:8])
    # the floor's events: arrivals, then ring warps; triggers on ring tiles (Hideout lift doors)
    eid = struct.unpack_from('<H', rec, 16)[0]
    g = events_decode(bytes(events.files[eid]))
    old = [struct.unpack_from('<4H', e, 0) for e in g[2]]
    nwarps = len(steps)
    assert [(a[0], a[1]) for a in old[:nwarps]] == old_arrival, (spec['name'], old[:nwarps], old_arrival)
    dest = {}
    for ax, az, dmap, anchor in old[nwarps:]:
        tile = (ax - OX, az - OZ)
        assert tile in owner, (spec['name'], 'ring warp off the ring', tile)
        wi = owner[tile]
        assert dest.setdefault(wi, (dmap, anchor)) == (dmap, anchor), (spec['name'], 'one warp, two destinations', wi)
    for wi, forced in spec.get('dest_override', {}).items():      # a warp with no open side has no ring event (Silph 10F's walled-in pad): the block itself becomes the way out
        assert wi not in dest, (spec['name'], wi, 'already has a destination')
        dest[wi] = forced
    triggers, moved = [], {}
    for t in g[3]:
        script, tx_, tz_, tw, th = struct.unpack_from('<Hhh2H', t, 0)
        tile = (tx_ - OX, tz_ - OZ)
        if tile in owner and (tw, th) == (1, 1):
            assert owner[tile] not in dest, (spec['name'], 'trigger and warp on the same ring', tile)
            moved.setdefault(owner[tile], []).append(bytes(t))
        else:
            triggers.append(bytes(t))
    for wi, ts in moved.items():
        for t in (ts[0],):
            for a, c in sorted(blocks[wi]):
                triggers.append(struct.pack('<Hhh', *struct.unpack_from('<Hhh', t, 0)[:1], OX + a, OZ + c) + t[6:])
    new = [struct.pack('<4H', ax, az, mapid, i) + bytes(4) for i, (ax, az) in enumerate(new_arrival)]
    for wi, b in enumerate(blocks):
        if wi in dest:
            for a, c in sorted(b):
                new.append(struct.pack('<4H', OX + a, OZ + c, *dest[wi]) + bytes(4))
    g[2], g[3] = new, triggers
    events.files[eid] = events_encode(g)
    # collision data: ring back to plain floor, blocks with a destination fire
    for ps in parts.values():
        perm = bytearray(ps[0])
        for i in range(0, len(perm), 2):
            if perm[i] == cl.WARP_TILE:
                perm[i:i + 2] = cl.PLAIN
        ps[0] = perm
    for wi, b in enumerate(blocks):
        if wi in dest:
            for a, c in b:
                gx, gz = OX + a, OZ + c
                at = ((gz % CHUNK) * CHUNK + gx % CHUNK) * 2
                parts[(gx // CHUNK, gz // CHUNK)][0][at:at + 2] = bytes([cl.WARP_TILE, 0])
    # markers
    used = sorted({k for _, _, k in spec['warps'] if k})
    textures_all = textures + extras
    mats_all = mats + [(f'm_{k}', len(textures) + KIND_TEXTURE[k], f'm_{k}') for k in KIND_TEXTURE]
    touched = {}
    for (sx, sy, kind), b in zip(spec['warps'], blocks):
        if not kind:
            continue
        gx, gz = OX + min(a for a, _ in b), OZ + min(c for _, c in b)
        cx, cz = gx // CHUNK, gz // CHUNK
        assert (gx + 1) // CHUNK == cx and (gz + 1) // CHUNK == cz and all(tk.get(t) == 'floor' for t in b), (spec['name'], gx, gz)
        x0, z0 = -4.0 + (gx - cx * CHUNK) * cl.TILE, -4.0 + (gz - cz * CHUNK) * cl.TILE
        touched.setdefault((cx, cz), {}).setdefault(f'm_{kind}', []).append(cl._quad(x0, z0, x0 + SCALE * cl.TILE, z0 + SCALE * cl.TILE, cl.PAD_Y))
    for (cx, cz), art in touched.items():
        quads = chunk_quads(cx, cz)
        quads.update(art)
        parts[(cx, cz)][2] = model(quads, cx, cz, textures_all, mats_all)
    for (cx, cz), (perm, blds, mdl, bdhc) in parts.items():
        lands.files[land_ids[cz * w + cx]] = cl.pack(bytes(perm), bytes(blds), mdl, bdhc)
    dummy.update({m[2]: dummy[mats[0][2]] for m in mats_all})
    banks.files[bank_id] = bank(textures_all, mats_all)
    rom.setFileByName('a/0/6/5', lands.save())
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/4/4', banks.save())
    return dict(name=spec['name'], warps=nwarps, kinds=[k for _, _, k in spec['warps']], dest_missing=[wi for wi in range(nwarps) if wi not in dest], triggers_moved=sorted(moved))


def _floor_no(text):
    m = re.search(r'(B?)(\d+)F$', text)
    return -int(m.group(2)) if m.group(1) else int(m.group(2))


def hideout_specs(source):
    out = []
    for f, name in hy.NAMES.items():
        warps = []
        for x, y, dest, wid in parse(source, name)['warps']:
            if dest == 'GAME_CORNER':
                kind = 'up'
            elif dest == 'ROCKET_HIDEOUT_ELEVATOR':
                kind = 'elevator'
            else:
                kind = 'down' if int(re.search(r'B(\d)F', dest).group(1)) > f else 'up'
            warps.append((x, y, kind))
        out.append(dict(map=559 + f, name=name, W=hy.BLOCKS[f][0], H=hy.BLOCKS[f][1], OX=hy.OX, OZ=hy.OZ, area=hy.AREA, tex=hy.TEX, mats=hy.MATS, warps=warps))
    return out


def silph_specs(source):
    out = []
    for f in range(1, 12):
        name = f'SilphCo{f}F'
        W, H = silph.BLOCKS[f]
        warps = []
        for i, (x, y, dest, wid) in enumerate(silph.parse(source, f)['warps']):
            if dest == 'SILPH_CO_ELEVATOR' or (f == 1 and i == 4):
                continue                                           # not built (silph_yellow.py: no elevator, 1F's fifth warp is inaccessible)
            if dest == 'LAST_MAP':
                kind = 'exit'
            elif y == 0 and abs(int(re.search(r'(\d+)F', dest).group(1)) - f) == 1:
                kind = 'up' if int(re.search(r'(\d+)F', dest).group(1)) > f else 'down'
            else:
                kind = 'pad'
            warps.append((x, y, kind))
        out.append(dict(map=563 + f, name=name, W=W, H=H, OX=(silph.CX * 32 - 4 * W) // 2, OZ=(silph.CZ * 32 - 4 * H) // 2, area=hy.AREA, tex=hy.TEX, mats=hy.MATS, warps=warps))
    # Yellow's 10F pad (9, 11) is walled in on all four sides (found 2026-11-02 by the other session: the player could only shuffle inside the block). Its block fires: back to the 4F pad that sent the player there.
    kept = {f: [i + 1 for i, (_, _, dest, _) in enumerate(silph.parse(source, f)['warps']) if dest != 'SILPH_CO_ELEVATOR' and not (f == 1 and i == 4)] for f in range(1, 12)}
    ten = out[9]
    index = next(i for i, (x, y, _) in enumerate(ten['warps']) if (x, y) == (9, 11))
    ten['dest_override'] = {index: (563 + 4, kept[4].index(4))}
    return out


def mansion_specs(source):
    out = []
    for f, name in mansion.NAMES.items():
        here = _floor_no(name)
        warps = []
        for x, y, dest, wid in parse(source, name)['warps']:
            if dest == 'LAST_MAP':
                kind = 'exit'
            else:
                kind = 'up' if _floor_no(dest.replace('POKEMON_MANSION_', '')) > here else 'down'
            warps.append((x, y, kind))
        out.append(dict(map=574 + f, name=name, W=mansion.BLOCKS[f][0], H=mansion.BLOCKS[f][1], OX=hy.OX, OZ=hy.OZ, area=hy.AREA, tex=hy.TEX, mats=hy.MATS, warps=warps))
    return out


if __name__ == '__main__':
    which = sys.argv[4] if len(sys.argv) > 4 else 'all'
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    extras = marker_textures(rom)
    todo = (hideout_specs(sys.argv[3]) if which in ('hideout', 'all') else []) + (silph_specs(sys.argv[3]) if which in ('silph', 'all') else []) + (mansion_specs(sys.argv[3]) if which in ('mansion', 'all') else [])
    for spec in todo:
        print(patch_floor(rom, spec, extras), flush=True)
    rom.saveToFile(sys.argv[2])
