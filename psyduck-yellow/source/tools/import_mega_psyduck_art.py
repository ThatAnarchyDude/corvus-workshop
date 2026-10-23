"""Import the supplied Mega Psyduck battle sprites and the Psyduckite icon into Mega Psyduck (record 1564) and item 3146.

Usage: import_mega_psyduck_art.py <in.nds> <out.nds> <extracted 000_Psyduck_Starter_Line folder> <work dir>

The supplied 160x80 two-frame templates are indexed with colour 0 transparent. Normal and shiny share pixel data in the
ROM, so the shiny palette is the supplied shiny sheet's most common colour for each normal-palette index (a few shiny-only
shading differences cannot be represented). Conversion uses the engine's own nitrogfx and is round-trip checked.
"""
import struct
import subprocess
import sys
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image
import ndspy.lz10
import ndspy.narc
import ndspy.rom

MEGA, STONE = 1564, 3146
ENGINE = Path(__file__).resolve().parents[2] / 'private/hg-engine-0037-v1/hg-engine-main'
GFX = ENGINE / 'tools/nitrogfx'
KEYS = ENGINE / 'data/graphics/sprites/psyduck/female'


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def rgb555(rgb):
    return sum((c * 31 // 255) << s for c, s in zip(rgb, (0, 5, 10)))


def shiny_palette(normal, shiny):
    """Per normal-palette index, the shiny sheet's most common colour at the same pixels (front and back together)."""
    votes = defaultdict(Counter)
    for n, s in zip(normal, shiny):
        np_, sp = n.getpalette(), s.getpalette()
        for a, b in zip(n.getdata(), s.getdata()):
            votes[a][tuple(sp[3 * b:3 * b + 3])] += 1
    out = []
    for i in range(16):
        np_ = normal[0].getpalette()
        out.append(rgb555(votes[i].most_common(1)[0][0]) if votes[i] else rgb555(tuple(np_[3 * i:3 * i + 3])))
    return out


def icon_png(source, target):
    im = Image.open(source).convert('RGBA')
    mask = im.getchannel('A').point(lambda v: 255 if v > 127 else 0)
    flat = Image.new('RGB', im.size, (0, 0, 0))
    flat.paste(im.convert('RGB'), mask=mask)
    q = flat.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:45]
    out = Image.new('P', im.size)
    out.putpalette([255, 0, 255] + pal + [0] * (768 - 48))
    out.putdata([0 if not m else i + 1 for i, m in zip(q.getdata(), mask.getdata())])
    out.save(target, transparency=0)


def main(src, dst, art, work):
    art, work = Path(art), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    sheets = {}
    for tag, folder, stem in (('normal', 'mega_form', 'mega_psyduck'), ('shiny', 'mega_form_shiny', 'mega_psyduck_shiny')):
        for view in ('front', 'back'):
            sheets[tag, view] = Image.open(art / 'battle_sprites' / folder / f'{stem}_{view}_160x80_two_frame_template.png')
    for view in ('front', 'back'):
        assert sheets['normal', view].size == (160, 80) and sheets['normal', view].mode == 'P'
        shutil.copyfile(KEYS / f'{view}.png.key', work / f'{view}-two-frame.png.key')
        sheets['normal', view].save(work / f'{view}-two-frame.png')
        run(GFX, work / f'{view}-two-frame.png', work / f'{view}.NCGR', '-scanfronttoback', '-handleempty', '-bitdepth', '4')
    run(GFX, work / 'front-two-frame.png', work / 'normal.NCLR', '-bitdepth', '8', '-nopad', '-comp', '10')
    normal = ndspy.lz10.decompress((work / 'normal.NCLR').read_bytes()) if (work / 'normal.NCLR').read_bytes()[0] == 16 else (work / 'normal.NCLR').read_bytes()
    assert normal[:4] == b'RLCN'
    colors = shiny_palette([sheets['normal', v] for v in ('front', 'back')], [sheets['shiny', v] for v in ('front', 'back')])
    shiny = bytearray(normal)
    struct.pack_into('<16H', shiny, 40, *colors)
    (work / 'shiny.NCLR').write_bytes(ndspy.lz10.compress(bytes(shiny)))
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    a = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    before = list(a.files)
    assert len(a.files) >= (MEGA + 1) * 6
    for i, view in enumerate(('back', 'back', 'front', 'front')):
        a.files[MEGA * 6 + i] = (work / f'{view}.NCGR').read_bytes()
    a.files[MEGA * 6 + 4] = (work / 'normal.NCLR').read_bytes()
    a.files[MEGA * 6 + 5] = (work / 'shiny.NCLR').read_bytes()
    changed = [i for i, (x, y) in enumerate(zip(before, a.files)) if x != y]
    assert changed == list(range(MEGA * 6, MEGA * 6 + 6)), changed
    rom.setFileByName('a/0/0/4', a.save())
    for view in ('front', 'back'):                                    # native-format round trip
        target = work / f'{view}-decoded.png'
        run(GFX, work / f'{view}.NCGR', target, '-scanfronttoback', '-palette', work / 'normal.NCLR', '-object')
        assert list(Image.open(target).getdata()) == list(sheets['normal', view].getdata()), view
    # Psyduckite icon
    icon_png(art / 'item_assets/psyduckite_32x32_RGBA.png', work / 'psyduckite.png')
    run(GFX, work / 'psyduckite.png', work / 'psyduckite.NCGR', '-clobbersize', '-version101', '-bitdepth', '4')
    run(GFX, work / 'psyduckite.png', work / 'psyduckite.NCLR', '-ir', '-bitdepth', '4')
    g = ndspy.narc.NARC(rom.getFileByName('a/0/1/8'))
    old = (len(g.files[STONE * 2 + 2]), len(g.files[STONE * 2 + 3]))
    g.files[STONE * 2 + 2] = (work / 'psyduckite.NCGR').read_bytes()
    g.files[STONE * 2 + 3] = (work / 'psyduckite.NCLR').read_bytes()
    assert (len(g.files[STONE * 2 + 2]), len(g.files[STONE * 2 + 3])) == old
    rom.setFileByName('a/0/1/8', g.save())
    rom.saveToFile(dst)
    print('mega members', changed, 'shiny palette', [hex(c) for c in colors], 'icon replaced')


if __name__ == '__main__':
    main(*sys.argv[1:5])
