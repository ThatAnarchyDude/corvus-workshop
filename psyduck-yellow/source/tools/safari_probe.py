"""TEST ONLY: install Yellow's Safari Zone Center with Kanto-outdoor textures as ext map and print its id. argv: in out source"""
import sys
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
from mtmoon_yellow import parse
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); src = sys.argv[3]
FOREST_COLL = {0x1E, 0x20, 0x2E, 0x30, 0x34, 0x37, 0x39, 0x3A, 0x40, 0x51, 0x52, 0x5A, 0x5C, 0x5E, 0x5F}
TEX = [('grass02', 'grass02_pl', 'SafFloor'), ('wall01_g', 'wall01_g', 'SafWall'), ('tree01_un', 'tree01_un', 'SafTop'), ('road01_sub', 'road01_sub_pl', 'SafRock')]
MATS = [('floor', 0, 'floor'), ('wall_top', 2, 'wall_top'), ('wall_slope', 1, 'wall_slope'), ('stone_top', 3, 'stone_top'), ('stone_side', 3, 'stone_side')]
y = parse(src, 'SafariZoneCenter')
mid = ext.install(rom, [ext.native_record(rom, 124)])[0]
rep = cf.install(rom, src, 'SafariZoneCenter', mid, 15, 13, [(w[0], w[1]) for w in y['warps']], 8, 12, 3, 3, 15, TEX, MATS, None, tileset='forest', coll=FOREST_COLL, extra_floor=[(o['x'], o['y']) for o in y['objs']])
rom.saveToFile(sys.argv[2])
print(mid, rep['quads_per_chunk'], cf.STATE['SafariZoneCenter']['arrival'][0])
