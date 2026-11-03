"""Mt. Moon's ladders (maps 555 1F, 556 B1F, 557 B2F): visible ladder art on every floor-changing warp, and only the 2x2 ladder block fires the warp (see cave_ladders.py).
Owner report 2026-11-02: most Mt. Moon warps were invisible and fired over several tiles, so the cave was very hard to get through. Yellow's warp list comes from pret/pokeyellow like mtmoon_yellow.py.
Usage: mtmoon_ladders.py <in.nds> <out.nds> <pokeyellow source>"""
import sys
import ndspy.rom
import cave_ladders as cl
import mtmoon_yellow as my

FIRST_MAP = 555
ORDER = ['MtMoon1F', 'MtMoonB1F', 'MtMoonB2F']
YELLOW_NAME = dict(zip(('MT_MOON_1F', 'MT_MOON_B1F', 'MT_MOON_B2F'), ORDER))


def specs(source):
    out = []
    for name, W, H, CX, CZ, OX, OZ in my.FLOORS:
        here = ORDER.index(name)
        warps = []
        for x, y, dest, wid in my.parse(source, name)['warps']:
            if dest == 'LAST_MAP':
                warps.append((x, y, my.ROUTE3 if name == 'MtMoon1F' else my.ROUTE4, 0, None))
            else:
                there = ORDER.index(YELLOW_NAME[dest])
                warps.append((x, y, FIRST_MAP + there, wid - 1, 'down' if there > here else 'up'))
        out.append(dict(map=FIRST_MAP + here, name=name, W=W, H=H, CX=CX, CZ=CZ, OX=OX, OZ=OZ, area=70, tex=my.TEX, mats=my.MATS, warps=warps))
    return out


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    for spec in specs(sys.argv[3]):
        print(cl.patch_floor(rom, spec))
    rom.saveToFile(sys.argv[2])
