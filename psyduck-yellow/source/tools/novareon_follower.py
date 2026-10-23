"""Novareon's own overworld follower (owner request 2026-10-23).

The follower sprite of a Pokemon is looked up by tag 2500 + base species in the engine's overworld table (overlay 131), and each tag names a
BTX0 file (a/0/8/1, 8 frames of 32x32 plus a normal and a shiny palette). Novareon used Umbreon's follower because the engine reduces forms to their base
species (Novareon's base is Umbreon). The table has no entry to spare, so Novareon borrows the entry of species id 1560, the last form id before the starter species (a
form nothing in this campaign uses): tag 4060, file 1857.
 - File 1857 becomes Umbreon's follower model with its palettes recoloured to Novareon's (dark blue body, cream rings, amber eyes): the same frames, new colours.
 - In the overlay-129 routine that turns a species into the follower tag, the call that reduces the species to its base species (BL at 0x23DA7A2) goes
   through a small wrapper that answers 1560 for species 1581 and 1582. Every other species is untouched.
Real hand-drawn Novareon walking frames can replace file 1857's textures later; nothing else needs to change.

Usage: novareon_follower.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import ndspy.texture
import map_header_extension as ext
from mega_starter import Gap

DEX_ID, NOVAREON, MEGA_NOVAREON = 1560, 1581, 1582     # DEX_ID: the follower slot Novareon borrows (a form id nothing in the campaign uses)
UMBREON = 197
GFX_BASE = 297
TAG_BASE = 2500
BL_SITE, OLD_TARGET = 0x23DA7A2, 0x23D9AE4
TABLE = 0x23CA660                                 # overlay 131: 6-byte entries (tag, file, params), ended by tag 0xFFFF
# palette index -> new 8-bit colour (indices not listed keep their value)
RECOLOUR = {3: (134, 98, 68), 4: (232, 143, 58), 5: (150, 85, 30), 6: (17, 28, 41), 7: (28, 49, 69), 8: (44, 71, 98), 9: (65, 93, 123),
            10: (211, 175, 138), 11: (230, 212, 184), 12: (250, 236, 207), 13: (8, 14, 24), 14: (179, 189, 196)}


def bl(source, target):
    off = target - (source + 4)
    assert -(1 << 22) <= off < (1 << 22) and off % 2 == 0, hex(off)
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xF800 | ((off >> 1) & 0x7FF))


def read_bl(data, base, site):
    h1, h2 = struct.unpack_from('<HH', data, site - base)
    off = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if off & 0x400000:
        off -= 0x800000
    return site + 4 + off


def recoloured_model(raw):
    t = ndspy.texture.NSBTX(raw)
    for _, palette in t.palettes:
        colours = list(palette.colors)
        for index, (r, g, b) in RECOLOUR.items():
            old = colours[index]
            colours[index] = type(old)(r * 31 // 255, g * 31 // 255, b * 31 // 255, old.a)
        palette.colors = colours
    return t.save()


def patch(rom):
    # the table already has the entry for species 500
    ovs = rom.loadArm9Overlays()
    table = bytes(ovs[131].data)
    at = TABLE - ovs[131].ramAddress
    found = None
    while True:
        tag, gfx, params = struct.unpack_from('<HHH', table, at)
        if tag == 0xFFFF:
            break
        if tag == TAG_BASE + DEX_ID:
            found = (tag, gfx)
        at += 6
    assert found == (TAG_BASE + DEX_ID, GFX_BASE + DEX_ID), found
    models = ndspy.narc.NARC(rom.getFileByName('a/0/8/1'))
    models.files[GFX_BASE + DEX_ID] = recoloured_model(bytes(models.files[GFX_BASE + UMBREON]))
    rom.setFileByName('a/0/8/1', models.save())
    # the wrapper
    address, size = ext.reserve_code(rom, 96)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    wrapper = gap.code(f'''push {{r4, lr}}
movs r4, r0
ldr r3, orig
blx r3
ldr r1, nova
cmp r4, r1
beq mapped
ldr r1, mega
cmp r4, r1
bne done
mapped:
ldr r0, dexid
done:
pop {{r4, pc}}
.align 2
orig: .word {OLD_TARGET | 1}
nova: .word {NOVAREON}
mega: .word {MEGA_NOVAREON}
dexid: .word {DEX_ID}
''')
    assert read_bl(perm.data, perm.ramAddress, BL_SITE) == OLD_TARGET, hex(read_bl(perm.data, perm.ramAddress, BL_SITE))
    perm.data[BL_SITE - perm.ramAddress:BL_SITE - perm.ramAddress + 4] = bl(BL_SITE, wrapper)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(wrapper=hex(wrapper), file=GFX_BASE + DEX_ID, tag=TAG_BASE + DEX_ID)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
