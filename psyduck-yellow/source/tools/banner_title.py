"""The ROM's banner (the title shown by launchers and emulators) reads "Psyduck Yellow (BETA)" with "Corvus Workshop" as the publisher line (owner request 2026-10-28; it still said "Native interiors - 0028").

Usage: banner_title.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.rom
from ndspy import _common

TITLE = 'Psyduck Yellow (BETA)\nCorvus Workshop'      # two lines at least: the forwarder generator (YANBF) fails on a one-line title


def patch(rom):
    banner = bytearray(rom.iconBanner)
    text = TITLE.encode('utf-16le')
    for at in range(0x240, 0x840, 0x100):                # the six language titles
        banner[at:at + 0x100] = text + bytes(0x100 - len(text))
    struct.pack_into('<H', banner, 2, _common.crc16(banner[0x20:0x840]))
    rom.iconBanner = bytes(banner)
    return dict(title=TITLE)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
