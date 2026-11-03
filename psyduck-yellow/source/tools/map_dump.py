"""TEST ONLY: dump one map's layout (collision, actors, bg events, warps, triggers) as text. Works for native and extension maps. Usage (from yellow-heartgold, PYTHONPATH=tools): map_dump.py <rom> <map_id> [map_id ...]"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE


def record(rom, mid):
    d = bytes(rom.loadArm9().sections[0].data)
    if mid < ext.NATIVE_COUNT:
        return d[TABLE + 24 * mid:TABLE + 24 * mid + 24]
    return bytes(ext.records(rom)[mid - ext.NATIVE_COUNT])


def free_tiles(rom, rec):
    mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    mat = bytes(mats.files[struct.unpack_from('<H', rec, 4)[0]])
    w, h, hd, ht, n = mat[:5]
    ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
    free, attr = set(), {}
    for cz in range(h):
        for cx in range(w):
            land = bytes(lands.files[ids[cz * w + cx]])
            bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
            perm = land[16 + bgs:16 + bgs + 2048]
            for lz in range(32):
                for lx in range(32):
                    o = (lz * 32 + lx) * 2
                    t = (cx * 32 + lx, cz * 32 + lz)
                    attr[t] = perm[o]
                    if not perm[o + 1] & 0x80:
                        free.add(t)
    return free, attr, (w, h)


def main(path, maps):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    for mid in maps:
        rec = record(rom, mid)
        matrix, script, level, text, eid = (struct.unpack_from('<H', rec, o)[0] for o in (4, 6, 8, 10, 16))
        free, attr, (mw, mh) = free_tiles(rom, rec)
        g = events_decode(ev.files[eid])
        print('=== map %d: matrix %d script file %d level script %d text %d event file %d; chunks %dx%d' % (mid, matrix, script, level, text, eid, mw, mh))
        marks = {}
        print('actors (id sprite move type flag script facing x z):')
        for a in g[1]:
            i, sp, mv, ty, fl, sc, fc = struct.unpack_from('<7H', a, 0)
            x, z = struct.unpack_from('<2H', a, 24)
            print('  %4d sprite %4d mv %2d ty %2d flag %5d script %5d face %d  at (%d,%d)' % (i, sp, mv, ty, fl, sc, fc, x, z))
            marks[(x, z)] = 'A'
        print('bg events (raw):')
        for b in g[0]:
            sc, = struct.unpack_from('<H', b, 0)
            print('  script %d  raw %s' % (sc, b.hex()))
            x, z = struct.unpack_from('<2i', b, 4)               # bg events: u32 script, i32 x, i32 z, ...
            marks.setdefault((x, z), 'B')
        print('warps (x z dest anchor):')
        for i, wp in enumerate(g[2]):
            x, z, dm, an = struct.unpack_from('<4H', wp, 0)
            print('  #%d (%d,%d) -> map %d anchor %d' % (i, x, z, dm, an))
            marks[(x, z)] = 'W'
        print('triggers (script x z w h var value):')
        for t in g[3]:
            sc, x, z, w, h, hz, var, val = struct.unpack_from('<HhhHHHHH', t, 0)
            print('  script %d at (%d,%d) %dx%d var %#x val %d' % (sc, x, z, w, h, var, val))
        xs = [t[0] for t in free] + [t[0] for t in marks]
        zs = [t[1] for t in free] + [t[1] for t in marks]
        x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
        print('grid x %d..%d z %d..%d  (. free, # blocked, A actor, B bg event, W warp)' % (x0, x1, z0, z1))
        print('     ' + ''.join(str((x // 10) % 10) if x % 10 == 0 else ' ' for x in range(x0, x1 + 1)))
        print('     ' + ''.join(str(x % 10) for x in range(x0, x1 + 1)))
        for z in range(z0, z1 + 1):
            row = ''.join(marks.get((x, z), '.' if (x, z) in free else '#') for x in range(x0, x1 + 1))
            print('%4d %s' % (z, row))


if __name__ == '__main__':
    main(sys.argv[1], [int(m) for m in sys.argv[2:]])
