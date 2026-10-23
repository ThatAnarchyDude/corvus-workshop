"""Silph Co.: the first floor's door back to the lobby landed in a black 'Mystery Zone' (found by tools/audit_warps.py, 2026-10-23).

silph.py gave that warp (clone A = map 551, warp 0 at (11,14)) the destination anchor 8, but the lobby (map 402) has only two warps. The anchor must name a lobby warp: 1 is
the lobby's elevator landing (3,4), where the lobby's own elevator ride up started, so a player who goes back down arrives next to the elevator.

Usage: silph_exit_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode, events_encode

CLONE_A, LOBBY, WARP, BAD, GOOD = 551, 402, 0, 8, 1


def patch(rom):
    ov = rom.loadArm9Overlays()[ext.OV]
    start = ext.table_address(rom) - ov.ramAddress
    at = start + 24 * (CLONE_A - ext.NATIVE_COUNT)
    rec = bytearray(ov.data[at:at + 24])
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    eid = struct.unpack_from('<H', rec, 16)[0]
    g = events_decode(events.files[eid])
    w = bytearray(g[2][WARP])
    x, y, dest, anchor = struct.unpack_from('<4H', w, 0)
    assert (dest, anchor) == (LOBBY, BAD), (dest, anchor)
    struct.pack_into('<H', w, 6, GOOD)
    g[2][WARP] = bytes(w)
    events.files.append(events_encode(g))
    rom.setFileByName('a/0/3/2', events.save())
    new = len(events.files) - 1
    d = rom.loadArm9Overlays()
    ovs = d
    o = ovs[ext.OV]
    o.data = bytearray(o.data)
    struct.pack_into('<H', o.data, at + 16, new)
    rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(warp=(x, y), event_file=new)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
