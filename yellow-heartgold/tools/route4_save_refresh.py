"""Refresh only Route 4's field objects once when carrying an older normal save."""
import struct
import ndspy.narc
from opening import Script,script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE
from starter_properties import CMD_TABLE,append_code

MIGRATED=0xB3A
REFRESH_STATE=0x4142
MARKER=0x4D501939
GET_OBJECT=0x0205EE60
DELETE_OBJECT=0x0205E3CC  # MapObject_Remove: do not mark the item collected.


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);previous=struct.unpack_from('<I',d,CMD_TABLE+4)[0]
    source=f'''push {{r4,r5,r6,lr}}
movs r4,r0
ldr r1,[r4,#8]
cmp r1,#0
beq delegate
ldrb r2,[r1,#0]
cmp r2,#57
bne delegate
ldrb r2,[r1,#1]
cmp r2,#25
bne delegate
ldrb r2,[r1,#2]
cmp r2,#80
bne delegate
ldrb r2,[r1,#3]
cmp r2,#77
bne delegate
adds r1,#4
str r1,[r4,#8]
adds r4,#128
ldr r4,[r4]
ldr r5,[r4,#60]
movs r6,#0
loop:
movs r0,r5
movs r1,r6
bl {GET_OBJECT}
cmp r0,#0
beq next
bl {DELETE_OBJECT}
next:
adds r6,#1
cmp r6,#4
blo loop
movs r0,#0
pop {{r4,r5,r6,pc}}
delegate:
movs r0,r4
ldr r3,previous
blx r3
pop {{r4,r5,r6,pc}}
.align 2
previous: .word {previous}
'''
    address,_=append_code(main,source);struct.pack_into('<I',d,CMD_TABLE+4,address|1)
    fid=rom.filenames.idOf('a/0/1/2');scripts=ndspy.narc.NARC(rom.files[fid]);rec=TABLE+12*24;sid=struct.unpack_from('<H',d,rec+6)[0];bank=split_bank(scripts.files[sid])
    s=Script().emit(32,MIGRATED).jump('done',1).emit(1);s.data.extend(struct.pack('<I',MARKER))
    s.emit(100,1).emit(32,0xB39).jump('item_collected',1).emit(100,3).label('item_collected').emit(30,MIGRATED).label('done').emit(41,REFRESH_STATE,1).emit(2)
    entry=len(bank)+1;bank.append(s.finish());ns=len(scripts.files);scripts.files.append(script_bank(bank));ni=len(scripts.files);scripts.files.append(struct.pack('<BI',1,1)+b'\0'+struct.pack('<4H',REFRESH_STATE,0,entry,0));struct.pack_into('<2H',d,rec+6,ns,ni);rom.files[fid]=scripts.save()
    struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    return dict(map=12,flag=MIGRATED,state_var=REFRESH_STATE,script=ns,init=ni,entry=entry,noop_hook=hex(address),previous_hook=hex(previous),marker=hex(MARKER),removed_ids=[0,1,2,3],restored_ids=[1,3],party_items_quest_and_normal_save_layout_preserved=True)
