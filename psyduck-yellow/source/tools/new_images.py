"""The three missing images: Stellar type chip, Sandwich item icon, Novareon party icon.

 - Stellar chip: the summary screen's type chips are LZ10-compressed 32x16 4bpp graphics in a/0/0/8 (files 219-241 for the
   types and contest conditions), chosen through a table of 4-byte file numbers at ARM9 0x2100048 (index 19 -> BEAUTY, which
   is why a Stellar Pokemon showed a BEAUTY chip). A new chip reading "STELLAR" is drawn in the chips' own style (the BEAUTY
   chip's body/colour indices and the 5x7 letter shapes of the existing chips), appended to a/0/0/8, and table entry 19 now
   points at it. The chip keeps the palette slots of the chip it replaces, so it takes that chip's colours.
 - Sandwich icon: a 32x32 pixel-art sandwich replaces the "?" placeholder (a/0/1/8, converted with the engine's nitrogfx).
 - Novareon party/menu icon: the supplied 32x32 candidate, fitted to the nearest of the three shared icon palettes, two
   frames (the second bobs down one pixel), for species 1581 and 1582; their palette-index byte (a/0/2/8 file 9) is set.

Usage: new_images.py <in.nds> <out.nds> <extracted 010_Novareon folder> <work dir>
"""
import struct
import subprocess
import sys
from pathlib import Path
import ndspy.lz10
import ndspy.narc
import ndspy.rom
from PIL import Image, ImageDraw

SANDWICH = 1830
NOVAREON = (1581, 1582)
CHIP_ARCHIVE = 'a/0/0/8'
BEAUTY_CHIP = 219
CHIP_TABLE = 0x2100048
STELLAR_INDEX = 19
ENGINE = Path(__file__).resolve().parents[2] / 'private/hg-engine-0037-v1/hg-engine-main'
GFX = ENGINE / 'tools/nitrogfx'

# 3x7 letters (the S is 4 wide) in the chips' own style (1 = letter body); each gets a one-pixel shadow to its right and below.
GLYPHS = {
    'S': ['.##.', '#..#', '#...', '.##.', '...#', '#..#', '.##.'],   # 4 wide: the rounder S
    'T': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '.#.'],
    'E': ['###', '#..', '#..', '##.', '#..', '#..', '###'],
    'L': ['#..', '#..', '#..', '#..', '#..', '#..', '###'],
    'A': ['.#.', '#.#', '#.#', '###', '#.#', '#.#', '#.#'],
    'R': ['##.', '#.#', '#.#', '##.', '#.#', '#.#', '#.#'],
}
TEXT = 'STELLAR'


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def chip_grid(raw):
    size = struct.unpack_from('<I', raw, 16 + 0x18)[0]
    data = raw[16 + 0x20:16 + 0x20 + size]
    px = []
    for b in data:
        px += [b & 15, b >> 4]
    grid = [[0] * 32 for _ in range(16)]
    for t in range(len(px) // 64):
        for y in range(8):
            for x in range(8):
                grid[(t // 4) * 8 + y][(t % 4) * 8 + x] = px[t * 64 + y * 8 + x]
    return grid


def chip_bytes(raw, grid):
    out = bytearray()
    for t in range(8):
        for y in range(8):
            row = [grid[(t // 4) * 8 + y][(t % 4) * 8 + x] for x in range(8)]
            out += bytes(row[i] | (row[i + 1] << 4) for i in range(0, 8, 2))
    size = struct.unpack_from('<I', raw, 16 + 0x18)[0]
    assert len(out) == size
    return raw[:16 + 0x20] + bytes(out) + raw[16 + 0x20 + size:]


def draw_stellar_chip(beauty_raw):
    grid = chip_grid(beauty_raw)
    body, letter, shadow = grid[3][1], 0xF, 0xE
    assert body == 4, 'unexpected BEAUTY chip layout'
    for y in range(4, 12):
        for x in range(32):
            grid[y][x] = body
    dots = set()
    x0 = 2
    for ch in TEXT:
        g = GLYPHS[ch]
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                if c == '#':
                    dots.add((x0 + x, 4 + y))
        x0 += len(g[0]) + 1
    assert x0 - 1 <= 30, x0                              # last letter plus its shadow column must fit in 32
    for (x, y) in dots:
        for sx, sy in ((x + 1, y), (x, y + 1)):
            if (sx, sy) not in dots and sx < 32 and sy < 12:
                grid[sy][sx] = shadow
    for (x, y) in dots:
        grid[y][x] = letter
    return grid


def sandwich_png(path):
    pal = [(255, 0, 255), (60, 36, 14), (217, 164, 65), (240, 205, 120), (168, 112, 40), (96, 176, 72), (60, 130, 50),
           (214, 64, 48), (244, 214, 84), (232, 144, 154), (255, 244, 214), (190, 120, 128), (255, 255, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
    im = Image.new('P', (32, 32), 0)
    flat = [c for rgb in pal for c in rgb] + [0] * (768 - 48)
    im.putpalette(flat)
    d = ImageDraw.Draw(im)
    d.ellipse((4, 5, 27, 17), fill=2)                       # top bun dome
    d.rectangle((4, 12, 27, 14), fill=2)
    d.arc((5, 6, 26, 16), 200, 300, fill=3)
    for x, y in ((11, 8), (15, 7), (19, 8), (13, 10), (17, 10), (21, 10), (9, 11)):
        d.point((x, y), fill=10)                            # sesame
    d.rectangle((3, 15, 28, 16), fill=5)                    # lettuce
    for x in range(3, 29, 3):
        d.point((x, 17), fill=5); d.point((x + 1, 17), fill=6)
    d.rectangle((5, 18, 26, 19), fill=7)                    # tomato
    d.rectangle((4, 20, 27, 21), fill=8)                    # cheese
    d.polygon([(6, 22), (12, 22), (9, 25)], fill=8)
    d.rectangle((5, 22, 26, 23), fill=9)                    # ham
    d.point((8, 22), fill=11); d.point((15, 23), fill=11); d.point((22, 22), fill=11)
    d.rounded_rectangle((4, 24, 27, 28), radius=2, fill=4)  # bottom bun
    d.rectangle((6, 24, 25, 25), fill=2)
    px = im.load()
    out = [[px[x, y] for x in range(32)] for y in range(32)]
    for y in range(32):                                     # dark outline round everything
        for x in range(32):
            if out[y][x] == 0 and any(0 <= x + dx < 32 and 0 <= y + dy < 32 and px[x + dx, y + dy] not in (0, 1)
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = 1
    for y in range(32):
        for x in range(32):
            px[x, y] = out[y][x]
    im.save(path, transparency=0)


def icon_frames(candidate, palettes):
    """The candidate fitted to the closest shared palette: returns (bank, [frame1, frame2]) as 32x32 index grids."""
    src = Image.open(candidate).convert('RGBA')
    assert src.size == (32, 32)
    best = None
    for bank, colors in enumerate(palettes):
        err, grid = 0, []
        for y in range(32):
            row = []
            for x in range(32):
                r, g, b, a = src.getpixel((x, y))
                if a < 128:
                    row.append(0)
                    continue
                i, e = min(((i, (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2) for i, c in enumerate(colors) if i), key=lambda t: t[1])
                err += e
                row.append(i)
            grid.append(row)
        if best is None or err < best[0]:
            best = (err, bank, grid)
    _, bank, grid = best
    second = [[0] * 32] + [row[:] for row in grid[:-1]]
    return bank, [grid, second]


def icon_payload(frames):
    px = []
    for g in frames:
        for t in range(16):
            for y in range(8):
                px += [g[(t // 4) * 8 + y][(t % 4) * 8 + x] for x in range(8)]
    return bytes(px[i] | (px[i + 1] << 4) for i in range(0, len(px), 2))


def patch(rom, art, work):
    art, work = Path(art), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    # --- Stellar type chip
    chips = ndspy.narc.NARC(rom.getFileByName(CHIP_ARCHIVE))
    beauty = ndspy.lz10.decompress(bytes(chips.files[BEAUTY_CHIP]))
    assert beauty[:4] == b'RGCN' and len(beauty) == 304
    chip = chip_bytes(beauty, draw_stellar_chip(beauty))
    chips.files.append(ndspy.lz10.compress(chip))
    new_file = len(chips.files) - 1
    rom.setFileByName(CHIP_ARCHIVE, chips.save())
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    at = CHIP_TABLE - section.ramAddress + 4 * STELLAR_INDEX
    assert struct.unpack_from('<I', section.data, at)[0] == BEAUTY_CHIP
    struct.pack_into('<I', section.data, at, new_file)
    rom.arm9 = main.save(compress=True)
    # --- Sandwich icon
    sandwich_png(work / 'sandwich.png')
    run(GFX, work / 'sandwich.png', work / 'sandwich.NCGR', '-clobbersize', '-version101', '-bitdepth', '4')
    run(GFX, work / 'sandwich.png', work / 'sandwich.NCLR', '-ir', '-bitdepth', '4')
    gfx = ndspy.narc.NARC(rom.getFileByName('a/0/1/8'))
    old = (len(gfx.files[SANDWICH * 2 + 2]), len(gfx.files[SANDWICH * 2 + 3]))
    gfx.files[SANDWICH * 2 + 2] = (work / 'sandwich.NCGR').read_bytes()
    gfx.files[SANDWICH * 2 + 3] = (work / 'sandwich.NCLR').read_bytes()
    rom.setFileByName('a/0/1/8', gfx.save())
    # --- Novareon party icon
    icons = ndspy.narc.NARC(rom.getFileByName('a/0/2/0'))
    pr = icons.files[0]
    colors = struct.unpack_from('<48H', pr, 16 + 0x18)
    palettes = [[((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31) for c in colors[b * 16:b * 16 + 16]]
                for b in range(3)]
    candidate = art / 'support_assets/novareon_menu_icon_32x32_RGBA_candidate.png'
    bank, frames = icon_frames(candidate, palettes)
    payload = icon_payload(frames)
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    banks = bytearray(addons.files[9])
    for species in NOVAREON:
        f = bytes(icons.files[7 + species])
        assert len(f) == 16 + 0x20 + len(payload) and f[:4] == b'RGCN'
        icons.files[7 + species] = f[:16 + 0x20] + payload
        banks[species] = bank
    addons.files[9] = bytes(banks)
    rom.setFileByName('a/0/2/0', icons.save())
    rom.setFileByName('a/0/2/8', addons.save())
    return dict(stellar_chip_file=new_file, sandwich_sizes_before=old, novareon_icon_palette=bank)


if __name__ == '__main__':
    src, dst, art, work = sys.argv[1:5]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom, art, work))
    rom.saveToFile(dst)
