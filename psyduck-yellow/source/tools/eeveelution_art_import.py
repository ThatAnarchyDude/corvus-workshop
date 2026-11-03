"""Import the derived battle sprites (tools/eeveelution_art.py output) into the ROM for the new Eeveelutions that have good art (owner order 2026-11-02: battle sprites first, only species
without art, originals untouched; the species still on placeholder art are listed in ROUGH).
Per species the picture goes into a/0/0/4 rows: ordinary (1536+i), starter (1545+i) and the Pokedex identity (501+i); files 0,1 = back, 2,3 = front (two animation frames each), 4 = normal and
5 = shiny palette. The engine's own nitrogfx (build/tools-nitrogfx/nitrogfx, rebuilt from the pokeheartgold source) converts; each species is round-trip checked.
The Mega rows keep the shared Mega Eevee art.
Usage (from yellow-heartgold, PYTHONPATH=tools): eeveelution_art_import.py <in.nds> <out.nds> <art dir> <work dir>"""
import json
import shutil
import subprocess
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image
from new_eeveelutions import NAMES, ordinary, starter
from dex_new_eeveelutions import dex_id

GFX = Path(__file__).resolve().parents[1] / 'build/tools-nitrogfx/nitrogfx'
KEYS = {'front': bytes.fromhex('110a4bba'), 'back': bytes.fromhex('c15c798a')}   # the sprite scramble keys nitrogfx reads next to the PNG (any 4 bytes work; these are Eevee's)
ROUGH = ()                                                      # all nine are imported (the three weakest were reworked 2026-11-02)


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def convert(art, work, name):
    work.mkdir(parents=True, exist_ok=True)
    pals = json.load(open(art / f'{name}_palettes.json'))
    out = {}
    for view in ('front', 'back'):
        sheet = Image.open(art / f'{name}_{view}.png')
        assert sheet.size == (160, 80) and sheet.mode == 'P'
        shutil.copyfile(art / f'{name}_{view}.png', work / f'{name}_{view}.png')
        (work / f'{name}_{view}.png.key').write_bytes(KEYS[view])
        run(GFX, work / f'{name}_{view}.png', work / f'{name}_{view}.NCGR', '-scanfronttoback', '-handleempty', '-bitdepth', '4')
        out[view] = (work / f'{name}_{view}.NCGR').read_bytes()
    front = Image.open(art / f'{name}_front.png')
    for kind in ('normal', 'shiny'):
        im = front.copy()
        flat = []
        for c in pals[kind]:
            flat += list(c)
        im.putpalette(flat + [0] * (48 - len(flat)))
        im.save(work / f'{name}_{kind}.png', transparency=0)
        run(GFX, work / f'{name}_{kind}.png', work / f'{name}_{kind}.NCLR', '-bitdepth', '8', '-nopad', '-comp', '10')
        out[kind] = (work / f'{name}_{kind}.NCLR').read_bytes()
    # round trip: the converted front sprite with the normal palette decodes to the same pixels
    run(GFX, work / f'{name}_front.NCGR', work / f'{name}_decoded.png', '-scanfronttoback', '-palette', work / f'{name}_normal.NCLR', '-object')
    assert list(Image.open(work / f'{name}_decoded.png').getdata()) == list(Image.open(art / f'{name}_front.png').getdata()), name
    return out


def patch(rom, art, work):
    art, work = Path(art), Path(work)
    g = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    done = []
    for i, name in enumerate(NAMES):
        if name in ROUGH:
            continue
        files = convert(art, work, name)
        payload = [files['back'], files['back'], files['front'], files['front'], files['normal'], files['shiny']]
        for sp in (ordinary(i), starter(i), dex_id(i)):
            for k in range(6):
                g.files[sp * 6 + k] = payload[k]
        done.append(name)
    rom.setFileByName('a/0/0/4', g.save())
    return done


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3], sys.argv[4]))
    rom.saveToFile(sys.argv[2])
