"""TEST ONLY: make a fixture ROM + save in a work dir. argv: src.nds workdir map x z [species level]. Env FIXTURE_BADGES / FIXTURE_FLAGS / FIXTURE_VARS as in fixture_party."""
import os
import shutil
import sys
import ndspy.rom
import fixture_party

SAVES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', '0040-release-v1', 'native-pickup-refreshed3')
src, work, mid, x, z = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
species, level = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (66, 29)
os.makedirs(work, exist_ok=True)
rom = ndspy.rom.NintendoDSRom.fromFile(src)
items = [(int(a), int(b)) for a, b in (p.split(':') for p in os.environ.get('FIXTURE_ITEMS', '').split(',') if p)]   # test-only: env FIXTURE_ITEMS=item:count,... ; FIXTURE_DEX=1 gives the Pokedex (shows POKEMON in the menu)
fixture_party.install(rom, species, int(os.environ.get('FIXTURE_HELD', '0'), 0), level, items, (tuple(int(v) for v in os.environ['FIXTURE_BATTLE'].split(',')) if os.environ.get('FIXTURE_BATTLE') else None), bool(os.environ.get('FIXTURE_DEX')), (mid, x, z), False, int(os.environ['FIXTURE_TRAINER']) if os.environ.get('FIXTURE_TRAINER') else None)       # env FIXTURE_TRAINER=id starts a battle against that trainer record
rom.saveToFile(os.path.join(work, 't.nds'))
dsv = [f for f in os.listdir(SAVES) if f.endswith('.dsv')][0]
shutil.copy(os.path.join(SAVES, dsv), os.path.join(work, 't.dsv'))
print('fixture ready in', work)
