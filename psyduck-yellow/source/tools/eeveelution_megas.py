"""Give each Eeveelution's Mega its own colours (owner: "they will evolve into their OWN Megas").

The eight starter-line Eeveelution Megas (species 1566, 1568, ..., 1580) all drew Mega Eevee's sprite with Mega Eevee's brown palette. The sprite shapes stay (no other
art exists); each Mega gets its own palette in a/0/0/4 (file 4 normal, file 5 shiny) made by recolouring Mega Eevee's: hue, saturation and brightness per colour from
a per-type recipe below. Mega Novareon keeps its own art. Shiny palettes are made from the same normal palette with a different hue (a type-appropriate alternative).

Usage: eeveelution_megas.py <in.nds> <out.nds>
"""
import colorsys
import struct
import sys
import ndspy.narc
import ndspy.rom
from starter_eevee_line import BASES, FIRST

MEGA_EEVEE = 1562
# base species -> (name, normal recipe, shiny recipe); recipe = (target hue degrees or None to keep, saturation factor, value factor, lightness lift 0..1 toward white)
RECIPES = {
    134: ('Vaporeon', (205, 0.95, 1.00, 0.00), (165, 0.90, 1.00, 0.00)),
    135: ('Jolteon', (52, 1.00, 1.05, 0.00), (35, 0.90, 1.00, 0.00)),
    136: ('Flareon', (8, 1.15, 1.00, 0.00), (45, 0.90, 1.05, 0.00)),
    196: ('Espeon', (305, 0.70, 1.02, 0.08), (200, 0.70, 1.02, 0.05)),
    197: ('Umbreon', (45, 0.35, 0.52, 0.00), (200, 0.55, 0.60, 0.00)),
    470: ('Leafeon', (105, 0.80, 0.98, 0.00), (35, 0.75, 1.00, 0.00)),
    471: ('Glaceon', (190, 0.45, 1.05, 0.18), (280, 0.45, 1.05, 0.15)),
    750: ('Sylveon', (335, 0.55, 1.05, 0.16), (190, 0.55, 1.05, 0.12)),
}


def recolour(rgb, recipe):
    hue, sat, val, lift = recipe
    r, g, b = (c / 255 for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if hue is not None and s > 0.05:
        h = hue / 360
    s = min(1.0, s * sat)
    v = min(1.0, v * val)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r, g, b = (c + (1 - c) * lift * v for c in (r, g, b))
    return tuple(min(255, int(round(c * 255))) for c in (r, g, b))


def palette_with(raw, recipe):
    out = bytearray(raw)
    at = bytes(raw).find(b'TTLP') + 0x18
    for i in range(1, 16):                                    # index 0 is transparent
        c = struct.unpack_from('<H', raw, at + 2 * i)[0]
        rgb = ((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31)
        r, g, b = recolour(rgb, recipe)
        struct.pack_into('<H', out, at + 2 * i, (r * 31 // 255) | ((g * 31 // 255) << 5) | ((b * 31 // 255) << 10))
    return bytes(out)


def patch(rom):
    gfx = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    normal = bytes(gfx.files[MEGA_EEVEE * 6 + 4])
    done = []
    for i, base in enumerate(BASES):
        if base not in RECIPES or i == len(BASES) - 1:           # the last entry is Novareon (Umbreon's stand-in): it keeps its own art
            continue
        species = FIRST + 2 * i + 1
        name, norm, shin = RECIPES[base]
        gfx.files[species * 6 + 4] = palette_with(normal, norm)
        gfx.files[species * 6 + 5] = palette_with(normal, shin)
        done.append((species, name))
    rom.setFileByName('a/0/0/4', gfx.save())
    return dict(recoloured=done)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
