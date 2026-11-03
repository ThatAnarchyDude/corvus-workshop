"""Box / artwork sprites for the custom species in the Psyduck Yellow PKHeX fork (owner order 2026-11-02).
Ten species have no national sprite: Brawleon, Venomeon, Duneon, Zephyreon, Chryseon, Strateon, Wraitheon, Wyrmeon, Ferreon and Stellareon. Each gets 68x56 RGBA pictures
b_py<i>.png (Big Pokemon Sprites), b_py<i>s.png (Big Shiny Sprites) and a_py<i>.png (Artwork Pokemon Sprites), i = index in NAMES, derived from the species' front battle sprite
(tools/eeveelution_art.py output; Stellareon's is decoded from the ROM with nitrogfx). The shiny picture is the same picture with its hue turned like the game's shiny palette.
Usage (from yellow-heartgold): pkhex_icons.py <rom> <art dir> <work dir> <PKHeX.Drawing.PokeSprite folder>"""
import colorsys
import shutil
import subprocess
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image
from eeveelution_art import SPECIES as ART

NAMES = ['Brawleon', 'Venomeon', 'Duneon', 'Zephyreon', 'Chryseon', 'Strateon', 'Wraitheon', 'Wyrmeon', 'Ferreon', 'Stellareon']
STELLAREON_SPECIES, STELLAREON_HUE = 1581, 150
GFX = Path(__file__).resolve().parents[1] / 'build/tools-nitrogfx/nitrogfx'
SIZE = (68, 56)
KEYS = {'front': bytes.fromhex('110a4bba')}


def front_frame(png):
    im = Image.open(png).convert('RGBA')
    return im.crop((0, 0, 80, 80))


def stellareon_front(rom, work):
    g = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    (work / 'st.NCGR').write_bytes(bytes(g.files[STELLAREON_SPECIES * 6 + 3]))
    (work / 'st.NCLR').write_bytes(bytes(g.files[STELLAREON_SPECIES * 6 + 4]))
    subprocess.run([str(GFX), str(work / 'st.NCGR'), str(work / 'st.png'), '-scanfronttoback', '-palette', str(work / 'st.NCLR'), '-object'], check=True)
    sheet = Image.open(work / 'st.png').convert('RGBA')
    frame = sheet.crop((0, 0, 80, 80))
    idx = Image.open(work / 'st.png')
    px = frame.load()
    ip = idx.load()
    for y in range(80):
        for x in range(80):
            if ip[x, y] == 0:
                px[x, y] = (0, 0, 0, 0)
    return frame


def fit(frame):
    box = frame.getchannel('A').getbbox()
    sprite = frame.crop(box)
    scale = min((SIZE[0] - 2) / sprite.width, (SIZE[1] - 2) / sprite.height)
    small = sprite.resize((max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))), Image.LANCZOS)
    out = Image.new('RGBA', SIZE, (0, 0, 0, 0))
    out.paste(small, ((SIZE[0] - small.width) // 2, SIZE[1] - small.height - 1), small)
    return out


def hue_shift(img, degrees):
    out = img.copy()
    px = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                rr, gg, bb = colorsys.hsv_to_rgb((h + degrees / 360) % 1.0, s, v)
                px[x, y] = (round(rr * 255), round(gg * 255), round(bb * 255), a)
    return out


def main(rom_path, art, work, target):
    work, target, art = Path(work), Path(target), Path(art)
    work.mkdir(parents=True, exist_ok=True)
    rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
    for i, name in enumerate(NAMES):
        if name == 'Stellareon':
            frame, hue = stellareon_front(rom, work), STELLAREON_HUE
        else:
            frame, hue = front_frame(art / f'{name}_front.png'), ART[name][3]
            sheet = Image.open(art / f'{name}_front.png')
            px, sp = frame.load(), sheet.load()
            for y in range(80):
                for x in range(80):
                    if sp[x, y] == 0:
                        px[x, y] = (0, 0, 0, 0)
        pic = fit(frame)
        pic.save(target / 'Resources/img/Big Pokemon Sprites' / f'b_py{i}.png')
        pic.save(target / 'Resources/img/Artwork Pokemon Sprites' / f'a_py{i}.png')
        hue_shift(pic, hue).save(target / 'Resources/img/Big Shiny Sprites' / f'b_py{i}s.png')
    print('wrote', len(NAMES) * 3, 'pictures')


if __name__ == '__main__':
    main(*sys.argv[1:5])
