"""Yellow Pokemon Tower on seven cloned Bell Tower floors (map IDs from the header extension).

Floors 1F-7F clone native Bell Tower maps 332-338 into extension IDs. Yellow trainers, wild
tables and stairs are fitted into the native layouts; the Lavender Radio Tower front door (map 439) leads
here until the Hall of Fame (flag 0x964), then behaves natively again.
"""
import struct
from collections import deque
import ndspy.narc
from opening import Script, actor, events_decode, events_encode
from parcel_quest import append_bank
from viridian_tutorial import TABLE
from forest_progression import SLOT_MAP
from route6_trainers import patch as install_trainers
import map_header_extension as ext

SOURCES = (332, 333, 334, 335, 336, 337, 338)          # Tower 1F..7F
LAVENDER, TOWER_DOOR_ANCHOR, TOWER_DOOR_HOUSE = 53, 6, 439
BELL_TOWER_OUTSIDE = 111
GAME_CLEAR = 0x964
STATE = 0x4000
TEMPLATES = {'Channeler': 46}
SPRITES = {'Channeler': 219}
FACING = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3}
TRAINER_FLOORS = {3: 'PokemonTower3F', 4: 'PokemonTower4F', 5: 'PokemonTower5F', 6: 'PokemonTower6F'}
TRAINER_COUNTS = {3: 3, 4: 3, 5: 4, 6: 3}


def _land(rom, map_id, d):
    rec = TABLE + map_id * 24
    mats = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')])
    lands = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
    mat = mats.files[struct.unpack_from('<H', d, rec + 4)[0]]
    w, h, headers, heights, n = mat[:5]
    assert (w, h) == (1, 1)
    off = 5 + n + w * h * (2 * headers + heights)
    lid = struct.unpack_from('<H', mat, off)[0]
    land = lands.files[lid]
    floor = set()
    for y in range(32):
        for x in range(32):
            v = struct.unpack_from('<H', land, 16 + 2 * (y * 32 + x))[0]
            if not v & 0x8000 and v & 255 not in (16, 17, 19, 21):
                floor.add((x, y))
    return floor


def _reachable(floor, starts, blocked):
    seen = {p for p in starts if p in floor}
    q = deque(seen)
    while q:
        x, y = q.popleft()
        for p in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if p in floor and p not in blocked and p not in seen:
                seen.add(p)
                q.append(p)
    return seen


def _largest_component(floor):
    best, left = set(), set(floor)
    while left:
        start = min(left)
        comp = _reachable(floor, {start}, set())
        left -= comp
        if len(comp) > len(best):
            best = comp
    return best


def _frame_entry(header, var, value, script):
    """Prepend one (var, value, script) row to a level-script header's frame table."""
    i = 0
    while header[i] != 0:
        i += 5
    has_table = any(header[j] == 1 for j in range(0, i, 5))
    table = bytearray(header[i + 1:])
    row = struct.pack('<3H', var, value, script)
    if has_table:
        return bytes(header[:i + 1]) + row + bytes(table)
    return bytes(header[:i]) + struct.pack('<BI', 1, 1) + b'\0' + row + b'\0\0'


def entrance_script(arrival, map_id):
    x, y, facing = arrival
    s = Script().emit(41, STATE, 1).emit(32, GAME_CLEAR).jump('native', 1)
    s.emit(96).emit(174, 6, 6, 0, 0).emit(175).emit(176, map_id, 0, x, y, facing)
    s.emit(174, 6, 6, 1, 0).emit(175).emit(97).emit(2)
    s.label('native').emit(2)
    return s.finish()


def patch(rom, references):
    """references: {floor: Yellow reference dict} for floors 3-6."""
    base = ext.NATIVE_COUNT + len(ext.records(rom))
    ids = {f: base + i for i, f in enumerate(range(1, 8))}
    remap = {src: ids[f] for f, src in zip(range(1, 8), SOURCES)}
    reports = {}
    trainer_reports = {}
    for f, name in TRAINER_FLOORS.items():
        trainer_reports[f] = install_trainers(rom, references[f], map_name=name, expected_count=TRAINER_COUNTS[f], templates=TEMPLATES)
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    wild = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/7')])
    records = []
    arrival = None
    for f, src in zip(range(1, 8), SOURCES):
        rec = bytearray(ext.native_record(rom, src))
        old_event = struct.unpack_from('<H', rec, 16)[0]
        g = events_decode(events.files[old_event])
        raw_warps = list(g[2])
        warps = [struct.unpack_from('<HHHHH', w) for w in raw_warps]
        down = next((i for i, w in enumerate(warps) if w[2] == SOURCES[f - 2]), 0) if f > 1 else 0
        new_warps = []
        for (x, y, dest, anchor, pad), raw in zip(warps, raw_warps):
            if f == 1 and dest == BELL_TOWER_OUTSIDE:
                new = (x, y, LAVENDER, TOWER_DOOR_ANCHOR, pad)
            elif dest in remap:
                new = (x, y, remap[dest], anchor, pad)
            else:
                new = (x, y, remap[src], down, pad)      # unused upper stairs: back to this floor's down stairs
            new_warps.append(struct.pack('<4H', *new[:4]) + raw[8:])
        g[2] = new_warps
        g[0] = []
        others = []
        floor = _land(rom, src, d)
        occupied = {(w[0], w[1]) for w in warps}
        seeds = {(x + dx, y + dy) for x, y in occupied for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))}
        accessible = _reachable(floor, seeds, set())
        if len(accessible) < 60:
            accessible = _largest_component(floor)
        positions = []
        if f in references:
            ref, train = references[f], trainer_reports[f]
            for entry, battle in zip(ref['trainers'], train['trainers']):
                desired = (entry['yellow_position'][0] + 5, entry['yellow_position'][1] + 6)
                cands = sorted((p for p in accessible - occupied
                                if sum((p[0] + dx, p[1] + dy) in floor for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3
                                and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 4 for q in occupied)),
                               key=lambda p: (abs(p[0] - desired[0]) + abs(p[1] - desired[1]), p))
                p = next(c for c in cands)
                occupied.add(p)
                positions.append(p)
                a = bytearray(actor(len(others), SPRITES[entry['role']], 3000 + battle['id'] - 1, *p, facing=FACING[entry['facing']]))
                struct.pack_into('<H', a, 6, 1)
                struct.pack_into('<H', a, 14, entry['vision'])
                others.append(bytes(a))
        g[1] = others
        eid = len(events.files)
        events.files.append(events_encode(g))
        struct.pack_into('<H', rec, 16, eid)
        if f in references:
            ref = references[f]
            row = bytearray(wild.files[rec[0]])
            assert len(row) == 196
            row[:6] = bytes([ref['grass_rate'], 0, 0, 0, 0, 0])
            slots = [ref['grass'][i] for i in SLOT_MAP]
            row[8:20] = bytes(p['level'] for p in slots)
            for period in range(3):
                struct.pack_into('<12H', row, 20 + 24 * period, *(p['species'] for p in slots))
            for at in (0x5C, 0x60, 0x64, 0x68, 0xBC):
                struct.pack_into('<2H', row, at, slots[0]['species'], slots[1]['species'])
            wid = len(wild.files)
            assert wid < 255
            wild.files.append(bytes(row))
            rec[0] = wid
        else:
            rec[0] = 255
        records.append(bytes(rec))
        if f == 1:
            e = next(i for i, w in enumerate(warps) if w[2] == BELL_TOWER_OUTSIDE)
            door = warps[e][:2]
            near = sorted(p for p in floor if abs(p[0] - door[0]) + abs(p[1] - door[1]) == 1 and p in accessible)
            arrival = (near[0][0], near[0][1], 0)
        reports[f] = dict(map=ids[f], source=src, event=eid, positions=positions)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.files[rom.filenames.idOf('a/0/3/7')] = wild.save()
    rom.arm9 = main.save(compress=True)
    got = ext.install(rom, records)
    assert got == [ids[f] for f in range(1, 8)]
    # Lavender Radio Tower (439): until the Hall of Fame its door leads to Tower 1F (frame script on the interior).
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    at = TABLE + TOWER_DOOR_HOUSE * 24
    old_bank, old_header = struct.unpack_from('<2H', d, at + 6)
    bank, count = append_bank(scripts.files[old_bank], [entrance_script(arrival, ids[1])])
    scripts.files[old_bank] = bytes(bank)
    scripts.files[old_header] = _frame_entry(scripts.files[old_header], STATE, 0, count + 1)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.arm9 = main.save(compress=True)
    return dict(floors=reports, arrival=arrival, lavender_gate_script=count + 1, trainers={f: t['trainers'] for f, t in trainer_reports.items()})
