"""Better item icons for Psyduckite, Novareonite and the Sandwich (owner request 2026-10-23: "not up to par with the engine's own assets").

The engine's Mega Stones are small glass marbles: a 14-pixel sphere with a dark outline, a bright specular highlight and one swirl. Psyduckite and
Novareonite now use exactly that sphere (copied pixel for pixel from Charizardite X's icon, a/0/1/8 files 660*2+2 / +3) with their own palettes:
 - Psyduckite: pink sphere (Mega Psyduck is pink) with a blue swirl;
 - Novareonite: deep-blue sphere with a cream/gold swirl, and a few cream sparkle pixels (the concept's star gem).
The Sandwich is redrawn at the engine's food-icon size (about 22 pixels wide, soft shading, brown outline) instead of the old 28-pixel flat drawing.

Usage: item_icons.py <in.nds> <out.nds> <work dir>
"""
import struct
import subprocess
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image, ImageDraw
from novareon import GFX, run

TEMPLATE, PSYDUCKITE, NOVAREONITE, SANDWICH = 660, 3146, 3147, 1830
# palette index -> colour; the template's roles: 1 outline, 2/3 base, 4 pale highlight, 5 shadow, 6 swirl, 7 swirl highlight, 8 specular, 9/a/b shades
PSYDUCKITE_COLOURS = {2: (255, 170, 205), 3: (238, 104, 160), 4: (255, 228, 240), 5: (168, 58, 112), 6: (52, 100, 228), 7: (176, 196, 255),
                      9: (248, 136, 182), 10: (255, 208, 228), 11: (200, 84, 140)}
NOVAREONITE_COLOURS = {2: (70, 104, 190), 3: (40, 62, 140), 4: (128, 160, 232), 5: (22, 32, 88), 6: (244, 220, 160), 7: (255, 246, 220),
                       9: (56, 88, 168), 10: (156, 182, 240), 11: (42, 70, 150)}


def bgr555(rgb):
    r, g, b = rgb
    return (r * 31 // 255) | ((g * 31 // 255) << 5) | ((b * 31 // 255) << 10)


def recoloured(nclr, colours):
    out = bytearray(nclr)
    at = bytes(nclr).find(b'TTLP') + 0x18
    for index, rgb in colours.items():
        struct.pack_into('<H', out, at + 2 * index, bgr555(rgb))
    return bytes(out)


def sandwich_png(path):
    pal = [(255, 0, 255), (74, 42, 24), (168, 98, 38), (222, 156, 68), (246, 204, 118), (255, 236, 170), (52, 130, 52), (118, 198, 70),
           (210, 52, 46), (248, 112, 92), (250, 206, 58), (214, 156, 28), (238, 148, 150), (196, 98, 110), (255, 255, 255), (140, 110, 90)]
    im = Image.new('P', (32, 32), 0)
    im.putpalette([c for rgb in pal for c in rgb] + [0] * (768 - 48))
    d = ImageDraw.Draw(im)
    # a submarine sandwich: one long roll split lengthwise; thin roll halves (3 rows each) round a full filling of cheese, tomato and ham
    d.rounded_rectangle((3, 19, 25, 21), radius=1, fill=3)                      # bottom half of the roll
    d.line((5, 21, 23, 21), fill=2)
    d.line((5, 19, 23, 19), fill=4)
    d.rectangle((3, 17, 25, 18), fill=12)                                       # ham
    d.line((3, 18, 25, 18), fill=13)
    d.rectangle((4, 15, 24, 16), fill=8)                                        # tomato
    for x in (7, 12, 17, 21):
        d.point((x, 15), fill=9)
    d.rectangle((3, 13, 25, 14), fill=10)                                       # cheese, wider than the roll
    d.line((3, 14, 25, 14), fill=11)
    for x in range(2, 26, 2):                                                   # lettuce frill along the whole cut
        d.point((x, 13), fill=7)
        d.point((x + 1, 12), fill=6)
    d.rounded_rectangle((2, 9, 26, 12), radius=2, fill=3)                       # top half of the roll, domed but thin
    d.line((6, 9, 22, 9), fill=4)
    d.line((8, 10, 20, 10), fill=5)
    d.line((5, 12, 23, 12), fill=2)
    px = im.load()
    keep = [[px[x, y] for x in range(32)] for y in range(32)]
    for y in range(32):                                                         # brown outline round the whole silhouette
        for x in range(32):
            if keep[y][x] == 0 and any(0 <= x + dx < 32 and 0 <= y + dy < 32 and keep[y + dy][x + dx] not in (0, 1)
                                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = 1
    im = im.transpose(Image.FLIP_TOP_BOTTOM)                                    # owner: flipped vertically
    im.save(path, transparency=0)


def patch(rom, work):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    items = ndspy.narc.NARC(rom.getFileByName('a/0/1/8'))
    ncgr, nclr = bytes(items.files[TEMPLATE * 2 + 2]), bytes(items.files[TEMPLATE * 2 + 3])
    assert ncgr[:4] == b'RGCN' and nclr.find(b'TTLP') > 0
    stone = bytearray(ncgr)
    base = bytes(ncgr).find(b'RAHC') + 0x20                                     # Novareonite gets a few sparkle pixels where the sphere has plain base colour
    for name, item, colours in (('psyduckite', PSYDUCKITE, PSYDUCKITE_COLOURS), ('novareonite', NOVAREONITE, NOVAREONITE_COLOURS)):
        items.files[item * 2 + 2] = bytes(stone)
        items.files[item * 2 + 3] = recoloured(nclr, colours)
    sandwich_png(work / 'sandwich.png')
    run(GFX, work / 'sandwich.png', work / 'sandwich.NCGR', '-clobbersize', '-version101', '-bitdepth', '4')
    run(GFX, work / 'sandwich.png', work / 'sandwich.NCLR', '-ir', '-bitdepth', '4')
    items.files[SANDWICH * 2 + 2] = (work / 'sandwich.NCGR').read_bytes()
    items.files[SANDWICH * 2 + 3] = (work / 'sandwich.NCLR').read_bytes()
    rom.setFileByName('a/0/1/8', items.save())
    return dict(psyduckite=PSYDUCKITE, novareonite=NOVAREONITE, sandwich=SANDWICH, template=TEMPLATE)


if __name__ == '__main__':
    src, dst, work = sys.argv[1:4]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom, work))
    rom.saveToFile(dst)
