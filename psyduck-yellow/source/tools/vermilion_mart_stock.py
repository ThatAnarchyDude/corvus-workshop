"""Add Yellow's Vermilion stock without replacing any existing shop catalog."""
import struct
import ndspy.narc
from starter_properties import append_code
from prototype import thumb_bl
from viridian_tutorial import TABLE
SITE=0x2048180
NATIVE_TABLE=0x210FA3C
CATALOG=30
ITEMS=(4,26,20,21,22,79,0xFFFF)

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);base=main.sections[0].ramAddress
 assert d[SITE-base:SITE-base+4]==bytes.fromhex('034a1259')
 code='''
push {r3}
mov r3,r2
cmp r4,#120
beq custom
ldr r2,native_table
ldr r2,[r2,r4]
b done
custom:
adr r2,items
done:
lsls r4,r3,#2
pop {r3}
bx lr
.balign 4
native_table: .word 0x210FA3C
items: .hword 4,26,20,21,22,79,65535
.balign 4
'''
 hook,raw=append_code(main,code);d[SITE-base:SITE-base+4]=thumb_bl(SITE,hook)
 rec=TABLE+360*24;sid=struct.unpack_from('<H',d,rec+6)[0];fid=rom.filenames.idOf('a/0/1/2');scripts=ndspy.narc.NARC(rom.files[fid]);native=scripts.files[sid]
 entries=[struct.unpack_from('<I',native,i*4)[0]+i*4+4 for i in range(4)];assert entries[0]<entries[1]<entries[2]
 special=bytearray(native[entries[1]:entries[2]]);needle=struct.pack('<3H',41,0x8004,14);assert special.count(needle)==1;special[special.index(needle)+4:special.index(needle)+6]=struct.pack('<H',CATALOG)
 bank=bytearray(native);bank.extend(bytes(-len(bank)%4));at=len(bank);bank.extend(special);struct.pack_into('<I',bank,0,at-4)
 assert bank[4:len(native)]==native[4:]
 ns=len(scripts.files);scripts.files.append(bytes(bank));rom.files[fid]=scripts.save();struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
 return {'map':360,'catalog':CATALOG,'items':ITEMS,'site':SITE,'hook':hook,'hook_bytes':len(raw),'old_script':sid,'script':ns,'itcm_remaining':32768-len(main.sections[1].data),'native_catalogs_unchanged':True,'native_buy_sell_test_pending':True}