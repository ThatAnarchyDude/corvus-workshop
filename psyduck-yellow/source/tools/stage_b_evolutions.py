"""Stage B of the starter redesign (owner list 2026-11-01): how Eevee and starter Eevee evolve.
Use an item (native stone rows, all 9 slots of the Eevee record are enough):
  Thunder Stone -> Jolteon, Fire Stone -> Flareon, Water Stone -> Vaporeon, Leaf Stone -> Leafeon, Ice Stone -> Glaceon (unchanged),
  Sun Stone (80) -> Espeon, Moon Stone (81) -> Umbreon (replace the friendship day/night rows); starter Eevee also: Stellar Sandwich (new item 3143) -> starter Novareon.
  The Sylveon "knows a Fairy move" row is removed. Wraitheon (Dusk Stone), Brawleon and the other new species come when they exist.
Level up while holding an item (new, a table in code): Fairy Feather (2401) -> Sylveon; the held item is kept (owner 2026-11-01): the method code is left alone, because the native item codes make the game take the item.
  The wrapper in front of the project's evolution hook handles evolution context 0 (level up): it reads the Pokemon's species and held item and looks them up in a table (species, item, target) that can grow without limit.
The old shortcut rules for Eevee (Dawn/Dusk/Never-Melt Ice/Leaf) are removed from the live table (overlay 129 0x5A12; the ARM9 ITCM copy at 0x940 is dead since a later patch replaced its hook); Psyduck (Moon Stone) and Togepi stay.
Stellar Sandwich is a copy of the Sandwich item (1830), free id 3143. Plain Sandwich no longer evolves anything.
Usage (from yellow-heartgold, PYTHONPATH=tools): stage_b_evolutions.py <in.nds> <out.nds>"""
import json
import os
import copy
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
from prototype import decode_messages, encode_messages, thumb_bl
import map_header_extension as ext
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from mega_starter import Gap

EEVEE, STARTER_EEVEE = 133, 1561
SUN, MOON = 80, 81
STELLAR_SANDWICH, SANDWICH = 3143, 1830
FAIRY_FEATHER = 2401
STONES = ((85, 470, 1575), (849, 471, 1577), (83, 135, 1567), (84, 134, 1565), (82, 136, 1569))   # (item, ordinary target, starter target)
SPECIES = {'espeon': (196, 1571), 'umbreon': (197, 1573)}
NOVAREON_STARTER = 1581
SYLVEON = (750, 1579)
CALL_SITE = 0x02070E3E                                   # BL into overlay 129's evolution routine (a later patch replaced the ITCM hook)
OVERLAY_ROUTINE = 0x023DA578
EVO_ITEM_DAY = 18
DUMMY_ITEM = 0xFFFF
TEXT_MAP = json.loads(open(__file__.replace('stage_b_evolutions.py', 'text-map.json')).read())
OLD_RULES = ((54, 81, 55), (133, 109, 196), (133, 108, 197), (133, 246, 471), (133, 85, 470), (175, 109, 176))    # the overlay-129 table, 0x5A12
NEW_RULES = ((54, 81, 55), (175, 109, 176))
HOLD_RULES = ((EEVEE, FAIRY_FEATHER, SYLVEON[0]), (STARTER_EEVEE, FAIRY_FEATHER, SYLVEON[1]))


def words(s):
    return [TEXT_MAP[c] for c in s] + [65535]


def evolution_rows(rom):
    eid = rom.filenames.idOf('a/0/3/4')
    ev = ndspy.narc.NARC(rom.files[eid])
    for sp, col in ((EEVEE, 1), (STARTER_EEVEE, 2)):
        rows = [(7, it, a if col == 1 else b) for it, a, b in STONES]
        rows += [(7, SUN, SPECIES['espeon'][col - 1]), (7, MOON, SPECIES['umbreon'][col - 1])]
        if sp == STARTER_EEVEE:
            rows.append((7, STELLAR_SANDWICH, NOVAREON_STARTER))
        rows.append((EVO_ITEM_DAY, DUMMY_ITEM, SYLVEON[col - 1]))      # placeholder: no Pokemon holds item 0xFFFF, but a level-type row makes the game call the evolution check at level-up; the wrapper's table does the real matching
        old = bytes(ev.files[sp])
        assert len(old) == 56
        out = b''.join(struct.pack('<HHH', *r) for r in rows).ljust(56, b'\0')
        ev.files[sp] = out
    rom.files[eid] = ev.save()


def item_and_text(rom):
    narc = lambda p: ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)])
    items, gfx, text = narc('a/0/1/7'), narc('a/0/1/8'), narc('a/0/2/7')
    # the id must be an unused filler row
    rows = decode_messages(text.files[222])[1]
    assert rows[STELLAR_SANDWICH] == [65535], 'item 3143 is not free'
    items.files[STELLAR_SANDWICH] = bytes(items.files[SANDWICH])
    gfx.files[STELLAR_SANDWICH * 2 + 2] = bytes(gfx.files[SANDWICH * 2 + 2])
    gfx.files[STELLAR_SANDWICH * 2 + 3] = bytes(gfx.files[SANDWICH * 2 + 3])

    def put(bank, index, row):
        key, rows = decode_messages(text.files[bank])
        while len(rows) <= index:
            rows.append([65535])
        assert rows[index] == [65535], ('would replace text', bank, index)
        rows[index] = row
        text.files[bank] = encode_messages(key, rows)
    put(222, STELLAR_SANDWICH, words('Stellar Sandwich'))
    off = STELLAR_SANDWICH - 2685
    put(221, off, words('A sandwich that makes Eevee evolve.'))
    put(223, off, words('a Stellar Sandwich'))
    put(224, off, words('Stellar Sandwiches'))
    put(829, off, words('Stellar Sandwich'))
    for name, a in (('a/0/1/7', items), ('a/0/1/8', gfx), ('a/0/2/7', text)):
        rom.files[rom.filenames.idOf(name)] = a.save()


def wrapper_source(old, getmon, table_at, trace_at=None):
    t0 = f'''push {{r3}}
ldr r3, trace_ptr
strh r2,[r3]
pop {{r3}}
''' if trace_at is not None else ''
    t1 = '''ldr r3, trace_ptr
strh r6,[r3,#2]
strh r7,[r3,#4]
''' if trace_at is not None else ''
    tz = f'''.align 2
trace_ptr: .word {trace_at}
trace_area: .word 0,0
''' if trace_at is not None else ''
    table = ''.join(f'.short {a},{b},{c}\n' for a, b, c in HOLD_RULES) + '.short 0,0,0\n'
    return f'''{t0}cmp r2,#0
beq hold
tail:
push {{r4}}
ldr r4, old
mov ip, r4
pop {{r4}}
bx ip
hold:
push {{r0,r1,r2,r3,r4,r5,r6,r7,lr}}
mov r5, r1
movs r0, r5
movs r1, #5
movs r2, #0
ldr r3, getmon
blx r3
mov r6, r0
movs r0, r5
movs r1, #6
movs r2, #0
ldr r3, getmon
blx r3
mov r7, r0
{t1}ldr r1, hold_ptr
loop:
ldrh r2,[r1]
cmp r2,#0
beq nomatch
cmp r2,r6
bne next
ldrh r2,[r1,#2]
cmp r2,r7
bne next
ldrh r0,[r1,#4]
str r0,[sp]
pop {{r0,r1,r2,r3,r4,r5,r6,r7,pc}}
next:
adds r1,#6
b loop
nomatch:
pop {{r0,r1,r2,r3,r4,r5,r6,r7}}
push {{r4}}
ldr r4,[sp,#4]
mov lr, r4
ldr r4, old
mov ip, r4
pop {{r4}}
add sp,#4
bx ip
.align 2
old: .word {old | 1}
getmon: .word {getmon | 1}
hold_ptr: .word {table_at}
hold_table:
{table}{tz}'''


def code_changes(rom):
    address, size = ext.reserve_code(rom, 9 * 24)             # a gap in overlay 129 (it rewrites the ARM9 trampoline and overlay 129)
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    site = CALL_SITE - 0x02000000
    h1, h2 = struct.unpack_from('<HH', d, site)
    assert h1 & 0xF800 == 0xF000 and h2 & 0xF800 == 0xF800, 'no BL at the evolution call site'
    disp = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if disp & (1 << 22):
        disp -= 1 << 23
    old = CALL_SITE + 4 + disp
    assert old == OVERLAY_ROUTINE, hex(old)
    ovs = rom.loadArm9Overlays()
    o = ovs[129]
    o.data = bytearray(o.data)
    at129 = 0x5A12
    assert tuple(struct.unpack_from('<3H', o.data, at129 + 6 * k) for k in range(6)) == OLD_RULES, 'overlay-129 rules differ'
    for k in range(6):
        struct.pack_into('<3H', o.data, at129 + 6 * k, *(NEW_RULES[k] if k < len(NEW_RULES) else (0, 0, 0)))
    gap = Gap(o, address, size)
    gap.at = (gap.at + 3) & ~3
    trace = os.environ.get('STAGE_B_TRACE') == '1'                    # debug build: the wrapper records (context, species, held item) in its own data
    first = bytes(gap.ks.asm(wrapper_source(old, 0x0206E540, 0, 0 if trace else None), addr=gap.at)[0])
    # keystone writes label words as offsets, so the real addresses are computed here and written as numbers
    tail = 12 if trace else 0
    table_at = gap.at + len(first) - tail - 6 * (len(HOLD_RULES) + 1)
    trace_at = gap.at + len(first) - 8 if trace else None
    raw = bytes(gap.ks.asm(wrapper_source(old, 0x0206E540, table_at, trace_at), addr=gap.at)[0])
    assert len(raw) == len(first)
    literal_bytes = 12 + 6 * (len(HOLD_RULES) + 1) + (12 if trace else 0)
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(raw[:-literal_bytes], gap.at):
        assert not (i.mnemonic.startswith('b') and i.mnemonic.endswith('.w')), i
    wrapper = gap.put(raw)
    d[site:site + 4] = thumb_bl(CALL_SITE, wrapper)
    # other code calls the overlay-129 routine directly through a stored address (the party menu's level-up check is one): point those at the wrapper too
    literal = struct.pack('<I', old | 1)
    redirected = []
    for oid, ov in ovs.items():
        if oid == 129:
            data = o.data
            skip = range(wrapper - ov.ramAddress, wrapper - ov.ramAddress + len(raw))
        else:
            if ov.compressed:
                continue
            data = ov.data = bytearray(ov.data)
            skip = ()
        i = -1
        while True:
            i = bytes(data).find(literal, i + 1)
            if i < 0:
                break
            if i % 4 == 0 and i not in skip:
                struct.pack_into('<I', data, i, wrapper | 1)
                redirected.append((oid, hex(ov.ramAddress + i)))
        if oid != 129 and any(r[0] == oid for r in redirected):
            rom.files[ov.fileID] = ov.save(compress=False)
    rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return dict(old=hex(old), wrapper=hex(wrapper), wrapper_bytes=len(raw), redirected=redirected, hold_table=hex(table_at), trace_area=hex(trace_at) if trace else None)


def patch(rom):
    evolution_rows(rom)
    item_and_text(rom)
    return code_changes(rom)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
