"""Static audit of the wild encounter files (a/0/3/7, 196 bytes each): slots of an enabled encounter type must hold a real species and a level 1-100.

Layout (HGSS): rates[6]+pad[2] (walk, surf, rock smash, old, good, super rod), walk levels[12], walk species 3x12 u16 (morning/day/night), radio 4 u16,
surf 5x(min, max, u16 species), rock smash 2x4, old rod 5x4, good rod 5x4, super rod 5x4, swarm 4 u16. The species word holds the species in its low 11 bits.

Usage: audit_encounters.py <rom.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom

SPECIES_MAX = 1583


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    files = ndspy.narc.NARC(rom.getFileByName('a/0/3/7')).files
    bad = 0
    for i, raw in enumerate(files):
        f = bytes(raw)
        rates = f[:6]
        problems = []
        if rates[0]:
            for k in range(12):
                level = f[8 + k]
                for t in range(3):
                    sp = struct.unpack_from('<H', f, 20 + 2 * (12 * t + k))[0] & 0x7FF
                    if not 1 <= sp < SPECIES_MAX or not 1 <= level <= 100:
                        problems.append(f'walk slot {k} time {t}: species {sp} level {level}')
        for rate, at, count, label in ((rates[1], 100, 5, 'surf'), (rates[2], 120, 2, 'rock'), (rates[3], 128, 5, 'old'), (rates[4], 148, 5, 'good'), (rates[5], 168, 5, 'super')):
            if rate:
                for k in range(count):
                    lo, hi, sp = struct.unpack_from('<BBH', f, at + 4 * k)
                    if not 1 <= (sp & 0x7FF) < SPECIES_MAX or not (1 <= lo <= hi <= 100):
                        problems.append(f'{label} slot {k}: species {sp & 0x7FF} levels {lo}-{hi}')
        if problems:
            bad += 1
            print('file', i, 'rates', list(rates), problems[:3])
    print(len(files), 'files,', bad, 'with problems')


if __name__ == '__main__':
    main(sys.argv[1])
