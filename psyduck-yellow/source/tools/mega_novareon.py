"""Mega Novareon's own art (owner's concept picture, 2026-10-23): battle sprites for species 1582 and the Novareonite item icon.

 - Battle sprites: mega_novareon_art.py builds the front and back sheets (Novareon's body, one big rainbow disk tail). They are converted
   with the engine's nitrogfx exactly as novareon.py does and written into a/0/0/4 for species 1582 (6 files: back, back, front, front, palette,
   shiny palette). No shiny design exists, so the shiny palette equals the normal one. Base Novareon (1581) is unchanged.
 - Novareonite icon: a hand-drawn 32x32 gem (blue faceted disk, copper rim and orbit ring, cream star), converted like the Sandwich icon, replaces the copy of
   Eonite's icon it had (a/0/1/8 files 3147*2+2 and +3).
 The Mega's party icon stays Novareon's (the shared icon palettes cannot hold the rainbow).

Usage: mega_novareon.py <in.nds> <out.nds> <010_Novareon folder> <work dir>
"""
import shutil
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image, ImageDraw
import mega_novareon_art as art_module
from novareon import GFX, KEYS, run
from starter_eevee_line import FIRST, NOVAREON, mega

NOVAREONITE = 3147


def novareonite_png(path):
    pal = [(255, 0, 255), (22, 18, 44), (150, 84, 52), (236, 152, 92), (26, 38, 98), (50, 74, 160), (108, 138, 214), (190, 206, 242),
           (252, 238, 204), (206, 176, 136), (255, 255, 255)]
    im = Image.new('P', (32, 32), 0)
    im.putpalette([c for rgb in pal for c in rgb] + [0] * (768 - 3 * len(pal)))
    d = ImageDraw.Draw(im)
    d.ellipse((2, 2, 29, 29), fill=1)                       # outline
    d.ellipse((3, 3, 28, 28), fill=2)                       # copper rim
    d.ellipse((4, 4, 27, 27), fill=4)                       # deep blue gem
    for poly, col in (([(7, 8), (14, 5), (12, 11)], 7), ([(5, 14), (9, 10), (10, 16)], 6), ([(20, 6), (25, 10), (21, 11)], 6),
                      ([(22, 22), (26, 17), (27, 22)], 5), ([(8, 23), (13, 21), (12, 26)], 5), ([(15, 4), (21, 5), (17, 9)], 6)):
        d.polygon(poly, fill=col)
    d.arc((7, 8, 25, 22), 0, 360, fill=3)                   # copper orbit ring
    d.ellipse((7, 14, 8, 15), fill=3)
    d.ellipse((24, 11, 25, 12), fill=3)
    star = [(16, 6), (18, 13), (24, 12), (19, 16), (22, 23), (16, 19), (10, 23), (13, 16), (8, 12), (14, 13)]
    d.polygon(star, fill=8)
    d.polygon([(16, 6), (18, 13), (16, 16), (14, 13)], fill=10)
    d.polygon([(16, 19), (22, 23), (19, 16)], fill=9)
    d.polygon([(16, 19), (10, 23), (13, 16)], fill=9)
    d.ellipse((3, 3, 28, 28), outline=3, width=1)
    d.arc((2, 2, 29, 29), 200, 340, fill=1)
    px = im.load()
    for y in range(32):
        for x in range(32):
            if (x - 15.5) ** 2 + (y - 15.5) ** 2 > 14.2 ** 2 and px[x, y] == 3:
                px[x, y] = 2
    im.save(path, transparency=0)


def patch(rom, art, work, icon=True):
    art, work = Path(art), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    art_module.main(art, work)
    for view in ('front', 'back'):
        shutil.copyfile(KEYS / f'{view}.png.key', work / f'mega_{view}_160x80_two_frame.png.key')
        run(GFX, work / f'mega_{view}_160x80_two_frame.png', work / f'mega_{view}.NCGR', '-scanfronttoback', '-handleempty', '-bitdepth', '4')
    run(GFX, work / 'mega_front_160x80_two_frame.png', work / 'mega.NCLR', '-bitdepth', '8', '-nopad', '-comp', '10')
    for view in ('front', 'back'):                                    # native-format round trip
        target = work / f'{view}-mega-decoded.png'
        run(GFX, work / f'mega_{view}.NCGR', target, '-scanfronttoback', '-palette', work / 'mega.NCLR', '-object')
        assert list(Image.open(target).getdata()) == list(Image.open(work / f'mega_{view}_160x80_two_frame.png').getdata()), view
    species = mega(NOVAREON)
    g = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    for i, view in enumerate(('back', 'back', 'front', 'front')):
        g.files[species * 6 + i] = (work / f'mega_{view}.NCGR').read_bytes()
    palette = (work / 'mega.NCLR').read_bytes()
    g.files[species * 6 + 4] = palette
    g.files[species * 6 + 5] = palette
    rom.setFileByName('a/0/0/4', g.save())
    if not icon:                                                      # the chain's item_icons.py already gave Novareonite its marble
        return dict(mega_species=species)
    novareonite_png(work / 'novareonite.png')
    run(GFX, work / 'novareonite.png', work / 'novareonite.NCGR', '-clobbersize', '-version101', '-bitdepth', '4')
    run(GFX, work / 'novareonite.png', work / 'novareonite.NCLR', '-ir', '-bitdepth', '4')
    items = ndspy.narc.NARC(rom.getFileByName('a/0/1/8'))
    items.files[NOVAREONITE * 2 + 2] = (work / 'novareonite.NCGR').read_bytes()
    items.files[NOVAREONITE * 2 + 3] = (work / 'novareonite.NCLR').read_bytes()
    rom.setFileByName('a/0/1/8', items.save())
    return dict(mega_species=species, novareonite_icon_files=(NOVAREONITE * 2 + 2, NOVAREONITE * 2 + 3))


if __name__ == '__main__':
    src, dst, art, work = [a for a in sys.argv[1:] if not a.startswith('--')][:4]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom, art, work, icon='--no-icon' not in sys.argv))
    rom.saveToFile(dst)
