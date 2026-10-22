"""Unpublished 0018 foundation: Yellow cave trainers and encounters.

This deliberately has no release/package entry point. Fossil and Rocket story
scenes, rewards and native playtests must be complete before publishing 0018.
"""
import json
import struct

import ndspy.narc

from build_rom import PROJECT
from opening import actor, events_decode, events_encode, script_bank, encode_text, talk
from parcel_quest import PH
from forest_progression import expanded_common, SLOT_MAP, pickup
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

DATA = json.loads((PROJECT / 'data/mtmoon.json').read_text())
INPUT_SHA = '71f86b48272129c0f3d8f6b876403bf831c454b5917add58caf9921560f1976d'
FLOORS = {107: '1F', 448: 'B1F'}


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    paths = ['a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/5/5',
             'a/0/5/6', 'a/0/3/7', 'a/0/5/7', 'a/1/3/1']
    arcs = {p: ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts, texts, events, trainers, parties, wild, trtable, offsets = arcs.values()
    namekey, names = decode_messages(texts.files[729])
    textkey, battle_text = decode_messages(texts.files[728])
    table, ofs = bytearray(trtable.files[0]), bytearray(offsets.files[0])
    added = []
    for entry in DATA['trainers']:
        tid = len(trainers.files)
        assert tid < 1000
        # Use an existing header of the appropriate class, retaining its native
        # payout/portrait conventions while removing held items and forced AI.
        template = next(r for r in trainers.files if r[1] == entry['trainer_class'])
        row = bytearray(template)
        row[0], row[3], row[16] = 1, len(entry['team']), 0
        row[4:12] = bytes(8)
        struct.pack_into('<I', row, 12, 1)
        trainers.files.append(row)
        parties.files.append(b''.join(struct.pack('<BB3H4H', 128, 0,
                             p['level'], p['species'], 0, *p['moves'])
                             for p in entry['team']))
        names.append([0xFFFF])
        while len(ofs) < 2 * (tid + 1):
            ofs.extend(struct.pack('<H', len(table)))
        struct.pack_into('<H', ofs, 2 * tid, len(table))
        for kind, suffix in enumerate(('BattleText', 'EndBattleText', 'AfterBattleText')):
            table.extend(struct.pack('<2H', tid, kind))
            line = DATA['messages'][entry['dialogue'] + suffix]
            battle_text.extend(decode_messages(encode_text([line], PH))[1])
        added.append(dict(id=tid, defeat_flag=0x550 + tid, **entry))
    texts.files[729] = encode_messages(namekey, names)
    texts.files[728] = encode_messages(textkey, battle_text)
    trtable.files[0], offsets.files[0] = bytes(table), bytes(ofs)

    # Both native trainer dispatch ranges use the same expanded common bank.
    dispatch = []
    for trigger in (3000, 5000):
        matches = [at for at in range(0, len(d) - 6, 2)
                   if struct.unpack_from('<H', d, at)[0] == trigger
                   and struct.unpack_from('<H', d, at + 4)[0] == 40
                   and struct.unpack_from('<H', d, at + 2)[0] < len(scripts.files)]
        assert len(matches) == 1
        dispatch.append(matches[0])
    previous_common = struct.unpack_from('<H', d, dispatch[0] + 2)[0]
    assert struct.unpack_from('<H', d, dispatch[1] + 2)[0] == previous_common
    common = len(scripts.files)
    scripts.files.append(expanded_common(scripts.files[previous_common], added[-1]['id']))
    for at in dispatch:
        struct.pack_into('<H', d, at + 2, common)

    maps = []
    for mapid, floor in FLOORS.items():
        rec = TABLE + 24 * mapid
        old_sid, old_iid, old_tid = struct.unpack_from('<3H', d, rec + 6)
        old_eid = struct.unpack_from('<H', d, rec + 16)[0]
        old_wild = d[rec]
        groups = events_decode(events.files[old_eid])
        groups[1] = []
        for entry in added:
            if entry['map'] != mapid:
                continue
            row = bytearray(actor(entry['actor'], entry['sprite'],
                                  3000 + entry['id'] - 1,
                                  entry['x'], entry['z'], facing=entry['facing']))
            struct.pack_into('<H', row, 6, 1)
            struct.pack_into('<H', row, 14, 3)
            groups[1].append(row)
        # Archive Silver's endgame scene and weekday warp rewrites. Retain the
        # native passages and the square's unrelated events without changing
        # their geometry. Story completion is still pending for this draft.
        groups[0], groups[3] = [], []
        lines = [DATA['messages']['MtMoon1FBewareZubatSign']]
        bank = [talk(0)]
        if mapid == 107:
            groups[0] = [struct.pack('<HHiiiH2x', 1, 1, 24, 7, 0, 4)]
        for item in DATA['pickups']:
            if item['map'] != mapid:
                continue
            index = len(lines)
            lines.extend([f"You found a {item['name']}!",
                          'Your BAG is full. Make some room and come back.'])
            entry = len(bank) + 1
            bank.append(pickup(item['item'], item['flag'], index, item['actor']))
            groups[1].append(actor(item['actor'], 87, entry,
                                   item['x'], item['z'], item['flag'], 0))
        sid = len(scripts.files)
        scripts.files.append(script_bank(bank))
        iid = len(scripts.files)
        scripts.files.append(bytes(4))
        tid = len(texts.files)
        texts.files.append(encode_text(lines, PH))
        eid = len(events.files)
        events.files.append(events_encode(groups))
        struct.pack_into('<3H', d, rec + 6, sid, iid, tid)
        struct.pack_into('<H', d, rec + 16, eid)
        w = bytearray(wild.files[old_wild])
        assert len(w) == 196
        slots = [DATA['wild_slots'][floor][i] for i in SLOT_MAP]
        w[0], w[1:6] = DATA['encounter_rate'], bytes(5)
        w[8:20] = bytes(p['level'] for p in slots)
        species = [p['species'] for p in slots]
        for period in range(3):
            struct.pack_into('<12H', w, 20 + 24 * period, *species)
        for at in (0x5C, 0x60, 0x64, 0x68, 0xBC):
            struct.pack_into('<2H', w, at, species[0], species[1])
        wid = len(wild.files)
        assert wid < 255
        wild.files.append(w)
        d[rec] = wid
        maps.append(dict(map=mapid, yellow_encounter_floor=floor, script=sid,
                         init=iid, text=tid, event=eid, wild=wid,
                         originals=dict(script=old_sid, init=old_iid,
                                        text=old_tid, event=old_eid, wild=old_wild)))
    for path, arc in arcs.items():
        rom.files[rom.filenames.idOf(path)] = arc.save()
    rom.arm9 = main.save(compress=True)
    return dict(status='unpublished foundation; not a completed checkpoint',
                input_sha256=INPUT_SHA, maps=maps, trainers=added,
                pickups=DATA['pickups'],
                trainer_common=common, original_common=previous_common,
                pending=DATA['pending'])
