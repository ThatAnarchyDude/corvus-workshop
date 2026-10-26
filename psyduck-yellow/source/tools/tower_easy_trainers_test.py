"""TEST ONLY: make every Pokemon Tower trainer a single level-5 Magikarp in a copy of the ROM so a scripted climb can win each fight in one hit."""
import struct, sys
import ndspy.rom, ndspy.narc
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import map_header_extension as ext
from opening import events_decode
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); recs = ext.records(rom)
tr = ndspy.narc.NARC(rom.getFileByName('a/0/5/5')); pa = ndspy.narc.NARC(rom.getFileByName('a/0/5/6'))
ids = set(range(856, 861))
for f in range(7):
    g = events_decode(ev.files[struct.unpack_from('<H', recs[f], 16)[0]])
    for a in g[1]:
        s = struct.unpack_from('<H', a, 10)[0]
        if 3000 <= s < 4000:
            ids.add(s - 2999)
done = []
for t in sorted(ids):
    row = bytearray(tr.files[t]); n = row[3]
    if not n: continue
    blob = bytes(pa.files[t]); size = len(blob) // n
    mon = bytearray(blob[:size])
    struct.pack_into('<HH', mon, 2, 5, 129)
    pa.files[t] = bytes(mon); row[3] = 1; tr.files[t] = bytes(row); done.append(t)
rom.setFileByName('a/0/5/5', tr.save()); rom.setFileByName('a/0/5/6', pa.save())
rom.saveToFile(sys.argv[2]); print('easy trainers', done)
