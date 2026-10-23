"""Pokedex numbers and registration for the starter species and for forms (owner order 2026-10-23).

Problem: the engine shows a Pokemon's national number as `id` for ids up to 493 and `id - 50` above that (that part is right for base species), but a
Pokemon stored under one of the project's own species ids (starter Eevee/Psyduck, the starter Eevee line, their Megas; ids >= 1076) showed
nonsense numbers (starter Eevee 1561 -> 1511) and, when registered, set the flag of a species that has no dex entry instead of Eevee's.

Fix: the engine already keeps a table that maps every id >= 1076 back to its base species (a/0/2/8 file 12: index id-1076). That table is copied
into overlay 129 and used in three places:
 - the number routine (ARM9 0x020FF114, `get_dex_num_patch`) maps the species through the table before the national/regional lookup;
 - Pokedex_SetMonSeenFlag (0x0202A36C) and Pokedex_SetMonCaughtFlag (0x0202A434) read the species with GetMonData at 0x0202A37A / 0x0202A442; those two
   calls now go through a wrapper that maps the result through the table, so a starter Eevee registers as Eevee (133), a starter Vaporeon as Vaporeon, etc.
Novareon (1581/1582) maps to Umbreon in the table (its stand-in), so it registers as Umbreon until it gets a dex entry of its own.

Usage: dex_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap

NUMBER_ROUTINE = 0x020FF114
SEEN_READ, CAUGHT_READ = 0x0202A37A, 0x0202A442
GET_MON_DATA = 0x0206E540
REGIONAL_NUM = 0x0207185C
FIRST_FORM = 1076
RESERVE = 1368                                      # bytes, a multiple of 24


def bl(source, target):
    off = target - (source + 4)
    assert -(1 << 22) <= off < (1 << 22) and off % 2 == 0, hex(off)
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xF800 | ((off >> 1) & 0x7FF))


def patch(rom):
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    table = bytes(addons.files[12])
    count = len(table) // 2
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    table_at = gap.put(table)
    species_wrapper = gap.code(f'''push {{lr}}
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
    number_routine = gap.code(f'''push {{lr}}
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
''')
    for ov in (perm,):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    base = section.ramAddress
    # 1. number routine: jump to the new one (the original is `push {lr}; cmp r0,#0 ...`)
    at = NUMBER_ROUTINE - base
    assert bytes(section.data[at:at + 4]) == bytes.fromhex('00b50028'), bytes(section.data[at:at + 4]).hex()
    section.data[at:at + 8] = bytes.fromhex('004a1047') + struct.pack('<I', number_routine | 1)   # ldr r2,[pc,#0]; bx r2; .word
    # 2. the two species reads in Pokedex_SetMonSeenFlag / Pokedex_SetMonCaughtFlag
    for site in (SEEN_READ, CAUGHT_READ):
        at = site - base
        assert bytes(section.data[at:at + 4]) == bl(site, GET_MON_DATA), hex(site)
        section.data[at:at + 4] = bl(site, species_wrapper)
    rom.arm9 = main.save(compress=True)
    return dict(table_entries=count, table=hex(table_at), species_wrapper=hex(species_wrapper), number_routine=hex(number_routine), gap_used=gap.at - gap.start)


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
