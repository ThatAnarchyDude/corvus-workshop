"""TEST ONLY: live gate check on Mansion 1F with the switch at 0. argv: rom, workdir, dsv. Warps beside a closed gate and an open one, steps into each, reports the end position."""
import sys, os, json, subprocess, shutil
import ndspy.rom
import fixture_party
import mansion_yellow as my
OX, OZ, SC = 18, 20, 2
rom0, work, dsv = sys.argv[1:4]
os.makedirs(work, exist_ok=True)
cases = []
for by, bx, closed in my.GATES[1]:
    x0, z0 = OX + SC * 2 * bx, OZ + SC * 2 * by
    cases.append(((bx, by, closed), (x0 - 1, z0 + 1), 'right', (x0 + 1, z0 + 1)))       # beside the block on its west side, step east
    cases.append(((bx, by, closed), (x0 + 1, z0 - 1), 'down', (x0 + 1, z0 + 1)))        # above it, step south
for gate, start, key, inside in cases:
    rom = ndspy.rom.NintendoDSRom.fromFile(rom0)
    fixture_party.install(rom, 68, 0, 50, [], None, False, (575, start[0], start[1]), False, None)
    rom.saveToFile(os.path.join(work, 't.nds')); shutil.copy(dsv, os.path.join(work, 't.dsv'))
    json.dump(['wait 500', 'pos', key, 'wait 200', 'pos', key, 'wait 200', 'pos', key, 'wait 200', 'pos'], open(os.path.join(work, 's.json'), 'w'))
    env = dict(os.environ, DS_ROM=os.path.join(work, 't.nds'), DS_OUT=work)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ds_tap.py'), os.path.join(work, 's.json')], env=env, capture_output=True, text=True, timeout=300)
    print(gate, 'from', start, key, [l for l in r.stdout.splitlines() if l.startswith('pos')], flush=True)
