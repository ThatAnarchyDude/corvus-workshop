"""Dazzling Gleam (TM58) compatibility = the owner's list (data/dazzling-gleam-tm-owner-list.txt) UNION what 0052 already allowed (owner order 2026-10-23).

Compatibility is a bit (TM-1) per species in a/0/2/8 file 14 (44 bytes per species). Names are matched to the species text bank; regional
and other forms have blank names, so each form is reached through the engine's form-alias table (a/0/2/8 file 12: species-1076 -> base species):
every form of a listed species gets the bit too, EXCEPT the seven names that mean only a regional form, which get only that form:
 Raichu (Alolan 1128), Vulpix (Alolan 1131), Ninetales (Alolan 1132), Ponyta (Galarian 1157), Rapidash (Galarian 1158),
 Weezing (Galarian 1162), Braviary (Hisuian 1337); the Kanto/Unova versions do not get it.
Names in the list that match no species here (Calfby, Radish, Soritzee) are ignored and reported.
Nothing is cleared: this only adds bits to the 0052 data.

Usage: tm_gleam_union.py <in.nds> <out.nds> <owner list .txt>
"""
import json
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
from prototype import decode_messages

GLEAM_TM = 58
BLOCK = 44
REGIONAL = {'raichu': (1128,), 'vulpix': (1131,), 'ninetales': (1132,), 'ponyta': (1157,), 'rapidash': (1158,), 'weezing': (1162,), 'braviary': (1337,)}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower().replace('é', 'e'))


def patch(rom, list_path):
    text = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    inv = {v: k for k, v in json.load(open(__file__.replace('tm_gleam_union.py', 'text-map.json'))).items()}
    species = [''.join(inv.get(w, '?') for w in r if w != 65535) for r in decode_messages(text.files[237])[1]]
    owner = [x.strip() for x in open(list_path, encoding='utf-8').read().replace('\n', ' ').split(',') if x.strip()]
    ids = {}
    for i, n in enumerate(species):
        if norm(n):
            ids.setdefault(norm(n), []).append(i)
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    block = bytearray(addons.files[14])
    alias = struct.unpack('<%dH' % (len(addons.files[12]) // 2), addons.files[12])
    forms = {}
    for k, base in enumerate(alias):
        if base:
            forms.setdefault(base, []).append(1076 + k)
    def has(sp):
        return bool(block[sp * BLOCK + (GLEAM_TM - 1) // 8] >> ((GLEAM_TM - 1) % 8) & 1)
    def put(sp):
        block[sp * BLOCK + (GLEAM_TM - 1) // 8] |= 1 << ((GLEAM_TM - 1) % 8)
    before = sum(has(s) for s in range(len(species)))
    unmatched, added = [], []
    targets = set()
    for name in owner:
        k = norm(name)
        if k in REGIONAL:
            targets.update(REGIONAL[k])
        elif k in ids:
            for base in ids[k]:
                targets.add(base)
                targets.update(forms.get(base, []))
        else:
            unmatched.append(name)
    # forms of the species 0052 already allowed (so every form of a base that can learn it can too), except the regional-only names
    for sp in range(len(species)):
        if has(sp) and sp < 1076:
            targets.update(f for f in forms.get(sp, []) if norm(species[sp]) not in REGIONAL)
    for sp in sorted(targets):
        if not has(sp):
            put(sp)
            added.append(sp)
    addons.files[14] = bytes(block)
    rom.setFileByName('a/0/2/8', addons.save())
    return dict(species_before=before, species_after=before + len(added), added=len(added), unmatched=unmatched,
                added_names=sorted({species[s] or f'form {s}' for s in added})[:60])


if __name__ == '__main__':
    src, dst, lst = sys.argv[1:4]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom, lst))
    rom.saveToFile(dst)
