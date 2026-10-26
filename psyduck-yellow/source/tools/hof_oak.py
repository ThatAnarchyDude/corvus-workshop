"""The Hall of Fame room's narration is Yellow's Oak speech instead of HeartGold's Lance (owner-visible leftover noted 2026-10-23).

Text bank 528 (rows 0 and 1, the two copies HG keeps for the male/female player) is only read by the Hall of Fame room; Yellow's _HallOfFameOakText replaces it.
Note: the postgame Johto Hall of Fame uses the same room, so it will also be Oak's speech until that part is revisited.

Usage: hof_oak.py <in.nds> <out.nds> <pokeyellow source>
"""
import sys
import ndspy.narc
import ndspy.rom
import yellow_text
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages, encode_messages

BANK = 528


def patch(rom, source):
    line = yellow_text.message(source, 'HallOfFame', '_HallOfFameOakText')
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    key, rows = decode_messages(texts.files[BANK])
    assert len(rows) == 2, len(rows)
    new = decode_messages(encode_text([line], PH))[1][0]
    rows[0] = rows[1] = new
    texts.files[BANK] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    return dict(bank=BANK, chars=len(new))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
