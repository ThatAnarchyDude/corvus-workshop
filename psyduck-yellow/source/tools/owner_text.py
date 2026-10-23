"""The owner's own wording (from Eevee-New-Horizons.pdf on the Desktop, pages 8, 13 and 14) for Novareon and the two Eevee-family Mega Stones.

 - Novareon's Pokedex category "Star Chart Pokemon" (banks 816 and 823, rows 500 and 1581) and its entry (bank 803, rows 500 and 1581, Pokedex line break 0xE000):
   "At dusk, it aligns its broad tail with the first star to appear. Even under heavy cloud, it can lead its group back to the same resting hollow."
 - Item descriptions (bank 221): Eonite (row 460) "A Mega Stone to be held by Eevee or an Evolution of Eevee. A Trainer's Key Stone enables Mega Evolution." and
   Novareonite (row 462) "A Mega Stone to be held by Novareon. A Trainer's Key Stone enables it to Mega Evolve into Mega Novareon."
Mega Novareon's own entry ("It spreads its broad tail beside mountain pools ...") has no page of its own in the game yet (Mega forms live inside the base entry); it is kept in
MEGA_ENTRY for when a forms page for it exists.

Usage: owner_text.py <in.nds> <out.nds>
"""
import json
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages, encode_messages

TEXT_MAP = json.loads((Path(__file__).resolve().parent / 'text-map.json').read_text())
CATEGORY = 'Star Chart Pokémon'
ENTRY = 'At dusk, it aligns its broad tail\nwith the first star to appear. Even\nunder heavy cloud, it can lead its group\nback to the same resting hollow.'
MEGA_ENTRY = ('It spreads its broad tail beside mountain pools, reflecting starlight onto the shallows. '
              'Small nocturnal Pokémon gather at the bright edge to drink, then slip away beneath its ruff.')
# The bag's description window shows only two lines of about 29 characters and does not scroll, so the owner's longer wording is shortened to fit
# (full text: "A Mega Stone to be held by Eevee or an Evolution of Eevee. A Trainer's Key Stone enables Mega Evolution." and
#  "A Mega Stone to be held by Novareon. A Trainer's Key Stone enables it to Mega Evolve into Mega Novareon."). A line break is 0xE000.
EONITE = "A Mega Stone held by Eevee\nor an Evolution of Eevee."
NOVAREONITE = "A Mega Stone held by Novareon\nto enable Mega Novareon."
ROWS = (500, 1581)


def dex_row(text):
    return [0xE000 if c == '\n' else 0x1B3 if c == "'" else TEXT_MAP[c] for c in text] + [0xFFFF]


def patch(rom):
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    for bank, text in ((816, CATEGORY), (823, CATEGORY), (803, ENTRY)):
        key, rows = decode_messages(texts.files[bank])
        for row in ROWS:
            rows[row] = dex_row(text)
        texts.files[bank] = encode_messages(key, rows)
    key, rows = decode_messages(texts.files[221])
    for row, text in ((460, EONITE), (462, NOVAREONITE)):
        rows[row] = dex_row(text)
    texts.files[221] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    return dict(rows=ROWS)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
