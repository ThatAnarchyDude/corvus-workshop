"""TEST ONLY: add trainer records up to a high id and put the last one as a sight-trainer in Vermilion's Pokemon Center. argv: in out tid"""
import struct, sys
import ndspy.rom, ndspy.narc
import tower_scenes as ts
from opening import events_decode, events_encode, actor
from viridian_tutorial import TABLE
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); target = int(sys.argv[3])
book = ts.TrainerBook(rom)
party = struct.pack('<BB3H4H', 128, 0, 5, 129, 0, 33, 0, 0, 0)       # Lv5 Magikarp, Tackle


def new(book, template, party_bytes, dialogue, name, count):
    tid = len(book.trainers.files)
    row = bytearray(book.trainers.files[template])
    row[0], row[3], row[4:12], row[16] = 1, count, bytes(8), 0
    struct.pack_into('<I', row, 12, 1)
    book.trainers.files.append(bytes(row)); book.parties.files.append(party_bytes); book.names.append(name)
    while len(book.ofs) < 2 * (tid + 1):
        book.ofs.extend(struct.pack('<H', len(book.table)))
    struct.pack_into('<H', book.ofs, tid * 2, len(book.table))
    for kind, text in enumerate(dialogue):
        book.table.extend(struct.pack('<2H', tid, kind))
        book.lines.extend(ts.decode_messages(ts.encode_text([text], ts.PH))[1])
    return tid


while len(book.trainers.files) <= target:
    tid = new(book, 326, party, ['Test trainer %d here.' % len(book.trainers.files), 'Ouch!', 'After.'], book.names[326], 1)
book.save()
if target >= 996: ts._cover_common(rom, target)
d = rom.loadArm9().sections[0].data
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
rec = TABLE + 358 * 24
eid = struct.unpack_from('<H', d, rec + 16)[0]
g = events_decode(ev.files[eid])
a = bytearray(actor(9, 330, 3000 + target - 1, 8, 14, 0, 1))
struct.pack_into("<H", a, 6, 1); struct.pack_into("<H", a, 14, 5)
g[1].append(bytes(a))
ev.files.append(events_encode(g))
rom.setFileByName('a/0/3/2', ev.save())
main = rom.loadArm9(); dd = main.sections[0].data = bytearray(main.sections[0].data)
struct.pack_into('<H', dd, rec + 16, len(ev.files) - 1)
rom.arm9 = main.save(compress=True)
rom.saveToFile(sys.argv[2])
print('trainers', len(book.trainers.files))
