"""Pokedex entries for the nine new Eeveelutions and the one-entry-per-species fix (owner order 2026-11-01).

Every species has ONE Pokedex entry: an ordinary species and its starter version register as the same entry (like starter Eevee -> Eevee).
Method = Novareon's (dex_novareon_id500.py): a Pokedex identity at an unused id of the Gen 4 / Gen 5 gap, here ids 501-509 for Brawleon..Ferreon (Novareon keeps 500),
National Nos. 1027-1035 after Novareon's 1026.
 - the Pokedex's species alias copy (overlay 129) sends ordinary 1536-1544 and starter 1545-1553 species to ids 501-509; starter Golduck (1535) to Golduck (55) (it mapped to 0, so it
   never registered);
 - ids 501-509 get the data the Pokedex reads by species id (personal record, art and palettes, icon, offsets, follower flags, names, the Pokedex text rows, height/weight arrays,
   the Pokedex-app NARCs). Art-type data is the placeholder template species' (new_eeveelutions.TEMPLATE); stats, abilities and names are the new species' own;
 - the National sort list gets 501..509 appended (entries 1027..1035);
 - three small routines are rewritten for the id range 500..509 instead of the single id 500: the Pokedex number routine (ids 500..509 -> No. id+526), the gap test (ids in
   494..543 are "not in the gap" except 500..509 now) and the Seen/Obtained counting test. They live in overlay 129's dead 1368-byte region of dex_fix.py (nothing points into it any more).
Text for the new pages is a placeholder for the owner to replace (category, name, one-line entry).
Usage (from yellow-heartgold, PYTHONPATH=tools): dex_new_eeveelutions.py <in.nds> <out.nds>"""
import re
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from mega_starter import Gap
from prototype import decode_messages, encode_messages
from dex_novareon import bl, read_bl, encode_row
from new_eeveelutions import NAMES, TEMPLATE, FIRST, ordinary, starter

DEX_FIRST, NATIONAL_FIRST = 501, 1027
NOVAREON_DEX, NOVAREON_NUMBER = 500, 1026
STARTER_GOLDUCK, GOLDUCK = 1535, 55
FIRST_FORM = 1076
DEAD_START, DEAD_END = 0x023DEB08, 0x023DF060
NUMBER_HOOK, HOLE_CHECK = 0x020FF114, 0x0202940C
REGIONAL_NUM = 0x0207185C
COUNT_SITES = (0x02029E2C, 0x02029E68)
ENTRY = 89
CATEGORY = {'Brawleon': 'Brawl', 'Venomeon': 'Toxin', 'Duneon': 'Dune', 'Zephyreon': 'Gale', 'Chryseon': 'Husk', 'Strateon': 'Bedrock', 'Wraitheon': 'Wraith', 'Wyrmeon': 'Wyrm',
            'Ferreon': 'Alloy'}
HEIGHT_WEIGHT_BANKS = (812, 813, 814, 815)


def dex_id(i):
    return DEX_FIRST + i


def number_code(alias_at, alias_count):
    return f'''push {{lr}}
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
subs r0, r1, r0
cmp r0, #10
bhs ordinary
ldr r1, novanumber
adds r0, r0, r1
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
count: .word {alias_count}
tbl: .word {alias_at}
regional: .word {REGIONAL_NUM | 1}
c493: .word 493
novadex: .word {NOVAREON_DEX}
novanumber: .word {NOVAREON_NUMBER}
'''


GAP_CODE = f'''movs r1, #0xf7
lsls r1, r1, #1
cmp r0, r1
blo ret0
adds r1, #0x32
cmp r0, r1
bhs ret0
movs r1, #0xfa
lsls r1, r1, #1
subs r1, r0, r1
cmp r1, #10
blo ret0
movs r0, #1
bx lr
ret0:
movs r0, #0
bx lr
'''

COUNT_CODE = '''movs r7, #0xfa
lsls r7, r7, #1
subs r7, r4, r7
cmp r7, #10
bhs notnew
cmp r4, r4
bx lr
notnew:
movs r7, #0x88
lsls r7, r7, #2
cmp r4, r7
bx lr
'''


def _put_code(gap, source, literal_bytes=0):
    gap.at = (gap.at + 3) & ~3
    raw = bytes(gap.ks.asm(source, addr=gap.at)[0])
    for ins in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(raw[:len(raw) - literal_bytes], gap.at):
        assert not (ins.mnemonic.startswith('b') and ins.mnemonic.endswith('.w')), ins
    return gap.put(raw)


def _data(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    for i, name in enumerate(NAMES):
        d, own, art = dex_id(i), ordinary(i), TEMPLATE[name]
        pe = narc('a/0/0/2')
        pe.files[d] = bytes(pe.files[own])                                   # the species' own stats/abilities/types
        for path, per in (('a/0/0/4', 6), ('a/0/0/5', 4), ('a/1/4/1', 1), ('a/0/6/9', 1), ('a/2/5/6', 1), ('a/2/4/8', 1), ('a/2/2/1', 1)):
            a = narc(path)
            for k in range(per):
                a.files[d * per + k] = bytes(a.files[own * per + k]) if path in ('a/0/0/4', 'a/0/0/5', 'a/1/4/1') else bytes(a.files[art * per + k])
        a = narc('a/0/2/0')
        a.files[7 + d] = bytes(a.files[7 + own])
        a = narc('a/0/2/8')
        banks = bytearray(a.files[9])
        banks[d] = banks[own]
        a.files[9] = bytes(banks)
        t = bytearray(narc('a/1/8/0').files[0])
        t[d * ENTRY:(d + 1) * ENTRY] = t[own * ENTRY:(own + 1) * ENTRY]
        narc('a/1/8/0').files[0] = bytes(t)
        lists = narc('a/2/1/4')
        for index, width in ((0, 4), (1, 4), (2, 1)):
            raw = bytearray(lists.files[index])
            raw[d * width:(d + 1) * width] = raw[art * width:(art + 1) * width]
            lists.files[index] = bytes(raw)
    texts = narc('a/0/2/7')
    for bank in (237, 238, 803, 812, 813, 814, 815, 816, 817, 823):
        key, rows = decode_messages(texts.files[bank])
        for i, name in enumerate(NAMES):
            d, own, art = dex_id(i), ordinary(i), TEMPLATE[name]
            if bank in (237, 238):
                rows[d] = rows[own]
            elif bank in HEIGHT_WEIGHT_BANKS:
                rows[d] = rows[art]
            elif bank == 803:
                rows[d] = encode_row(f'{name} is an evolution of Eevee.\nIts Pokédex entry is a placeholder.', None)
            elif bank == 817:
                rows[d] = encode_row(name.upper(), None)
            else:
                rows[d] = encode_row(f'{CATEGORY[name]} Pokémon', None)
        texts.files[bank] = encode_messages(key, rows)
    lists = narc('a/2/1/4')
    cur = list(struct.unpack('<%dH' % (len(lists.files[11]) // 2), bytes(lists.files[11])))
    assert len(cur) == 1026 and cur[-1] == NOVAREON_DEX, (len(cur), cur[-1])
    cur += [dex_id(i) for i in range(len(NAMES))]
    lists.files[11] = struct.pack('<%dH' % len(cur), *cur)
    for name, a in ns.items():
        rom.setFileByName(name, a.save())
    return len(cur)


def _code(rom):
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    original = bytes(addons.files[12])
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    data = perm.data
    base = perm.ramAddress
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    sbase = section.ramAddress
    # the dead region must be unreferenced
    lo, hi = DEAD_START, DEAD_END
    for k in range(0, len(section.data) - 3, 4):
        assert not lo <= (struct.unpack_from('<I', section.data, k)[0] & ~1) < hi, 'ARM9 points into the dead region'
    for k in range(0, len(data) - 3, 4):
        if lo <= base + k < hi:
            continue
        assert not lo <= (struct.unpack_from('<I', data, k)[0] & ~1) < hi, ('overlay 129 points into the dead region', hex(base + k))
    live = [m.start() for m in re.finditer(re.escape(original[:64]), bytes(data))]
    live = [c for c in live if struct.unpack_from('<H', data, c + 2 * (1581 - FIRST_FORM))[0] == NOVAREON_DEX]
    assert len(live) == 1, 'cannot tell the live alias copy'
    alias_at = live[0]
    for c in (alias_at, *[m.start() for m in re.finditer(re.escape(original[:64]), bytes(data)) if m.start() != alias_at]):
        assert struct.unpack_from('<H', data, c + 2 * (STARTER_GOLDUCK - FIRST_FORM))[0] == 0
        struct.pack_into('<H', data, c + 2 * (STARTER_GOLDUCK - FIRST_FORM), GOLDUCK)
        for i in range(len(NAMES)):
            struct.pack_into('<H', data, c + 2 * (ordinary(i) - FIRST_FORM), dex_id(i))
            struct.pack_into('<H', data, c + 2 * (starter(i) - FIRST_FORM), dex_id(i))
    data[DEAD_START - base:DEAD_END - base] = bytes(DEAD_END - DEAD_START)
    gap = Gap(perm, DEAD_START, DEAD_END - DEAD_START)
    number = _put_code(gap, number_code(base + alias_at, len(original) // 2), 28)
    hole = _put_code(gap, GAP_CODE)
    count = _put_code(gap, COUNT_CODE)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    d = section.data
    at = NUMBER_HOOK - sbase
    assert bytes(d[at:at + 4]) == bytes.fromhex('004a1047'), 'number hook missing'
    struct.pack_into('<I', d, at + 4, number | 1)
    at = HOLE_CHECK - sbase
    assert bytes(d[at:at + 4]) == bytes.fromhex('004b1847'), 'gap-test stub missing'
    struct.pack_into('<I', d, at + 4, hole | 1)
    for site in COUNT_SITES:
        read_bl(d, sbase, site)
        d[site - sbase:site - sbase + 4] = bl(site, count)
    rom.arm9 = main.save(compress=True)
    return dict(number=hex(number), gap_test=hex(hole), count=hex(count), dead_left=gap.end - gap.at)


def patch(rom):
    entries = _data(rom)
    report = _code(rom)
    report['national_entries'] = entries
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
