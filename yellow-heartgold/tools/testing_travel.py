"""Temporary testing Fly access and one two-way Route 4 return gap."""
import struct
import ndspy.narc,ndspy.code
from starter_properties import append_code
from prototype import thumb_bl

HM_FLY=421
STOCK_PTR=0x10FA3C+20*4
BADGE_CALL=0x02068026
QUANTITY_CALL=0x022578FA
DIVIDE=0x020F2BA4
GAP=(1268,117)


def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 assert d[BADGE_CALL-0x2000000:BADGE_CALL-0x2000000+4]==thumb_bl(BADGE_CALL,0x02028F98)
 d[BADGE_CALL-0x2000000:BADGE_CALL-0x2000000+4]=bytes.fromhex('0120c046')
 old=struct.unpack_from('<I',d,STOCK_PTR)[0];stock=[];at=old-0x2000000
 while (item:=struct.unpack_from('<H',d,at)[0])!=65535:stock.append(item);at+=2
 assert len(stock)==12 and HM_FLY not in stock
 address,_=append_code(main,'.hword '+','.join(map(str,[HM_FLY,*stock,65535])));struct.pack_into('<I',d,STOCK_PTR,address)
 # Native shop divides available money by unit price. A free HM needs a
 # bounded quantity of one, including when the player's balance is zero.
 source=f'''cmp r1,#0
bne original
ldr r3,item_offset
ldrh r3,[r5,r3]
ldr r2,fly
cmp r3,r2
bne original
movs r0,#1
movs r1,#0
bx lr
original:
ldr r3,divide
bx r3
.align 2
item_offset: .word 0x284
fly: .word {HM_FLY}
divide: .word {DIVIDE}
'''
 hook,_=append_code(main,source);ov=rom.loadArm9Overlays();shop=ov[3];o=QUANTITY_CALL-shop.ramAddress;before=bytes(shop.data[o:o+4]);assert before==bytes.fromhex('9bf654e9'),before.hex()
 shop.data[o:o+4]=thumb_bl(QUANTITY_CALL,hook);rom.files[shop.fileID]=shop.save(compress=shop.compressed);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(ov)
 matrices=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')]);lands=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')]);m=bytearray(matrices.files[0]);w,h,headers,heights,n=m[:5];offset=5+n+w*h*(2*headers+heights);x,z=GAP;cell=z//32*w+x//32;land=struct.unpack_from('<H',m,offset+2*cell)[0];raw=bytearray(lands.files[land]);a=20+2*((z%32)*32+x%32);old_permission=struct.unpack_from('<H',raw,a)[0];assert old_permission==0x803B
 struct.pack_into('<H',raw,a,0);new_land=len(lands.files);lands.files.append(raw);struct.pack_into('<H',m,offset+2*cell,new_land);matrices.files[0]=m
 rom.files[rom.filenames.idOf('a/0/4/1')]=matrices.save();rom.files[rom.filenames.idOf('a/0/6/5')]=lands.save()
 struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
 return dict(temporary_testing_feature=True,fly=dict(item=HM_FLY,price=0,department_store_floor=3,stock_index=20,original_stock=stock,stock_address=hex(address),badge_call=hex(BADGE_CALL),quantity_hook=hex(hook),quantity_call=hex(QUANTITY_CALL),quantity_original=before.hex(),visited_destinations_and_other_field_restrictions_preserved=True),return_gap=dict(x=x,z=z,original_permission=old_permission,permission=0,land=land,new_land=new_land,matrix_cell=cell),save_layout_unchanged=True)
