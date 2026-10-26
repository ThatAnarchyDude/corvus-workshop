"""TEST ONLY: Vermilion Center gets an NPC (object 9, tile 8,14) and a step trigger at the arrival tile that runs 'cmd 106: GetNPCPosition(9, 0x406E, 0x406F)'. argv: in out"""
import struct, sys
import ndspy.rom, ndspy.narc
from opening import Script, actor, events_decode, events_encode, script_bank, end
from parcel_quest import split_bank
from viridian_tutorial import TABLE
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
main = rom.loadArm9(); d = main.sections[0].data = bytearray(main.sections[0].data)
rec = TABLE + 358 * 24
scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2')); events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
sid = struct.unpack_from('<H', d, rec + 6)[0]
bank = split_bank(scripts.files[sid]); entry = len(bank) + 1
s = Script().emit(106, 9, 0x406E, 0x406F)
s.emit(2)
bank.append(s.finish())
scripts.files.append(script_bank(bank)); struct.pack_into('<H', d, rec + 6, len(scripts.files) - 1)
g = events_decode(events.files[struct.unpack_from('<H', d, rec + 16)[0]])
g[1].append(bytes(actor(9, 330, 0, 8, 14, 0, 1)))
# frame script: every frame while var 0x4179 == 0, read the NPC's tile
scripts.files.append(struct.pack('<BI', 1, 1) + b'\0' + struct.pack('<3H', 0x4179, 0, entry) + b'\0\0'); struct.pack_into('<H', d, rec + 8, len(scripts.files) - 1)
events.files.append(events_encode(g)); struct.pack_into('<H', d, rec + 16, len(events.files) - 1)
rom.setFileByName('a/0/1/2', scripts.save()); rom.setFileByName('a/0/3/2', events.save()); rom.arm9 = main.save(compress=True)
rom.saveToFile(sys.argv[2])
