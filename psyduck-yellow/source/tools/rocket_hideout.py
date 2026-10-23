"""Rocket Hideout under the Celadon Game Corner.

Four clones of Rocket HQ's first floor (map 247, whose walkable tiles were measured with tools/explore.py and
live in data/hq247-tiles.json) stand in for Yellow's B1F-B4F. Yellow's trainers, Jessie & James and Giovanni
are placed along the stairs-to-stairs route; Giovanni hands over the Silph Scope. The Lift Key, elevator and item
balls are deferred. A Rocket in the Game Corner (map 381) opens the way once beaten.
"""
import json
import struct
from collections import deque
from pathlib import Path
import ndspy.narc
import map_header_extension as ext
import tower_scenes as ts
import yellow_route_reference as yellow_ref
from opening import Script, actor, events_decode, events_encode, encode_text, end
from parcel_quest import PH
from prototype import decode_messages
from route6_trainers import patch as install_trainers
from viridian_tutorial import TABLE
import yellow_text

HQ_MAP, GAME_CORNER = 247, 381
FLOORS = ('RocketHideoutB1F', 'RocketHideoutB2F', 'RocketHideoutB3F', 'RocketHideoutB4F')
COUNTS = {1: 5, 2: 1, 3: 2, 4: 1}
FIRST_INDEX = {4: 2}                           # B4F's only header is "TRAINER_2" in pokeyellow
ROCKET_TEMPLATE, ROCKET_SPRITE = 12, 222
GIOVANNI_TEMPLATE, GIOVANNI_SPRITE = 700, 385  # Rocket Boss class record; 385 is the boss sprite HQ uses
UP_ARRIVAL, DOWN_ARRIVAL = (51, 5), (10, 28)  # tiles beside the HQ clone's two stairs
FACING = {(0, -1): 0, (0, 1): 1, (-1, 0): 2, (1, 0): 3}
HQ_OPEN, JJ_HIDE, GIOVANNI_HIDE = 0xA70, 0xA71, 0xA6D
JJ_STATE = 0x4174
SILPH_SCOPE = 874
GUARD = (11, 12, 0)                            # Game Corner: Rocket beside the entrance corridor (x, z, facing up)
TILES = {tuple(t) for t in json.loads((Path(__file__).resolve().parents[1] / 'data/hq247-tiles.json').read_text())['tiles']}


def bfs(a, b, tiles=TILES):
    prev, q = {a: None}, deque([a])
    while q:
        c = q.popleft()
        if c == b:
            path = []
            while c:
                path.append(c)
                c = prev[c]
            return path[::-1]
        for dx, dz in FACING:
            n = (c[0] + dx, c[1] + dz)
            if n in tiles and n not in prev:
                prev[n] = c
                q.append(n)
    raise ValueError('stairs are not connected')


def side_spots(path, taken, count):
    """Tiles beside the route (never on it), spread along it, each facing a route tile."""
    on_path, spots = set(path), []
    for k in range(count):
        want = (k + 1) * len(path) // (count + 1)
        for shift in range(len(path)):
            for idx in (want + shift, want - shift):
                if not 3 <= idx < len(path) - 3:
                    continue
                for (dx, dz), face in FACING.items():
                    p = (path[idx][0] - dx, path[idx][1] - dz)      # stand one step away from the route, look back at it
                    if p in TILES and p not in on_path and p not in taken and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) > 1 for q in taken):
                        spots.append((p[0], p[1], face))
                        taken.add(p)
                        break
                else:
                    continue
                break
            else:
                continue
            break
    assert len(spots) == count
    return spots


def cluster(path, taken, count):
    """`count` neighbouring tiles off the route near its far end (Giovanni and the two ambushers)."""
    on_path = set(path)
    centre = path[len(path) * 85 // 100]
    near = sorted((p for p in TILES if p not in on_path and p not in taken and abs(p[0] - centre[0]) + abs(p[1] - centre[1]) <= 4
                   and sum((p[0] + dx, p[1] + dz) in on_path for dx, dz in FACING) >= 1),
                  key=lambda p: (abs(p[0] - centre[0]) + abs(p[1] - centre[1]), p))
    spots = []
    for p in near:
        if len(spots) == count:
            break
        if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) <= 3 for q in spots):
            face = next(f for (dx, dz), f in FACING.items() if (p[0] + dx, p[1] + dz) in on_path)
            spots.append((p[0], p[1], face))
            taken.add(p)
    assert len(spots) == count
    return spots


def hq_record(rom, eid_old, scripts_header):
    rec = bytearray(ext.native_record(rom, HQ_MAP))
    rec[0] = 255                                  # no wild encounters
    struct.pack_into('<H', rec, 8, scripts_header)
    return rec


def patch(rom, source):
    yellow = ts.Yellow(source)
    refs = {f: yellow_ref.reference(source, name, COUNTS[f], extra_roles={'OPP_ROCKET': 'Rocket'}, wild=False,
                                    first_index=FIRST_INDEX.get(f, 0)) for f, name in enumerate(FLOORS, 1)}
    trainer_reports = {f: install_trainers(rom, refs[f], map_name=FLOORS[f - 1], expected_count=COUNTS[f],
                                           templates={'Rocket': ROCKET_TEMPLATE}) for f in refs}
    book = ts.TrainerBook(rom)
    book.assert_unused((HQ_OPEN, JJ_HIDE, GIOVANNI_HIDE, JJ_STATE))
    t = yellow_text.message
    b4 = 'RocketHideoutB4F'
    giovanni_text = [t(source, b4, f'_RocketHideoutB4FGiovanni{x}Text') for x in ('ImpressedYouGotHere', 'WhatCannotBe', 'HopeWeMeetAgain')]
    team = yellow.leader_party('GiovanniData')
    giovanni = book.new(GIOVANNI_TEMPLATE, b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in team),
                        giovanni_text, decode_messages(encode_text(['GIOVANNI'], PH))[1][0], len(team))
    jj_team = yellow.rocket_by_comment('Rocket Hideout B4F')
    jj_text = [t(source, b4, f'_RocketHideoutJessieJamesText{i}') for i in (2, 3, 4)]
    assert book.trainers.files[777][1] == 129
    jj = book.new(777, b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in jj_team),
                  jj_text, book.names[777], len(jj_team))
    guard_team = yellow.class_party('RocketData', 7)
    guard_text = [t(source, 'GameCorner', f'_GameCornerRocket{x}Text') for x in ('ImGuardingThisPoster', 'BattleEnd', 'AfterBattle')]
    guard = book.new(ROCKET_TEMPLATE, b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in guard_team),
                     guard_text, book.names[ROCKET_TEMPLATE], len(guard_team))
    book.save()
    ts._cover_common(rom, guard)

    base = ext.NATIVE_COUNT + len(ext.records(rom))
    ids = {f: base + f - 1 for f in range(1, 5)}
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    scripts.files.append(b'\0')                    # empty level-script header: the clones keep none of HQ's story scripts
    header = len(scripts.files) - 1
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    native = events_decode(events.files[struct.unpack_from('<H', ext.native_record(rom, HQ_MAP), 16)[0]])
    route = bfs(UP_ARRIVAL, DOWN_ARRIVAL)
    records, report, extras = [], {}, {}
    for f in range(1, 5):
        rec = hq_record(rom, None, header)
        g = [[], [], [], []]
        raw = native[2]
        up = (GAME_CORNER, 0) if f == 1 else (ids[f - 1], 1)
        down = (ids[f + 1], 0) if f < 4 else (ids[f], 0)
        for w, (dest, anchor) in zip(raw, (up, down)):
            x, y = struct.unpack_from('<2H', w)
            g[2].append(struct.pack('<4H', x, y, dest, anchor) + w[8:])
        taken = {UP_ARRIVAL, DOWN_ARRIVAL}
        spots = side_spots(route, taken, COUNTS[f])
        if f == 4:
            spots += cluster(route, taken, 3)         # Giovanni and the two ambushers
        for obj, (entry, battle) in enumerate(zip(refs[f]['trainers'], trainer_reports[f]['trainers'])):
            x, z, face = spots[obj]
            a = bytearray(actor(obj, ROCKET_SPRITE, 3000 + battle['id'] - 1, x, z, facing=face))
            struct.pack_into('<H', a, 6, 1)
            struct.pack_into('<H', a, 14, entry['vision'])
            g[1].append(bytes(a))
        report[f] = dict(map=ids[f], trainers=[(spots[i][0], spots[i][1]) for i in range(COUNTS[f])])
        if f == 4:
            extras = ts_floor4(rom, rec, g, spots[COUNTS[f]:], giovanni, jj, source)
            report[f].update(extras)
        eid = len(events.files)
        events.files.append(events_encode(g))
        struct.pack_into('<H', rec, 16, eid)
        records.append(bytes(rec))
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    assert ext.install(rom, records) == [ids[f] for f in range(1, 5)]
    report['game_corner'] = game_corner(rom, guard, ids[1], source)
    return dict(floors=report, giovanni=giovanni, jessie_james=jj, guard=guard, route_length=len(route))


def ts_floor4(rom, rec, g, spots, giovanni, jj, source):
    """B4F: Jessie & James stand by Giovanni and ambush whoever walks up; then Giovanni gives the Silph Scope."""
    t = yellow_text.message
    m = lambda l: t(source, 'RocketHideoutB4F', l)
    lines = [m('_RocketHideoutJessieJamesText1').rstrip('@'), m('_RocketHideoutJessieJamesText2'), m('_RocketHideoutJessieJamesText3'),
             m('_RocketHideoutJessieJamesText4').rstrip('@'),
             m('_RocketHideoutB4FGiovanniImpressedYouGotHereText'), m('_RocketHideoutB4FGiovanniWhatCannotBeText'),
             m('_RocketHideoutB4FGiovanniHopeWeMeetAgainText'), 'GIOVANNI left the SILPH SCOPE behind!']
    (gx, gz, gf), (jx, jz, jf), (kx, kz, kf) = spots
    scene = Script().emit(96)
    ts.music(scene, 1112).msg(0).msg(1)
    scene.emit(213, jj, 0)
    scene.data.extend(bytes(2))
    scene.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    scene.emit(36, jj)
    ts.music(scene, 1112).msg(2).msg(3)
    scene.emit(30, JJ_HIDE).emit(101, 1).emit(101, 2).emit(41, JJ_STATE, 1).emit(81, 0).emit(82)
    end(scene)
    scene.label('lost').emit(219)
    end(scene)
    stand = Script().emit(96).emit(104).msg(0).emit(97).emit(2).finish()
    boss = Script().emit(96).emit(104).emit(32, GIOVANNI_HIDE).jump('gone', 1)
    boss.msg(4)
    boss.emit(213, giovanni, 0)
    boss.data.extend(bytes(2))
    boss.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    boss.emit(36, giovanni).msg(6)
    boss.emit(125, SILPH_SCOPE, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    boss.emit(30, GIOVANNI_HIDE).emit(101, 0).msg(7)
    end(boss)
    boss.label('full').msg(7)
    end(boss)
    boss.label('gone').msg(6)
    end(boss)
    boss.label('lost').emit(219)
    end(boss)
    entry = ts._attach(rom, rec, lines, [scene.finish(), stand, boss.finish()])
    obj = len(g[1])
    g[1].extend([actor(obj, GIOVANNI_SPRITE, entry + 2, gx, gz, GIOVANNI_HIDE, gf),
                 actor(obj + 1, ts.JESSIE_SPRITE, entry + 1, jx, jz, JJ_HIDE, jf), actor(obj + 2, ts.JAMES_SPRITE, entry + 1, kx, kz, JJ_HIDE, kf)])
    # The ambush starts when the player closes to three tiles of Giovanni; J&J always come first.
    g[3].append(struct.pack('<Hhh5H', entry, gx - 3, gz - 3, 7, 7, 0, 0, JJ_STATE))
    return dict(giovanni=(gx, gz), jessie=(jx, jz), james=(kx, kz), entry=entry)


def game_corner(rom, guard, b1f, source):
    """A Rocket in the Game Corner: beat him and the poster switch opens the stairs down."""
    main = rom.loadArm9()
    d = main.sections[0].data
    at = TABLE + GAME_CORNER * 24
    rec = bytearray(d[at:at + 24])
    t = lambda l: yellow_text.message(source, 'GameCorner', l)
    lines = [t('_GameCornerRocketImGuardingThisPosterText'), t('_GameCornerRocketAfterBattleText'),
             t('_GameCornerPosterSwitchBehindPosterText').rstrip('@')]
    enter = lambda s: s.emit(174, 6, 6, 0, 0).emit(175).emit(176, b1f, 0, UP_ARRIVAL[0], UP_ARRIVAL[1], 1).emit(174, 6, 6, 1, 0).emit(175)
    s = Script().emit(96).emit(104).emit(32, HQ_OPEN).jump('open', 1)
    s.msg(0)
    s.emit(213, guard, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, guard).msg(1).msg(2).emit(30, HQ_OPEN)
    s.label('open')
    enter(s)
    s.emit(97).emit(2)
    s.label('lost').emit(219)
    end(s)
    entry = ts._attach(rom, rec, lines, [s.finish()])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    g = events_decode(events.files[struct.unpack_from('<H', rec, 16)[0]])
    g[1].append(actor(len(g[1]) + 20, ROCKET_SPRITE, entry, GUARD[0], GUARD[1], 0, GUARD[2]))
    struct.pack_into('<H', rec, 16, len(events.files))
    events.files.append(events_encode(g))
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    main = rom.loadArm9()
    main.sections[0].data = bytearray(main.sections[0].data)
    main.sections[0].data[at:at + 24] = rec
    rom.arm9 = main.save(compress=True)
    return dict(map=GAME_CORNER, guard=GUARD, entry=entry)
