@ Entry replaces GetMonEvolution's first three instructions. r12 holds its
@ original caller LR; all four arguments and the fifth stack argument survive.
push {r0,r1,r2,r3,r4,r5,r6,r7,lr}
sub sp,#4
mov r0,r12
str r0,[sp,#36]
cmp r2,#2
beq item_context
cmp r2,#3
bne ordinary
item_context:
movs r0,r1
movs r1,#5
movs r2,#0
bl 0x0206E540
ldr r1,rules_ptr
ldr r3,[sp,#16]
rule_loop:
ldrh r2,[r1]
cmp r2,#0
beq ordinary
cmp r2,r0
bne next_rule
ldrh r2,[r1,#2]
cmp r2,r3
bne next_rule
ldrh r0,[r1,#4]
str r0,[sp,#4]
ldr r1,[sp,#40]
cmp r1,#0
beq done
movs r2,#0
str r2,[r1]
done:
add sp,#4
pop {r0,r1,r2,r3,r4,r5,r6,r7,pc}
next_rule:
adds r1,#6
b rule_loop
ordinary:
ldr r0,[sp,#36]
mov lr,r0
add sp,#4
pop {r0,r1,r2,r3,r4,r5,r6,r7}
add sp,#4
@ Replay the overwritten native prologue; r6 is zeroed by native code next.
push {r4,r5,r6,r7,lr}
sub sp,#68
movs r7,r1
ldr r6,resume_ptr
bx r6
.align 2
resume_ptr: .word 0x02070E3B
rules_ptr: .word rules
rules:
.short 54,84,55
.short 133,109,196
.short 133,108,197
.short 133,246,471
.short 133,85,470
.short 175,109,176
.short 0,0,0
