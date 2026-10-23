"""Novareon (starter Eevee line, species 1581) and Mega Novareon (1582): Sandwich evolution, supplied art, Stellar typing.

Builds on starter_eevee_line, where Novareon is an Umbreon stand-in evolved with the Dusk Stone.
 - Starter Eevee's ninth evolution slot now takes the Sandwich (item 1830). The Sandwich's record becomes a copy of the
   Dusk Stone's (the engine's evolution-stone use) at price 0, so it works from the Items pocket; it joins the free
   Mega Stone pool in the Vermilion shared Mart so the evolution is reachable.
 - Both species get the supplied Novareon battle sprites (front/back). No shiny sheet exists, so the shiny palette is the
   normal palette. The supplied menu icon is not imported.
 - Both species are named Novareon (the stand-in copied Umbreon's name).
 - Both species' types are Stellar (type 19, which hg-engine already defines for Terastallization): the personal-data
   type bytes are 19/19.

Usage: novareon.py <in.nds> <out.nds> <extracted 010_Novareon folder> <work dir>
"""
import shutil
import struct
import subprocess
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image
import mega_shop
from prototype import decode_messages, encode_messages
from starter_eevee_line import FIRST, NOVAREON, starter, mega, _words

SANDWICH, DUSK_STONE, STELLAR = 1830, 108, 19
ENGINE = Path(__file__).resolve().parents[2] / 'private/hg-engine-0037-v1/hg-engine-main'
GFX = ENGINE / 'tools/nitrogfx'
KEYS = ENGINE / 'data/graphics/sprites/psyduck/female'
SPECIES = (starter(NOVAREON), mega(NOVAREON))                      # 1581, 1582


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def convert_art(art, work):
    sheets = {}
    for view in ('front', 'back'):
        sheets[view] = Image.open(art / 'battle_sprites/base_form' / f'novareon_{view}_160x80_two_frame_template.png')
        assert sheets[view].size == (160, 80) and sheets[view].mode == 'P'
        shutil.copyfile(KEYS / f'{view}.png.key', work / f'{view}-two-frame.png.key')
        sheets[view].save(work / f'{view}-two-frame.png')
        run(GFX, work / f'{view}-two-frame.png', work / f'{view}.NCGR', '-scanfronttoback', '-handleempty', '-bitdepth', '4')
    run(GFX, work / 'front-two-frame.png', work / 'normal.NCLR', '-bitdepth', '8', '-nopad', '-comp', '10')
    for view in ('front', 'back'):                                    # native-format round trip
        target = work / f'{view}-decoded.png'
        run(GFX, work / f'{view}.NCGR', target, '-scanfronttoback', '-palette', work / 'normal.NCLR', '-object')
        assert list(Image.open(target).getdata()) == list(sheets[view].getdata()), view


def patch(rom, art, work):
    art, work = Path(art), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    convert_art(art, work)
    ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/4'))
    rec = bytearray(ev.files[FIRST - 4])                             # starter Eevee (1561)
    assert struct.unpack_from('<HHH', rec, 48) == (7, DUSK_STONE, SPECIES[0]), 'ninth slot is not the Dusk Stone stand-in'
    struct.pack_into('<H', rec, 50, SANDWICH)
    ev.files[FIRST - 4] = bytes(rec)
    rom.setFileByName('a/0/3/4', ev.save())
    items = ndspy.narc.NARC(rom.getFileByName('a/0/1/7'))
    record = bytearray(items.files[DUSK_STONE])
    record[0:2] = bytes(2)                                            # price 0, like the Mega Stones
    items.files[SANDWICH] = bytes(record)
    rom.setFileByName('a/0/1/7', items.save())
    g = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    pers = ndspy.narc.NARC(rom.getFileByName('a/0/0/2'))
    for species in SPECIES:
        for i, view in enumerate(('back', 'back', 'front', 'front')):
            g.files[species * 6 + i] = (work / f'{view}.NCGR').read_bytes()
        normal = (work / 'normal.NCLR').read_bytes()
        g.files[species * 6 + 4] = normal
        g.files[species * 6 + 5] = normal                             # no shiny sheet supplied
        p = bytearray(pers.files[species])
        p[6] = p[7] = STELLAR
        pers.files[species] = bytes(p)
    rom.setFileByName('a/0/0/4', g.save())
    rom.setFileByName('a/0/0/2', pers.save())
    text = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    for bank in (237, 238):                                           # species names: stop reading "Umbreon"
        key, rows = decode_messages(text.files[bank])
        for species in SPECIES:
            rows[species] = _words('Novareon')
        text.files[bank] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', text.save())
    return dict(evolution='starter Eevee + Sandwich (1830) -> %d' % SPECIES[0], sandwich_price=0, species=SPECIES, types=STELLAR)


if __name__ == '__main__':
    src, dst, art, work = sys.argv[1:5]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom, art, work))
    print(mega_shop.patch(rom, Path(__file__).resolve().parent.parent, extra=(SANDWICH,)))
    rom.saveToFile(dst)
