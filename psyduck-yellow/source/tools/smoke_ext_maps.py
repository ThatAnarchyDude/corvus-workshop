"""Emulator smoke test: warp into each extension map (540+) on its first warp tile and report how much of the top screen is drawn (a black screen means a broken map).

TEST-ONLY (uses fixture_party.py's warp option). Usage: smoke_ext_maps.py <rom.nds> <out dir> [first last]
"""
import struct
import subprocess
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
from PIL import Image
import map_header_extension as ext
from opening import events_decode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main(path, out, first=540, last=554):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    records = ext.records(rom)
    for m in range(first, last + 1):
        rec = records[m - ext.NATIVE_COUNT]
        w = events_decode(events[struct.unpack_from('<H', rec, 16)[0]])[2]
        x, y = struct.unpack_from('<2H', w[0], 0) if w else (10, 10)
        rom_out = out / f'fx{m}.nds'
        subprocess.run([sys.executable, str(HERE / 'fixture_party.py'), path, str(rom_out), '25', '0', '30', '--warp', f'{m},{x},{y + 1}'], check=True, capture_output=True, cwd=ROOT)
        subprocess.run(['bash', str(HERE / 'shoot.sh'), str(rom_out), str(out / f'em{m}'), 'fx', '{"frames":300}', '{"frames":20,"buttons":[0]}', '{"frames":60}'], check=True, cwd=ROOT)
        shot = out / f'em{m}' / 'fx.png'
        im = Image.open(shot).convert('L').crop((0, 0, 256, 192))
        dark = sum(1 for p in im.getdata() if p < 12) / (256 * 192)
        print(m, (x, y + 1), 'black fraction %.2f' % dark, flush=True)
        rom_out.unlink()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], *(int(v) for v in sys.argv[3:5]))
