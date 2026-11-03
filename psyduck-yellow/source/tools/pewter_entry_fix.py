"""Pewter City (map 51) no longer crashes the 3DS on the Route 2 -> Pewter border (owner's investigation 2026-11-01 + this check).
Cause: Pewter's entry script (level-script type 2, script 11 of bank a/0/1/2 file 1098) is `clearflag 0xB23; check_badge 8 -> VAR_RESULT(0x800C); compare VAR_RESULT,1; ... setvar 0x4146 = 0/1`.
VAR_RESULT is a special variable stored in the field's script environment, reached through fsys->taskman (fsys+0x10). While a map change is in progress that pointer can still be NULL (the 3DS' slower SD reads widen the window), so the read at 0x02050650 (`ldr r0,[r0,#0xC]`) aborts with ADDR 0000000C.
Fix: the badge result is stored in an ordinary save variable instead (the same 0x4146 the script sets afterwards; the final value is identical), so the script never touches the script environment. Only these two bytes pairs change.
Usage: pewter_entry_fix.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.narc
import ndspy.rom

FILE = 1098
EXPECT = bytes.fromhex('1f00230b260108000c8011000c8001001c00010c00000029004641000016000600000029004641010002' '00')
VAR_RESULT, VAR_SCENE = 0x800C, 0x4146


def patch(rom):
    fid = rom.filenames.idOf('a/0/1/2')
    narc = ndspy.narc.NARC(rom.files[fid])
    b = bytearray(narc.files[FILE])
    start = 4 * 10 + 4 + struct.unpack_from('<I', b, 40)[0]                 # script 11
    assert bytes(b[start:start + len(EXPECT)]) == EXPECT, 'Pewter entry script is not the expected one'
    for at in (start + 8, start + 12):                                       # check_badge destination, compare variable
        assert struct.unpack_from('<H', b, at)[0] == VAR_RESULT
        struct.pack_into('<H', b, at, VAR_SCENE)
    narc.files[FILE] = bytes(b)
    rom.files[fid] = narc.save()


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
    print('wrote', sys.argv[2])
