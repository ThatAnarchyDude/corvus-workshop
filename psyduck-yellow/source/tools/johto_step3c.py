"""Johto postgame, step 3c: the custom Mega Typhlosion and its stone, Typhlosionite (owner plan 2026-11-02; Typhlosion has no Mega in the game's data).

One more species row (1586, after the rows megas_part2.py added) holds Mega Typhlosion: a copy of Typhlosion (157) with Mega stats (base +100: HP 78, Atk 104, Def 98, Spe 110, SpA 149, SpD 95), types Fire/Dark, ability Sheer Force,
no evolution; its battle sprites are Typhlosion's with the flames recoloured (blue; purple when shiny), its icon is Typhlosion's. Typhlosion's form table already holds the Hisuian form in slot 0 (form 1), so the Mega is slot 1
(form 2, like Charizard's Mega Y): slot 1 = row | 0x8000 and one more Mega-table entry (species 157, Typhlosionite, form 2). Typhlosionite is a new item (3148) with Eonite's record and a recoloured Mega Stone sphere.
Code (overlay 129): the Mega table (116 entries at 0x023DEE80) grows in place by one entry (the 16 bytes after it are free); the alias/tag/form hooks get one more chained link for id 1586 (placed in the free
space after step 2's routine); the TM check literal (1585) becomes 1586; the Pokedex limit stays (a Mega id above it is rejected, as for the other Megas).
Also: Mr. Pokemon (step 3a) now hands over Typhlosionite to a Cyndaquil player, and every Kanto Mart's supplies vendor is regenerated with the new stone in its catalog (the GoTo sites of johto_step3b.py and Vermilion's table entry are retargeted).
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step3c.py <in.nds> <out.nds>"""
import colorsys
import copy
import json
import struct
import sys
from pathlib import Path
import ndspy.code
import ndspy.narc
import ndspy.rom
import johto_step3 as s3
import johto_step3b as s3b
import megas_part1 as p1
import mega_shop
from kanto_mart_shared import vendor_script
from mega_starter import EEVEE_STONE, HOOKS, MEGA_COUNT_SITES, MEGA_TABLE_SITES, Gap, _words
from new_eeveelutions import NAMES, starter
from prototype import decode_messages, encode_messages
from item_icons import recoloured
from viridian_tutorial import TABLE

BASE, NEW_ROW, FILLER = 157, 1586, 1560
STONE, STONE_TEMPLATE_RECORD, STONE_ICON = 3148, 3145, 660          # Eonite's item record, Charizardite X's sphere
OLD_ROWS = 1586
TM_LITERAL, TM_OLD = 0x023DB208, 1585
TABLE_AT, TABLE_ENTRIES, FREE_END = 0x023DEE80, 116, 0x023DF060
GAP_AT, GAP_END = 0x023DECE0, 0x023DEE14                              # free space after johto_step2's routine, before the old hook links' end
FORM_SLOT = 1                                                          # Typhlosion's form slot 0 is the Hisuian form; the Mega is form 2
STATS = (78, 104, 98, 110, 149, 95)                                    # HP, Atk, Def, Spe, SpA, SpD (base 78/84/78/100/109/85 + 100)
TYPES, ABILITY = (10, 17), 125                                         # Fire/Dark, Sheer Force
SPHERE_COLOURS = {2: (255, 150, 90), 3: (226, 74, 40), 4: (255, 226, 190), 5: (146, 38, 28), 6: (60, 76, 226), 7: (180, 192, 255),
                  9: (246, 120, 72), 10: (255, 196, 160), 11: (190, 60, 40)}


def hue_shift(nclr, degrees):
    """Recolour the warm (red/orange/yellow) colours of a 16-colour species palette; the blue body and the cream belly keep their colours."""
    out = bytearray(nclr)
    at = bytes(nclr).find(b'TTLP') + 0x18
    for i in range(1, 16):
        v = struct.unpack_from('<H', out, at + 2 * i)[0]
        r, g, b = (v & 31) / 31, ((v >> 5) & 31) / 31, ((v >> 10) & 31) / 31
        h, s, val = colorsys.rgb_to_hsv(r, g, b)
        deg = h * 360
        if s > 0.25 and (deg < 70 or deg > 340):
            r, g, b = colorsys.hsv_to_rgb(((deg + degrees) % 360) / 360, s, val)
            struct.pack_into('<H', out, at + 2 * i, round(r * 31) | (round(g * 31) << 5) | (round(b * 31) << 10))
    return bytes(out)


def grow(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    for name, stride, prefix in (('a/0/0/2', 1, 0), ('a/0/0/4', 6, 0), ('a/0/0/5', 4, 0), ('a/0/2/0', 1, 7), ('a/0/3/4', 1, 0), ('a/0/6/9', 1, 0), ('a/1/4/1', 1, 0),
                                 ('a/2/2/1', 1, 0), ('a/2/4/8', 1, 0), ('a/2/5/6', 1, 0)):
        a = narc(name)
        assert len(a.files) == prefix + OLD_ROWS * stride, (name, len(a.files))
        src = FILLER if name == 'a/0/3/4' else BASE                    # no evolution: the filler row's blank record
        a.files.extend(bytes(x) for x in a.files[prefix + src * stride:prefix + (src + 1) * stride])
    sprites = narc('a/0/0/4')
    sprites.files[NEW_ROW * 6 + 4] = hue_shift(sprites.files[BASE * 6 + 4], 195)     # normal: blue flames
    sprites.files[NEW_ROW * 6 + 5] = hue_shift(sprites.files[BASE * 6 + 5], 275)     # shiny: purple flames
    personal = narc('a/0/0/2')
    p = bytearray(personal.files[NEW_ROW])
    p[0:6] = bytes(STATS)
    p[6], p[7] = TYPES
    p[22] = p[23] = ABILITY
    personal.files[NEW_ROW] = bytes(p)
    t = narc('a/0/2/8')
    for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (14, 44), (15, 8)):
        b = bytes(t.files[i])
        assert len(b) == OLD_ROWS * width, (i, len(b))
        t.files[i] = b + b[BASE * width:(BASE + 1) * width]
    b = bytearray(t.files[11])
    assert len(b) == OLD_ROWS * 64
    assert struct.unpack_from('<H', b, BASE * 64 + 2 * FORM_SLOT)[0] == 0, 'Typhlosion form slot 1 is taken'
    b.extend(bytes(64))
    struct.pack_into('<H', b, BASE * 64 + 2 * FORM_SLOT, NEW_ROW | 0x8000)
    t.files[11] = bytes(b)
    for i, value in ((12, BASE), (13, None)):
        b = bytearray(t.files[i])
        assert len(b) == (OLD_ROWS - 1076) * 2, (i, len(b))
        b.extend(b[(FILLER - 1076) * 2:(FILLER - 1075) * 2])
        if value is not None:
            struct.pack_into('<H', b, (NEW_ROW - 1076) * 2, value)
        t.files[i] = bytes(b)
    for name, width in (('a/0/3/3', 136), ('a/1/8/0', 89)):
        a = narc(name)
        b = bytes(a.files[0])
        assert len(b) == OLD_ROWS * width, (name, len(b))
        a.files[0] = b + b[BASE * width:(BASE + 1) * width]
    text = narc('a/0/2/7')
    for bank in (237, 238):
        key, rows = decode_messages(text.files[bank])
        assert len(rows) == OLD_ROWS, (bank, len(rows))
        text.files[bank] = encode_messages(key, list(rows) + [rows[BASE]])
    # the stone
    items = narc('a/0/1/7')
    assert len(items.files) == STONE, len(items.files)
    items.files.append(bytes(items.files[STONE_TEMPLATE_RECORD]))
    gfx = narc('a/0/1/8')
    assert len(gfx.files) == STONE * 2 + 2, len(gfx.files)
    gfx.files.extend([bytes(gfx.files[STONE_ICON * 2 + 2]), recoloured(gfx.files[STONE_ICON * 2 + 3], SPHERE_COLOURS)])

    def add_text(bank, index, row):
        key, rows = decode_messages(text.files[bank])
        rows = copy.deepcopy(rows)
        assert index >= len(rows) or rows[index] == [65535], ('would replace text', bank, index)
        while len(rows) <= index:
            rows.append([65535])
        rows[index] = row
        text.files[bank] = encode_messages(key, rows)
    add_text(222, STONE, _words('Typhlosionite'))
    offset = STONE - 2685
    for bank, value in ((221, 'A Mega Stone for Typhlosion.'), (223, 'a Typhlosionite'), (224, 'Typhlosionites'), (829, 'Typhlosionite')):
        add_text(bank, offset, _words(value))
    for name, a in ns.items():
        rom.setFileByName(name, a.save())


def code(rom):
    ovs = rom.loadArm9Overlays()
    perm, battle, ov131 = ovs[129], ovs[130], ovs[131]
    perm.data, battle.data, ov131.data = bytearray(perm.data), bytearray(battle.data), bytearray(ov131.data)
    base = perm.ramAddress
    table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    assert table == TABLE_AT, hex(table)
    for site in MEGA_TABLE_SITES:
        assert struct.unpack_from('<I', battle.data, site - battle.ramAddress)[0] == table
    last = struct.unpack_from('<I', perm.data, TABLE_AT - base + (TABLE_ENTRIES - 1) * 4)[0]
    assert last == starter(NAMES.index('Ferreon')) | (EEVEE_STONE << 12) | (1 << 24), hex(last)
    end = TABLE_AT - base + TABLE_ENTRIES * 4
    assert end + 4 <= FREE_END - base and not any(perm.data[end:end + 4]), 'no room to grow the Mega table'
    struct.pack_into('<I', perm.data, end, BASE | (STONE << 12) | ((FORM_SLOT + 1) << 24))
    counts = []
    for site, _ in MEGA_COUNT_SITES:
        at = site - battle.ramAddress
        value = struct.unpack_from('<H', battle.data, at)[0]
        assert value & 0xFF == TABLE_ENTRIES, (hex(site), hex(value))
        struct.pack_into('<H', battle.data, at, value + 1)
        counts.append(hex(value + 1))
    assert not any(perm.data[GAP_AT - base:GAP_END - base]), 'the hook space is not free'
    gap = Gap(perm, GAP_AT, GAP_END - GAP_AT)
    p1.FIRST, p1.MEGA_FOR = NEW_ROW, ('Typhlosion',)
    alias = gap.put(struct.pack('<H', BASE))
    ovmap = {129: perm, 131: ov131}
    report = dict(counts=counts)
    for name, (ovid, site, lit) in HOOKS.items():
        ov = ovmap[ovid]
        at = site - ov.ramAddress + lit
        old = struct.unpack_from('<I', ov.data, at)[0]
        assert old & 1 and ov.ramAddress <= old - 1 < 0x23E0000, (name, hex(old))
        routine = p1._put(gap, p1._hook(old, 'forms' if name == 'forms' else 'alias', alias), 8 if name == 'forms' else 12)
        struct.pack_into('<I', ov.data, at, routine | 1)
        report[name] = (hex(old), hex(routine))
    at = TM_LITERAL - base
    assert struct.unpack_from('<I', perm.data, at)[0] == TM_OLD, 'TM literal moved'
    struct.pack_into('<I', perm.data, at, NEW_ROW)
    for ov in (perm, battle, ov131):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    report['gap_left'] = gap.end - gap.at
    return report


def restock(rom, repo='.'):
    """Regenerate the supplies vendor of every Kanto Mart with Typhlosionite in the catalog."""
    items, _ = mega_shop.mega_stones(rom)
    items = sorted(set(items) | {STONE})
    stages = json.loads((Path(repo) / 'data/kanto-mart-inventory.json').read_text())['verified_stages']
    both = s3b.combined(stages)
    assert len(items) + max(len(s['supplies']) for s in both) <= s3b.CAPACITY
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    fid = rom.filenames.idOf('a/0/1/2')
    arc = ndspy.narc.NARC(rom.files[fid])
    prelude = bytes.fromhex('4900dc0560006800')
    report = {}
    for m in (360,) + s3b.MARTS:
        bank_id = struct.unpack_from('<H', d, TABLE + 24 * m + 6)[0]
        bank = bytearray(arc.files[bank_id])
        if m == 360:
            # Vermilion: the vendor scripts are the bank's entries 0 (supplies) and 1 (balls)
            at = struct.unpack_from('<I', bank, 0)[0] + 4
            assert bank[at:at + 8] == prelude, 'Vermilion entry 0 is not a vendor script'
            bank.extend(bytes(-len(bank) % 4))
            start = len(bank)
            bank.extend(vendor_script(stages, 'supplies', items))
            struct.pack_into('<I', bank, 0, start - 4)
            report[m] = ('entry 0', start)
        else:
            sites = []
            for p in range(0, len(bank) - 6):
                if struct.unpack_from('<H', bank, p)[0] == 0x16:
                    t = p + 6 + struct.unpack_from('<i', bank, p + 2)[0]
                    if 8 <= t < len(bank) and bank[t - 8:t] == prelude:
                        sites.append(p)
            assert len(sites) in (1, 2), (m, sites)
            single = len(sites) == 1
            bank.extend(bytes(-len(bank) % 4))
            start = len(bank)
            bank.extend(vendor_script(both if single else stages, 'supplies', items))
            site = sites[0]
            bank[site:site + 6] = struct.pack('<Hi', 0x16, start + s3b.PRELUDE - (site + 6))
            report[m] = (site, start)
        arc.files[bank_id] = bytes(bank)
    rom.files[fid] = arc.save()
    return report


def patch(rom, repo='.'):
    grow(rom)
    report = code(rom)
    s3.mr_pokemon_scene(rom, 0x4128, 0x413C, (s3.STONES[0], (STONE, 'TYPHLOSIONITE'), s3.STONES[2]))
    report['marts'] = restock(rom, repo)
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
