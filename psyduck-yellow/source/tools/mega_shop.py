"""Every Mega Stone is in the shared Kanto Mart pool from the first stage, at buy price 0.

The Stones are the item column of the engine's Mega table (stock stones plus Eonite, Psyduckite, the starter Eevee line's Eonite entries and Novareonite). Their item
records already carry price 0; this asserts that and regenerates the Vermilion Mart's two vendor scripts with the
Stones appended to the supplies vendor's catalog in every badge stage. Marts built later should pass the same list
as `extra` to kanto_mart_shared.vendor_script.
"""
import json
import struct
from pathlib import Path
import ndspy.narc
from kanto_mart_shared import vendor_script
from viridian_tutorial import TABLE

MART_MAP = 360
TABLE_SITE = 0x23CF9D4
ENTRIES = 106                                      # 95 stock entries, starter Eevee, starter Psyduck, nine starter-line evolutions
CAPACITY = 254                                     # inline_catalog limit


def mega_stones(rom):
    ovs = rom.loadArm9Overlays()
    battle, perm = ovs[130], ovs[129]
    table = struct.unpack_from('<I', battle.data, TABLE_SITE - battle.ramAddress)[0]
    holder = battle if battle.ramAddress <= table < battle.ramAddress + len(battle.data) else perm
    at = table - holder.ramAddress
    entries = [struct.unpack_from('<I', holder.data, at + 4 * i)[0] for i in range(ENTRIES)]
    assert entries[95] == 1561 | (3145 << 12) | (1 << 24) and entries[96] == 1563 | (3146 << 12) | (1 << 24)   # Eonite, Psyduckite
    assert entries[105] == 1581 | (3147 << 12) | (1 << 24)                                                       # Novareonite
    return sorted({(e >> 12) & 0xFFF for e in entries}), len(entries)


def patch(rom, repo, extra=()):
    items, count = mega_stones(rom)
    items = sorted(set(items) | set(extra))
    assert len(items) >= 90, len(items)
    records = ndspy.narc.NARC(rom.getFileByName('a/0/1/7'))
    for i in items:
        assert struct.unpack_from('<H', records.files[i], 0)[0] == 0, f'item {i} has a buy price'
    stages = json.loads((Path(repo) / 'data/kanto-mart-inventory.json').read_text())['verified_stages']
    assert len(stages) == 9 and len(items) + max(len(s['supplies']) for s in stages) <= CAPACITY
    main = rom.loadArm9()
    d = main.sections[0].data
    sid = struct.unpack_from('<H', d, TABLE + MART_MAP * 24 + 6)[0]
    arc = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    native = arc.files[sid]
    bank = bytearray(native)
    for entry, vendor in ((0, 'supplies'), (1, 'balls')):
        bank.extend(bytes(-len(bank) % 4))
        at = len(bank)
        bank.extend(vendor_script(stages, vendor, items if vendor == 'supplies' else ()))
        struct.pack_into('<I', bank, entry * 4, at - entry * 4 - 4)
    assert bank[8:len(native)] == native[8:]
    arc.files.append(bytes(bank))
    rom.files[rom.filenames.idOf('a/0/1/2')] = arc.save()
    d2 = main.sections[0].data = bytearray(d)
    struct.pack_into('<H', d2, TABLE + MART_MAP * 24 + 6, len(arc.files) - 1)
    rom.arm9 = main.save(compress=True)
    return dict(stones=len(items), first=items[:3], price=0, vendor='supplies', stages=len(stages), old_script=sid, script=len(arc.files) - 1)
