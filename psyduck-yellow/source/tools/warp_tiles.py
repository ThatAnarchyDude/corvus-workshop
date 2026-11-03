"""Warp tiles of every rebuilt cave and facility floor, in ONE pass over a ROM that still has cave_floor.py's original ring warps (ROM 0145). Supersedes cave_ladders.patch_floor / patch_exits and facility_markers.patch_floor
(their separate passes are kept only as history). Owner rules (2026-11-02): warps must be visible, and a teleport pad, ladder, staircase or lift door is triggered by exactly ONE tile; of an "up" ladder (which may look two
tiles high) only the lower tile fires. Exits to the outside keep their full-width mat (a doorway is wide).
Per warp (Yellow's 2x2 block of tiles):
 - the FIRING tile is the block's bottom-left tile: behaviour 110 and one warp event; the other three tiles are plain floor; the arrival tile is next to it (south, else west, else a neighbouring block tile: a walled-in pad
   such as Silph 10F's now has its way out by stepping onto the firing tile);
 - exits (kind 'exit'): every block tile fires and glows (the glowing yellow pad), arrival next to the block as before;
 - art, centred on the firing tile: caves: native ladder model (building 69 up / 70 down) with a dark pit (down) or pale pad (up) from the cave's own materials; facility floors: flat pads (blue up arrow, orange down arrow,
   cyan teleport rings, the Celadon department store's 'ele_ent' panel for elevator doors).
Destinations are read from the floor's own ring warp events, so nothing is recomputed from Yellow except where each block stands and what kind it is. Hideout B1F/B2F lift doors are triggers (Lift Key check): the trigger
moves from the ring onto the firing tile. Before anything is changed, the stored chunk models and texture bank of the floor are regenerated and compared (the floor must be reproduced byte for byte).
Usage: warp_tiles.py <in.nds> <out.nds> <pokeyellow source> [caves|facilities|all]"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import ndspy.texture
import cave_floor as cf
import cave_ladders as cl
import facility_markers as fm
import map_header_extension as ext
import mtmoon_ladders as moon
import rock_vr_ladders as rv
import vr_switch_plates as plates
import yellow_3d
import yellow_imd
from opening import events_decode, events_encode

SCALE, CHUNK, TILE = cf.SCALE, cf.CHUNK, cl.TILE
PIT_AREA = 70


def _cave_marker(x0, z0, kind):
    """One-tile art under a ladder, from the cave's own materials: a dark pit (down) or a pale pad (up). (x0, z0) = the tile's local corner in model units."""
    x1, z1 = x0 + TILE, z0 + TILE
    if kind == 'down':
        m, g = 0.08 * TILE, 0.25 * TILE
        return {'stone_top': [cl._quad(x0 + m, z0 + m, x1 - m, z1 - m, cl.PAD_Y)], 'wall_slope': [cl._quad(x0 + g, z0 + g, x1 - g, z1 - g, cl.PIT_Y)]}
    m = 0.06 * TILE
    return {'wall_top': [cl._quad(x0 + m, z0 + m, x1 - m, z1 - m, cl.PAD_Y)]}


def cave_specs(source):
    out = []
    for spec in moon.specs(source) + rv.rock_specs(source) + rv.vr_specs(source):
        s = dict(spec, style='cave', warps=[(x, y, kind or 'exit') for x, y, _, _, kind in spec['warps']],
                 dest_fallback={i: (dmap, anchor) for i, (_, _, dmap, anchor, _) in enumerate(spec['warps'])})      # for a walled-in block with no ring (Rock Tunnel 1F's south exit): the builder's own destination
        if 'marker_fn' in spec:
            s['markers'], s['marker_fn'] = spec['markers'], spec['marker_fn']
        out.append(s)
    return out


def facility_specs(source):
    return [dict(s, style='facility') for s in fm.hideout_specs(source) + fm.silph_specs(source) + fm.mansion_specs(source)]


def patch_floor(rom, spec, extras):
    mapid, OX, OZ, style = spec['map'], spec['OX'], spec['OZ'], spec['style']
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    sets = ndspy.narc.NARC(rom.getFileByName('a/0/4/3'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    rec = ext.records(rom)[mapid - ext.NATIVE_COUNT]
    bank_id = struct.unpack_from('<H', areas.files[rec[1]], 2)[0]
    if style == 'cave':
        sid = struct.unpack_from('<H', areas.files[rec[1]], 0)[0]
        building_set = struct.unpack('<%dH' % (len(sets.files[sid]) // 2), bytes(sets.files[sid]))
        assert cl.LADDER_UP in building_set and cl.LADDER_DOWN in building_set, (spec['name'], building_set)
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
    tk = cf.tile_grid(cf.classify(walk, set()))
    plate_art = [(gx, gz, kind) for gx, gz, kind in spec.get('markers', ())]

    def chunk_quads(cx, cz):
        kc = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items() if (OX + a) // CHUNK == cx and (OZ + b) // CHUNK == cz}
        full = {(OX + a - cx * CHUNK, OZ + b - cz * CHUNK): k for (a, b), k in tk.items()}
        quads = yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)
        for gx, gz, kind in plate_art:                              # Victory Road's switch pads and hole (ROM 0109) are part of the stored model
            if (gx // CHUNK, gz // CHUNK) == (cx, cz) and any(quads.values()):
                for key, more in spec['marker_fn'](gx - cx * CHUNK, gz - cz * CHUNK, kind).items():
                    quads[key].extend(more)
        return quads

    def model(quads, cx, cz, texs, ms):
        return yellow_imd.convert(yellow_imd.imd_multi(texs, ms, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f"{spec['name']}c{cx}{cz}")[0]
    for (cx, cz), (perm, blds, old_model, bdhc) in parts.items():
        quads = chunk_quads(cx, cz)
        if any(quads.values()):
            assert model(quads, cx, cz, textures, mats) == old_model, (spec['name'], cx, cz, 'the regenerated chunk differs from the stored one')
    dummy = [((0, 0, 0, 0, 0, 0, 1, 0), (0, 0, 0.01, 0, 1, 0, 1, 0), (0.01, 0, 0.01, 1, 1, 0, 1, 0), (0.01, 0, 0, 1, 0, 0, 1, 0))]

    def bank(texs, ms):
        return yellow_imd.convert(yellow_imd.imd_multi(texs, ms, {m[2]: dummy for m in ms}, -4.0, -4.0, 4.0, 4.0, 0.1), f"{spec['name']}tex")[1]
    assert bank(textures, mats) == bytes(banks.files[bank_id]), (spec['name'], 'the regenerated texture bank differs from the stored one')
    # blocks, the old ring and arrivals (exactly as cave_floor.install made them), then the new firing tiles and arrivals
    kinds = [k for _, _, k in spec['warps']]
    blocks, all_block = [], set()
    for sx, sy, _ in spec['warps']:
        b = {(sx * SCALE + dx, sy * SCALE + dz) for dx in range(SCALE) for dz in range(SCALE)}
        blocks.append(b)
        all_block |= b
    claimed, owner, old_arrival, new_arrival, fire = set(), {}, [], [], []
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
        for side in open_sides:
            for c in sides[side]:
                if tk.get(c) == 'floor' and c not in all_block and c not in claimed:
                    claimed.add(c)
                    owner[c] = wi
        if kinds[wi] == 'exit':
            fire.append(sorted(b))
            new_arrival.append((OX + adjacent[0], OZ + adjacent[1]))
        else:
            x_lo, z_hi = min(t[0] for t in b), max(t[1] for t in b)
            fire.append([(x_lo, z_hi)])
            options = [(x_lo, z_hi + 1), (x_lo - 1, z_hi), (x_lo + 1, z_hi), (x_lo, z_hi - 1)]
            arrival = next(c for c in options if tk.get(c) == 'floor' and (c not in all_block or c in b))
            new_arrival.append((OX + arrival[0], OZ + arrival[1]))
    found = {(a, c) for (a, c) in tk if parts[((OX + a) // CHUNK, (OZ + c) // CHUNK)][0][(((OZ + c) % CHUNK) * CHUNK + (OX + a) % CHUNK) * 2] == cl.WARP_TILE}
    assert found == set(owner), (spec['name'], sorted(found ^ set(owner))[:8])
    # events: destinations from the ring warps, triggers on the ring (Hideout lift doors) move onto the firing tile
    eid = struct.unpack_from('<H', rec, 16)[0]
    g = events_decode(bytes(events.files[eid]))
    old = [struct.unpack_from('<4H', e, 0) for e in g[2]]
    nwarps = len(blocks)
    assert [(a[0], a[1]) for a in old[:nwarps]] == old_arrival, (spec['name'], old[:nwarps], old_arrival)
    dest = {}
    for ax, az, dmap, anchor in old[nwarps:]:
        tile = (ax - OX, az - OZ)
        assert tile in owner, (spec['name'], 'ring warp off the ring', tile)
        assert dest.setdefault(owner[tile], (dmap, anchor)) == (dmap, anchor), (spec['name'], 'one warp, two destinations', owner[tile])
    for wi, forced in spec.get('dest_override', {}).items():
        assert wi not in dest, (spec['name'], wi, 'already has a destination')
        dest[wi] = forced
    for wi, fallback in spec.get('dest_fallback', {}).items():
        dest.setdefault(wi, fallback)
    triggers, moved = [], {}
    for t in g[3]:
        tile = (struct.unpack_from('<h', t, 2)[0] - OX, struct.unpack_from('<h', t, 4)[0] - OZ)
        if tile in owner and struct.unpack_from('<2H', t, 6) == (1, 1):
            assert owner[tile] not in dest, (spec['name'], 'trigger and warp on the same ring', tile)
            moved.setdefault(owner[tile], bytes(t))
        else:
            triggers.append(bytes(t))
    for wi, t in moved.items():
        for a, c in fire[wi]:
            triggers.append(struct.pack('<Hhh', struct.unpack_from('<H', t, 0)[0], OX + a, OZ + c) + t[6:])
    new = [struct.pack('<4H', ax, az, mapid, i) + bytes(4) for i, (ax, az) in enumerate(new_arrival)]
    for wi in range(nwarps):
        if wi in dest:
            for a, c in fire[wi]:
                new.append(struct.pack('<4H', OX + a, OZ + c, *dest[wi]) + bytes(4))
    g[2], g[3] = new, triggers
    events.files[eid] = events_encode(g)
    # collision data: the ring back to plain floor, firing tiles of warps with a destination get behaviour 110
    for ps in parts.values():
        perm = bytearray(ps[0])
        for i in range(0, len(perm), 2):
            if perm[i] == cl.WARP_TILE:
                perm[i:i + 2] = cl.PLAIN
        ps[0] = perm
    for wi in range(nwarps):
        if wi in dest:
            for a, c in fire[wi]:
                gx, gz = OX + a, OZ + c
                at = ((gz % CHUNK) * CHUNK + gx % CHUNK) * 2
                parts[(gx // CHUNK, gz // CHUNK)][0][at:at + 2] = bytes([cl.WARP_TILE, 0])
    # art
    textures_all = textures + extras
    mats_all = mats + [(f'm_{k}', len(textures) + fm.KIND_TEXTURE[k], f'm_{k}') for k in fm.KIND_TEXTURE]
    art, placed = {}, []
    for wi, (sx, sy, kind) in enumerate(spec['warps']):
        for a, c in fire[wi]:
            gx, gz = OX + a, OZ + c
            cx, cz = gx // CHUNK, gz // CHUNK
            assert tk.get((a, c)) == 'floor', (spec['name'], gx, gz)
            x0, z0 = -4.0 + (gx - cx * CHUNK) * TILE, -4.0 + (gz - cz * CHUNK) * TILE
            quads = art.setdefault((cx, cz), {})
            if kind == 'exit':
                quads.setdefault('m_exit', []).append(cl._quad(x0, z0, x0 + TILE, z0 + TILE, cl.PAD_Y))
            elif style == 'cave':
                for key, more in _cave_marker(x0, z0, kind).items():
                    quads.setdefault(key, []).extend(more)
                parts[(cx, cz)][1] = bytes(parts[(cx, cz)][1]) + cl.building(cl.LADDER_DOWN if kind == 'down' else cl.LADDER_UP, gx - cx * CHUNK + 0.5 - CHUNK / 2, cl.LADDER_Y, gz - cz * CHUNK + 0.5 - CHUNK / 2)
                placed.append((kind, (gx, gz)))
            else:
                quads.setdefault(f'm_{kind}', []).append(cl._quad(x0, z0, x0 + TILE, z0 + TILE, cl.PAD_Y))
                placed.append((kind, (gx, gz)))
    for (cx, cz), more in art.items():
        quads = chunk_quads(cx, cz)
        for key, qs in more.items():
            quads.setdefault(key, []).extend(qs)
        parts[(cx, cz)][2] = model(quads, cx, cz, textures_all, mats_all)
    for (cx, cz), (perm, blds, mdl, bdhc) in parts.items():
        lands.files[land_ids[cz * w + cx]] = cl.pack(bytes(perm), bytes(blds), mdl, bdhc)
    banks.files[bank_id] = bank(textures_all, mats_all)
    rom.setFileByName('a/0/6/5', lands.save())
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/4/4', banks.save())
    return dict(name=spec['name'], warps=nwarps, fire=[len(f) for f in fire], no_destination=[wi for wi in range(nwarps) if wi not in dest], triggers_moved=sorted(moved), art=len(placed))


if __name__ == '__main__':
    which = sys.argv[4] if len(sys.argv) > 4 else 'all'
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    extras = fm.marker_textures(rom)
    todo = (cave_specs(sys.argv[3]) if which in ('caves', 'all') else []) + (facility_specs(sys.argv[3]) if which in ('facilities', 'all') else [])
    for spec in todo:
        print(patch_floor(rom, spec, extras), flush=True)
    rom.saveToFile(sys.argv[2])
