"""Rock Tunnel (maps 558 1F, 559 B1F) and Victory Road (580 1F, 581 2F, 582 3F): the same warp fix as Mt. Moon (cave_ladders.py): only the 2x2 ladder block fires, ladder art on every floor-changing warp.
In Victory Road the ladders lead UP to the higher floors; in Rock Tunnel B1F is the lower floor. Usage: rock_vr_ladders.py <in.nds> <out.nds> <pokeyellow source> [rock|vr|all]"""
import sys
import ndspy.rom
import cave_ladders as cl
import mtmoon_yellow as my
import rocktunnel_yellow as rt
import victoryroad_yellow as vr
import vr_switch_plates as plates

ROCK_FIRST = 558
ROCK_ORDER = ['RockTunnel1F', 'RockTunnelB1F']
ROCK_YELLOW = dict(zip(('ROCK_TUNNEL_1F', 'ROCK_TUNNEL_B1F'), ROCK_ORDER))
VR_FIRST = 579                                                     # floor f is map 579 + f


def rock_specs(source):
    out = []
    for name, W, H, CX, CZ, OX, OZ in rt.FLOORS:
        here = ROCK_ORDER.index(name)
        warps = []
        for x, y, dest, wid in my.parse(source, name)['warps']:
            if dest == 'LAST_MAP':
                warps.append((x, y, rt.ROUTE10_NORTH if wid == 2 else rt.ROUTE10_SOUTH, 0, None))
            else:
                there = ROCK_ORDER.index(ROCK_YELLOW[dest])
                warps.append((x, y, ROCK_FIRST + there, wid - 1, 'down' if there > here else 'up'))
        out.append(dict(map=ROCK_FIRST + here, name=name, W=W, H=H, CX=CX, CZ=CZ, OX=OX, OZ=OZ, area=70, tex=my.TEX, mats=my.MATS, warps=warps))
    return out


def vr_specs(source):
    out = []
    floor_of = {'VICTORY_ROAD_1F': 1, 'VICTORY_ROAD_2F': 2, 'VICTORY_ROAD_3F': 3}
    for f, name in vr.NAMES.items():
        W, H = vr.BLOCKS[f]
        y = my.parse(source, name)
        warps = []
        for x, yy, dest, wid in y['warps']:
            if dest == 'LAST_MAP':
                warps.append((x, yy, vr.ROUTE23_GATE if f == 1 else vr.INDIGO, 1 if f == 1 else 0, None))
            else:
                warps.append((x, yy, VR_FIRST + floor_of[dest], wid - 1, 'up' if floor_of[dest] > f else 'down'))
        out.append(dict(map=VR_FIRST + f, name=name, W=W, H=H, CX=vr.CX, CZ=vr.CZ, OX=vr.OX, OZ=vr.OZ, area=vr.AREA, tex=vr.TEX, mats=vr.MATS, warps=warps, markers=plates.switch_tiles(f), marker_fn=plates.plate_quads,
                        extra_floor=[(o['x'], o['y']) for o in y['objs']]))
    return out


if __name__ == '__main__':
    which = sys.argv[4] if len(sys.argv) > 4 else 'all'
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    todo = (rock_specs(sys.argv[3]) if which in ('rock', 'all') else []) + (vr_specs(sys.argv[3]) if which in ('vr', 'all') else [])
    for spec in todo:
        print(cl.patch_floor(rom, spec))
    rom.saveToFile(sys.argv[2])
