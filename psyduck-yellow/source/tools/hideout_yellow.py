"""Rocket Hideout laid out like Yellow's: B1F-B4F rebuilt from pret/pokeyellow's maps (facility tileset) at 2x scale with cave_floor.py, joined to the Game Corner.

Everything gameplay-side is reused from the four stand-in clones (rocket_hideout.py + hideout_items.py, maps 547-550): their script banks and texts stay as they are, so the trainer
records, ball pickups, the Jessie/James ambush and Giovanni's Silph Scope scene work unchanged. What changes is the geometry and where things stand: Yellow's coordinates and warps.
The elevator is a pair of door tiles on B1F and B2F (a trigger script: no Lift Key -> Yellow's 'It appears to need a key.', Lift Key -> straight to B4F's elevator doors) and B4F's doors lead back to B1F;
there is no floor menu. The Lift Key is the real key item (878): its ball stands where Yellow's does, and the doors check the bag.
Left out (recorded in CAMPAIGN-FIRST-PLAN.md): the spin-tile mazes (arrow tiles are plain floor), the elevator's floor menu, Yellow's TM balls (this ROM has no Horn Drill / Double-Edge / Razor Wind).

Usage: hideout_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
from forest_progression import pickup
from hideout_items import BALLS
from mtmoon_yellow import parse, FACE
from opening import Script, actor, encode_text, end, events_decode, events_encode, script_bank
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
import spin_tiles
import yellow_text
from rocket_hideout import GAME_CORNER, GIOVANNI_HIDE, JJ_HIDE
from viridian_tutorial import TABLE

OLD = {1: 547, 2: 548, 3: 549, 4: 550}
NAMES = {1: 'RocketHideoutB1F', 2: 'RocketHideoutB2F', 3: 'RocketHideoutB3F', 4: 'RocketHideoutB4F'}
BLOCKS = {1: (15, 14), 2: (15, 14), 3: (15, 14), 4: (15, 12)}
CX = CZ = 3
OX, OZ = 18, 20
AREA = 64                                      # Rocket HQ's area: the source of the facility textures
TEX = [('aj_fl01', 'aj_fl01_pl', 'HqFloor'), ('aji_w01', 'aji_w01_pl', 'HqWall'), ('aji_f02', 'aji_f02_pl', 'HqTop'), ('aj_box01', 'aj_box01_pl', 'HqCrate')]
MATS = [('floor', 0, 'floor'), ('wall_top', 2, 'wall_top'), ('wall_slope', 1, 'wall_slope'), ('stone_top', 3, 'stone_top'), ('stone_side', 3, 'stone_side')]
ITEM_ID = {'ESCAPE_ROPE': 78, 'HYPER_POTION': 25, 'MOON_STONE': 81, 'NUGGET': 92, 'SUPER_POTION': 26, 'RARE_CANDY': 50, 'HP_UP': 45, 'IRON': 47}
LIFT_KEY, LIFT_FLAG, ELEV_VAR = 878, 0x9F9, 0x4178     # the Lift Key is a real item (878); LIFT_FLAG hides its ball; the elevator doors' trigger var is never written (stays 0)
FLOOR_OF = {f'ROCKET_HIDEOUT_B{f}F': f for f in (1, 2, 3, 4)}
SPIN = {2: 'RocketHideoutB2F', 3: 'RocketHideoutB3F'}     # the floors with Yellow's arrow-tile mazes (spin_tiles.py)


def kept_warps(y):
    """Every Yellow warp, in order. -> [(x, y, dest, dest warp number, Yellow warp number)]"""
    return [(x, yy, dest, wid, i + 1) for i, (x, yy, dest, wid) in enumerate(y['warps'])]


def patch(rom, source):
    y = {f: parse(source, NAMES[f]) for f in OLD}
    keep = {f: kept_warps(y[f]) for f in OLD}
    index = {(f, num): k for f in OLD for k, (*_, num) in enumerate(keep[f])}      # (floor, Yellow warp number) -> my warp index
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    olds = ext.records(rom)
    templates = [bytes(olds[OLD[f] - ext.NATIVE_COUNT]) for f in OLD]
    ids = dict(zip(OLD, ext.install(rom, templates)))
    report = {}
    for f in OLD:
        W, H = BLOCKS[f]
        report[f] = cf.install(rom, source, NAMES[f], ids[f], W, H, [(w[0], w[1]) for w in keep[f]], OX, OZ, CX, CZ, AREA, TEX, MATS, None, tileset='facility', coll=cf.FACILITY_COLL, extra_floor=[(o['x'], o['y']) for o in y[f]['objs']])
    old_flags = {flag: item for f in BALLS for item, _, flag in BALLS[f]}
    scripts_narc = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    for v in (LIFT_FLAG, ELEV_VAR):                # fresh in every script and actor list of this ROM
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts_narc.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for g in events_decode(raw) for a in g), hex(v)
    first = {f: len(split_bank(scripts_narc.files[struct.unpack_from('<H', templates[f - 1], 6)[0]])) + 1 for f in OLD}   # entry of the one script each floor gains
    b4_arrival = cf.STATE[NAMES[4]]['arrival'][index[(4, 2)]]       # B4F's elevator doors: where the lift lets you out
    spin = {f: spin_tiles.load(source, SPIN[f]) for f in SPIN}
    spin_first = {f: first[f] + (0 if f == 3 else 1) for f in SPIN}      # entry of each floor's first slide script (B3F gains no other script)
    new_events = {}
    for f in OLD:
        name = NAMES[f]
        st = cf.STATE[name]
        og = events_decode(events.files[struct.unpack_from('<H', olds[OLD[f] - ext.NATIVE_COUNT], 16)[0]])
        old_actors = [bytes(a) for a in og[1]]
        flag = lambda a: struct.unpack_from('<H', a, 8)[0]
        script = lambda a: struct.unpack_from('<H', a, 10)[0]
        trainers_old = [a for a in old_actors if script(a) >= 3000]
        balls_old = {old_flags[flag(a)]: a for a in old_actors if flag(a) in old_flags}
        giovanni_old = next((a for a in old_actors if flag(a) == GIOVANNI_HIDE), None)
        jj_old = [a for a in old_actors if flag(a) == JJ_HIDE]
        objs = y[f]['objs']
        g = [[], [], [], []]
        used = set()

        def put(a, pos, face):
            a = bytearray(a)
            struct.pack_into('<2H', a, 24, *cf.place(name, *pos))
            struct.pack_into('<h', a, 12, FACE[face])
            return a

        def obj_id(a):
            n = struct.unpack_from('<H', a, 0)[0]
            assert n not in used, (name, n)
            used.add(n)
        y_trainers = [o for o in objs if o['opp'] and o['sprite'] == 'SPRITE_ROCKET']
        assert len(y_trainers) == len(trainers_old), (name, len(y_trainers), len(trainers_old))
        for o, a in zip(y_trainers, trainers_old):
            vision = struct.unpack_from('<H', a, 14)[0]
            a = put(a, (o['x'], o['y']), o['face'])
            struct.pack_into('<H', a, 14, vision * cf.SCALE)
            obj_id(a); g[1].append(bytes(a))
        for o in objs:
            if o['item'] in ITEM_ID and ITEM_ID[o['item']] in balls_old:
                a = put(balls_old[ITEM_ID[o['item']]], (o['x'], o['y']), 'NONE')
                obj_id(a); g[1].append(bytes(a))
        assert len([1 for o in objs if o['item'] in ITEM_ID]) == len(balls_old), name
        if f == 4:
            gio = next(o for o in objs if o['sprite'] == 'SPRITE_GIOVANNI')
            a = put(giovanni_old, (gio['x'], gio['y']), gio['face']); obj_id(a); g[1].append(bytes(a))
            jj = [o for o in objs if o['sprite'] in ('SPRITE_JESSIE', 'SPRITE_JAMES')]
            assert len(jj) == len(jj_old) == 2
            jessie_old, james_old = jj_old[0], jj_old[1]      # old order: Jessie then James (Yellow lists James first)
            for o in jj:
                a = put(jessie_old if o['sprite'] == 'SPRITE_JESSIE' else james_old, (o['x'], o['y']), o['face'])
                obj_id(a); g[1].append(bytes(a))
            # the ambush: one trigger over the corridor around Jessie and James (the old trigger's script, state and value)
            old_trig = og[3][0]
            tscript, _, _, _, _, _, tvalue, tstate = struct.unpack('<Hhh5H', old_trig)
            cx0, cz0 = min(o['x'] for o in jj) - 3, min(o['y'] for o in jj) - 3
            g[3].append(struct.pack('<Hhh5H', tscript, st['OX'] + cf.SCALE * cx0, st['OZ'] + cf.SCALE * cz0, cf.SCALE * 8, cf.SCALE * 7, 0, tvalue, tstate))
        if f == 4:
            key = next(o for o in objs if o['item'] == 'LIFT_KEY')
            obj = max(used) + 1
            used.add(obj)
            g[1].append(actor(obj, 87, first[4], *cf.place(name, key['x'], key['y']), LIFT_FLAG, 0))
        # warps: arrivals first (one per kept Yellow warp), then the ring tiles
        for k, (wx, wy, dest, wid, num) in enumerate(keep[f]):
            ax, az = st['arrival'][k]
            g[2].append(struct.pack('<4H', ax, az, ids[f], k) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            dest, wid = keep[f][wi][2], keep[f][wi][3]
            if dest == 'GAME_CORNER':
                dmap, anchor = GAME_CORNER, 0
            elif dest == 'ROCKET_HIDEOUT_ELEVATOR':
                if f in (1, 2):                    # the lift doors: a trigger that checks the Lift Key (script below)
                    g[3].append(struct.pack('<Hhh5H', first[f], tx, tz, 1, 1, 0, 0, ELEV_VAR))
                    continue
                dmap, anchor = ids[1], index[(1, 3)]       # B4F's doors lead back up to B1F's lift
            else:
                df = FLOOR_OF[dest]
                dmap, anchor = ids[df], index[(df, wid)]
            g[2].append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        if f in SPIN:                              # every arrow tile starts its slide (a one-tile trigger; the shared var is never written)
            lists = spin_tiles.distinct(spin[f])
            for (ax, ay), mv in sorted(spin[f].items()):
                g[3].append(struct.pack('<Hhh5H', spin_first[f] + lists.index(mv), st['OX'] + cf.SCALE * ax, st['OZ'] + cf.SCALE * ay, cf.SCALE, cf.SCALE, 0, 0, ELEV_VAR))
        new_events[f] = len(events.files)
        events.files.append(events_encode(g))
    rom.setFileByName('a/0/3/2', events.save())
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for f in OLD:
        struct.pack_into('<H', ovd, start + 24 * (ids[f] - ext.NATIVE_COUNT) + 16, new_events[f])
    # ---- one new script per floor: the lift door check (B1F, B2F) and the Lift Key pickup (B4F); text rows are appended to the floor's own bank
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    need_key = yellow_text.message(source, 'RocketHideoutElevator', '_RocketHideoutElevatorAppearsToNeedKeyText').rstrip('@')
    for f in OLD:
        at = start + 24 * (ids[f] - ext.NATIVE_COUNT)
        bank_id, _, text_id = struct.unpack_from('<3H', ovd, at + 6)
        key, rows = decode_messages(texts.files[text_id])
        base = len(rows)
        bank = split_bank(scripts.files[bank_id])
        assert len(bank) + 1 == first[f], (f, len(bank), first[f])
        if f in (1, 2):
            lines = [need_key, 'The lift rumbles upward...']
            s_ = Script().emit(96).emit(128, LIFT_KEY, 1, 0x800C).compare(0x800C, 1).jump('go', 1)
            s_.msg(base)
            end(s_)
            s_.label('go')
            s_.emit(174, 6, 6, 0, 0).emit(175).emit(176, ids[4], 0, b4_arrival[0], b4_arrival[1], 1).emit(174, 6, 6, 1, 0).emit(175)
            s_.emit(97).emit(2)
            new = s_.finish()
        elif f == 4:
            lines = ['{PLAYER} found LIFT KEY!', 'You have no room for this.']
            lift_obj = max(struct.unpack_from('<H', a, 0)[0] for a in events_decode(events.files[new_events[4]])[1])
            new = pickup(LIFT_KEY, LIFT_FLAG, base, lift_obj)
        else:
            lines, new = [], None
        if f == 4:                                  # the old B4F scripts hid the wrong objects (Giovanni=1, Jessie=2, James=3): fix them in this floor's bank
            fixes = [(struct.pack('<6H', 30, JJ_HIDE, 101, 1, 101, 2), struct.pack('<6H', 30, JJ_HIDE, 101, 2, 101, 3)),
                     (struct.pack('<4H', 30, GIOVANNI_HIDE, 101, 0), struct.pack('<4H', 30, GIOVANNI_HIDE, 101, 1))]
            for pat, repl in fixes:
                hits = [i for i, sc in enumerate(bank) if bytes(sc).count(pat)]
                assert len(hits) == 1 and bytes(bank[hits[0]]).count(pat) == 1, (pat.hex(), hits)
                bank[hits[0]] = bytes(bank[hits[0]]).replace(pat, repl)
        if new is not None:
            bank.append(new)
        if f in SPIN:
            assert len(bank) + 1 == spin_first[f], (f, len(bank), spin_first[f])
            bank.extend(spin_tiles.script(mv, cf.SCALE) for mv in spin_tiles.distinct(spin[f]))
        encoded = []
        for line in lines:
            encoded.extend(decode_messages(encode_text([line], PH))[1])
        scripts.files.append(script_bank(bank))
        texts.files.append(encode_messages(key, rows + encoded))
        struct.pack_into('<H', ovd, at + 6, len(scripts.files) - 1)
        struct.pack_into('<H', ovd, at + 10, len(texts.files) - 1)
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- the Game Corner poster leads to the new B1F: retarget its warp command (opcode 176: map, 0, x, z, 1)
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    bank = struct.unpack_from('<H', d, TABLE + GAME_CORNER * 24 + 6)[0]
    raw = bytearray(scripts.files[bank])
    ax, az = cf.STATE[NAMES[1]]['arrival'][index[(1, 2)]]
    hits = 0
    for old in OLD.values():
        pat = struct.pack('<6H', 176, old, 0, 51, 5, 1)
        at = raw.find(pat)
        while at >= 0:
            raw[at:at + 12] = struct.pack('<6H', 176, ids[1], 0, ax, az, 1)
            hits += 1
            at = raw.find(pat)
    assert hits == 1, hits
    scripts.files[bank] = bytes(raw)
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.arm9 = main.save(compress=True)
    return dict(ids=ids, floors=report, game_corner_arrival=(ax, az))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
