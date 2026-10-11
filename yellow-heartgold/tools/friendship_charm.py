"""Temporary passive friendship test item, delivered through bedroom PC storage."""
import struct
import ndspy.narc
from starter_properties import append_code
from opening import script_bank,encode_text
from parcel_quest import split_bank,PH
from player_pc import script
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
from yellow_tms import ITEM_TABLE

ITEM=121

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    previous=struct.unpack_from('<I',d,0x503D4)[0]
    assert d[0x503D0:0x503D4]==bytes.fromhex('004b1847')
    address,code=append_code(main,f'''push {{r4,r5,r6,r7,lr}}
sub sp,#4
movs r4,r0
bl {previous & ~1}
movs r5,r0
movs r0,r4
movs r1,#3
bl 0x020272C8
ldr r1, =660
adds r0,r0,r1
movs r2,#50
scan:
ldrh r1,[r0]
cmp r1,#121
bne next
ldrh r1,[r0,#2]
cmp r1,#0
bne owned
next:
adds r0,#4
subs r2,#1
bne scan
b done
owned:
movs r0,r4
movs r1,#2
bl 0x020272C8
movs r4,r0
ldr r7,[r4,#4]
movs r6,#0
mon_loop:
cmp r6,r7
bhs done
movs r0,r4
movs r1,r6
bl 0x02074644
str r0,[sp]
movs r1,#76
movs r2,#0
bl 0x0206E540
cmp r0,#0
bne next_mon
ldr r0,[sp]
movs r1,#9
movs r2,#0
bl 0x0206E540
cmp r0,#255
beq next_mon
ldr r0,[sp]
movs r1,#255
str r1,[sp]
movs r1,#9
mov r2,sp
bl 0x0206EC40
next_mon:
adds r6,#1
b mon_loop
done:
movs r0,r5
add sp,#4
pop {{r4,r5,r6,r7,pc}}
.ltorg
''')
    struct.pack_into('<I',d,0x503D4,address|1)
    paths=('a/0/1/2','a/0/2/7','a/0/1/7');scripts,texts,items=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    assert struct.unpack_from('<H',d,ITEM_TABLE+ITEM*8)[0]==0
    source,icon,palette,_=struct.unpack_from('<4H',d,ITEM_TABLE+114*8)
    index=len(items.files);items.files.append(items.files[source])
    struct.pack_into('<4H',d,ITEM_TABLE+ITEM*8,index,icon,palette,0)
    for bank,line in ((222,'FRIENDSHIP CHARM'),(221,'A testing charm. While carried in the Bag, it sets friendship to maximum for all non-Egg party POKEMON.')):
        key,words=decode_messages(texts.files[bank]);words[ITEM]=decode_messages(encode_text([line],PH))[1][0];texts.files[bank]=encode_messages(key,words)
    rec=TABLE+506*24;sid=struct.unpack_from('<H',d,rec+6)[0];tid=struct.unpack_from('<H',d,rec+10)[0]
    bank=split_bank(scripts.files[sid]);bank[1]=script(evolution_items=True,shiny_charm=True,friendship_charm=True)
    ns=len(scripts.files);scripts.files.append(script_bank(bank));struct.pack_into('<H',d,rec+6,ns)
    key,words=decode_messages(texts.files[tid]);words[39]=decode_messages(encode_text(['Make room in ITEM STORAGE, then reopen the PC to receive the remaining testing items.'],PH))[1][0]
    # This existing message guards both permanent testing charms against tossing.
    words[40]=decode_messages(encode_text(['You should keep this testing charm. You can withdraw it or deposit it in your PC.'],PH))[1][0]
    nt=len(texts.files);texts.files.append(encode_messages(key,words));struct.pack_into('<H',d,rec+10,nt)
    for p,a in zip(paths,(scripts,texts,items)):rom.files[rom.filenames.idOf(p)]=a.save()
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    return dict(item=ITEM,hook=hex(address),bytes=len(code),pc_map=506,pc_script=ns,pc_text=nt,
                passive=True,friendship=255,scope='non-Egg party Pokemon',existing_saves=True,
                other_evolution_prerequisites_unchanged=True)
