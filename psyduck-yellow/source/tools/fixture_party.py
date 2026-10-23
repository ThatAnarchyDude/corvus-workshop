"""TEST-ONLY fixture: give the player a Pokemon and items the first time the bedroom loads of a copied 0040 fixture save.

Never part of a release ROM and never campaign proof. Optionally starts a wild battle.
Usage: fixture_party.py <in.nds> <out.nds> <species> <held item> <level> [item:count ...] [--battle species,level] [--dex]
--dex also gives the Pokedex and National Dex mode (script commands 291, flag 0x6B, 477), which unlocks the POKEDEX and POKEMON entries of the field menu.
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


def install(rom, species, held, level, items, battle, dex=False):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    at = TABLE + BEDROOM * 24
    bank_id, header_id = struct.unpack_from('<2H', d, at + 6)
    s = Script().emit(41, STATE, 1).emit(137, species, level, held, 0, 0, 0x800C)
    for item, count in items:
        s.emit(125, item, count, 0x800C)
    if dex:
        s.emit(291).emit(30, 0x6B).emit(477)       # the project's own dex grant: give Pokedex, flag 0x6B, National Dex mode on
        s.data.append(1)
        s.emit(0x800C)
        for flag in (0x68, 0x69, 0x6A, 0x6C, 0x6D, 0x6E):   # neighbours of the Pokedex flag; one of them is the POKEMON menu entry
            s.emit(30, flag)
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
    dex = '--dex' in args
    if dex:
        args.remove('--dex')
    if '--battle' in args:
        i = args.index('--battle')
        battle = tuple(int(v) for v in args[i + 1].split(','))
        del args[i:i + 2]
    src, dst, species, held, level = args[:5]
    items = [tuple(int(v) for v in a.split(':')) for a in args[5:]]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    install(rom, int(species), int(held), int(level), items, battle, dex)
    rom.saveToFile(dst)
