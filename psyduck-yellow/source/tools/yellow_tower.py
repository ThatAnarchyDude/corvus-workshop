"""Pokemon Tower laid out like Yellow's: seven rebuilt floors (3D walls and floor from the Yellow grid, matching collision) with warps, trainers, item balls and scenes on Yellow's coordinates.

Runs on top of the finished Tower build (tools/pokemon_tower.py, tower_scenes.py, tower_items.py, tower_look.py): floors are maps 540-546. For each floor yellow_floor.install() adds
a model/texture bank/collision grid; this module then rewrites the floor's event file (warps, actor positions, scene triggers) from pret/pokeyellow's object data.
Yellow step (x, y) = chunk tile (OX + x, OZ + y). Messages, trainers, flags and scripts are unchanged.

Usage: yellow_tower.py <in.nds> <out.nds> <pokeyellow source>
"""
import re
import struct
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
import yellow_floor as yf
from opening import actor, encode_text, events_decode, events_encode, script_bank, talk, Script, end
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
import yellow_text
from parcel_quest import split_bank
from viridian_tutorial import TABLE

LAVENDER, DOOR_ANCHOR, BASE = 53, 6, 540
BALL, TRAINER, RIVAL, FUJI_SPRITES = 87, 219, 375, (221, 222, 317)
MAPSEC_NAME, MAPSEC = 'Pokémon Tower', 70            # location-name row 70 of text bank 279 ("Old Chateau", unused here); the Tower floors used 205 = "Bell Tower"
FACE = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3, 'NONE': 1}
# Yellow's plain Pokemon Tower people: floor -> (step x, step y, HG sprite, facing, text file, label). Sprites are HeartGold's closest: receptionist 332, woman 320, old man 342, girl 319, Channeler 219.
NPCS = {
    1: [(15, 13, 332, 'UP', '_PokemonTower1FReceptionistText'), (6, 8, 320, 'NONE', '_PokemonTower1FMiddleAgedWomanText'),
        (8, 12, 342, 'NONE', '_PokemonTower1FBaldingGuyText'), (13, 7, 319, 'NONE', '_PokemonTower1FGirlText'),
        (17, 7, 219, 'LEFT', '_PokemonTower1FChannelerText')],
    2: [(3, 7, 219, 'RIGHT', '_PokemonTower2FChannelerText')],
    5: [(12, 8, 219, 'NONE', '_PokemonTower5FChanneler1Text')],
}
PURIFIED = (10, 8, 2, 2)                      # 5F: Yellow steps (10..11, 8..9) heal the party
PURIFIED_TEXT = '_PokemonTower5FPurifiedZoneText'
TEMP_VAR = 0x4000


def parse(source, floor):
    text = (Path(source) / f'data/maps/objects/PokemonTower{floor}F.asm').read_text()
    warps = [(int(a), int(b), c, int(d)) for a, b, c, d in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', text)]
    objs = []
    for line in re.findall(r'object_event\s+([^\n]+)', text):
        p = [x.strip() for x in line.split(',')]
        objs.append(dict(x=int(p[0]), y=int(p[1]), sprite=p[2], opp=len(p) > 6 and p[6].startswith('OPP_'), ball=p[2] == 'SPRITE_POKE_BALL'))
    return dict(warps=warps, trainers=[o for o in objs if o['opp']], balls=[o for o in objs if o['ball']], objs=objs)


def tile(x, y):
    """Top-left HeartGold tile of Yellow step (x, y); every step is SCALE x SCALE tiles."""
    return yf.OX + yf.SCALE * x, yf.OZ + yf.SCALE * y


def place(floor, x, y):
    """Global tile for something standing on Yellow step (x, y): the tile of its 2x2 block with the most open floor around it, preferring clear floor to the north
    (a standing sprite is drawn upward, so a wall just north of it looks like the person is stuck in the wall)."""
    kinds = yf.TK[floor]
    best = None
    for dz in (1, 0):
        for dx in (0, 1):
            tx, tz = yf.SCALE * x + dx, yf.SCALE * y + dz
            floor_at = lambda a, b: kinds.get((a, b)) == 'floor'
            score = (floor_at(tx, tz - 1) + floor_at(tx, tz - 2), sum(floor_at(tx + i, tz + j) for i in (-1, 0, 1) for j in (-1, 0, 1)), dz)
            if kinds.get((tx, tz)) == 'floor' and (best is None or score > best[0]):
                best = (score, tx, tz)
    assert best, (floor, x, y)
    return yf.OX + best[1], yf.OZ + best[2]


def patch(rom, source):
    data = {f: parse(source, f) for f in range(1, 8)}
    yf.WARPS = {f: [(w[0], w[1]) for w in d['warps']] for f, d in data.items()}
    yf.EXITS = {f: [(w[0], w[1]) for w in d['warps']] for f, d in data.items()}      # every warp tile gets the mat behaviour: plain tiles only fire when entered upward
    report = {}
    for f in range(1, 8):
        report[f] = yf.install(rom, source, f, BASE + f - 1)
    # events
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for f in range(1, 8):
        rec = bytes(o.data[start + 24 * (f - 1):start + 24 * f])
        eid = struct.unpack_from('<H', rec, 16)[0]
        g = events_decode(events.files[eid])
        d = data[f]
        raw0 = g[2][0]
        # Warp events: first one inert "arrival" event per Yellow warp (index = Yellow warp number; it is where the player lands, one step outside the ring),
        # then the ring tiles around each stair block / door mat that fire (behaviour 110, any direction) and send you to the destination's arrival event.
        warps = []
        for i, (x, y, dest, wid) in enumerate(d['warps']):
            ax, az = yf.ARRIVAL[f][i]
            warps.append(struct.pack('<4H', ax, az, BASE + f - 1, i) + raw0[8:])
        for tx, tz, behaviour, wi in yf.RING.get(f, []):
            x, y, dest, wid = d['warps'][wi]
            if dest == 'LAST_MAP':
                dmap, anchor = LAVENDER, DOOR_ANCHOR
            else:
                dmap, anchor = BASE + int(re.search(r'TOWER_(\d)F', dest).group(1)) - 1, wid - 1
            warps.append(struct.pack('<4H', tx, tz, dmap, anchor) + raw0[8:])
        g[2] = warps
        trainers, balls = iter(d['trainers']), iter(d['balls'])
        for i, a in enumerate(g[1]):
            b = bytearray(a)
            sprite = struct.unpack_from('<H', b, 2)[0]
            where = None
            if f == 2 and sprite == RIVAL:
                where = (14, 5)
                struct.pack_into('<h', b, 12, 1)                       # face down, toward the stairs' room
            elif sprite == TRAINER:
                t = next(trainers)
                where = (t['x'], t['y'])
            elif sprite == BALL:
                t = next(balls)
                where = (t['x'], t['y'])
            elif f == 7 and sprite in FUJI_SPRITES:
                where = {221: (10, 8), 222: (11, 8), 317: (10, 3)}[sprite]
            if where:
                struct.pack_into('<2H', b, 24, *place(f, *where))
            if struct.unpack_from('<H', b, 14)[0]:
                struct.pack_into('<H', b, 14, struct.unpack_from('<H', b, 14)[0] * yf.SCALE)       # sight range grows with the room
            g[1][i] = bytes(b)
        left = (len(list(trainers)), len(list(balls)))
        assert left == (0, 0), (f, left)
        triggers = {2: (14, 5, 2, 2), 6: (10, 16, 1, 1), 7: (9, 10, 3, 2)}
        if f in triggers:
            assert len(g[3]) == 1
            t = bytearray(g[3][0])
            struct.pack_into('<hhHH', t, 2, *tile(*triggers[f][:2]), triggers[f][2] * yf.SCALE, triggers[f][3] * yf.SCALE)
            g[3] = [bytes(t)]
        # Yellow's plain Tower people (and 5F's purified zone) get a fresh script bank and text bank of their own, written into the floor's header record
        if f in NPCS:
            off = start + 24 * (f - 1)
            sid, tid = struct.unpack_from('<H', ovd, off + 6)[0], struct.unpack_from('<H', ovd, off + 10)[0]
            bank = split_bank(bytes(scripts.files[sid]))
            key, rows = decode_messages(texts.files[tid])
            base_index = len(rows) if len(rows) < 200 else 0          # a per-floor bank keeps its rows; the shared battle bank is replaced by a fresh one
            rows = rows if base_index else []
            lines, new_scripts = [], []
            first_script = len(bank) + 1
            for x, y, spr, face, label in NPCS[f]:
                lines.append(yellow_text.message(source, f'PokemonTower{f}F', label))
                new_scripts.append(talk(base_index + len(lines) - 1))
                g[1].append(actor(len(g[1]), spr, first_script + len(new_scripts) - 1, *place(f, x, y), 0, FACE[face]))
            if f == 5:
                lines.append(yellow_text.message(source, 'PokemonTower5F', PURIFIED_TEXT))
                zone = Script().emit(96).msg(base_index + len(lines) - 1).emit(282).emit(41, TEMP_VAR, 1).emit(97).emit(2).finish()
                new_scripts.append(zone)
                zx, zz = tile(PURIFIED[0], PURIFIED[1])
                g[3].append(struct.pack('<Hhh5H', first_script + len(new_scripts) - 1, zx, zz, PURIFIED[2] * yf.SCALE, PURIFIED[3] * yf.SCALE, 0, 0, TEMP_VAR))
            for line in lines:
                rows.extend(decode_messages(encode_text([line], PH))[1])
            texts.files.append(encode_messages(key, rows))
            scripts.files.append(script_bank(bank + new_scripts))
            struct.pack_into('<H', ovd, off + 6, len(scripts.files) - 1)
            struct.pack_into('<H', ovd, off + 10, len(texts.files) - 1)
            report[f]['npcs'] = len(NPCS[f])
        ovd[start + 24 * (f - 1) + 18] = MAPSEC                           # location name "Pokemon Tower" instead of the Bell Tower's
        events.files[eid] = events_encode(g)
        report[f]['warps'] = d['warps']
    rom.setFileByName('a/0/3/2', events.save())
    key, names = decode_messages(texts.files[279])                          # location-name bank: row MAPSEC becomes "Pokemon Tower"
    names[MAPSEC] = decode_messages(encode_text([MAPSEC_NAME], PH))[1][0]
    texts.files[279] = encode_messages(key, names)
    rom.setFileByName('a/0/2/7', texts.save())
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # 6F ghost: the retreat walks the player back from (10,16): right two steps instead of up three
    rec6 = bytes(o.data[start + 24 * 5:start + 24 * 6])
    bank_id = struct.unpack_from('<H', rec6, 6)[0]
    blob = bytes(scripts.files[bank_id])
    old = struct.pack('<4H', 12, 3, 0xFE, 0)
    assert blob.count(old) == 1, blob.count(old)
    scripts.files[bank_id] = blob.replace(old, struct.pack('<4H', 15, 2 * yf.SCALE, 0xFE, 0))
    # Lavender -> Tower arrival (frame script on the Radio Tower interior, map 439): in front of Yellow's exit door, facing up
    d9 = rom.loadArm9().sections[0].data
    bank_439 = struct.unpack_from('<H', d9, TABLE + 439 * 24 + 6)[0]
    blob = bytes(scripts.files[bank_439])
    at = [i for i in range(len(blob) - 11) if blob[i:i + 6] == struct.pack('<3H', 176, BASE, 0)]
    assert len(at) == 1, at
    x, y = yf.ARRIVAL[1][0]                               # 1F's first door block: the arrival event's tile, one step above the ring
    blob = blob[:at[0] + 6] + struct.pack('<3H', x, y, 0) + blob[at[0] + 12:]
    scripts.files[bank_439] = blob
    rom.setFileByName('a/0/1/2', scripts.save())
    report['arrival'] = (x, y)
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
