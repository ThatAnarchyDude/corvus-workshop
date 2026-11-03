"""Party / box / summary icons for the nine new Eeveelutions (owner order 2026-11-02, after the battle sprites), derived from the same pictures.
Each icon is the front sprite (tools/eeveelution_art.py output) shrunk to 32x32 and fitted to the closest of the three shared 16-colour icon banks (a/0/2/0 file 0); the species' bank goes in
a/0/2/8 file 9, the second frame is the first one pixel down (the same bounce new_images uses). Rows changed: ordinary (1536+i), starter (1545+i), Pokedex identity (501+i) and the Mega rows of the
starter species (they copied the starter's placeholder icon). The three banks have no pure blues/purples, so Venomeon/Wraitheon/Zephyreon icons drift towards the nearest colours.
Usage (from yellow-heartgold, PYTHONPATH=tools): eeveelution_icons.py <in.nds> <out.nds> <art dir> <work dir>"""
import struct
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image
from new_images import icon_payload
from new_eeveelutions import NAMES, ordinary, starter
from dex_new_eeveelutions import dex_id
import megas_part1 as p1
import megas_part2 as p2


BOOST = {'Venomeon': (2.0, 1.6), 'Wraitheon': (1.6, 1.25), 'Wyrmeon': (1.3, 1.05), 'Ferreon': (1.0, 1.25)}   # (colour, brightness) enhancement before fitting; default (1.35, 1.3)
BANK = {'Brawleon': 0, 'Chryseon': 1, 'Wyrmeon': 0}                  # the others fit bank 2 (blues, purples, tans, grays) best; chosen by colour, not by raw error (the paintings are dark)


def fit(path, colours):
    src = Image.open(path).convert('RGBA')
    grid = []
    for y in range(32):
        row = []
        for x in range(32):
            r, g, b, a = src.getpixel((x, y))
            if a < 128:
                row.append(0)
                continue
            row.append(min((i for i in range(1, 16)), key=lambda i: (r - colours[i][0]) ** 2 + (g - colours[i][1]) ** 2 + (b - colours[i][2]) ** 2))
        grid.append(row)
    return grid


def candidate(art, name, work):
    sheet = Image.open(Path(art) / f'{name}_front.png')
    frame = sheet.crop((0, 0, 80, 80)).convert('RGBA')
    px = frame.load()
    for y in range(80):
        for x in range(80):
            if sheet.getpixel((x, y)) == 0:
                px[x, y] = (0, 0, 0, 0)
    box = frame.getchannel('A').getbbox()
    sprite = frame.crop(box)
    scale = 30 / max(sprite.size)
    small = sprite.resize((max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))), Image.BOX)
    from PIL import ImageEnhance
    colour, bright = BOOST.get(name, (1.35, 1.3))
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(small.convert('RGB')).enhance(colour)).enhance(bright)
    small = Image.merge('RGBA', (*rgb.split(), small.getchannel('A')))
    out = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    out.paste(small, ((32 - small.width) // 2, 31 - small.height), small)
    path = Path(work) / f'{name}_icon.png'
    out.save(path)
    return path


def patch(rom, art, work):
    Path(work).mkdir(parents=True, exist_ok=True)
    icons = ndspy.narc.NARC(rom.getFileByName('a/0/2/0'))
    raw = struct.unpack_from('<48H', icons.files[0], 16 + 0x18)
    palettes = [[((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31) for c in raw[b * 16:(b + 1) * 16]] for b in range(3)]
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    banks = bytearray(addons.files[9])
    mega_row = {}
    for rows, names in ((p1.MEGA_ROWS, p1.MEGA_FOR), (tuple(p2.FIRST + k for k in range(p2.NEW)), p2.MEGA_FOR)):
        for m, n in zip(rows, names):
            mega_row[n] = m
    report = {}
    for i, name in enumerate(NAMES):
        bank = BANK.get(name, 2)
        grid = fit(candidate(art, name, work), palettes[bank])
        frames = [grid, [[0] * 32] + [row[:] for row in grid[:-1]]]
        payload = icon_payload(frames)
        targets = [ordinary(i), starter(i), dex_id(i)] + ([mega_row[name]] if name in mega_row else [])
        for sp in targets:
            f = bytes(icons.files[7 + sp])
            assert f[:4] == b'RGCN' and len(f) == 16 + 0x20 + len(payload), (name, sp, len(f))
            icons.files[7 + sp] = f[:16 + 0x20] + payload
            banks[sp] = bank
        report[name] = bank
    addons.files[9] = bytes(banks)
    rom.setFileByName('a/0/2/0', icons.save())
    rom.setFileByName('a/0/2/8', addons.save())
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3], sys.argv[4]))
    rom.saveToFile(sys.argv[2])
