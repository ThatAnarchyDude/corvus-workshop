"""Silph Co. in HeartGold's single Saffron Silph map (402, a small lobby).

Four clones of the lobby (tiles measured with tools/explore.py, data/silph402-tiles.json) hold Yellow's 2F-11F in
order: A = 2F-4F, B = 5F-6F, C = 7F-8F (rival, Lapras), D = 9F-11F (Giovanni, President, Master Ball). The lobby's
elevator warp leads up through A-D; D's elevator returns to the lobby. Yellow's trainers, teams, moves and dialogue
are kept. Card Key doors, warp tiles, item balls and the Pokemon reports are deferred.
"""
import json
import re
import struct
from pathlib import Path
import ndspy.narc
import map_header_extension as ext
import tower_scenes as ts
import rocket_hideout as rh
import route_progression as rp
import yellow_route_reference as yellow_ref
import yellow_text
import blue_properties_shared as shared
from map_edit import MapEdit
from opening import Script, actor, events_decode, events_encode, end
from prototype import decode_messages
from progression_cleanup import selected_battle
from escort import music
from route6_trainers import patch as install_trainers

LOBBY = 402
TILES = {tuple(t) for t in json.loads((Path(__file__).resolve().parents[1] / 'data/silph402-tiles.json').read_text())['tiles']}
DOOR, ELEVATOR, LANDING = (11, 13), (3, 3), (3, 4)      # the elevator is a step trigger on ELEVATOR; LANDING is where a warp from above arrives
GROUPS = {1: (2, 3, 4), 2: (5, 6), 3: (7, 8), 4: (9, 10, 11)}        # clone -> Yellow floors it stands in for
ROLES = {'OPP_ROCKET': 'Rocket', 'OPP_SCIENTIST': 'Scientist', 'OPP_JUGGLER': 'Juggler'}
RIVAL_DONE, GIOVANNI_DONE, LAPRAS_GIVEN, MASTER_GIVEN = 0xA8B, 0xA68, 0xA65, 0xA64
RIVAL_STATE = 0x4176                            # 0x4175 collides with bytes in an unrelated script bank
RIVAL_SPRITE, FUJI_SPRITE, GIOVANNI_SPRITE, GIOVANNI_TEMPLATE = 375, 317, 385, 700
LAPRAS, LAPRAS_LEVEL, MASTER_BALL = 131, 15, 1
FACING = rh.FACING
SIDE = {(0, -1): 0, (0, 1): 1, (-1, 0): 2, (1, 0): 3}


def yellow_trainers(source, floor):
    name = f'SilphCo{floor}F'
    scripts = (Path(source) / 'scripts' / (name + '.asm')).read_text()
    if floor == 11:                  # pokeyellow's header names _SilphCo11FRocket*, but the text file labels them Rocket2*
        messages = {k: yellow_text.message(source, name, f'_{name}Rocket2{k}') for k in ('BattleText', 'EndBattleText', 'AfterBattleText')}
        return dict(map=name, trainers=[dict(role='Rocket', yellow_position=[15, 9], facing='UP', vision=3, messages=messages,
                                             team=ts.Yellow(source).class_party('RocketData', 40))], grass=[], grass_rate=0)
    heads = re.findall(r'trainer EVENT_BEAT_\w+_TRAINER_(\d+),', scripts)
    objects = (Path(source) / 'data/maps/objects' / (name + '.asm')).read_text()
    count = len(re.findall(r'object_event[^\n]*OPP_(?:ROCKET|SCIENTIST|JUGGLER)\b', objects))
    ref = yellow_ref.reference(source, name, len(heads), extra_roles=ROLES, wild=False, first_index=int(heads[0]) if heads else 0)
    assert len(ref['trainers']) == count, (name, count)
    return ref


def place(route, count, taken):
    """Trainer tiles spread over the whole floor in order of distance from the door, off the route, facing it."""
    on_route = set(route)
    dist = {}
    queue = [DOOR]
    dist[DOOR] = 0
    for c in queue:
        for dx, dz in FACING:
            n = (c[0] + dx, c[1] + dz)
            if n in TILES and n not in dist:
                dist[n] = dist[c] + 1
                queue.append(n)
    ring = sorted(TILES, key=lambda p: (dist[p], p))
    spots = []
    for k in range(count):
        target = ring[(k + 1) * len(ring) // (count + 1)]
        free = [p for p in ring if p not in on_route and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 3 for q in taken)
                and abs(p[0] - DOOR[0]) + abs(p[1] - DOOR[1]) >= 4 and abs(p[0] - ELEVATOR[0]) + abs(p[1] - ELEVATOR[1]) >= 3]
        p = min(free, key=lambda p: (abs(p[0] - target[0]) + abs(p[1] - target[1]), p))
        near = min(route, key=lambda q: abs(p[0] - q[0]) + abs(p[1] - q[1]))
        dx, dz = near[0] - p[0], near[1] - p[1]
        face = (0 if dz < 0 else 1) if abs(dz) >= abs(dx) else (2 if dx < 0 else 3)
        spots.append((p[0], p[1], face))
        taken.add(p)
    return spots


def extend_hook(rom, silph_first):
    """The Blue-starter eligibility helper (rebuilt by the Tower step) gains a fifth range for Silph's rival records."""
    main = rom.loadArm9()
    itcm = main.sections[1]
    base = itcm.ramAddress
    target = shared.OLD + ts.FREE_FROM
    at = target - base
    old = ts._helper(809, 856, target)
    assert bytes(itcm.data[at:at + len(old)]) == old, 'Blue helper is not the Tower-step helper'
    new = shared.assemble(f'''movs r0,r3
ldr r1,old_first
subs r0,r0,r1
cmp r0,#9
bls yes
movs r0,r3
ldr r1,cerulean_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,r3
ldr r1,ship_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,r3
ldr r1,tower_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,r3
ldr r1,silph_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,#0
bx lr
yes:
movs r0,#1
bx lr
.align 2
old_first: .word 741
cerulean_first: .word 782
ship_first: .word 809
tower_first: .word 856
silph_first: .word {silph_first}
''', target)
    assert len(new) <= ts.OLD_WRAPPER_BYTES - ts.FREE_FROM
    itcm.data = bytearray(itcm.data)
    itcm.data[at:at + len(new)] = new
    rom.arm9 = main.save(compress=True)


def rival_scripts(trainers, obj):
    s = Script().emit(96)
    music(s, 1088).msg(0)
    selected_battle(s, trainers, 1, 'result')
    s.label('result').emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.msg(1).jump('outro')
    s.label('lost').msg(2)
    s.label('outro').msg(3)
    music(s, 1089).emit(30, RIVAL_DONE).emit(101, obj).emit(41, RIVAL_STATE, 1).emit(81, 0).emit(82)
    end(s)
    return s.finish()


def elevator_script(dest):
    s = Script().emit(96).emit(174, 6, 6, 0, 0).emit(175).emit(176, dest, 0, DOOR[0], DOOR[1], 0).emit(174, 6, 6, 1, 0).emit(175).emit(97).emit(2)
    return s.finish()


def talk(*lines):
    return Script().emit(96).emit(104).msg(lines[0]).emit(97).emit(2).finish()


def lapras_script(first, full):
    s = Script().emit(96).emit(104).emit(32, GIOVANNI_DONE).jump('saved', 1)
    s.msg(first)                                         # still dangerous
    end(s)
    s.label('saved').emit(32, LAPRAS_GIVEN).jump('again', 1)
    s.msg(first + 1).msg(first + 2)
    s.emit(73, 1501).emit(137, LAPRAS, LAPRAS_LEVEL, 0, 0, 0, 0x800C)
    s.compare(0x800C, 1).jump('got', 1).msg(full)
    end(s)
    s.label('got').emit(30, LAPRAS_GIVEN).msg(first + 3)
    end(s)
    s.label('again').msg(first + 3)
    end(s)
    return s.finish()


def giovanni_script(giovanni, obj, base):
    s = Script().emit(96).emit(104).emit(32, GIOVANNI_DONE).jump('gone', 1)
    s.msg(base)
    s.emit(213, giovanni, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, giovanni).msg(base + 1).msg(base + 2)
    s.emit(30, GIOVANNI_DONE).emit(101, obj)
    end(s)
    s.label('gone').msg(base + 2)
    end(s)
    s.label('lost').emit(219)
    end(s)
    return s.finish()


def president_script(base):
    s = Script().emit(96).emit(104).emit(32, GIOVANNI_DONE).jump('freed', 1)
    s.msg(base + 3)
    end(s)
    s.label('freed').emit(32, MASTER_GIVEN).jump('again', 1)
    s.msg(base)
    s.emit(125, MASTER_BALL, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    s.emit(30, MASTER_GIVEN).emit(73, 1501).msg(base + 1).msg(base + 2)
    end(s)
    s.label('full').msg(base + 4)
    end(s)
    s.label('again').msg(base + 2)
    end(s)
    return s.finish()


def patch(rom, source):
    yellow = ts.Yellow(source)
    tables = rp.class_tables(rom)
    templates = {role: tables[role][0] for role in ('Scientist', 'Juggler')} | {'Rocket': rh.ROCKET_TEMPLATE}
    sprites = {role: tables[role][1] for role in ('Scientist', 'Juggler')} | {'Rocket': rh.ROCKET_SPRITE}
    refs = {floor: yellow_trainers(source, floor) for floor in range(2, 12)}
    installed = {}
    for floor, ref in refs.items():
        if ref['trainers']:
            installed[floor] = install_trainers(rom, ref, map_name=f'SilphCo{floor}F', expected_count=len(ref['trainers']), templates=templates)['trainers']
        else:
            installed[floor] = []
    book = ts.TrainerBook(rom)
    book.assert_unused((RIVAL_DONE, GIOVANNI_DONE, LAPRAS_GIVEN, MASTER_GIVEN, RIVAL_STATE))
    t = yellow_text.message
    rival_lines = [t(source, 'SilphCo7F', '_SilphCo7FRival' + x + 'Text') for x in ('WaitedHere', 'Defeated', 'Victory', 'GoodLuckToYou')]
    first, rival_ids = len(book.trainers.files), {}
    pairs = yellow.rival_team(4)                       # Silph Co. 7F, first of its three Eevee-evolution variants (Jolteon)
    for species in (54, 133):
        for gender, value in (('male', 1), ('female', 2)):
            team = [yellow.mon(n, lv) | dict(gender=0) for lv, n in pairs[:-1]]
            starter = yellow.mon('GOLDUCK' if species == 54 else pairs[-1][1], pairs[-1][0]) | dict(gender=value)
            if species == 54:                              # Psyduck's line is Golduck by Lv40, as the Eevee line is Jolteon
                starter['species'] = 55
            body = b''.join(struct.pack('<BB3H4H', 0, m['gender'], m['level'], m['species'], 0, *m['moves']) for m in team + [starter])
            rival_ids[f'{species}_{gender}'] = book.new(742, body, [rival_lines[0], rival_lines[1], rival_lines[3]], book.names[742], len(team) + 1)
    rival_ids[54], rival_ids[133] = rival_ids['54_male'], rival_ids['133_female']
    assert rival_ids['54_male'] == first
    giovanni_team = yellow.leader_party('GiovanniData', 1)
    giovanni_lines = [t(source, 'SilphCo11F', '_SilphCo11FGiovanni' + x + 'Text') for x in ('', 'ILostAgain', 'YouRuinedOurPlans')]
    giovanni = book.new(GIOVANNI_TEMPLATE, b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in giovanni_team),
                        giovanni_lines, rh.decode_messages(rh.encode_text(['GIOVANNI'], rh.PH))[1][0], len(giovanni_team))
    book.save()
    ts._cover_common(rom, giovanni)
    extend_hook(rom, first)

    base = ext.NATIVE_COUNT + len(ext.records(rom))
    ids = {n: base + n - 1 for n in GROUPS}
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    scripts.files.append(b'\0')
    header = len(scripts.files) - 1
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    native = events_decode(events.files[struct.unpack_from('<H', ext.native_record(rom, LOBBY), 16)[0]])
    route = rh.bfs(DOOR, ELEVATOR, TILES)
    records, report = [], {}
    for n, yellow_floors in GROUPS.items():
        rec = bytearray(ext.native_record(rom, LOBBY))
        rec[0] = 255
        struct.pack_into('<H', rec, 8, header)
        g = [[], [], [], []]
        down = (LOBBY if n == 1 else ids[n - 1], 8 if n == 1 else 1)
        up = (ids[n + 1], 0) if n < 4 else (LOBBY, 0)
        for w, (dest, anchor), (x, y) in zip(native[2], (down, up), ((11, 14), LANDING)):   # the native elevator tile (3,2) is a wall and plain floor never fires a warp
            g[2].append(struct.pack('<4H', x, y, dest, anchor) + w[8:])
        taken = {DOOR, ELEVATOR}
        entries = [(floor, e, b) for floor in yellow_floors for e, b in zip(refs[floor]['trainers'], installed[floor])]
        specials = []
        rh.TILES = TILES                                  # rocket_hideout's cluster() reads its module-level tile set
        if n == 3:
            rival_at = route[len(route) * 55 // 100]
            taken.add(rival_at)
            specials = rh.cluster(route, taken, 1)
        elif n == 4:
            specials = rh.cluster(route, taken, 2)
        spots = place(route, len(entries), taken)
        for obj, ((floor, entry, battle), (x, z, face)) in enumerate(zip(entries, spots)):
            a = bytearray(actor(obj, sprites[entry['role']], 3000 + battle['id'] - 1, x, z, facing=face))
            struct.pack_into('<H', a, 6, 1)
            struct.pack_into('<H', a, 14, entry['vision'])
            g[1].append(bytes(a))
        extra = {}
        lift = ids[n + 1] if n < 4 else LOBBY
        if n == 3:
            m = lambda l: t(source, 'SilphCo7F', l)
            lines = rival_lines + [m('_SilphCo7FSilphWorkerM4ItsReallyDangerousHereText'), m('_SilphCo7FSilphWorkerM1HaveThisPokemonText'),
                                   m('_SilphCo7FSilphWorkerM1LaprasDescriptionText'), m('_SilphCo7FSilphWorkerM1SavedText'),
                                   'You have no room for this.']
            robj, lobj = len(g[1]), len(g[1]) + 1
            entry = ts._attach(rom, rec, lines, [elevator_script(lift), rival_scripts(rival_ids, robj), talk(3), lapras_script(4, 8)])
            rx, rz = rival_at
            g[1].append(actor(robj, RIVAL_SPRITE, entry + 2, rx, rz, RIVAL_DONE, 1))
            lx, lz, lf = specials[0]
            g[1].append(actor(lobj, tables['Scientist'][1], entry + 3, lx, lz, 0, lf))
            g[3].append(struct.pack('<Hhh5H', entry + 1, rx - 2, rz - 2, 5, 5, 0, 0, RIVAL_STATE))
            extra = dict(rival=rival_at, lapras=(lx, lz), entry=entry)
        if n == 4:
            m = lambda l: t(source, 'SilphCo11F', l)
            lines = giovanni_lines + [m('_SilphCo11FSilphPresidentText'), '{PLAYER} got a MASTER BALL!', m('_SilphCo11FSilphPresidentMasterBallDescriptionText'),
                                      '...', m('_SilphCo11FSilphPresidentNoRoomText')]
            gobj, pobj = len(g[1]), len(g[1]) + 1
            entry = ts._attach(rom, rec, lines, [elevator_script(lift), giovanni_script(giovanni, gobj, 0), president_script(3)])
            (gx, gz, gf), (px, pz, pf) = specials
            g[1].append(actor(gobj, GIOVANNI_SPRITE, entry + 1, gx, gz, GIOVANNI_DONE, gf))
            g[1].append(actor(pobj, FUJI_SPRITE, entry + 2, px, pz, 0, pf))
            extra = dict(giovanni=(gx, gz), president=(px, pz), entry=entry)
        if n < 3:
            lines = []
            entry = ts._attach(rom, rec, lines or ['.'], [elevator_script(lift)])
        g[3].append(struct.pack('<Hhh5H', entry, ELEVATOR[0], ELEVATOR[1], 1, 1, 0, 0, 0))
        eid = len(events.files)
        events.files.append(events_encode(g))
        struct.pack_into('<H', rec, 16, eid)
        records.append(bytes(rec))
        report[n] = dict(map=ids[n], yellow_floors=yellow_floors, trainers=len(entries), **extra)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    assert ext.install(rom, records) == [ids[n] for n in GROUPS]
    edit = MapEdit(rom, LOBBY)
    lift = edit.script(lambda msg: elevator_script(ids[1]))
    edit.groups[3].append(struct.pack('<Hhh5H', lift, ELEVATOR[0], ELEVATOR[1], 1, 1, 0, 0, 0))                                  # the lobby's elevator now rides up through the clones
    w = bytearray(edit.groups[2][1])
    struct.pack_into('<4H', w, 0, LANDING[0], LANDING[1], ids[1], 0)
    edit.groups[2][1] = bytes(w)
    edit.save()
    return dict(floors=report, giovanni=giovanni, rival_first=first, rival_team=pairs, giovanni_team=giovanni_team)
