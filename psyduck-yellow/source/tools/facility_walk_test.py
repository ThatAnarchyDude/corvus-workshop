"""TEST ONLY: live walk through chosen facility warps. For each (map, warp index) it reads the ROM's own events (arrival tile, block tiles, destination), builds a fixture next to the block under build/fx, steps onto the block,
and prints where the player lands against the destination's own arrival tile. Screenshots (start/after) go to build/fx/<tag>/. Env NULL_TRACE_PY = python with py-desmume + capstone.
Usage: facility_walk_test.py <rom.nds> <map:warp>[,<map:warp>...]"""
import json
import os
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, '..', 'build', 'fx')
KEY = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}


def warps_of(rom, events, recs, m):
    g = events_decode(bytes(events[struct.unpack_from('<H', recs[m - ext.NATIVE_COUNT], 16)[0]]))
    return [struct.unpack_from('<4H', w, 0) for w in g[2]], g[3]


def plan(rom, m, i):
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    recs = ext.records(rom)
    warps, triggers = warps_of(rom, events, recs, m)
    n = sum(1 for w in warps if w[2] == m and w[3] < 64 and (warps.index(w) < 64)) if False else None
    arrivals = []
    for k, w in enumerate(warps):
        if w[2] == m and w[3] == k:
            arrivals.append(w)
        else:
            break
    n = len(arrivals)
    ax, az = arrivals[i][0], arrivals[i][1]
    block = [(w[0], w[1], w[2], w[3]) for w in warps[n:]]
    near = [b for b in block if abs(b[0] - ax) + abs(b[1] - az) == 1] or [b for b in block if abs(b[0] - ax) + abs(b[1] - az) == 1]
    return arrivals, block, (ax, az)


def run(rom_path, m, i):
    rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    recs = ext.records(rom)
    warps, triggers = warps_of(rom, events, recs, m)
    arrivals = []
    for k, w in enumerate(warps):
        if w[2] == m and w[3] == k:
            arrivals.append(w)
        else:
            break
    n = len(arrivals)
    ax, az = arrivals[i][0], arrivals[i][1]
    block = [w for w in warps[n:]]
    step = None
    for w in block:
        d = (w[0] - ax, w[1] - az)
        if d in KEY and (w[2], w[3]) != (m, i):
            step = (KEY[d], w)
            break
    if step is None:                                           # arrival on the block itself (walled-in pad): move to any neighbouring block tile
        for w in block:
            d = (w[0] - ax, w[1] - az)
            if d in KEY:
                step = (KEY[d], w)
                break
    tag = f'w{m}_{i}'
    work = os.path.join(FX, tag)
    env = dict(os.environ, PYTHONPATH=HERE)
    subprocess.run([sys.executable, os.path.join(HERE, 'mkfix.py'), rom_path, work, str(m), str(ax), str(az)], check=True, capture_output=True, env=env)
    key = step[0] if step else 'down'
    json.dump(['boot', 'hold b 30', 'pos', 'tshot start', 'hold %s 20' % key, 'pos', 'wait 200', 'pos', 'tshot after'], open(os.path.join(work, 'steps.json'), 'w'))
    subprocess.run([os.environ['NULL_TRACE_PY'], os.path.join(HERE, 'null_trace.py'), os.path.join(work, 't.nds'), os.path.join(work, 'steps.json'), os.path.join(work, 'out.json')], capture_output=True, text=True, timeout=900)
    data = json.load(open(os.path.join(work, 'out.json')))
    os.remove(os.path.join(work, 't.nds'))
    pos = [p[1:] for p in data['results']]
    exp = None
    if step:
        dm, da = step[1][2], step[1][3]
        if dm != m or True:
            dwarps, _ = warps_of(rom, events, recs, dm) if dm >= ext.NATIVE_COUNT else ([], [])
            exp = (dm, dwarps[da][:2]) if dwarps and da < len(dwarps) else (dm, da)
    return dict(map=m, warp=i, arrival=(ax, az), step=key, block_tile=step[1][:2] if step else None, positions=pos, expected=exp, hits=len(data['hits']))


if __name__ == '__main__':
    todo = [tuple(int(v) for v in s.split(':')) for s in sys.argv[2].split(',')]
    with ThreadPoolExecutor(4) as pool:
        for r in pool.map(lambda t: run(sys.argv[1], *t), todo):
            print(r, flush=True)
