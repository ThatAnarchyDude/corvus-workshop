@ Expand bag selection only during our player-PC deposit transaction.
push {r4, r5, r6, lr}
sub sp, #8
movs r5, r0
movs r6, r1
ldr r1, context_var
bl 0x020403AC
ldr r1, context_magic
cmp r0, r1
beq player_pc
movs r0, r5
movs r1, r6
bl 0x0203E460
b finished
player_pc:
movs r0, r5
ldr r1, pocket_var
bl 0x020403AC
mov r1, sp
strb r0, [r1, #4]
movs r0, #255
strb r0, [r1, #5]
ldr r0, [r5, #12]
bl 0x0207879C
add r1, sp, #4
movs r2, #32
bl 0x02078644
movs r4, r0
movs r1, r5
ldr r2, input_offset
adds r1, r1, r2
str r1, [sp]
ldr r1, [r5, #12]
movs r3, r5
adds r3, #148
ldr r3, [r3]
movs r2, #1
bl 0x0207789C
movs r0, r5
movs r1, r4
bl 0x0203E3D4
movs r0, r4
finished:
add sp, #8
pop {r4, r5, r6, pc}
.align 2
context_var: .word 0x800B
context_magic: .word 0xCAFE
input_offset: .word 0x10C
pocket_var: .word 0x800A
