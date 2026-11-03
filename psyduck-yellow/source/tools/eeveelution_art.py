"""Battle sprites for the nine new Eeveelutions, derived from the owner's Eevee New Horizons boards (owner order 2026-11-02: battle sprites first, only for species without art).

Each creature is cut out of its painted panel (GrabCut inside a hand-set box), cropped, flipped to face left like the game's front sprites, shrunk to 80x80 with an outline and 15 colours
(index 0 transparent), and written as a 160x80 two-frame sheet (frame 2 is the same picture one pixel up, a small idle bounce) for the front and the back view. The boards only show side
views, so the back view is the same pose, a little larger and facing right (the way a trainer's own Pokemon face away from the camera).
The shiny palette is the normal palette with its hue turned (HUE_SHIFT per species).
Output (in the out dir): <name>_front.png, <name>_back.png (160x80, P mode), <name>_shiny.pal.json, preview.png (all nine). Nothing is written into a ROM here (see eeveelution_art_import.py).
Usage (from yellow-heartgold): .venv/bin/python tools/eeveelution_art.py <out dir>"""
import colorsys
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

BOARDS = Path('/mnt/c/Users/thata/Desktop/The Lab/Psyduck Yellow Releases/Psyduck-Yellow-ExMons/Eevee-Artwork-and-Editable-Files (2)/Eevee-New-Horizons/art')
# name: (board, creature box x0,y0,x1,y1 in board pixels, faces right?, shiny hue shift in degrees)
SPECIES = {
    'Brawleon': ('01-new-evolutions.png', (150, 75, 625, 470), True, 140),
    'Zephyreon': ('01-new-evolutions.png', (825, 78, 1405, 425), True, 150),
    'Venomeon': ('01-new-evolutions.png', (80, 535, 625, 935), True, 170),
    'Duneon': ('01-new-evolutions.png', (835, 535, 1345, 905), True, 120),
    'Strateon': ('02-new-evolutions.png', (85, 82, 395, 470), True, 180),
    'Chryseon': ('02-new-evolutions.png', (580, 78, 945, 505), True, 200),
    'Wraitheon': ('02-new-evolutions.png', (1060, 82, 1395, 510), True, 150),
    'Wyrmeon': ('02-new-evolutions.png', (65, 562, 785, 960), False, 160),
    'Ferreon': ('02-new-evolutions.png', (920, 562, 1405, 945), True, 40),
}
# hand-traced outlines (crop coordinates) for the creatures GrabCut alone cannot separate from their backgrounds
POLYGONS = {
    'Zephyreon': [(430, 60), (400, 18), (300, 6), (200, 10), (185, 40), (150, 60), (80, 65), (20, 85), (5, 125), (25, 175), (70, 205), (130, 225), (180, 245), (175, 272), (205, 292), (245, 282), (275, 272),
                  (300, 290), (335, 262), (385, 252), (430, 262), (480, 292), (520, 322), (557, 332), (562, 300), (548, 262), (520, 228), (500, 190), (522, 165), (532, 135), (520, 100), (470, 92)],
    'Chryseon': [(5, 170), (25, 130), (75, 118), (125, 122), (135, 160), (115, 175), (130, 200), (110, 230), (105, 260), (120, 285), (105, 320), (115, 355), (150, 355), (165, 335), (195, 345), (190, 300),
                 (215, 310), (225, 350), (235, 395), (280, 395), (275, 360), (300, 300), (330, 260), (355, 200), (355, 150), (335, 110), (300, 100), (280, 60), (260, 10), (235, 5), (225, 25), (200, 10),
                 (170, 15), (165, 60), (200, 110), (180, 150), (160, 190), (130, 205), (80, 225), (40, 245), (10, 230)],
    'Wraitheon': [(55, 10), (100, 25), (140, 40), (190, 80), (215, 40), (250, 20), (290, 40), (300, 90), (300, 140), (325, 170), (335, 230), (320, 300), (300, 350), (300, 395), (270, 420), (240, 415),
                  (235, 370), (210, 330), (185, 355), (150, 375), (125, 420), (100, 420), (95, 370), (70, 330), (40, 310), (10, 280), (0, 240), (15, 205), (50, 190), (80, 160), (100, 110), (60, 70), (30, 30)],
    'Wyrmeon': [(10, 20), (60, 40), (110, 10), (150, 25), (180, 50), (240, 35), (265, 60), (290, 100), (270, 130), (250, 150), (260, 170), (320, 175), (390, 200), (440, 230), (500, 270), (560, 265),
                (620, 255), (670, 265), (705, 310), (710, 360), (690, 390), (650, 392), (610, 350), (560, 310), (480, 300), (420, 330), (410, 350), (430, 370), (415, 395), (370, 390), (340, 345),
                (300, 335), (280, 365), (250, 395), (190, 395), (150, 370), (135, 340), (100, 320), (95, 295), (130, 260), (150, 210), (130, 170), (160, 135), (90, 105), (30, 75)],
}
# light creatures on a darker or more saturated background: a colour test inside the traced outline instead of GrabCut (channel, S or V, and the bound)
COLOUR_TEST = {}
POLYGON_ONLY = ('Zephyreon', 'Wraitheon')              # the traced outline IS the silhouette (the painting's light fur and its background cannot be told apart by colour)
TRIM_LEFT = {'Zephyreon': 100}                      # the trailing wing is cut here so the body is bigger in the frame
CLOSE_KERNEL = {}                    # smoke-like creature: dark notches between the mane and the body are filled
TRIM_RIGHT = {'Wyrmeon': 560}                       # the long tail is cut here (crop x) so the body can use the 80x80 frame
ENHANCE = ('Zephyreon', 'Wyrmeon')   # local contrast + sharpening before the shrink: pale or soft paintings lose their shading otherwise
FRONT_BOX, BACK_BOX = 74, 78            # largest side of the creature in the 80x80 frame


def cutout(img, box, iterations=8, polygon=None, test=None, name=''):
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1].copy()
    mask = np.zeros(crop.shape[:2], np.uint8)
    h, w = mask.shape
    if polygon is not None and name in POLYGON_ONLY:
        filled = np.zeros((h, w), np.uint8)
        cv2.fillPoly(filled, [np.array(polygon, np.int32)], 255)
        return crop, filled
    if polygon is not None and test is not None:
        poly = np.zeros((h, w), np.uint8)
        cv2.fillPoly(poly, [np.array(polygon, np.int32)], 255)
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV).astype(float) / 255
        chan = hsv[:, :, 1] if test[0] == 'S' else hsv[:, :, 2]
        ok = (chan < test[1]) if test[2] == 'below' else (chan > test[1])
        fg = np.where(ok & (cv2.dilate(poly, np.ones((9, 9), np.uint8)) > 0), 255, 0).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((CLOSE_KERNEL.get(name, 11),) * 2, np.uint8))
        n, labels, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
        if n > 1:
            fg = np.where(labels == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)
        cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(fg)
        cv2.drawContours(filled, cnts, -1, 255, -1)
        return crop, filled
    if polygon is not None:
        poly = np.zeros((h, w), np.uint8)
        cv2.fillPoly(poly, [np.array(polygon, np.int32)], 255)
        wide = cv2.dilate(poly, np.ones((25, 25), np.uint8))
        core = cv2.erode(poly, np.ones((15, 15), np.uint8))
        mask[:] = cv2.GC_BGD
        mask[wide > 0] = cv2.GC_PR_BGD
        mask[poly > 0] = cv2.GC_PR_FGD
        mask[core > 0] = cv2.GC_FGD
        bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
        cv2.grabCut(crop, mask, None, bgd, fgd, iterations, cv2.GC_INIT_WITH_MASK)
        fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        return crop, fg
    m = max(4, int(min(h, w) * 0.04))
    rect = (m, m, w - 2 * m, h - 2 * m)
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(crop, mask, rect, bgd, fgd, iterations, cv2.GC_INIT_WITH_RECT)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg = np.where(labels == keep, 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return crop, fg


def to_sprite(crop, mask, size_box, flip):
    ys, xs = np.where(mask > 0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgb = crop[y0:y1, x0:x1][:, :, ::-1]                    # BGR -> RGB
    a = mask[y0:y1, x0:x1]
    if flip:
        rgb, a = rgb[:, ::-1], a[:, ::-1]
    h, w = a.shape
    scale = size_box / max(h, w)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    rgb_s = np.array(Image.fromarray(np.ascontiguousarray(rgb)).resize((nw, nh), Image.LANCZOS))
    a_s = np.array(Image.fromarray(np.ascontiguousarray(a)).resize((nw, nh), Image.LANCZOS)) > 127
    canvas = np.zeros((80, 80, 3), np.uint8)
    alpha = np.zeros((80, 80), bool)
    ox, oy = (80 - nw) // 2, 80 - nh - 2                    # feet near the bottom, like the game's sprites
    oy = max(0, oy)
    canvas[oy:oy + nh, ox:ox + nw] = rgb_s
    alpha[oy:oy + nh, ox:ox + nw] = a_s
    return canvas, alpha


def indexed_pair(views):
    """views: [(canvas, alpha), ...]; one shared palette (the ROM keeps one palette for both views): 14 colours + outline + transparent (index 0)."""
    stack = np.concatenate([c for c, _ in views], axis=0)
    alpha_all = np.concatenate([a for _, a in views], axis=0)
    pil = Image.fromarray(stack)
    # quantise only the creature's pixels: transparent background pixels would otherwise take a palette entry
    flat = Image.fromarray(np.where(alpha_all[:, :, None], stack, stack[alpha_all].mean(axis=0).astype(np.uint8)))
    pal = flat.quantize(colors=14, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal_rgb = np.array(pal.getpalette()[:42], np.uint8).reshape(14, 3)
    idx_all = np.array(pal, np.uint8) + 1
    dark = np.clip(pal_rgb.min(axis=0).astype(int) // 2, 0, 255)
    palette = [(255, 0, 255)] + [tuple(int(v) for v in c) for c in pal_rgb] + [tuple(int(v) for v in dark)]
    outs = []
    for k, (_, alpha) in enumerate(views):
        idx = idx_all[k * 80:(k + 1) * 80]
        border = alpha & ~cv2.erode(alpha.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        out = np.zeros((80, 80), np.uint8)
        out[alpha] = idx[alpha]
        out[border] = 15
        outs.append(out)
    return outs, palette


def sheet(idx, palette, bounce=1):
    f2 = np.zeros_like(idx)
    f2[:-bounce] = idx[bounce:]
    both = np.concatenate([idx, f2], axis=1)
    im = Image.fromarray(both).convert('P') if False else Image.fromarray(both)
    flat = []
    for c in palette:
        flat += list(c)
    im.putpalette(flat + [0] * (48 - len(flat)))                # 16 entries: nitrogfx wants a 4-bit palette
    return im


def shiny(palette, degrees):
    out = [palette[0]]
    for r, g, b in palette[1:]:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        rr, gg, bb = colorsys.hsv_to_rgb((h + degrees / 360) % 1.0, s, v)
        out.append((round(rr * 255), round(gg * 255), round(bb * 255)))
    return out


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    boards = {}
    previews = []
    for name, (board, box, faces_right, hue) in SPECIES.items():
        if board not in boards:
            boards[board] = cv2.imread(str(BOARDS / board))
        crop, mask = cutout(boards[board], box, polygon=POLYGONS.get(name), test=COLOUR_TEST.get(name), name=name)
        if name in TRIM_LEFT:
            mask[:, :TRIM_LEFT[name]] = 0
        if name in TRIM_RIGHT:
            mask[:, TRIM_RIGHT[name]:] = 0
        if name in ENHANCE:
            lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4)).apply(lab[:, :, 0])
            crop = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            blur = cv2.GaussianBlur(crop, (0, 0), 2.0)
            crop = cv2.addWeighted(crop, 1.8, blur, -0.8, 0)
        cv2.imwrite(str(out / f'{name}_mask.png'), mask)
        views = []
        for view, size in (('front', FRONT_BOX), ('back', BACK_BOX)):
            flip = faces_right if view == 'front' else not faces_right
            views.append(to_sprite(crop, mask, size, flip))
        (front, back), palette = indexed_pair(views)
        json.dump(dict(normal=palette, shiny=shiny(palette, hue)), open(out / f'{name}_palettes.json', 'w'))
        row = []
        for view, idx in (('front', front), ('back', back)):
            sheet(idx, palette).save(out / f'{name}_{view}.png', transparency=0)
            prev = Image.new('RGB', (80, 80), (200, 200, 200))
            rgba = Image.fromarray(idx)
            flat = []
            for c in palette:
                flat += list(c)
            rgba.putpalette(flat + [0] * (768 - len(flat)))
            rgba = rgba.convert('RGBA')
            rgba.putalpha(Image.fromarray(np.where(idx > 0, 255, 0).astype(np.uint8)))
            prev.paste(rgba, (0, 0), rgba)
            row.append(prev.resize((160, 160), Image.NEAREST))
        previews.append(row)
    cols = 3
    rows = (len(previews) + cols - 1) // cols
    sheet_im = Image.new('RGB', (cols * 340, rows * 170), (255, 255, 255))
    for i, (f, b) in enumerate(previews):
        sheet_im.paste(f, ((i % cols) * 340, (i // cols) * 170))
        sheet_im.paste(b, ((i % cols) * 340 + 170, (i // cols) * 170))
    sheet_im.save(out / 'preview.png')


if __name__ == '__main__':
    main(sys.argv[1])
