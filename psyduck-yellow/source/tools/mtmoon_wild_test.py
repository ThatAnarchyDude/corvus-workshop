"""TEST ONLY: pace back and forth on a cave floor until a wild battle starts, screenshot it. env DS_ROM/DS_OUT as ds_session."""
import sys
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
UP, DOWN, LEFT, RIGHT, A = 4, 5, 6, 7, 8
from PIL import Image
def menu():
    d.shot('_p.png'); r, g, b = Image.open(d.root / '_p.png').convert('RGB').getpixel((20, 300)); return g > 150 and r < 90 and b < 150
import struct
X, Z = 0x1da6f6, 0x1da6fe
def pos():
    r = d.ram(); return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]
d.boot()
for i in range(120):
    d.run(40, ((DOWN, UP) if len(sys.argv) > 1 and sys.argv[1] == 'v' else (RIGHT, LEFT))[i % 2]); d.run(4)
    if i < 8 or i % 40 == 0: print(i, pos(), flush=True)
    if not menu() and (d.run(240) or not menu()):
        d.run(60); d.shot('wild.png'); print('battle after', i, flush=True); break
else: print('no battle')
