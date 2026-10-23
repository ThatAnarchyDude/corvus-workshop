"""Oak's Pokedex evaluation talks about the Kanto Pokedex now (owner order 2026-10-23: the regional Pokedex is Kanto's).

"Johto" -> "Kanto" (same length, so the codes are swapped in place) in the menu entry "Evaluate Johto Pokedex" (text bank 271, row 12) and in Oak's evaluation lines
(bank 666, rows 18 "Have Johto Pokedex Evaluated", 22, 23, 26 the complete-Pokedex speeches, 51 the Safari Zone remark).
The "JOHTO" button on the Pokedex's AREA page (bank 802 row 65) really is the Johto map and stays.

Usage: oak_kanto_dex.py <in.nds> <out.nds>
"""
import json
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from prototype import decode_messages, encode_messages

TEXT_MAP = json.loads((Path(__file__).resolve().parent / 'text-map.json').read_text())
ROWS = {271: (12,), 666: (18, 22, 23, 26, 51)}
OLD = [TEXT_MAP[c] for c in 'Johto']
NEW = [TEXT_MAP[c] for c in 'Kanto']


def patch(rom):
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    swapped = 0
    for bank, rows_to_fix in ROWS.items():
        key, rows = decode_messages(texts.files[bank])
        for index in rows_to_fix:
            row = list(rows[index])
            for i in range(len(row) - 4):
                if row[i:i + 5] == OLD:
                    row[i:i + 5] = NEW
                    swapped += 1
            rows[index] = row
        texts.files[bank] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    return dict(swapped=swapped)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
