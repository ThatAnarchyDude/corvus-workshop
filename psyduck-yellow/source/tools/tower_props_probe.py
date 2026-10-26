"""Probe: append pillar models (building id 65) to Tower 1F's land data at given tiles, to learn the position mapping. Test only.
Usage: tower_props_probe.py <in.nds> <out.nds> <tile x,z> ..."""
import struct, sys
import ndspy.narc, ndspy.rom
LAND = 437
def add(rom, model, tiles, y=0):
    lands = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
    L = bytearray(lands.files[LAND])
    ps, bs, ms, bd = struct.unpack_from('<4I', L, 0)
    bmd = L.find(b'BMD0')
    new = b''.join(struct.pack('<I3i3i3i2i', model, int((x + .5 - 16) * 16 * 4096), y * 4096, int((z + .5 - 16) * 16 * 4096), 0, 0, 0, 4096, 4096, 4096, 0, 0) for x, z in tiles)
    L[bmd:bmd] = new
    struct.pack_into('<I', L, 4, bs + len(new))
    lands.files[LAND] = bytes(L)
    rom.files[rom.filenames.idOf('a/0/6/5')] = lands.save()
if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    import os; add(rom, int(os.environ.get('MODEL', 65)), [tuple(int(v) for v in a.split(',')) for a in sys.argv[3:]])
    rom.saveToFile(sys.argv[2])
