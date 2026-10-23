"""Saffron (Sabrina), Cinnabar/Seafoam (Blaine) and Viridian gyms: Yellow teams on the native HG gym trainers; native flow and badges stay.

Native trainer ids come from each gym's sight-trainer scripts (3000+id-1) or its leader script. Yellow's gyms have more
trainers than HG's; the first N Yellow trainers (object order) take the N native records and the rest are deferred.
"""
import struct
import gym_conversion
import tower_scenes as ts
from opening import encode_text, events_decode, events_encode
from parcel_quest import PH
from prototype import decode_messages
from viridian_tutorial import TABLE

BOSS_CLASS, GIOVANNI_SPRITE = 124, 385         # Rocket Boss class (battle art) and the boss overworld sprite used in the Hideout

GYMS = {
    'saffron': dict(map=410, yellow='SaffronGym', natives=[369, 415, 368, 230], leader=258, label='SabrinaData', index=0),
    'seafoam': dict(map=457, yellow='CinnabarGym', natives=[689, 692], leader=259, label='BlaineData', index=0),
    'viridian': dict(map=496, yellow='ViridianGym', natives=[681, 682, 683, 684], leader=261, label='GiovanniData', index=2),
}


def patch(rom, source):
    report = {}
    for name, g in GYMS.items():
        yellow = gym_conversion.yellow_gym_trainers(source, g['yellow'])
        mapping = dict(zip(g['natives'], yellow))
        report[name] = dict(map=g['map'], teams=gym_conversion.convert(rom, source, mapping, g['leader'], g['label'], g['index']),
                            deferred=max(0, len(yellow) - len(g['natives'])))
    report['viridian_leader'] = viridian_giovanni(rom)
    return report


def viridian_giovanni(rom):
    """HG's Viridian leader is Blue (rival class 110): present him as Giovanni - Rocket Boss class, name and overworld sprite."""
    book = ts.TrainerBook(rom)
    row = bytearray(book.trainers.files[261])
    assert row[1] == 110
    row[1] = BOSS_CLASS
    book.trainers.files[261] = bytes(row)
    book.names[261] = decode_messages(encode_text(['GIOVANNI'], PH))[1][0]
    book.save()
    d = rom.loadArm9().sections[0].data
    rec = TABLE + 496 * 24
    events = ts.ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    g = events_decode(events.files[struct.unpack_from('<H', d, rec + 16)[0]])
    hit = [i for i, a in enumerate(g[1]) if struct.unpack_from('<H', a, 10)[0] == 1]
    assert len(hit) == 1
    g[1][hit[0]] = bytearray(g[1][hit[0]])
    struct.pack_into('<H', g[1][hit[0]], 2, GIOVANNI_SPRITE)
    events.files.append(events_encode(g))
    main = rom.loadArm9()
    dd = main.sections[0].data = bytearray(main.sections[0].data)
    struct.pack_into('<H', dd, rec + 16, len(events.files) - 1)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.arm9 = main.save(compress=True)
    return dict(trainer=261, class_id=BOSS_CLASS, sprite=GIOVANNI_SPRITE)
