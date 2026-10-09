@ Reserved script Dummy command: operates only while VAR 416B is explicitly 1.
@ Call after GiveMon and before the follower/Dex UI reads the new party member.
@ Native SetMonPersonality reshuffles and re-encrypts both data blocks safely.
push {r4, r5, r6, r7, lr}
sub sp, #20
adds r0, #128
ldr r5, [r0]
movs r0, r5
ldr r1, generation_var
bl 0x020403AC
cmp r0, #1
beq enabled
b done
enabled:
ldr r0, [r5, #12]
bl 0x02074904
movs r1, #0
bl 0x02074644
movs r4, r0
movs r1, #5
movs r2, #0
bl 0x0206E540
movs r5, r0
cmp r5, #54
beq valid
cmp r5, #133
beq valid
cmp r5, #175
beq valid
b done
valid:
movs r0, r4
movs r1, #7
movs r2, #0
bl 0x0206E540
lsrs r1, r0, #16
eors r0, r1
lsls r6, r0, #16
lsrs r6, r6, #16
@ Independent shiny and perfect-IV rolls, each exactly 1/16384.
bl 0x0201FD44
lsls r0, r0, #18
lsrs r0, r0, #18
str r0, [sp]
bl 0x0201FD44
lsls r0, r0, #18
lsrs r0, r0, #18
str r0, [sp, #4]
ability_roll:
bl 0x0201FD44
ldr r1, max_random
cmp r0, r1
beq ability_roll
movs r1, #3
blx 0x020F2998
str r1, [sp, #12]
pid_low:
bl 0x0201FD44
@ Normal ability slots retain the correct PID parity through evolution.
ldr r1, [sp, #12]
cmp r1, #2
beq parity_ready
movs r2, #1
bics r0, r2
orrs r0, r1
parity_ready:
movs r7, r0
lsls r0, r0, #24
lsrs r0, r0, #24
cmp r5, #133
bne not_eevee
cmp r0, #31
bhs pid_low
b pid_high
not_eevee:
cmp r5, #54
bne pid_high
cmp r0, #127
blo pid_low
pid_high:
bl 0x0201FD44
movs r1, r0
ldr r0, [sp]
cmp r0, #0
bne not_shiny
movs r1, r7
eors r1, r6
b join_pid
not_shiny:
movs r0, r7
eors r0, r6
eors r0, r1
cmp r0, #8
bhs join_pid
movs r0, #1
lsls r0, r0, #12
eors r1, r0
join_pid:
lsls r1, r1, #16
orrs r7, r1
movs r0, r4
movs r1, r7
bl 0x0207235C
@ Refresh the cached gender and ordinary ability after changing the PID.
lsls r0, r7, #24
lsrs r0, r0, #24
movs r1, #0
cmp r5, #54
beq gender_ready
cmp r0, #31
bhs gender_ready
movs r1, #1
gender_ready:
str r1, [sp, #8]
movs r0, r4
movs r1, #111
add r2, sp, #8
bl 0x0206EC40
movs r0, r4
bl 0x020722DC
ldr r0, [sp, #4]
cmp r0, #0
bne choose_ability
movs r0, #31
str r0, [sp, #8]
movs r6, #70
iv_loop:
movs r0, r4
movs r1, r6
add r2, sp, #8
bl 0x0206EC40
adds r6, #1
cmp r6, #76
blo iv_loop
choose_ability:
@ One third receives the supported Hidden Ability, otherwise the PID slot.
ldr r0, [sp, #12]
cmp r0, #2
bne recalculate
movs r0, #33
cmp r5, #54
beq ability_ready
movs r0, #107
cmp r5, #133
beq ability_ready
movs r0, #105
ability_ready:
str r0, [sp, #8]
movs r0, r4
movs r1, #10
add r2, sp, #8
bl 0x0206EC40
recalculate:
movs r0, r4
bl 0x0206E250
done:
movs r0, #0
add sp, #20
pop {r4, r5, r6, r7, pc}
.align 2
generation_var: .word 0x416B
max_random: .word 65535
