"""Silph Co. laid out like Yellow's: 1F-11F rebuilt from pret/pokeyellow's maps (facility tileset) at 2x scale with cave_floor.py, joined to Saffron City.

Everything gameplay-side is reused from the four stand-in clones (silph.py + silph_items.py, maps 551-554): their script banks and texts stay as they are, so the trainer records,
item pickups, the rival fight, the Lapras gift, Giovanni and the President's Master Ball work unchanged. What changes is the geometry and where things stand: Yellow's coordinates
and warps (stairs and teleport pads). The old lobby (map 402) and the clones are orphaned; Saffron's two doors now enter the new 1F.
Card Key doors: Yellow's map data holds each door block open and closes it at load; here every door block is a trigger rectangle over its two-tile-deep footprint. Walking into one without
the Card Key says Yellow's 'Darn! It needs a CARD KEY!' and steps you back; with the key it says 'Bingo! The CARD KEY opened the door!' and sets that door's own flag, after which it is open.
The Card Key (real item 876) is the 5F ball. Left out (recorded in CAMPAIGN-FIRST-PLAN.md): the elevator (stairs and pads reach every floor), Yellow's talk-only NPCs,
the Pokemon report clipboards, Jessie and James on 11F, TM Take Down.

Usage: silph_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import re
import struct
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
from hideout_yellow import TEX, MATS, AREA
from mtmoon_yellow import FACE
from forest_progression import pickup
from opening import Script, actor, encode_text, end, events_decode, events_encode, script_bank
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from silph import GROUPS, RIVAL_DONE, GIOVANNI_DONE, LOBBY
from silph_items import BALLS
from viridian_tutorial import TABLE

SAFFRON = 59
CLONES = {1: 551, 2: 552, 3: 553, 4: 554}
GROUP_OF = {floor: n for n, floors in GROUPS.items() for floor in floors} | {1: 1}
BLOCKS = {**{f: (15, 9) for f in range(1, 6)}, **{f: (13, 9) for f in range(6, 10)}, 10: (9, 8), 11: (9, 9)}
CX, CZ = 3, 2
ITEM_ID = {'HYPER_POTION': 25, 'FULL_HEAL': 27, 'MAX_REVIVE': 29, 'ESCAPE_ROPE': 78, 'PROTEIN': 46, 'HP_UP': 45, 'X_ACCURACY': 60, 'CALCIUM': 49,
           'TM_SWORDS_DANCE': 402, 'TM_EARTHQUAKE': 353, 'RARE_CANDY': 50, 'CARBOS': 48}
TRAINER_SPRITES = ('SPRITE_ROCKET', 'SPRITE_SCIENTIST', 'SPRITE_ROCKER')
CARD_KEY, DOOR_VAR = 876, 0x4179                 # the Card Key item; the door triggers' var (never written, stays 0)
# one script VARIABLE per door (0 = shut, 1 = opened). Not flags: flags 0x550 + trainer id are the trainers' defeat flags, and the old door flags 0x907-0x934 were Silph's own trainers' flags.
DOOR_FLAGS = list(range(0x4059, 0x4059 + 20))
KEY_BALL_FLAG = 0x93D                            # hides the Card Key ball once taken
STEP_UP, STEP_DOWN = 12, 13                      # movement codes: walk one step north / south


def parse(source, floor):
    text = (Path(source) / f'data/maps/objects/SilphCo{floor}F.asm').read_text()
    warps = [(int(a), int(b), c, int(d)) for a, b, c, d in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', text)]
    objs = []
    for line in re.findall(r'^\s*object_event\s+(\d+,[^\n;]+)', text, re.M):
        p = [x.strip() for x in line.split(',')]
        objs.append(dict(x=int(p[0]), y=int(p[1]), sprite=p[2], face=p[4], text=p[5], opp=len(p) > 6 and p[6].startswith('OPP_'),
                         item=p[6] if len(p) > 6 and not p[6].startswith('OPP_') else None))
    return dict(warps=warps, objs=objs)


def doors(source, floor):
    """Yellow's Card Key doors on a floor: block coordinates (x, y) from its GateCoordinates table."""
    text = (Path(source) / f'scripts/SilphCo{floor}F.asm').read_text()
    m = re.search(r'GateCoord\w*:\s*\n((?:\s*dbmapcoord[^\n]*\n)+)', text)
    return [(int(a), int(b)) for a, b in re.findall(r'dbmapcoord\s+(\d+),\s*(\d+)', m.group(1))] if m else []


def door_script(flag, z_top, base):
    s = Script().emit(96).compare(flag, 1).jump('open', 1)
    s.emit(128, CARD_KEY, 1, 0x800C).compare(0x800C, 1).jump('key', 1)
    s.msg(base)                                           # Darn! It needs a CARD KEY!
    s.emit(105, 0x4000, 0x4001).compare(0x4001, z_top).jump('from_south', 5)
    s.movement(255, 'up').emit(95)
    end(s)
    s.label('from_south').movement(255, 'down').emit(95)
    end(s)
    s.label('key').emit(41, flag, 1).msg(base + 1).emit(78, 1185).msg(base + 2).emit(79)
    end(s)
    s.label('open')
    end(s)
    s.moves('up', [(STEP_UP, 1)])
    s.moves('down', [(STEP_DOWN, 1)])
    return s.finish()


def patch(rom, source):
    y = {f: parse(source, f) for f in range(1, 12)}
    keep = {f: [(x, yy, dest, wid, i + 1) for i, (x, yy, dest, wid) in enumerate(y[f]['warps'])
                if dest != 'SILPH_CO_ELEVATOR' and not (f == 1 and i == 4)] for f in y}          # 1F's fifth warp is marked 'inaccessible'
    index = {(f, num): k for f in y for k, (*_, num) in enumerate(keep[f])}
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    olds = ext.records(rom)
    main = rom.loadArm9()
    d = main.sections[0].data
    lobby = events_decode(events.files[struct.unpack_from('<H', bytes(d[TABLE + LOBBY * 24:TABLE + LOBBY * 24 + 24]), 16)[0]])
    exit_dest = struct.unpack_from('<4H', lobby[2][0])[2:4]            # where the lobby's door led: (Saffron, its door warp)
    templates = [bytes(olds[CLONES[GROUP_OF[f]] - ext.NATIVE_COUNT]) for f in range(1, 12)]
    ids = dict(zip(range(1, 12), ext.install(rom, templates)))
    report = {}
    for f in range(1, 12):
        W, H = BLOCKS[f]
        ox, oz = (CX * 32 - 4 * W) // 2, (CZ * 32 - 4 * H) // 2
        report[f] = cf.install(rom, source, f'SilphCo{f}F', ids[f], W, H, [(w[0], w[1]) for w in keep[f]], ox, oz, CX, CZ, AREA, TEX, MATS, None,
                               tileset='facility', coll=cf.FACILITY_COLL, extra_floor=[(o['x'], o['y']) for o in y[f]['objs']])
    old_flags = {flag: item for n in BALLS for item, _, flag in BALLS[n]}
    old = {}
    for n, m in CLONES.items():
        og = events_decode(events.files[struct.unpack_from('<H', olds[m - ext.NATIVE_COUNT], 16)[0]])
        acts = [bytes(a) for a in og[1]]
        flag = lambda a: struct.unpack_from('<H', a, 8)[0]
        script = lambda a: struct.unpack_from('<H', a, 10)[0]
        old[n] = dict(trainers=[a for a in acts if script(a) >= 3000], balls={old_flags[flag(a)]: a for a in acts if flag(a) in old_flags},
                      rival=next((a for a in acts if flag(a) == RIVAL_DONE), None), giovanni=next((a for a in acts if flag(a) == GIOVANNI_DONE), None),
                      others=[a for a in acts if script(a) < 3000 and flag(a) == 0 and struct.unpack_from('<H', a, 2)[0] != 87], triggers=og[3])
    cursor = {n: 0 for n in CLONES}
    scripts_narc = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    d_doors = {f: doors(source, f) for f in range(2, 12)}
    flag_of, k = {}, 0
    for f in range(2, 12):
        for i, _ in enumerate(d_doors[f]):
            flag_of[(f, i)] = DOOR_FLAGS[k]
            k += 1
    assert k == len(DOOR_FLAGS), k
    for v in DOOR_FLAGS + [KEY_BALL_FLAG, DOOR_VAR]:            # fresh in every script and actor list of this ROM
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts_narc.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for gg in events_decode(raw) for a in gg), hex(v)
    first = {f: len(split_bank(scripts_narc.files[struct.unpack_from('<H', templates[f - 1], 6)[0]])) + 1 for f in range(1, 12)}
    new_events = {}
    for f in range(1, 12):
        name = f'SilphCo{f}F'
        st = cf.STATE[name]
        n = GROUP_OF[f]
        objs = y[f]['objs']
        g = [[], [], [], []]
        used = set()

        def put(a, pos, face):
            a = bytearray(a)
            struct.pack_into('<2H', a, 24, *cf.place(name, *pos))
            struct.pack_into('<h', a, 12, FACE[face])
            assert struct.unpack_from('<H', a, 0)[0] not in used
            used.add(struct.unpack_from('<H', a, 0)[0])
            return a
        yt = [o for o in objs if o['opp'] and o['sprite'] in TRAINER_SPRITES]
        for o in yt:
            a = old[n]['trainers'][cursor[n]]
            cursor[n] += 1
            vision = struct.unpack_from('<H', a, 14)[0]
            a = put(a, (o['x'], o['y']), o['face'])
            struct.pack_into('<H', a, 14, vision * cf.SCALE)
            g[1].append(bytes(a))
        for o in objs:
            if o['item'] in ITEM_ID:
                g[1].append(bytes(put(old[n]['balls'][ITEM_ID[o['item']]], (o['x'], o['y']), 'NONE')))
        if f == 7:
            rv = next(o for o in objs if o['sprite'] == 'SPRITE_BLUE')
            g[1].append(bytes(put(old[n]['rival'], (rv['x'], rv['y']), rv['face'])))
            lp = next(o for o in objs if o['text'] == 'TEXT_SILPHCO7F_SILPH_WORKER_M1')
            assert len(old[n]['others']) == 1
            g[1].append(bytes(put(old[n]['others'][0], (lp['x'], lp['y']), lp['face'])))
            for t in old[n]['triggers']:
                tscript, _, _, _, _, _, tvalue, tstate = struct.unpack('<Hhh5H', t)
                if tstate == 0x4176:                       # the rival's ambush: a 5x5 square of steps around him
                    g[3].append(struct.pack('<Hhh5H', tscript, st['OX'] + cf.SCALE * (rv['x'] - 2), st['OZ'] + cf.SCALE * (rv['y'] - 2),
                                            cf.SCALE * 5, cf.SCALE * 5, 0, tvalue, tstate))
            assert g[3]
        if f == 11:
            gv = next(o for o in objs if o['sprite'] == 'SPRITE_GIOVANNI')
            pr = next(o for o in objs if o['sprite'] == 'SPRITE_SILPH_PRESIDENT')
            g[1].append(bytes(put(old[n]['giovanni'], (gv['x'], gv['y']), gv['face'])))
            assert len(old[n]['others']) == 1
            g[1].append(bytes(put(old[n]['others'][0], (pr['x'], pr['y']), pr['face'])))
        for i, (bx, by) in enumerate(d_doors.get(f, [])):          # each door block's top step row: 2 steps wide, 1 step deep = 4 x 2 tiles
            rx, rz = st['OX'] + cf.SCALE * 2 * bx, st['OZ'] + cf.SCALE * 2 * by
            g[3].append(struct.pack('<Hhh5H', first[f] + i, rx, rz, cf.SCALE * 2, cf.SCALE, 0, 0, DOOR_VAR))
        if f == 5:
            kb = next(o for o in objs if o['item'] == 'CARD_KEY')
            kobj = max(used) + 1
            used.add(kobj)
            g[1].append(actor(kobj, 87, first[5] + len(d_doors[5]), *cf.place(name, kb['x'], kb['y']), KEY_BALL_FLAG, 0))
        for k, (wx, wy, dest, wid, num) in enumerate(keep[f]):
            ax, az = st['arrival'][k]
            g[2].append(struct.pack('<4H', ax, az, ids[f], k) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            dest, wid = keep[f][wi][2], keep[f][wi][3]
            if dest == 'LAST_MAP':
                dmap, anchor = exit_dest
            else:
                df = int(re.match(r'SILPH_CO_(\d+)F', dest).group(1))
                dmap, anchor = ids[df], index[(df, wid)]      # KeyError = a warp pointing at a dropped one
            g[2].append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        new_events[f] = len(events.files)
        events.files.append(events_encode(g))
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for f in range(1, 12):
        struct.pack_into('<H', ovd, start + 24 * (ids[f] - ext.NATIVE_COUNT) + 16, new_events[f])
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- the door scripts (and the 5F Card Key pickup), with their text rows, appended to each floor's own copy of its clone's bank
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    for f in range(2, 12):
        at = start + 24 * (ids[f] - ext.NATIVE_COUNT)
        bank_id, _, text_id = struct.unpack_from('<3H', ovd, at + 6)
        key, rows = decode_messages(texts.files[text_id])
        bank = split_bank(scripts.files[bank_id])
        assert len(bank) + 1 == first[f], (f, len(bank), first[f])
        lines, new = [], []
        for i, (bx, by) in enumerate(d_doors[f]):
            base = len(rows) + len(lines)
            lines += ["Darn! It needs a CARD KEY!", 'Bingo!', 'The CARD KEY opened the door!']
            new.append(door_script(flag_of[(f, i)], cf.STATE[f'SilphCo{f}F']['OZ'] + cf.SCALE * 2 * by, base))
        if f == 5:
            base = len(rows) + len(lines)
            lines += ['{PLAYER} found CARD KEY!', 'You have no room for this.']
            kobj = max(struct.unpack_from('<H', a, 0)[0] for a in events_decode(events.files[new_events[5]])[1])
            new.append(pickup(CARD_KEY, KEY_BALL_FLAG, base, kobj))
        bank.extend(new)
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
    # ---- Saffron's two Silph doors enter the new 1F
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    eid = struct.unpack_from('<H', d, TABLE + SAFFRON * 24 + 16)[0]
    g = events_decode(events.files[eid])
    hit = 0
    for i, wp in enumerate(g[2]):
        x, z, dest, anc = struct.unpack_from('<4H', wp)
        if dest == LOBBY:
            g[2][i] = struct.pack('<4H', x, z, ids[1], 0) + bytes(wp[8:])
            hit += 1
    assert hit == 2, hit
    events.files.append(events_encode(g))
    struct.pack_into('<H', d, TABLE + SAFFRON * 24 + 16, len(events.files) - 1)
    rom.setFileByName('a/0/3/2', events.save())
    rom.arm9 = main.save(compress=True)
    return dict(ids=ids, floors=report, exit=exit_dest)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
