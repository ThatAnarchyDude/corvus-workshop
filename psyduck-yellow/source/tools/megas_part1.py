"""Stage D2: Mega forms for six of the nine new starter Eeveelutions, built in the free filler rows 1554-1559 (owner order 2026-11-01).

Mega i (species row MEGA_ROWS[i]) belongs to the starter species of MEGA_FOR[i] (ids 1545..1553): its record is a copy of that starter species (stats, types, abilities, level-up list, TM row,
names), its battle art is the shared Mega Eevee art (species 1562, like the other starter Megas), it evolves into nothing, and it reverts to the starter species after battle
(form row of the starter species: Mega row | 0x8000). Eonite (the Eevee Mega Stone) triggers it: six more entries of the Mega table.
Not yet (needs the table-growth step): Strateon, Wyrmeon and Ferreon Megas and the ordinary Novareon (rows 1560 is the Novareon follower slot, and 1535-1553 are taken).
Stats are the base species' for now; the +120 rule is a separate later script.
Code: the Mega table moves to the dead dex_fix region of overlay 129 (116... entries), and the follower-sprite / overworld-tag / form hooks get one more chained link for ids 1554-1559.
The Pokedex alias copies send each Mega to its species' Pokedex id (501-509) so nothing registers under a Mega id.
Usage (from yellow-heartgold, PYTHONPATH=tools): megas_part1.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import re
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from mega_starter import EEVEE_STONE, HOOKS, MEGA_COUNT_SITES, MEGA_TABLE_SITES, Gap
from new_eeveelutions import NAMES, TEMPLATE, ordinary, starter
from dex_new_eeveelutions import dex_id

MEGA_FOR = ('Brawleon', 'Zephyreon', 'Wraitheon', 'Venomeon', 'Duneon', 'Chryseon')
FIRST = 1554
MEGA_ROWS = tuple(FIRST + k for k in range(len(MEGA_FOR)))
FILLER = 1560
SHARED_MEGA_ART = 1562
FIRST_FORM = 1076
FREE_AT = 0x023DEC50                      # dead dex_fix region of overlay 129 (after dex_new_eeveelutions's routines and dex_stellar_icon's table)
FREE_END = 0x023DF060
ENTRIES_OLD = 107


def _tables(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    for k, name in enumerate(MEGA_FOR):
        m, s = MEGA_ROWS[k], starter(NAMES.index(name))
        for path, stride, prefix, art in (('a/0/0/2', 1, 0, None), ('a/0/0/4', 6, 0, SHARED_MEGA_ART), ('a/0/0/5', 4, 0, None), ('a/0/2/0', 1, 7, None),
                                          ('a/0/6/9', 1, 0, None), ('a/2/5/6', 1, 0, None), ('a/2/4/8', 1, 0, None), ('a/2/2/1', 1, 0, None)):
            a = narc(path)
            src = art or s
            assert [bytes(x) for x in a.files[prefix + m * stride:prefix + (m + 1) * stride]] == [bytes(x) for x in a.files[prefix + FILLER * stride:prefix + (FILLER + 1) * stride]], (path, m, 'not filler')
            a.files[prefix + m * stride:prefix + (m + 1) * stride] = [bytes(x) for x in a.files[prefix + src * stride:prefix + (src + 1) * stride]]
        a = narc('a/1/4/1')
        a.files[m] = bytes(a.files[s])
        ev = narc('a/0/3/4')
        assert bytes(ev.files[m]) == bytes(ev.files[FILLER])
        ev.files[m] = bytes(len(ev.files[m]))
        t = narc('a/0/2/8')
        for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (14, 44), (15, 8)):
            b = bytearray(t.files[i])
            assert b[m * width:(m + 1) * width] == b[FILLER * width:(FILLER + 1) * width], (i, m)
            b[m * width:(m + 1) * width] = b[s * width:(s + 1) * width]
            t.files[i] = bytes(b)
        b = bytearray(t.files[11])                                   # forms: the starter species reverts from this Mega; the Mega row itself has no forms
        assert b[m * 64:(m + 1) * 64] == b[FILLER * 64:(FILLER + 1) * 64]
        b[m * 64:(m + 1) * 64] = bytes(64)
        assert struct.unpack_from('<H', b, s * 64)[0] == 0
        struct.pack_into('<H', b, s * 64, m | 0x8000)
        t.files[11] = bytes(b)
        b = bytearray(t.files[12])
        struct.pack_into('<H', b, (m - FIRST_FORM) * 2, TEMPLATE[name])
        t.files[12] = bytes(b)
        ls = narc('a/0/3/3')
        b = bytearray(ls.files[0])
        assert b[m * 136:(m + 1) * 136] == b[FILLER * 136:(FILLER + 1) * 136]
        b[m * 136:(m + 1) * 136] = b[s * 136:(s + 1) * 136]
        ls.files[0] = bytes(b)
        d = narc('a/1/8/0')
        tb = bytearray(d.files[0])
        tb[m * 89:(m + 1) * 89] = tb[s * 89:(s + 1) * 89]
        d.files[0] = bytes(tb)
    from prototype import decode_messages, encode_messages
    text = narc('a/0/2/7')
    for bank in (237, 238):
        key, rows = decode_messages(text.files[bank])
        for k, name in enumerate(MEGA_FOR):
            assert rows[MEGA_ROWS[k]] == [65535], (bank, MEGA_ROWS[k])
            rows[MEGA_ROWS[k]] = rows[starter(NAMES.index(name))]
        text.files[bank] = encode_messages(key, rows)
    for name, a in ns.items():
        rom.setFileByName(name, a.save())


def _hook(old, kind, table):
    head = f'''ldr r3, first
subs r3, r0, r3
cmp r3, #{len(MEGA_FOR) - 1}
bhi next
'''
    if kind == 'forms':
        return head + f'''movs r0,#1
bx lr
next:
ldr r3, back
bx r3
.align 2
first: .word {FIRST}
back: .word {old}
'''
    return head + f'''lsls r3,r3,#1
push {{r4}}
ldr r4, table
ldrh r0,[r4,r3]
pop {{r4}}
movs r1,#0
next:
ldr r3, back
bx r3
.align 2
first: .word {FIRST}
table: .word {table}
back: .word {old}
'''


def _put(gap, source, literal_bytes):
    gap.at = (gap.at + 3) & ~3
    raw = bytes(gap.ks.asm(source, addr=gap.at)[0])
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(raw[:len(raw) - literal_bytes], gap.at):
        assert not (i.mnemonic.startswith('b') and i.mnemonic.endswith('.w')), i
    return gap.put(raw)


def _code(rom):
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    original = bytes(addons.files[12])
    ovs = rom.loadArm9Overlays()
    perm, battle, ov131 = ovs[129], ovs[130], ovs[131]
    perm.data, battle.data, ov131.data = bytearray(perm.data), bytearray(battle.data), bytearray(ov131.data)
    base = perm.ramAddress
    assert not any(perm.data[FREE_AT - base:FREE_END - base]), 'the free region is not free'
    gap = Gap(perm, FREE_AT, FREE_END - FREE_AT)
    old_table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    for site in MEGA_TABLE_SITES:
        assert struct.unpack_from('<I', battle.data, site - battle.ramAddress)[0] == old_table
    holder = battle if battle.ramAddress <= old_table < battle.ramAddress + len(battle.data) else perm
    raw = bytes(holder.data[old_table - holder.ramAddress:old_table - holder.ramAddress + ENTRIES_OLD * 4])
    assert struct.unpack_from('<I', raw, (ENTRIES_OLD - 1) * 4)[0] == 1535 | (3146 << 12) | (1 << 24), 'the Mega table is not the starter Golduck build'
    new = b''.join(struct.pack('<I', starter(NAMES.index(n)) | (EEVEE_STONE << 12) | (1 << 24)) for n in MEGA_FOR)
    table = gap.put(raw + new)
    for site in MEGA_TABLE_SITES:
        struct.pack_into('<I', battle.data, site - battle.ramAddress, table)
    counts = []
    for site, _ in MEGA_COUNT_SITES:
        at = site - battle.ramAddress
        value = struct.unpack_from('<H', battle.data, at)[0]
        assert value & 0xFF == ENTRIES_OLD, (hex(site), hex(value))
        struct.pack_into('<H', battle.data, at, value + len(MEGA_FOR))
        counts.append(hex(value + len(MEGA_FOR)))
    alias = gap.put(b''.join(struct.pack('<H', TEMPLATE[n]) for n in MEGA_FOR))
    ovmap = {129: perm, 131: ov131}
    report = dict(mega_table=hex(table), counts=counts)
    for name, (ovid, site, lit) in HOOKS.items():
        ov = ovmap[ovid]
        at = site - ov.ramAddress + lit
        old = struct.unpack_from('<I', ov.data, at)[0]
        assert old & 1 and ov.ramAddress <= old - 1 < 0x23E0000, (name, hex(old))
        routine = _put(gap, _hook(old, 'forms' if name == 'forms' else 'alias', alias), 8 if name == 'forms' else 12)
        struct.pack_into('<I', ov.data, at, routine | 1)
        report[name] = (hex(old), hex(routine))
    # Pokedex: a Mega id registers as its species' Pokedex id (both alias copies)
    for m in re.finditer(re.escape(original[:64]), bytes(perm.data)):
        for k, name in enumerate(MEGA_FOR):
            struct.pack_into('<H', perm.data, m.start() + 2 * (MEGA_ROWS[k] - FIRST_FORM), dex_id(NAMES.index(name)))
    for ov in (perm, battle, ov131):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    report['free_left'] = gap.end - gap.at
    return report


def patch(rom):
    _tables(rom)
    return _code(rom)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
