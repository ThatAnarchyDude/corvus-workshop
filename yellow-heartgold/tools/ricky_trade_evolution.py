"""Post-trade native evolution, scoped to Yellow RICKY at map469/trade9."""
import struct
from starter_properties import append_code
SITE=0x02067A5C
ORIGINAL=0x0206795C
SOURCE=r"""
push {r4,r5,r6,r7,lr}
sub sp,#44
movs r4,r0
bl 0x0205064C
movs r5,r0
movs r0,r4
bl 0x02050650
movs r6,r0
ldr r0,[r6]
ldr r0,[r0,#12]
cmp r0,#9
beq check_map
b ordinary
check_map:
ldr r0,[r5,#32]
ldr r0,[r0]
ldr r1,trade_map
cmp r0,r1
beq check_state
b ordinary
check_state:
ldr r0,[r6,#4]
cmp r0,#7
bne maybe_start
b wait_evo
maybe_start:
cmp r0,#4
beq start_evo
b ordinary
start_evo:
ldr r0,[r5,#12]
bl 0x02074904
ldr r1,[r6,#8]
bl 0x02074644
movs r7,r0
movs r1,#5
movs r2,#0
bl 0x0206E540
cmp r0,#67
beq get_evolution
b ordinary
get_evolution:
add r0,sp,#32
str r0,[sp]
movs r0,#0
movs r1,r7
movs r2,#1
movs r3,#0
bl 0x02070E34
cmp r0,#68
beq launch_evo
b ordinary
launch_evo:
movs r0,#3
movs r1,#26
lsls r2,r0,#16
bl 0x0201A910
ldr r0,[r5,#12]
bl 0x02028EA8
str r0,[sp,#28]
ldr r0,[r5,#12]
bl 0x02088288
str r0,[sp]
ldr r0,[r5,#12]
bl 0x0202A634
str r0,[sp,#4]
ldr r0,[r5,#12]
bl 0x0207879C
str r0,[sp,#8]
ldr r0,[r5,#12]
bl 0x0202CF54
str r0,[sp,#12]
ldr r0,[sp,#32]
str r0,[sp,#16]
movs r0,#4
str r0,[sp,#20]
movs r0,#26
str r0,[sp,#24]
movs r0,#0
movs r1,r7
movs r2,#68
ldr r3,[sp,#28]
bl 0x02075A7C
str r0,[r6,#12]
movs r0,#7
str r0,[r6,#4]
b pending
wait_evo:
ldr r0,[r6,#12]
bl 0x02075D3C
cmp r0,#0
beq pending
ldr r0,[r6,#12]
bl 0x02075D4C
movs r0,#26
bl 0x0201A9C4
movs r0,#4
str r0,[r6,#4]
ordinary:
movs r0,r4
bl 0x0206795C
b finish
pending:
movs r0,#0
finish:
add sp,#44
pop {r4,r5,r6,r7,pc}
.balign 4
trade_map: .word 469
"""
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 at=SITE-0x02000000
 assert struct.unpack_from('<I',d,at)[0]==ORIGINAL|1
 # Assert native lifecycle sites used by wrapper still match the source.
 assert d[0x6795C:0x67960]==bytes.fromhex('70b582b0')
 hook,code=append_code(main,SOURCE)
 struct.pack_into('<I',d,at,hook|1)
 struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
 rom.arm9=main.save(compress=True)
 return {'site':hex(SITE),'hook':hex(hook),'code_bytes':len(code),'map':469,'trade':9,'expected_species':68,'native_evolution_flags':4,'gameplay_validation_pending':True}