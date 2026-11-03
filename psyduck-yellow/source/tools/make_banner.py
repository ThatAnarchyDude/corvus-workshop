"""TEST/ART: (env BANNER="top_y,bottom_y,curve,stone_radius,font1,font2" tries variations) draws the 256x128 forwarder banner (art/psyduck-banner.png): "Psyduck Yellow" in Pokemon-logo style, "BETA v0.1.10" in red with a black outline, on a textured golden background."""
import os
import random
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
S = 4
W, H = 256 * S, 128 * S
random.seed(7)


def background():
    bg = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(232 - 70 * t), int(178 - 80 * t), int(52 - 36 * t)))
    # brushed / woven texture: fine diagonal lines plus grain
    tex = Image.new('L', (W, H), 128)
    td = ImageDraw.Draw(tex)
    for k in range(-H, W, 6 * S // 2):
        td.line([(k, 0), (k + H, H)], fill=150, width=max(1, S // 2))
    for k in range(0, W + H, 11 * S // 2):
        td.line([(k, 0), (k - H, H)], fill=108, width=max(1, S // 2))
    noise = Image.effect_noise((W, H), 38)
    tex = ImageChops.blend(tex, noise, 0.45).filter(ImageFilter.GaussianBlur(S / 3))
    bg = ImageChops.overlay(bg, Image.merge('RGB', (tex, tex, tex)))
    # soft light in the middle, darker edges
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.08, H * 0.05, W * 0.92, H * 0.95], fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(40 * S / 4))
    bg.paste(Image.new('RGB', (W, H), (255, 236, 150)), mask=glow.point(lambda a: int(a * 0.55)))
    edge = ImageChops.invert(glow).point(lambda a: int(a * 0.4))
    bg.paste(Image.new('RGB', (W, H), (96, 52, 8)), mask=edge)
    return bg


def stripe(size, stops):
    g = Image.new('RGB', size)
    gd = ImageDraw.Draw(g)
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0)
                gd.line([(0, y), (size[0], y)], fill=tuple(int(a + (b - a) * u) for a, b in zip(c0, c1)))
                break
    return g


def sparkles(bg, cx, cy, r):
    """Four white sparkles around the stone (drawn last, in front of the lettering)."""
    sp = ImageDraw.Draw(bg)
    for dx, dy, size in ((1.45, -0.95, 0.5), (-1.55, 0.75, 0.38), (1.65, 0.7, 0.28), (-1.3, -1.0, 0.26),
                           (0.12, 1.22, 0.5),      # under the stone
                           (0.48, -0.5, 0.55),     # over the stone
                           (-0.95, 0.05, 0.17), (1.05, 0.1, 0.15), (-0.55, -1.2, 0.17), (0.7, 1.0, 0.15), (-0.35, 1.12, 0.14)):
        x0, y0, q = cx + dx * r, cy + dy * r, size * r
        sp.polygon([(x0, y0 - q), (x0 + q * 0.18, y0 - q * 0.18), (x0 + q, y0), (x0 + q * 0.18, y0 + q * 0.18),
                    (x0, y0 + q), (x0 - q * 0.18, y0 + q * 0.18), (x0 - q, y0), (x0 - q * 0.18, y0 - q * 0.18)], fill=(255, 252, 235), outline=(120, 70, 10))


def bend(img, lift):
    """Shift each pixel column vertically so a line of lettering arcs: lift > 0 raises the middle (an arch), lift < 0 lowers it (a bowl)."""
    out = Image.new(img.mode, img.size)
    for x in range(W):
        u = (x - W / 2) / (W / 2)
        out.paste(img.crop((x, 0, x + 1, H)), (x, -int(round(lift * (1 - u * u)))))
    return out


def stretch(img, cy, k):
    """Make the picture k times taller around the row cy (same width)."""
    if k == 1:
        return img
    h = int(H / k)
    band = img.crop((0, int(cy - h / 2), W, int(cy + h / 2))).resize((W, H), Image.BICUBIC)
    out = Image.new(img.mode, img.size)
    out.paste(band, (0, int(cy - H / 2)))             # the row cy stays where it was
    return out


def logo(bg, text, cy, size, stops, outline, shadow, stroke, edge=0, inner=0, lift=0, tall=1):
    d = ImageDraw.Draw(bg)
    while True:
        f = ImageFont.truetype(F, size)
        if d.textbbox((0, 0), text, font=f, stroke_width=stroke)[2] <= W - 22 * S or size < 10:
            break
        size -= 2
    bb = d.textbbox((0, 0), text, font=f)
    x, y = (W - (bb[2] - bb[0])) // 2 - bb[0], cy - (bb[3] - bb[1]) // 2 - bb[1]
    top, bot = y + bb[1], y + bb[3]
    fill = Image.new('L', (W, H), 0)
    ImageDraw.Draw(fill).text((x, y), text, font=f, fill=255)
    B = lambda m: bend(stretch(m, cy, tall), lift) if lift else stretch(m, cy, tall)
    fill = B(fill)
    big = Image.new('L', (W, H), 0)
    ImageDraw.Draw(big).text((x, y), text, font=f, fill=255, stroke_width=stroke)
    big = B(big)
    sh = ImageChops.offset(big, 3 * S // 2, 3 * S // 2).filter(ImageFilter.GaussianBlur(S))
    bg.paste(Image.new('RGB', (W, H), shadow), mask=sh.point(lambda a: int(a * 0.7)))
    if edge:                                    # thin black line around the outside of the outline
        rim = Image.new('L', (W, H), 0)
        ImageDraw.Draw(rim).text((x, y), text, font=f, fill=255, stroke_width=stroke + edge)
        rim = B(rim)
        bg.paste(Image.new('RGB', (W, H), (0, 0, 0)), mask=rim)
    bg.paste(Image.new('RGB', (W, H), outline), mask=big)
    if inner:                                   # thin black line between the lettering and its outline
        ring = Image.new('L', (W, H), 0)
        ImageDraw.Draw(ring).text((x, y), text, font=f, fill=255, stroke_width=inner)
        ring = B(ring)
        bg.paste(Image.new('RGB', (W, H), (0, 0, 0)), mask=ring)
    grad = Image.new('RGB', (W, H), stops[-1][1])
    grad.paste(stripe((W, max(1, bot - top)), stops), (0, top))
    grad = B(grad)
    bg.paste(grad, mask=fill)
    hl = Image.new('L', (W, H), 0)
    ImageDraw.Draw(hl).rectangle([0, top, W, top + (bot - top) // 5], fill=120)
    hl = B(hl)
    bg.paste(Image.new('RGB', (W, H), (255, 255, 255)), mask=ImageChops.multiply(fill, hl))


def psyduckite(bg, cx, cy, r):
    """A glossy pink Mega Stone: glass sphere with a blue double-helix (the Mega symbol), rim light, reflections, a glow and sparkles."""
    import math
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse([cx - r * 1.55, cy - r * 1.55, cx + r * 1.55, cy + r * 1.55], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(r * 0.5))
    bg.paste(Image.new('RGB', (W, H), (255, 236, 200)), mask=glow.point(lambda a: int(a * 0.55)))
    ring = Image.new('L', (W, H), 0)
    ImageDraw.Draw(ring).ellipse([cx - r - S, cy - r - S, cx + r + S, cy + r + S], fill=255)
    sh = ImageChops.offset(ring, 2 * S, 3 * S).filter(ImageFilter.GaussianBlur(S * 1.5))
    bg.paste(Image.new('RGB', (W, H), (60, 30, 10)), mask=sh.point(lambda a: int(a * 0.65)))
    bg.paste(Image.new('RGB', (W, H), (24, 6, 18)), mask=ring)
    ball = Image.new('RGB', (W, H))
    bd = ImageDraw.Draw(ball)
    for i in range(r, 0, -1):                        # shading: light from the upper left, darker pink at the lower right
        t = i / r
        ox, oy = int(-0.3 * (r - i)), int(-0.34 * (r - i))
        col = tuple(int(a + (b - a) * (t ** 1.4)) for a, b in zip((255, 226, 240), (176, 40, 108)))
        bd.ellipse([cx + ox - i, cy + oy - i, cx + ox + i, cy + oy + i], fill=col)
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    # inner rim glow (glass edge)
    inner = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(max(3, (r // 6) | 1)))).filter(ImageFilter.GaussianBlur(S))
    ball.paste(Image.new('RGB', (W, H), (255, 150, 200)), mask=inner.point(lambda a: int(a * 0.7)))
    # double helix: two sine strands crossing, rotated 35 degrees, with rungs
    helix = Image.new('L', (W, H), 0)
    hd = ImageDraw.Draw(helix)
    rot = math.radians(35)
    def pt(u, v):
        return (cx + u * math.cos(rot) - v * math.sin(rot), cy + u * math.sin(rot) + v * math.cos(rot))
    strand_a, strand_b = [], []
    for k in range(0, 201):
        u = (k / 200 - 0.5) * r * 1.5
        v = math.sin(k / 200 * math.pi * 2.0) * r * 0.36
        strand_a.append(pt(u, v)); strand_b.append(pt(u, -v))
    for k in range(10, 200, 20):                      # rungs where the strands cross apart
        hd.line([strand_a[k], strand_b[k]], fill=150, width=max(2, int(r * 0.06)))
    hd.line(strand_a, fill=255, width=int(r * 0.17), joint='curve')
    hd.line(strand_b, fill=255, width=int(r * 0.17), joint='curve')
    helix = helix.filter(ImageFilter.GaussianBlur(S * 0.5))
    edge = helix.filter(ImageFilter.MaxFilter(5))
    ball.paste(Image.new('RGB', (W, H), (20, 40, 140)), mask=ImageChops.multiply(edge, mask))
    ball.paste(Image.new('RGB', (W, H), (70, 130, 255)), mask=ImageChops.multiply(helix, mask))
    # more detail: gem facets, a fine inner ring, tube highlights on the helix strands, nodes at the crossings and some grain
    fac = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fac)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        fd.line([(cx + r * 0.28 * math.cos(a), cy + r * 0.28 * math.sin(a)), (cx + r * 0.98 * math.cos(a), cy + r * 0.98 * math.sin(a))], fill=(255, 255, 255, 46), width=max(1, S // 2))
    fd.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], outline=(255, 255, 255, 60), width=max(1, S // 2))
    fd.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28], outline=(150, 30, 90, 70), width=max(1, S // 2))
    ball.paste(fac.convert('RGB'), mask=ImageChops.multiply(fac.getchannel('A'), mask))
    tube = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    td2 = ImageDraw.Draw(tube)
    for strand in (strand_a, strand_b):
        td2.line([(x - r * 0.025, y - r * 0.05) for x, y in strand], fill=(190, 225, 255, 230), width=max(2, int(r * 0.05)), joint='curve')
    for k in (0, 100, 200):
        for strand in (strand_a,):
            x, y = strand[k]
            td2.ellipse([x - r * 0.1, y - r * 0.1, x + r * 0.1, y + r * 0.1], fill=(40, 70, 190, 255), outline=(15, 25, 110, 255))
            td2.ellipse([x - r * 0.05, y - r * 0.06, x + r * 0.01, y], fill=(220, 240, 255, 255))
    ball.paste(tube.convert('RGB'), mask=ImageChops.multiply(tube.getchannel('A'), mask))
    grain = Image.effect_noise((W, H), 22).point(lambda v: int(v * 0.35))
    ball = ImageChops.add(ball, Image.merge('RGB', (grain, grain, grain)).point(lambda v: max(0, v - 38)))
    # reflections
    hi = Image.new('L', (W, H), 0)
    ImageDraw.Draw(hi).ellipse([cx - r * 0.7, cy - r * 0.76, cx - r * 0.12, cy - r * 0.34], fill=240)
    ball.paste(Image.new('RGB', (W, H), (255, 255, 255)), mask=ImageChops.multiply(hi.filter(ImageFilter.GaussianBlur(S * 0.8)), mask))
    lo = Image.new('L', (W, H), 0)
    ImageDraw.Draw(lo).ellipse([cx + r * 0.25, cy + r * 0.42, cx + r * 0.72, cy + r * 0.78], fill=120)
    ball.paste(Image.new('RGB', (W, H), (255, 235, 250)), mask=ImageChops.multiply(lo.filter(ImageFilter.GaussianBlur(S * 1.2)), mask))
    # extra detail: bright rim arc, warm caustic at the lower right, tiny glints and a faint inner ring
    det = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(det)
    dd.arc([cx - r * 0.92, cy - r * 0.92, cx + r * 0.92, cy + r * 0.92], 200, 285, fill=(255, 255, 255, 190), width=max(2, int(r * 0.07)))
    dd.arc([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], 20, 70, fill=(255, 200, 230, 150), width=max(2, int(r * 0.05)))
    dd.ellipse([cx - r * 0.5, cy + r * 0.52, cx - r * 0.4, cy + r * 0.62], fill=(255, 255, 255, 200))
    dd.ellipse([cx + r * 0.52, cy - r * 0.38, cx + r * 0.6, cy - r * 0.3], fill=(255, 255, 255, 190))
    dd.ellipse([cx + r * 0.1, cy - r * 0.78, cx + r * 0.2, cy - r * 0.68], fill=(255, 255, 255, 170))
    det = det.filter(ImageFilter.GaussianBlur(S * 0.35))
    ball.paste(det.convert('RGB'), mask=ImageChops.multiply(det.getchannel('A'), mask))
    cal = Image.new('L', (W, H), 0)
    ImageDraw.Draw(cal).ellipse([cx + r * 0.05, cy + r * 0.1, cx + r * 0.85, cy + r * 0.85], fill=90)
    ball.paste(Image.new('RGB', (W, H), (255, 120, 170)), mask=ImageChops.multiply(cal.filter(ImageFilter.GaussianBlur(r * 0.25)), mask))
    bg.paste(ball, mask=mask)



bg = background()
TOP, BOTTOM, LIFT, STONE, FONT1, FONT2, TALL = (float(v) for v in os.environ.get('BANNER', '41.5,91,14,24,44,34,1.42').split(','))
psyduckite(bg, W // 2, 65 * S, int(STONE * S))                  # drawn first: the lettering overlaps its top and bottom edges
logo(bg, 'Psyduck Yellow', int(TOP * S), int(FONT1 * S), [(0, (255, 244, 120)), (0.55, (255, 214, 30)), (1, (240, 168, 0))], (34, 70, 160), (14, 28, 90), int(3.6 * S), edge=S, inner=S, lift=int(LIFT * S), tall=TALL)
logo(bg, 'BETA v0.1.10', int(BOTTOM * S), int(FONT2 * S), [(0, (255, 110, 90)), (0.5, (226, 24, 24)), (1, (150, 0, 0))], (0, 0, 0), (0, 0, 0), 3 * S, lift=-int(LIFT * S), tall=TALL)
if not os.environ.get('NOSPARKLES'):
    sparkles(bg, W // 2, 65 * S, int(STONE * S))
out = bg.resize((256, 128), Image.LANCZOS)
out.save(sys.argv[1] if len(sys.argv) > 1 else 'art/psyduck-banner.png')
