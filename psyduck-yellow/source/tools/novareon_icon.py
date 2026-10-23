"""Novareon / Mega Novareon party-menu icon in blue (owner request 2026-10-23: the gray icon "is not right").

The party/summary/box icons draw from three shared 16-colour banks (a/0/2/0 file 0); a species picks one in a/0/2/8 file 9. The supplied Novareon icon
was fitted to the nearest bank by RGB, which picked gray (bank 1). Bank 2 is the only one with blues, so the icon is recoloured to it by a fixed map
from Novareon's own body palette to bank 2's colours: dark navy -> dark grays, body -> its blue, highlights -> its light blue, cream and tan stay
cream and tan. The Mega keeps the same icon (the rainbow tail needs more colours than a bank has).

Usage: novareon_icon.py <in.nds> <out.nds> <010_Novareon folder>
"""
import struct
import sys
from pathlib import Path
from PIL import Image
import ndspy.narc
import ndspy.rom
from new_images import icon_payload
from starter_eevee_line import NOVAREON, mega, starter

BANK = 2
BASE = [(17, 28, 41), (28, 49, 69), (44, 71, 98), (65, 93, 123), (92, 119, 141), (132, 153, 166), (179, 189, 196), (230, 212, 184),
        (250, 236, 207), (211, 175, 138), (134, 98, 68), (232, 143, 58), (255, 187, 73), (255, 247, 225), (255, 255, 255)]
MAP = [15, 14, 14, 4, 5, 5, 2, 7, 3, 6, 6, 10, 9, 3, 3]          # Novareon palette index 1..15 -> bank-2 index


def patch(rom, art):
    icons = ndspy.narc.NARC(rom.getFileByName('a/0/2/0'))
    colours = struct.unpack_from('<48H', icons.files[0], 16 + 0x18)
    assert colours[33] == 15 | (15 << 5) | (15 << 10), 'bank 2 is not the expected one'
    src = Image.open(Path(art) / 'support_assets/novareon_menu_icon_32x32_RGBA_candidate.png').convert('RGBA')
    grid = []
    for y in range(32):
        row = []
        for x in range(32):
            r, g, b, a = src.getpixel((x, y))
            if a < 128:
                row.append(0)
                continue
            k = min(range(15), key=lambda k: (r - BASE[k][0]) ** 2 + (g - BASE[k][1]) ** 2 + (b - BASE[k][2]) ** 2)
            row.append(MAP[k])
        grid.append(row)
    second = [[0] * 32] + [row[:] for row in grid[:-1]]
    payload = icon_payload([grid, second])
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    banks = bytearray(addons.files[9])
    for species in (starter(NOVAREON), mega(NOVAREON)):          # 1581, 1582
        f = bytes(icons.files[7 + species])
        assert len(f) == 16 + 0x20 + len(payload) and f[:4] == b'RGCN'
        icons.files[7 + species] = f[:16 + 0x20] + payload
        banks[species] = BANK
    addons.files[9] = bytes(banks)
    rom.setFileByName('a/0/2/0', icons.save())
    rom.setFileByName('a/0/2/8', addons.save())
    return dict(bank=BANK)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
