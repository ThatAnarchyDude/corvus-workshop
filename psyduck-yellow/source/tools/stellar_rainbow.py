"""The Stellar type chip with a six-colour rainbow background (red, orange, yellow, green, blue, purple).

Every type chip draws from one palette file, a/0/0/8 file 74, which holds three 16-colour banks; ARM9 0x21000A4 is a
byte per type naming the bank, and two spots (ARM9 0x2077708 and 0x207773E, `movs r0,#3`) tell the sprite loader how many
banks to load. This adds a fourth bank holding the rainbow, grows the palette file's bank map to match, loads four banks,
and sends type 19 (Stellar) to bank 3. The chip graphic (a/0/0/8 file 369) is redrawn with diagonal rainbow bands, the
white STELLAR lettering with its dark shadow, and the same rim as the other chips. Every other chip keeps its bank.

Usage: stellar_rainbow.py <in.nds> <out.nds>      (input: a ROM that already has the STELLAR chip, i.e. 0048)
"""
import struct
import sys
import ndspy.lz10
import ndspy.narc
import ndspy.rom
import new_images as N

PALETTE_FILE = 74
CHIP_FILE = 369
BANK_TABLE = 0x21000A4
BANK_TABLE_LEN = 23
STELLAR_TYPE = N.STELLAR_INDEX                  # 19
LOAD_COUNT_SITES = (0x2077708, 0x207773E)       # movs r0,#3
OLD_BANKS, NEW_BANK = 3, 3

RAINBOW = [(240, 56, 56), (248, 144, 40), (248, 216, 48), (64, 200, 72), (56, 120, 248), (152, 72, 216)]
RIM, SHADOW, WHITE = (232, 232, 248), (40, 32, 88), (255, 255, 255)
RIM_I, SHADOW_I, WHITE_I = 7, 14, 15


def bgr555(rgb):
    return (rgb[0] >> 3) | ((rgb[1] >> 3) << 5) | ((rgb[2] >> 3) << 10)


def rainbow_bank():
    colors = [0] * 16
    for i, rgb in enumerate(RAINBOW):
        colors[1 + i] = bgr555(rgb)
    colors[RIM_I], colors[SHADOW_I], colors[WHITE_I] = bgr555(RIM), bgr555(SHADOW), bgr555(WHITE)
    return struct.pack('<16H', *colors)


def grow_palette_file(raw):
    """Append a fourth bank to the RLCN and bring the block sizes and the bank map up to date."""
    assert raw[:4] == b'RLCN' and raw[16:20] == b'TTLP'
    pltt_size = struct.unpack_from('<I', raw, 20)[0]
    assert pltt_size == 0x78 and raw[16 + pltt_size:16 + pltt_size + 4] == b'PMCP', 'unexpected palette file layout'
    pmcp = raw[16 + pltt_size:]
    count = struct.unpack_from('<H', pmcp, 8)[0]
    assert count == OLD_BANKS and len(pmcp) == 22
    data_end = 16 + pltt_size
    out = bytearray(raw[:data_end]) + rainbow_bank()
    struct.pack_into('<I', out, 20, pltt_size + 32)
    new_pmcp = bytearray(pmcp[:16]) + struct.pack('<4H', 0, 1, 2, 3)
    struct.pack_into('<I', new_pmcp, 4, len(new_pmcp))
    struct.pack_into('<H', new_pmcp, 8, 4)
    out += new_pmcp
    struct.pack_into('<I', out, 8, len(out))
    return bytes(out)


def rainbow_grid():
    grid = [[0] * 32 for _ in range(16)]
    def band(x, y):
        return 1 + max(0, min(5, int((x - 0.5 * (y - 7) + 0.5) * 6 / 32)))
    for x in range(1, 31):
        grid[1][x] = RIM_I
    for y in range(2, 13):
        for x in range(32):
            grid[y][x] = band(x, y)
    for x in (0, 31):
        grid[2][x] = RIM_I
    for x in range(32):
        grid[13][x] = band(x, 13)
    grid[13][0] = grid[13][31] = SHADOW_I
    for x in range(1, 31):
        grid[14][x] = SHADOW_I
    dots = set()
    x0 = 2
    for ch in N.TEXT:
        g = N.GLYPHS[ch]
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                if c == '#':
                    dots.add((x0 + x, 4 + y))
        x0 += len(g[0]) + 1
    assert x0 - 1 <= 30
    for (x, y) in dots:
        for sx, sy in ((x + 1, y), (x, y + 1)):
            if (sx, sy) not in dots:
                grid[sy][sx] = SHADOW_I
    for (x, y) in dots:
        grid[y][x] = WHITE_I
    return grid


def patch(rom):
    chips = ndspy.narc.NARC(rom.getFileByName(N.CHIP_ARCHIVE))
    chips.files[PALETTE_FILE] = grow_palette_file(bytes(chips.files[PALETTE_FILE]))
    beauty = ndspy.lz10.decompress(bytes(chips.files[N.BEAUTY_CHIP]))
    chips.files[CHIP_FILE] = ndspy.lz10.compress(N.chip_bytes(beauty, rainbow_grid()))
    rom.setFileByName(N.CHIP_ARCHIVE, chips.save())
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    base = section.ramAddress
    assert struct.unpack_from('<I', section.data, N.CHIP_TABLE - base + 4 * STELLAR_TYPE)[0] == CHIP_FILE
    assert section.data[BANK_TABLE - base + STELLAR_TYPE] == 1, 'Stellar should still be on the BEAUTY chip bank'
    section.data[BANK_TABLE - base + STELLAR_TYPE] = NEW_BANK
    for site in LOAD_COUNT_SITES:
        assert bytes(section.data[site - base:site - base + 2]) == bytes.fromhex('0320'), hex(site)
        section.data[site - base:site - base + 2] = bytes.fromhex('0420')
    rom.arm9 = main.save(compress=True)
    return dict(palette_banks=4, stellar_bank=NEW_BANK)


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
