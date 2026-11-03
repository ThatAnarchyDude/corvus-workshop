"""Novareon (starter 1581) and Mega Novareon (1582) get Beast Boost (ability 224) in every ability slot (owner order 2026-10-29, "for now").
Personal data a/0/0/2, 44 bytes per species: byte 22 = ability 1, byte 23 = ability 2, byte 26 = hidden ability (seen on Eevee: Run Away at 22, Adaptability at 26).
The hidden-ability helper in starter_properties.py is keyed by species id and has no row for 1581/1582, so it takes the ordinary path and reads these bytes.
Whether the battle engine runs Beast Boost's effect is NOT verified here (the ability exists in the name list, id 224).
Usage: novareon_ability.py <in.nds> <out.nds>"""
import sys
import ndspy.narc
import ndspy.rom

BEAST_BOOST = 224
SPECIES = (1581, 1582)


def patch(rom):
    fid = rom.filenames.idOf('a/0/0/2')
    narc = ndspy.narc.NARC(rom.files[fid])
    for sp in SPECIES:
        row = bytearray(narc.files[sp])
        assert len(row) == 44
        row[22] = row[23] = row[26] = BEAST_BOOST
        narc.files[sp] = bytes(row)
    rom.files[fid] = narc.save()


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
    print('wrote', sys.argv[2])
