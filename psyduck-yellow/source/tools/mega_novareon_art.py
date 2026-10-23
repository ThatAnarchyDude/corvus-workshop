"""Mega Novareon battle sprites, built from the Novareon pixel sprites and the owner's concept picture (2026-10-23).

The concept shows the same Novareon with one big disk-shaped tail of seven rainbow wedges (red, white, green, blue, purple, yellow, orange)
between dark wedges and a golden rim. The disk looks the same from behind, so both views get it. The body pixels are kept; the old tail is
replaced by a disk drawn behind the body. The sprite palette is 16 colours: Novareon's 11 body colours are merged to 9 (indices 1-9) so six rainbow colours fit in 10-15
(index 12, yellow, is also the rim colour).

Usage: mega_novareon_art.py <010_Novareon folder> <out dir>      -> mega_front.png / mega_back.png (80x80, P) and the two-frame 160x80 sheets
"""
import math
import sys
from pathlib import Path
from PIL import Image

BODY_MAP = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 8, 11: 9, 14: 7, 15: 7}
RAINBOW = {'red': (10, (226, 40, 52)), 'orange': (11, (255, 140, 28)), 'yellow': (12, (255, 208, 70)),
           'green': (13, (52, 200, 62)), 'blue': (14, (46, 84, 232)), 'purple': (15, (136, 44, 204))}
BODY_PALETTE = [(0, 0, 0), (17, 28, 41), (28, 49, 69), (44, 71, 98), (65, 93, 123), (92, 119, 141), (230, 212, 184), (250, 236, 207), (211, 175, 138), (134, 98, 68)]
WHITE = 7
# the concept's wedges: (colour, bearing of the wedge's axis clockwise from up, half-width in degrees at the rim); dark fur lies between them
WEDGES = (('white', -8, 15), ('green', 48, 16), ('blue', 90, 17), ('purple', 150, 11), ('yellow', 208, 17), ('orange', 255, 16), ('red', 302, 16))
# view -> (disk centre, radius, mirrored, the old tail's ellipse (cx, cy, rx, ry)); the disk is drawn behind the body, which overlaps it
VIEWS = {'front': ((57.0, 44.0), 20.0, True, (64, 53, 15, 17)),
         'back': ((32.0, 47.0), 20.5, False, (23, 50, 21, 17))}   # (..., mirrored): the front view sees the disk's far face, so its colours run the other way


def palette():
    flat = []
    for rgb in BODY_PALETTE:
        flat += rgb
    for name in ('red', 'orange', 'yellow', 'green', 'blue', 'purple'):
        flat += RAINBOW[name][1]
    return flat + [0] * (768 - len(flat))


def build(src, view):
    base = Image.open(src).convert('P')
    px = base.load()
    cx, cy, rx, ry = VIEWS[view][3]
    disk, radius, mirrored = VIEWS[view][0], VIEWS[view][1], VIEWS[view][2]
    out = Image.new('P', (80, 80), 0)
    out.putpalette(palette())
    o = out.load()
    def inside(x, y, shift=0):
        dx, dz = x + 0.5 - disk[0] - shift, y + 0.5 - disk[1] - shift * 2
        ang = math.atan2(dz, dx)
        return math.hypot(dx, dz) <= radius + 0.9 * math.sin(ang * 9) + 0.5 * math.sin(ang * 17 + 1)
    for y in range(80):
        for x in range(80):
            if not inside(x, y) and inside(x, y, -1):        # the disk's thickness: its lower right edge, one step back
                o[x, y] = 1 if not inside(x, y, -2) else 2
            if not inside(x, y):
                continue
            dx, dz = x + 0.5 - disk[0], y + 0.5 - disk[1]
            d = math.hypot(dx, dz)
            bearing = (math.degrees(math.atan2(dx, -dz))) % 360                 # clockwise from straight up
            if mirrored:
                bearing = (-bearing) % 360
            light = (-dx * 0.55 - dz * 0.85) / radius                         # +1 at the upper left, -1 at the lower right
            streak = 0.30 * math.sin(math.radians(bearing) * 7 + d * 0.15) + 0.2 * math.sin(math.radians(bearing) * 19)
            colour = None
            for name, centre, half in WEDGES:
                if abs((bearing - centre + 180) % 360 - 180) < half * (0.45 + 0.55 * min(1.0, d / radius)) and d > 2.5:
                    colour = name
            rim = not inside(x - 1, y - 1) or not inside(x, y - 1) or not inside(x - 1, y)       # upper left rim: the gold glow
            if rim:
                o[x, y] = RAINBOW['yellow'][0]
            elif not inside(x + 1, y + 1) or not inside(x + 1, y):                                  # lower right rim: shaded
                o[x, y] = 8                                           # tan: the rim's shaded gold
            elif colour is not None:
                shade = (x + y) % 2 == 0 and light < -0.45
                o[x, y] = 3 if shade else (WHITE if colour == 'white' else RAINBOW[colour][0])
            else:
                v = light + streak
                o[x, y] = 5 if v > 0.60 else 4 if v > 0.15 else 3 if v > -0.40 else 2 if v > -0.85 else 1
    for y in range(80):                                   # the body goes on top, minus the old tail
        for x in range(80):
            v = px[x, y]
            if v and not (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and not body_over(view, x, y)):
                o[x, y] = BODY_MAP[v]
    return out


def body_over(view, x, y):
    """Pixels inside the old tail's ellipse that belong to the body (legs and haunch) and stay."""
    if view == 'front':
        return y >= 62 and x <= 57 or x <= 51
    return x >= 36 and y >= 56 or x >= 41


def main(art, out):
    art, out = Path(art), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for view in ('front', 'back'):
        im = build(art / 'battle_sprites/base_form' / f'novareon_{view}_80x80_indexed.png', view)
        im.info['transparency'] = 0
        im.save(out / f'mega_{view}.png', transparency=0)
        sheet = Image.new('P', (160, 80), 0)
        sheet.putpalette(im.getpalette())
        sheet.paste(im, (0, 0))
        sheet.paste(im, (80, 0))
        sheet.save(out / f'mega_{view}_160x80_two_frame.png', transparency=0)
        big = im.convert('RGBA').resize((480, 480), Image.NEAREST)
        bg = Image.new('RGBA', big.size, (200, 200, 200, 255))
        bg.alpha_composite(big)
        bg.save(out / f'preview_{view}.png')


if __name__ == '__main__':
    main(*sys.argv[1:3])
