"""Mt. Moon laid out like Yellow's: three floors (1F, B1F, B2F) rebuilt from pret/pokeyellow's maps at 2x scale (cave_floor.py), joined to Route 3 and Route 4.

Everything gameplay-side is reused from the existing build: the same trainer records, ball flags, hidden items, Super Nerd fossil boss, fossil choice and Jessie/James ambush
(trainer ids and sprites are read back out of the old maps 107/448). What changes is where things stand: Yellow's coordinates, Yellow's warps, Yellow's wild tables per floor.
Story scripts lose their walking choreography (it was written for the old geometry): the boss fights when you step next to him, the fossil choice hides the other fossil,
and the Jessie/James ambush fires as you step out of the fossil area once a fossil is taken.

Usage: mtmoon_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import json
import re
import struct
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
from build_rom import PROJECT
from escort import music
from forest_progression import SLOT_MAP, pickup
from opening import Script, actor, encode_text, end, events_decode, events_encode, script_bank, talk
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

CAVE = json.loads((PROJECT / 'data/mtmoon.json').read_text())
STORY = json.loads((PROJECT / 'data/mtmoon-story.json').read_text())
OLD_1F, OLD_B1F = 107, 448
ROUTE3, ROUTE4 = 11, 12
STAGE, CHOICE = 0x4140, 0x4141
FACE = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3, 'NONE': 1}
FLOORS = [('MtMoon1F', 20, 18, 3, 3, 8, 12), ('MtMoonB1F', 14, 14, 2, 2, 4, 4), ('MtMoonB2F', 20, 18, 3, 3, 8, 12)]        # name, W, H blocks, chunks x, z, OX, OZ
TEX = [('droad01', 'droad01_pl', 'CavFloor'), ('dwall_n', 'dwall_n_pl', 'CavWall'), ('dcliff01', 'dcliff01_pl', 'CavTop'), ('droad01_sub2', 'droad01_sub2_pl', 'CavRock')]
MATS = [('floor', 0, 'floor'), ('wall_top', 2, 'wall_top', (22, 16)), ('wall_slope', 1, 'wall_slope', (19, 13)), ('stone_top', 3, 'stone_top', (27, 20)), ('stone_side', 3, 'stone_side', (23, 17))]
VISION = 6


def parse(source, name):
    text = (Path(source) / f'data/maps/objects/{name}.asm').read_text()
    warps = [(int(a), int(b), c, int(d)) for a, b, c, d in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', text)]
    objs = []
    for line in re.findall(r'object_event\s+([^\n]+)', text):
        p = [x.strip() for x in line.split(',')]
        objs.append(dict(x=int(p[0]), y=int(p[1]), sprite=p[2], face=p[4], opp=len(p) > 6 and p[6].startswith('OPP_'), item=p[6] if len(p) > 6 and not p[6].startswith('OPP_') else None))
    bgs = [(int(a), int(b)) for a, b in re.findall(r'bg_event\s+(\d+),\s*(\d+)', text)]
    return dict(warps=warps, objs=objs, bgs=bgs)


def trainer_arg(script, which=0):
    """Trainer id inside a script (opcode 213 = TrainerBattle)."""
    i = bytes(script).find(b'\xd5\x00')
    assert i >= 0
    return struct.unpack_from('<H', script, i + 2)[0]


def boss_script(trainer, msg):
    s = Script().emit(96).compare(STAGE, 0).jump('repeat', 5).emit(104)
    s.msg(msg).emit(213, trainer, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, trainer).emit(41, STAGE, 1).msg(msg + 1).msg(msg + 2)
    end(s)
    s.label('repeat').compare(STAGE, 1).jump('research', 5).msg(msg + 2)
    end(s)
    s.label('research').msg(msg + 3)
    end(s)
    s.label('lost').emit(219)
    end(s)
    return s.finish()


def fossil_script(f, other, msg):
    s = Script().emit(96).compare(STAGE, 0).jump('unbeaten', 1)
    s.compare(STAGE, 1).jump('done', 5)
    s.msg(msg).emit(63, 0x800C).compare(0x800C, 0).jump('done', 5)
    s.emit(125, f['item'], 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    s.emit(41, CHOICE, f['choice']).emit(41, STAGE, 2)
    s.emit(30, f['hide_flag']).emit(101, f['actor'])
    s.emit(78, 1185).msg(msg + 1).emit(79)
    s.msg(msg + 2)
    s.emit(30, other['hide_flag']).emit(101, other['actor'])
    end(s)
    s.label('full').msg(msg + 3)
    end(s)
    s.label('unbeaten').msg(msg + 4)
    s.label('done')
    end(s)
    return s.finish()


def ambush_script(trainer, msg, hide_j, hide_m, jessie, james):
    s = Script().compare(STAGE, 2).jump('done', 5).emit(96)
    music(s, 1112).msg(msg).msg(msg + 1)
    s.emit(213, trainer, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, trainer)
    music(s, 1112).msg(msg + 2).msg(msg + 3)
    s.emit(30, hide_m).emit(101, james).emit(30, hide_j).emit(101, jessie)
    s.emit(41, STAGE, 3).emit(81, 0).emit(82)
    end(s)
    s.label('lost').emit(219)
    end(s)
    s.label('done').emit(2)
    return s.finish()


def msgs(*keys):
    return [CAVE['messages'][k] for k in keys]


def patch(rom, source):
    y = {name: parse(source, name) for name, *_ in FLOORS}
    main = rom.loadArm9()
    d = main.sections[0].data
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    wild = ndspy.narc.NARC(rom.getFileByName('a/0/3/7'))
    # ---- what the old two-floor build already knows
    old = {}
    for m in (OLD_1F, OLD_B1F):
        g = events_decode(events.files[struct.unpack_from('<H', d, TABLE + m * 24 + 16)[0]])
        old[m] = dict(g=g, bank=split_bank(bytes(scripts.files[struct.unpack_from('<H', d, TABLE + m * 24 + 6)[0]])), wild=d[TABLE + m * 24])
    by_obj = {}
    for m in old:
        for a in old[m]['g'][1]:
            by_obj[struct.unpack_from('<H', a, 0)[0]] = bytes(a)
    boss_trainer = trainer_arg(old[OLD_1F]['bank'][6])           # script 7: the Super Nerd fossil boss
    jj_trainer = trainer_arg(old[OLD_1F]['bank'][12])            # script 13: the Jessie/James ambush
    # ---- install three header records cloned from the old 1F record and lay the floors out
    template = ext.native_record(rom, OLD_1F)
    ids = ext.install(rom, [template, template, template])
    ref = source
    report = {}
    for (name, W, H, CX, CZ, OX, OZ), mid in zip(FLOORS, ids):
        report[name] = cf.install(rom, ref, name, mid, W, H, [(w[0], w[1]) for w in y[name]['warps']], OX, OZ, CX, CZ, 70, TEX, MATS, None)
    fid = dict(zip(('MT_MOON_1F', 'MT_MOON_B1F', 'MT_MOON_B2F'), ids))
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    # ---- events, scripts, texts per floor
    new_files = {}
    def tile(name, x, yy):
        return cf.place(name, x, yy)

    def clone_actor(obj, name, pos, face, new_obj, vision=None):
        a = bytearray(by_obj[obj])
        struct.pack_into('<H', a, 0, new_obj)
        struct.pack_into('<2H', a, 24, *tile(name, *pos))
        struct.pack_into('<h', a, 12, FACE[face])
        if vision is not None:
            struct.pack_into('<H', a, 14, vision)
        return bytes(a)

    def warps_for(name):
        out = []
        st = cf.STATE[name]
        for i, (x, yy, dest, wid) in enumerate(y[name]['warps']):
            ax, az = st['arrival'][i]
            out.append(struct.pack('<4H', ax, az, ids[[n for n, *_ in FLOORS].index(name)], i) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            x, yy, dest, wid = y[name]['warps'][wi]
            if dest == 'LAST_MAP':
                dmap, anchor = (ROUTE3 if name == 'MtMoon1F' else ROUTE4), 0
            else:
                dmap, anchor = fid[dest], wid - 1
            out.append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        return out

    wild_floor = {'MtMoon1F': '1F', 'MtMoonB1F': 'B1F', 'MtMoonB2F': 'B2F'}
    # 1F -----------------------------------------------------------------
    for name in ('MtMoon1F', 'MtMoonB1F', 'MtMoonB2F'):
        objs, g = y[name]['objs'], [[], [], [], []]
        lines, bank = [], []
        if name == 'MtMoon1F':
            lines.append(CAVE['messages']['MtMoon1FBewareZubatSign'])
            bank.append(talk(0))
            st = cf.STATE[name]
            bx, by = y[name]['bgs'][0]                                   # the sign stands on a rock step: a sign event on each of its four tiles
            for ddx in range(cf.SCALE):
                for ddz in range(cf.SCALE):
                    g[0].append(struct.pack('<HHiiiH2x', 1, 0, st['OX'] + cf.SCALE * bx + ddx, st['OZ'] + cf.SCALE * by + ddz, 0, 4))
            trainers = [o for o in objs if o['opp']]
            for i, o in enumerate(trainers):
                g[1].append(clone_actor(i, name, (o['x'], o['y']), o['face'], i, VISION))
            balls = [o for o in objs if o['item']]
            pk = {p['item']: p for p in CAVE['pickups']}
            water_gun = dict(item=116, name='TM12 (WATER GUN)', flag=0xB36, actor=25)
            potions = [p for p in CAVE['pickups'] if p['item'] == 17]
            order = {'POTION': iter(potions), 'MOON_STONE': iter([pk[81]]), 'RARE_CANDY': iter([pk[50]]), 'ESCAPE_ROPE': iter([pk[78]]), 'TM_WATER_GUN': iter([water_gun])}
            for o in balls:
                p = next(order[o['item']])
                idx = len(lines)
                lines.extend([f"You found a {p['name']}!", 'Your BAG is full. Make some room and come back.'])
                bank.append(pickup(p['item'], p['flag'], idx, p['actor']))
                g[1].append(actor(p['actor'], 87, len(bank), *tile(name, o['x'], o['y']), p['flag'], 0))
        elif name == 'MtMoonB2F':
            rockets = [o for o in objs if o['opp'] and o['sprite'] == 'SPRITE_ROCKET']
            for i, o in enumerate(rockets):
                g[1].append(clone_actor(7 + i, name, (o['x'], o['y']), o['face'], 7 + i, VISION))
            # visible balls
            for o, p in zip([o for o in objs if o['item']], [dict(item=45, name='HP UP', flag=0xB35, actor=24), dict(item=117, name='TM01 (MEGA PUNCH)', flag=0xB38, actor=26)]):
                idx = len(lines)
                lines.extend([f"You found a {p['name']}!", 'Your BAG is full. Make some room and come back.'])
                bank.append(pickup(p['item'], p['flag'], idx, p['actor']))
                g[1].append(actor(p['actor'], 87, len(bank), *tile(name, o['x'], o['y']), p['flag'], 0))
            # hidden items (Yellow's two on B2F)
            hid = [(8198, 18, 12), (8195, 33, 9)]
            for sid, hx, hz in hid:
                st = cf.STATE[name]
                for ddx in range(cf.SCALE):          # Yellow's hidden items sit on one step: an event on each of its four tiles (they share the found flag)
                    for ddz in range(cf.SCALE):
                        g[0].append(struct.pack('<HHiiiH2x', sid, 2, st['OX'] + cf.SCALE * hx + ddx, st['OZ'] + cf.SCALE * hz + ddz, 0, 4))
            # boss + fossils + Jessie/James
            boss = STORY['fossil_boss']
            base = len(lines)
            lines.extend(msgs('MtMoonB2FSuperNerdTheyreBothMineText', 'MtMoonB2FSuperNerdOkIllShareText', 'MtMoonB2fSuperNerdEachTakeOneText', 'MtMoonB2FSuperNerdTheresAPokemonLabText'))
            bank.append(boss_script(boss_trainer, base))
            boss_entry = len(bank)
            sup = next(o for o in objs if o['sprite'] == 'SPRITE_SUPER_NERD' and o['opp'])
            g[1].append(clone_actor(boss['actor'], name, (sup['x'], sup['y']), sup['face'], boss['actor']) )
            a = bytearray(g[1][-1]); struct.pack_into('<H', a, 10, boss_entry); g[1][-1] = bytes(a)
            fossils = STORY['fossils']
            fossil_objs = [o for o in objs if o['sprite'] == 'SPRITE_FOSSIL']
            for f, other, o in zip(fossils, fossils[::-1], fossil_objs):
                m0 = len(lines)
                lines.extend([CAVE['messages'][f"MtMoonB2F{f['name'].split()[0].title()}FossilYouWantText"], '{PLAYER} got the ' + f['name'] + '!',
                              CAVE['messages']['MtMoonB2FSuperNerdThenThisIsMineText'], CAVE['messages']['MtMoonB2FYouHaveNoRoomText'], CAVE['messages']['MtMoonB2FSuperNerdTheyreBothMineText']])
                bank.append(fossil_script(f, other, m0))
                fa = bytearray(by_obj[f['actor']])
                struct.pack_into('<2H', fa, 24, *tile(name, o['x'], o['y']))
                struct.pack_into('<H', fa, 10, len(bank))
                g[1].append(bytes(fa))
            # Jessie and James
            jm = len(lines)
            lines.extend(msgs('MtMoonJessieJamesText1', 'MtMoonJessieJamesText2', 'MtMoonJessieJamesText3', 'MtMoonJessieJamesText4'))
            jj_objs = [o for o in objs if o['sprite'] in ('SPRITE_JESSIE', 'SPRITE_JAMES')]
            HIDE_J, HIDE_M, JESSIE, JAMES = 0xB33, 0xB34, 30, 31
            bank.append(ambush_script(jj_trainer, jm, HIDE_J, HIDE_M, JESSIE, JAMES))
            amb = len(bank)
            bank.append(Script().emit(96).emit(104).msg(jm).emit(97).emit(2).finish())
            stand = len(bank)
            for obj_id, o in zip((JESSIE, JAMES), jj_objs):
                ja = bytearray(by_obj[obj_id])
                struct.pack_into('<2H', ja, 24, *tile(name, o['x'], o['y']))
                struct.pack_into('<H', ja, 10, stand)
                struct.pack_into('<h', ja, 12, FACE[o['face']])
                g[1].append(bytes(ja))
            # triggers: the boss fights when you step next to him; the ambush fires inside the fossil area once a fossil is taken
            def rect(x0, z0, w, h):
                st = cf.STATE[name]
                return st['OX'] + cf.SCALE * x0, st['OZ'] + cf.SCALE * z0, cf.SCALE * w, cf.SCALE * h
            g[3].append(struct.pack('<Hhh5H', boss_entry, *rect(13, 8, 1, 1), 0, 0, STAGE))
            g[3].append(struct.pack('<Hhh5H', amb, *rect(11, 5, 4, 4), 0, 2, STAGE))
        lines = lines or ['...']
        bank = bank or [talk(0)]
        sid = len(scripts.files); scripts.files.append(script_bank(bank))
        iid = len(scripts.files); scripts.files.append(bytes(4))
        tid = len(texts.files); texts.files.append(encode_text(lines, PH))
        g[2] = warps_for(name)
        eid = len(events.files); events.files.append(events_encode(g))
        # wild table cloned from the old floor's record
        w = bytearray(wild.files[old[OLD_1F]['wild']])
        slots = [CAVE['wild_slots'][wild_floor[name]][i] for i in SLOT_MAP]
        w[0], w[1:6] = CAVE['encounter_rate'], bytes(5)
        w[8:20] = bytes(p['level'] for p in slots)
        species = [p['species'] for p in slots]
        for period in range(3):
            struct.pack_into('<12H', w, 20 + 24 * period, *species)
        for at in (0x5C, 0x60, 0x64, 0x68, 0xBC):
            struct.pack_into('<2H', w, at, species[0], species[1])
        wid = len(wild.files); assert wid < 255
        wild.files.append(bytes(w))
        new_files[name] = dict(script=sid, init=iid, text=tid, event=eid, wild=wid)
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    rom.setFileByName('a/0/3/7', wild.save())
    # ---- header records
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for (name, *_), mid in zip(FLOORS, ids):
        at = start + 24 * (mid - ext.NATIVE_COUNT)
        nf = new_files[name]
        struct.pack_into('<3H', ovd, at + 6, nf['script'], nf['init'], nf['text'])
        struct.pack_into('<H', ovd, at + 16, nf['event'])
        ovd[at] = nf['wild']
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- Route 3 / Route 4 enter the new floors
    rewired = {}
    for m, old_anchor, target, anchor in ((ROUTE3, 0, fid['MT_MOON_1F'], 0), (ROUTE4, 1, fid['MT_MOON_B1F'], 7)):
        eid = struct.unpack_from('<H', d, TABLE + m * 24 + 16)[0]
        g = events_decode(events.files[eid])
        hit = 0
        for i, wp in enumerate(g[2]):
            x, z, dest, anc = struct.unpack_from('<4H', wp)
            if dest == OLD_1F:
                g[2][i] = struct.pack('<4H', x, z, target, anchor) + bytes(wp[8:])
                hit += 1
        assert hit == 1, (m, hit)
        events.files.append(events_encode(g))
        struct.pack_into('<H', d, TABLE + m * 24 + 16, len(events.files) - 1)
        rewired[m] = (target, anchor)
    rom.setFileByName('a/0/3/2', events.save())
    rom.arm9 = main.save(compress=True)
    return dict(ids=ids, floors=report, files=new_files, rewired=rewired, boss_trainer=boss_trainer, jj_trainer=jj_trainer)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
