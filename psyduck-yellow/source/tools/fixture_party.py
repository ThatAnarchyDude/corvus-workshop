"""TEST-ONLY fixture: give the player a Pokemon and items the first time the bedroom loads of a copied 0040 fixture save.

Never part of a release ROM and never campaign proof. Optionally starts a wild battle.
Usage: fixture_party.py <in.nds> <out.nds> <species> <held item> <level> [item:count ...] [--battle species,level]
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


def install(rom, species, held, level, items, battle):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    at = TABLE + BEDROOM * 24
    bank_id, header_id = struct.unpack_from('<2H', d, at + 6)
    s = Script().emit(41, STATE, 1).emit(137, species, level, held, 0, 0, 0x800C)
    for item, count in items:
        s.emit(125, item, count, 0x800C)
    if battle:
        s.emit(589, battle[0], battle[1])
        s.data.append(0)
        s.emit(220, 0x800C)
    s.emit(97).emit(2)
    bank, count = append_bank(scripts.files[bank_id], [s.finish()])
    scripts.files[bank_id] = bytes(bank)
    scripts.files[header_id] = _frame_entry(scripts.files[header_id], STATE, 0, count + 1)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.arm9 = main.save(compress=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    battle = None
    if '--battle' in args:
        i = args.index('--battle')
        battle = tuple(int(v) for v in args[i + 1].split(','))
        del args[i:i + 2]
    src, dst, species, held, level = args[:5]
    items = [tuple(int(v) for v in a.split(':')) for a in args[5:]]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    install(rom, int(species), int(held), int(level), items, battle)
    rom.saveToFile(dst)
