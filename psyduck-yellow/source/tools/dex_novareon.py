"""Novareon gets its own Pokedex entry, National No. 1026, at the end of the National Pokedex (owner order 2026-10-23).

Problem: dex_fix.py registered Novareon (species 1581, Mega 1582) as Umbreon. The Pokedex code limits species ids to 1075 (the flag struct itself has room up to
id 8160) and its text banks (weight, height, category, name, entry text) stop at row 1534.
Fix:
 - The six ARM9 pool literals and the one overlay-18 literal that hold the limit 1075 become 1582.
 - The seven Pokedex text banks (803, 812-817, 823) grow to 1583 rows (new rows copy the blank "-----" row); Novareon's row 1581 gets its category, name and entry text
   (placeholders the owner can replace, see TEXT below) and Umbreon's height and weight strings.
 - dex_fix's two routines are replaced by new copies (a fresh gap in overlay 129): the species wrapper maps Mega Novareon (1582) to 1581 and leaves 1581 alone, and the
   number routine answers 1026 for species 1581 in the National Pokedex (the regional dex has no Novareon). The three hooks are repointed.
 - The National sort list (a/2/1/4 file 11) gets 1581 appended as entry 1026.

Usage: dex_novareon.py <in.nds> <out.nds>
"""
import json
import struct
import sys
from pathlib import Path
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap
from prototype import decode_messages, encode_messages

NOVAREON, MEGA_NOVAREON, NATIONAL = 1581, 1582, 1026
DEX_SPECIES = NOVAREON
LIMIT_OLD, LIMIT_NEW = 1075, 1582
LIMIT_SITES = (0x2029E3C, 0x2029E78, 0x2029EF0, 0x2029F44, 0x2029FA8, 0x2029FF4)
OV18_LIMIT = 0x21E5A9C
BANKS = (803, 812, 813, 814, 815, 816, 817, 823)
PAD_ROW = 494                              # '-----' / '????.? lbs.' / '????? Pokemon'
NUMBER_HOOK, SEEN_READ, CAUGHT_READ = 0x020FF114, 0x0202A37A, 0x0202A442
GET_MON_DATA, REGIONAL_NUM = 0x0206E540, 0x0207185C
FIRST_FORM = 1076
RESERVE = 1368
ENTRY = 89
TEXT = {                                    # placeholder wording for the owner to replace (marked in SESSION-HANDOFF.md)
    816: 'Starlit Pokémon', 823: 'Starlit Pokémon', 817: 'NOVAREON',
    803: 'It evolved under the light of a\nthousand stars. The rainbow disk\nof its tail shows when it Mega Evolves.',
}


def bl(source, target):
    off = target - (source + 4)
    assert -(1 << 22) <= off < (1 << 22) and off % 2 == 0, hex(off)
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xF800 | ((off >> 1) & 0x7FF))


def read_bl(data, base, site):
    h1, h2 = struct.unpack_from('<HH', data, site - base)
    off = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if off & 0x400000:
        off -= 0x800000
    return site + 4 + off


def encode_row(text, charmap):
    from opening import encode_text
    from parcel_quest import PH
    return decode_messages(encode_text([text], PH))[1][0]


def patch(rom):
    # ---- 1. the code: new routines with Novareon -> 500
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    table = bytearray(addons.files[12])
    count = len(table) // 2
    struct.pack_into('<H', table, 2 * (NOVAREON - FIRST_FORM), NOVAREON)
    struct.pack_into('<H', table, 2 * (MEGA_NOVAREON - FIRST_FORM), NOVAREON)
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    table_at = gap.put(bytes(table))
    wrapper = gap.code(f'''push {{lr}}
ldr r3, getmon
blx r3
lsls r1, r0, #16
lsrs r1, r1, #16
ldr r2, first
cmp r1, r2
blo done
subs r1, r1, r2
ldr r2, count
cmp r1, r2
bhs done
lsls r1, r1, #1
ldr r2, tbl
ldrh r1, [r2, r1]
cmp r1, #0
beq done
movs r0, r1
done:
pop {{pc}}
.align 2
getmon: .word {GET_MON_DATA | 1}
first: .word {FIRST_FORM}
count: .word {count}
tbl: .word {table_at}
''')
    number = gap.code(f'''push {{lr}}
ldr r2, first
cmp r1, r2
blo skip
subs r2, r1, r2
ldr r3, count
cmp r2, r3
bhs skip
lsls r2, r2, #1
ldr r3, tbl
ldrh r2, [r3, r2]
cmp r2, #0
beq skip
movs r1, r2
skip:
cmp r0, #0
bne national
movs r0, r1
ldr r3, regional
blx r3
pop {{pc}}
national:
ldr r0, novadex
cmp r1, r0
bne ordinary
ldr r0, novanumber
pop {{pc}}
ordinary:
ldr r0, c493
cmp r1, r0
ble ret
subs r1, #50
ret:
movs r0, r1
pop {{pc}}
.align 2
first: .word {FIRST_FORM}
count: .word {count}
tbl: .word {table_at}
regional: .word {REGIONAL_NUM | 1}
c493: .word 493
novadex: .word {DEX_SPECIES}
novanumber: .word {NATIONAL}
''')
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    base = section.ramAddress
    at = NUMBER_HOOK - base
    assert bytes(section.data[at:at + 4]) == bytes.fromhex('004a1047'), 'dex_fix number hook missing'
    struct.pack_into('<I', section.data, at + 4, number | 1)
    for site in (SEEN_READ, CAUGHT_READ):
        old = read_bl(section.data, base, site)
        assert 0x023C0000 <= old < 0x023E0000, hex(old)               # dex_fix's wrapper in overlay 129
        section.data[site - base:site - base + 4] = bl(site, wrapper)
    rom.arm9 = main.save(compress=True)
    for site in LIMIT_SITES:
        at = site - base
        assert struct.unpack_from('<I', section.data, at)[0] == LIMIT_OLD, hex(site)
        struct.pack_into('<I', section.data, at, LIMIT_NEW)
    rom.arm9 = main.save(compress=True)
    ov18 = rom.loadArm9Overlays()[18]
    ov18.data = bytearray(ov18.data)
    at = OV18_LIMIT - ov18.ramAddress
    assert struct.unpack_from('<I', ov18.data, at)[0] == LIMIT_OLD
    struct.pack_into('<I', ov18.data, at, LIMIT_NEW)
    rom.files[ov18.fileID] = ov18.save(compress=False)
    # ---- 3. text rows: every Pokedex bank grows to 1583 rows; row 1581 is Novareon's
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    for bank in BANKS:
        key, rows = decode_messages(texts.files[bank])
        rows = list(rows) + [rows[PAD_ROW]] * (MEGA_NOVAREON + 1 - len(rows))
        if bank in (812, 813, 814, 815):                               # height and weight: Umbreon's strings
            rows[NOVAREON] = rows[197]
        else:
            rows[NOVAREON] = encode_row(TEXT[bank], None)
        texts.files[bank] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    # ---- 4. the National sort list gets entry 1026
    lists = ndspy.narc.NARC(rom.getFileByName('a/2/1/4'))
    cur = struct.unpack('<%dH' % (len(lists.files[11]) // 2), bytes(lists.files[11]))
    assert len(cur) == 1025 and cur[-1] == 1075, (len(cur), cur[-1])
    lists.files[11] = struct.pack('<%dH' % (len(cur) + 1), *cur, NOVAREON)
    rom.setFileByName('a/2/1/4', lists.save())
    # ---- 5. the height and weight arrays (a/2/1/4 files 0 and 1, one u32 per species id) grow to 1583 entries; Novareon and its Mega take Umbreon's values
    lists = ndspy.narc.NARC(rom.getFileByName('a/2/1/4'))
    for index in (0, 1):
        raw = bytes(lists.files[index])
        entries = list(struct.unpack('<%dI' % (len(raw) // 4), raw))
        entries += [0] * (MEGA_NOVAREON + 1 - len(entries))
        entries[NOVAREON] = entries[MEGA_NOVAREON] = entries[197]
        lists.files[index] = struct.pack('<%dI' % len(entries), *entries)
    rom.setFileByName('a/2/1/4', lists.save())
    # ---- 5b. per-species byte array (a/2/1/4 file 2) and three per-species NARCs of the Pokedex app grow to 1583 entries (Novareon and Mega: Umbreon's)
    lists = ndspy.narc.NARC(rom.getFileByName('a/2/1/4'))
    raw = bytearray(lists.files[2])
    raw += bytes(MEGA_NOVAREON + 1 - len(raw))
    raw[NOVAREON] = raw[MEGA_NOVAREON] = raw[197]
    lists.files[2] = bytes(raw)
    rom.setFileByName('a/2/1/4', lists.save())
    for path in ('a/2/5/6', 'a/2/4/8', 'a/2/2/1'):
        narc = ndspy.narc.NARC(rom.getFileByName(path))
        blank = bytes(narc.files[PAD_ROW])
        narc.files.extend(blank for _ in range(MEGA_NOVAREON + 1 - len(narc.files)))
        narc.files[NOVAREON] = narc.files[MEGA_NOVAREON] = bytes(narc.files[197])
        rom.setFileByName(path, narc.save())
    # ---- 6. footprints (a/0/6/9, one RGCN per species id, 1101 files) grow to 1583; Novareon and its Mega take Umbreon's footprint, the gap a plain one
    prints = ndspy.narc.NARC(rom.getFileByName('a/0/6/9'))
    plain = bytes(prints.files[PAD_ROW])
    prints.files.extend(plain for _ in range(MEGA_NOVAREON + 1 - len(prints.files)))
    prints.files[NOVAREON] = prints.files[MEGA_NOVAREON] = bytes(prints.files[197])
    rom.setFileByName('a/0/6/9', prints.save())
    return dict(wrapper=hex(wrapper), number=hex(number), table=hex(table_at), list_entries=len(cur) + 1)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
