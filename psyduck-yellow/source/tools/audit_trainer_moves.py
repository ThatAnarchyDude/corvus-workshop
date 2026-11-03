"""Static trainer-party audit with the REAL party layout (found 2026-11-02: audit_trainers.py reads moves at offset 8 for every moves record, but type 1 records carry them at offset 6; step 5a moved the ball seal to the end).
Entry layout: [iv u8, ability u8, level u16, species u16, item u16 (types 2 and 3), 4 moves u16 (types 1 and 3), ball seal u16]. For every party member: species/level sane, every move exists, and every move is one the species
can learn by level-up at some level (a/0/3/3: one file, 136 bytes per species, u16 move + u16 level pairs ending 0xFFFF). Also reports members whose four moves are not Yellow's default (the last four level-up moves at or below the level).
Usage: audit_trainer_moves.py <rom.nds> [first last]   Prints a summary and the outliers."""
import struct
import sys
import ndspy.narc
import ndspy.rom


def main(path, lo, hi):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    trainers = ndspy.narc.NARC(rom.getFileByName('a/0/5/5')).files
    parties = ndspy.narc.NARC(rom.getFileByName('a/0/5/6')).files
    learn = ndspy.narc.NARC(rom.getFileByName('a/0/3/3')).files
    move_count = len(ndspy.narc.NARC(rom.getFileByName('a/0/1/1')).files)

    blob = bytes(learn[0])                                    # a/0/3/3 is ONE file: 136 bytes per species (u16 move, u16 level pairs, 0xFFFF end)

    def learnset(species):
        if (species + 1) * 136 > len(blob):
            return None
        data = blob[species * 136:(species + 1) * 136]
        pairs = []
        for i in range(0, 136, 4):
            m, lv = struct.unpack_from('<HH', data, i)
            if m == 0xFFFF:
                break
            pairs.append((lv, m))
        return pairs

    stats = dict(trainers=0, members=0, with_moves=0, not_learnable=0, not_default=0, bad_size=0, bad_range=0)
    outliers = []
    for i in range(lo, min(hi, len(trainers))):
        row, party = bytes(trainers[i]), bytes(parties[i])
        count, kind = row[3], row[0]
        if not count:
            continue
        stats['trainers'] += 1
        size = 8 + (8 if kind & 1 else 0) + (2 if kind & 2 else 0)
        if len(party) != count * size:
            stats['bad_size'] += 1
            outliers.append((i, 'party size %d != %d x %d (type %d)' % (len(party), count, size, kind)))
            continue
        for k in range(count):
            e = party[k * size:(k + 1) * size]
            level, species = struct.unpack_from('<HH', e, 2)
            stats['members'] += 1
            if not (1 <= level <= 100 and 1 <= species < 1583):
                stats['bad_range'] += 1
                outliers.append((i, 'member %d species %d level %d' % (k, species, level)))
                continue
            if not kind & 1:
                continue
            at = 8 if kind & 2 else 6
            moves = [m for m in struct.unpack_from('<4H', e, at)]
            stats['with_moves'] += 1
            ls = learnset(species)
            if ls is None:
                continue
            known = {m for _, m in ls}
            bad = [m for m in moves if m and (m >= move_count or m not in known)]
            if bad:
                stats['not_learnable'] += 1
                outliers.append((i, 'member %d species %d L%d moves %s not learnable: %s' % (k, species, level, moves, bad)))
                continue
            default = []
            for lv, m in sorted(ls):
                if lv <= level and m not in default:
                    default.append(m)
            default = default[-4:]
            if sorted(m for m in moves if m) != sorted(default):
                stats['not_default'] += 1
    print(stats)
    for o in outliers[:40]:
        print('  trainer %d: %s' % o)
    if len(outliers) > 40:
        print('  ... %d more' % (len(outliers) - 40))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9)
