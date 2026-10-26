"""The Sandwich's bag description showed another text's line (known gap since 0044).

The engine reads item 1830's description from text bank 850 row 1 (the row after the first expanded-item row), a bank no map header uses any more (it only holds the
old parcel-scene dialogue from an early prototype; verified: no map's text bank id is 850 in the ROM). Row 1 now holds a two-line description that fits the bag window.
The wording is a placeholder written by Claude: the owner has not supplied one.

Usage: sandwich_desc.py <in.nds> <out.nds>
"""
import sys
import ndspy.narc
import ndspy.rom
from owner_text import dex_row
from prototype import decode_messages, encode_messages

BANK, ROW = 850, 1
TEXT = 'A hearty sandwich that makes\ncertain Eevee evolve.'


def patch(rom):
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    key, rows = decode_messages(texts.files[BANK])
    rows[ROW] = dex_row(TEXT)
    texts.files[BANK] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    return dict(bank=BANK, row=ROW)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
