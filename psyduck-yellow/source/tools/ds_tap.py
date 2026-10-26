"""TEST ONLY: boot a fixture ROM (env DS_ROM/DS_OUT), then run a script of steps from argv[1] (JSON file): ["tap x y", "a", "b", "up", "down", "left", "right", "wait n", "shot name", "pos"]. Touch coords are image coords of the 256x384 screenshot."""
import sys, json, struct
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
X, Z = 0x1da6f6, 0x1da6fe
KEYS = {'x': 9, 'start': 3, 'l': 10, 'r': 11, 'a': 8, 'b': 0, 'up': 4, 'down': 5, 'left': 6, 'right': 7}
def pos():
    r = d.ram(); return struct.unpack_from('<H', r, X)[0], struct.unpack_from('<H', r, Z)[0]
d.boot(); print('start', pos(), flush=True)
for step in json.load(open(sys.argv[1])):
    w = step.split()
    if w[0] == 'tap': d.touch = (int(w[1]), int(w[2])); d.run(8); d.touch = None; d.run(50)
    elif w[0] in KEYS: d.run(8, KEYS[w[0]]); d.run(40)
    elif w[0] == 'hold': d.run(int(w[2]), KEYS[w[1]]); d.run(20)
    elif w[0] == 'wait': d.run(int(w[1]))
    elif w[0] == 'shot': d.shot(w[1] + '.png')
    elif w[0] == 'tshot': d.shot_true(w[1] + '.png')           # true colours (see ds_session.shot_true)
    elif w[0] == 'pos': print('pos', pos(), flush=True)
print('done', flush=True)
