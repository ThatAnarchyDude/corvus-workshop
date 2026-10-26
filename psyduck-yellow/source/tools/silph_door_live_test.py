"""TEST ONLY: live Card Key door check on chosen Silph floors. argv: rom, workdir, dsv, floors (e.g. 3,6,9). For the first door of each floor: approach from the north without the key (must be turned back), then with the key (Bingo, then through)."""
import sys, os, json, subprocess, shutil, struct
import ndspy.rom, ndspy.narc
import map_header_extension as ext
import fixture_party
from opening import events_decode
rom0, work, dsv, floors = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(',')]
os.makedirs(work, exist_ok=True)
base = ndspy.rom.NintendoDSRom.fromFile(rom0)
ev = ndspy.narc.NARC(base.getFileByName('a/0/3/2'))
recs = ext.records(base)
def run(m, start, steps, items):
    rom = ndspy.rom.NintendoDSRom.fromFile(rom0)
    fixture_party.install(rom, 68, 0, 50, items, None, False, (m, start[0], start[1]), False, None)
    rom.saveToFile(os.path.join(work, 't.nds')); shutil.copy(dsv, os.path.join(work, 't.dsv'))
    json.dump(steps, open(os.path.join(work, 's.json'), 'w'))
    env = dict(os.environ, DS_ROM=os.path.join(work, 't.nds'), DS_OUT=work)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ds_tap.py'), os.path.join(work, 's.json')], env=env, capture_output=True, text=True, timeout=300)
    return [l for l in r.stdout.splitlines() if l.startswith('pos')]
for f in floors:
    m = 564 + f - 1
    g = events_decode(ev.files[struct.unpack_from('<H', recs[m - ext.NATIVE_COUNT], 16)[0]])
    doors = [struct.unpack_from('<Hhh5H', t) for t in g[3] if struct.unpack_from('<Hhh5H', t)[3:5] == (4, 2)]
    entry, x, z = doors[0][:3]
    start = (x + 1, z - 1)
    print('floor', f, 'door', (x, z), 'of', len(doors), 'no key:', run(m, start, ['wait 500', 'pos', 'down', 'wait 300', 'a', 'wait 100', 'a', 'wait 300', 'pos'], []), flush=True)
    print('floor', f, 'with key:', run(m, start, ['wait 500', 'pos', 'down', 'wait 200', 'a', 'wait 100', 'a', 'wait 100', 'a', 'wait 300', 'a', 'wait 300', 'a', 'wait 300', 'down', 'down', 'wait 200', 'pos', 'down', 'wait 200', 'pos'], [(876, 1)]), flush=True)
