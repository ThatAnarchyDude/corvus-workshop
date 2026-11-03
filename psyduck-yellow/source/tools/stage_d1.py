"""Stage D1 of the starter redesign: Mega stat rule and one-Pokedex-entry-per-species fix (owner orders 2026-10-29, 2026-11-01). Data only.
 - Every Mega form's six base stats become its OWN base form's stats + 20 each (+120 BST), stock Megas included (owner: "ALL Megas", option B).
   Mega forms are found from the Mega table (107 entries, species + stone): the flagged (reverting) form rows of each listed species that are not Gigantamax
   rows (a Gigantamax row keeps the base stats; a project Mega row, id >= 1562, counts even while it still equals its base). A form shared by several bases
   (the shared Mega Psyduck: starter Psyduck and starter Golduck) takes the strongest base. Re-running on an already boosted ROM re-derives the same numbers.
 - The Pokedex copy of the alias table (overlay 129) sent starter Golduck (1535) and the nine new Eeveelutions (1536-1553) to species 0, so nothing registered.
   Starter Golduck now registers as Golduck (55); each starter Eeveelution (1545-1553) registers as its ordinary species (1536-1544), which registers as itself
   until the Pokedex gets a real slot for it (page text and number come later).
Usage (from yellow-heartgold, PYTHONPATH=tools): stage_d1.py <in.nds> <out.nds>"""
import os
import re
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
from mega_starter import MEGA_TABLE_SITES

STARTER_GOLDUCK, GOLDUCK = 1535, 55
FIRST_NEW, NEW_COUNT = 1536, 9
FIRST_FORM = 1076
BONUS = 20
ENTRIES = 107


def mega_table(rom):
    ovs = rom.loadArm9Overlays()
    battle = ovs[130]
    table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    holder = battle if battle.ramAddress <= table < battle.ramAddress + len(battle.data) else ovs[129]
    raw = holder.data[table - holder.ramAddress:table - holder.ramAddress + 4 * ENTRIES]
    return [struct.unpack_from('<I', raw, 4 * i)[0] & 0xFFF for i in range(ENTRIES)]


def patch(rom):
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    forms = addons.files[11]
    pe = ndspy.narc.NARC(rom.getFileByName('a/0/0/2'))
    bst = lambda sp: sum(pe.files[sp][:6])
    best = {}                                          # Mega form row -> base species with the highest stat total
    for sp in sorted(set(mega_table(rom))):
        for k in range(32):
            v = struct.unpack_from('<H', forms, sp * 64 + 2 * k)[0]
            if not v & 0x8000:
                continue
            f = v & 0x7FFF
            if f < 1562 and bytes(pe.files[f][:6]) == bytes(pe.files[sp][:6]):
                continue                               # Gigantamax-style row: same stats as its base
            if f not in best or bst(sp) > bst(best[f]):
                best[f] = sp
    for f, sp in (best.items() if os.environ.get('MEGA_BONUS') == '1' else ()):     # the +120 rule waits (owner 2026-11-01): off unless MEGA_BONUS=1
        row = bytearray(pe.files[f])
        row[0:6] = bytes(min(255, pe.files[sp][i] + BONUS) for i in range(6))
        pe.files[f] = bytes(row)
    rom.setFileByName('a/0/0/2', pe.save())
    # Pokedex alias copy in overlay 129 (the copy of a/0/2/8 file 12 made by dex_fix.py)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    data = bytearray(perm.data)
    original = bytes(addons.files[12])
    copies = [m.start() for m in re.finditer(re.escape(original[:64]), bytes(data))]   # dex_fix.py's copy and dex_novareon.py's copy
    assert copies, 'alias copy not found'
    for at in copies:
        set_row = lambda sp, to: struct.pack_into('<H', data, at + 2 * (sp - FIRST_FORM), to)
        assert struct.unpack_from('<H', data, at + 2 * (STARTER_GOLDUCK - FIRST_FORM))[0] == 0
        set_row(STARTER_GOLDUCK, GOLDUCK)
        for i in range(NEW_COUNT):
            set_row(FIRST_NEW + i, FIRST_NEW + i)
            set_row(FIRST_NEW + NEW_COUNT + i, FIRST_NEW + i)
    perm.data = data
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(mega_rows=len(best), sample={f: (best[f], [pe.files[f][i] for i in range(6)]) for f in sorted(best)[:3]})


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
