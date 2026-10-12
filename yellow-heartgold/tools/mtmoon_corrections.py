"""Mandatory fossil-room battles and item rendering, cumulative from 0022."""
import struct
import ndspy.narc
from opening import Script, end, events_decode, events_encode, script_bank
from parcel_quest import split_bank
from prototype import thumb_bl
from starter_properties import append_code
from viridian_tutorial import TABLE
from mtmoon_story import STAGE, BOSS, exit_script
from mtmoon_rockets import JESSIE, JAMES, HIDE_JESSIE, HIDE_JAMES
from escort import music
from route24 import refresh_hook, refresh_script, init_header
from item_collision import SITE

REFRESHED=0xA93
REFRESH_STATE=0x4149
MARKER=0x4D50236D

def guard_paths():
    paths={}
    for x in range(10,16):paths[x,20]=([(14,15-x)] if x<15 else [],2,3)
    for x in range(19,24):paths[x,20]=([(13,1),(15,x-16)],0,1)
    paths[24,20]=([(13,1),(15,7),(12,1)],3,2)
    for z,xs in ((21,range(14,25)),(22,range(20,25))):
        for x in xs:
            if x<=16:walk=[(14,17-x),(13,z-20)]
            else:walk=[(13,1)]+([(15,x-17)] if x>17 else [])+([(13,z-21)] if z>21 else [])
            paths[x,z]=(walk,3,2)
    for x in range(20,25):paths[x,23]=([(13,1),(15,x-16),(13,1)],1,0)
    paths[24,23]=([(13,1),(15,7),(13,1),(15,1)],1,0)
    return paths

def guard(trainer,msg):
    paths=guard_paths()
    s=Script().emit(96).compare(STAGE,0).jump('repeat',5).emit(105,0x4000,0x4001)
    for z in (20,21,22,23):
        s.compare(0x4001,z).jump('row'+str(z),1)
    s.jump('manual')
    for z in (20,21,22,23):
        s.label('row'+str(z))
        for x,row in paths:
            if row==z:s.compare(0x4000,x).jump(f'approach{x}_{z}',1)
        s.jump('manual')
    for x,z in paths:
        s.label(f'approach{x}_{z}').movement(BOSS,f'walk{x}_{z}').emit(95)
        s.movement(255,f'face{x}_{z}').emit(95).jump('fight')
    s.label('manual').emit(104)
    s.label('fight').msg(msg).emit(213,trainer,0);s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5).emit(36,trainer).emit(41,STAGE,1).msg(msg+1)
    s.emit(105,0x4000,0x4001)
    for z in (20,21,22,23):s.compare(0x4001,z).jump('return_row'+str(z),1)
    s.jump('shared')
    for z in (20,21,22,23):
        s.label('return_row'+str(z))
        for x,row in paths:
            if row==z:s.compare(0x4000,x).jump(f'return{x}_{z}',1)
        s.jump('shared')
    for x,z in paths:
        s.label(f'return{x}_{z}').movement(BOSS,f'back{x}_{z}').emit(95).jump('shared')
    s.label('shared').msg(msg+2);end(s)
    s.label('repeat').compare(STAGE,1).jump('research',5).msg(msg+2);end(s)
    s.label('research').msg(msg+3);end(s)
    s.label('lost').emit(219);end(s)
    reverse={12:13,13:12,14:15,15:14}
    for (x,z),(walk,facing,player_facing) in paths.items():
        s.moves(f'walk{x}_{z}',walk+[(facing,1)])
        s.moves(f'face{x}_{z}',[(player_facing,1)])
        s.moves(f'back{x}_{z}',[(reverse[op],n) for op,n in reversed(walk)]+[(3,1)])
    return s.finish()

def blocked_exit(trainer,boss_msg,exit_msg):
    # First prove the guard was defeated; only then ask for the fossil choice.
    s=Script().compare(STAGE,0).jump('guard',1).jump('choice')
    s.data.extend(bytes(-len(s.data)%4));s.label('choice')
    s.data.extend(exit_script(exit_msg))
    s.data.extend(bytes(-len(s.data)%4));s.label('guard');s.data.extend(guard(trainer,boss_msg))
    return s.finish()

def rocket_ambush(trainer,msg):
    s=Script().compare(STAGE,2).jump('done',5).emit(96)
    music(s,1112);s.msg(msg).emit(105,0x4000,0x4001)
    s.compare(0x4001,23).jump('align',5).movement(255,'up').emit(95)
    s.label('align')
    for x in (20,21,23,24):s.compare(0x4000,x).jump('align'+str(x),1)
    s.jump('row')
    for x in (20,21,23,24):s.label('align'+str(x)).movement(255,'player'+str(x)).emit(95).jump('row')
    s.label('row').compare(0x4001,21).jump('face',5).movement(255,'down').emit(95)
    s.label('face').movement(255,'face_left').emit(95)
    # Sequential approaches keep the actors from crossing one another.
    s.movement(JESSIE,'jessie_in').emit(95).movement(JAMES,'james_in').emit(95).msg(msg+1)
    s.emit(213,trainer,0);s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5).emit(36,trainer)
    music(s,1112);s.msg(msg+2).msg(msg+3)
    s.movement(JAMES,'james_out').emit(95).emit(30,HIDE_JAMES).emit(101,JAMES)
    s.movement(JESSIE,'jessie_out').emit(95).emit(30,HIDE_JESSIE).emit(101,JESSIE)
    s.emit(41,STAGE,3).emit(81,0).emit(82);end(s)
    s.label('lost').emit(219);end(s)
    s.label('done').emit(2)
    for x in (20,21,23,24):s.moves('player'+str(x),[(15 if x<22 else 14,abs(x-22))])
    s.moves('up',[(12,1)]).moves('down',[(13,1)]).moves('face_left',[(2,1)])
    s.moves('jessie_in',[(12,1),(15,3),(3,1)])
    s.moves('james_in',[(12,2),(15,4),(13,1),(2,1)])
    s.moves('james_out',[(13,1),(14,1)])
    return s.moves('jessie_out',[(13,1),(15,1)]).finish()

def item_rendering(rom,main):
    field=rom.loadArm9Overlays()[1]
    pointer=struct.unpack_from('<I',field.data,0x021F92FC-field.ramAddress)[0]
    section=main.sections[1];at=pointer-section.ramAddress;found={}
    while True:
        sprite,resource,flags=struct.unpack_from('<3H',section.data,at)
        if sprite==87:item_flags=flags
        if sprite in (93,94):found[sprite]=(at,flags)
        if sprite==65535:break
        at+=6
    assert set(found)=={93,94} and item_flags==0x420
    for at,flags in found.values():
        assert flags==0
        struct.pack_into('<H',section.data,at+4,item_flags)
    d=main.sections[0].data;at=SITE-0x02000000;hi,lo=struct.unpack_from('<2H',d,at)
    assert hi&0xF800==0xF000 and lo&0xF800==0xF800
    delta=((hi&0x7FF)<<12)|((lo&0x7FF)<<1)
    if delta&(1<<22):delta-=1<<23
    previous=SITE+4+delta
    source=f'ldr r2,[r0,#16]\ncmp r2,#93\nbeq solid\ncmp r2,#94\nbeq solid\nldr r3,previous\nbx r3\nsolid:\nmovs r0,#0\nbx lr\n.align 2\nprevious: .word {previous|1}\n'
    address,_=append_code(main,source);d[at:at+4]=thumb_bl(SITE,address)
    return dict(sprites=[93,94],old_flags=0,item_flags=item_flags,collision_hook=hex(address),previous_collision_hook=hex(previous))

def first_message(body):
    prefix=struct.pack('<H',190)+b'\0'+struct.pack('<H',191)+b'\1'+struct.pack('<H',45)
    at=body.index(prefix)+len(prefix);return body[at]

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    render=item_rendering(rom,main)
    spath,epath='a/0/1/2','a/0/3/2';scripts=ndspy.narc.NARC(rom.files[rom.filenames.idOf(spath)]);events=ndspy.narc.NARC(rom.files[rom.filenames.idOf(epath)])
    rec=TABLE+107*24;old_sid,old_iid=struct.unpack_from('<2H',d,rec+6);old_eid=struct.unpack_from('<H',d,rec+16)[0]
    bank=split_bank(scripts.files[old_sid]);g=events_decode(events.files[old_eid])
    boss_msg=first_message(bank[6]);rocket_msg=first_message(bank[12]);exit_msg=first_message(bank[9])
    bank[6]=guard(776,boss_msg);bank[9]=blocked_exit(776,boss_msg,exit_msg);bank[12]=rocket_ambush(777,rocket_msg)
    for i,row in enumerate(g[1]):
        obj=struct.unpack_from('<H',row)[0];b=bytearray(row)
        if obj==BOSS:struct.pack_into('<H',b,2,338)
        if obj in (JESSIE,JAMES):struct.pack_into('<2H',b,24,18 if obj==JESSIE else 19,23);struct.pack_into('<H',b,12,0)
        g[1][i]=bytes(b)
    coord=lambda entry,x,z,w,h,value:struct.pack('<Hhh5H',entry,x,z,w,h,0,value,STAGE)
    g[3]=[coord(7,10,20,6,1,0),coord(7,19,20,6,1,0),coord(7,14,21,11,1,0),coord(10,20,22,5,2,0),coord(10,20,22,5,2,1),coord(13,20,21,5,2,2),coord(13,21,23,1,1,2),coord(13,23,23,1,1,2)]
    refresh=refresh_hook(main,list(range(64)),MARKER)
    reset=Script().emit(41,REFRESH_STATE,0).compare(STAGE,3).jump('visible',5).emit(30,HIDE_JESSIE).emit(30,HIDE_JAMES).emit(2)
    reset.label('visible').emit(31,HIDE_JESSIE).emit(31,HIDE_JAMES).emit(2)
    bank.append(reset.finish());reset_entry=len(bank)
    bank.append(refresh_script(REFRESHED,REFRESH_STATE,MARKER,[(struct.unpack_from('<H',row)[0],struct.unpack_from('<H',row,8)[0]) for row in g[1]]))
    sid=len(scripts.files);scripts.files.append(script_bank(bank));iid=len(scripts.files);scripts.files.append(init_header(reset_entry,len(bank),REFRESH_STATE));eid=len(events.files);events.files.append(events_encode(g))
    struct.pack_into('<2H',d,rec+6,sid,iid);struct.pack_into('<H',d,rec+16,eid)
    rom.files[rom.filenames.idOf(spath)]=scripts.save();rom.files[rom.filenames.idOf(epath)]=events.save()
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    return dict(map=107,script=sid,init=iid,event=eid,original=dict(script=old_sid,init=old_iid,event=old_eid),rendering=render,refresh=refresh,refresh_flag=REFRESHED,guard_trainer=776,rocket_trainer=777,guard_message=boss_msg,rocket_message=rocket_msg,exit_message=exit_msg,rocket_standby=[[18,23],[19,23]],terrain_and_warps_unchanged=True)
