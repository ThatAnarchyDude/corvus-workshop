"""Rock Tunnel laid out like Yellow's: two floors (1F, B1F) rebuilt from pret/pokeyellow's maps at 2x scale (cave_floor.py), joined to Route 10 (north and south).

Everything gameplay-side is reused from the existing build: the same trainer records and scripts (read back out of the old native maps 108/452, in Yellow's object order)
and the same wild tables. What changes is where things stand: Yellow's coordinates, Yellow's warps (ladders included). Yellow's Rock Tunnel has no item balls, so the old
HeartGold balls are dropped.

Usage: rocktunnel_yellow.py <in.nds> <out.nds> <pokeyellow source>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_floor as cf
import map_header_extension as ext
from opening import encode_text, events_decode, events_encode, script_bank, talk
from parcel_quest import PH
from viridian_tutorial import TABLE
from mtmoon_yellow import parse, FACE, TEX, MATS

OLD_1F, OLD_B1F = 108, 452
ROUTE10_NORTH, ROUTE10_SOUTH = 18, 388          # Route 10 (Pokemon Center side) and Route 10 (Lavender side)
FLOORS = [('RockTunnel1F', 20, 18, 3, 3, 8, 12), ('RockTunnelB1F', 20, 18, 3, 3, 8, 12)]
OLD_TRAINERS = {OLD_1F: range(2, 9), OLD_B1F: range(3, 11)}     # object ids of the old trainers, in Yellow's object order
SIGN = 'ROCK TUNNEL: CERULEAN CITY - LAVENDER TOWN'


def patch(rom, source):
    y = {name: parse(source, name) for name, *_ in FLOORS}
    main = rom.loadArm9()
    d = main.sections[0].data
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    old = {}
    for m in (OLD_1F, OLD_B1F):
        g = events_decode(events.files[struct.unpack_from('<H', d, TABLE + m * 24 + 16)[0]])
        old[m] = dict(actors={struct.unpack_from('<H', a, 0)[0]: bytes(a) for a in g[1]}, wild=d[TABLE + m * 24])
    templates = [ext.native_record(rom, OLD_1F), ext.native_record(rom, OLD_B1F)]
    ids = ext.install(rom, templates)
    report = {}
    for (name, W, H, CX, CZ, OX, OZ), mid in zip(FLOORS, ids):
        report[name] = cf.install(rom, source, name, mid, W, H, [(w[0], w[1]) for w in y[name]['warps']], OX, OZ, CX, CZ, 70, TEX, MATS, None)
    fid = dict(zip(('ROCK_TUNNEL_1F', 'ROCK_TUNNEL_B1F'), ids))
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    new_files = {}

    def warps_for(name):
        out, st = [], cf.STATE[name]
        for i, (x, yy, dest, wid) in enumerate(y[name]['warps']):
            ax, az = st['arrival'][i]
            out.append(struct.pack('<4H', ax, az, ids[[n for n, *_ in FLOORS].index(name)], i) + bytes(4))
        for tx, tz, beh, wi in st['ring']:
            x, yy, dest, wid = y[name]['warps'][wi]
            if dest == 'LAST_MAP':
                dmap, anchor = (ROUTE10_NORTH, 0) if wid == 2 else (ROUTE10_SOUTH, 0)
            else:
                dmap, anchor = fid[dest], wid - 1
            out.append(struct.pack('<4H', tx, tz, dmap, anchor) + bytes(4))
        return out

    for (name, *_), old_map in zip(FLOORS, (OLD_1F, OLD_B1F)):
        g, lines, bank = [[], [], [], []], [], []
        trainers = [o for o in y[name]['objs'] if o['opp']]
        assert len(trainers) == len(OLD_TRAINERS[old_map]), (name, len(trainers))
        for i, (o, obj) in enumerate(zip(trainers, OLD_TRAINERS[old_map])):
            a = bytearray(old[old_map]['actors'][obj])
            vision = struct.unpack_from('<H', a, 14)[0]
            struct.pack_into('<H', a, 0, i)
            struct.pack_into('<2H', a, 24, *cf.place(name, o['x'], o['y']))
            struct.pack_into('<h', a, 12, FACE[o['face']])
            struct.pack_into('<H', a, 14, vision * cf.SCALE)
            g[1].append(bytes(a))
        if name == 'RockTunnel1F':
            lines.append(SIGN)
            bank.append(talk(0))
            st = cf.STATE[name]
            bx, by = y[name]['bgs'][0]
            for ddx in range(cf.SCALE):
                for ddz in range(cf.SCALE):
                    g[0].append(struct.pack('<HHiiiH2x', 1, 0, st['OX'] + cf.SCALE * bx + ddx, st['OZ'] + cf.SCALE * by + ddz, 0, 4))
        lines = lines or ['...']
        bank = bank or [talk(0)]
        sid = len(scripts.files); scripts.files.append(script_bank(bank))
        iid = len(scripts.files); scripts.files.append(bytes(4))
        tid = len(texts.files); texts.files.append(encode_text(lines, PH))
        g[2] = warps_for(name)
        eid = len(events.files); events.files.append(events_encode(g))
        new_files[name] = dict(script=sid, init=iid, text=tid, event=eid, wild=old[old_map]['wild'])
    rom.setFileByName('a/0/1/2', scripts.save())
    rom.setFileByName('a/0/2/7', texts.save())
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    ovd = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for (name, *_), mid in zip(FLOORS, ids):
        at = start + 24 * (mid - ext.NATIVE_COUNT)
        nf = new_files[name]
        struct.pack_into('<3H', ovd, at + 6, nf['script'], nf['init'], nf['text'])
        struct.pack_into('<H', ovd, at + 16, nf['event'])
        ovd[at] = nf['wild']
    o.data = ovd
    rom.files[o.fileID] = o.save(compress=False)
    # ---- Route 10 (north and south) enter the new 1F
    rewired = {}
    for m, target, anchor in ((ROUTE10_NORTH, fid['ROCK_TUNNEL_1F'], 0), (ROUTE10_SOUTH, fid['ROCK_TUNNEL_1F'], 2)):
        eid = struct.unpack_from('<H', d, TABLE + m * 24 + 16)[0]
        g = events_decode(events.files[eid])
        hit = 0
        for i, wp in enumerate(g[2]):
            x, z, dest, anc = struct.unpack_from('<4H', wp)
            if dest == OLD_1F:
                g[2][i] = struct.pack('<4H', x, z, target, anchor) + bytes(wp[8:])
                hit += 1
        assert hit == 1, (m, hit)
        events.files.append(events_encode(g))
        struct.pack_into('<H', d, TABLE + m * 24 + 16, len(events.files) - 1)
        rewired[m] = (target, anchor)
    rom.setFileByName('a/0/3/2', events.save())
    rom.arm9 = main.save(compress=True)
    return dict(ids=ids, floors=report, files=new_files, rewired=rewired)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
