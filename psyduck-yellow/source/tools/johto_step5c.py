"""Johto postgame, step 5c: wild encounters in Johto follow the Johto badges (owner 2026-11-02, JOHTO-POSTGAME-PLAN.md).

Same curve as the ordinary trainers (step 5b): 0 Johto badges = the level the encounter has, 8 badges = level 100: level = O + floor((100 - O) * min(badges, 8) / 8).
Two creators in overlay 2 build every table encounter (0x02247910 and 0x02247A18; species r0, level r1; each starts with a stub to a routine in overlay 129). Two small pieces:
 - the table getter (ARM9 0x0203B8B8, called with the FieldSystem for every encounter table read; its stub already points at the Mt. Moon routine in ITCM) first jumps to a new routine that reads the player's
   map (FieldSystem -> location -> map id) and stores K in a RAM byte: the Johto badge count for a native map (id < 540) whose header byte 20 has bit 0 clear (Johto), else 0. It then continues into the Mt. Moon routine;
 - the two creators' stub literals are redirected to two thunks and one shared scaler: r1 = r1 + floor((100 - r1) * K / 8) when K != 0, then the creator's own overlay-129 routine runs as before.
Kanto maps (header bit 0 set) and the project's extension maps (id >= 540) never scale. Scripted wild battles (script command 589, e.g. static legendaries, gifts of Pokemon) do not go through these
creators' table path and are NOT scaled (checked live: a scripted Rattata L5 stayed L5), nor are roamers and fixed-level static encounters.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step5c.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.rom
from mega_starter import Gap

GET_TABLE = 0x0203B8B8                                        # ARM9: `ldr r3,[pc]; bx r3; .word <Mt. Moon routine | 1>`
CREATORS = {0x02247914: 0x023DD02D, 0x02247A20: 0x023DD125}   # overlay 2: stub literal address -> the creator's overlay-129 routine
COUNT = 0x023DEDB0                                            # step 5b's subroutine: r4 = Johto badge count (clobbers r0-r2, keeps r3)
HEADER_TABLE = 0x020F6BE0                                     # native map headers, 24 bytes each, Kanto flag = bit 0 of byte 20
CHUNK_A = (0x023DEBA0, 0x023DEC00)                            # free zeros of the old dex_fix region (the getter hook and the K byte)
CHUNK_B = (0x023DEDE0, 0x023DEE14)                            # free space behind step 5b's routine (thunks and scaler)
K_AT = 0x023DEBFC                                             # the RAM byte (last word of chunk A)


def patch(rom):
    main = rom.loadArm9()
    arm9 = main.sections[0]
    arm9.data = bytearray(arm9.data)
    ovs = rom.loadArm9Overlays()
    perm, field = ovs[129], ovs[2]
    perm.data, field.data = bytearray(perm.data), bytearray(field.data)
    count_at = COUNT - perm.ramAddress
    assert perm.data[count_at:count_at + 2] == bytes.fromhex('00b5'), 'step 5b count subroutine not found'
    for lo, hi in (CHUNK_A, CHUNK_B):
        assert not any(perm.data[lo - perm.ramAddress:hi - perm.ramAddress]), 'free space not free'
    at = GET_TABLE - arm9.ramAddress
    assert bytes(arm9.data[at:at + 4]) == bytes.fromhex('004b1847'), bytes(arm9.data[at:at + 4]).hex()
    mt_moon = struct.unpack_from('<I', arm9.data, at + 4)[0]
    assert mt_moon & 1 and 0x01FF0000 < mt_moon < 0x02000000, hex(mt_moon)

    getter_gap = Gap(perm, CHUNK_A[0], K_AT - CHUNK_A[0])
    getter = getter_gap.code(f'''
push {{r0, r4, lr}}
ldr r4, [r0, #0x20]
cmp r4, #0
beq done
ldr r4, [r4]
movs r1, #135
lsls r1, r1, #2
cmp r4, r1
bcs zero
movs r1, #24
muls r4, r1, r4
ldr r1, header
adds r4, r4, r1
ldrb r4, [r4, #20]
movs r1, #1
ands r4, r1
bne zero
bl {COUNT}
b store
zero:
movs r4, #0
store:
ldr r1, kptr
strb r4, [r1]
done:
ldr r3, [sp, #8]
mov lr, r3
ldr r0, [sp, #0]
ldr r4, [sp, #4]
add sp, #12
ldr r3, target
bx r3
.align 2
header: .word {HEADER_TABLE}
kptr: .word {K_AT}
target: .word {mt_moon}
''')
    scaler_gap = Gap(perm, *(CHUNK_B[0], CHUNK_B[1] - CHUNK_B[0]))
    thunks = []
    pieces = []
    for literal, creator in CREATORS.items():
        pieces.append((literal, creator))
    code = scaler_gap.code(f'''
thunk_a:
ldr r4, next_a
mov r12, r4
b scale
thunk_b:
ldr r4, next_b
mov r12, r4
b scale
scale:
push {{r5}}
ldr r4, kptr
ldrb r4, [r4]
cmp r4, #0
beq out
movs r5, #100
subs r5, r5, r1
muls r5, r4, r5
lsrs r5, r5, #3
adds r1, r1, r5
out:
pop {{r5}}
bx r12
.align 2
next_a: .word {pieces[0][1]}
next_b: .word {pieces[1][1]}
kptr: .word {K_AT}
''')
    thunk_a, thunk_b = code, code + 6
    for (literal, creator), thunk in zip(pieces, (thunk_a, thunk_b)):
        lat = literal - field.ramAddress
        assert struct.unpack_from('<I', field.data, lat)[0] == creator, hex(literal)
        struct.pack_into('<I', field.data, lat, thunk | 1)
    struct.pack_into('<I', arm9.data, at + 4, getter | 1)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.files[field.fileID] = field.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return dict(getter=hex(getter), thunks=[hex(thunk_a), hex(thunk_b)], getter_left=getter_gap.end - getter_gap.at, scaler_left=scaler_gap.end - scaler_gap.at)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
