"""TEST ONLY: boot DS_ROM once and keep the emulator alive; step lists written to DS_OUT/cmd.json run in order and results land in DS_OUT/out.json.
Steps: touch x y [frames] | wait n | a b x up down left right (one tap) | hold key frames | pos | tshot name | crop name x0 y0 x1 y1 | peek hexaddr n | find hexbytes | quit"""
import json
import os
import struct
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ds_session as d
from PIL import Image
X, Z = 0x1da6f6, 0x1da6fe
KEYS = {'x': 9, 'start': 3, 'l': 10, 'r': 11, 'a': 8, 'b': 0, 'up': 4, 'down': 5, 'left': 6, 'right': 7}


def pos():
    r = d.ram()
    return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]


d.boot()
print('start', pos(), flush=True)
cmd, out = os.path.join(os.environ['DS_OUT'], 'cmd.json'), os.path.join(os.environ['DS_OUT'], 'out.json')
while True:
    if not os.path.exists(cmd):
        time.sleep(0.2)
        continue
    time.sleep(0.2)
    steps = json.load(open(cmd))
    os.remove(cmd)
    res = []
    for step in steps:
        w = step.split()
        if w[0] == 'quit':
            sys.exit(0)
        elif w[0] in KEYS:
            d.run(8, KEYS[w[0]]); d.run(40)
        elif w[0] == 'touch':
            d.touch = (int(w[1]), int(w[2])); d.run(int(w[3]) if len(w) > 3 else 12); d.touch = None; d.run(30)
        elif w[0] == 'hold':
            d.run(int(w[2]), KEYS[w[1]]); d.run(20)
        elif w[0] == 'wait':
            d.run(int(w[1]))
        elif w[0] == 'pos':
            res.append(['pos'] + list(pos()))
        elif w[0] == 'tshot':
            d.shot_true(w[1] + '.png')
        elif w[0] == 'crop':
            d.shot_true('_full.png')
            im = Image.open(os.path.join(os.environ['DS_OUT'], '_full.png')).crop(tuple(int(v) for v in w[2:6]))
            im.save(os.path.join(os.environ['DS_OUT'], w[1] + '.png'))
        elif w[0] == 'peek':
            a = int(w[1], 16)
            res.append(['peek', w[1], d.ram()[a:a + int(w[2])].hex()])
        elif w[0] == 'find':
            pat = bytes.fromhex(w[1])
            r = d.ram()
            hits, i = [], r.find(pat)
            while i >= 0 and len(hits) < 20:
                hits.append(hex(i))
                i = r.find(pat, i + 1)
            res.append(['find', w[1], hits])
    json.dump(res, open(out + '.tmp', 'w'))
    os.replace(out + '.tmp', out)
