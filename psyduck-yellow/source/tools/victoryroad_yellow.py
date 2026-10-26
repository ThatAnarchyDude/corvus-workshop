"""Victory Road rebuilt from pret/pokeyellow's maps (1F 10x9 blocks, 2F and 3F 15x9; cavern tileset) with Yellow's Strength-boulder puzzle.

Replaces HG's three caves (maps 124/178/179, which needed Rock Smash and had no switches). Everything gameplay-side is carried over from the current build: the same eleven trainer actors (records
3981-3991), the item balls (Rare Candy 1F; Full Heal, Guard Spec 2F; Max Revive, TM Explosion 3F, their old hide flags), Moltres, and the old wild tables. Yellow's TM Sky Attack, Submission and
Mega Kick stay out (this ROM has no such TMs).

The puzzle: boulders are HG's own Strength boulders (sprite 85, script 10001). A trigger ring around each switch (the player always ends a push on a tile beside the boulder's new tile) runs a script that reads every boulder's tile (script command 106);
a boulder on the switch sets that barrier's flag and hides its rocks (the barrier is a row of sprite-84 rocks across the corridor in the places Yellow's block swaps happen: 1F 1 barrier, 2F 2, 3F 1). 3F's hole drops the player (and a pushed boulder)
to 2F. Yellow's exits: 1F south -> Route 23's gate; 2F east -> Indigo Plateau's front (HG's 3F top exit).

Usage: victoryroad_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
import trainer_alloc
from forest_progression import pickup
from mansion_yellow import corridor_axis, drop_script
from mtmoon_yellow import FACE, MATS, TEX, parse
from opening import Script, actor, encode_text, end, events_decode, events_encode, script_bank
from parcel_quest import PH
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE
import vr_items

OLD = {1: 124, 2: 178, 3: 179}
NAMES = {1: 'VictoryRoad1F', 2: 'VictoryRoad2F', 3: 'VictoryRoad3F'}
BLOCKS = {1: (10, 9), 2: (15, 9), 3: (15, 9)}
OX, OZ, CX, CZ, AREA = 8, 12, 3, 3, 70
ROUTE23_GATE, INDIGO = 299, 58
BOULDER_SPRITE, BOULDER_SCRIPT, ROCK_SPRITE = 85, 10001, 84
FLAGS = {'b1': 0x956, 'b2a': 0x957, 'b2b': 0x958, 'b3': 0x959}        # one hide flag per barrier (checked free by trainer_alloc.assert_flags_free)
# switches (Yellow step) and the barrier block each opens: (barrier key, switch (x, y), barrier block (y, x), open block id)
SWITCHES = {1: [('b1', (17, 13), (6, 4), 0x1D)],
            2: [('b2a', (1, 16), (4, 3), 0x15), ('b2b', (9, 16), (7, 11), 0x1D)],
            3: [('b3', (3, 5), (5, 3), 0x1D)]}
HOLE3 = (23, 15)                                    # 3F: the hole (player falls to 2F at (22, 16))
HOLE_TO = (22, 16)
BALLS = {'RARE_CANDY': (1, 0xA37, 50, 'RARE CANDY'), 'FULL_HEAL': (2, 0xA35, 27, 'FULL HEAL'), 'GUARD_SPEC': (2, 0xA31, 55, 'GUARD SPEC.'),
         'MAX_REVIVE': (3, 0xA30, 29, 'MAX REVIVE'), 'TM_EXPLOSION': (3, 0xA2F, 391, 'TM64 (EXPLOSION)')}
DUMMY_VAR = 0x4179                                  # never written (stays 0): the triggers' var
MOLTRES_OBJECT_FLOOR = 2


def poll_switch(boulders, flag, x0, z0, rocks):
    """Trigger script beside a switch: is any boulder on one of the switch's four tiles? (not a frame script: one that runs every frame keeps the player locked)"""
    s = Script().emit(96).emit(32, flag).jump('done', 1)
    for b in boulders:
        s.emit(106, b, 0x4000, 0x4001)
        for dx in range(cf.SCALE):
            for dz in range(cf.SCALE):
                s.compare(0x4000, x0 + dx).jump(f'no{b}_{dx}_{dz}', 5).compare(0x4001, z0 + dz).jump(f'no{b}_{dx}_{dz}', 5)
                s.jump('hit')
                s.label(f'no{b}_{dx}_{dz}')
    s.jump('done')
    s.label('hit').emit(30, flag)
    for r in rocks:
        s.emit(101, r)
    s.label('done')
    end(s)
    return s.finish()


def poll_hole(boulders, hx0, hz0):
    """Trigger script beside 3F's hole: a boulder in the hole is gone."""
    s = Script().emit(96)
    for b in boulders:
        s.emit(106, b, 0x4000, 0x4001)
        for dx in range(cf.SCALE):
            for dz in range(cf.SCALE):
                s.compare(0x4000, hx0 + dx).jump(f'n{b}_{dx}_{dz}', 5).compare(0x4001, hz0 + dz).jump(f'n{b}_{dx}_{dz}', 5)
                s.emit(101, b)
                s.label(f'n{b}_{dx}_{dz}')
    end(s)
    return s.finish()


def patch(rom, source):
    y = {f: parse(source, NAMES[f]) for f in NAMES}
    trainer_alloc.assert_flags_free(rom, list(FLAGS.values()))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    old = {}
    for f, m in OLD.items():
        g = events_decode(events.files[struct.unpack_from('<H', d, TABLE + m * 24 + 16)[0]])
        old[f] = dict(actors=[bytes(a) for a in g[1]], wild=d[TABLE + m * 24])
    ids = dict(zip(OLD, ext.install(rom, [ext.native_record(rom, OLD[f]) for f in OLD])))
    edits = {f: {(bx, by): blk for _, _, (by, bx), blk in SWITCHES.get(f, [])} for f in NAMES}
    report = {}
    for f in NAMES:
        W, H = BLOCKS[f]
        report[f] = cf.install(rom, source, NAMES[f], ids[f], W, H, [(w[0], w[1]) for w in y[f]['warps']], OX, OZ, CX, CZ, AREA, TEX, MATS, None, edits=edits[f],
                               extra_floor=[(o['x'], o['y']) for o in y[f]['objs']])
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    wild = ndspy.narc.NARC(rom.getFileByName('a/0/3/7'))
    new_events, new_scripts, new_texts, new_inits = {}, {}, {}, {}
    key = decode_messages(encode_text(['x'], PH))[0]
    for f in NAMES:
        name, st = NAMES[f], cf.STATE[NAMES[f]]
        bank, rows = [], []

        def message(*lines):
            first = len(rows)
            for line in lines:
                rows.extend(decode_messages(encode_text([line], PH))[1])
            return first

        g = [[], [], [], []]
        used = 0
        # trainers: the old actors, in order, at Yellow's positions
        old_trainers = [a for a in old[f]['actors'] if 3000 <= struct.unpack_from('<H', a, 10)[0] < 4100]
        trainers = [o for o in y[f]['objs'] if o['opp']]
        assert len(trainers) == len(old_trainers), (f, len(trainers), len(old_trainers))
        for o, a in zip(trainers, old_trainers):
            a = bytearray(a)
            struct.pack_into('<H', a, 0, used)
            struct.pack_into('<2H', a, 24, *cf.place(name, o['x'], o['y']))
            struct.pack_into('<h', a, 12, FACE[o['face']])
            struct.pack_into('<H', a, 14, struct.unpack_from('<H', a, 14)[0] * cf.SCALE)
            used += 1
            g[1].append(bytes(a))
        # balls
        for o in y[f]['objs']:
            if o['item'] in BALLS and BALLS[o['item']][0] == f:
                _, flag, item, label = BALLS[o['item']]
                base = message('{PLAYER} found %s!' % label, 'You have no room for this.')
                bank.append(pickup(item, flag, base, used))
                g[1].append(actor(used, 87, len(bank), *cf.place(name, o['x'], o['y']), flag, 0))
                used += 1
        # Moltres
        for o in y[f]['objs']:
            if o['sprite'] == 'SPRITE_BIRD':
                vr_items.MOLTRES['object'] = used
                text = message(vr_items.MOLTRES['text'])
                bank.append(vr_items.moltres_script(text))
                g[1].append(actor(used, vr_items.MOLTRES['sprite'], len(bank), *cf.place(name, o['x'], o['y']), vr_items.MOLTRES['flag'], 0))
                used += 1
        # boulders
        boulders = []
        for o in y[f]['objs']:
            if o['sprite'] == 'SPRITE_BOULDER':
                g[1].append(actor(used, BOULDER_SPRITE, BOULDER_SCRIPT, *cf.place(name, o['x'], o['y']), 0, 0))
                boulders.append(used)
                used += 1
        # barriers: a row of rocks across each corridor, hidden by the barrier's flag
        _, walk = cf.load(source, name, *BLOCKS[f], 'cavern', cf.CAVERN_COLL, edits[f])
        switches = []
        for key_, (sx, sy), (by, bx), blk in SWITCHES.get(f, []):
            axis = corridor_axis(walk, bx, by)
            tiles = [(4 * bx + a, 4 * by + b) for a in range(4) for b in range(4) if st['tk'].get((4 * bx + a, 4 * by + b)) == 'floor']
            if axis == 'ns':
                row = max({t[1] for t in tiles}, key=lambda z: (sum(1 for t in tiles if t[1] == z), -abs(z - (4 * by + 1))))
                line = [t for t in tiles if t[1] == row]
            else:
                col = max({t[0] for t in tiles}, key=lambda c: (sum(1 for t in tiles if t[0] == c), -abs(c - (4 * bx + 1))))
                line = [t for t in tiles if t[0] == col]
            rocks = []
            for tx, tz in line:
                g[1].append(actor(used, ROCK_SPRITE, 0, st['OX'] + tx, st['OZ'] + tz, FLAGS[key_], 0))
                rocks.append(used)
                used += 1
            x0, z0 = st['OX'] + cf.SCALE * sx, st['OZ'] + cf.SCALE * sy
            switches.append((FLAGS[key_], x0, z0, rocks))
        hole = None
        if f == 3:
            hx0, hz0 = st['OX'] + cf.SCALE * HOLE3[0], st['OZ'] + cf.SCALE * HOLE3[1]
            dx, dz = cf.place(NAMES[2], *HOLE_TO)
            bank.append(drop_script(ids[2], dx, dz))
            g[3].append(struct.pack('<Hhh5H', len(bank), hx0, hz0, cf.SCALE, cf.SCALE, 0, 0, DUMMY_VAR))
            hole = (hx0, hz0)
        # the switch checks: a trigger over the switch's four tiles and the ring around them
        for flag, x0, z0, rocks in switches:
            bank.append(poll_switch(boulders, flag, x0, z0, rocks))
            g[3].append(struct.pack('<Hhh5H', len(bank), x0 - 1, z0 - 1, cf.SCALE + 2, cf.SCALE + 2, 0, 0, DUMMY_VAR))
        if hole:
            bank.append(poll_hole(boulders, *hole))
            g[3].append(struct.pack('<Hhh5H', len(bank), hole[0] - 1, hole[1] - 1, cf.SCALE + 2, cf.SCALE + 2, 0, 0, DUMMY_VAR))
        init = bytes(4)
        # warps: arrivals, then the ring tiles (Yellow's destinations)
        for k, w in enumerate(y[f]['warps']):
            ax, az = st['arrival'][k]
            g[2].append(struct.pack('<4H', ax, az, ids[f], k) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            dest, wid = y[f]['warps'][wi][2], y[f]['warps'][wi][3]
            if dest == 'LAST_MAP':
                dmap, anchor = (ROUTE23_GATE, 1) if f == 1 else (INDIGO, 0)
            else:
                dmap, anchor = ids[{'VICTORY_ROAD_1F': 1, 'VICTORY_ROAD_2F': 2, 'VICTORY_ROAD_3F': 3}[dest]], wid - 1
            g[2].append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        new_events[f] = len(events.files)
        events.files.append(events_encode(g))
        new_scripts[f] = len(scripts.files)
        scripts.files.append(script_bank(bank))
        new_inits[f] = len(scripts.files)
        scripts.files.append(init)
        new_texts[f] = len(texts.files)
        texts.files.append(encode_messages(key, rows))
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for f in NAMES:
        at = start + 24 * (ids[f] - ext.NATIVE_COUNT)
        ovd[at] = old[f]['wild']
        struct.pack_into('<3H', ovd, at + 6, new_scripts[f], new_inits[f], new_texts[f])
        struct.pack_into('<H', ovd, at + 16, new_events[f])
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- the rest of the world: Route 23's gate and Indigo Plateau's front door lead to the new floors
    main = rom.loadArm9()
    dd = main.sections[0].data = bytearray(main.sections[0].data)
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    rewired = {}
    for m, old_dest, target, anchor in ((ROUTE23_GATE, OLD[1], ids[1], 0), (INDIGO, OLD[3], ids[2], 1)):
        eid = struct.unpack_from('<H', dd, TABLE + m * 24 + 16)[0]
        g = events_decode(events.files[eid])
        hit = [i for i, w in enumerate(g[2]) if struct.unpack_from('<4H', w)[2] == old_dest]
        assert len(hit) == 1, (m, hit)
        x, z, _, _ = struct.unpack_from('<4H', g[2][hit[0]])
        g[2][hit[0]] = struct.pack('<4H', x, z, target, anchor) + bytes(g[2][hit[0]][8:])
        events.files.append(events_encode(g))
        struct.pack_into('<H', dd, TABLE + m * 24 + 16, len(events.files) - 1)
        rewired[m] = (target, anchor)
    rom.arm9 = main.save(compress=True)
    rom.setFileByName('a/0/3/2', events.save())
    return dict(ids=ids, floors=report, rewired=rewired)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
