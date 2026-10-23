"""Pokemon Tower floor item balls (Yellow's 3F-6F balls), added to the Tower floor clones built by pokemon_tower.py.

Yellow's balls: 3F Escape Rope; 4F Elixir, Awakening, HP Up; 5F Nugget; 6F Rare Candy, X Accuracy. Each goes on the accessible floor tile nearest Yellow's position
(shifted by the same (+5, +6) the trainers use), with at least three open neighbours and two tiles clear of every actor and warp. They vanish when picked up (hide flags in BALLS;
every flag was in no script or actor list of 0070).

Usage: tower_items.py <in.nds> <out.nds> <pokeyellow source>
"""
import re
import struct
import sys
from pathlib import Path
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
import pokemon_tower as PT
from forest_progression import pickup
from opening import actor, events_decode, events_encode, script_bank, encode_text
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

BALL_SPRITE = 87
OFFSET = (5, 6)
# floor -> [(item id, name, Yellow object label, hide flag)]
BALLS = {3: [(78, 'ESCAPE ROPE', 'POKEMONTOWER3F_ESCAPE_ROPE', 0xA1F)],
         4: [(40, 'ELIXIR', 'POKEMONTOWER4F_ELIXER', 0xA20), (21, 'AWAKENING', 'POKEMONTOWER4F_AWAKENING', 0xA23), (45, 'HP UP', 'POKEMONTOWER4F_HP_UP', 0xA24)],
         5: [(92, 'NUGGET', 'POKEMONTOWER5F_NUGGET', 0xA25)],
         6: [(50, 'RARE CANDY', 'POKEMONTOWER6F_RARE_CANDY', 0xA27), (60, 'X ACCURACY', 'POKEMONTOWER6F_X_ACCURACY', 0xA29)]}


def yellow_positions(source, floor):
    text = (Path(source) / 'data/maps/objects' / f'PokemonTower{floor}F.asm').read_text()
    out = {}
    for x, y, label in re.findall(r'object_event\s+(\d+),\s*(\d+),\s*SPRITE_POKE_BALL,\s*\w+,\s*\w+,\s*TEXT_(\w+),', text):
        out[label] = (int(x), int(y))
    return out


def patch(rom, source):
    flags = [f for balls in BALLS.values() for _, _, _, f in balls]
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    texts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    for v in flags:
        assert not any(struct.pack('<H', v) in bytes(raw) for raw in scripts.files), hex(v)
        assert not any(struct.pack('<H', v) in a for raw in events.files for g in events_decode(raw) for a in g), hex(v)
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    ovs = rom.loadArm9Overlays()
    ov = ovs[ext.OV]
    ov.data = bytearray(ov.data)
    start = ext.table_address(rom) - ov.ramAddress
    report = {}
    for floor, balls in BALLS.items():
        map_id = 540 + floor - 1                         # the Tower floor clones are the first seven extension records
        src = PT.SOURCES[floor - 1]
        at = start + 24 * (map_id - ext.NATIVE_COUNT)
        rec = bytearray(ov.data[at:at + 24])
        assert bytes(rec[4:6]) == bytes(ext.native_record(rom, src)[4:6]), map_id
        sid, tid, eid = struct.unpack_from('<H', rec, 6)[0], struct.unpack_from('<H', rec, 10)[0], struct.unpack_from('<H', rec, 16)[0]
        g = events_decode(events.files[eid])
        floor_tiles = PT._land(rom, src, d)
        occupied = {struct.unpack_from('<2H', a, 24) for a in g[1]} | {tuple(struct.unpack_from('<2H', w, 0)) for w in g[2]}
        seeds = {(x + dx, y + dy) for x, y in occupied for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))}
        accessible = PT._reachable(floor_tiles, seeds, set())
        if len(accessible) < 60:
            accessible = PT._largest_component(floor_tiles)
        yellow = yellow_positions(source, floor)
        bank = split_bank(scripts.files[sid])
        key, rows = decode_messages(texts.files[tid])
        if len(rows) >= 250:                                # HG points these floors at the shared battle-message bank, which their scripts never read
            assert all(struct.unpack_from('<H', bytes(scripts.files[sid]), k)[0] != 45 for k in range(0, len(scripts.files[sid]) - 1, 2)), map_id
            rows = []
        first_script, first_object = len(bank) + 1, max(struct.unpack_from('<H', a, 0)[0] for a in g[1]) + 1 if g[1] else 0
        placed = []
        for k, (item, name, label, flag) in enumerate(balls):
            desired = (yellow[label][0] + OFFSET[0], yellow[label][1] + OFFSET[1])
            cands = sorted((p for p in accessible
                            if sum((p[0] + dx, p[1] + dy) in floor_tiles for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3
                            and all(abs(p[0] - q[0]) + abs(p[1] - q[1]) >= 2 for q in occupied)),
                           key=lambda p: (abs(p[0] - desired[0]) + abs(p[1] - desired[1]), p))
            x, z = cands[0]
            occupied.add((x, z))
            message = len(rows)
            rows.extend(decode_messages(encode_text([f'{{PLAYER}} found {name}!', 'You have no room for this.'], PH))[1])
            assert len(rows) < 255
            bank.append(pickup(item, flag, message, first_object + k))
            g[1].append(actor(first_object + k, BALL_SPRITE, first_script + k, x, z, flag, 0))
            placed.append((name, (x, z), desired))
        scripts.files.append(script_bank(bank))
        texts.files.append(encode_messages(key, rows))
        events.files.append(events_encode(g))
        struct.pack_into('<H', rec, 6, len(scripts.files) - 1)
        struct.pack_into('<H', rec, 10, len(texts.files) - 1)
        struct.pack_into('<H', rec, 16, len(events.files) - 1)
        ov.data[at:at + 24] = rec
        report[floor] = placed
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.files[rom.filenames.idOf('a/0/2/7')] = texts.save()
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
