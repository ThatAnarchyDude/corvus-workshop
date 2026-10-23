"""Starter Psyduck and Mega Psyduck, added the way starter Eevee / Mega Eevee were (private/build-starter-eevee-mega.py).

Two new internal species are appended after the Eevee pair: STARTER (1563) and MEGA (1564, the starter's form 1). Both copy
Psyduck's records (stats, ability, typing, moves, art), so the Mega inherits everything and only the Stone and the
starter-only rule are new. The starter cannot evolve (blank evolution record); ordinary Psyduck is untouched.
Psyduckite is a new item (3146) that only the starter Psyduck can use, through one more Mega-table entry.

Code lives in a gap reserved inside overlay 129 (map_header_extension.reserve_code moves the map-header table up). Each
existing Eevee hook is chained: the stub's literal is repointed at a new routine that handles the Psyduck IDs and then
jumps to the old Eevee routine, so every Eevee behaviour is unchanged.
"""
import copy
import json
import struct
from pathlib import Path
import ndspy.code
import ndspy.narc
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
import map_header_extension as ext
from prototype import decode_messages, encode_messages

BASE, STARTER, MEGA, STONE = 54, 1563, 1564, 3146
OLD_COUNT, COUNT = 1563, 1565
EEVEE_STARTER, EEVEE_STONE = 1561, 3145
RESERVE = 1200                                     # bytes of overlay-129 code/data space (50 table records' worth)
TEXT_MAP = json.loads((Path(__file__).resolve().parent / 'text-map.json').read_text())
CMD_SLOT = 0xFAD04                                 # script command 1, the starter-gift hook
HOOKS = {                                          # name: (overlay, site, offset of the stub's literal)
    'field': (131, 0x23C912A, 6),
    'tag': (129, 0x23DA73C, 4),
    'forms': (129, 0x23D9B54, 4),
}
MEGA_TABLE_SITES = (0x23CF9D4, 0x23CFABC, 0x23CFB7C)
MEGA_COUNT_SITES = ((0x23CF9C8, 0x2A60), (0x23CFAB0, 0x2D60), (0x23CFB6E, 0x2D60))


def _words(s):
    return [TEXT_MAP[c] for c in s] + [65535]


class Gap:
    """Bump allocator over the reserved overlay-129 space."""

    def __init__(self, ov, address, size):
        self.ov, self.start, self.end, self.at = ov, address, address + size, address
        self.ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)

    def put(self, raw):
        self.at = (self.at + 3) & ~3
        address = self.at
        assert address + len(raw) <= self.end, 'reserved code space exhausted'
        offset = address - self.ov.ramAddress
        self.ov.data[offset:offset + len(raw)] = raw
        self.at += len(raw)
        return address

    def code(self, source):
        self.at = (self.at + 3) & ~3
        raw = bytes(self.ks.asm(source, addr=self.at)[0])
        for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(raw, self.at):
            assert not (i.mnemonic.startswith('b') and i.mnemonic.endswith('.w')), i
        return self.put(raw)


def _extend_narcs(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]

    def append_records(name, stride=1, prefix=0, blank=False):
        a = narc(name)
        assert len(a.files) == prefix + OLD_COUNT * stride, (name, len(a.files))
        sample = a.files[prefix + BASE * stride:prefix + (BASE + 1) * stride]
        for _ in range(COUNT - OLD_COUNT):
            a.files.extend(bytes(len(f)) if blank else f for f in sample)

    for name, stride, prefix, blank in (('a/0/0/2', 1, 0, False), ('a/0/0/4', 6, 0, False), ('a/0/0/5', 4, 0, False),
                                        ('a/0/3/4', 1, 0, True), ('a/0/2/0', 1, 7, False)):
        append_records(name, stride, prefix, blank)
    a = narc('a/0/2/8')
    for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (14, 44), (15, 8)):
        b = bytearray(a.files[i])
        assert len(b) == OLD_COUNT * width, (i, len(b))
        b.extend(b[BASE * width:(BASE + 1) * width] * (COUNT - OLD_COUNT))
        a.files[i] = bytes(b)
    b = bytearray(a.files[11])                                        # species -> form row; 0x8000 marks a reverting form
    assert len(b) == OLD_COUNT * 64
    b.extend(bytes((COUNT - OLD_COUNT) * 64))
    struct.pack_into('<H', b, STARTER * 64, MEGA | 0x8000)
    a.files[11] = bytes(b)
    for i in (12, 13):                                                # external adjusted-form IDs alias back to Psyduck
        b = bytearray(a.files[i])
        assert len(b) == (OLD_COUNT - 1076) * 2
        b.extend(bytes((COUNT - OLD_COUNT) * 2))
        a.files[i] = bytes(b)
    b = bytearray(a.files[12])
    for ident in (STARTER, MEGA):
        struct.pack_into('<H', b, (ident - 1076) * 2, BASE)
    a.files[12] = bytes(b)
    levels = narc('a/0/3/3')
    b = bytearray(levels.files[0])
    stride = 34 * 4
    assert len(b) == OLD_COUNT * stride
    b.extend(b[BASE * stride:(BASE + 1) * stride] * (COUNT - OLD_COUNT))
    levels.files[0] = bytes(b)
    items = narc('a/0/1/7')
    assert len(items.files) == STONE
    items.files.append(items.files[EEVEE_STONE])                     # same Mega Stone record as Eonite
    gfx = narc('a/0/1/8')
    assert len(gfx.files) == EEVEE_STONE * 2 + 4
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
        for ident in (STARTER, MEGA):
            add_text(bank, ident, rows[BASE])
    add_text(222, STONE, _words('Psyduckite'))
    offset = STONE - 2685
    for bank, value in ((221, 'A Mega Stone for the starter Psyduck.'), (223, 'a Psyduckite'), (224, 'Psyduckites'), (829, 'Psyduckite')):
        add_text(bank, offset, _words(value))
    for name, a in ns.items():
        rom.setFileByName(name, a.save())


def _chain_alias(gap, old, species_to):
    return gap.code(f'''ldr r3, sid
cmp r0,r3
beq alias
adds r3,#1
cmp r0,r3
bne next
alias:
movs r0,#{species_to}
movs r1,#0
next:
push {{r4}}
ldr r4, back
mov ip,r4
pop {{r4}}
bx ip
.align 2
sid: .word {STARTER}
back: .word {old}
''')


def _chain_forms(gap, old):
    return gap.code(f'''ldr r3, sid
cmp r0,r3
beq base
adds r3,#1
cmp r0,r3
beq mega
push {{r4}}
ldr r4, back
mov ip,r4
pop {{r4}}
bx ip
base:
movs r0,#0
bx lr
mega:
movs r0,#1
bx lr
.align 2
sid: .word {STARTER}
back: .word {old}
''')


def _gift(gap, previous):
    return gap.code(f'''push {{r4,r5,r6,lr}}
movs r4,r0
ldr r3, original
blx r3
movs r6,r0
movs r0,r4
adds r0,#128
ldr r5,[r0]
ldr r0,[r5,#32]
ldr r0,[r0]
ldr r1,lab_map
cmp r0,r1
bne done
movs r0,r5
ldr r1, generation_var
ldr r3, getvar
blx r3
cmp r0,#1
bne done
ldr r0,[r5,#12]
ldr r3,getparty
blx r3
movs r1,#0
ldr r3,getmon
blx r3
movs r4,r0
movs r1,#5
movs r2,#0
ldr r3,getdata
blx r3
cmp r0,#{BASE}
bne done
sub sp,#8
ldr r0,starter
str r0,[sp]
movs r0,r4
movs r1,#5
mov r2,sp
ldr r3,setdata
blx r3
movs r0,r4
ldr r3,recalc
blx r3
add sp,#8
done:
movs r0,r6
pop {{r4,r5,r6,pc}}
.align 2
original: .word {previous}
lab_map: .word 505
generation_var: .word 0x416b
getvar: .word 0x020403ad
getparty: .word 0x02074905
getmon: .word 0x02074645
getdata: .word 0x0206e541
setdata: .word 0x0206ec41
recalc: .word 0x0206e251
starter: .word {STARTER}
''')


def patch(rom):
    for name, n in (('a/0/0/2', OLD_COUNT), ('a/0/3/4', OLD_COUNT)):
        assert len(ndspy.narc.NARC(rom.getFileByName(name)).files) == n, 'ROM does not have the Eevee species pair as its last species'
    _extend_narcs(rom)
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm, battle = ovs[129], ovs[130]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    # Mega table: all earlier entries (95 stock + starter Eevee) stay; one more entry for Psyduckite.
    old_table = struct.unpack_from('<I', battle.data, MEGA_TABLE_SITES[0] - battle.ramAddress)[0]
    for site in MEGA_TABLE_SITES:
        assert struct.unpack_from('<I', battle.data, site - battle.ramAddress)[0] == old_table
    entries = 96
    holder = battle if battle.ramAddress <= old_table < battle.ramAddress + len(battle.data) else perm
    raw = bytes(holder.data[old_table - holder.ramAddress:old_table - holder.ramAddress + entries * 4])
    assert struct.unpack_from('<I', raw, 95 * 4)[0] == EEVEE_STARTER | (EEVEE_STONE << 12) | (1 << 24), 'Mega table is not 95 stock entries + Eonite'
    table = gap.put(raw + struct.pack('<I', STARTER | (STONE << 12) | (1 << 24)))
    battle.data = bytearray(battle.data)
    for site in MEGA_TABLE_SITES:
        struct.pack_into('<I', battle.data, site - battle.ramAddress, table)
    for site, expected in MEGA_COUNT_SITES:
        assert struct.unpack_from('<H', battle.data, site - battle.ramAddress)[0] == expected
        struct.pack_into('<H', battle.data, site - battle.ramAddress, expected + 1)
    report = dict(mega_table=hex(table))
    # Chain the three Eevee hooks (field follower, overworld tag, form identity).
    ovmap = {129: perm, 131: ovs[131]}
    ovmap[131].data = bytearray(ovmap[131].data)
    for name, (ovid, site, lit) in HOOKS.items():
        ov = ovmap[ovid]
        at = site - ov.ramAddress + lit
        old = struct.unpack_from('<I', ov.data, at)[0]
        assert old & 1 and ov.ramAddress <= old - 1 < 0x23E0000, (name, hex(old))
        new = _chain_forms(gap, old) if name == 'forms' else _chain_alias(gap, old, BASE)
        struct.pack_into('<I', ov.data, at, new | 1)
        report[name] = (hex(old), hex(new))
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    previous = struct.unpack_from('<I', d, CMD_SLOT)[0]
    handler = _gift(gap, previous)
    struct.pack_into('<I', d, CMD_SLOT, handler | 1)
    report['gift'] = (hex(previous), hex(handler))
    for ov in (perm, battle, ovmap[131]):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    report['gap_used'] = gap.at - gap.start
    return report
