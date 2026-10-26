"""TEST ONLY: set the sight range of every trainer actor on the given maps to 0 (no trigger battles), so a scripted walk can test geometry only. argv: in.nds out.nds map,map"""
import struct, sys
import ndspy.rom, ndspy.narc
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import map_header_extension as ext
from opening import events_decode, events_encode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); recs = ext.records(rom)
for m in (int(v) for v in sys.argv[3].split(',')):
    eid = struct.unpack_from('<H', recs[m - 540], 16)[0]
    g = events_decode(ev.files[eid])
    for i, a in enumerate(g[1]):
        if struct.unpack_from('<H', a, 10)[0] >= 3000:
            a = bytearray(a); struct.pack_into('<H', a, 14, 0); g[1][i] = bytes(a)
    ev.files[eid] = events_encode(g)
rom.setFileByName('a/0/3/2', ev.save())
rom.saveToFile(sys.argv[2])
