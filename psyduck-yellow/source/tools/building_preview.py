"""TEST ONLY: drop native building models onto a built floor to see them in game (preview before a real patch).
Usage: building_preview.py <in.nds> <out.nds> <map id> <model:tile x:tile z[:y]>[,...]   (tile x/z = the centre of the spot in global tiles, e.g. 67.5:20.5; y in tiles, default 0)
The model must be in the floor area's building set (a/0/4/3). Land chunk = tile // 32, building position = tile - chunk * 32 - 16 (tiles from the chunk centre), like cave_ladders.py."""
import struct
import sys
import ndspy.narc
import ndspy.rom
import cave_ladders as cl
import map_header_extension as ext

if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    mapid = int(sys.argv[3])
    specs = [s.split(':') for s in sys.argv[4].split(',')]
    mats_n = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    areas = ndspy.narc.NARC(rom.getFileByName('a/0/4/2'))
    sets = ndspy.narc.NARC(rom.getFileByName('a/0/4/3'))
    rec = ext.records(rom)[mapid - ext.NATIVE_COUNT]
    sid = struct.unpack_from('<H', areas.files[rec[1]], 0)[0]
    allowed = struct.unpack('<%dH' % (len(sets.files[sid]) // 2), bytes(sets.files[sid]))[1:]
    mat = bytes(mats_n.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    land_ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    for model, tx, tz, *y in specs:
        model, tx, tz = int(model), float(tx), float(tz)
        assert model in allowed, (model, 'not in the area building set', sid)
        cx, cz = int(tx) // cl.CHUNK, int(tz) // cl.CHUNK
        lid = land_ids[cz * w + cx]
        perm, blds, mdl, bdhc = cl.parse(bytes(lands.files[lid]))
        blds = bytes(blds) + cl.building(model, tx - cx * cl.CHUNK - cl.CHUNK / 2, float(y[0]) if y else 0.0, tz - cz * cl.CHUNK - cl.CHUNK / 2)
        lands.files[lid] = cl.pack(perm, blds, mdl, bdhc)
    rom.setFileByName('a/0/6/5', lands.save())
    rom.saveToFile(sys.argv[2])
    print('placed', specs)
