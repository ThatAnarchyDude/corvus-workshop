"""The VS banner of Blue's battles reads BLUE, not GIOVANNI (found 2026-10-24, cause and fix 2026-10-27).

Problem: every battle against a trainer of class 110 (the rival class: the Champion, the Silph/Tower/Route fights, all records that use Blue's class) opens with the
VS banner (the "VS" logo and Blue's portrait), and the name on that banner read GIOVANNI. The banner does not use the opponent's own name. Overlay 115 keeps a table of
12-byte VS records {0x6000, 0x000D, trainer id, 0, trainer class, flag}, one per VS class, selected by the opponent's class, and builds the banner text from the name row
of the record's trainer id. The record for class 110 still names trainer 261 (HG's Viridian Gym leader Blue); kanto_gyms.py turned that trainer into Giovanni (class 124,
name GIOVANNI), so Blue's banner showed his name.
Fix: the record's trainer id (overlay 115 0x022604E0, a u16) becomes 742, the rival template record whose name row is BLUE (champion_blue.py copies the same row into the
Champion records), so the banner always matches the rival's battle name.
Not covered here: the Elite Four banners use five 8-byte records next to this table (classes 86, 87, 88, 89, 112 -> trainers 244..247, 418) and still read the old HG rows. ROM 0107's vs_banner_names.py fixes them and makes every banner name the trainer actually fought (this record stays as its fallback).

Usage: vs_banner_blue.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.rom

OVERLAY = 115
RECORD = 0x022604DC                # {0x6000, 0x000D, trainer id, 0, class, flag}
RIVAL_CLASS, OLD_ID, NEW_ID = 110, 261, 742


def patch(rom):
    ovs = rom.loadArm9Overlays()
    ov = ovs[OVERLAY]
    ov.data = bytearray(ov.data)
    at = RECORD - ov.ramAddress
    marker, tid, zero, cls, flag = struct.unpack_from('<IHHHH', ov.data, at)
    assert marker == 0x000D6000 and cls == RIVAL_CLASS, (hex(marker), cls)
    assert tid == OLD_ID, tid
    struct.pack_into('<H', ov.data, at + 4, NEW_ID)
    rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(record=hex(RECORD), trainer_id=f'{OLD_ID} -> {NEW_ID}')


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
