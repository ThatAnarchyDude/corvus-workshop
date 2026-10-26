"""TEST ONLY: Game Corner Rocket guard -> win -> the poster opens the hideout. Prints the map position after each phase (env DS_ROM/DS_OUT as ds_session)."""
import sys, struct
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
from PIL import Image
X, Z = 0x1da6f6, 0x1da6fe
A, UP = 8, 4
def pos():
    r = d.ram(); return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]
def field():
    d.shot('_p.png'); r, g, b = Image.open(d.root / '_p.png').convert('RGB').getpixel((20, 300)); return g > 150 and r < 90 and b < 150
d.boot(); print('start', pos(), flush=True)
d.run(12, UP); d.run(20)
for i in range(400):
    d.run(6, A); d.run(30)
    if not field():
        d.touch = (128, 270); d.run(6); d.touch = None; d.run(40)
        d.touch = ((64, 240), (190, 240), (64, 300), (190, 300))[i % 4]; d.run(6); d.touch = None; d.run(50)
    if i % 20 == 0: print(i, pos(), flush=True)
    if i > 40 and pos()[0] > 8 and pos()[1] < 4000 and (pos()[0] > 30 or pos()[1] > 30):
        pass
d.shot('end.png'); print('end', pos(), flush=True)
