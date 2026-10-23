"""Minimal Yellow gym conversion inside a native HG Kanto gym: native trainers and leader take Yellow's teams and moves."""
import struct
import ndspy.narc
from tower_scenes import Yellow


def _write(parties, trainers, tid, team, leader=False):
    row = bytearray(trainers.files[tid])
    row[0] = 1 if leader else 0
    row[3], row[4:12], row[16] = len(team), bytes(8), 0
    trainers.files[tid] = bytes(row)
    parties.files[tid] = b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in team)


ROLE_LABEL = {'OPP_CHANNELER': 'ChannelerData', 'OPP_PSYCHIC_TR': 'PsychicData', 'OPP_SUPER_NERD': 'SuperNerdData',
              'OPP_BURGLAR': 'BurglarData', 'OPP_BLACKBELT': 'BlackbeltData', 'OPP_TAMER': 'TamerData',
              'OPP_COOLTRAINER_M': 'CooltrainerMData', 'OPP_COOLTRAINER_F': 'CooltrainerFData', 'OPP_JUGGLER': 'JugglerData',
              'OPP_LASS': 'LassData', 'OPP_BEAUTY': 'BeautyData', 'OPP_JR_TRAINER_F': 'JrTrainerFData', 'OPP_ROCKER': 'RockerData'}


def yellow_gym_trainers(source, name):
    """[(class label, 1-based party index)] for the gym's non-leader trainers, in Yellow's object order."""
    import re
    from pathlib import Path
    text = (Path(source) / 'data/maps/objects' / (name + '.asm')).read_text()
    out = []
    for role, index in re.findall(r'(OPP_\w+),\s*(\d+)\s*$', text, re.M):
        if role in ROLE_LABEL:
            out.append((ROLE_LABEL[role], int(index)))
    return out


def convert(rom, source, natives, leader_tid, leader_label, leader_index=0):
    """natives: {trainer id: (Yellow class label, 1-based index)}; the leader uses a $FF-format class party."""
    yellow = Yellow(source)
    trainers = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/5/5')])
    parties = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/5/6')])
    report = {}
    for tid, (label, index) in natives.items():
        report[tid] = yellow.class_party(label, index)
        _write(parties, trainers, tid, report[tid])
    report[leader_tid] = yellow.leader_party(leader_label, leader_index)
    _write(parties, trainers, leader_tid, report[leader_tid], leader=True)
    rom.files[rom.filenames.idOf('a/0/5/5')] = trainers.save()
    rom.files[rom.filenames.idOf('a/0/5/6')] = parties.save()
    return report
