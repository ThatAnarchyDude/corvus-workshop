"""Novareon's Pokedex entry text showed only fragments ("the light of ... a thousand"): dex_novareon.py encoded its line breaks with the dialogue encoder, which turns
every break after the first into a different code. Pokedex entries separate their lines with the single code 0xE000. This rewrites row 500 (and 1581) of the entry-text
bank (803) with the right codes.

The wording is still the placeholder from dex_novareon.py (owner to replace).

Usage: dex_text_fix.py <in.nds> <out.nds>
"""
import json
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from prototype import decode_messages, encode_messages

ENTRY = ('It evolved under the light of a\nthousand stars. The rainbow disk\nof its tail shows when it Mega Evolves.')
BANK, ROWS = 803, (500, 1581)
TEXT_MAP = json.loads((Path(__file__).resolve().parent / 'text-map.json').read_text())


def encode(text):
    return [0xE000 if c == '\n' else TEXT_MAP[c] for c in text] + [0xFFFF]


def patch(rom):
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    key, rows = decode_messages(texts.files[BANK])
    for row in ROWS:
        rows[row] = encode(ENTRY)
    texts.files[BANK] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    return dict(rows=ROWS)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
