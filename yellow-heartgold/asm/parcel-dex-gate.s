@ Script Dummy mode 4 hides early Dex access, retaining seen/caught data.
@ All existing starter, follower and table modes retain their original handler.
push {r0,r4,r5,lr}
movs r4,r0
adds r0,#128
ldr r5,[r0]
movs r0,r5
ldr r1,generation_var
bl 0x020403AC
cmp r0,#4
bne original
ldr r0,[r5,#12]
bl 0x0202A634
ldr r1,dex_flags
adds r1,r0,r1
movs r0,#0
strb r0,[r1]
strb r0,[r1,#1]
pop {r1,r4,r5,pc}
original:
pop {r0,r4,r5}
pop {r3}
mov lr,r3
ldr r3,original_hook
bx r3
.align 2
generation_var: .word 0x416B
dex_flags: .word 0x336
original_hook: .word 0x01FF8621
