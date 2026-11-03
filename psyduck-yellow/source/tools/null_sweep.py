"""TEST ONLY: sweep area-boundary crossings with the NULL tracer (tools/null_trace.py). The 3DS aborts on NULL accesses that DeSmuME tolerates (owner photos 2026-10-29 / 2026-11-02), so each hit is a
potential real-hardware crash. For every row of <boundaries.json> ([matrix, header A, header B, [x, z], direction]) it builds a fixture on <rom> at (header A, x, z) with tools/mkfix.py, boots it, walks across
the boundary, waits for the area popup, and records the tracer's NULL hits (direction 'load' = boot into the map at (x, z) and wait instead). The fixture is deleted afterwards. Results -> <out.json>.
Env NULL_TRACE_PY = python with py-desmume + capstone installed. Usage (from yellow-heartgold): null_sweep.py <rom.nds> <boundaries.json> <out.json> [workers=4] [first last]"""
import json
import os
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TRACE_PY = os.environ['NULL_TRACE_PY']
WORK = os.path.join(HERE, '..', 'build', 'sweep')


def one(rom, row):
    matrix, a, b, (x, z), key = row
    name = 'h%d_%d_%d_%d' % (a, b, x, z)
    work = os.path.join(WORK, name)
    shutil.rmtree(work, ignore_errors=True)
    env = dict(os.environ, PYTHONPATH=HERE)
    subprocess.run([sys.executable, os.path.join(HERE, 'mkfix.py'), rom, work, str(a), str(x), str(z)], check=True, capture_output=True, env=env)
    if key == 'load':                                          # no walking: just boot into the map and let it run (map load, NPC and script init)
        steps = ['boot', 'hold b 10', 'mark loaded', 'pos', 'wait 300', 'pos', 'tshot shot']
    else:
        steps = ['boot', 'mark before', 'pos', 'mark crossing', 'hold %s 45' % key, 'pos', 'hold %s 45' % key, 'pos', 'mark popup', 'wait 240', 'pos', 'tshot shot']
    json.dump(steps, open(os.path.join(work, 'steps.json'), 'w'))
    proc = subprocess.run([TRACE_PY, os.path.join(HERE, 'null_trace.py'), os.path.join(work, 't.nds'), os.path.join(work, 'steps.json'), os.path.join(work, 'out.json')],
                          capture_output=True, text=True, timeout=900)
    result = dict(row=row)
    try:
        data = json.load(open(os.path.join(work, 'out.json')))
        result.update(positions=[p[1:] for p in data['results']], hits=data['hits'], stats=data['stats'])
        shot = os.path.join(work, 'shot.png')
        if data['hits'] and os.path.exists(shot):
            os.makedirs(os.path.join(WORK, 'hitshots'), exist_ok=True)
            shutil.copy(shot, os.path.join(WORK, 'hitshots', name + '.png'))
    except Exception as error:
        result.update(error=repr(error), stderr=proc.stderr[-400:])
    shutil.rmtree(work, ignore_errors=True)
    return result


def main(rom, rows_file, out, workers, lo, hi):
    rows = json.load(open(rows_file))[lo:hi]
    os.makedirs(WORK, exist_ok=True)
    done, lock = [], threading.Lock()

    def job(row):
        res = one(rom, row)
        with lock:
            done.append(res)
            json.dump(done, open(out, 'w'))
            print('%d/%d %s hits=%d %s' % (len(done), len(rows), row[:3], len(res.get('hits', [])), res.get('error', '')), flush=True)
        return res

    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(job, rows))


if __name__ == '__main__':
    argv = sys.argv
    main(argv[1], argv[2], argv[3], int(argv[4]) if len(argv) > 4 else 4, int(argv[5]) if len(argv) > 5 else 0, int(argv[6]) if len(argv) > 6 else 10 ** 9)
