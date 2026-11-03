"""Victory Road's boulder switches (and the 3F hole) get visible art (found 2026-10-28: cave_floor.py draws every switch as plain floor, so the puzzles cannot be solved by sight; they are optional shortcuts, the Indigo exit is reachable without them).

The three floors' chunk models are regenerated exactly as cave_floor.install builds them (the step kinds come back from the chunks' collision data; regenerating an untouched chunk reproduces the stored
model byte for byte) with a few extra flat quads on the chunks that hold a switch or the hole: a pale pad with a dark button on every switch (the 2x2 tiles the poll scripts watch) and a dark pit on 3F's hole.
Only the chunk land files that gain a quad are rewritten (model section; collision data and the rest are copied). Nothing else changes: the walk grid, scripts and actors are untouched.

Usage: vr_switch_plates.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import ndspy.texture
import cave_floor as cf
import map_header_extension as ext
import victoryroad_yellow as vr
import yellow_3d
import yellow_imd

CHUNK = cf.CHUNK
TILE = yellow_3d.TILE
PAD_Y, BUTTON_Y = 0.02, 0.035                  # pad and button sit just above the floor (y = 0)
FIRST_FLOOR_MAP = 579                          # floor f is map 579 + f


def _parse(land):
    perm_size, buildings, model_size, bdhc_size = struct.unpack_from('<4I', land, 0)
    assert land[16:20] == bytes.fromhex('34120000') and buildings == 0
    at = 20
    perm = land[at:at + perm_size]
    model = land[at + perm_size:at + perm_size + model_size]
    bdhc = land[at + perm_size + model_size:]
    assert len(bdhc) == bdhc_size
    return perm, model, bdhc


def _pack(perm, model, bdhc):
    return struct.pack('<4I', len(perm), 0, len(model), len(bdhc)) + bytes.fromhex('34120000') + perm + model + bdhc


def _quad(x0, z0, x1, z1, y):
    return ((x0, y, z0, 0, 0, 0, 1, 0), (x0, y, z1, 0, 1, 0, 1, 0), (x1, y, z1, 1, 1, 0, 1, 0), (x1, y, z0, 1, 0, 0, 1, 0))


def plate_quads(lx, lz, kind):
    """Extra quads for the 2x2-tile area whose local origin tile is (lx, lz) inside its chunk. 'switch': pale pad with a dark button; 'hole': dark pit."""
    x0, z0 = -4.0 + lx * TILE, -4.0 + lz * TILE
    x1, z1 = x0 + 2 * TILE, z0 + 2 * TILE
    if kind == 'switch':
        m, g = 0.06 * TILE, 0.5 * TILE
        return {'wall_top': [_quad(x0 + m, z0 + m, x1 - m, z1 - m, PAD_Y)], 'stone_top': [_quad(x0 + g, z0 + g, x1 - g, z1 - g, BUTTON_Y)]}
    m, g = 0.08 * TILE, 0.3 * TILE
    return {'stone_top': [_quad(x0 + m, z0 + m, x1 - m, z1 - m, PAD_Y)], 'wall_slope': [_quad(x0 + g, z0 + g, x1 - g, z1 - g, BUTTON_Y)]}


def switch_tiles(floor):
    """(tile x, tile z, kind) of every marker of a floor: the origin tile of each switch's 2x2 area, and 3F's hole."""
    out = [(vr.OX + cf.SCALE * sx, vr.OZ + cf.SCALE * sy, 'switch') for _, (sx, sy), _, _ in vr.SWITCHES.get(floor, [])]
    if floor == 3:
        out.append((vr.OX + cf.SCALE * vr.HOLE3[0], vr.OZ + cf.SCALE * vr.HOLE3[1], 'hole'))
    return out


def patch(rom, markers=None):
    """markers: {floor: [(tile x, tile z, kind)]}, default switch_tiles(). Returns a report."""
    markers = markers or {f: switch_tiles(f) for f in vr.NAMES}
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[vr.AREA], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)

    def grab(tname, pname, new):
        t = tx[tname]
        return dict(name=new, fmt=int(t.format), w=t.width, h=t.height, pixels=bytes(t.data1), palette=[(c.r, c.g, c.b) for c in pl[pname].colors])
    textures = [grab(*s) for s in vr.TEX]
    yellow_3d.VISIBLE_DEPTH = 2                                   # cave_floor.install's default, which Victory Road used
    records = ext.records(rom)
    report = {}
    for floor, name in vr.NAMES.items():
        rec = records[FIRST_FLOOR_MAP + floor - ext.NATIVE_COUNT]
        mat = bytes(mats_n.files[struct.unpack_from('<H', rec, 4)[0]])
        w, h, hd, ht, n = mat[:5]
        land_ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
        parts = {(i % w, i // w): _parse(bytes(lands.files[lid])) for i, lid in enumerate(land_ids)}
        W, H = vr.BLOCKS[floor]
        walk = []
        for sy in range(H * 2):
            row = []
            for sx in range(W * 2):
                gx, gz = vr.OX + cf.SCALE * sx, vr.OZ + cf.SCALE * sy
                perm = parts[(gx // CHUNK, gz // CHUNK)][0]
                row.append(not perm[((gz % CHUNK) * CHUNK + gx % CHUNK) * 2 + 1] & 0x80)
            walk.append(row)
        tk = cf.tile_grid(cf.classify(walk, set()))
        extra = {}
        for gx, gz, kind in markers.get(floor, []):
            cx, cz = gx // CHUNK, gz // CHUNK
            assert (gx + 1) // CHUNK == cx and (gz + 1) // CHUNK == cz, (floor, gx, gz)       # a marker never straddles a chunk
            assert all(tk.get((gx - vr.OX + dx, gz - vr.OZ + dz)) == 'floor' for dx in (0, 1) for dz in (0, 1)), (floor, gx, gz)
            for key, quads in plate_quads(gx - cx * CHUNK, gz - cz * CHUNK, kind).items():
                extra.setdefault((cx, cz), {}).setdefault(key, []).extend(quads)
        for (cx, cz), more in extra.items():
            kc = {(vr.OX + a - cx * CHUNK, vr.OZ + b - cz * CHUNK): k for (a, b), k in tk.items() if (vr.OX + a) // CHUNK == cx and (vr.OZ + b) // CHUNK == cz}
            full = {(vr.OX + a - cx * CHUNK, vr.OZ + b - cz * CHUNK): k for (a, b), k in tk.items()}
            quads = yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)
            perm, old_model, bdhc = parts[(cx, cz)]
            plain, _ = yellow_imd.convert(yellow_imd.imd_multi(textures, vr.MATS, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f'{name}c{cx}{cz}')
            assert plain == old_model, (floor, cx, cz, 'the regenerated chunk differs from the stored one')
            for key, qs in more.items():
                quads[key].extend(qs)
            model, _ = yellow_imd.convert(yellow_imd.imd_multi(textures, vr.MATS, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f'{name}c{cx}{cz}')
            lands.files[land_ids[cz * w + cx]] = _pack(perm, model, bdhc)
            report.setdefault(floor, []).append(dict(chunk=(cx, cz), quads_added=sum(len(v) for v in more.values()), model_bytes=(len(old_model), len(model))))
    rom.setFileByName('a/0/6/5', lands.save())
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
