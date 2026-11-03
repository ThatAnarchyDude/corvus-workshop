"""TEST ONLY: does each rebuilt floor's stored chunk model equal what cave_floor.install would regenerate from the floor's own collision data? (a mismatch = extra art or an edit a patch must reproduce)
Usage: floor_model_check.py <rom.nds> <pokeyellow source>   Prints one line per floor with the mismatching chunks."""
import struct
import sys
import ndspy.narc
import ndspy.rom
import ndspy.texture
import cave_floor as cf
import cave_ladders as cl
import hideout_yellow as hy
import map_header_extension as ext
import silph_yellow as sy
import yellow_3d
import yellow_imd


def floors():
    for f, name in hy.NAMES.items():
        yield 559 + f, name, hy.BLOCKS[f], hy.OX, hy.OZ, hy.CX, hy.CZ
    for f in range(1, 12):
        W, H = sy.BLOCKS[f]
        yield 563 + f, f'SilphCo{f}F', (W, H), (sy.CX * 32 - 4 * W) // 2, (sy.CZ * 32 - 4 * H) // 2, sy.CX, sy.CZ
    import mansion_yellow as my
    for f, name in my.NAMES.items():
        yield 574 + f, name, my.BLOCKS[f], hy.OX, hy.OZ, hy.CX, hy.CZ


def check(rom, mapid, name, blocks, OX, OZ, CX, CZ):
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4'))
    rec = ext.records(rom)[mapid - ext.NATIVE_COUNT]
    src = ndspy.texture.NSBTX(banks.files[struct.unpack_from('<H', areas.files[hy.AREA], 2)[0]])
    tx, pl = dict(src.textures), dict(src.palettes)
    textures = [dict(name=new, fmt=int(tx[t].format), w=tx[t].width, h=tx[t].height, pixels=bytes(tx[t].data1), palette=[(c.r, c.g, c.b) for c in pl[p].colors]) for t, p, new in hy.TEX]
    yellow_3d.VISIBLE_DEPTH = 2
    mat = bytes(mats_n.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    land_ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    parts = {(i % w, i // w): cl.parse(bytes(lands.files[lid])) for i, lid in enumerate(land_ids)}
    W, H = blocks
    walk = [[not parts[((OX + 2 * sx) // 32, (OZ + 2 * sy) // 32)][0][(((OZ + 2 * sy) % 32) * 32 + (OX + 2 * sx) % 32) * 2 + 1] & 0x80 for sx in range(W * 2)] for sy in range(H * 2)]
    tk = cf.tile_grid(cf.classify(walk, set()))
    bad, total = [], 0
    for (cx, cz), (perm, blds, old_model, bdhc) in parts.items():
        kc = {(OX + a - cx * 32, OZ + b - cz * 32): k for (a, b), k in tk.items() if (OX + a) // 32 == cx and (OZ + b) // 32 == cz}
        full = {(OX + a - cx * 32, OZ + b - cz * 32): k for (a, b), k in tk.items()}
        quads = yellow_3d.geometry_sloped(kc, full, -4.0, -4.0)
        if not any(quads.values()):
            continue
        total += 1
        new, _ = yellow_imd.convert(yellow_imd.imd_multi(textures, hy.MATS, quads, -4.0, -4.0, 4.0, 4.0, yellow_3d.WALL_H), f'{name}c{cx}{cz}')
        if new != old_model:
            bad.append((cx, cz))
    return total, bad


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    for mapid, name, blocks, OX, OZ, CX, CZ in floors():
        total, bad = check(rom, mapid, name, blocks, OX, OZ, CX, CZ)
        print(mapid, name, 'chunks', total, 'mismatch', bad, flush=True)
