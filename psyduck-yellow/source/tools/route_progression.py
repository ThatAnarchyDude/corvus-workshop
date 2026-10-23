"""Yellow's trainers and wild tables on HeartGold's existing Kanto routes (any route, data-driven).

Generalises route9_progression: Yellow's trainers (teams, moves, dialogue) are installed with route6_trainers.patch; native
trainer actors are replaced - the first ones reuse the native tiles, the rest are spread over reachable ground by
farthest-point sampling - and the route's grass table becomes Yellow's. Roles map to the HG trainer class whose record is the
template and whose overworld sprite is the one native trainers of that class use (both read from the ROM).
Terrain, items, signs and warps are untouched.
"""
import re
import struct
from collections import Counter, deque, defaultdict
from pathlib import Path
import ndspy.narc
from opening import actor, events_decode, events_encode
from route6_trainers import patch as install_trainers
from forest_progression import SLOT_MAP
from viridian_tutorial import TABLE
import yellow_route_reference as yellow_ref

FACING = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3}
# Yellow role -> HG trainer class id (see the class-name bank 730)
ROLE_CLASS = {'Youngster': 2, 'Lass': 3, 'JrTrainerM': 4, 'JrTrainerF': 5, 'BugCatcher': 6, 'Hiker': 9, 'Fisher': 11,
              'Gambler': 20, 'Engineer': 113, 'SuperNerd': 78, 'Rocker': 52, 'Beauty': 36, 'Biker': 65, 'BirdKeeper': 69,
              'CueBall': 14, 'Sailor': 46, 'Juggler': 31, 'Tamer': 14, 'Burglar': 63, 'Psychic': 49, 'Scientist': 113,
              'CooltrainerM': 24, 'CooltrainerF': 25, 'PokeManiac': 68, 'Pokemaniac': 68, 'Blackbelt': 14, 'Swimmer': 42,
              'Channeler': 82}
OPP = {'OPP_' + re.sub(r'(?<!^)(?=[A-Z])', '_', r).upper(): r for r in ROLE_CLASS}
OPP.update({'OPP_JR_TRAINER_M': 'JrTrainerM', 'OPP_JR_TRAINER_F': 'JrTrainerF', 'OPP_COOLTRAINER_M': 'CooltrainerM',
            'OPP_COOLTRAINER_F': 'CooltrainerF', 'OPP_CUE_BALL': 'CueBall', 'OPP_BIRD_KEEPER': 'BirdKeeper',
            'OPP_SUPER_NERD': 'SuperNerd', 'OPP_BUG_CATCHER': 'BugCatcher', 'OPP_POKEMANIAC': 'PokeManiac', 'OPP_BLACKBELT': 'Blackbelt'})
LEDGES = ((1, 0, 56), (-1, 0, 57), (0, -1, 58), (0, 1, 59))


def class_tables(rom):
    """role -> (template trainer id, overworld sprite id), read from the native trainers and their actors."""
    trainers = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/5/5')])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    sprites = defaultdict(Counter)
    for raw in events.files:
        try:
            groups = events_decode(raw)
        except Exception:
            continue
        for a in groups[1]:
            u = struct.unpack('<6Hh5h2Hi', a)
            if 3000 <= u[5] < 4000 and u[5] - 2999 < len(trainers.files):
                sprites[trainers.files[u[5] - 2999][1]][u[1]] += 1
    out = {}
    for role, cls in ROLE_CLASS.items():
        template = next(t for t in range(len(trainers.files)) if trainers.files[t][1] == cls and trainers.files[t][3] <= 3)
        out[role] = (template, sprites[cls].most_common(1)[0][0])
    return out


def yellow_count(source, name):
    scripts = (Path(source) / 'scripts' / (name + '.asm')).read_text()
    return len(re.findall(r'^\s*trainer EVENT_BEAT_\w+,', scripts, re.M))


def terrain(rom, rec_bytes):
    matrices = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')])
    lands = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
    matrix = matrices.files[struct.unpack_from('<H', rec_bytes, 4)[0]]
    w, h, headers, heights, n = matrix[:5]
    off = 5 + n + w * h * (2 * headers + heights)

    def permission(x, z):
        cx, cz = x // 32, z // 32
        if not (0 <= cx < w and 0 <= cz < h):
            return 0x8000
        land = lands.files[struct.unpack_from('<H', matrix, off + 2 * (cz * w + cx))[0]]
        start = 20 if struct.unpack_from('<H', land, 16)[0] == 0x1234 else 16
        return struct.unpack_from('<H', land, start + 2 * (z % 32 * 32 + x % 32))[0]

    def floor(p):
        v = permission(*p)
        return not v & 0x8000 and (v & 255) not in (16, 17, 19, 21) and not 56 <= (v & 255) <= 59

    return permission, floor


def reachable_from(start, floor, permission, window):
    x0, z0, x1, z1 = window

    def inside(p):
        return x0 <= p[0] <= x1 and z0 <= p[1] <= z1

    seen, queue = {start}, deque([start])
    while queue:
        p = queue.popleft()
        for dx, dz, ledge in LEDGES:
            q = (p[0] + dx, p[1] + dz)
            nxt = []
            if inside(q) and floor(q):
                nxt.append(q)
            elif inside(q) and permission(*q) & 255 == ledge:
                r = (q[0] + dx, q[1] + dz)
                if inside(r) and floor(r):
                    nxt.append(r)
            for n in nxt:
                if n not in seen:
                    seen.add(n)
                    queue.append(n)
    return seen


def spread(candidates, occupied, count):
    """Farthest-point sampling over candidate tiles, keeping clear of what is already placed."""
    chosen, taken = [], set(occupied)
    pool = sorted(candidates)
    for _ in range(count):
        best = max(pool, key=lambda p: (min([abs(p[0] - q[0]) + abs(p[1] - q[1]) for q in taken] or [99]), p))
        assert min([abs(best[0] - q[0]) + abs(best[1] - q[1]) for q in taken] or [99]) >= 3, 'no safe trainer tile left'
        chosen.append(best)
        taken.add(best)
    return chosen


def patch(rom, source, route, extra_items=None):
    """Convert HG Route `route` (map 8+route) to Yellow's Route{route}."""
    name, map_id = f'Route{route}', 8 + route
    tables = class_tables(rom)
    count = yellow_count(source, name)
    roles = {k: v for k, v in OPP.items() if v in tables}
    reference = yellow_ref.reference(source, name, count, extra_roles=roles, wild=True)
    used = {e['role'] for e in reference['trainers']}
    report = install_trainers(rom, reference, map_name=name, expected_count=count, templates={r: tables[r][0] for r in used})
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    rec = TABLE + map_id * 24
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    wild = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/7')])
    eid = struct.unpack_from('<H', d, rec + 16)[0]
    groups = events_decode(events.files[eid])
    native = [a for a in groups[1] if 3000 <= struct.unpack_from('<H', a, 10)[0] < 6000]
    others = [a for a in groups[1] if a not in native]
    anchors = [struct.unpack_from('<2H', a, 24) for a in groups[1]] + [struct.unpack_from('<2H', w, 0) for w in groups[2]]
    window = (min(p[0] for p in anchors) - 10, min(p[1] for p in anchors) - 10, max(p[0] for p in anchors) + 10, max(p[1] for p in anchors) + 10)
    permission, floor = terrain(rom, bytes(d[rec:rec + 24]))
    start = next((tuple(struct.unpack_from('<2H', a, 24)) for a in native if floor(struct.unpack_from('<2H', a, 24))),
                 next(p for p in ((x, z) for x, z in anchors) if floor(p)))
    ground = reachable_from(start, floor, permission, window)
    positions = [tuple(struct.unpack_from('<2H', a, 24)) for a in native][:count]
    occupied = set(positions) | {tuple(struct.unpack_from('<2H', a, 24)) for a in others} | {tuple(p) for p in anchors}
    open4 = lambda p: sum(floor((p[0] + dx, p[1] + dz)) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    candidates = [p for p in ground if open4(p) >= 3 and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 3 for q in occupied)]
    positions += spread(candidates, occupied, count - len(positions))
    taken = {struct.unpack_from('<H', a)[0] for a in others}      # native NPC ids stay as they are
    free = (i for i in range(256) if i not in taken)
    actors = []
    for entry, battle, p in zip(reference['trainers'], report['trainers'], positions):
        a = bytearray(actor(next(free), tables[entry['role']][1], 3000 + battle['id'] - 1, *p, facing=FACING[entry['facing']]))
        struct.pack_into('<H', a, 6, 1)
        struct.pack_into('<H', a, 14, entry['vision'])
        actors.append(bytes(a))
    groups[1] = actors + others
    ne = len(events.files)
    events.files.append(events_encode(groups))
    struct.pack_into('<H', d, rec + 16, ne)
    wid = None
    if d[rec] != 255 and reference['grass']:
        raw = bytearray(wild.files[d[rec]])
        assert len(raw) == 196
        raw[0] = reference['grass_rate']
        raw[1:6] = bytes(5)
        slots = [reference['grass'][i] for i in SLOT_MAP]
        raw[8:20] = bytes(s['level'] for s in slots)
        for period in range(3):
            struct.pack_into('<12H', raw, 20 + 24 * period, *(s['species'] for s in slots))
        wid = len(wild.files)
        assert wid < 255
        wild.files.append(bytes(raw))
        d[rec] = wid
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.files[rom.filenames.idOf('a/0/3/7')] = wild.save()
    rom.arm9 = main.save(compress=True)
    return dict(route=route, map=map_id, trainers=count, native_replaced=len(native), positions=positions, wild=wid, event=ne)
