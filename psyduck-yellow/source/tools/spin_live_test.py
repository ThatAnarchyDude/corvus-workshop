"""TEST ONLY: live spin-tile check. argv: rom, map, yellow asm, OX, OZ, source, workdir, dsv, count. Picks arrow tiles with a free non-arrow neighbour, warps next to each, steps onto it, compares the end position."""
import sys, os, struct, json, subprocess, shutil
import ndspy.rom, ndspy.narc
import map_header_extension as ext
import spin_tiles, fixture_party
rom0, m, asm, OX, OZ, src, work, dsv, count = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], sys.argv[7], sys.argv[8], int(sys.argv[9])
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spin_static_test.py')).read().split("tiles = spin_tiles.load")[0].replace("sys.argv[1]", "rom0").replace("int(sys.argv[2])", "m").replace("int(sys.argv[4]), int(sys.argv[5])", "OX, OZ"))
tiles = spin_tiles.load(src, asm)
D = {12: (0, -1), 13: (0, 1), 14: (-1, 0), 15: (1, 0)}
KEY = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
arrow = {(OX + SC * x + a, OZ + SC * y + b) for x, y in tiles for a in range(SC) for b in range(SC)}
cases = []
for (x, y), mv in sorted(tiles.items()):
    p = (OX + SC * x, OZ + SC * y)
    for d, k in KEY.items():
        s = (p[0] - d[0], p[1] - d[1])
        if s in free and s not in arrow:
            q = p
            for code, n in mv:
                q = (q[0] + D[code][0] * n * SC, q[1] + D[code][1] * n * SC)
            cases.append(((x, y), s, k, q)); break
step = max(1, len(cases) // count); cases = cases[::step][:count]
os.makedirs(work, exist_ok=True)
for (xy, s, k, q) in cases:
    rom = ndspy.rom.NintendoDSRom.fromFile(rom0)
    fixture_party.install(rom, 68, 0, 50, [], None, False, (m, s[0], s[1]), False, None)
    rom.saveToFile(os.path.join(work, 't.nds')); shutil.copy(dsv, os.path.join(work, 't.dsv'))
    json.dump(['wait 500', 'pos', k, 'wait 200', 'pos', 'wait 200', 'pos'], open(os.path.join(work, 's.json'), 'w'))
    env = dict(os.environ, DS_ROM=os.path.join(work, 't.nds'), DS_OUT=work, PYTHONPATH=os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ds_tap.py'), os.path.join(work, 's.json')], env=env, capture_output=True, text=True, timeout=300)
    pos = [l for l in r.stdout.splitlines() if l.startswith('pos')]
    print(xy, 'from', s, k, 'expect', q, '->', pos[-1] if pos else r.returncode, flush=True)
