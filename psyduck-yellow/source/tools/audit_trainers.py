"""Static audit of trainer parties: record size matches the type byte, species 1..1075 (or a project species), level 1..100, moves valid.

Usage: audit_trainers.py <rom.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    trainers = ndspy.narc.NARC(rom.getFileByName('a/0/5/5')).files
    parties = ndspy.narc.NARC(rom.getFileByName('a/0/5/6')).files
    moves = len(ndspy.narc.NARC(rom.getFileByName('a/0/1/1')).files)
    bad = 0
    for i, (row, party) in enumerate(zip(trainers, parties)):
        row, party = bytes(row), bytes(party)
        count, kind = row[3], row[0]
        if not count:
            continue
        size = 8 + (8 if kind & 1 else 0) + (2 if kind & 2 else 0)
        if len(party) != count * size:
            print('trainer', i, 'party', len(party), 'bytes, count', count, 'type', kind, 'expects', count * size)
            bad += 1
            continue
        for k in range(count):
            e = party[k * size:(k + 1) * size]
            level, species = struct.unpack_from('<HH', e, 2)
            problems = []
            if not 1 <= level <= 100:
                problems.append(f'level {level}')
            if not 1 <= species < 1583:
                problems.append(f'species {species}')
            if kind & 1:
                for m in struct.unpack_from('<4H', e, 8):
                    if m >= moves:
                        problems.append(f'move {m}')
            if problems:
                print('trainer', i, 'mon', k, problems)
                bad += 1
    print(len(trainers), 'trainers,', bad, 'problems')


if __name__ == '__main__':
    main(sys.argv[1])
