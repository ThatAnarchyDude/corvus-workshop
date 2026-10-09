@ Sentinel selects fixed Yellow stock; every other mart uses the original code.
push {r4, r5, r6, lr}
movs r4, r0
ldr r5, [r4, #8]
bl 0x0203FE2C
movs r1, r0
movs r0, r4
adds r0, #0x80
ldr r0, [r0]
bl 0x020403AC
ldr r1, sentinel
cmp r0, r1
beq yellow
str r5, [r4, #8]
movs r0, r4
pop {r4, r5, r6}
pop {r3}
mov lr, r3
ldr r3, original
bx r3
yellow:
sub sp, #16
movs r3, #0
str r3, [sp]
str r3, [sp, #4]
str r3, [sp, #8]
ldr r0, [r4, #0x74]
movs r1, r4
adds r1, #0x80
ldr r1, [r1]
adr r2, stock
bl 0x02256D34
movs r0, #1
add sp, #16
pop {r4, r5, r6, pc}
.align 2
sentinel: .word 0x3FFE
original: .word 0x02048061
stock: .short 4, 17, 18, 22, 19, 0xFFFF
