"""Replace the "JOHTO" wording on the Pokedex's main screen with "KANTO" (owner order 2026-10-23).

Both pieces are pixels in the Pokedex app's tile sheet (a/0/6/8 file 1, LZ10 4bpp, drawn as 35 tiles per row):
 - the big title "JOHTO POKeDEX": 20 pixels tall, tile columns 16-34, rows y=24..47. "JOHTO" occupies x=128..178; it is rebuilt as "KANTO"
   from letters of the same font already on the sheet (K from POKeDEX, A, N, T, O from NATIONAL), one blank column between letters.
 - the tiny region label beside the National/regional switch: a 3-pixel-tall font, "JOHTO" at x=130; rebuilt as "KANTO" from the neighbouring
   NATIONAL label's N, A, T, O plus a hand-drawn K in the same style.
Nothing else on the sheet changes (the National title and label are untouched).

Usage: dex_labels.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.lz10
import ndspy.narc
import ndspy.rom

ARCHIVE, FILE = 'a/0/6/8', 1
COLS = 35
TITLE_Y0, TITLE_Y1 = 24, 48
JOHTO_X0, JOHTO_X1 = 128, 183                      # columns rewritten (the word and its trailing gap, up to the P of POKeDEX at 184)
TITLE_LETTERS = (('K', 206, 214), ('A', 43, 52), ('N', 32, 41), ('T', 159, 167), ('O', 169, 178))
GAP_COLUMN = 180
# The small label is two tiles tall. Each letter is 4 pixels wide and 6 rows tall: its upper three rows are rows 5-7 of a tile in tile row 2
# (tiles 86-90 for the JOHTO label, tiles 58-.. region for NATIONAL, read from x=59) and its lower three rows are rows 0-2 of a tile in tile row 2's
# companions (tiles 98-102 for JOHTO, 93-97 for NATIONAL, which start at x=224 and x=184 of row 16).
UPPER_Y = 21                                        # first of the three upper rows
UPPER_X0 = 130                                      # JOHTO's first letter
LOWER_X0, LOWER_Y = 224 + 2, 16                     # JOHTO's lower halves: tile 98 starts at x=224; letters start 2 pixels in
NATIONAL_LOWER_X0 = 184                             # NATIONAL's lower halves: tile 93 starts at x=184
UPPER_SRC = {'N': 59, 'A': 64, 'T': 69, 'O': 77}    # x of each glyph's upper half in the NATIONAL label
LOWER_SRC = {'N': 3, 'A': 8, 'T': 13, 'O': 21}      # offset of each glyph's lower half from tile 93
K_UPPER = ('f.df', 'ffd.', 'ff..')
K_LOWER = ('ffd.', 'f.df', 'f..f')
SYMBOL = {'.': 1, 'd': 13, 'f': 15}


class Sheet:
    def __init__(self, raw):
        self.raw = raw
        size = struct.unpack_from('<I', raw, 16 + 0x18)[0]
        data = raw[16 + 0x20:16 + 0x20 + size]
        px = []
        for b in data:
            px += [b & 15, b >> 4]
        self.tiles = [px[t * 64:(t + 1) * 64] for t in range(len(px) // 64)]
        self.tail = raw[16 + 0x20 + size:]

    def get(self, x, y):
        return self.tiles[(y // 8) * COLS + x // 8][(y % 8) * 8 + x % 8]

    def put(self, x, y, v):
        self.tiles[(y // 8) * COLS + x // 8][(y % 8) * 8 + x % 8] = v

    def encode(self):
        flat = [v for t in self.tiles for v in t]
        data = bytes(flat[i] | (flat[i + 1] << 4) for i in range(0, len(flat), 2))
        return self.raw[:16 + 0x20] + data + self.tail


def patch(rom):
    narc = ndspy.narc.NARC(rom.getFileByName(ARCHIVE))
    sheet = Sheet(ndspy.lz10.decompress(bytes(narc.files[FILE])))
    # --- title
    col = lambda x: [sheet.get(x, y) for y in range(TITLE_Y0, TITLE_Y1)]
    new = []
    for n, (name, x0, x1) in enumerate(TITLE_LETTERS):
        if n:
            new.append(col(GAP_COLUMN))
        new += [col(x) for x in range(x0, x1 + 1)]
    assert len(new) <= JOHTO_X1 - JOHTO_X0 + 1, len(new)
    background = col(GAP_COLUMN)
    new += [background] * (JOHTO_X1 - JOHTO_X0 + 1 - len(new))
    for k, column in enumerate(new):
        for j, v in enumerate(column):
            sheet.put(JOHTO_X0 + k, TITLE_Y0 + j, v)
    # --- small label
    glyphs = {}
    for name in 'ANTO':
        upper = [[sheet.get(UPPER_SRC[name] + dx, UPPER_Y + j) for dx in range(4)] for j in range(3)]
        lower = [[sheet.get(NATIONAL_LOWER_X0 + LOWER_SRC[name] + dx, LOWER_Y + j) for dx in range(4)] for j in range(3)]
        glyphs[name] = (upper, lower)
    glyphs['K'] = ([[SYMBOL[c] for c in row] for row in K_UPPER], [[SYMBOL[c] for c in row] for row in K_LOWER])
    up_bg = [sheet.get(UPPER_X0 + 30, UPPER_Y + j) for j in range(3)]       # plain background beside the label
    lo_bg = [sheet.get(LOWER_X0 + 30, LOWER_Y + j) for j in range(3)]
    for k in range(0, 40):                                                   # blank the old word (both halves, 5 tiles wide)
        for j in range(3):
            if UPPER_X0 + k < 128 + 40:
                sheet.put(UPPER_X0 - 2 + k, UPPER_Y + j, up_bg[j])
            sheet.put(LOWER_X0 - 2 + k, LOWER_Y + j, lo_bg[j])
    for k, name in enumerate('KANTO'):
        upper, lower = glyphs[name]
        for j in range(3):
            for dx in range(4):
                sheet.put(UPPER_X0 + 5 * k + dx, UPPER_Y + j, upper[j][dx])
                sheet.put(LOWER_X0 + 5 * k + dx, LOWER_Y + j, lower[j][dx])
    narc.files[FILE] = ndspy.lz10.compress(sheet.encode())
    rom.setFileByName(ARCHIVE, narc.save())
    return dict(title_columns=len(new), label='KANTO')


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
