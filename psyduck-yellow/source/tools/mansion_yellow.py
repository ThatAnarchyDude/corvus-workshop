"""Pokemon Mansion (Yellow's Cinnabar Mansion) rebuilt from pret/pokeyellow's maps: 1F, 2F, 3F and B1F as four extension maps (cave_floor.py, 2x scale), reached from Cinnabar Island.

What the puzzle is, as Yellow has it: statues hide switches (press = a yes/no question); one switch state toggles every gate of the building at once (1F 4 gates, 2F 3, 3F 2, B1F 4);
3F has three holes that drop you to 1F or 2F; the SECRET KEY lies on B1F and opens Cinnabar's gym door.
Here: the gate blocks are plain floor in the 3D map and each gate is a trigger over its block (closed -> the player is stepped back, silent, like a wall); the switch state is one script
variable (reset when you walk in from Cinnabar, as Yellow resets its event); the gym door (Seafoam's gym, map 146) checks for the Secret Key (real item 872).
Cinnabar Island's own exterior (map 57) has only the Pokemon Center, so the Mansion's door is a step trigger on the ruins beside it.

State is in script variables and a few free flags (see SESSION-HANDOFF.md: persistent flags are nearly gone; a trainer's defeat flag is 0x550 + its id).

Usage: mansion_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
import route_progression as rp
import trainer_alloc
import yellow_route_reference as yellow_ref
import yellow_text
from forest_progression import SLOT_MAP, pickup
from hideout_yellow import AREA, CX, CZ, MATS, OX, OZ, TEX
from mtmoon_yellow import FACE, parse
from opening import Script, actor, encode_text, end, events_decode, events_encode, script_bank
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

NAMES = {1: 'PokemonMansion1F', 2: 'PokemonMansion2F', 3: 'PokemonMansion3F', 4: 'PokemonMansionB1F'}
DEST_FLOOR = {'POKEMON_MANSION_1F': 1, 'POKEMON_MANSION_2F': 2, 'POKEMON_MANSION_3F': 3, 'POKEMON_MANSION_B1F': 4}
BLOCKS = {1: (15, 14), 2: (15, 14), 3: (15, 9), 4: (15, 14)}
EMPTY = 0x0e
CINNABAR, SEAFOAM = 57, 146
ENTRY, EXIT_ARRIVAL = (1032, 503), (1032, 506)       # the step trigger on Cinnabar's ruins, and where leaving the Mansion puts you
GYM_DOOR = ((55, 23), (55, 24))                      # Seafoam cave tiles whose warps lead into Blaine's gym (map 457)
SECRET_KEY = 872
TM_BLIZZARD, TM_SOLARBEAM = 341, 349
# gate blocks per floor: (block y, block x, switch value at which the gate is CLOSED); pokeyellow's Mansion*CheckReplaceSwitchDoorBlocks
GATES = {1: [(3, 8, 0), (8, 10, 0), (13, 13, 0), (6, 12, 1)],
         2: [(2, 4, 1), (4, 9, 0), (11, 3, 0)],
         3: [(2, 7, 1), (5, 7, 0)],
         4: [(8, 13, 1), (11, 6, 1), (3, 4, 0), (8, 8, 0)]}
STATUES = {1: [(2, 5)], 2: [(2, 11)], 3: [(10, 5)], 4: [(20, 3), (18, 25)]}                 # hidden_events.asm: the switches
DIARIES = {2: [((18, 2), '_PokemonMansion2FDiary1Text'), ((3, 22), '_PokemonMansion2FDiary2Text')], 3: [((6, 12), '_PokemonMansion3FDiaryText')],
           4: [((16, 20), '_PokemonMansionB1FDiaryText')]}
HOLES = [((16, 14), 1, (16, 14)), ((17, 14), 1, (16, 14)), ((19, 14), 2, (18, 14))]         # 3F step -> (floor, arrival step); pokeyellow DungeonWarpList
HIDDEN = {3: ((1, 9), 'MAX_REVIVE'), 4: ((1, 9), 'RARE_CANDY')}
ITEM_ID = {'ESCAPE_ROPE': 78, 'CARBOS': 48, 'CALCIUM': 49, 'MAX_POTION': 24, 'IRON': 47, 'RARE_CANDY': 50, 'FULL_RESTORE': 23, 'MAX_REVIVE': 29,
           'TM_BLIZZARD': TM_BLIZZARD, 'TM_SOLARBEAM': TM_SOLARBEAM, 'SECRET_KEY': SECRET_KEY}
ITEM_NAME = {'ESCAPE_ROPE': 'ESCAPE ROPE', 'CARBOS': 'CARBOS', 'CALCIUM': 'CALCIUM', 'MAX_POTION': 'MAX POTION', 'IRON': 'IRON', 'RARE_CANDY': 'RARE CANDY',
             'FULL_RESTORE': 'FULL RESTORE', 'MAX_REVIVE': 'MAX REVIVE', 'TM_BLIZZARD': 'TM14', 'TM_SOLARBEAM': 'TM22', 'SECRET_KEY': 'SECRET KEY'}
# State (checked fresh against every script bank and actor list below). Flags: hide flags of the balls and the defeat flags (0x550 + id) of the trainers.
BALL_FLAGS = {'ESCAPE_ROPE': 0x954, 'CARBOS': 0x95C, 'CALCIUM': 0x960, 'MAX_POTION': 0x968, 'IRON': 0x970, 'RARE_CANDY': 0x974, 'FULL_RESTORE': 0x97C,
              'TM_BLIZZARD': 0x98C, 'TM_SOLARBEAM': 0x99C, 'SECRET_KEY': 0x9A0}
TRAINER_IDS = [999, 1003, 1004, 1007, 1020, 1024]           # defeat flags 0x937, 0x93B, 0x93C, 0x93F, 0x94C, 0x950
SWITCH_VAR, HIDDEN_VARS, TRIGGER_VAR = 0x406D, {3: 0x406E, 4: 0x406F}, 0x4179     # the trigger var is never written (stays 0)
UP, DOWN, LEFT, RIGHT = 12, 13, 14, 15


def flat(source, file, label):
    return yellow_text.message(source, file, label).rstrip('@')


class Floor:
    """Script bank and text bank of one floor, appended to as the floor is built (scripts are 1-based entries, text rows 0-based)."""

    def __init__(self):
        self.bank, self.rows = [], []
        self.key = decode_messages(encode_text(['x'], PH))[0]

    def text(self, *lines):
        first = len(self.rows)
        for line in lines:
            self.rows.extend(decode_messages(encode_text([line], PH))[1])
        return first

    def script(self, data):
        self.bank.append(data)
        return len(self.bank)


def gate_script(var, closed_when, axis, edge):
    """Silent step-back at a closed gate. axis 'ns': edge = z of the block's top row; 'ew': edge = x of its left column."""
    s = Script().emit(96).compare(var, closed_when).jump('shut', 1)
    end(s)
    s.label('shut').emit(105, 0x4000, 0x4001)
    if axis == 'ns':
        s.compare(0x4001, edge).jump('far', 5)
        s.movement(255, 'up').emit(95)
        end(s)
        s.label('far').movement(255, 'down').emit(95)
    else:
        s.compare(0x4000, edge).jump('far', 5)
        s.movement(255, 'left').emit(95)
        end(s)
        s.label('far').movement(255, 'right').emit(95)
    end(s)
    s.moves('up', [(UP, 1)]).moves('down', [(DOWN, 1)]).moves('left', [(LEFT, 1)]).moves('right', [(RIGHT, 1)])
    return s.finish()


def switch_script(var, ask, pressed, not_pressed):
    s = Script().emit(96).msg(ask).emit(63, 0x800C).compare(0x800C, 0).jump('yes', 1)
    s.msg(not_pressed)
    end(s)
    s.label('yes').msg(pressed).compare(var, 0).jump('on', 1)
    s.emit(41, var, 0)
    end(s)
    s.label('on').emit(41, var, 1)
    end(s)
    return s.finish()


def text_script(msg):
    s = Script().emit(96).msg(msg)
    end(s)
    return s.finish()


def drop_script(dest_map, x, z):
    s = Script().emit(96)
    s.emit(174, 6, 6, 0, 0).emit(175).emit(176, dest_map, 0, x, z, 1).emit(174, 6, 6, 1, 0).emit(175)
    s.emit(97).emit(2)
    return s.finish()


def hidden_script(item, var, base):
    s = Script().emit(96).compare(var, 1).jump('done', 1)
    s.emit(125, item, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    s.emit(41, var, 1).emit(78, 1185).msg(base).emit(79)
    end(s)
    s.label('full').msg(base + 1)
    end(s)
    s.label('done')
    end(s)
    return s.finish()


def corridor_axis(walk, bx, by):
    """'ns' if the gate block's open neighbours are north and south, else 'ew' (the walkable steps beside the 2x2-step block)."""
    h, w = len(walk), len(walk[0])
    ok = lambda sx, sy: 0 <= sx < w and 0 <= sy < h and walk[sy][sx]
    n = ok(2 * bx, 2 * by - 1) or ok(2 * bx + 1, 2 * by - 1)
    s = ok(2 * bx, 2 * by + 2) or ok(2 * bx + 1, 2 * by + 2)
    e = ok(2 * bx + 2, 2 * by) or ok(2 * bx + 2, 2 * by + 1)
    wv = ok(2 * bx - 1, 2 * by) or ok(2 * bx - 1, 2 * by + 1)
    return 'ns' if (n and s) or not (e and wv) else 'ew'


def fresh(rom, values):
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    for v in values:
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for g in events_decode(raw) for a in g), hex(v)


def append_to_native(rom, map_id, make, lines):
    """Add scripts and text rows to a native map's own banks. make(first entry (1-based), first new text row) -> the new scripts. -> the entries' first number"""
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    rec = TABLE + map_id * 24
    sid, _, tid = struct.unpack_from('<3H', d, rec + 6)
    bank = split_bank(scripts.files[sid])
    first = len(bank) + 1
    key, rows = decode_messages(texts.files[tid])
    if tid == 3:           # the shared common bank (2769 rows, 128 maps): messages are 8-bit indices, so a map that only borrows it gets its own small bank instead
        assert len(bank) <= 1, 'this map has scripts of its own that may show common messages'
        key, rows = decode_messages(encode_text(['x'], PH))[0], []
    base = len(rows)
    for line in lines:
        rows.extend(decode_messages(encode_text([line], PH))[1])
    scripts.files.append(script_bank(bank + list(make(first, base))))
    texts.files.append(encode_messages(key, rows))
    struct.pack_into('<H', d, rec + 6, len(scripts.files) - 1)
    struct.pack_into('<H', d, rec + 10, len(texts.files) - 1)
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    rom.arm9 = main.save(compress=True)
    return first


def add_event_rows(rom, map_id, warps=(), triggers=(), expect_warps=None):
    """Copy a native map's event file with extra warp rows and trigger rows appended; repoint its header."""
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    rec = TABLE + map_id * 24 + 16
    g = events_decode(events.files[struct.unpack_from('<H', d, rec)[0]])
    if expect_warps is not None:
        assert len(g[2]) == expect_warps, (map_id, len(g[2]))
    g[2].extend(warps)
    g[3].extend(triggers)
    events.files.append(events_encode(g))
    struct.pack_into('<H', d, rec, len(events.files) - 1)
    rom.setFileByName('a/0/3/2', events.save())
    rom.arm9 = main.save(compress=True)


def patch(rom, source):
    y = {f: parse(source, NAMES[f]) for f in NAMES}
    fresh(rom, list(BALL_FLAGS.values()) + [0x550 + t for t in TRAINER_IDS] + [SWITCH_VAR, *HIDDEN_VARS.values()])
    refs = {}
    for f in NAMES:
        scripts_txt = (open(f'{source}/scripts/{NAMES[f]}.asm')).read()
        heads = re.findall(r'trainer EVENT_BEAT_\w+_TRAINER_(\d+),', scripts_txt)
        refs[f] = yellow_ref.reference(source, NAMES[f], len(heads), extra_roles={'OPP_BURGLAR': 'Burglar', 'OPP_SCIENTIST': 'Scientist'}, wild=True,
                                       first_index=int(heads[0]) if heads else 0)
    # ---- trainers: Yellow's six, at chosen ids
    tables = rp.class_tables(rom)
    entries = [t for f in NAMES for t in refs[f]['trainers']]
    assert len(entries) == len(TRAINER_IDS), len(entries)
    trainer_alloc.add(rom, entries, TRAINER_IDS, {r: tables[r][0] for r in ('Burglar', 'Scientist')})
    tid_of = dict(zip([(f, i) for f in NAMES for i in range(len(refs[f]['trainers']))], TRAINER_IDS))
    # ---- the four floors
    olds = ext.records(rom)
    template = bytes(olds[560 - ext.NATIVE_COUNT])
    ids = dict(zip(NAMES, ext.install(rom, [template] * 4)))
    report, edits = {}, {}
    for f in NAMES:
        W, H = BLOCKS[f]
        edits[f] = {(bx, by): EMPTY for by, bx, _ in GATES[f]}
        report[f] = cf.install(rom, source, NAMES[f], ids[f], W, H, [(w[0], w[1]) for w in y[f]['warps']], OX, OZ, CX, CZ, AREA, TEX, MATS, None, tileset='facility',
                               coll=cf.FACILITY_COLL, extra_floor=[(o['x'], o['y']) for o in y[f]['objs'] if o['sprite'] == 'SPRITE_POKE_BALL' or o['sprite'] == 'SPRITE_POKEDEX'], edits=edits[f])
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts_narc = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts_narc = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    wild = ndspy.narc.NARC(rom.getFileByName('a/0/3/7'))
    wild_template = bytes(wild.files[template[0]] if template[0] != 255 else wild.files[0])
    switch_lines = [flat(source, 'PokemonMansion2F', '_PokemonMansion2F' + k) for k in ('SwitchText', 'SwitchPressedText', 'SwitchNotPressedText')]
    switch_lines[0] = switch_lines[0].replace('\x00', '')
    sprites = {r: tables[r][1] for r in ('Burglar', 'Scientist')}
    new_events, new_scripts, new_texts, new_wild = {}, {}, {}, {}
    for f in NAMES:
        name, st = NAMES[f], cf.STATE[NAMES[f]]
        floor = Floor()
        g = [[], [], [], []]
        used = set()
        # trainers
        for i, t in enumerate(refs[f]['trainers']):
            a = bytearray(actor(len(used), sprites[t['role']], 3000 + tid_of[(f, i)] - 1, *cf.place(name, *t['yellow_position']), facing=FACE.get(t['facing'], FACE['LEFT'] if 'LEFT' in t['facing'] else 1)))
            struct.pack_into('<H', a, 6, 1)
            struct.pack_into('<H', a, 14, t['vision'] * cf.SCALE)
            used.add(len(used))
            g[1].append(bytes(a))
        # item balls
        for o in y[f]['objs']:
            if o['item']:
                obj = len(used)
                used.add(obj)
                base = floor.text('{PLAYER} found %s!' % ITEM_NAME[o['item']], 'You have no room for this.')
                entry = floor.script(pickup(ITEM_ID[o['item']], BALL_FLAGS[o['item']], base, obj))
                g[1].append(actor(obj, 87, entry, *cf.place(name, o['x'], o['y']), BALL_FLAGS[o['item']], 0))
        # statues (switches), diaries and hidden items: talk events over the 2x2 tiles of the step
        def talk(entry, xy, rows=(1,)):
            for ddz in rows:
                for ddx in range(cf.SCALE):
                    g[0].append(struct.pack('<HHiiiH2x', entry, 0, st['OX'] + cf.SCALE * xy[0] + ddx, st['OZ'] + cf.SCALE * xy[1] + ddz, 0, 4))
        ask = floor.text(*switch_lines)
        sw = floor.script(switch_script(SWITCH_VAR, ask, ask + 1, ask + 2))
        for xy in STATUES[f]:
            talk(sw, xy)
        for xy, label in DIARIES.get(f, []):
            msg = floor.text(flat(source, NAMES[f], label))
            talk(floor.script(text_script(msg)), xy, rows=range(cf.SCALE))
        if f in HIDDEN:
            xy, item = HIDDEN[f]
            base = floor.text('{PLAYER} found %s!' % ITEM_NAME[item], 'You have no room for this.')
            talk(floor.script(hidden_script(ITEM_ID[item], HIDDEN_VARS[f], base)), xy, rows=range(cf.SCALE))
        # gates: one trigger over each gate block
        _, walk = cf.load(source, name, *BLOCKS[f], 'facility', cf.FACILITY_COLL, edits[f])
        for by, bx, closed in GATES[f]:
            axis = corridor_axis(walk, bx, by)
            x0, z0 = st['OX'] + cf.SCALE * 2 * bx, st['OZ'] + cf.SCALE * 2 * by
            entry = floor.script(gate_script(SWITCH_VAR, closed, axis, z0 if axis == 'ns' else x0))
            g[3].append(struct.pack('<Hhh5H', entry, x0, z0, cf.SCALE * 2, cf.SCALE * 2, 0, 0, TRIGGER_VAR))
        # the holes on 3F
        if f == 3:
            for (hx, hy), to, (ax, ay) in HOLES:
                dx, dz = cf.place(NAMES[to], ax, ay)
                entry = floor.script(drop_script(ids[to], dx, dz))
                g[3].append(struct.pack('<Hhh5H', entry, st['OX'] + cf.SCALE * hx, st['OZ'] + cf.SCALE * hy, cf.SCALE, cf.SCALE, 0, 0, TRIGGER_VAR))
        # warps: arrivals first, then the ring tiles
        for k, (wx, wy, dest, wid) in enumerate(y[f]['warps']):
            ax, az = st['arrival'][k]
            g[2].append(struct.pack('<4H', ax, az, ids[f], k) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            dest, wid = y[f]['warps'][wi][2], y[f]['warps'][wi][3]
            if dest == 'LAST_MAP':
                dmap, anchor = CINNABAR, 1
            else:
                dmap, anchor = ids[DEST_FLOOR[dest]], wid - 1
            g[2].append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        new_events[f] = len(events.files)
        events.files.append(events_encode(g))
        # banks
        new_scripts[f] = len(scripts_narc.files)
        scripts_narc.files.append(script_bank(floor.bank))
        new_texts[f] = len(texts_narc.files)
        texts_narc.files.append(encode_messages(floor.key, floor.rows))
        # wild encounters (Yellow's grass table)
        ref = refs[f]
        if ref.get('grass') and ref.get('grass_rate'):
            row = bytearray(wild_template)
            row[:6] = bytes([ref['grass_rate'], 0, 0, 0, 0, 0])
            slots = [ref['grass'][i] for i in SLOT_MAP]
            row[8:20] = bytes(p['level'] for p in slots)
            for period in range(3):
                struct.pack_into('<12H', row, 20 + 24 * period, *(p['species'] for p in slots))
            for at in (0x5C, 0x60, 0x64, 0x68, 0xBC):
                struct.pack_into('<2H', row, at, slots[0]['species'], slots[1]['species'])
            assert len(wild.files) < 255
            new_wild[f] = len(wild.files)
            wild.files.append(bytes(row))
        else:
            new_wild[f] = 255
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/1/2', scripts_narc.save())
    rom.setFileByName('a/0/2/7', texts_narc.save())
    rom.setFileByName('a/0/3/7', wild.save())
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for f in NAMES:
        at = start + 24 * (ids[f] - ext.NATIVE_COUNT)
        ovd[at] = new_wild[f]
        struct.pack_into('<H', ovd, at + 6, new_scripts[f])
        struct.pack_into('<H', ovd, at + 10, new_texts[f])
        struct.pack_into('<H', ovd, at + 16, new_events[f])
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- Cinnabar Island (map 57): the door on the ruins, and the arrival tile for people leaving
    st1 = cf.STATE[NAMES[1]]
    arrive = st1['arrival'][[k for k, w in enumerate(y[1]['warps']) if w[2] == 'LAST_MAP'][0]]

    def enter_script(first, base):
        s = Script().emit(96).emit(41, SWITCH_VAR, 0)
        s.emit(174, 6, 6, 0, 0).emit(175).emit(176, ids[1], 0, arrive[0], arrive[1], 1).emit(174, 6, 6, 1, 0).emit(175)
        s.emit(97).emit(2)
        return [s.finish()]
    first = append_to_native(rom, CINNABAR, enter_script, [])
    add_event_rows(rom, CINNABAR, warps=[struct.pack('<4H', EXIT_ARRIVAL[0], EXIT_ARRIVAL[1], CINNABAR, 1) + bytes(4)],
                   triggers=[struct.pack('<Hhh5H', first, ENTRY[0], ENTRY[1], 2, 1, 0, 0, TRIGGER_VAR)], expect_warps=1)
    # ---- the gym door in the Seafoam cave: no SECRET KEY, no way in (the tiles beside the door turn you back)
    locked = flat(source, 'CinnabarIsland', '_CinnabarIslandDoorIsLockedText')
    sides = [((GYM_DOOR[0][0] - 1, GYM_DOOR[0][1]), LEFT), ((GYM_DOOR[1][0] - 1, GYM_DOOR[1][1]), LEFT),
             ((GYM_DOOR[0][0] + 1, GYM_DOOR[0][1]), RIGHT), ((GYM_DOOR[1][0] + 1, GYM_DOOR[1][1]), RIGHT),
             ((GYM_DOOR[0][0], GYM_DOOR[0][1] - 1), UP), ((GYM_DOOR[1][0], GYM_DOOR[1][1] + 1), DOWN)]

    def lock_scripts(first, base):
        out = []
        for _, code in sides:
            s = Script().emit(96).emit(128, SECRET_KEY, 1, 0x800C).compare(0x800C, 1).jump('open', 1).msg(base)
            s.movement(255, 'back').emit(95)
            end(s)
            s.label('open')
            end(s)
            s.moves('back', [(code, 1)])
            out.append(s.finish())
        return out
    first = append_to_native(rom, SEAFOAM, lock_scripts, [locked])
    add_event_rows(rom, SEAFOAM, triggers=[struct.pack('<Hhh5H', first + k, xy[0], xy[1], 1, 1, 0, 0, TRIGGER_VAR) for k, (xy, _) in enumerate(sides)])
    return dict(ids=ids, trainers=TRAINER_IDS, floors=report, wild=new_wild)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
