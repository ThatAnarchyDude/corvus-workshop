"""TEST ONLY: strip parts of an extension map's event file. argv: in.nds out.nds map what (actors|ring|bg|arrivals)"""
import struct, sys
import ndspy.rom, ndspy.narc
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import map_header_extension as ext
from opening import events_decode, events_encode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); recs = ext.records(rom)
m, what = int(sys.argv[3]), sys.argv[4]
eid = struct.unpack_from('<H', recs[m - 540], 16)[0]
g = events_decode(ev.files[eid])
if what == 'actors': g[1] = []
elif what == 'ring': g[2] = g[2][:8]
elif what == 'bg': g[0] = []
elif what == 'arrivals': g[2] = g[2][8:]
elif what == 'all': g[0], g[1], g[2], g[3] = [], [], [], []
ev.files[eid] = events_encode(g)
rom.setFileByName('a/0/3/2', ev.save())
rom.saveToFile(sys.argv[2])
