"""Routes 11 and 12: HeartGold's sleeping Snorlax wakes to the Poke Flute (item 651) instead of the Pokegear radio tune.

Each Snorlax script is kept whole. Its 'is the radio tune playing?' test (RadioMusicIsPlaying) becomes 'result = 1', and a
prefix is put in front of it: without the Poke Flute the player gets Yellow's blocked-road text and the script ends.
Native wake text, battle (Lv50), flags and hiding are unchanged.
"""
import struct
import ndspy.narc
from opening import Script
from parcel_quest import append_bank, PH
from opening import encode_text
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE
import yellow_text

POKE_FLUTE = 651
SNORLAX = {19: 1, 20: 6}               # map -> the Snorlax actor's script id (Route 11, Route 12)
RADIO = struct.pack('<3H', 779, 5, 32780)
FORCE_YES = struct.pack('<3H', 41, 32780, 1)


def patch(rom, source):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    texts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    blocked = yellow_text.message(source, 'Route12', '_Route12SnorlaxText')
    report = {}
    from opening import events_decode, events_encode
    for map_id, script_id in SNORLAX.items():
        rec = TABLE + map_id * 24
        sid, tid = struct.unpack_from('<H', d, rec + 6)[0], struct.unpack_from('<H', d, rec + 10)[0]
        raw = scripts.files[sid]
        count = next(i for i in range(400) if struct.unpack_from('<H', raw, 4 * i)[0] == 0xFD13)
        starts = [4 * i + 4 + struct.unpack_from('<I', raw, 4 * i)[0] for i in range(count)]
        begin = starts[script_id - 1]
        original = bytes(raw[begin:min([a for a in starts if a > begin] + [len(raw)])])
        assert original.count(RADIO) == 1, 'unexpected Snorlax script'
        key, rows = decode_messages(texts.files[tid])
        index = len(rows)
        assert index < 250
        rows.extend(decode_messages(encode_text([blocked], PH))[1])
        pre = Script().emit(73, 1500).emit(96).emit(128, POKE_FLUTE, 1, 0x800C).compare(0x800C, 1).jump('wake', 1)
        pre.msg(index).emit(97).emit(2)
        pre.label('wake')
        prefix = pre.finish()
        if len(prefix) % 2:
            prefix += b'\0'
        new_bank, before = append_bank(raw, [prefix + original.replace(RADIO, FORCE_YES)])
        entry = before + 1
        scripts.files.append(bytes(new_bank))
        texts.files.append(encode_messages(key, rows))
        struct.pack_into('<H', d, rec + 6, len(scripts.files) - 1)
        struct.pack_into('<H', d, rec + 10, len(texts.files) - 1)
        eid = struct.unpack_from('<H', d, rec + 16)[0]
        groups = events_decode(events.files[eid])
        hit = [i for i, a in enumerate(groups[1]) if struct.unpack_from('<2H', a, 2)[0] == 395 and struct.unpack_from('<H', a, 10)[0] == script_id]
        assert len(hit) == 1
        groups[1][hit[0]] = bytearray(groups[1][hit[0]])
        struct.pack_into('<H', groups[1][hit[0]], 10, entry)
        events.files.append(events_encode(groups))
        struct.pack_into('<H', d, rec + 16, len(events.files) - 1)
        report[map_id] = dict(entry=entry, message=index)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.files[rom.filenames.idOf('a/0/2/7')] = texts.save()
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.arm9 = main.save(compress=True)
    return report
