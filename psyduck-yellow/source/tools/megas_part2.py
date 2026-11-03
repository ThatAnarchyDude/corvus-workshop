"""Stage D3: three more species rows (1583-1585) and the Megas of starter Strateon, Wyrmeon and Ferreon (owner order 2026-11-01, option "grow the tables").

The per-species tables stop at row 1582. Here every one of them grows by three rows (copies of the unused filler row 1560 first, then filled like megas_part1's Megas):
 a/0/0/2, a/0/0/4 (6 files per species), a/0/0/5 (4), a/0/2/0 (prefix 7), a/0/3/4, a/0/6/9, a/1/4/1, a/2/2/1, a/2/4/8, a/2/5/6 (one file per species), a/0/2/8 files 7-15, a/0/3/3 and a/1/8/0
 (one big file), and the species name banks 237/238.
Code: the TM check literal (overlay 129 0x023DB208, was 1582) becomes 1585; the Mega table (113 entries) moves to a larger copy (116) in the end of the dead dex region of overlay 129 and the
alias/form hooks get one more chained link for ids 1583-1585 (they go in the old table's space). The Pokedex limit (1582) is left alone: a Mega id above it is rejected by the Pokedex, which is what a Mega should get.
Ordinary Novareon needed no row (species 500, see novareon_ordinary.py).
Usage (from yellow-heartgold, PYTHONPATH=tools): megas_part2.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
from mega_starter import EEVEE_STONE, HOOKS, MEGA_COUNT_SITES, MEGA_TABLE_SITES, Gap
import megas_part1 as p1
from new_eeveelutions import NAMES, starter
from prototype import decode_messages, encode_messages

MEGA_FOR = ('Strateon', 'Wyrmeon', 'Ferreon')
FIRST, NEW = 1583, 3
FILLER = 1560
TM_LITERAL, TM_OLD = 0x023DB208, 1582
OLD_TABLE_AT, OLD_ENTRIES = 0x023DEC50, 113
NEW_TABLE_AT, FREE_END = 0x023DEE80, 0x023DF060


def _grow(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    for name, stride, prefix in (('a/0/0/2', 1, 0), ('a/0/0/4', 6, 0), ('a/0/0/5', 4, 0), ('a/0/2/0', 1, 7), ('a/0/3/4', 1, 0), ('a/0/6/9', 1, 0), ('a/1/4/1', 1, 0),
                                 ('a/2/2/1', 1, 0), ('a/2/4/8', 1, 0), ('a/2/5/6', 1, 0)):
        a = narc(name)
        assert len(a.files) == prefix + FIRST * stride, (name, len(a.files))
        for _ in range(NEW):
            a.files.extend(bytes(x) for x in a.files[prefix + FILLER * stride:prefix + (FILLER + 1) * stride])
    t = narc('a/0/2/8')
    for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (11, 64), (14, 44), (15, 8)):
        b = bytes(t.files[i])
        assert len(b) == FIRST * width, (i, len(b))
        t.files[i] = b + b[FILLER * width:(FILLER + 1) * width] * NEW
    for i in (12, 13):
        b = bytes(t.files[i])
        assert len(b) == (FIRST - 1076) * 2, (i, len(b))
        t.files[i] = b + b[(FILLER - 1076) * 2:(FILLER - 1075) * 2] * NEW
    ls = narc('a/0/3/3')
    b = bytes(ls.files[0])
    assert len(b) == FIRST * 136
    ls.files[0] = b + b[FILLER * 136:(FILLER + 1) * 136] * NEW
    d = narc('a/1/8/0')
    b = bytes(d.files[0])
    assert len(b) == FIRST * 89, len(b)
    d.files[0] = b + b[FILLER * 89:(FILLER + 1) * 89] * NEW
    text = narc('a/0/2/7')
    for bank in (237, 238):
        key, rows = decode_messages(text.files[bank])
        assert len(rows) == FIRST, (bank, len(rows))
        rows = list(rows) + [[65535]] * NEW
        text.files[bank] = encode_messages(key, rows)
    for name, a in ns.items():
        rom.setFileByName(name, a.save())


def _code(rom):
    ovs = rom.loadArm9Overlays()
    perm, battle, ov131 = ovs[129], ovs[130], ovs[131]
    perm.data, battle.data, ov131.data = bytearray(perm.data), bytearray(battle.data), bytearray(ov131.data)
    base = perm.ramAddress
    old_table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    assert old_table == OLD_TABLE_AT, hex(old_table)
    for site in MEGA_TABLE_SITES:
        assert struct.unpack_from('<I', battle.data, site - battle.ramAddress)[0] == old_table
    assert not any(perm.data[NEW_TABLE_AT - base:FREE_END - base]), 'the new table space is not free'
    raw = bytes(perm.data[old_table - base:old_table - base + OLD_ENTRIES * 4])
    assert struct.unpack_from('<I', raw, (OLD_ENTRIES - 1) * 4)[0] == starter(NAMES.index('Chryseon')) | (EEVEE_STONE << 12) | (1 << 24), 'not the megas_part1 table'
    new = b''.join(struct.pack('<I', starter(NAMES.index(n)) | (EEVEE_STONE << 12) | (1 << 24)) for n in MEGA_FOR)
    table = NEW_TABLE_AT
    perm.data[table - base:table - base + len(raw) + len(new)] = raw + new
    assert table + len(raw) + len(new) <= FREE_END
    for site in MEGA_TABLE_SITES:
        struct.pack_into('<I', battle.data, site - battle.ramAddress, table)
    counts = []
    for site, _ in MEGA_COUNT_SITES:
        at = site - battle.ramAddress
        value = struct.unpack_from('<H', battle.data, at)[0]
        assert value & 0xFF == OLD_ENTRIES, (hex(site), hex(value))
        struct.pack_into('<H', battle.data, at, value + NEW)
        counts.append(hex(value + NEW))
    # the old table's space (452 bytes) holds the new hook links
    perm.data[OLD_TABLE_AT - base:OLD_TABLE_AT - base + OLD_ENTRIES * 4] = bytes(OLD_ENTRIES * 4)
    gap = Gap(perm, OLD_TABLE_AT, OLD_ENTRIES * 4)
    p1.FIRST, p1.MEGA_FOR = FIRST, MEGA_FOR
    alias = gap.put(b''.join(struct.pack('<H', p1.TEMPLATE[n]) for n in MEGA_FOR))
    ovmap = {129: perm, 131: ov131}
    report = dict(mega_table=hex(table), counts=counts)
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
    struct.pack_into('<I', perm.data, at, FIRST + NEW - 1)
    for ov in (perm, battle, ov131):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    report['old_space_left'] = gap.end - gap.at
    return report


def patch(rom):
    _grow(rom)
    p1.MEGA_FOR, p1.MEGA_ROWS = MEGA_FOR, tuple(FIRST + k for k in range(NEW))
    p1._tables(rom)
    return _code(rom)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
