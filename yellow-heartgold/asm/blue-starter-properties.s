@ Trainer-party wrapper: preserve one Blue starter seed and independent rare
@ rolls in unused saved flags B00..B1F and B3C..B3E. Original HG is untouched.
push {r4, r5, r6, r7, lr}
sub sp, #44
str r0, [sp, #28]
str r1, [sp, #32]
bl 0x02073604
ldr r0, [sp, #28]
ldr r1, [sp, #32]
lsls r1, r1, #2
adds r2, r0, r1
ldr r3, [r2, #24]
ldr r1, first_trainer
cmp r3, r1
bhs range_low
b finished
range_low:
adds r1, #9
cmp r3, r1
bls eligible
b finished
eligible:
ldr r0, [r2, #4]
ldr r1, [r0, #4]
subs r1, #1
bl 0x02074644
movs r4, r0
ldr r0, [sp, #28]
ldr r1, save_offset
ldr r0, [r0, r1]
bl 0x020503D0
ldr r1, seed_offset
adds r5, r0, r1
ldrb r0, [r5, #7]
movs r1, #16
tst r0, r1
bne initialized
bl 0x0201FD44
movs r6, r0
bl 0x0201FD44
lsls r0, r0, #16
orrs r6, r0
str r6, [r5]
ldrb r7, [r5, #7]
movs r0, #112
bics r7, r0
bl 0x0201FD44
lsls r0, r0, #20
lsrs r0, r0, #20
cmp r0, #0
bne perfect_roll
movs r0, #32
orrs r7, r0
perfect_roll:
bl 0x0201FD44
lsls r0, r0, #18
lsrs r0, r0, #18
cmp r0, #0
bne record_rolls
movs r0, #64
orrs r7, r0
record_rolls:
movs r0, #16
orrs r7, r0
strb r7, [r5, #7]
initialized:
bl 0x0201FD2C
str r0, [sp]
ldr r0, [r5]
bl 0x0201FD38
movs r0, r4
movs r1, #111
movs r2, #0
bl 0x0206E540
str r0, [sp, #8]
movs r0, r4
movs r1, #5
movs r2, #0
bl 0x0206E540
str r0, [sp, #12]
@ Give this starter a stable OT ID across Blue's appended battle records.
ldr r0, [r5]
ldr r1, blue_ot
 eors r0, r1
str r0, [sp, #4]
movs r0, r4
movs r1, #7
add r2, sp, #4
bl 0x0206EC40
ldr r0, [sp, #4]
lsrs r1, r0, #16
eors r0, r1
lsls r0, r0, #16
lsrs r0, r0, #16
str r0, [sp, #16]
pid_low:
bl 0x0201FD44
movs r7, r0
lsls r0, r0, #24
lsrs r0, r0, #24
ldr r1, [sp, #12]
cmp r1, #54
beq duck_threshold
movs r1, #31
b compare_gender
duck_threshold:
movs r1, #127
compare_gender:
movs r2, #0
cmp r0, r1
bhs gender_test
movs r2, #1
gender_test:
ldr r0, [sp, #8]
cmp r0, r2
bne pid_low
bl 0x0201FD44
movs r6, r0
ldrb r0, [r5, #7]
movs r1, #32
tst r0, r1
beq not_shiny
ldr r6, [sp, #16]
eors r6, r7
b set_pid
not_shiny:
ldr r0, [sp, #16]
eors r0, r7
eors r0, r6
cmp r0, #8
bhs set_pid
movs r0, #1
lsls r0, r0, #12
eors r6, r0
set_pid:
lsls r6, r6, #16
orrs r6, r7
movs r0, r4
movs r1, r6
bl 0x0207235C
movs r0, r4
movs r1, #111
add r2, sp, #8
bl 0x0206EC40
movs r0, r4
bl 0x020722DC
movs r6, #70
iv_loop:
bl 0x0201FD44
movs r1, #31
ands r0, r1
ldrb r2, [r5, #7]
movs r3, #64
tst r2, r3
beq iv_ready
movs r0, #31
iv_ready:
str r0, [sp, #4]
movs r0, r4
movs r1, r6
add r2, sp, #4
bl 0x0206EC40
adds r6, #1
cmp r6, #76
blo iv_loop
movs r0, r4
bl 0x0206E250
ldr r0, [sp]
bl 0x0201FD38
finished:
add sp, #44
pop {r4, r5, r6, r7, pc}
.align 2
first_trainer: .word 741
save_offset: .word 0x1C0
seed_offset: .word 0x440
blue_ot: .word 0x424C5545
