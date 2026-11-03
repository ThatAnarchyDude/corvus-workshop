"""Give the ROM a custom 32x32 banner icon (the picture launchers and the 3DS HOME forwarder show). Owner request 2026-10-28 (it showed a generic Pokeball).

The icon is 32x32, 4 bits per pixel in 8x8 tiles, with a 16-colour RGB555 palette (index 0 is transparent). The picture is cropped to its visible part, fitted into 32x32 and reduced to 15 colours.
Usage: banner_icon.py <in.nds> <out.nds> <picture.png> [preview.png]
"""
import struct
import sys
import ndspy.rom
from ndspy import _common
from PIL import Image


def icon_data(picture):
    im = Image.open(picture).convert('RGBA')
    im = im.crop(im.getchannel('A').point(lambda a: 255 if a > 40 else 0).getbbox())
    scale = min(32 / im.width, 32 / im.height)
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    canvas = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    canvas.paste(im, ((32 - im.width) // 2, (32 - im.height) // 2))
    solid = Image.new('RGB', (32, 32), (0, 0, 0))
    solid.paste(canvas.convert('RGB'), mask=canvas.getchannel('A').point(lambda a: 255 if a > 100 else 0))
    pal = solid.quantize(colors=15, method=Image.MEDIANCUT, dither=Image.NONE)
    colors = pal.getpalette()[:45]
    palette = [(0, 0, 0)] + [tuple(colors[i:i + 3]) for i in range(0, 45, 3)]
    alpha = canvas.getchannel('A')
    pixels = [[0 if alpha.getpixel((x, y)) <= 100 else pal.getpixel((x, y)) + 1 for x in range(32)] for y in range(32)]
    return palette, pixels


def patch(rom, picture):
    palette, pixels = icon_data(picture)
    banner = bytearray(rom.iconBanner)
    tiles = bytearray()
    for ty in range(4):
        for tx in range(4):
            for y in range(8):
                for x in range(0, 8, 2):
                    tiles.append(pixels[ty * 8 + y][tx * 8 + x] | (pixels[ty * 8 + y][tx * 8 + x + 1] << 4))
    banner[0x20:0x220] = tiles
    for i, (r, g, b) in enumerate(palette):
        struct.pack_into('<H', banner, 0x220 + 2 * i, (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10))
    struct.pack_into('<H', banner, 2, _common.crc16(banner[0x20:0x840]))
    rom.iconBanner = bytes(banner)
    return palette, pixels


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    palette, pixels = patch(rom, sys.argv[3])
    rom.saveToFile(sys.argv[2])
    if len(sys.argv) > 4:
        pv = Image.new('RGBA', (32, 32))
        for y in range(32):
            for x in range(32):
                i = pixels[y][x]
                pv.putpixel((x, y), (0, 0, 0, 0) if i == 0 else palette[i] + (255,))
        bg = Image.new('RGBA', (32, 32), (230, 230, 230, 255)); bg.alpha_composite(pv)
        bg.resize((256, 256), Image.NEAREST).save(sys.argv[4])
