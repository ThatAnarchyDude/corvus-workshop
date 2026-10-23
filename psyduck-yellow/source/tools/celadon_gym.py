"""Minimal Yellow Celadon Gym conversion in HeartGold's Kanto gym (map 395); native flow and Rainbow Badge stay.

Teams are Yellow's (Erika, Beauty 1, Lass 17, Jr. Trainer F 11, Cooltrainer F 1). HG's gym has four trainers, so
Beauty 2/3 and Lass 18 are deferred. The native reward stays Giga Drain (TM19): HG has no Mega Drain TM.
"""
import struct
import ndspy.narc
from tower_scenes import Yellow

ERIKA = 256
# native trainer -> Yellow (class label, 1-based index)
NATIVE = {326: ('BeautyData', 1), 356: ('CooltrainerFData', 1), 336: ('JrTrainerFData', 11), 346: ('LassData', 17)}


def _write(parties, trainers, tid, team, leader=False):
    row = bytearray(trainers.files[tid])
    row[0] = 1 if leader else 0
    row[3], row[4:12], row[16] = len(team), bytes(8), 0
    trainers.files[tid] = bytes(row)
    parties.files[tid] = b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in team)


def patch(rom, source):
    yellow = Yellow(source)
    trainers = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/5/5')])
    parties = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/5/6')])
    report = {}
    for tid, (label, index) in NATIVE.items():
        report[tid] = yellow.class_party(label, index)
        _write(parties, trainers, tid, report[tid])
    report[ERIKA] = yellow.leader_party('ErikaData')
    _write(parties, trainers, ERIKA, report[ERIKA], leader=True)
    rom.files[rom.filenames.idOf('a/0/5/5')] = trainers.save()
    rom.files[rom.filenames.idOf('a/0/5/6')] = parties.save()
    return dict(map=395, teams=report, reward='native TM19 Giga Drain', deferred='Beauty 2/3, Lass 18, Mega Drain TM, Yellow dialogue')
