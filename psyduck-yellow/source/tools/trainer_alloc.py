"""Add trainer records at CHOSEN ids.

A trainer's defeat flag is 0x550 + id, so a new trainer may only take an id whose flag nothing else uses (persistent flags are nearly exhausted; see SESSION-HANDOFF.md).
Ids in between become unused copies of the template record. The shared trainer-script bank (3000+id-1 aliases) is extended to cover the highest id.
Tested 2026-10-26: a trainer at id 1007 starts its battle normally (the old '< 1000' guard in route6_trainers/TrainerBook is not an engine limit).
"""
import struct
import ndspy.narc
from forest_progression import expanded_common
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages, encode_messages


def add(rom, entries, ids, templates):
    """entries: [{'role', 'team': [{'level','species','moves'}], 'messages': {'BattleText','EndBattleText','AfterBattleText'}}]; ids: the chosen id of each entry (ascending, all >= len(records)).
    templates: role -> template trainer id. -> [trainer id]"""
    assert list(ids) == sorted(set(ids)) and len(ids) == len(entries)
    paths = ('a/0/1/2', 'a/0/2/7', 'a/0/5/5', 'a/0/5/6', 'a/0/5/7', 'a/1/3/1')
    scripts, texts, trainers, parties, trtable, offsets = arcs = [ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    namekey, names = decode_messages(texts.files[729])
    textkey, lines = decode_messages(texts.files[728])
    assert len(trainers.files) == len(parties.files) == len(names)
    assert ids[0] >= len(trainers.files) and 0x550 + ids[-1] < 0xAA0, (ids, len(trainers.files))
    table, ofs = bytearray(trtable.files[0]), bytearray(offsets.files[0])
    by_id = dict(zip(ids, entries))
    filler = None
    for tid in range(len(trainers.files), ids[-1] + 1):
        entry = by_id.get(tid)
        template = templates[entry['role']] if entry else templates[entries[0]['role']]
        team = entry['team'] if entry else [dict(level=2, species=129, moves=(33, 0, 0, 0))]
        row = bytearray(trainers.files[template])
        row[0], row[3], row[4:12], row[16] = 1, len(team), bytes(8), 0
        struct.pack_into('<I', row, 12, 1)
        trainers.files.append(bytes(row))
        parties.files.append(b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in team))
        names.append([0xFFFF])
        while len(ofs) < 2 * (tid + 1):
            ofs.extend(struct.pack('<H', len(table)))
        struct.pack_into('<H', ofs, tid * 2, len(table))
        for kind, suffix in enumerate(('BattleText', 'EndBattleText', 'AfterBattleText')):
            text = entry['messages'][suffix] if entry else '...'
            table.extend(struct.pack('<2H', tid, kind))
            lines.extend(decode_messages(encode_text([text], PH))[1])
    texts.files[729], texts.files[728] = encode_messages(namekey, names), encode_messages(textkey, lines)
    trtable.files[0], offsets.files[0] = bytes(table), bytes(ofs)
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    sites = []
    for trigger in (3000, 5000):
        matches = [at for at in range(0, len(d) - 6, 2) if struct.unpack_from('<H', d, at)[0] == trigger
                   and struct.unpack_from('<H', d, at + 4)[0] == 40 and struct.unpack_from('<H', d, at + 2)[0] < len(scripts.files)]
        assert len(matches) == 1
        sites.append(matches[0])
    original = struct.unpack_from('<H', d, sites[0] + 2)[0]
    assert struct.unpack_from('<H', d, sites[1] + 2)[0] == original
    common = len(scripts.files)
    scripts.files.append(expanded_common(scripts.files[original], ids[-1]))
    for at in sites:
        struct.pack_into('<H', d, at + 2, common)
    for path, arc in zip(paths, arcs):
        rom.files[rom.filenames.idOf(path)] = arc.save()
    rom.arm9 = main.save(compress=True)
    return list(ids)


def assert_flags_free(rom, flags):
    """Precise check (see flagprecise.py): no script sets/clears/checks the flag (opcodes 30/31/32) and no actor's hide-flag field holds it; also not a defeat flag of an existing trainer."""
    from opening import events_decode
    ntr = len(ndspy.narc.NARC(rom.getFileByName('a/0/5/5')).files)
    flags = set(flags)
    for f in flags:
        assert not (0 < f - 0x550 < ntr), (hex(f), 'is the defeat flag of an existing trainer')
    for raw in ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files:
        b = bytes(raw)
        for at in range(len(b) - 3):
            op, v = struct.unpack_from('<HH', b, at)
            assert not (op in (30, 31, 32) and v in flags), (hex(v), 'used by a script')
    for raw in ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files:
        try:
            g = events_decode(raw)
        except Exception:
            continue
        for a in g[1]:
            assert struct.unpack_from('<H', a, 8)[0] not in flags, 'used by an actor'
