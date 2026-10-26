"""TEST ONLY: poke bytes of an extension-map header record. argv: in.nds out.nds map offset=value,offset=value"""
import sys
import ndspy.rom
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import map_header_extension as ext
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
m = int(sys.argv[3])
o = rom.loadArm9Overlays({ext.OV})[ext.OV]
data = bytearray(o.data)
at = ext.table_address(rom) - o.ramAddress + 24 * (m - ext.NATIVE_COUNT)
for kv in sys.argv[4].split(','):
    k, v = kv.split('='); data[at + int(k)] = int(v, 0)
o.data = data
rom.files[o.fileID] = o.save(compress=False)
rom.saveToFile(sys.argv[2])
