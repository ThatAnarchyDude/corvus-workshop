"""Trainer records whose party holds 16-byte Pokemon (species, level and four moves) but whose type byte says "no moves" (found 2026-10-23 by a size audit).

A trainer's type byte (record byte 0) tells the engine how big each party Pokemon is: bit 0 = the party has moves (16 bytes), bit 1 = it has held items (+2). Seventeen records
(the Rock Tunnel and Viridian Gym trainers among them: 681-684, 326, 336, 346, 356, 368, 369, 415, 230, and unused 83, 84, 136, 689, 692) were written with moves
but kept a type byte of 0, so the engine read 8 bytes per Pokemon: the first Pokemon was right and the "second" was built from the first one's move bytes (for example a
Lv28 Hoothoot instead of the real second Pokemon). Setting bit 0 makes every party read correctly.

Usage: trainer_type_fix.py <in.nds> <out.nds>
"""
import sys
import ndspy.narc
import ndspy.rom


def patch(rom):
    trainers = ndspy.narc.NARC(rom.getFileByName('a/0/5/5'))
    parties = ndspy.narc.NARC(rom.getFileByName('a/0/5/6'))
    fixed = []
    for i, (row, party) in enumerate(zip(trainers.files, parties.files)):
        row = bytearray(row)
        count = row[3]
        if count and len(party) == count * 16 and row[0] & 3 == 0:
            row[0] |= 1
            trainers.files[i] = bytes(row)
            fixed.append(i)
    rom.setFileByName('a/0/5/5', trainers.save())
    return dict(fixed=fixed)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
