"""A non-rainbow STELLAR chip for the Summary screen's type chips (owner report 2026-10-23: its colours were wrong there).

The Summary draws type chips as background tiles with ARM9 code at 0x0208BA88 that only ever gets three palette banks, so the rainbow chip (bank 3) came out in the wrong colours
(see SESSION-HANDOFF.md). Every other screen is fine. This adds a second Stellar chip drawn with the colours of bank 1 only (violet/blue/cyan/pink "nebula" bands, white lettering) and
makes that one function use it: type 19 is swapped for the spare chip slot 22 (contest slot, unused in the campaign), whose chip-table entry is the new chip and whose bank is 1.
The rainbow chip stays for the battle screens and the Summary header.

Usage: stellar_summary_chip.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.lz10
import ndspy.narc
import ndspy.rom
import capstone
import map_header_extension as ext
from mega_starter import Gap
import new_images as N
import stellar_rainbow as R

SLOT = 22
FUNCTION_SITE = 0x0208BA8C                      # adds r7,r3,#0 ; adds r5,r0,#0 inside the BG type-chip drawing function
BANDS = (11, 8, 9, 5, 4, 2)                     # bank-1 colours: magenta, pink, peach, cyan, blue, violet
RIM, SHADOW, WHITE = 7, 14, 15


def bl(source, target):
    off = target - (source + 4)
    assert -(1 << 22) <= off < (1 << 22) and off % 2 == 0, hex(off)
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xF800 | ((off >> 1) & 0x7FF))


def grid():
    g = [[0] * 32 for _ in range(16)]
    def band(x, y):
        return BANDS[max(0, min(5, int((x - 0.5 * (y - 7) + 0.5) * 6 / 32)))]
    for x in range(1, 31):
        g[1][x] = RIM
    for y in range(2, 13):
        for x in range(32):
            g[y][x] = band(x, y)
    for x in (0, 31):
        g[2][x] = RIM
    for x in range(32):
        g[13][x] = band(x, 13)
    g[13][0] = g[13][31] = SHADOW
    for x in range(1, 31):
        g[14][x] = SHADOW
    dots = set()
    x0 = 2
    for ch in N.TEXT:
        glyph = N.GLYPHS[ch]
        for y, row in enumerate(glyph):
            for x, c in enumerate(row):
                if c == '#':
                    dots.add((x0 + x, 4 + y))
        x0 += len(glyph[0]) + 1
    for (x, y) in dots:
        for sx, sy in ((x + 1, y), (x, y + 1)):
            if (sx, sy) not in dots:
                g[sy][sx] = SHADOW
    for (x, y) in dots:
        g[y][x] = WHITE
    return g


def patch(rom):
    chips = ndspy.narc.NARC(rom.getFileByName(N.CHIP_ARCHIVE))
    beauty = ndspy.lz10.decompress(bytes(chips.files[N.BEAUTY_CHIP]))
    chips.files.append(ndspy.lz10.compress(N.chip_bytes(beauty, grid())))
    new_file = len(chips.files) - 1
    rom.setFileByName(N.CHIP_ARCHIVE, chips.save())
    address, size = ext.reserve_code(rom, 24)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    routine = gap.code(f'''adds r7, r3, #0
adds r5, r0, #0
cmp r7, #19
bne done
movs r7, #{SLOT}
done:
bx lr
''')
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    base = section.ramAddress
    at = FUNCTION_SITE - base
    text = ' ; '.join(f'{i.mnemonic} {i.op_str}' for i in capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB).disasm(bytes(section.data[at:at + 4]), FUNCTION_SITE))
    assert text == 'adds r7, r3, #0 ; adds r5, r0, #0', text
    section.data[at:at + 4] = bl(FUNCTION_SITE, routine)
    struct.pack_into('<I', section.data, N.CHIP_TABLE - base + 4 * SLOT, new_file)
    assert section.data[R.BANK_TABLE - base + SLOT] in (0, 1, 2), section.data[R.BANK_TABLE - base + SLOT]
    section.data[R.BANK_TABLE - base + SLOT] = 1
    rom.arm9 = main.save(compress=True)
    return dict(chip_file=new_file, slot=SLOT, routine=hex(routine))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
