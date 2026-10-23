"""Stellar Pokemon get the same-type attack bonus on every move.

The engine's damage routine (CalcBaseDamage, overlay 130 at 0x23C5070) applies STAB where it calls HasType(ctx, attacker,
moveType) at 0x23C5D0A (then 1.5x, or 2.0x with Adaptability). That one `ldr r3,=HasType ; blx r3` is replaced by a BL to
a routine in a reserved overlay-129 gap that answers true when HasType does, or when the attacker has the Stellar type (19).
Nothing else that calls HasType changes (type immunities, weather checks, ...).

Usage: stellar_stab.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap

SITE = 0x23C5D0A                  # ldr r3,[pc,#0x244] ; blx r3
EXPECTED = bytes.fromhex('914b9847')
HAS_TYPE = 0x23D0AB9              # Thumb
STELLAR = 19
RESERVE = 48


def bl(source, target):
    off = target - (source + 4)
    assert -(1 << 22) <= off < (1 << 22) and off % 2 == 0
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xF800 | ((off >> 1) & 0x7FF))


def patch(rom):
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm, battle = ovs[129], ovs[130]
    perm.data = bytearray(perm.data)
    battle.data = bytearray(battle.data)
    at = SITE - battle.ramAddress
    assert bytes(battle.data[at:at + 4]) == EXPECTED, bytes(battle.data[at:at + 4]).hex()
    gap = Gap(perm, address, size)
    routine = gap.code(f'''push {{r4,r5,lr}}
movs r4,r0
movs r5,r1
ldr r3, has_type
blx r3
cmp r0,#0
bne done
movs r0,r4
movs r1,r5
movs r2,#{STELLAR}
ldr r3, has_type
blx r3
done:
pop {{r4,r5,pc}}
.align 2
has_type: .word {HAS_TYPE}
''')
    battle.data[at:at + 4] = bl(SITE, routine)
    for ov in (perm, battle):
        rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(site=hex(SITE), routine=hex(routine), gap_used=gap.at - gap.start)


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
