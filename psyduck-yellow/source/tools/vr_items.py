"""Victory Road item balls (Yellow's 1F-3F balls), placed in the parts of HG's three caves that can be reached on foot.

Yellow's balls: 1F TM Sky Attack, Rare Candy; 2F TM Submission, Full Heal, TM Mega Kick, Guard Spec; 3F Max Revive, TM Explosion. This ROM has no
Sky Attack, Submission or Mega Kick TM, so those three are left out. Balls go on reachable tiles (data/vr*.json) whose removal leaves every other reachable tile
reachable, two tiles clear of every actor and warp, spread by distance from the arrival tile; they vanish when picked up (hide flags in BALLS).

Usage: vr_items.py <in.nds> <out.nds>
"""
import json
import struct
import sys
from pathlib import Path
import ndspy.rom
from forest_progression import pickup
from map_edit import MapEdit
from opening import actor, events_decode
from viridian_tutorial import TABLE

DATA = Path(__file__).resolve().parents[1] / 'data'
BALL_SPRITE = 87
# map -> arrival tile, [(item id, name, hide flag)]; the flags were in no script or actor list of 0063
BALLS = {124: ((46, 58), [(50, 'RARE CANDY', 0xA37)]),
         178: ((8, 31), [(27, 'FULL HEAL', 0xA35), (55, 'GUARD SPEC.', 0xA31)]),
         179: ((38, 15), [(29, 'MAX REVIVE', 0xA30), (391, 'TM64 (EXPLOSION)', 0xA2F)])}
STEPS = ((0, -1), (0, 1), (-1, 0), (1, 0))
# Moltres: Victory Road 2F, Lv50 static battle at the far end of the reachable cave. The engine's own Moltres overworld sprite (1026, used by its existing static Moltres) is used.
MOLTRES = dict(map=178, species=146, level=50, sprite=1026, flag=0xA2D, text='Gyaoo!')


def connected(tiles, start):
    seen, queue = {start}, [start]
    for c in queue:
        for dx, dz in STEPS:
            n = (c[0] + dx, c[1] + dz)
            if n in tiles and n not in seen:
                seen.add(n)
                queue.append(n)
    return seen


def choose(tiles, entry, taken, count):
    dist = {}
    queue = [entry]
    dist[entry] = 0
    for c in queue:
        for dx, dz in STEPS:
            n = (c[0] + dx, c[1] + dz)
            if n in tiles and n not in dist:
                dist[n] = dist[c] + 1
                queue.append(n)
    ring = sorted(dist, key=lambda p: (dist[p], p))
    spots = []
    for k in range(count):
        target = ring[(k + 1) * len(ring) // (count + 1)]
        free = [p for p in ring if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 2 for q in taken) and abs(p[0] - entry[0]) + abs(p[1] - entry[1]) >= 4]
        for p in sorted(free, key=lambda p: (abs(p[0] - target[0]) + abs(p[1] - target[1]), p)):
            if len(connected(tiles - {p}, entry)) == len(tiles) - 1:        # the ball must not wall off any reachable tile
                spots.append(p)
                taken.add(p)
                tiles = tiles - {p}
                break
        else:
            raise RuntimeError('no tile for a ball')
    return spots


def moltres_script(message):
    from opening import Script, end
    s = Script().emit(96).msg(message)
    s.emit(589, MOLTRES['species'], MOLTRES['level'])
    s.data.append(0)
    s.emit(220, 0x800C).compare(0x800C, 1).jump('stays', 1)           # lost or ran: it stays
    s.emit(30, MOLTRES['flag']).emit(101, MOLTRES['object'])             # won or caught: gone for good
    end(s)
    s.label('stays')
    return end(s).finish()


def patch(rom):
    report = {}
    flags = [f for _, balls in BALLS.values() for _, _, f in balls] + [MOLTRES['flag']]
    import ndspy.narc
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    for v in flags:
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for g in events_decode(raw) for a in g), hex(v)
    for map_id, (entry, balls) in BALLS.items():
        tiles = {tuple(t) for f in DATA.glob(f'vr{map_id}-*.json') for t in json.loads(f.read_text())['tiles']}
        edit = MapEdit(rom, map_id)
        if len(edit.rows) >= 255:                    # HG points these caves at the shared battle-message bank, which their one empty script never reads
            assert all(struct.unpack_from('<H', edit.bank, k)[0] != 45 for k in range(0, len(edit.bank) - 1, 2)), map_id      # no message command in its scripts
            edit.rows = edit.rows[:0]
        taken = {struct.unpack_from('<2h', a, 24) for a in edit.groups[1]} | {entry}
        taken |= {tuple(struct.unpack_from('<2H', w, 0)) for w in edit.groups[2]}
        spots = choose(tiles, entry, taken, len(balls))
        obj = max(struct.unpack_from('<H', a, 0)[0] for a in edit.groups[1]) + 1
        for k, ((item, name, flag), (x, z)) in enumerate(zip(balls, spots)):
            found = edit.message(f'{{PLAYER}} found {name}!')
            edit.message('You have no room for this.')
            sid = edit.script(lambda msg, item=item, flag=flag, found=found, o=obj + k: pickup(item, flag, found, o))
            edit.groups[1].append(actor(obj + k, BALL_SPRITE, sid, x, z, flag, 0))
        if map_id == MOLTRES['map']:
            rest = tiles - set(spots)
            far = sorted(rest, key=lambda p: (-(abs(p[0] - entry[0]) + abs(p[1] - entry[1])), p))
            mx, mz = next(p for p in far if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 2 for q in taken)
                          and len(connected(rest - {p}, entry)) == len(rest) - 1)
            MOLTRES['object'] = obj + len(balls)
            text = edit.message(MOLTRES['text'])
            sid = edit.script(lambda msg: moltres_script(text))
            edit.groups[1].append(actor(MOLTRES['object'], MOLTRES['sprite'], sid, mx, mz, MOLTRES['flag'], 0))
            spots = spots + [(mx, mz)]
            balls = balls + [(0, 'MOLTRES', 0)]
        edit.save()
        report[map_id] = [(name, spot) for (_, name, _), spot in zip(balls, spots)]
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(json.dumps(patch(rom)))
    rom.saveToFile(sys.argv[2])
