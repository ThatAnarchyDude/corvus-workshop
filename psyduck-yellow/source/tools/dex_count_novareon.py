"""The Pokedex's Seen and Obtained totals count Novareon (owner decision 2026-10-27, built 2026-10-28).

Problem: the two counting functions (ARM9 0x02029E0C for Seen, 0x02029E48 for Obtained) walk species ids 1..1582 and skip the gap 494..543 between Gen 4 and Gen 5. Novareon's
Pokedex identity is id 500 (dex_novareon_id500.py: the species wrapper stores its flags at id 500, the list, number routine and pages already treat 500 as No. 1026, and the
gap test at 0x0202940C lets 500 through), but the counting loops skip it, so the totals never included it.
Fix: in both loops the two instructions that test "id is inside the gap" (adds r7,#0x32; cmp r4,r7) become a BL to a routine in overlay 129 that gives the same flags except
that id 500 compares as "not in the gap", so the loop calls the normal seen/obtained test for it. Every other id behaves exactly as before. Mega Novareon (1582) maps to the
same id 500 through the wrapper, so it does not count twice; the starter Eevee/Psyduck lines already map to their base species.

Usage: dex_count_novareon.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap

SITES = (0x02029E2C, 0x02029E68)        # adds r7,#0x32; cmp r4,r7   (seen loop, obtained loop)
OLD = '3237bc42'
NOVAREON_ID = 500


def _bl(site, target):
    off = (target - (site + 4)) >> 1
    assert target % 2 == 0 and -(1 << 21) <= off < (1 << 21), (hex(site), hex(target))
    return struct.pack('<HH', 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


def patch(rom):
    address, size = ext.reserve_code(rom, 24 * 2)                  # first: it rewrites overlay 129 (the header table moves up)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    routine = gap.code(f'''
movs r7, #{NOVAREON_ID // 2}
lsls r7, r7, #1
cmp r4, r7
beq out
adds r7, #{544 - NOVAREON_ID}
cmp r4, r7
out:
bx lr
''')
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    for site in SITES:
        at = site - section.ramAddress
        assert bytes(section.data[at:at + 4]).hex() == OLD, (hex(site), bytes(section.data[at:at + 4]).hex())
        section.data[at:at + 4] = _bl(site, routine)
    rom.arm9 = main.save(compress=True)
    return dict(routine=hex(routine), sites=[hex(s) for s in SITES], gap_left=gap.end - gap.at)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
