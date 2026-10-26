"""TEST ONLY: rewrite floor tiles (0,0) of every chunk of an extension map to (behavior, flags). argv: in.nds out.nds map behavior flags"""
import struct, sys
import ndspy.rom, ndspy.narc
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import map_header_extension as ext
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1')); lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5')); recs = ext.records(rom)
m, beh, fl = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
mat = bytes(mats.files[struct.unpack_from('<H', recs[m - 540], 4)[0]]); w, h, hd, ht, n = mat[:5]
ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
for i in ids:
    land = bytearray(lands.files[i]); bgs = 4 + struct.unpack_from('<H', land, 18)[0] if land[16:18] == b'\x34\x12' else 0
    base = 16 + bgs
    for k in range(1024):
        if land[base + 2 * k] == 0 and land[base + 2 * k + 1] == 0:
            land[base + 2 * k], land[base + 2 * k + 1] = beh, fl
    lands.files[i] = bytes(land)
rom.setFileByName('a/0/6/5', lands.save())
rom.saveToFile(sys.argv[2])
