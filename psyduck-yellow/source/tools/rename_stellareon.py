"""Novareon -> Stellareon, Novareonite -> Stellareonite (owner order 2026-11-01). Text only: species ids and everything else stay.
Rows changed in the message NARC a/0/2/7: species names (banks 237, 238: ids 500, 1581, 1582), Pokedex name (817: 500, 1581), the Mega Stone's name, article forms, plural and description (item 3147: banks 221-224, 829 row 462 / 3147).
Usage (from yellow-heartgold, PYTHONPATH=tools): rename_stellareon.py <in.nds> <out.nds>"""
import json
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from prototype import decode_messages, encode_messages

TEXT_MAP = json.loads((Path(__file__).resolve().parent / 'text-map.json').read_text())
INV = {v: k for k, v in TEXT_MAP.items()}


def text(row):
    return ''.join(INV.get(w, '?') for w in row if w != 65535)


ROWS = {237: (500, 1581, 1582), 238: (500, 1581, 1582), 817: (500, 1581), 221: (462,), 222: (3147,), 223: (462,), 224: (462,), 829: (462,)}
PAIRS = (('Novareon', 'Stellareon'), ('NOVAREON', 'STELLAREON'))


def replace(row):
    """Swap the letter runs inside a message row (other codes, such as the line break, stay as they are)."""
    out = list(row)
    for old, new in PAIRS:
        o, n = [TEXT_MAP[c] for c in old], [TEXT_MAP[c] for c in new]
        i = 0
        while i <= len(out) - len(o):
            if out[i:i + len(o)] == o:
                out[i:i + len(o)] = n
                i += len(n)
            else:
                i += 1
    return out


def patch(rom):
    t = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    changed = []
    for bank, indexes in ROWS.items():
        key, rows = decode_messages(t.files[bank])
        for index in indexes:
            new = replace(rows[index])
            assert new != rows[index], (bank, index, text(rows[index]))
            rows[index] = new
            changed.append((bank, index, text(new)))
        t.files[bank] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', t.save())
    return changed


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    for c in patch(rom):
        print(c)
    rom.saveToFile(sys.argv[2])
