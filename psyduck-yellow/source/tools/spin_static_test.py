"""TEST ONLY: static check of spin-tile slides. argv: rom, map, yellow asm name, OX, OZ, pokeyellow source.
Every arrow cell must be free, every step of every slide must be free, and the slide must end on a free cell that is not itself an arrow cell."""
import sys, struct
import ndspy.rom, ndspy.narc
import map_header_extension as ext
import spin_tiles
from viridian_tutorial import TABLE
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); m = int(sys.argv[2]); OX, OZ = int(sys.argv[4]), int(sys.argv[5])
SC = 2
mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
r = ext.records(rom)[m - 540]
mat = bytes(mats.files[struct.unpack_from('<H', r, 4)[0]]); w, h, hd, ht, n = mat[:5]
ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht)); free = set()
for cz in range(h):
    for cx in range(w):
        land = bytes(lands.files[ids[cz * w + cx]]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
        perm = land[16 + bgs:16 + bgs + 2048]
        for lz in range(32):
            for lx in range(32):
                if not perm[(lz * 32 + lx) * 2 + 1] & 0x80: free.add((cx * 32 + lx, cz * 32 + lz))
tiles = spin_tiles.load(sys.argv[6], sys.argv[3])
arrow_cells = {(OX + SC * x + a, OZ + SC * y + b) for x, y in tiles for a in range(SC) for b in range(SC)}
D = {12: (0, -1), 13: (0, 1), 14: (-1, 0), 15: (1, 0)}
bad = 0
for (x, y), mv in sorted(tiles.items()):
    for a in range(SC):
        for b in range(SC):
            p = (OX + SC * x + a, OZ + SC * y + b)
            if p not in free: print('arrow cell blocked', (x, y), p); bad += 1; continue
            q = p
            for code, k in mv:
                for _ in range(k * SC):
                    q = (q[0] + D[code][0], q[1] + D[code][1])
                    if q not in free: print('slide hits wall', (x, y), p, q); bad += 1; break
                else: continue
                break
            else:
                if q in arrow_cells: print('ends on an arrow cell', (x, y), p, q); bad += 1
print(len(tiles), 'arrow tiles,', bad, 'problems')
