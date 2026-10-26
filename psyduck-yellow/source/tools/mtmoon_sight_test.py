"""TEST ONLY: walk UP a lane toward a trainer, print the player's tile each step and whether a dialogue/battle interrupts. env DS_ROM/DS_OUT as ds_session."""
import sys, struct
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
from PIL import Image
X, Z = 0x1da6f6, 0x1da6fe
UP = 4
def pos():
    r = d.ram(); return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]
def dialog():
    d.shot('_p.png'); im = Image.open(d.root / '_p.png').convert('RGB')
    return sum(min(im.getpixel((x, 151))) > 235 for x in (30, 60, 100, 150, 200, 230)) >= 5
d.boot(); print('start', pos(), flush=True)
for i in range(14):
    d.run(14, UP); d.run(10); p = pos(); print(i, p, 'dialog' if dialog() else '', flush=True)
    if dialog(): break
