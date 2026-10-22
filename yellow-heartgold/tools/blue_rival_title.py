"""Display Blue as Rival before first Hall of Fame, preserving native postgame titles."""
import struct
import ndspy.narc
from blue_properties_shared import OLD,helper,assemble
from prototype import thumb_bl,decode_messages,encode_messages
SITES=(0x0200C2F0,0x0200C328,0x0200C360)
READ_MESSAGE=0x0200BB6C
LABEL_INDEX=130
FLAG_BYTE_OFFSET=0x2E0+(0x964//8)

def code(address,save_pointer):
 return assemble(f'''push {{r0,r1,r2,r3,r4,lr}}
cmp r1,#110
bne restore
ldr r0,save_pointer
ldr r0,[r0]
cmp r0,#0
beq restore
bl 0x020503D0
ldr r1,flag_offset
ldrb r0,[r0,r1]
movs r1,#16
tst r0,r1
bne restore
movs r0,#{LABEL_INDEX}
str r0,[sp,#4]
restore:
pop {{r0,r1,r2,r3,r4}}
pop {{r3}}
mov lr,r3
ldr r3,original
bx r3
.align 2
save_pointer: .word {save_pointer}
flag_offset: .word {FLAG_BYTE_OFFSET}
original: .word {READ_MESSAGE|1}
''',address)

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);itcm=main.sections[1];address=OLD+len(helper(809));save_pointer=struct.unpack_from('<I',d,0x272C4)[0];assert save_pointer==0x021D2228
 assert bytes(itcm.data[OLD-itcm.ramAddress:address-itcm.ramAddress])==helper(809)
 raw=code(address,save_pointer);assert len(raw)<=316
 for site in SITES:assert d[site-0x02000000:site-0x02000000+4]==thumb_bl(site,READ_MESSAGE)
 texts_id=rom.filenames.idOf('a/0/2/7');texts=ndspy.narc.NARC(rom.files[texts_id])
 for index in (730,731):
  key,messages=decode_messages(texts.files[index]);assert len(messages)==LABEL_INDEX
  messages.append(list(messages[23]));texts.files[index]=encode_messages(key,messages)
 itcm.data=bytearray(itcm.data);itcm.data[address-itcm.ramAddress:address-itcm.ramAddress+len(raw)]=raw
 for site in SITES:d[site-0x02000000:site-0x02000000+4]=thumb_bl(site,address)
 rom.files[texts_id]=texts.save();rom.arm9=main.save(compress=True)
 return dict(helper_address=address,helper_bytes=len(raw),extra_itcm_bytes=0,sites=list(SITES),native_class_id=110,text_only_rival_label=LABEL_INDEX,hall_of_fame_flag=0x964,postgame_native_label_preserved=True,other_classes_preserved=True)
