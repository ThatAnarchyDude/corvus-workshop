"""Viridian Gym rebuilt from pret/pokeyellow's map (10x9 blocks, GYM tileset) with Yellow's arrow-tile maze (spin_tiles.py), replacing the native HG gym layout (map 496).

Everything gameplay-side is reused from the native gym: the same four trainer actors and records (Yellow teams were already set by kanto_gyms.py), Giovanni (the native leader script, badge and TM),
the Gym Guide and the entry trigger; only where they stand (Yellow's coordinates), the walls and the arrows change. Viridian City's gym door is rewired to the new map.
Yellow's other four gym trainers are new records (trainer_alloc.py) with Yellow's teams and lines. Yellow's Revive ball is added.

Usage: viridian_gym_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
import re
import gym_conversion
import route_progression as rp
import spin_tiles
import tower_scenes as ts
import trainer_alloc
import yellow_text
from forest_progression import pickup
from hideout_yellow import AREA, MATS, OX, OZ, TEX
from mtmoon_yellow import FACE, parse
from opening import actor, encode_text, events_decode, events_encode, script_bank
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

GYM, CITY = 496, 50
W, H, CX, CZ = 10, 9, 2, 2
GYM_COLL = {0x11, 0x16, 0x19, 0x2B, 0x3C, 0x3D, 0x3F, 0x4A, 0x4C, 0x4D, 0x03}       # Gym_Coll (walkable tile ids, pokeyellow data/tilesets/collision_tile_ids.asm)
REVIVE, REVIVE_FLAG = 28, 0x9FD
TRIGGER_VAR = 0x4179                  # never written (stays 0)
NATIVE_TRAINER_SCRIPTS = (3680, 3681, 3682, 3683)       # trainers 681-684: Yellow's first four gym trainers, in object order
NEW_IDS = [1025, 1026, 1027, 1029]                      # Yellow's other four: new records; defeat flags 0x951-0x953 and 0x955 (checked free; 1028 would be 0x954, a Mansion ball)
CAMEL = ['CooltrainerM1', 'Hiker1', 'Rocker1', 'Hiker2', 'CooltrainerM2', 'Hiker3', 'Rocker2', 'CooltrainerM3']     # Yellow's text labels, in object order
SIGHT = [4, 4, 4, 2, 3, 4, 3, 4]                         # the gym's trainer headers' ranges, same order


def fresh(rom, values):
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    for v in values:
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for g in events_decode(raw) for a in g), hex(v)


def patch(rom, source):
    y = parse(source, 'ViridianGym')
    fresh(rom, [REVIVE_FLAG])
    trainer_alloc.assert_flags_free(rom, [0x550 + t_ for t_ in NEW_IDS])
    obj_text = open(f'{source}/data/maps/objects/ViridianGym.asm').read()
    roles = [rp.OPP[r] for r in re.findall(r'(OPP_\w+),\s*\d+\s*$', obj_text, re.M) if r != 'OPP_GIOVANNI']
    yellow = ts.Yellow(source)
    labels = gym_conversion.yellow_gym_trainers(source, 'ViridianGym')
    entries = [dict(role=roles[k], team=yellow.class_party(*labels[k]),
                    messages={s: yellow_text.message(source, 'ViridianGym', '_ViridianGym' + CAMEL[k] + s).rstrip('@') for s in ('BattleText', 'EndBattleText', 'AfterBattleText')}) for k in range(4, 8)]
    tables = rp.class_tables(rom)
    trainer_alloc.add(rom, entries, NEW_IDS, {r: tables[r][0] for r in set(e['role'] for e in entries)})
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    native = events_decode(events.files[struct.unpack_from('<H', d, TABLE + GYM * 24 + 16)[0]])
    template = ext.native_record(rom, GYM)
    mid = ext.install(rom, [template])[0]
    cg = events_decode(events.files[struct.unpack_from('<H', d, TABLE + CITY * 24 + 16)[0]])
    hit = [i for i, w in enumerate(cg[2]) if struct.unpack_from('<4H', w)[2] == GYM]
    assert len(hit) == 1
    objs = y['objs']
    report = cf.install(rom, source, 'ViridianGym', mid, W, H, [(w[0], w[1]) for w in y['warps']], OX, OZ, CX, CZ, AREA, TEX, MATS, None, tileset='gym',
                        coll=GYM_COLL, extra_floor=[(o['x'], o['y']) for o in objs])
    st = cf.STATE['ViridianGym']
    tiles = spin_tiles.load(source, 'ViridianGym')
    lists = spin_tiles.distinct(tiles)
    # ---- the script bank: native scripts, then the Revive pickup, then one slide per distinct arrow movement
    sid, iid, tid = struct.unpack_from('<3H', template, 6)
    bank = split_bank(scripts.files[sid])
    key, rows = decode_messages(texts.files[tid])
    assert len(rows) + 2 < 256, len(rows)
    base = len(rows)
    for line in ('{PLAYER} found REVIVE!', 'You have no room for this.'):
        rows.extend(decode_messages(encode_text([line], PH))[1])
    ball_entry = len(bank) + 1
    spin_first = ball_entry + 1
    # ---- the actors
    trainers = [o for o in objs if o['opp'] and o['sprite'] != 'SPRITE_GIOVANNI']
    natives = {struct.unpack_from('<H', a, 10)[0]: bytes(a) for a in native[1]}
    g = [[], [], [], []]
    placed = []
    for i, (o, script) in enumerate(zip(trainers, NATIVE_TRAINER_SCRIPTS)):
        a = bytearray(natives[script])
        struct.pack_into('<2H', a, 24, *cf.place('ViridianGym', o['x'], o['y']))
        struct.pack_into('<h', a, 12, FACE[o['face']])
        struct.pack_into('<H', a, 14, SIGHT[i] * cf.SCALE)
        g[1].append(bytes(a))
        placed.append(struct.unpack_from('<H', a, 0)[0])
    used_ids = {struct.unpack_from('<H', a, 0)[0] for a in native[1]}
    next_obj = max(used_ids) + 2
    for k, (o, tid_) in enumerate(zip(trainers[4:], NEW_IDS)):
        a = bytearray(actor(next_obj + k, tables[entries[k]['role']][1], 3000 + tid_ - 1, *cf.place('ViridianGym', o['x'], o['y']), facing=FACE[o['face']]))
        struct.pack_into('<H', a, 6, 1)
        struct.pack_into('<H', a, 14, SIGHT[4 + k] * cf.SCALE)
        g[1].append(bytes(a))
    others = {'SPRITE_GIOVANNI': 1, 'SPRITE_GYM_GUIDE': 2}
    for o in objs:
        if o['sprite'] in others:
            a = bytearray(natives[others[o['sprite']]])
            struct.pack_into('<2H', a, 24, *cf.place('ViridianGym', o['x'], o['y']))
            struct.pack_into('<h', a, 12, FACE[o['face']])
            g[1].append(bytes(a))
    ball = next(o for o in objs if o['item'] == 'REVIVE')
    obj = max(struct.unpack_from('<H', a, 0)[0] for a in g[1]) + 1
    g[1].append(actor(obj, 87, ball_entry, *cf.place('ViridianGym', ball['x'], ball['y']), REVIVE_FLAG, 0))
    bank.append(pickup(REVIVE, REVIVE_FLAG, base, obj))
    bank.extend(spin_tiles.script(mv, cf.SCALE) for mv in lists)
    # ---- the entry trigger of the native gym (script 4), one row inside the door
    ax, az = st['arrival'][0]
    t = struct.unpack('<Hhh5H', native[3][0])
    g[3].append(struct.pack('<Hhh5H', t[0], ax - 4, az - 1, t[3], t[4], 0, t[6], t[7]))
    for (tx_, ty_), mv in sorted(tiles.items()):
        g[3].append(struct.pack('<Hhh5H', spin_first + lists.index(mv), st['OX'] + cf.SCALE * tx_, st['OZ'] + cf.SCALE * ty_, cf.SCALE, cf.SCALE, 0, 0, TRIGGER_VAR))
    # ---- warps: one arrival per Yellow warp, then the ring tiles; both lead out to Viridian City's gym door
    for k in range(len(y['warps'])):
        ax_, az_ = st['arrival'][k]
        g[2].append(struct.pack('<4H', ax_, az_, mid, k) + bytes(4))
    for tx_, tz_, beh, wi in st['ring']:
        g[2].append(struct.pack('<4H', tx_, tz_, CITY, hit[0]) + bytes(4))
    new_event = len(events.files)
    events.files.append(events_encode(g))
    scripts.files.append(script_bank(bank))
    texts.files.append(encode_messages(key, rows))
    # ---- header: the new banks and event file
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    at = ext.table_address(rom) - o.ramAddress + 24 * (mid - ext.NATIVE_COUNT)
    struct.pack_into('<H', ovd, at + 6, len(scripts.files) - 1)
    struct.pack_into('<H', ovd, at + 10, len(texts.files) - 1)
    struct.pack_into('<H', ovd, at + 16, new_event)
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- Viridian City's gym door
    x, z, _, anchor = struct.unpack_from('<4H', cg[2][hit[0]])
    cg[2][hit[0]] = struct.pack('<4H', x, z, mid, 0) + bytes(cg[2][hit[0]][8:])
    events.files.append(events_encode(cg))
    dd = main.sections[0].data = bytearray(main.sections[0].data)
    struct.pack_into('<H', dd, TABLE + CITY * 24 + 16, len(events.files) - 1)
    rom.arm9 = main.save(compress=True)
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    return dict(id=mid, floor=report, arrows=len(tiles), slides=len(lists), trainers=len(trainers), trainers_new=NEW_IDS)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
