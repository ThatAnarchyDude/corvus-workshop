"""TEST ONLY: vr_free.py <rom> <map id> prints a map's free tiles and actors. Importable: load(rom_path, mid) -> (free tiles, actors [(id, sprite, script, hide flag, (x, z))], event groups)."""
import struct, sys
import ndspy.rom, ndspy.narc
import map_header_extension as ext
from opening import events_decode

def load(path, mid):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    if mid >= ext.NATIVE_COUNT:
        r = bytearray(ext.records(rom)[mid - ext.NATIVE_COUNT])
    else:
        from viridian_tutorial import TABLE
        d = bytes(rom.loadArm9().sections[0].data)
        r = bytearray(d[TABLE + 24 * mid:TABLE + 24 * mid + 24])
    mat = bytes(mats.files[struct.unpack_from('<H', r, 4)[0]]); w, h, hd, ht, n = mat[:5]
    lid = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht)); free = set()
    for cz in range(h):
        for cx in range(w):
            if lid[cz * w + cx] == 0xFFFF: continue
            land = bytes(lands.files[lid[cz * w + cx]]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
            perm = land[16 + bgs:16 + bgs + 2048]
            for lz in range(32):
                for lx in range(32):
                    if not perm[(lz * 32 + lx) * 2 + 1] & 0x80: free.add((cx * 32 + lx, cz * 32 + lz))
    g = events_decode(events.files[struct.unpack_from('<H', r, 16)[0]])
    actors = [(struct.unpack_from('<H', a, 0)[0], struct.unpack_from('<H', a, 2)[0], struct.unpack_from('<H', a, 10)[0], struct.unpack_from('<H', a, 8)[0], tuple(struct.unpack_from('<2H', a, 24))) for a in g[1]]
    return free, actors, g

if __name__ == '__main__':
    free, actors, g = load(sys.argv[1], int(sys.argv[2]))
    print(len(free), 'free tiles')
    for a in actors: print(a)
    xs = sorted(set(x for x, z in free)); zs = sorted(set(z for x, z in free))
    print('x range', xs[0], xs[-1], 'z range', zs[0], zs[-1])
