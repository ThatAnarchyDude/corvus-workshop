"""TEST ONLY: crash/black-screen sweep. For each map: build a throwaway fixture ROM that teleports to the map's first warp tile, boot it in DeSmuME (own process), and report
OK / CRASH (emulator died) / BLACK (top screen blank) plus the position read back.
Usage: sweep_maps.py <base.nds> <fixture .dsv> <workdir> <out.json> <worker> <workers> [map ids comma-separated]
"""
import json, os, struct, subprocess, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ndspy.rom, ndspy.narc
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE
import fixture_party
from PIL import Image

base, dsv, work, out, wi, wn = sys.argv[1:7]
wi, wn = int(wi), int(wn)
rom0 = ndspy.rom.NintendoDSRom.fromFile(base)
d = bytes(rom0.loadArm9().sections[0].data)
ev = ndspy.narc.NARC(rom0.getFileByName('a/0/3/2')).files
recs = [d[TABLE + 24 * m:TABLE + 24 * m + 24] for m in range(ext.NATIVE_COUNT)] + list(ext.records(rom0))
maps = [int(v) for v in sys.argv[7].split(',')] if len(sys.argv) > 7 else list(range(len(recs)))
maps = maps[wi::wn]
work = os.path.join(work, 'w%d' % wi); os.makedirs(work, exist_ok=True)
results = json.load(open(out)) if os.path.exists(out) else {}
for m in maps:
    if str(m) in results:
        continue
    try:
        g = events_decode(ev[struct.unpack_from('<H', recs[m], 16)[0]])
    except Exception:
        results[str(m)] = 'NOEVENTS'; continue
    if not g[2]:
        results[str(m)] = 'NOWARPS'; continue
    x, z = struct.unpack_from('<4H', g[2][0])[:2]
    rom = ndspy.rom.NintendoDSRom.fromFile(base)
    fixture_party.install(rom, 68, 0, 50, [], None, False, (m, x, z), False, None)
    p = os.path.join(work, 't.nds'); rom.saveToFile(p); shutil.copy(dsv, os.path.join(work, 't.dsv'))
    steps = os.path.join(work, 's.json'); json.dump(['wait 500', 'shot t', 'pos'], open(steps, 'w'))
    env = dict(os.environ, DS_ROM=p, DS_OUT=work, PYTHONPATH=os.path.dirname(os.path.abspath(__file__)))
    try:
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ds_tap.py'), steps], env=env, capture_output=True, text=True, timeout=600)
        status = 'OK' if r.returncode == 0 and 'done' in r.stdout else 'CRASH(%s)' % r.returncode
        pos = [l for l in r.stdout.splitlines() if l.startswith('pos')]
        if status == 'OK':
            im = Image.open(os.path.join(work, 't.png')).convert('L').crop((0, 0, 256, 192))
            if max(im.getdata()) < 20:
                status = 'BLACK'
        results[str(m)] = [status, pos[-1] if pos else '', (x, z)]
    except subprocess.TimeoutExpired:
        results[str(m)] = ['TIMEOUT', '', (x, z)]
    json.dump(results, open(out, 'w'))
    print(m, results[str(m)], flush=True)
