"""Persist first-entry/per-date-and-lighting-period native preview eligibility."""
import struct
from prototype import thumb_bl
from starter_properties import append_code
SITE=0x02055F42
GET_INDEX=0x0206A360
MAGIC=0x31565050
OFFSET=0x288
SOURCE=r"""
push {r4,r5,r6,r7,lr}
sub sp,#20
bl 0x0206A360
movs r4,r0
cmp r0,#25
blo eligible_index
b done
eligible_index:
ldr r0,[r5,#12]
movs r1,#9
bl 0x020272C8
ldr r1,padding
adds r6,r0,r1
mov r0,sp
bl 0x02014780
bl 0x0201481C
movs r7,r0
cmp r0,#4
bne date_ready
@ Native LATE hours continue the previous evening's night period.
ldr r0,[sp,#8]
cmp r0,#1
beq previous_month
subs r0,#1
str r0,[sp,#8]
b date_ready
previous_month:
ldr r1,[sp,#4]
cmp r1,#1
bne decrement_month
movs r1,#13
ldr r0,[sp]
cmp r0,#0
bne decrement_year
movs r0,#100
decrement_year:
subs r0,#1
str r0,[sp]
decrement_month:
subs r1,#1
str r1,[sp,#4]
movs r2,r1
subs r2,#1
adr r0,month_days
ldrb r0,[r0,r2]
cmp r1,#2
bne store_previous_day
ldr r2,[sp]
movs r1,#3
tst r2,r1
bne store_previous_day
adds r0,#1
store_previous_day:
str r0,[sp,#8]
date_ready:
cmp r7,#3
blo phase_ready
movs r7,#3
phase_ready:
ldr r0,[sp]
lsls r0,r0,#16
orrs r7,r0
ldr r0,[sp,#4]
lsls r0,r0,#12
orrs r7,r0
ldr r0,[sp,#8]
lsls r0,r0,#4
orrs r7,r0
ldr r0,[r6]
ldr r1,version_magic
cmp r0,r1
bne reset_history
ldr r0,[r6,#4]
cmp r0,r7
beq seen_test
reset_history:
ldr r0,version_magic
str r0,[r6]
str r7,[r6,#4]
movs r0,#0
str r0,[r6,#8]
seen_test:
movs r1,#1
adr r2,history_keys
ldrb r2,[r2,r4]
lsls r1,r2
ldr r0,[r6,#8]
tst r0,r1
beq first_entry
movs r4,#255
b done
first_entry:
orrs r0,r1
str r0,[r6,#8]
done:
movs r0,r4
add sp,#20
pop {r4,r5,r6,r7,pc}
.balign 4
padding: .word 0x288
version_magic: .word 0x31565050
month_days: .byte 31,28,31,30,31,30,31,31,30,31,30,31
.balign 4
"""
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);at=SITE-0x02000000
 assert d[at:at+4]==thumb_bl(SITE,GET_INDEX)
 table=struct.unpack_from("<I",d,0x6A384)[0]-0x02000000
 groups={};keys=[]
 for i in range(25):
  art=bytes(d[table+i*60+8:table+i*60+56]);keys.append(groups.setdefault(art,i))
 source=SOURCE+"\nhistory_keys: .byte "+",".join(map(str,keys))+"\n.balign 4\n"
 hook,code=append_code(main,source);d[at:at+4]=thumb_bl(SITE,hook)
 struct.pack_into("<I",d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
 rom.arm9=main.save(compress=True)
 return {"site":hex(SITE),"hook":hex(hook),"code_bytes":len(code),"save_block":9,"history_offset":OFFSET,"history_bytes":12,"preview_count":25,"history_keys":keys,"night_late_shared":True,"native_art_unchanged":True,"native_gameplay_validation_pending":True}