"""TEST-ONLY fixture: one-shot transport out of the bedroom of a copied 0040 fixture save.

Never part of a release ROM. Usage: test_transport.py <in.nds> <out.nds> <map> <x> <y> <facing>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import Script
from parcel_quest import append_bank
from viridian_tutorial import TABLE
from pokemon_tower import _frame_entry, STATE

BEDROOM = 506


def install(rom, map_id, x, y, facing):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    at = TABLE + BEDROOM * 24
    bank_id, header_id = struct.unpack_from('<2H', d, at + 6)
    s = Script().emit(41, STATE, 1).emit(96).emit(174, 6, 6, 0, 0).emit(175).emit(176, map_id, 0, x, y, facing)
    s.emit(174, 6, 6, 1, 0).emit(175).emit(97).emit(2)
    bank, count = append_bank(scripts.files[bank_id], [s.finish()])
    scripts.files[bank_id] = bytes(bank)
    scripts.files[header_id] = _frame_entry(scripts.files[header_id], STATE, 0, count + 1)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.arm9 = main.save(compress=True)


if __name__ == '__main__':
    src, dst, m, x, y, f = sys.argv[1:7]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    install(rom, int(m), int(x), int(y), int(f))
    rom.saveToFile(dst)
