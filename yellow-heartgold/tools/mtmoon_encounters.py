"""Select Yellow's deepest-cave encounters in the existing fossil corridor.

Use the player's live tile, rather than the last saved location. No terrain,
map headers, save data or encounter behavior outside Mt. Moon is changed.
"""
import struct
import ndspy.narc
from mtmoon import DATA
from forest_progression import SLOT_MAP
from viridian_tutorial import TABLE
from starter_properties import append_code

GET_TABLE = 0x0203B8B8
ORIGINAL = bytes.fromhex('41699220000108187047')


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    at = GET_TABLE - 0x02000000
    assert d[at:at+10] == ORIGINAL
    assert struct.unpack_from('<I', d, 0xD2C68)[0] == main.sections[1].ramAddress + len(main.sections[1].data)
    bank = d[TABLE + 107*24]
    wild = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/7')])
    table = bytearray(wild.files[bank])
    assert len(table) == 196
    slots = [DATA['wild_slots']['B2F'][i] for i in SLOT_MAP]
    table[8:20] = bytes(p['level'] for p in slots)
    species = [p['species'] for p in slots]
    for period in range(3):
        struct.pack_into('<12H', table, 20+24*period, *species)
    for offset in (0x5C, 0x60, 0x64, 0x68, 0xBC):
        struct.pack_into('<2H', table, offset, species[0], species[1])
    itcm = main.sections[1]
    itcm.data.extend(bytes(-len(itcm.data) % 4))
    address = itcm.ramAddress + len(itcm.data)
    itcm.data.extend(table)
    code, _ = append_code(main, f'''
ldr r1, [r0, #0x14]
ldr r2, [r0, #0x20]
cmp r2, #0
beq original
ldr r2, [r2]
cmp r2, #107
bne original
ldr r2, [r0, #0x40]
cmp r2, #0
beq original
ldr r2, [r2, #0x30]
cmp r2, #0
beq original
ldr r2, [r2, #0x6c]
cmp r2, #20
blo original
ldr r0, deepest
bx lr
original:
movs r0, #0x92
lsls r0, r0, #4
adds r0, r1, r0
bx lr
.align 2
deepest: .word {address}
''')
    d[at:at+8] = bytes.fromhex('004b1847') + struct.pack('<I', code|1)
    struct.pack_into('<I', d, 0xD2C68, itcm.ramAddress + len(itcm.data))
    rom.arm9 = main.save(compress=True)
    return dict(map=107, region='live player tile z >= 20; fossil corridor',
                yellow_floor='B2F', table=hex(address), hook=hex(code),
                slots=slots, all_other_maps_unchanged=True)
