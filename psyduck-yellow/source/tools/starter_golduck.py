"""Starter Golduck (owner order 2026-11-01): the species a starter Psyduck evolves into, with Psyduckite Mega Evolution into the shared Mega Psyduck.

It lives in species row 1535, a filler row (rows 1535-1560 exist in every per-species table as unused copies of Eevee), so no table grows and no species-count literal changes.
 - row data: a copy of Golduck (55) in every table the other starter species copy (personal data, art, level-up list, TM row, display tables, names), with the shared Mega Psyduck (1564) as its form 1;
 - evolution: starter Psyduck (1563) evolves by the Moon Stone into 1535 (it pointed at the ordinary Golduck as an interim);
 - Mega table: one more entry (1535 + Psyduckite), so starter Golduck and starter Psyduck both Mega Evolve into Mega Psyduck;
 - code: the alias hooks (follower sprite, overworld tag) and the form hook of the earlier starter builders get one more link for id 1535.
Usage (from yellow-heartgold, PYTHONPATH=tools): starter_golduck.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from mega_starter import HOOKS, MEGA_COUNT_SITES, MEGA_TABLE_SITES, Gap
from prototype import decode_messages, encode_messages

NEW, BASE = 1535, 55
STARTER_PSYDUCK, MEGA_PSYDUCK, PSYDUCKITE, MOON_STONE = 1563, 1564, 3146, 81
FILLER = 1560
RESERVE = 27 * 24


def _row_copy(a, name, stride=1, prefix=0):
    got = a.files[prefix + FILLER * stride:prefix + (FILLER + 1) * stride]
    here = a.files[prefix + NEW * stride:prefix + (NEW + 1) * stride]
    assert [bytes(x) for x in got] == [bytes(x) for x in here], ('row 1535 is not an unused filler copy in ' + name)
    a.files[prefix + NEW * stride:prefix + (NEW + 1) * stride] = a.files[prefix + BASE * stride:prefix + (BASE + 1) * stride]


def _tables(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    for name, stride, prefix in (('a/0/0/2', 1, 0), ('a/0/0/4', 6, 0), ('a/0/0/5', 4, 0), ('a/0/2/0', 1, 7), ('a/1/4/1', 1, 0)):
        _row_copy(narc(name), name, stride, prefix)
    ev = narc('a/0/3/4')
    assert bytes(ev.files[NEW]) == bytes(ev.files[FILLER]), 'row 1535 is not an unused filler copy in a/0/3/4'
    ev.files[NEW] = bytes(len(ev.files[NEW]))                         # the filler copies Eevee's evolutions; starter Golduck evolves into nothing
    a = narc('a/0/2/8')
    for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (14, 44), (15, 8)):
        b = bytearray(a.files[i])
        assert b[FILLER * width:(FILLER + 1) * width] == b[NEW * width:(NEW + 1) * width], i
        b[NEW * width:(NEW + 1) * width] = b[BASE * width:(BASE + 1) * width]
        a.files[i] = bytes(b)
    b = bytearray(a.files[11])                                        # species -> form row; 0x8000 marks a reverting form
    assert b[NEW * 64:(NEW + 1) * 64] == b[FILLER * 64:(FILLER + 1) * 64], 'form row 1535 is not filler'
    b[NEW * 64:(NEW + 1) * 64] = bytes(64)
    struct.pack_into('<H', b, NEW * 64, MEGA_PSYDUCK | 0x8000)
    a.files[11] = bytes(b)
    b = bytearray(a.files[12])                                        # external adjusted-form ids alias back to the ordinary species
    assert b[(NEW - 1076) * 2:(NEW - 1075) * 2] == b[(FILLER - 1076) * 2:(FILLER - 1075) * 2], 'alias row 1535 is not filler'
    struct.pack_into('<H', b, (NEW - 1076) * 2, BASE)
    a.files[12] = bytes(b)
    levels = narc('a/0/3/3')
    b = bytearray(levels.files[0])
    stride = 34 * 4
    assert b[FILLER * stride:(FILLER + 1) * stride] == b[NEW * stride:(NEW + 1) * stride]
    b[NEW * stride:(NEW + 1) * stride] = b[BASE * stride:(BASE + 1) * stride]
    levels.files[0] = bytes(b)
    # evolution: starter Psyduck -> starter Golduck
    row = bytearray(ev.files[STARTER_PSYDUCK])
    assert struct.unpack_from('<HHH', row, 0)[:2] == (7, MOON_STONE) and not any(row[6:])
    struct.pack_into('<H', row, 4, NEW)
    ev.files[STARTER_PSYDUCK] = bytes(row)
    disp = narc('a/1/8/0')                                           # "spriteoffsets": 89 bytes per species
    t = bytearray(disp.files[0])
    assert len(t) >= (NEW + 1) * 89
    t[NEW * 89:(NEW + 1) * 89] = t[BASE * 89:(BASE + 1) * 89]
    disp.files[0] = bytes(t)
    text = narc('a/0/2/7')
    for bank in (237, 238):                                           # species name and its article form
        key, rows = decode_messages(text.files[bank])
        assert rows[NEW] == [65535], (bank, rows[NEW])
        rows[NEW] = rows[BASE]
        text.files[bank] = encode_messages(key, rows)
    for name, a in ns.items():
        rom.setFileByName(name, a.save())


def _code(gap, source):
    """Like Gap.code, but the wide-branch check skips the three literal words at the end (an address can decode as a 32-bit instruction)."""
    gap.at = (gap.at + 3) & ~3
    raw = bytes(gap.ks.asm(source, addr=gap.at)[0])
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(raw[:-12], gap.at):
        assert not (i.mnemonic.startswith('b') and i.mnemonic.endswith('.w')), i
    return gap.put(raw)


def _tail(old, table=0):
    return f'''push {{r4}}
ldr r4, back
mov ip,r4
pop {{r4}}
bx ip
.align 2
first: .word {NEW}
table: .word {table}
back: .word {old}
'''


def patch(rom):
    _tables(rom)
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm, battle = ovs[129], ovs[130]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    old_table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    for site in MEGA_TABLE_SITES:
        assert struct.unpack_from('<I', battle.data, site - battle.ramAddress)[0] == old_table
    holder = battle if battle.ramAddress <= old_table < battle.ramAddress + len(battle.data) else perm
    entries = 106
    raw = bytes(holder.data[old_table - holder.ramAddress:old_table - holder.ramAddress + entries * 4])
    last = struct.unpack_from('<I', raw, (entries - 1) * 4)[0]
    assert last & 0xFFF == 1581 + 0 or (last & 0xFFF) in range(1561, 1583), hex(last)
    assert struct.pack('<I', STARTER_PSYDUCK | (PSYDUCKITE << 12) | (1 << 24)) in raw, 'Mega table lacks the starter Psyduck entry'
    table = gap.put(raw + struct.pack('<I', NEW | (PSYDUCKITE << 12) | (1 << 24)))
    battle.data = bytearray(battle.data)
    for site in MEGA_TABLE_SITES:
        struct.pack_into('<I', battle.data, site - battle.ramAddress, table)
    counts = []
    for site, _ in MEGA_COUNT_SITES:
        at = site - battle.ramAddress
        value = struct.unpack_from('<H', battle.data, at)[0]
        assert value & 0xFF == entries, (hex(site), hex(value))      # cmp rN, #entries
        struct.pack_into('<H', battle.data, at, value + 1)
        counts.append(hex(value + 1))
    alias_table = gap.put(struct.pack('<H', BASE) + b'\0\0')
    ovmap = {129: perm, 131: ovs[131]}
    ovmap[131].data = bytearray(ovmap[131].data)
    report = dict(mega_table=hex(table), count_halfwords=counts)
    for name, (ovid, site, lit) in HOOKS.items():
        ov = ovmap[ovid]
        at = site - ov.ramAddress + lit
        old = struct.unpack_from('<I', ov.data, at)[0]
        assert old & 1 and ov.ramAddress <= old - 1 < 0x23E0000, (name, hex(old))
        if name == 'forms':
            routine = _code(gap, f'''ldr r3, first
cmp r0,r3
bne next
movs r0,#0
bx lr
next:
''' + _tail(old))
        else:
            routine = _code(gap, f'''ldr r3, first
cmp r0,r3
bne next
push {{r4}}
ldr r4, table
ldrh r0,[r4]
pop {{r4}}
movs r1,#0
next:
''' + _tail(old, alias_table))
        struct.pack_into('<I', ov.data, at, routine | 1)
        report[name] = (hex(old), hex(routine))
    for ov in (perm, battle, ovmap[131]):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    report['gap_used'] = gap.at - gap.start
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
