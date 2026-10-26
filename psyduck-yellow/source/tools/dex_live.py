"""TEST ONLY: live Pokedex check. dex_live.py <out dir>: builds fixtures that own six species each (so they count as caught), opens the National Pokedex and screenshots the list and details pages of each dex number. R pages 15 entries, down 5, right 1."""
import json, os, subprocess, sys
T = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(T, '..', '.venv', 'bin', 'python')
ROM = os.path.join(T, '..', 'build', '0104-safari', 'sz.nds')
FIX = os.path.join(T, '..', 'build', '0040-release-v1', 'native-pickup-refreshed3', 'Pokemon-Psyduck-Yellow-prototype-0040-EXPERIMENTAL.dsv')
BATCHES = [[(386, 386), (387, 387), (493, 493)], [(494, 544), (649, 699), (650, 700)], [(721, 771), (722, 772), (809, 859)],
           [(810, 860), (905, 955), (906, 956)], [(972, 1022), (973, 1023), (1025, 1075)], [(1026, 500)]]       # three owned species per fixture (six at once broke the start script)
out = sys.argv[1]
for b, batch in enumerate(BATCHES):
    if b < int(sys.argv[2] if len(sys.argv) > 2 else 0):
        continue
    rom, dsv = f'{out}/b{b}.nds', f'{out}/b{b}.dsv'
    env = dict(os.environ, FIXTURE_EXTRA=','.join(f'{s}:20' for _, s in batch[1:]), PYTHONPATH=T)
    subprocess.run([PY, '-W', 'ignore', f'{T}/fixture_party.py', ROM, rom, str(batch[0][1]), '0', '20', '--dex'], env=env, check=True, capture_output=True)
    subprocess.run(['cp', FIX, dsv], check=True)
    steps = ['wait 600', 'x', 'wait 60', 'a', 'wait 120', 'left', 'wait 40', 'a', 'wait 90']
    cur = batch[0][0] + (1 if batch[0][0] != 1 else 0)     # the list opens one entry after the first owned one (observed)
    for n, sp in batch:
        d = n - cur
        steps += ['r', 'wait 25'] * (d // 15)
        d %= 15
        steps += ['down', 'wait 25'] * (d // 5) + ['right', 'wait 25'] * (d % 5)
        cur = n
        steps += ['tshot %d_list' % n, 'a', 'wait 90', 'tshot %d_info' % n]
        for p in range(1, 4):
            steps += ['right', 'wait 60', 'tshot %d_p%d' % (n, p)]
        steps += ['b', 'wait 90']
    json.dump(steps, open(f'{out}/b{b}.json', 'w'))
    r = subprocess.run([PY, '-W', 'ignore', f'{T}/ds_tap.py', f'{out}/b{b}.json'], env=dict(os.environ, DS_ROM=rom, DS_OUT=out), capture_output=True, text=True, timeout=1500, cwd=out)
    print('batch', b, r.stdout.strip().splitlines()[-1:], flush=True)
    os.remove(rom)
