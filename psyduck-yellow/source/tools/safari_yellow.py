"""Safari Zone (Center, East, North, West) rebuilt from pret/pokeyellow's maps (forest tileset, Kanto-outdoor textures), entered from Fuchsia City, with Yellow's wild tables, item balls, the Gold Teeth and the
secret-house Fishing Guru (HM03 Surf).

HG has no Safari game for Kanto, so this is a free-roam park (no fee, no step limit, normal Poke Balls). Yellow's rest houses and secret house are not built as rooms: the Fishing Guru stands in the
West area near where the secret house's door was. Yellow's TM Egg Bomb and TM Skull Bash do not exist in this ROM and are left out.
The Warden (Fuchsia map 481, see fuchsia_warden.py) now gives HM04 Strength only for the Gold Teeth; Surf comes from the Fishing Guru.

Entrance: the dead-end street tile at the east end of Fuchsia's south street (map 56, trigger at 1221,441) asks whether to go in. Leaving through the Center's south gate returns there.

Usage: safari_yellow.py <in.nds> <out.nds> <pokeyellow source>
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
import yellow_text
import yellow_route_reference as yellow_ref
from forest_progression import SLOT_MAP, pickup
from map_edit import MapEdit
from mansion_yellow import add_event_rows, append_to_native
from mtmoon_yellow import FACE, parse
from opening import Script, actor, encode_text, end, events_decode, events_encode, script_bank
from parcel_quest import PH
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

NAMES = {1: 'SafariZoneCenter', 2: 'SafariZoneEast', 3: 'SafariZoneNorth', 4: 'SafariZoneWest'}
DEST_AREA = {'SAFARI_ZONE_CENTER': 1, 'SAFARI_ZONE_EAST': 2, 'SAFARI_ZONE_NORTH': 3, 'SAFARI_ZONE_WEST': 4}
BLOCKS = {1: (15, 13), 2: (15, 13), 3: (20, 18), 4: (15, 13)}
KEPT_WARPS = {1: 8, 2: 4, 3: 8, 4: 6}                     # the first N Yellow warps (the last ones are the rest houses and the secret house)
FOREST_COLL = {0x1E, 0x20, 0x2E, 0x30, 0x34, 0x37, 0x39, 0x3A, 0x40, 0x51, 0x52, 0x5A, 0x5C, 0x5E, 0x5F}      # Forest_Coll (walkable tile ids)
TEX = [('grass01gs', 'grass01', 'SafFloor'), ('tree01gs', 'tree01_un', 'SafWall'), ('tree01_un', 'tree01_un', 'SafTop'), ('cliff01gs', 'cliff01', 'SafRock')]
MATS = [('floor', 0, 'floor'), ('wall_top', 2, 'wall_top'), ('wall_slope', 1, 'wall_slope'), ('stone_top', 3, 'stone_top'), ('stone_side', 3, 'stone_side')]
OX, OZ, CX, CZ, AREA = 8, 12, 3, 3, 15
FUCHSIA, ENTRY, EXIT_ARRIVAL, FUCHSIA_ANCHOR = 56, (1221, 441), (1218, 441), 11        # the new arrival row is Fuchsia's 12th warp row (it has 11)
WARDEN_MAP, GOLD_TEETH, HM_SURF, HM_STRENGTH, WARDEN_GIVEN = 481, 877, 422, 423, 0xA6C
GURU_FLAG = 0x967                                          # Surf given (checked free by trainer_alloc.assert_flags_free)
ITEM_ID = {'NUGGET': 92, 'FULL_RESTORE': 23, 'MAX_POTION': 24, 'CARBOS': 48, 'PROTEIN': 46, 'MAX_REVIVE': 29, 'GOLD_TEETH': GOLD_TEETH, 'TM_DOUBLE_TEAM': 359}
ITEM_NAME = {'NUGGET': 'NUGGET', 'FULL_RESTORE': 'FULL RESTORE', 'MAX_POTION': 'MAX POTION', 'CARBOS': 'CARBOS', 'PROTEIN': 'PROTEIN', 'MAX_REVIVE': 'MAX REVIVE', 'GOLD_TEETH': 'GOLD TEETH',
             'TM_DOUBLE_TEAM': 'TM32'}
BALL_FLAGS = [0x95A, 0x95B, 0x95D, 0x95E, 0x95F, 0x961, 0x962, 0x963, 0x965]       # one per ball placed (9; Egg Bomb and Skull Bash TMs are not in this ROM)
# Yellow's Nugget lies on an island in the Center pond (reached by Surf); the pond is solid here, so the ball goes on the pond's north shore
NUGGET_SHORE = (36, 27)
TRIGGER_VAR = 0x4179                                       # never written (stays 0)


def guru_script(base):
    s = Script().emit(96).emit(104).emit(32, GURU_FLAG).jump('again', 1)
    s.msg(base)
    s.emit(125, HM_SURF, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    s.emit(30, GURU_FLAG).emit(78, 1185).msg(base + 1).emit(79).msg(base + 2)
    end(s)
    s.label('full').msg(base + 3)
    end(s)
    s.label('again').msg(base + 2)
    end(s)
    return s.finish()


def warden(rom, source):
    """The Warden (Fuchsia map 481) wants his GOLD TEETH: without them Yellow's gibberish, with them HM04 Strength. (HM03 Surf now comes from the Fishing Guru in the Safari Zone.)"""
    m = lambda l: yellow_text.message(source, 'WardensHouse', l).rstrip('@')
    edit = MapEdit(rom, WARDEN_MAP)

    def build(msg):
        gib = msg(m('_WardensHouseWardenGibberish1Text') + '\r' + m('_WardensHouseWardenGibberish2Text'))
        gave = msg(m('_WardensHouseWardenGaveTheGoldTeethText'))
        popped = msg(m('_WardensHouseWardenTeethPoppedInHisTeethText'))
        thanks = msg(m('_WardensHouseWardenThanksText'))
        got4 = msg('{PLAYER} received HM04!')
        explain = msg(m('_WardensHouseWardenHM04ExplanationText'))
        full = msg(m('_WardensHouseWardenHM04NoRoomText'))
        again = msg(m('_WardensHouseWardenHM04ExplanationText'))
        s = Script().emit(96).emit(104).emit(32, WARDEN_GIVEN).jump('again', 1)
        s.emit(126, GOLD_TEETH, 1, 0x800C).compare(0x800C, 0).jump('noteeth', 1)
        s.msg(gave).msg(popped).msg(thanks)
        s.emit(125, HM_STRENGTH, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
        s.emit(30, WARDEN_GIVEN).emit(78, 1185).msg(got4).emit(79).msg(explain)
        end(s)
        s.label('noteeth').msg(gib)
        end(s)
        s.label('full').msg(full)
        end(s)
        s.label('again').msg(again)
        end(s)
        return s.finish()

    entry = edit.script(build)
    i = max(range(len(edit.groups[1])), key=lambda k: struct.unpack_from('<H', edit.groups[1][k], 10)[0])        # the Warden is the actor fuchsia_warden.py gave its own script
    edit.groups[1][i] = bytearray(edit.groups[1][i])
    struct.pack_into('<H', edit.groups[1][i], 10, entry)
    edit.save()
    return entry


def patch(rom, source):
    trainer_alloc.assert_flags_free(rom, BALL_FLAGS + [GURU_FLAG])
    y = {f: parse(source, NAMES[f]) for f in NAMES}
    refs = {}
    for f in NAMES:
        refs[f] = yellow_ref.reference(source, NAMES[f], 0, extra_roles={}, wild=True, first_index=0)
    template = bytes(ext.records(rom)[560 - ext.NATIVE_COUNT])
    ids = dict(zip(NAMES, ext.install(rom, [template] * 4)))
    report = {}
    for f in NAMES:
        W, H = BLOCKS[f]
        warps = [(w[0], w[1]) for w in y[f]['warps'][:KEPT_WARPS[f]]]
        report[f] = cf.install(rom, source, NAMES[f], ids[f], W, H, warps, OX, OZ, CX, CZ, AREA, TEX, MATS, None, tileset='forest', coll=FOREST_COLL,
                               extra_floor=[(o['x'], o['y']) for o in y[f]['objs']] + [(3, 3)] * (f == 4))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts_narc = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts_narc = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    wild = ndspy.narc.NARC(rom.getFileByName('a/0/3/7'))
    wild_template = bytes(wild.files[template[0]] if template[0] != 255 else wild.files[0])
    key = decode_messages(encode_text(['x'], PH))[0]
    flags = iter(BALL_FLAGS)
    new_events, new_scripts, new_texts, new_wild = {}, {}, {}, {}
    placed = []
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
        for o in y[f]['objs']:
            if o['item'] in ITEM_ID:
                flag = next(flags)
                base = message('{PLAYER} found %s!' % ITEM_NAME[o['item']], 'You have no room for this.')
                bank.append(pickup(ITEM_ID[o['item']], flag, base, used))
                at = NUGGET_SHORE if o['item'] == 'NUGGET' else cf.place(name, o['x'], o['y'])
                g[1].append(actor(used, 87, len(bank), *at, flag, 0))
                placed.append((f, o['item'], hex(flag)))
                used += 1
        if f == 4:
            m = lambda l: yellow_text.message(source, 'SafariZoneSecretHouse', l).rstrip('@')
            base = message(m('_SafariZoneSecretHouseFishingGuruYouHaveWonText'), '{PLAYER} received HM03!', 'FISHING GURU: Use SURF to cross the water! It needs the SOUL BADGE.',
                           m('_SafariZoneSecretHouseFishingGuruHM03NoRoomText'))
            bank.append(guru_script(base))
            g[1].append(actor(used, 329, len(bank), *cf.place(name, 3, 4), 0, 1))
            used += 1
        for k, (wx, wy, dest, wid) in enumerate(y[f]['warps'][:KEPT_WARPS[f]]):
            ax, az = st['arrival'][k]
            g[2].append(struct.pack('<4H', ax, az, ids[f], k) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            dest, wid = y[f]['warps'][wi][2], y[f]['warps'][wi][3]
            if dest in ('LAST_MAP', 'SAFARI_ZONE_GATE'):           # Yellow's gate building is not built: out to Fuchsia
                dmap, anchor = FUCHSIA, FUCHSIA_ANCHOR         # the new arrival row added to Fuchsia below
            else:
                dmap, anchor = ids[DEST_AREA[dest]], wid - 1
            g[2].append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        new_events[f] = len(events.files)
        events.files.append(events_encode(g))
        new_scripts[f] = len(scripts_narc.files)
        scripts_narc.files.append(script_bank(bank))
        new_texts[f] = len(texts_narc.files)
        texts_narc.files.append(encode_messages(key, rows))
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
    # ---- Fuchsia: the entrance (a question, then in) and the arrival row for people leaving
    arrive = cf.STATE[NAMES[1]]['arrival'][0]

    def entrance(first, base):
        s = Script().emit(96).msg(base).emit(63, 0x800C).compare(0x800C, 0).jump('go', 1)
        s.msg(base + 1)
        end(s)
        s.label('go').emit(174, 6, 6, 0, 0).emit(175).emit(176, ids[1], 0, arrive[0], arrive[1], 1).emit(174, 6, 6, 1, 0).emit(175)
        s.emit(97).emit(2)
        return [s.finish()]
    first = append_to_native(rom, FUCHSIA, entrance, ['This is the SAFARI ZONE. Would you like to go in?', 'Come back any time!'])
    add_event_rows(rom, FUCHSIA, warps=[struct.pack('<4H', EXIT_ARRIVAL[0], EXIT_ARRIVAL[1], FUCHSIA, FUCHSIA_ANCHOR) + bytes(4)], expect_warps=FUCHSIA_ANCHOR,
                   
                   triggers=[struct.pack('<Hhh5H', first, ENTRY[0], ENTRY[1], 1, 1, 0, 0, TRIGGER_VAR)])
    warden_entry = warden(rom, source)
    return dict(ids=ids, floors=report, wild=new_wild, balls=placed, warden=warden_entry)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
