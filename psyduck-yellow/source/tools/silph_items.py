"""Silph Co. floor item balls (Yellow's 3F-10F balls), added to the four floor clones built by silph.py.

Each clone holds the item balls of the Yellow floors it stands in for (silph.GROUPS). Two balls are left out: TM09 Take Down (this ROM has
no Take Down TM) and the Card Key (the clones have no Card Key doors to open). Balls stand on floor tiles off the entrance-to-elevator route,
two tiles clear of everything else on the floor, and disappear when picked up (hide flags in BALLS; the pickup script is the cave pickup's).

Usage: silph_items.py <in.nds> <out.nds>
"""
import json
import struct
import sys
from pathlib import Path
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
import rocket_hideout as rh
from forest_progression import pickup
from opening import actor, events_decode, events_encode, script_bank, encode_text
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages

CLONES = {1: 551, 2: 552, 3: 553, 4: 554}        # silph.py's clones in order (A..D)
LOBBY = 402
TILES = {tuple(t) for t in json.loads((Path(__file__).resolve().parents[1] / 'data/silph402-tiles.json').read_text())['tiles']}
DOOR, ELEVATOR = (11, 13), (3, 3)
BALL_SPRITE = 87                                  # the item-ball sprite used by the cave pickups
# clone -> (item id, name, hide flag): flags 0xA38-0xA61 were in no script or actor list in 0056
BALLS = {1: [(25, 'HYPER POTION', 0xA5B), (27, 'FULL HEAL', 0xA5C), (29, 'MAX REVIVE', 0xA5F), (78, 'ESCAPE ROPE', 0xA61)],
         2: [(46, 'PROTEIN', 0xA45), (45, 'HP UP', 0xA44), (60, 'X ACCURACY', 0xA43)],
         3: [(49, 'CALCIUM', 0xA3F), (402, 'TM75 (SWORDS DANCE)', 0xA3D)],
         4: [(353, 'TM26 (EARTHQUAKE)', 0xA3C), (50, 'RARE CANDY', 0xA39), (48, 'CARBOS', 0xA38)]}


def scatter(route, count, taken):
    """Floor tiles off the route, two tiles from anything in `taken` and three from the door and elevator, spread by distance from the door."""
    on_route = set(route)
    ring = sorted(TILES, key=lambda p: (abs(p[0] - DOOR[0]) + abs(p[1] - DOOR[1]), p))
    spots = []
    for k in range(count):
        target = ring[(k + 1) * len(ring) // (count + 1)]
        free = [p for p in ring if p not in on_route and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 2 for q in taken)
                and abs(p[0] - DOOR[0]) + abs(p[1] - DOOR[1]) >= 3 and abs(p[0] - ELEVATOR[0]) + abs(p[1] - ELEVATOR[1]) >= 3]
        p = min(free, key=lambda p: (abs(p[0] - target[0]) + abs(p[1] - target[1]), p))
        spots.append(p)
        taken.add(p)
    return spots


def patch(rom):
    flags = [f for balls in BALLS.values() for _, _, f in balls]
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    texts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    for v in flags:                                # fresh in every script and actor list of this ROM
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for g in events_decode(raw) for a in g), hex(v)
    ovs = rom.loadArm9Overlays()
    ov = ovs[ext.OV]
    ov.data = bytearray(ov.data)
    start = ext.table_address(rom) - ov.ramAddress
    route = rh.bfs(DOOR, ELEVATOR, TILES)
    report = {}
    for n, map_id in CLONES.items():
        at = start + 24 * (map_id - ext.NATIVE_COUNT)
        rec = bytearray(ov.data[at:at + 24])
        sid, tid, eid = struct.unpack_from('<H', rec, 6)[0], struct.unpack_from('<H', rec, 10)[0], struct.unpack_from('<H', rec, 16)[0]
        g = events_decode(events.files[eid])
        assert rec[0] == 255 and any(struct.unpack_from('<2H', w, 0) == (3, 4) or struct.unpack_from('<2H', w, 0) == (11, 14) for w in g[2]), map_id
        taken = {DOOR, ELEVATOR, (3, 4), (11, 14)}
        taken |= {struct.unpack_from('<2H', a, 24) for a in g[1]}
        taken |= {tuple(struct.unpack_from('<2h', t, 2)) for t in g[3]}
        bank = split_bank(scripts.files[sid])
        key, rows = decode_messages(texts.files[tid])
        first_script, first_object = len(bank) + 1, len(g[1])
        spots = scatter(route, len(BALLS[n]), taken)
        for k, ((item, name, flag), (x, z)) in enumerate(zip(BALLS[n], spots)):
            message = len(rows)
            rows.extend(decode_messages(encode_text([f'{{PLAYER}} found {name}!', 'You have no room for this.'], PH))[1])
            assert len(rows) < 255
            bank.append(pickup(item, flag, message, first_object + k))
            g[1].append(actor(first_object + k, BALL_SPRITE, first_script + k, x, z, flag, 0))
        scripts.files.append(script_bank(bank))
        texts.files.append(encode_messages(key, rows))
        events.files.append(events_encode(g))
        struct.pack_into('<H', rec, 6, len(scripts.files) - 1)
        struct.pack_into('<H', rec, 10, len(texts.files) - 1)
        struct.pack_into('<H', rec, 16, len(events.files) - 1)
        ov.data[at:at + 24] = rec
        report[n] = dict(map=map_id, balls=[(name, spot) for (_, name, _), spot in zip(BALLS[n], spots)])
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.files[rom.filenames.idOf('a/0/2/7')] = texts.save()
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(json.dumps(patch(rom), indent=1))
    rom.saveToFile(sys.argv[2])
