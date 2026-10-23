"""Yellow Vermilion fishing; preserve existing Route 6 and native behavior elsewhere."""
import struct
import ndspy.code,ndspy.narc
from viridian_tutorial import TABLE
from starter_properties import append_code
from prototype import thumb_bl
from route6_fishing import OLD,GOOD,tail
MAP=54
SUPER=((72,15),(72,20),(72,10),(116,5),(116,5))
NIGHT_SENTINEL=0xFFFF
def bl_target(data,site,base):
 hi,lo=struct.unpack_from('<HH',data,site-base);assert hi&0xF800==0xF000 and lo&0xF800==0xF800
 n=((hi&2047)<<12)|((lo&2047)<<1)
 if n&(1<<22):n-=1<<23
 return site+4+n
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+MAP*24;assert d[rec+20]&1
 fid=rom.filenames.idOf('a/0/3/7');arc=ndspy.narc.NARC(rom.files[fid]);assert not any(len(v)==196 and struct.unpack_from('<H',v,0xC0)[0]==NIGHT_SENTINEL for v in arc.files)
 old=d[rec];raw=bytearray(arc.files[old]);assert len(raw)==196
 for at,slots in ((0x80,OLD),(0x94,GOOD),(0xA8,SUPER)):
  for i,(species,level) in enumerate(slots):struct.pack_into('<BBH',raw,at+4*i,level,level,species)
 struct.pack_into('<H',raw,0xC0,NIGHT_SENTINEL);wid=len(arc.files);assert wid<255;arc.files.append(bytes(raw));d[rec]=wid;rom.files[fid]=arc.save()
 ovs=rom.loadArm9Overlays();ov=ovs[2];old_marker=bl_target(ov.data,0x224708A,ov.ramAddress);old_swarm=bl_target(ov.data,0x2247070,ov.ramAddress)
 assert old_marker==0x1FFFD38 and old_swarm==0x1FFFD80
 marker='''
push {r4,r5}
ldr r4,[r0,#32]
ldr r4,[r4]
cmp r4,#54
bne native
ldr r5,[sp,#12]
cmp r5,#2
bne native
movs r5,#3
str r5,[sp,#12]
native:
pop {r4,r5}
'''+tail('previous_marker',old_marker)
 swarm='''
push {r4}
ldr r4,[r0,#32]
ldr r4,[r4]
cmp r4,#54
pop {r4}
bne native
bx lr
native:
'''+tail('previous_swarm',old_swarm)
 # Only the newly appended table carries this sentinel. Preserve r0-r3 and
 # all native night substitutions for original encounter tables.
 night='''
push {r3}
movs r3,r0
adds r3,#192
ldrh r3,[r3]
adds r3,#1
lsls r3,r3,#16
pop {r3}
bne native
bx lr
native:
'''+tail('native_night',0x2246AD4)
 hooks=[]
 for name,site,target,code in [('super_marker',0x224708A,old_marker,marker),('swarm',0x2247070,old_swarm,swarm),('night',0x2247064,0x2246AD4,night)]:
  at=site-ov.ramAddress;assert ov.data[at:at+4]==thumb_bl(site,target);hook,rawcode=append_code(main,code);ov.data[at:at+4]=thumb_bl(site,hook);hooks.append({'name':name,'site':hex(site),'previous':hex(target),'hook':hex(hook),'bytes':len(rawcode)})
 rom.files[ov.fileID]=ov.save(compress=ov.compressed);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(ovs);struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
 return {'map':MAP,'old_wild':old,'wild':wid,'hooks':hooks,'encounter_file':fid,'overlay_file':ov.fileID,'itcm_remaining_bytes':32768-len(main.sections[1].data),'old_rod':OLD,'good_rod':GOOD,'super_rod':SUPER,'native_gameplay_pending':True}