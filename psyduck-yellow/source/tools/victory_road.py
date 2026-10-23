"""Victory Road (HG maps 124/178/179) gets Yellow's 11 trainers with their teams, moves and dialogue.

HG's cave has boulders and items but no trainers. Tiles come from tools/explore.py (data/vr*-tiles.json); trainers
are spread over each floor by distance from where the player arrives, off the main route and facing it.
Moltres, item balls and the boulder switches are deferred.
"""
import json
import struct
from pathlib import Path
import ndspy.narc
import map_header_extension as ext
import route_progression as rp
import tower_scenes as ts
import yellow_route_reference as yellow_ref
from opening import actor, events_decode, events_encode
from route6_trainers import patch as install_trainers
from rocket_hideout import bfs
from viridian_tutorial import TABLE

DATA = Path(__file__).resolve().parents[1] / 'data'
# HG map, Yellow floor, count, arrival tile (the part of each cave reachable on foot; the rest needs HMs)
FLOORS = ((124, 'VictoryRoad1F', 2, (46, 58)), (178, 'VictoryRoad2F', 5, (8, 31)), (179, 'VictoryRoad3F', 4, (38, 15)))
FACING = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3}
STEPS = ((0, -1), (0, 1), (-1, 0), (1, 0))


def place(tiles, route, taken, entry, count):
    on_route = set(route)
    dist, queue = {entry: 0}, [entry]
    for c in queue:
        for dx, dz in STEPS:
            n = (c[0] + dx, c[1] + dz)
            if n in tiles and n not in dist:
                dist[n] = dist[c] + 1
                queue.append(n)
    ring = sorted(dist, key=lambda p: (dist[p], p))
    spots = []
    for k in range(count):
        target = ring[(k + 1) * len(ring) // (count + 1)]
        for spacing, away, open_sides in ((3, 6, 3), (2, 4, 2), (2, 3, 1), (2, 1, 1)):
            free = [p for p in ring if p not in on_route and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= spacing for q in taken)
                    and abs(p[0] - entry[0]) + abs(p[1] - entry[1]) >= away
                    and sum((p[0] + dx, p[1] + dz) in tiles for dx, dz in STEPS) >= open_sides]
            if free:
                break
        p = min(free, key=lambda p: (abs(p[0] - target[0]) + abs(p[1] - target[1]), p))
        near = min(route, key=lambda q: abs(p[0] - q[0]) + abs(p[1] - q[1]))
        dx, dz = near[0] - p[0], near[1] - p[1]
        spots.append((p[0], p[1], (0 if dz < 0 else 1) if abs(dz) >= abs(dx) else (2 if dx < 0 else 3)))
        taken.add(p)
    return spots


def patch(rom, source):
    tables = rp.class_tables(rom)
    roles = {k: v for k, v in rp.OPP.items() if v in tables} | {'OPP_POKEMANIAC': 'Pokemaniac'}   # pokeyellow's class label is PokemaniacData
    refs = {name: yellow_ref.reference(source, name, count, extra_roles=roles, wild=False) for _, name, count, _ in FLOORS}
    installed = {}
    for _, name, count, _ in FLOORS:
        used = {e['role'] for e in refs[name]['trainers']}
        installed[name] = install_trainers(rom, refs[name], map_name=name, expected_count=count, templates={r: tables[r][0] for r in used})['trainers']
    last = max(b['id'] for name in installed for b in installed[name])
    ts._cover_common(rom, last)
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    report = {}
    for map_id, name, count, entry in FLOORS:
        tiles = {tuple(t) for f in DATA.glob(f'vr{map_id}-*.json') for t in json.loads(f.read_text())['tiles']}
        goal = max((t for t in tiles if abs(t[0] - entry[0]) + abs(t[1] - entry[1]) < 60), key=lambda t: (abs(t[0] - entry[0]) + abs(t[1] - entry[1]), t))
        route = bfs(entry, goal, tiles) if goal in tiles else [entry, goal]
        eid = struct.unpack_from('<H', ext.native_record(rom, map_id), 16)[0]
        g = events_decode(events.files[eid])
        taken = {struct.unpack_from('<2h', a, 24) for a in g[1]} | {entry, goal}
        spots = place(tiles, route, taken, entry, count)
        for (e, battle), (x, z, face) in zip(zip(refs[name]['trainers'], installed[name]), spots):
            a = bytearray(actor(max(struct.unpack_from('<H', o, 0)[0] for o in g[1]) + 1, tables[e['role']][1], 3000 + battle['id'] - 1, x, z, facing=face))
            struct.pack_into('<H', a, 6, 1)
            struct.pack_into('<H', a, 14, e['vision'])
            g[1].append(bytes(a))
        new = len(events.files)
        events.files.append(events_encode(g))
        struct.pack_into('<H', d, TABLE + map_id * 24 + 16, new)
        report[name] = dict(map=map_id, spots=spots, route=len(route))
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.arm9 = main.save(compress=True)
    return report
