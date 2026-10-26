"""TEST ONLY: every trainer standing on the given maps (and the extra ids) becomes a single level-5 Magikarp in a copy of the ROM."""
import struct, sys
import ndspy.rom, ndspy.narc
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
maps = [int(v) for v in sys.argv[3].split(',')]; extra = {int(v) for v in sys.argv[4].split(',')} if len(sys.argv) > 4 else set()
ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')); tr = ndspy.narc.NARC(rom.getFileByName('a/0/5/5')); pa = ndspy.narc.NARC(rom.getFileByName('a/0/5/6'))
dd = rom.loadArm9().sections[0].data; recs = ext.records(rom)
ids = set(extra)
for m in maps:
    r = bytes(dd[TABLE + m * 24:TABLE + m * 24 + 24]) if m < 540 else recs[m - 540]
    for a in events_decode(ev.files[struct.unpack_from('<H', r, 16)[0]])[1]:
        s = struct.unpack_from('<H', a, 10)[0]
        if 3000 <= s < 4000: ids.add(s - 2999)
done = []
for t in sorted(ids):
    row = bytearray(tr.files[t]); n = row[3]
    if not n: continue
    blob = bytes(pa.files[t]); size = len(blob) // n; mon = bytearray(blob[:size]); struct.pack_into('<HH', mon, 2, 5, 129)
    pa.files[t] = bytes(mon); row[3] = 1; tr.files[t] = bytes(row); done.append(t)
rom.setFileByName('a/0/5/5', tr.save()); rom.setFileByName('a/0/5/6', pa.save()); rom.saveToFile(sys.argv[2]); print('easy trainers', done)
