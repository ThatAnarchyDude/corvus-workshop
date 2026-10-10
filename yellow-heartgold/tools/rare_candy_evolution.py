"""Permit level-100 Rare Candy evolution through the native evolution scene.

Use the same party, time/location, friendship, gender and held-item checks as
ordinary level-up evolution. Never award experience or rerun level-100 moves.
An unsuccessful eligibility check falls back to the native no-effect message.
"""
import struct
from starter_properties import append_code

DISPATCH = 0x0207C288
GET_EVOLUTION = 0x02070E34
GET_MAP_EVOLUTION = 0x0203B60C
TAKE_ITEM = 0x02078434


def patch(rom):
    main = rom.loadArm9()
    data = main.sections[0].data = bytearray(main.sections[0].data)
    offset = DISPATCH - 0x02000000
    assert data[offset:offset+8] == bytes.fromhex('38b5051c4c480021')
    # Relocate the native PC-relative prologue explicitly rather than copying
    # its literal load into ITCM. The original entry saved r3 on the stack.
    trampoline, _ = append_code(main, '''
push {r3, r4, r5, lr}
movs r5, r0
ldr r0, args_offset
movs r1, #0
ldr r3, continuation
bx r3
.align 2
args_offset: .word 0x654
continuation: .word 0x0207C291
''')
    entry, _ = append_code(main, f'''
push {{r4, r5, r6, r7, lr}}
sub sp, #4
movs r4, r0
ldr r0, args_offset
ldr r5, [r4, r0]
ldrh r0, [r5, #0x28]
cmp r0, #50
bne native
ldr r1, slot_offset
ldrb r1, [r4, r1]
ldr r0, [r5]
bl 0x02074644
movs r6, r0
movs r1, #161
movs r2, #0
bl 0x0206E540
cmp r0, #100
bne native
movs r0, r6
movs r1, #76
movs r2, #0
bl 0x0206E540
cmp r0, #0
bne native
ldr r0, [r5, #0x1c]
ldr r0, [r0, #0x20]
ldr r0, [r0]
bl {GET_MAP_EVOLUTION}
lsls r3, r0, #16
lsrs r3, r3, #16
movs r0, r5
adds r0, #0x40
str r0, [sp]
ldr r0, [r5]
movs r1, r6
movs r2, #0
bl {GET_EVOLUTION}
movs r7, r0
cmp r0, #0
beq native
ldr r0, [r5, #4]
movs r1, #50
movs r2, #1
movs r3, #12
bl {TAKE_ITEM}
cmp r0, #0
beq native
strh r7, [r5, #0x3c]
movs r0, r5
adds r0, #0x27
movs r1, #9
strb r1, [r0]
movs r0, #32
add sp, #4
pop {{r4, r5, r6, r7, pc}}
native:
movs r0, r4
add sp, #4
pop {{r4, r5, r6, r7}}
pop {{r3}}
mov lr, r3
ldr r3, original
bx r3
.align 2
args_offset: .word 0x654
slot_offset: .word 0xC65
original: .word {trampoline | 1}
''')
    data[offset:offset+8] = bytes.fromhex('004b1847') + struct.pack('<I', entry | 1)
    rom.arm9 = main.save(compress=True)
    return dict(dispatch=hex(DISPATCH),entry=hex(entry),trampoline=hex(trampoline),
                level_100_evolution=True,native_requirements=True,
                no_effect_consumes_item=False,evolution_cancel_available=True)
