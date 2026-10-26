"""TEST/DESIGN TOOL: contact sheet of an area's 4/16-colour textures. Usage: texsheet.py <rom> <area> <out.png> [name prefixes...]"""
import struct, sys
import ndspy.rom, ndspy.narc, ndspy.texture
from PIL import Image, ImageDraw
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); a = int(sys.argv[2]); keep = sys.argv[4:]
areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2')).files; banks = ndspy.narc.NARC(rom.getFileByName('a/0/4/4')).files
tx = ndspy.texture.NSBTX(banks[struct.unpack_from('<H', areas[a], 2)[0]])
pals = dict(tx.palettes); items = []
for n, t in tx.textures:
    if int(t.format) not in (2, 3) or (keep and not any(n.startswith(p) for p in keep)):
        continue
    cand = [p for p in pals if p == n + '_pl' or p == n or p.startswith(n)] or list(pals)[:1]
    col = [(c.r, c.g, c.b) for c in pals[cand[0]].colors]
    w, h, data = t.width, t.height, bytes(t.data1)
    im = Image.new('RGB', (w, h))
    px = []
    for b in data:
        if int(t.format) == 3: px += [b & 15, b >> 4]
        else: px += [b & 3, (b >> 2) & 3, (b >> 4) & 3, b >> 6]
    im.putdata([col[i] if i < len(col) else (255, 0, 255) for i in px[:w * h]])
    items.append((n, im))
cols = 8; W = max(i.width for _, i in items); H = max(i.height for _, i in items) + 12; rows = (len(items) + cols - 1) // cols
S = Image.new('RGB', (cols * (W + 4), rows * (H + 4)), (40, 40, 40)); dr = ImageDraw.Draw(S)
for k, (n, im) in enumerate(items):
    x, y = (k % cols) * (W + 4), (k // cols) * (H + 4); S.paste(im, (x, y + 12)); dr.text((x, y), n[:14], fill=(255, 255, 0))
S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(sys.argv[3]); print(len(items), 'textures')
