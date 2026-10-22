"""Prototype 012: removable coffee barriers, Cut trees and parcel Pokégear reward."""
import json,struct,subprocess
import ndspy.rom,ndspy.narc,ndspy.code,ndspy.texture
from build_rom import PROJECT,BASE,EXPECTED,sha
from opening import Script,actor,events_decode,events_encode,script_bank,encode_text,end,command
from prototype import decode_messages,encode_messages
from parcel_quest import PARCEL_STATE,PH,split_bank,clerk_talk
from viridian_tutorial import TABLE,TUTORIAL_DONE,BLOCKER_HIDE,PASSED_HIDE
from opening_corrections import BARRIER_TILES,old_man

INPUT_SHA='6ac69f643d8277aee718157a0c1fafc7b3e6dfe960f12d59ae372b0fbcf41b7e'
WORLD_MIGRATED=0xB47
WEST_HIDE=0xB46
GEAR_REWARD=0xB45
INVISIBLE_SPRITE=90
BLOCKERS=[(14+i,x,z) for i,(x,z) in enumerate([(x,z) for x,z in BARRIER_TILES if x not in [1021,1032]])]
GRANDDAUGHTER=17
GRANDDAUGHTER_ASIDE=22
TREES=[(19,1021,235,0x10),(20,1032,235,0x11)]
WEST_ACTOR=21
WEST_POSITION=(1002,259)
PROMISE="Come back here once it's delivered and I'll give you something that will help you A LOT on your travels."
WEST_MESSAGE="Stop! You can't go this way right now. There's been reports of terrifyingly strong Pokémon down this path. You're not ready for that yet."
THANKS="Thanks for delivering that parcel! You really helped us out a lot! Here's your payment as promised."
REWARD="{PLAYER} received a POKéGEAR!\rIts Town Map card is already installed. You can check your location and explore Kanto with it!"


def invisible_model(rom,main):
    file=rom.filenames.idOf('a/0/8/1');models=ndspy.narc.NARC(rom.files[file]);tex=ndspy.texture.NSBTX(models.files[128])
    for _,t in tex.textures:t.data1=bytes(len(t.data1));t.isColor0Transparent=True
    model=len(models.files);models.files.append(tex.save());rom.files[file]=models.save()
    overlays=rom.loadArm9Overlays();o=overlays[1];previous=struct.unpack_from('<I',o.data,0x021F92FC-o.ramAddress)[0];section=main.sections[1];at=previous-section.ramAddress;i=0
    while struct.unpack_from('<H',section.data,at+i*6)[0]!=65535:i+=1
    rows=section.data[at:at+i*6]+struct.pack('<3H',INVISIBLE_SPRITE,model,0)+section.data[at+i*6:at+(i+1)*6]
    section.data.extend(bytes(-len(section.data)%4));address=section.ramAddress+len(section.data);section.data.extend(rows)
    for p in [0x021F92FC,0x021FA280]:assert struct.unpack_from('<I',o.data,p-o.ramAddress)[0]==previous;struct.pack_into('<I',o.data,p-o.ramAddress,address)
    rom.files[o.fileID]=o.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    return dict(sprite=INVISIBLE_SPRITE,model=model,lookup=hex(address))


def restore_land(rom):
    mf=rom.filenames.idOf('a/0/4/1');lf=rom.filenames.idOf('a/0/6/5');matrices=ndspy.narc.NARC(rom.files[mf]);lands=ndspy.narc.NARC(rom.files[lf]);m=bytearray(matrices.files[0]);w,h,headers,heights,name=m[:5];at=5+name+w*h*(2*headers+heights);clones={};records=[]
    for x,z in BARRIER_TILES:
        cell=z//32*w+x//32;pos=at+cell*2
        if cell not in clones:
            old=struct.unpack_from('<H',m,pos)[0];new=len(lands.files);lands.files.append(bytearray(lands.files[old]));struct.pack_into('<H',m,pos,new);clones[cell]=new;records.append(dict(cell=cell,old_land=old,new_land=new))
        b=lands.files[clones[cell]];i=20+2*(z%32*32+x%32);v=struct.unpack_from('<H',b,i)[0];assert v&0x8000;struct.pack_into('<H',b,i,v&0x7FFF)
    matrices.files[0]=m;rom.files[mf]=matrices.save();rom.files[lf]=lands.save();return records


def world_sync(reloading=False):
    s=Script().compare(PARCEL_STATE,2).jump('west_clear',1).emit(31,WEST_HIDE).jump('west_done')
    s.label('west_clear')
    if reloading:
        # A saved 012 guard exists only after our first migration, and only
        # while its previous hide flag was clear. Never delete a missing actor.
        s.emit(32,WORLD_MIGRATED).jump('west_hide',5).emit(32,WEST_HIDE).jump('west_hide',1).emit(101,WEST_ACTOR)
    s.label('west_hide').emit(30,WEST_HIDE).label('west_done')
    s.emit(32,WORLD_MIGRATED).jump('done',1)
    s.emit(32,TUTORIAL_DONE).jump('trees',1)
    for obj,_,_ in BLOCKERS:s.emit(100,obj)
    s.label('trees').emit(32,TUTORIAL_DONE).jump('trees_start',5).emit(100,GRANDDAUGHTER_ASIDE).label('trees_start')
    for obj,_,_,flag in TREES:
        s.emit(32,flag).jump(f'tree{obj}',1).emit(100,obj).label(f'tree{obj}')
    s.emit(32,WEST_HIDE).jump('done',1).emit(100,WEST_ACTOR)
    return s.label('done').emit(30,WORLD_MIGRATED).finish()


def west_guard(index,interaction=False):
    s=Script().compare(PARCEL_STATE,2).jump('done',1).emit(96)
    if interaction:s.emit(104)
    s.msg(index)
    if not interaction:s.movement(255,'back').emit(95)
    end(s);s.label('done').emit(2)
    if not interaction:s.moves('back',[(15,1)])
    return s.finish()


def upper_clerk(thanks,reward):
    s=Script().compare(PARCEL_STATE,2).jump('talk',5).emit(30,0x9A)
    s.emit(32,GEAR_REWARD).jump('talk',1).emit(96).emit(104).msg(thanks)
    # HG Pokégear has no bag item. Grant access and its native map card without
    # resetting any saved phone contacts, skin, clock or already installed cards.
    s.emit(30,0x9C).emit(145);s.data.append(1)
    s.emit(804);s.data.append(2)
    s.emit(30,GEAR_REWARD).emit(78,1187).msg(reward).emit(79).emit(97)
    s.label('talk');s.data.extend(clerk_talk())
    return s.finish()


def patch(rom):
    main=rom.loadArm9();data=main.sections[0].data=bytearray(main.sections[0].data);old_end=main.sections[1].ramAddress+len(main.sections[1].data)
    report={'invisible':invisible_model(rom,main),'land_clones':restore_land(rom)}
    paths=['a/0/1/2','a/0/2/7','a/0/3/2'];arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths};scripts,texts,events=(arcs[p] for p in paths)
    mappings=[]
    for mapid in [50,500]:
        rec=TABLE+mapid*24;sid,iid,tid=struct.unpack_from('<3H',data,rec+6);eid=struct.unpack_from('<H',data,rec+16)[0];bank=split_bank(scripts.files[sid]);groups=events_decode(events.files[eid]);key,messages=decode_messages(texts.files[tid])
        # Both the outdoor escort scene and indoor cashier use local message 4.
        messages[4]=decode_messages(encode_text(["Okay! Say hi to PROF.OAK for me!\r"+PROMISE],PH))[1][0]
        new_message=len(messages)
        lines=[WEST_MESSAGE,"Grandpa hasn't had his coffee yet. Please come back later.","Grandpa loves teaching new Trainers! Good luck on your adventure!"] if mapid==50 else [THANKS,REWARD]
        messages.extend(decode_messages(encode_text(lines,PH))[1])
        if mapid==50:
            cleared=[v[0] for v in BLOCKERS if v[0]!=GRANDDAUGHTER];companion=(GRANDDAUGHTER,[(13,3),(0,1)])
            bank[13]=old_man(12,clear_objects=cleared,companion=companion,companion_after=GRANDDAUGHTER_ASIDE);bank[14]=old_man(12,True,clear_objects=cleared,companion=companion,companion_after=GRANDDAUGHTER_ASIDE)
            bank[10]=west_guard(new_message);guard_script=len(bank)+1;bank.append(west_guard(new_message,True))
            girl_script=len(bank)+1;girl=Script().emit(96).emit(104).emit(32,TUTORIAL_DONE).jump('after',1).msg(new_message+1);end(girl);girl.label('after').msg(new_message+2);bank.append(end(girl).finish())
            # First map entry creates actors normally from flags; mark migration
            # before sync to avoid double creation. Type 3 reload migrates once.
            bank[11]=command(30,WORLD_MIGRATED)+world_sync()+bank[11]
            bank[15]=world_sync(True)+bank[15]
            groups[1].extend(actor(obj,7 if obj==GRANDDAUGHTER else INVISIBLE_SPRITE,girl_script if obj==GRANDDAUGHTER else 0,x,z,BLOCKER_HIDE) for obj,x,z in BLOCKERS)
            groups[1].extend(actor(obj,86,10000,x,z,flag,0) for obj,x,z,flag in TREES)
            groups[1].append(actor(WEST_ACTOR,34,guard_script,*WEST_POSITION,WEST_HIDE,3))
            wandering=bytearray(actor(GRANDDAUGHTER_ASIDE,7,girl_script,1028,238,PASSED_HIDE,0));struct.pack_into('<H',wandering,4,3);struct.pack_into('<2h',wandering,20,1,1);groups[1].append(wandering)
        else:bank[1]=upper_clerk(new_message,new_message+1)
        new_sid=len(scripts.files);scripts.files.append(script_bank(bank));new_iid=len(scripts.files);scripts.files.append(scripts.files[iid]);new_tid=len(texts.files);texts.files.append(encode_messages(key,messages));new_eid=len(events.files);events.files.append(events_encode(groups))
        struct.pack_into('<3H',data,rec+6,new_sid,new_iid,new_tid);struct.pack_into('<H',data,rec+16,new_eid);mappings.append(dict(map=mapid,script=new_sid,init=new_iid,text=new_tid,event=new_eid))
    for p,arc in arcs.items():rom.files[rom.filenames.idOf(p)]=arc.save()
    assert struct.unpack_from('<I',data,0xD2C68)[0]==old_end;main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',data,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));assert len(main.sections[1].data)<0x8000;rom.arm9=main.save(compress=True)
    report.update(mappings=mappings,blockers=BLOCKERS,granddaughter={'before':GRANDDAUGHTER,'after':GRANDDAUGHTER_ASIDE,'aside':[1028,238]},cut_trees=TREES,west_guard=WEST_POSITION,flags={'migration':WORLD_MIGRATED,'west_hide':WEST_HIDE,'gear_reward':GEAR_REWARD});return report


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-011.nds';assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));old=ndspy.rom.NintendoDSRom.fromFile(str(source));report=patch(rom)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nAdventure preparation prototype 012\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    assert rom.arm7==old.arm7;target=PROJECT/'build/yellow-heartgold-prototype-012.nds';target.write_bytes(rom.save());patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/adventure-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True);subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True);assert sha(decoded.read_bytes())==sha(target.read_bytes())
    report.update(version='012',base_version='011',input_sha256=INPUT_SHA,output_sha256=sha(target.read_bytes()),patch_sha256=sha(patchfile.read_bytes()),changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b]);(PROJECT/'build/adventure-ready-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
