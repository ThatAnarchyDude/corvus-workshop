"""TEST-ONLY fixture: give the player a Pokemon and items the first time the bedroom loads of a copied 0040 fixture save.

Never part of a release ROM and never campaign proof. Optionally starts a wild battle.
Usage: fixture_party.py <in.nds> <out.nds> <species> <held item> <level> [item:count ...] [--battle species,level] [--dex] [--warp map,x,z] [--follower] [--trainer id]
--dex also gives the Pokedex and National Dex mode (script commands 291, flag 0x6B, 477), which unlocks the POKEDEX and POKEMON entries of the field menu.
"""
import os
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import Script
from parcel_quest import append_bank
from viridian_tutorial import TABLE
from pokemon_tower import _frame_entry, STATE

BEDROOM = 506


def install(rom, species, held, level, items, battle, dex=False, warp=None, follower=False, trainer=None):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    at = TABLE + BEDROOM * 24
    bank_id, header_id = struct.unpack_from('<2H', d, at + 6)
    s = Script().emit(41, STATE, 1).emit(137, species, level, held, 0, 0, 0x800C)
    for item, count in items:
        s.emit(125, item, count, 0x800C)
    for extra in filter(None, os.environ.get('FIXTURE_EXTRA', '').split(',')):       # test-only: give more species (registers them as caught in the Pokedex); env FIXTURE_EXTRA=species:level,...
        sp, lv = extra.split(':')
        s.emit(137, int(sp), int(lv), 0, 0, 0, 0x800C)
    for flag in filter(None, os.environ.get('FIXTURE_FLAGS', '').split(',')):      # test-only: set story flags (env FIXTURE_FLAGS=0x9f9,...)
        s.emit(30, int(flag, 0))
    for pair in filter(None, os.environ.get('FIXTURE_VARS', '').split(',')):         # test-only: set script variables (env FIXTURE_VARS=0x406d=1,...)
        var, value = pair.split('=')
        s.emit(41, int(var, 0), int(value, 0))
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
    if trainer is not None:                                   # test-only: start a battle against trainer record `trainer`
        s.emit(213, trainer, 0)
        s.data.extend(bytes(2))
        s.emit(220, 0x800C)
    if follower:                                              # the starter gift's own follower initialisation (tools/escort.py)
        s.emit(30, 0x6A).emit(131, species)
        s.emit(41, 0x416B, 3).emit(1).emit(41, 0x416B, 0)
        s.emit(605)
        s.data.extend(bytes([1, 0]))
        s.emit(602, 0).emit(608).emit(3, 10, 0x800C).emit(602, 1)
    if warp:
        s.emit(176, warp[0], 0, warp[1], warp[2], 0)       # test-only teleport to map, x, z
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
    warp = None
    trainer = None
    if '--trainer' in args:
        i = args.index('--trainer')
        trainer = int(args[i + 1])
        del args[i:i + 2]
    follower = '--follower' in args
    if follower:
        args.remove('--follower')
    if '--warp' in args:
        i = args.index('--warp')
        warp = tuple(int(v) for v in args[i + 1].split(','))
        del args[i:i + 2]
    if '--battle' in args:
        i = args.index('--battle')
        battle = tuple(int(v) for v in args[i + 1].split(','))
        del args[i:i + 2]
    src, dst, species, held, level = args[:5]
    items = [tuple(int(v) for v in a.split(':')) for a in args[5:]]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    install(rom, int(species), int(held), int(level), items, battle, dex, warp, follower, trainer)
    rom.saveToFile(dst)
