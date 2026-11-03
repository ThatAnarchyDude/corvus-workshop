"""Stage C of the starter redesign: the nine new Eeveelutions, as ordinary and starter species (owner order 2026-11-01).

Species ids are filler rows (rows 1535-1560 exist in every per-species table as unused copies of Eevee; 1535 is starter Golduck):
  ordinary Brawleon..Ferreon = 1536..1544, starter versions = 1545..1553 (same order). Rows 1554-1560 stay free.
Data per species: personal record (copy of Umbreon's, then the approved stats/type/abilities), art and display rows (placeholder: a copy of a
thematic existing species, TEMPLATE below), level-up list and TM/HM row (data/eeveelution-levelup-plan.json, data/eevee-tm-plan.json), name text.
Evolution: Eevee and starter Eevee get a Dusk Stone row for Wraitheon; Brawleon and the others use "level up while holding" items (a new, larger
hold table replaces stage B's; the placeholder row is dropped from the Eevee records). The Stage B rows are rebuilt here so the Eevee records stay in step.
Code: the three alias/form hooks (follower sprite, overworld tag, form) get one more chained link for the whole id range 1536..1553.
Usage (from yellow-heartgold, PYTHONPATH=tools): new_eeveelutions.py <in.nds> <out.nds>"""
import json
import struct
import sys
from pathlib import Path
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from mega_starter import HOOKS, Gap
from prototype import decode_messages, encode_messages
import stage_b_evolutions as sb

HERE = Path(__file__).resolve().parent
TEXT_MAP = json.loads((HERE / 'text-map.json').read_text())
FILLER = 1560
FIRST = 1536
EEVEE, STARTER_EEVEE = 133, 1561
UMBREON = 197
# name, types, stats HP/Atk/Def/SpA/SpD/Spe, abilities (slot 0, slot 1, hidden), evolution item, placeholder art species
NAMES = ('Brawleon', 'Venomeon', 'Duneon', 'Zephyreon', 'Chryseon', 'Strateon', 'Wraitheon', 'Wyrmeon', 'Ferreon')
TYPES = {'Brawleon': 1, 'Venomeon': 3, 'Duneon': 4, 'Zephyreon': 2, 'Chryseon': 6, 'Strateon': 5, 'Wraitheon': 7, 'Wyrmeon': 16, 'Ferreon': 8}
STATS = {'Brawleon': (90, 130, 75, 45, 100, 85), 'Venomeon': (85, 65, 70, 120, 105, 80), 'Duneon': (110, 120, 115, 45, 75, 60),
         'Zephyreon': (65, 110, 70, 60, 90, 130), 'Chryseon': (85, 85, 100, 85, 100, 70), 'Strateon': (90, 90, 140, 50, 105, 50),
         'Wraitheon': (75, 55, 75, 125, 100, 95), 'Wyrmeon': (85, 110, 80, 110, 70, 70), 'Ferreon': (80, 100, 135, 55, 95, 60)}
ABILITIES = {'Brawleon': ('Iron Fist', 'Inner Focus', 'Guts'), 'Venomeon': ('Poison Point', 'Synchronize', None), 'Duneon': ('Sand Force', 'Sand Veil', None),
             'Zephyreon': ('Super Luck', 'Keen Eye', None), 'Chryseon': ('Shed Skin', 'Swarm', None), 'Strateon': ('Sturdy', 'Solid Rock', None),
             'Wraitheon': ('Cursed Body', 'Pressure', None), 'Wyrmeon': ('Rough Skin', 'Moxie', None), 'Ferreon': ('Clear Body', 'Heavy Metal', None)}
HOLD_ITEMS = {'Brawleon': 241, 'Venomeon': 272, 'Duneon': 237, 'Zephyreon': 539, 'Chryseon': 222, 'Strateon': 238, 'Wyrmeon': 235, 'Ferreon': 233}
DUSK_STONE = 108
TEMPLATE = {'Brawleon': 107, 'Venomeon': 169, 'Duneon': 28, 'Zephyreon': 18, 'Chryseon': 123, 'Strateon': 76, 'Wraitheon': 94, 'Wyrmeon': 148, 'Ferreon': 227}
RESERVE = 6 * 24                      # overlay 129 has only ~160 free bytes left; the hold table reuses Stage B's gap


def ordinary(i):
    return FIRST + i


def starter(i):
    return FIRST + len(NAMES) + i


ALL = [(ordinary(i), n, i) for i, n in enumerate(NAMES)] + [(starter(i), n, i) for i, n in enumerate(NAMES)]
COUNT = len(ALL)


def words(s):
    return [TEXT_MAP[c] for c in s] + [65535]


def _tables(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    text = narc('a/0/2/7')
    inv = {v: k for k, v in TEXT_MAP.items()}
    moves = [''.join(inv.get(w, '?') for w in row if w != 65535) for row in decode_messages(text.files[750])[1]]
    midx = {n: i for i, n in enumerate(moves) if n}
    abil = [''.join(inv.get(w, '?') for w in row if w != 65535) for row in decode_messages(text.files[720])[1]]
    aidx = {n: i for i, n in enumerate(abil) if n}
    levelplan = json.load(open(HERE.parent / 'data/eeveelution-levelup-plan.json'))
    tmplan = json.load(open(HERE.parent / 'data/eevee-tm-plan.json'))
    d = bytes(rom.loadArm9().sections[0].data)
    tab = struct.unpack_from('<108H', d, d.find(struct.pack('<6H', 264, 337, 352, 347, 46, 92)))
    bit = {}
    for k in range(100):
        bit.setdefault(moves[tab[k]], k)

    def same_filler(a, name, stride, prefix):
        want = [bytes(x) for x in a.files[prefix + FILLER * stride:prefix + (FILLER + 1) * stride]]
        for sp, _, _ in ALL:
            assert [bytes(x) for x in a.files[prefix + sp * stride:prefix + (sp + 1) * stride]] == want, (name, sp, 'not filler')

    # personal record: Umbreon's, then stats/types/abilities
    pe = narc('a/0/0/2')
    same_filler(pe, 'a/0/0/2', 1, 0)
    for sp, name, i in ALL:
        row = bytearray(pe.files[UMBREON])
        hp, atk, df, spa, spd, spe = STATS[name]
        row[0:6] = bytes((hp, atk, df, spe, spa, spd))
        row[6] = row[7] = TYPES[name]
        a0, a1, hidden = ABILITIES[name]
        row[22], row[23] = aidx[a0], aidx[a1]
        row[26] = aidx[hidden] if hidden else 0
        pe.files[sp] = bytes(row)
    # display / art rows: placeholder from the template species
    for name, stride, prefix in (('a/0/0/4', 6, 0), ('a/0/0/5', 4, 0), ('a/0/2/0', 1, 7), ('a/1/4/1', 1, 0)):
        a = narc(name)
        if name != 'a/1/4/1':                                          # rows 1539 and 1541 hold stray bytes there (unused ids, overwritten below)
            same_filler(a, name, stride, prefix)
        for sp, nm, i in ALL:
            t = TEMPLATE[nm]
            a.files[prefix + sp * stride:prefix + (sp + 1) * stride] = a.files[prefix + t * stride:prefix + (t + 1) * stride]
    ev = narc('a/0/3/4')
    for sp, _, _ in ALL:
        assert bytes(ev.files[sp]) == bytes(ev.files[FILLER])
        ev.files[sp] = bytes(len(ev.files[sp]))
    a = narc('a/0/2/8')
    for k, width in ((7, 2), (8, 2), (9, 1), (10, 2), (15, 8)):
        b = bytearray(a.files[k])
        for sp, nm, i in ALL:
            assert b[FILLER * width:(FILLER + 1) * width] == b[sp * width:(sp + 1) * width], (k, sp)
            t = TEMPLATE[nm]
            b[sp * width:(sp + 1) * width] = b[t * width:(t + 1) * width]
        a.files[k] = bytes(b)
    tm = bytearray(a.files[14])
    for sp, nm, i in ALL:
        assert tm[sp * 44:(sp + 1) * 44] == tm[FILLER * 44:(FILLER + 1) * 44]
        keep = int.from_bytes(tm[sp * 44:sp * 44 + 16], 'little') & ~((1 << 100) - 1)
        tm[sp * 44:sp * 44 + 16] = (sum(1 << bit[m] for m in tmplan[nm]) | keep).to_bytes(16, 'little')
    a.files[14] = bytes(tm)
    b = bytearray(a.files[11])
    for sp, _, _ in ALL:
        assert b[sp * 64:(sp + 1) * 64] == b[FILLER * 64:(FILLER + 1) * 64]
        b[sp * 64:(sp + 1) * 64] = bytes(64)
    a.files[11] = bytes(b)
    b = bytearray(a.files[12])
    for sp, nm, _ in ALL:
        assert b[(sp - 1076) * 2:(sp - 1075) * 2] == b[(FILLER - 1076) * 2:(FILLER - 1075) * 2]
        struct.pack_into('<H', b, (sp - 1076) * 2, TEMPLATE[nm])
    a.files[12] = bytes(b)
    ls = narc('a/0/3/3')
    b = bytearray(ls.files[0])
    for sp, nm, _ in ALL:
        assert b[sp * 136:(sp + 1) * 136] == b[FILLER * 136:(FILLER + 1) * 136]
        entries = sorted(levelplan[nm], key=lambda e: e[0])
        assert len(entries) <= 34
        row = b''.join(struct.pack('<HH', midx[m], lv) for lv, m in entries) + struct.pack('<HH', 0xFFFF, 0) * (34 - len(entries))
        b[sp * 136:(sp + 1) * 136] = row
    ls.files[0] = bytes(b)
    disp = narc('a/1/8/0')
    t = bytearray(disp.files[0])
    for sp, nm, _ in ALL:
        s = TEMPLATE[nm]
        t[sp * 89:(sp + 1) * 89] = t[s * 89:(s + 1) * 89]
    disp.files[0] = bytes(t)
    for bank, article in ((237, False), (238, True)):
        key, rows = decode_messages(text.files[bank])
        for sp, nm, _ in ALL:
            assert rows[sp] == [65535], (bank, sp)
            rows[sp] = words(('an ' if nm[0] in 'AEIOU' else 'a ') + nm if article else nm)
        text.files[bank] = encode_messages(key, rows)
    # Eevee's evolution records: stones, Sun/Moon, Dusk Stone (Wraitheon); the held-item rules live in the hold table
    for sp, col in ((EEVEE, 1), (STARTER_EEVEE, 2)):
        rows = [(7, it, a1 if col == 1 else b1) for it, a1, b1 in sb.STONES]
        rows += [(7, sb.SUN, sb.SPECIES['espeon'][col - 1]), (7, sb.MOON, sb.SPECIES['umbreon'][col - 1])]
        rows.append((7, DUSK_STONE, (ordinary if col == 1 else starter)(NAMES.index('Wraitheon'))))
        if sp == STARTER_EEVEE:
            rows.append((7, sb.STELLAR_SANDWICH, sb.NOVAREON_STARTER))
        assert len(rows) <= 9
        ev.files[sp] = b''.join(struct.pack('<HHH', *r) for r in rows).ljust(56, b'\0')
    for name, a_ in ns.items():
        rom.setFileByName(name, a_.save())


def _hook_code(first, count, table, old, kind):
    head = f'''ldr r3, first
subs r3, r0, r3
cmp r3, #{count}
bhs next
'''
    if kind == 'forms':
        return head + f'''movs r0,#0
bx lr
next:
ldr r3, back
bx r3
.align 2
first: .word {first}
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
first: .word {first}
table: .word {table}
back: .word {old}
'''


def _put_code(gap, source, literals):
    gap.at = (gap.at + 3) & ~3
    raw = bytes(gap.ks.asm(source, addr=gap.at)[0])
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(raw[:-literals], gap.at):
        assert not (i.mnemonic.startswith('b') and i.mnemonic.endswith('.w')), i
    return gap.put(raw)


def _code(rom):
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm, ov131 = ovs[129], ovs[131]
    perm.data = bytearray(perm.data)
    ov131.data = bytearray(ov131.data)
    gap = Gap(perm, address, size)
    # larger hold table: (species, item, target) rows, zero-terminated; the Stage B wrapper's table pointer is repointed at it
    rules = [(EEVEE, sb.FAIRY_FEATHER, sb.SYLVEON[0]), (STARTER_EEVEE, sb.FAIRY_FEATHER, sb.SYLVEON[1])]
    for i, n in enumerate(NAMES):
        if n in HOLD_ITEMS:
            rules += [(EEVEE, HOLD_ITEMS[n], ordinary(i)), (STARTER_EEVEE, HOLD_ITEMS[n], starter(i))]
    raw = b''.join(struct.pack('<HHH', *r) for r in rules) + bytes(6)
    table = None
    for k in range(0, len(perm.data) - 3, 4):                         # the wrapper's literal: the Stage B hold table's address
        v = struct.unpack_from('<I', perm.data, k)[0]
        if 0x23DF000 <= v < 0x23E0000 and perm.data[v - perm.ramAddress:v - perm.ramAddress + 6] == struct.pack('<HHH', EEVEE, sb.FAIRY_FEATHER, sb.SYLVEON[0]):
            assert table is None, 'two candidates for the hold table pointer'
            table = v
    assert table, 'hold table pointer not found'
    start = table - perm.ramAddress
    stage_b_rules = 3 * 6 + 6                                          # Stage B left (Eevee, starter Eevee) + terminator... the rest of its reserved gap is zero
    assert not any(perm.data[start + 6 * 2 + 6:start + len(raw)]), 'the space after the Stage B hold table is not free'
    perm.data[start:start + len(raw)] = raw                            # grows in place into the rest of Stage B's reserved gap
    old_table = table
    alias = gap.put(b''.join(struct.pack('<H', TEMPLATE[n]) for _, n, _ in ALL))
    ovmap = {129: perm, 131: ov131}
    report = dict(hold_rules=len(rules), hold_table=hex(table), old_table=hex(old_table))
    for name, (ovid, site, lit) in HOOKS.items():
        ov = ovmap[ovid]
        at = site - ov.ramAddress + lit
        old = struct.unpack_from('<I', ov.data, at)[0]
        assert old & 1 and ov.ramAddress <= old - 1 < 0x23E0000, (name, hex(old))
        routine = _put_code(gap, _hook_code(FIRST, COUNT, alias, old, 'forms' if name == 'forms' else 'alias'), 8 if name == 'forms' else 12)
        struct.pack_into('<I', ov.data, at, routine | 1)
        report[name] = (hex(old), hex(routine))
    for ov in (perm, ov131):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    report['gap_used'] = gap.at - gap.start
    return report


def patch(rom):
    _tables(rom)
    return _code(rom)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
