"""Fly points on map entry: give New Bark Town's entry its own map back (owner 2026-11-03: New Bark's Fly point must not be available at the start; Pallet Town's should be).
The engine's fly-point-on-entry table (ARM9 0x020F9E80, 30 entries of 0x12 bytes: halfword 0 = Fly point index in the low byte and bit 9 = "set it", halfword 3 at +6 = map id) has, since the 0037 engine build, entry 0 (Fly point 11 = New Bark Town) on map 49 = Pallet Town
instead of HeartGold's map 60 (New Bark Town). Walking into Pallet therefore set New Bark's flag 0x9BB, and the function returns after the FIRST match, so Pallet's own entry (entry 12, map 49, Fly point 0) was never reached: Pallet could not be a Fly destination.
Fix: entry 0's map id goes back to 60 (checked against the original HeartGold table). New Bark's Fly point is then set by entering the real New Bark Town (or by Elm's call), Pallet's by entering Pallet.
Usage (from yellow-heartgold, PYTHONPATH=tools): fly_point_table_fix.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.rom

TABLE = 0x020F9E80
STRIDE = 0x12
NEW_BARK_MAP = 60


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    base = TABLE - main.sections[0].ramAddress
    e0, e12 = base, base + 12 * STRIDE
    assert d[e0] == 11 and (d[e0 + 1] >> 1) & 1 and struct.unpack_from('<H', d, e0 + 6)[0] == 49, 'entry 0 is not New Bark (Fly point 11) on map 49'
    assert d[e12] == 0 and (d[e12 + 1] >> 1) & 1 and struct.unpack_from('<H', d, e12 + 6)[0] == 49, 'entry 12 is not Pallet (Fly point 0) on map 49'
    struct.pack_into('<H', d, e0 + 6, NEW_BARK_MAP)
    rom.arm9 = main.save(compress=True)
    return dict(entry0_map=NEW_BARK_MAP)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
