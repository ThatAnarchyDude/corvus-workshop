"""Johto postgame, step 3b: the shared Kanto Mart stock (badge stages + every Mega Stone at price 0) in ALL Kanto Marts (owner plan 2026-11-02).

Vermilion (map 360) already has it (kanto_mart_shared.py, mega_shop.py). The native Marts all call the shop the same way: `CallStd 2011` (greeting) + a 2-byte command (0x32/0x36) + `SetVar 0x8004 <id>` + `CallStd 2048/2052`.
In every shop script of the maps below that first `CallStd 2011` + command (6 bytes) becomes a GoTo into a vendor script appended to the map's script bank (the native tail stays as dead code):
 - maps with two clerks (Viridian, Saffron, Lavender, Fuchsia): the first shop script (in bank order) is the supplies vendor with the Mega Stones, the second the Poke Ball vendor, as in Vermilion;
 - maps with a single clerk (Pewter, Cerulean): one vendor with the supplies and the balls together plus the Mega Stones.
Left alone: the Celadon Dept Store floors (371-374), the Indigo Plateau shop (300) and Cinnabar (no Mart in this ROM), as in the inventory file ("league and Johto shops unchanged").
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step3b.py <in.nds> <out.nds>"""
import json
import struct
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
import mega_shop
from kanto_mart_shared import vendor_script
from viridian_tutorial import TABLE

MARTS = (500, 426, 474, 409, 433, 478)               # Viridian, Cerulean, Pewter, Saffron, Lavender, Fuchsia
CALL_GREETING = bytes([0x14, 0, 0xDB, 7])             # CallStd 2011
SHOP_COMMANDS = (0x32, 0x36)
PRELUDE = 8                                           # PlaySE 1500 (4) + LockAll (2) + FacePlayer (2): skipped, the native script has done them
CAPACITY = 254


def combined(stages):
    out = json.loads(json.dumps(stages))
    for stage in out:
        stage['supplies'] = list(dict.fromkeys(stage['supplies'] + stage['balls']))
    return out


def patch(rom, repo='.'):
    items, _ = mega_shop.mega_stones(rom)
    stages = json.loads((Path(repo) / 'data/kanto-mart-inventory.json').read_text())['verified_stages']
    assert len(stages) == 9
    both = combined(stages)
    assert len(items) + max(len(s['supplies']) for s in both) <= CAPACITY, 'combined stock exceeds the catalog capacity'
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    fid = rom.filenames.idOf('a/0/1/2')
    arc = ndspy.narc.NARC(rom.files[fid])
    owners = {}
    for m in range(0, 800):
        try:
            owners.setdefault(struct.unpack_from('<H', d, TABLE + 24 * m + 6)[0], []).append(m)
        except struct.error:
            break
    report = {}
    for m in MARTS:
        bank_id = struct.unpack_from('<H', d, TABLE + 24 * m + 6)[0]
        assert owners[bank_id] == [m], (m, owners[bank_id])
        bank = bytearray(arc.files[bank_id])
        sites = []
        at = bank.find(CALL_GREETING)
        while at >= 0:
            if struct.unpack_from('<H', bank, at + 4)[0] in SHOP_COMMANDS:
                sites.append(at)
            at = bank.find(CALL_GREETING, at + 1)
        assert 1 <= len(sites) <= 2, (m, sites)
        vendors = ('supplies', 'balls') if len(sites) == 2 else ('supplies',)
        for site, vendor in zip(sites, vendors):
            raw = vendor_script(both if len(sites) == 1 else stages, vendor, items if vendor == 'supplies' else ())
            assert raw[:PRELUDE] == bytes.fromhex('49 00 dc 05 60 00 68 00'.replace(' ', '')), 'unexpected vendor prelude'
            bank.extend(bytes(-len(bank) % 4))
            start = len(bank)
            bank.extend(raw)
            bank[site:site + 6] = struct.pack('<Hi', 0x16, start + PRELUDE - (site + 6))
        arc.files[bank_id] = bytes(bank)
        report[m] = dict(bank=bank_id, sites=sites, vendors=vendors, bytes=len(bank))
    rom.files[fid] = arc.save()
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
