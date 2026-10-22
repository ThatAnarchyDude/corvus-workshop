"""Yellow Route 6 rod encounters, with native behavior elsewhere preserved."""
import struct
import ndspy.code,ndspy.narc
from viridian_tutorial import TABLE
from starter_properties import append_code
from prototype import thumb_bl

MAP=14
WEIGHTS=(40,30,15,10,5)
OLD=((129,5),)*5
GOOD=((118,10),(60,10),(60,10),(118,10),(60,10))
SUPER=((118,5),(118,10),(118,15),(118,20),(118,20))

def table(original):
    if len(original)!=196:raise ValueError('Unexpected encounter size')
    b=bytearray(original)
    for at,slots in ((0x80,OLD),(0x94,GOOD),(0xA8,SUPER)):
        for i,(species,level) in enumerate(slots):struct.pack_into('<BBH',b,at+4*i,level,level,species)
    # Native night replacement changes Good slot3 / Super slot1: both Goldeen.
    struct.pack_into('<H',b,0xC0,118)
    return bytes(b)

def tail(label,address):
    return f"""
push {{r3}}
ldr r3,{label}
mov r12,r3
pop {{r3}}
bx r12
.balign 4
{label}: .word {address|1}
"""

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    rec=TABLE+MAP*24;assert d[rec+20]&1
    fid=rom.filenames.idOf('a/0/3/7');arc=ndspy.narc.NARC(rom.files[fid]);old=d[rec]
    wid=len(arc.files);assert wid<255;arc.files.append(table(arc.files[old]));d[rec]=wid;rom.files[fid]=arc.save()
    ovs=rom.loadArm9Overlays();ov=ovs[2];hooks=[]
    # Only Route6 Super Rod tags the copied helper argument with3. The original
    # rod variable and selected encounter table remain unchanged. Native helper
    # receives the same register/stack arguments on every other map.
    marker=f"""
push {{r4,r5}}
ldr r4,[r0,#32]
ldr r4,[r4]
cmp r4,#14
bne native
ldr r5,[sp,#12]
cmp r5,#2
bne native
movs r5,#3
str r5,[sp,#12]
native:
pop {{r4,r5}}
"""+tail('native_helper',0x02247514)
    # Native rods0..2 retain their original slot distribution; private tag3
    # uses all four Yellow Super Rod slots equally from native RNG low bits.
    selector=f"""
cmp r0,#3
bne native
push {{r4,lr}}
ldr r3,rng
blx r3
movs r1,#3
ands r0,r1
pop {{r4,pc}}
native:
"""+tail('native_selector',0x02247764)+f"""
rng: .word {0x0201FD45}
"""
    # Yellow Route6 has no fish swarms. Avoid native species substitution only
    # here; preserve native swarm behavior unchanged for every other map.
    swarm=f"""
push {{r4}}
ldr r4,[r0,#32]
ldr r4,[r4]
cmp r4,#14
pop {{r4}}
bne native
bx lr
native:
"""+tail('native_swarm',0x02246BD8)
    for name,site,target,source in [('super_marker',0x0224708A,0x02247514,marker),('slot_selector',0x02247CCC,0x02247764,selector),('swarm',0x02247070,0x02246BD8,swarm)]:
        at=site-ov.ramAddress;assert ov.data[at:at+4]==thumb_bl(site,target)
        hook,code=append_code(main,source);ov.data[at:at+4]=thumb_bl(site,hook)
        hooks.append({'name':name,'site':hex(site),'target':hex(target),'hook':hex(hook),'bytes':len(code)})
    rom.files[ov.fileID]=ov.save(compress=ov.compressed);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(ovs)
    struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    return {'map':MAP,'old_wild':old,'wild':wid,'hooks':hooks,'overlay_file':ov.fileID,'encounter_file':fid,'old_rod':OLD,'good_rod':GOOD,'super_rod':SUPER,'good_species_odds':[50,50],'super_level_odds':[25]*4,'bite_rates_preserved':True,'native_gameplay_pending':True}