@ Draw Blue inside the native selected-player SUB BG3 portrait frame.
@ Native player OBJ art, cells and animations are kept untouched.
push {r4, r5, r6, lr}
sub sp, #16
movs r4, r0
movs r1, #1
movs r2, #0
bl 0x021E66E8
movs r0, r4
movs r1, #3
bl 0x021E80B8
movs r0, #77
lsls r0, r0, #2
ldrh r5, [r4, r0]
movs r0, #0
str r0, [sp]
str r0, [sp, #4]
str r0, [sp, #8]
ldr r0, [r4]
str r0, [sp, #12]
movs r0, #120
movs r1, #BLUE_CHAR
ldr r2, [r4, #24]
movs r3, #7
bl 0x020078F0
movs r0, #120
movs r1, #BLUE_SCREEN
adds r1, r1, r5
ldr r2, [r4, #24]
movs r3, #7
bl 0x02007914
movs r0, #32
str r0, [sp]
ldr r0, [r4]
str r0, [sp, #4]
movs r0, #120
movs r1, #BLUE_PALETTE_A
movs r2, #4
movs r3, #192
bl 0x02007938
movs r0, #120
movs r1, #BLUE_PALETTE_B
movs r2, #4
movs r3, #10
lsls r3, r3, #5
bl 0x02007938
movs r0, #7
movs r1, #1
bl 0x0201BC28
add sp, #16
pop {r4, r5, r6, pc}
