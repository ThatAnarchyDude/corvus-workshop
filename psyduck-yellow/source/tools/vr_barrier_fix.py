"""Victory Road is as hard as Yellow's: the switch barriers sit on the steps Yellow's switches open, and 2F's blocking boulder is plugged (2026-10-28, owner request).

Why it was easy: the maps are rebuilt at twice Yellow's scale (one Yellow step = 2x2 tiles) but a boulder is still one tile, so it filled half of a corridor that is two tiles wide and the road could be walked without
moving one; and victoryroad_yellow.py put every barrier's rocks one step beside the steps Yellow's switch really opens, so no barrier blocked anything.
Yellow's data (pret/pokeyellow, with its walk grids, objects and warps) says which things matter: with the barriers closed the Indigo exit is reachable only through step (5,5) of 2F, where a boulder sits at the mouth
of a one-step corridor that is a dead end when pushed (it jams at the next wall); opening the first 2F barrier (the switch at step (1,16)) bypasses it. The other three switches only open shortcuts. So Yellow needs Strength and one
boulder pushed onto the first 2F switch.
Fix (no bigger boulders: an object is one tile and moves one tile per push):
 - every barrier gets rocks on all four tiles of each step Yellow opens (1F (9,12); 2F (7,8) and (7,9), and (23,14); 3F (7,10)), hidden by the same flag as before; the poll scripts are rebuilt with the new rock ids;
 - 2F's blocking boulder (tile (18,23)) gets three permanent rocks beside and behind it, (19,23), (18,22) and (19,22), so the pair fills the corridor and the boulder cannot be pushed (in Yellow it only jams).
With the walk grids of this build the reachability table then matches Yellow's exactly: blocked unless the first 2F barrier is open. Boulders reset when you leave a floor and come back, as in Yellow.

Usage: vr_barrier_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
import victoryroad_yellow as vr
from opening import actor, events_decode, events_encode, script_bank
from parcel_quest import split_bank

FIRST_FLOOR_MAP = 579                  # floor f is map 579 + f
OPENED = {1: {'b1': [(9, 12)]}, 2: {'b2a': [(7, 8), (7, 9)], 'b2b': [(23, 14)]}, 3: {'b3': [(7, 10)]}}      # steps Yellow's switches open (closed vs open walk grids)
PLUG = {2: [(19, 23), (18, 22), (19, 22)]}                  # permanent rocks around 2F's blocking boulder at (18, 23)
OLD_ROCKS = {1: 2, 2: 8, 3: 2}                              # rocks the barriers had before (asserted)
ROCK_SPRITE, BOULDER_SPRITE, BOULDER_SCRIPT = 85, 84, 10002


def floor_tiles(rom, floor):
    """The walkable tiles of a Victory Road floor, from the chunks' collision data."""
    mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    rec = ext.records(rom)[FIRST_FLOOR_MAP + floor - ext.NATIVE_COUNT]
    mat = bytes(mats.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    free = set()
    for i, lid in enumerate(ids):
        land = bytes(lands.files[lid])
        perm = land[20:20 + 2048]
        assert land[16:20] == bytes.fromhex('34120000')
        for lz in range(32):
            for lx in range(32):
                if not perm[(lz * 32 + lx) * 2 + 1] & 0x80:
                    free.add(((i % w) * 32 + lx, (i // w) * 32 + lz))
    return free


def patch(rom):
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    records = ext.records(rom)
    report = {}
    for floor in vr.NAMES:
        rec = records[FIRST_FLOOR_MAP + floor - ext.NATIVE_COUNT]
        eid, sid = struct.unpack_from('<H', rec, 16)[0], struct.unpack_from('<H', rec, 6)[0]
        groups = events_decode(events.files[eid])
        free = floor_tiles(rom, floor)
        flags = {key: vr.FLAGS[key] for key in OPENED[floor]}
        keep, removed = [], 0
        for a in groups[1]:
            sprite, script, flag = struct.unpack_from('<H', a, 2)[0], struct.unpack_from('<H', a, 10)[0], struct.unpack_from('<H', a, 8)[0]
            if (sprite, script) == (ROCK_SPRITE, 0) and flag in flags.values():
                removed += 1
                continue
            keep.append(a)
        assert removed == OLD_ROCKS[floor], (floor, removed)
        next_id = max(struct.unpack_from('<H', a, 0)[0] for a in keep) + 1
        boulders = [struct.unpack_from('<H', a, 0)[0] for a in keep if (struct.unpack_from('<H', a, 2)[0], struct.unpack_from('<H', a, 10)[0]) == (BOULDER_SPRITE, BOULDER_SCRIPT)]
        new, rock_ids = [], {}
        for key, steps in OPENED[floor].items():
            for sx, sz in steps:
                for dx in range(cf.SCALE):
                    for dz in range(cf.SCALE):
                        tile = (vr.OX + cf.SCALE * sx + dx, vr.OZ + cf.SCALE * sz + dz)
                        assert tile in free, (floor, key, tile)
                        new.append(actor(next_id, ROCK_SPRITE, 0, *tile, flags[key], 0))
                        rock_ids.setdefault(key, []).append(next_id)
                        next_id += 1
        for tile in PLUG.get(floor, []):
            assert tile in free and not any(struct.unpack_from('<2H', a, 24) == tile for a in keep), (floor, tile)
            new.append(actor(next_id, ROCK_SPRITE, 0, *tile, 0, 0))
            next_id += 1
        groups[1] = keep + new
        bank = split_bank(bytes(scripts.files[sid]))
        for key, (sx, sy), _, _ in vr.SWITCHES[floor]:
            x0, z0 = vr.OX + cf.SCALE * sx, vr.OZ + cf.SCALE * sy
            hits = [t for t in groups[3] if struct.unpack_from('<Hhh', t, 0)[1:] == (x0 - 1, z0 - 1)]
            assert len(hits) == 1, (floor, key, len(hits))
            script_id = struct.unpack_from('<H', hits[0], 0)[0]
            bank[script_id - 1] = vr.poll_switch(boulders, flags[key], x0, z0, rock_ids[key])
        scripts.files[sid] = script_bank(bank)
        events.files[eid] = events_encode(groups)
        report[floor] = dict(barrier_rocks={k: len(v) for k, v in rock_ids.items()}, plug_rocks=len(PLUG.get(floor, [])), removed=removed)
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/1/2', scripts.save())
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
