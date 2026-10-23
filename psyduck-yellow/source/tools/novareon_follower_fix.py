"""Novareon's follower really uses its own recoloured model (found 2026-10-23: the follower in game was still Umbreon's colours).

novareon_follower.py borrowed the follower slot of species id 1560 (tag 4060, model file 1857) but redirected a call that Novareon never reaches: the starter Eevee
line's hooks (starter_eevee_line.py, 'field' and 'tag') first alias every starter-line species to its ordinary species through a table of 18 u16 values in overlay 129
([Vaporeon x2, Jolteon x2, Flareon x2, Espeon x2, Umbreon x2, Leafeon x2, Glaceon x2, Sylveon x2, Umbreon x2]); the last pair, Novareon and Mega Novareon, answered Umbreon.
They now answer 1560, so the follower is built from tag 4060 and the recoloured model.

Usage: novareon_follower_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.rom

BASES = (134, 135, 136, 196, 197, 470, 471, 750, 197)          # the line's ordinary species; the last is Novareon's Umbreon stand-in
FOLLOWER_SLOT = 1560


def patch(rom):
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    pattern = b''.join(struct.pack('<2H', b, b) for b in BASES)
    hits = []
    start = 0
    while True:
        at = bytes(perm.data).find(pattern, start)
        if at < 0:
            break
        hits.append(at)
        start = at + 1
    assert hits, hits
    for hit in hits:                                    # every copy of the table (the hooks chain through more than one)
        at = hit + 2 * 16
        assert struct.unpack_from('<2H', perm.data, at) == (197, 197)
        struct.pack_into('<2H', perm.data, at, FOLLOWER_SLOT, FOLLOWER_SLOT)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(tables=[hex(perm.ramAddress + h) for h in hits])


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
