"""Ordinary (non-starter) Novareon = species id 500 (owner 2026-11-01: "there IS already a non-starter Novareon").

Row 500 was Novareon's Pokedex identity (dex_novareon_id500.py copied only the data the Pokedex reads); starter Novareon (1581) changed since (abilities, level-up list, TM row...).
Here row 500 becomes a full copy of 1581 in every per-species table, it has no Mega and no evolution, ordinary Eevee (133) gets the Stellar Sandwich row (7, 3143 -> 500), and the Novareon follower
wrapper (overlay 129, compares the species with 1581 and 1582) answers for 500 instead of the Mega's 1582 (a Mega is never a follower).
Keep row 500 in step with 1581 whenever Novareon's data changes (abilities, stats). No new species row is used.
Usage (from yellow-heartgold, PYTHONPATH=tools): novareon_ordinary.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom

ORDINARY, STARTER, MEGA = 500, 1581, 1582
EEVEE, STELLAR_SANDWICH = 133, 3143
FOLLOWER_LITERAL = 0x023DF5D8


def patch(rom):
    ns = {}

    def narc(name):
        if name not in ns:
            ns[name] = ndspy.narc.NARC(rom.getFileByName(name))
        return ns[name]
    for name, stride, prefix in (('a/0/0/2', 1, 0), ('a/0/0/4', 6, 0), ('a/0/0/5', 4, 0), ('a/0/2/0', 1, 7), ('a/1/4/1', 1, 0), ('a/0/6/9', 1, 0), ('a/2/5/6', 1, 0), ('a/2/4/8', 1, 0), ('a/2/2/1', 1, 0)):
        a = narc(name)
        a.files[prefix + ORDINARY * stride:prefix + (ORDINARY + 1) * stride] = [bytes(x) for x in a.files[prefix + STARTER * stride:prefix + (STARTER + 1) * stride]]
    t = narc('a/0/2/8')
    for i, width in ((7, 2), (8, 2), (9, 1), (10, 2), (14, 44), (15, 8)):
        b = bytearray(t.files[i])
        b[ORDINARY * width:(ORDINARY + 1) * width] = b[STARTER * width:(STARTER + 1) * width]
        t.files[i] = bytes(b)
    b = bytearray(t.files[11])                                          # no forms: ordinary Novareon has no Mega
    b[ORDINARY * 64:(ORDINARY + 1) * 64] = bytes(64)
    t.files[11] = bytes(b)
    ls = narc('a/0/3/3')
    b = bytearray(ls.files[0])
    b[ORDINARY * 136:(ORDINARY + 1) * 136] = b[STARTER * 136:(STARTER + 1) * 136]
    ls.files[0] = bytes(b)
    d = narc('a/1/8/0')
    tb = bytearray(d.files[0])
    tb[ORDINARY * 89:(ORDINARY + 1) * 89] = tb[STARTER * 89:(STARTER + 1) * 89]
    d.files[0] = bytes(tb)
    ev = narc('a/0/3/4')
    ev.files[ORDINARY] = bytes(len(ev.files[ORDINARY]))
    rec = bytearray(ev.files[EEVEE])
    assert not any(rec[48:54]), 'ordinary Eevee has no free ninth evolution slot'
    struct.pack_into('<HHH', rec, 48, 7, STELLAR_SANDWICH, ORDINARY)
    ev.files[EEVEE] = bytes(rec)
    for name, a in ns.items():
        rom.setFileByName(name, a.save())
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    at = FOLLOWER_LITERAL - perm.ramAddress
    assert struct.unpack_from('<I', perm.data, at)[0] == MEGA, 'follower wrapper literal moved'
    struct.pack_into('<I', perm.data, at, ORDINARY)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    patch(rom)
    rom.saveToFile(sys.argv[2])
