"""Every VS banner names the trainer you are actually fighting (found 2026-10-27, built 2026-10-28; the Elite Four banners read the wrong names).

Problem: the VS banner (the "VS" logo with the opponent's portrait) does not use the opponent's own name. Overlay 115 keeps one VS record per trainer class
(12-byte records for the gym leaders and Blue, five 8-byte records for the Elite Four and Champion), and builds the text from the name row of the record's trainer id.
HG had exactly one trainer per class, Yellow does not: Lorelei and Agatha share class 88 (record -> trainer 246, now LANCE), Lance (class 86) reads trainer 244 (BLUE),
Bruno (class 112) reads trainer 418 (AGATHA), and Blue's class-110 record named trainer 261 until vs_banner_blue.py repointed it.
Fix: the two places that pick the id for the name builder (0x0225F158) ask a small routine in overlay 129 first. It walks from the effect (FieldSystem -> current task ->
the task below it, which must be the battle task 0x02050739 -> its environment -> BattleSetup) to the first opponent's trainer id (BattleSetup + 0x1C, the value the
TrainerBattle script command stored) and returns that. Anything unexpected (a pointer outside main RAM, another parent task, an id of 0 or beyond the trainer table) keeps
the record's own id, so a banner can only fall back to the old behaviour. The rival-name special case (class 23, the saved rival name) is untouched.
Portraits and the effect that is chosen stay class based, so Lorelei and Agatha keep the same portrait but now read their own names.

Usage: vs_banner_names.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap

OVERLAY = 115
STATE_SITE = 0x0225F2D4            # state machine: ldr r0,[r6,#4] (record id); adds r1,r7,#0 (heap id)   [r5 = effect]
ELITE_SITE = 0x0225FD26            # Elite Four function: bl 0x0225F158 with r0 = record id, r1 = heap id [r6 = effect]
BUILDER = 0x0225F158
BATTLE_TASK = 0x02050739          # callback of the battle task (ARM9 0x02050738)
TRAINER_NARC = 'a/0/5/5'


def _bl(site, target):
    off = (target - (site + 4)) >> 1
    assert target % 2 == 0 and -(1 << 21) <= off < (1 << 21), (hex(site), hex(target))
    return struct.pack('<HH', 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


def patch(rom):
    limit = len(ndspy.narc.NARC(rom.getFileByName(TRAINER_NARC)).files)
    address, size = ext.reserve_code(rom, 24 * 8)                  # first: it rewrites overlay 129 (the header table moves up)
    ovs = rom.loadArm9Overlays()
    perm, vs = ovs[129], ovs[OVERLAY]
    perm.data, vs.data = bytearray(perm.data), bytearray(vs.data)
    gap = Gap(perm, address, size)
    core = gap.code(f'''
push {{r4, lr}}
adds r4, r0, #0
ldr r2, [r1, #0x10]
lsrs r3, r2, #22
cmp r3, #8
bne done
ldr r2, [r2, #0x10]
lsrs r3, r2, #22
cmp r3, #8
bne done
ldr r2, [r2]
lsrs r3, r2, #22
cmp r3, #8
bne done
ldr r3, [r2, #4]
ldr r1, battle
cmp r3, r1
bne done
ldr r2, [r2, #0xc]
lsrs r3, r2, #22
cmp r3, #8
bne done
ldr r2, [r2, #0x10]
lsrs r3, r2, #22
cmp r3, #8
bne done
ldr r2, [r2, #0x1c]
cmp r2, #0
beq done
ldr r3, limit
cmp r2, r3
bhs done
adds r4, r2, #0
done:
adds r0, r4, #0
pop {{r4, pc}}
.align 2
battle: .word {BATTLE_TASK}
limit: .word {limit}
''') | 1
    state = gap.code(f'''
push {{lr}}
ldr r0, [r6, #4]
adds r1, r5, #0
ldr r3, core
blx r3
adds r1, r7, #0
pop {{pc}}
.align 2
core: .word {core}
''') | 1
    elite = gap.code(f'''
push {{r1, lr}}
adds r1, r6, #0
ldr r3, core
blx r3
pop {{r1}}
ldr r3, builder
blx r3
pop {{pc}}
.align 2
core: .word {core}
builder: .word {BUILDER | 1}
''') | 1
    for site, old, new in ((STATE_SITE, '7068391c', state), (ELITE_SITE, 'fff717fa', elite)):
        at = site - vs.ramAddress
        assert bytes(vs.data[at:at + 4]).hex() == old, (hex(site), bytes(vs.data[at:at + 4]).hex())
        vs.data[at:at + 4] = _bl(site, new & ~1)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.files[vs.fileID] = vs.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(core=hex(core & ~1), state_shim=hex(state & ~1), elite_shim=hex(elite & ~1), trainer_limit=limit, gap_left=gap.end - gap.at)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
