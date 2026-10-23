"""Starter Eevee's evolutions, each with its own starter-line species and its own Mega.

Builds on mega_starter (starter Eevee 1561 / Mega Eevee 1562, starter Psyduck 1563 / Mega 1564). Nine pairs are appended
after them: for each Eeveelution i, STARTER_i = 1565 + 2i and MEGA_i = 1566 + 2i. Every record is a copy of the ordinary
evolution (stats, ability, typing, moves, art); each Mega uses the shared Mega Eevee front/back art (species 1562) with
the evolution's own typing. Starter Eevee's evolution record is repointed at the STARTER_i species, so the starter line
never turns into an ordinary Pokemon and ordinary Eevee is untouched. Eonite works on every STARTER_i (one more Mega-table
entry each). The ninth slot is Novareon: a stand-in copy of Umbreon (placeholder until its real data exists), evolved with
the Dusk Stone and Mega-evolving with Novareonite, a new item copied from Eonite's record like Psyduckite.

Code goes in a second reserved gap in overlay 129. Each of the three Eevee/Psyduck hooks is chained once more: the stub's
literal is repointed at a routine that aliases the new IDs back to their ordinary species (follower sprite, overworld
tag) or reports base/Mega form, then jumps to the previous routine.
"""
import copy
import json
import struct
import sys
from pathlib import Path
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from mega_starter import (COUNT as OLD_COUNT, EEVEE_STARTER, EEVEE_STONE, HOOKS, MEGA_COUNT_SITES,
                          MEGA_TABLE_SITES, STARTER as PSYDUCK_STARTER, STONE as PSYDUCKITE, Gap)
from prototype import decode_messages, encode_messages

EEVEE = 133
FIRST = OLD_COUNT                                   # 1565
# Ordinary species of each Eeveelution, in the Eevee record's own targets; the ninth is the Umbreon stand-in for Novareon.
BASES = (134, 135, 136, 196, 197, 470, 471, 750, 197)
NOVAREON = 8
NEW = 2 * len(BASES)
COUNT = OLD_COUNT + NEW
NOVAREONITE = PSYDUCKITE + 1                        # 3147
DUSK_STONE = 108
RESERVE = 720                                       # bytes of overlay-129 space (30 table records' worth)
OLD_ENTRIES = 97                                    # 95 stock + starter Eevee + starter Psyduck
TEXT_MAP = json.loads((Path(__file__).resolve().parent / 'text-map.json').read_text())


def starter(i):
    return FIRST + 2 * i


def mega(i):
    return FIRST + 2 * i + 1


def _words(s):
    return [TEXT_MAP[c] for c in s] + [65535]


def _extend_narcs(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]

    def base_of(j):
        return BASES[j // 2]

    def append_records(name, stride=1, prefix=0, blank=False, art=None):
        a = narc(name)
        assert len(a.files) == prefix + OLD_COUNT * stride, (name, len(a.files))
        for j in range(NEW):
            src = base_of(j)
            if art is not None and j % 2:
                src = art
            sample = a.files[prefix + src * stride:prefix + (src + 1) * stride]
            a.files.extend(bytes(len(f)) if blank else f for f in sample)

    for name, stride, prefix, blank, art in (('a/0/0/2', 1, 0, False, None), ('a/0/0/4', 6, 0, False, EEVEE_STARTER + 1),
                                             ('a/0/0/5', 4, 0, False, None), ('a/0/3/4', 1, 0, True, None),
                                             ('a/0/2/0', 1, 7, False, None)):
        append_records(name, stride, prefix, blank, art)
    # Starter Eevee evolves into the starter line; the ninth (previously empty) slot is Novareon.
    ev = narc('a/0/3/4')
    rec = bytearray(ev.files[EEVEE_STARTER])
    assert bytes(rec[48:54]) == bytes(6), 'Eevee evolution record has no free ninth slot'
    targets = {BASES[i]: starter(i) for i in range(NOVAREON)}
    for at in range(0, 48, 6):
        method, param, target = struct.unpack_from('<HHH', rec, at)
        assert method and target in targets, (at, method, param, target)
        struct.pack_into('<H', rec, at + 4, targets[target])
    struct.pack_into('<HHH', rec, 48, 7, DUSK_STONE, starter(NOVAREON))
    ev.files[EEVEE_STARTER] = bytes(rec)
    a = narc('a/0/2/8')
    for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (14, 44), (15, 8)):
        b = bytearray(a.files[i])
        assert len(b) == OLD_COUNT * width, (i, len(b))
        for j in range(NEW):
            src = base_of(j)
            b.extend(b[src * width:(src + 1) * width])
        a.files[i] = bytes(b)
    b = bytearray(a.files[11])                                        # species -> form row; 0x8000 marks a reverting form
    assert len(b) == OLD_COUNT * 64
    b.extend(bytes(NEW * 64))
    for i in range(len(BASES)):
        struct.pack_into('<H', b, starter(i) * 64, mega(i) | 0x8000)
    a.files[11] = bytes(b)
    for i in (12, 13):                                                # external adjusted-form IDs alias back to the ordinary species
        b = bytearray(a.files[i])
        assert len(b) == (OLD_COUNT - 1076) * 2
        b.extend(bytes(NEW * 2))
        a.files[i] = bytes(b)
    b = bytearray(a.files[12])
    for j in range(NEW):
        struct.pack_into('<H', b, (FIRST + j - 1076) * 2, base_of(j))
    a.files[12] = bytes(b)
    levels = narc('a/0/3/3')
    b = bytearray(levels.files[0])
    stride = 34 * 4
    assert len(b) == OLD_COUNT * stride
    for j in range(NEW):
        src = base_of(j)
        b.extend(b[src * stride:(src + 1) * stride])
    levels.files[0] = bytes(b)
    items = narc('a/0/1/7')
    assert len(items.files) == NOVAREONITE
    items.files.append(items.files[EEVEE_STONE])                     # same Mega Stone record as Eonite
    gfx = narc('a/0/1/8')
    assert len(gfx.files) == PSYDUCKITE * 2 + 4
    gfx.files.extend([gfx.files[660 * 2 + 2], gfx.files[660 * 2 + 3]])  # Charizardite X art as a placeholder icon
    text = narc('a/0/2/7')

    def add_text(bank, index, row):
        key, rows = decode_messages(text.files[bank])
        old = copy.deepcopy(rows)
        assert index >= len(old) or rows[index] == [65535] or bank == 238, ('would replace text', bank, index)
        while len(rows) <= index:
            rows.append([65535])
        rows[index] = row
        text.files[bank] = encode_messages(key, rows)

    for bank in (237, 238):                                           # species names and their article forms
        key, rows = decode_messages(text.files[bank])
        for j in range(NEW):
            add_text(bank, FIRST + j, rows[base_of(j)])
    add_text(222, NOVAREONITE, _words('Novareonite'))
    offset = NOVAREONITE - 2685
    for bank, value in ((221, 'A Mega Stone for the starter Novareon.'), (223, 'a Novareonite'), (224, 'Novareonites'), (829, 'Novareonite')):
        add_text(bank, offset, _words(value))
    for name, a in ns.items():
        rom.setFileByName(name, a.save())


def _tail(old):
    return f'''push {{r4}}
ldr r4, back
mov ip,r4
pop {{r4}}
bx ip
.align 2
first: .word {FIRST}
table: .word 0
back: .word {old}
'''


def _chain_alias(gap, old, table):
    return gap.code(f'''ldr r3, first
subs r3,r0,r3
cmp r3,#{NEW - 1}
bhi next
push {{r4}}
ldr r4, table
lsls r3,r3,#1
ldrh r0,[r4,r3]
pop {{r4}}
movs r1,#0
next:
''' + _tail(old).replace('table: .word 0', f'table: .word {table}'))


def _chain_forms(gap, old):
    return gap.code(f'''ldr r3, first
subs r3,r0,r3
cmp r3,#{NEW - 1}
bhi next
movs r0,#1
ands r0,r3
bx lr
next:
''' + _tail(old))


def patch(rom):
    for name, n in (('a/0/0/2', OLD_COUNT), ('a/0/3/4', OLD_COUNT)):
        assert len(ndspy.narc.NARC(rom.getFileByName(name)).files) == n, 'ROM is not the Psyduck-pair build (1565 species)'
    _extend_narcs(rom)
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm, battle = ovs[129], ovs[130]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    old_table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    for site in MEGA_TABLE_SITES:
        assert struct.unpack_from('<I', battle.data, site - battle.ramAddress)[0] == old_table
    holder = battle if battle.ramAddress <= old_table < battle.ramAddress + len(battle.data) else perm
    raw = bytes(holder.data[old_table - holder.ramAddress:old_table - holder.ramAddress + OLD_ENTRIES * 4])
    last = struct.unpack_from('<I', raw, 96 * 4)[0]
    assert last == PSYDUCK_STARTER | (PSYDUCKITE << 12) | (1 << 24), 'Mega table is not stock + Eonite + Psyduckite'
    new = b''.join(struct.pack('<I', starter(i) | ((NOVAREONITE if i == NOVAREON else EEVEE_STONE) << 12) | (1 << 24))
                   for i in range(len(BASES)))
    table = gap.put(raw + new)
    battle.data = bytearray(battle.data)
    for site in MEGA_TABLE_SITES:
        struct.pack_into('<I', battle.data, site - battle.ramAddress, table)
    for site, expected in MEGA_COUNT_SITES:
        expected += 1                                  # mega_starter already raised the stock count by one
        assert struct.unpack_from('<H', battle.data, site - battle.ramAddress)[0] == expected, hex(site)
        struct.pack_into('<H', battle.data, site - battle.ramAddress, expected + len(BASES))
    report = dict(mega_table=hex(table), entries=OLD_ENTRIES + len(BASES))
    bases = gap.put(b''.join(struct.pack('<H', BASES[j // 2]) for j in range(NEW)))
    ovmap = {129: perm, 131: ovs[131]}
    ovmap[131].data = bytearray(ovmap[131].data)
    for name, (ovid, site, lit) in HOOKS.items():
        ov = ovmap[ovid]
        at = site - ov.ramAddress + lit
        old = struct.unpack_from('<I', ov.data, at)[0]
        assert old & 1 and ov.ramAddress <= old - 1 < 0x23E0000, (name, hex(old))
        routine = _chain_forms(gap, old) if name == 'forms' else _chain_alias(gap, old, bases)
        struct.pack_into('<I', ov.data, at, routine | 1)
        report[name] = (hex(old), hex(routine))
    for ov in (perm, battle, ovmap[131]):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    report['gap_used'] = gap.at - gap.start
    return report


if __name__ == '__main__':
    import mega_shop
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    print(mega_shop.patch(rom, Path(__file__).resolve().parent.parent))
    rom.saveToFile(dst)
