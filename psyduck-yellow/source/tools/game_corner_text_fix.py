"""Celadon Game Corner: the native NPCs read garbage after the Rocket Hideout patch (found by tools/audit_messages.py, 2026-10-23).

rocket_hideout.game_corner() gave the map a fresh three-line text bank (the Rocket guard's lines), so the map's own 24 scripts, which show messages 0-17 of the original
23-row bank (text file 508), pointed past the end of the new bank. The new bank is now the original 23 rows followed by the three Rocket lines (rows 23-25), and the guard's
script (the last one in the map's script bank) shows rows 23-25 instead of 0-2.

Usage: game_corner_text_fix.py <in.nds> <out.nds>
"""
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import script_bank
from parcel_quest import split_bank
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

GAME_CORNER, ORIGINAL_TEXT, ORIGINAL_ROWS, GUARD_LINES = 381, 508, 23, 3


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    at = TABLE + GAME_CORNER * 24
    sid, tid = struct.unpack_from('<H', d, at + 6)[0], struct.unpack_from('<H', d, at + 10)[0]
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    key, old_rows = decode_messages(texts.files[ORIGINAL_TEXT])
    _, guard_rows = decode_messages(texts.files[tid])
    assert len(old_rows) == ORIGINAL_ROWS and len(guard_rows) == GUARD_LINES, (len(old_rows), len(guard_rows))
    bank = split_bank(scripts.files[sid])
    guard = bytearray(bank[-1])
    hits = list(re.finditer(rb'\x2d\x00([\x00\x01\x02])\x32\x00', bytes(guard)))
    assert len(hits) == 3, len(hits)
    for h in hits:
        guard[h.start(1)] = ORIGINAL_ROWS + h.group(1)[0]
    bank[-1] = bytes(guard)
    scripts.files.append(script_bank(bank))
    texts.files.append(encode_messages(key, old_rows + guard_rows))
    struct.pack_into('<H', d, at + 6, len(scripts.files) - 1)
    struct.pack_into('<H', d, at + 10, len(texts.files) - 1)
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    rom.arm9 = main.save(compress=True)
    return dict(rows=ORIGINAL_ROWS + GUARD_LINES, scripts=len(bank))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
