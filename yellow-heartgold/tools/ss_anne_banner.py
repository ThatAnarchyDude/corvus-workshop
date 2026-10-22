"""Native S.S. Anne banners, using only the existing 64-byte overlay routine."""
import ndspy.code
from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from prototype import thumb_bl
from viridian_tutorial import TABLE
CLONES=(254,255)
SITE=0x021EFAF8
END=0x021EFB38
SOURCE='''push {r3,r4,r5,lr}
ldr r4,[r0,#32]
ldr r4,[r4]
ldr r5,[r0,#4]
ldr r5,[r5,#8]
movs r0,r4
bl 0x0203B388
cmp r0,#0
beq done
str r0,[sp]
cmp r4,#254
beq named
cmp r4,#255
beq named
movs r0,r4
bl 0x0203B58C
cmp r0,#0
bne done
named:
movs r0,r4
bl 0x0203B36C
movs r1,r0
ldr r2,[sp]
subs r2,#1
movs r0,r5
bl 0x021EFA3C
done:
pop {r3,r4,r5,pc}
'''
def assemble():
 raw,_=Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(SOURCE,addr=SITE)
 code=bytes(raw)
 assert len(code)<=END-SITE
 assert all(i.size==2 or i.mnemonic=='bl' for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(code,SITE))
 return code+bytes.fromhex('c046')*((END-SITE-len(code))//2)
def patch(rom):
 data=rom.loadArm9().sections[0].data
 for mid in CLONES:
  at=TABLE+mid*24
  assert data[at+18]==235 and data[at+19]&15==9
 overlays=rom.loadArm9Overlays();overlay=overlays[1];offset=SITE-overlay.ramAddress
 assert overlay.data[offset:offset+4]==bytes.fromhex('38b5051c')
 assert overlay.data[offset+20:offset+24]==thumb_bl(SITE+20,0x0203B58C)
 assert overlay.data[offset+62:offset+64]==bytes.fromhex('38bd')
 overlay.data[offset:offset+64]=assemble()
 rom.files[overlay.fileID]=overlay.save(compress=overlay.compressed)
 rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
 return {'maps':list(CLONES),'overlay':1,'site':SITE,'routine_bytes':64,'extra_itcm_bytes':0,'native_banner_icon':9,'all_other_maps_use_native_building_check':True,'native_playtest_pending':True}
