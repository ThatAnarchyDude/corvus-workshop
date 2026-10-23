@ Isolated prototype: NOT installed in any ROM.
@ Keep native validation for every non-general/unchanged spec.
push {r4,r5,r6,r7,lr}
sub sp,#12
movs r4,r0
movs r5,r1
movs r6,r2
cmp r6,#0
bne native
ldr r7,spec_offset
adds r7,r4,r7
ldr r0,[r7,#8]
ldr r1,new_size
cmp r0,r1
bne native
movs r0,r4
movs r1,r5
movs r2,r6
bl 0x0202761C
cmp r0,#0
bne check_header
ldr r0,old_size
str r0,[r7,#8]
movs r0,r4
movs r1,r5
movs r2,r6
bl 0x0202761C
ldr r1,new_size
str r1,[r7,#8]
cmp r0,#0
beq finish
ldr r0,tail_offset
adds r7,r5,r0
ldr r6,[r7]
movs r0,r7
movs r1,#0
movs r2,#54
zero_tail:
str r1,[r0]
adds r0,#4
subs r2,#1
bne zero_tail
ldr r0,extension_magic
str r0,[r7]
ldr r0,version_count
str r0,[r7,#4]
adds r7,#216
str r6,[r7]
ldr r0,new_size
str r0,[r7,#4]
ldr r0,native_magic
str r0,[r7,#8]
strh r1,[r7,#12]
movs r0,r5
ldr r1,new_footer
bl 0x0201FF98
strh r0,[r7,#14]
movs r0,#1
b finish
check_header:
ldr r1,tail_offset
adds r1,r5,r1
ldr r0,[r1]
ldr r2,extension_magic
cmp r0,r2
bne invalid
ldr r0,[r1,#4]
ldr r2,version_count
cmp r0,r2
bne invalid
ldr r0,[r1,#8]
ldr r1,[r1,#12]
orrs r0,r1
bne invalid
movs r0,#1
b finish
invalid:
movs r0,#0
b finish
native:
movs r0,r4
movs r1,r5
movs r2,r6
bl 0x0202761C
finish:
add sp,#12
pop {r4,r5,r6,r7,pc}
.align 2
spec_offset: .word 0x232B4
new_size: .word 0xF700
old_size: .word 0xF628
tail_offset: .word 0xF618
new_footer: .word 0xF6F0
native_magic: .word 0x20060623
extension_magic: .word 0x43505950
version_count: .word 0x00320001
