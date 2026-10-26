"""TEST ONLY: ROM whose bedroom script writes marker values into script vars and flags, to learn where the save stores them. argv: in out"""
import struct, sys
import ndspy.narc, ndspy.rom
from opening import Script
from parcel_quest import append_bank
from viridian_tutorial import TABLE
from pokemon_tower import _frame_entry, STATE
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
main = rom.loadArm9(); d = main.sections[0].data = bytearray(main.sections[0].data)
scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
at = TABLE + 506 * 24
bank_id, header_id = struct.unpack_from('<2H', d, at + 6)
FLAGS = [int(x, 0) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else []
s = Script().emit(41, STATE, 1)
VARS = {0x4152: 0x1357, 0x4178: 0x3579, 0x41A0: 0x4680, 0x41F0: 0x5791, 0x4210: 0x68A2, 0x4250: 0x79B3}
for v, val in VARS.items():
    s.emit(41, v, val)
for f in FLAGS:
    s.emit(30, f)
s.emit(97).emit(2)
bank, count = append_bank(scripts.files[bank_id], [s.finish()])
scripts.files[bank_id] = bytes(bank)
scripts.files[header_id] = _frame_entry(scripts.files[header_id], STATE, 0, count + 1)
rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
rom.arm9 = main.save(compress=True)
rom.saveToFile(sys.argv[2])
