@ Thumb-1 wrapper around OakSpeech_DoMainTask for US HeartGold overlay 53.
@ OakSpeechData: state=0x0C, unused phase=0x10, overlayManager=0x14,
@ namingScreenArgs_Rival=0x124, menu cursor=0x163, queuedMsgId=0x170.
@ Native OakSpeech_Main owns graphics teardown/reload for the naming overlay.
@ Preserve the player's naming args. OakSpeech_Exit saves both names natively.

push {r4, r5, r6, lr}
movs r4, r0
ldr r5, [r4, #12]
ldr r6, [r4, #16]
cmp r5, #103
bne check_launch
cmp r6, #0
beq show_blue
cmp r6, #3
bne original
b print_rival
show_blue:
movs r1, #3
movs r2, #0
bl #0x021e66e8
movs r0, #3
str r0, [r4, #16]
print_rival:
movs r0, r4
movs r1, #63
movs r2, #1
bl #0x021e611c
cmp r0, #1
bne pending
movs r0, #1
str r0, [r4, #16]
movs r0, #131
str r0, [r4, #12]
b pending

check_launch:
cmp r5, #131
bne check_restore
movs r0, #73
lsls r0, r0, #2
ldr r5, [r4, r0]
ldr r0, [r5, #24]
bl #0x020263ac
ldr r0, =0x02102610
movs r1, r5
ldr r2, [r4]
bl #0x0200724c
str r0, [r4, #20]
movs r0, #132
str r0, [r4, #12]
b pending

check_restore:
cmp r5, #132
bne check_confirm
movs r0, #73
lsls r0, r0, #2
ldr r0, [r4, r0]
ldr r0, [r0, #20]
cmp r0, #0
beq restore_graphics
movs r0, #131
str r0, [r4, #12]
b pending
restore_graphics:
movs r0, #96
str r0, [r4, #12]
movs r0, r4
bl #0x021e6f9c
movs r0, r4
movs r1, #3
movs r2, #0
bl #0x021e66e8
movs r0, r4
movs r1, #3
bl #0x021e80b8
movs r0, #23
lsls r0, r0, #4
movs r1, #64
str r1, [r4, r0]
b pending

check_confirm:
cmp r6, #1
bne original
cmp r5, #99
bne original
movs r0, #89
lsls r0, r0, #2
subs r0, #1
ldrb r0, [r4, r0]
cmp r0, #0
bne rename
movs r0, #2
str r0, [r4, #16]
movs r0, #100
str r0, [r4, #12]
b pending
rename:
movs r0, #131
str r0, [r4, #12]
b pending

original:
cmp r5, #100
bne run_original
cmp r6, #2
bne run_original
movs r0, r4
movs r1, #1
movs r2, #0
bl #0x021e66e8
movs r0, #4
str r0, [r4, #16]
run_original:
movs r0, r4
bl #0x021e6f9c
pop {r4, r5, r6, pc}
pending:
movs r0, #0
pop {r4, r5, r6, pc}
