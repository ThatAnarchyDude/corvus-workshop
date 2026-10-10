"""Prototype 013: readable dialogue, Yellow Route 22 and safe League gates."""
import json,struct,subprocess
import ndspy.rom,ndspy.narc,ndspy.code
from build_rom import PROJECT,BASE,EXPECTED,sha
from opening import Script,actor,trigger,events_decode,events_encode,script_bank,encode_text,talk,end,command
from parcel_quest import split_bank,PH,PARCEL_STATE,BOUNDARY
from viridian_tutorial import TABLE,oak_parcel
from starter_properties import append_code
from prototype import decode_messages,encode_messages,thumb_bl
from escort import music,ball_choice,rival_battle
INPUT_SHA='7910d6ed6b6e1a47107084405de67c5adb0ac6408107348e6adba0f53e733bec'
R22_DONE=0xB44
R22_HIDE=0xB43
R22_MIGRATED=0xB42
RIVAL_PICKED=0xB41
RIVAL_DUCK=0xB40
RIVAL_FEMALE=0xB3F
BLUE=30
ROUTE_X=982
R22_LINES=["{RIVAL}: Hey! {PLAYER}!\rYou're going to POKEMON LEAGUE?\rForget it! You probably don't have any BADGEs!\rThe guard won't let you through!\rBy the way, did your POKEMON get any stronger?",
           "Awww! You just lucked out!",
           "{RIVAL}: What? Why do I have 2 POKEMON?\rYou should catch some more too!",
           "I heard POKEMON LEAGUE has many tough trainers!\rI have to figure out how to get past them!\rYou should quit dawdling and get a move on!",
           "POKEMON LEAGUE\rThe ultimate goal of every POKEMON Trainer!"]


def repair_scroll(words):
    out=[];scrolled=False
    for v in words:
        if v==0x25BC:scrolled=False
        if v==0x25BD:scrolled=True
        out.append(0x25BD if v==0xE000 and scrolled else v)
    return out


def player_shiny_odds(main,roll_hook):
    from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
    assembler=Ks(KS_ARCH_ARM,KS_MODE_THUMB)
    old=bytes(assembler.asm('lsls r0,r0,#18; lsrs r0,r0,#18; str r0,[sp]')[0])
    new=bytes(assembler.asm('lsls r0,r0,#20; lsrs r0,r0,#20; str r0,[sp]')[0])
    itcm=main.sections[1];assert itcm.data.count(old)==1
    at=itcm.data.index(old);itcm.data[at:at+len(old)]=new
    site=itcm.ramAddress+at-4
    assert itcm.data[at-4:at]==thumb_bl(site,0x0201FD44)
    itcm.data[at-4:at]=thumb_bl(site,roll_hook)
    guard=bytes(assembler.asm('cmp r0,#8; bhs 0x1000',addr=0x1000)[0])[:2]
    # Only the PID rejection comparison, between the rare roll and join_pid.
    search_end=at+180
    pos=itcm.data.index(guard,at,search_end);itcm.data[pos:pos+2]=bytes.fromhex('1028')
    return dict(hook='0x1ff8620',shiny_roll_denominator=4096,perfect_iv_roll_denominator=16384,mask_site=hex(itcm.ramAddress+at))


def experience_hook(rom,main):
    # Task_GetExp: after item/trainer/ownership multipliers, before the native
    # EXP update, HUD animation, stat recalculation and move-learning handling.
    source='''push {r4, r5, r6, lr}
sub sp, #8
movs r5, r0
bl 0x0206E540
movs r6, r0
ldr r3, [r4]
adds r3, #162
ldrh r3, [r3]
ldr r2, first
cmp r3, r2
blo done
adds r2, #5
cmp r3, r2
bhi done
eligible:
ldr r0, [sp, #12]
cmp r0, #0
bne done
movs r0, r5
movs r1, #5
movs r2, #0
bl 0x0206E540
movs r1, #6
bl 0x0206FD00
cmp r0, r6
bhi award
movs r0, #0
b store
award:
subs r0, r0, r6
store:
str r0, [sp, #80]
done:
movs r0, r6
add sp, #8
pop {r4, r5, r6, pc}
.align 2
first: .word 741'''
    addr,_=append_code(main,source);overlays=rom.loadArm9Overlays();o=overlays[12];at=0x02245AD8-o.ramAddress;assert o.data[at:at+4]==thumb_bl(0x02245AD8,0x0206E540);o.data[at:at+4]=thumb_bl(0x02245AD8,addr);rom.files[o.fileID]=o.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays);return {'hook':hex(addr),'site':'0x02245ad8','trainer_ids':list(range(741,747)),'level':6}


def blue_properties_hook(main,roll_hook):
    source=(PROJECT/'asm/blue-starter-properties.s').read_text().replace('bl 0x0201FD44\nlsls r0, r0, #20',f'bl {roll_hook}\nlsls r0, r0, #20').replace('cmp r0, #8','cmp r0, #16')
    address,code=append_code(main,source)
    data=main.sections[0].data;site=0x02073440
    assert data[site-0x02000000:site-0x02000000+4]==thumb_bl(site,0x02073604)
    data[site-0x02000000:site-0x02000000+4]=thumb_bl(site,address)
    return dict(hook=hex(address),site=hex(site),trainers=list(range(741,751)),seed_flags=['0xB00','0xB1F'],initialized_flag='0xB3C',shiny_flag='0xB3D',perfect_flag='0xB3E',shiny_roll_denominator=4096,perfect_iv_roll_denominator=16384,bytes=len(code))


def selected_battle(s,trainers,allow_loss,result):
    s.emit(32,RIVAL_PICKED).jump('legacy_choice',5).emit(32,RIVAL_DUCK).jump('selected_duck',1).jump('selected_eevee')
    s.label('legacy_choice').emit(206,0x800C).compare(0x800C,133).jump('default_duck',1).jump('default_eevee')
    for species,name in [(54,'duck'),(133,'eevee')]:
        s.label('selected_'+name).emit(32,RIVAL_FEMALE).jump(name+'_female',1)
        for gender in ['male','female']:
            if gender=='female':s.label(name+'_female')
            s.emit(213,trainers[f'{species}_{gender}'],0);s.data.extend(bytes([allow_loss,0]));s.jump(result)
        s.label('default_'+name).emit(213,trainers[species],0);s.data.extend(bytes([allow_loss,0]));s.jump(result)


def random_togepi_choice():
    # Rolls made on a cancelled menu are discarded; accepted choices persist.
    s=Script().emit(380,0x800A,2).compare(0x800A,0).jump('duck',1)
    for rival_index in [2,0]:
        # Each embedded script's movement arrays were assembled relative to a
        # four-byte-aligned origin. Keep that origin aligned in the outer bank.
        if len(s.data)%2:s.emit(190);s.data.append(0)
        if len(s.data)%4:s.emit(1)
        if rival_index==0:s.label('duck')
        def save_choice(c):
            c.emit(30,RIVAL_PICKED).emit(30 if rival_index==0 else 31,RIVAL_DUCK).emit(239,0,0x800B)
            c.compare(0x800B,0).jump('opposite_female',1).emit(31,RIVAL_FEMALE).jump('gender_saved')
            c.label('opposite_female').emit(30,RIVAL_FEMALE).label('gender_saved')
        code=ball_choice(1,grant_dex=False,rival_override=rival_index,after_properties=save_choice)
        code=code.replace(command(45)+bytes([19]),command(45)+bytes([49]))
        s.data.extend(code)
    return s.finish()


def rival_scene(trainers):
    s=Script().emit(32,R22_DONE).jump('done',1).compare(PARCEL_STATE,2).jump('done',5)
    s.emit(96).emit(105,0x4000,0x4001);music(s,1088)
    for z in range(265,269):s.compare(0x4001,z).jump(f'approach{z}',1)
    s.jump('approach266')
    for z in range(265,269):s.label(f'approach{z}').movement(BLUE,f'walk{z}').emit(95).jump('battle')
    s.label('battle').movement(255,'face_blue').emit(95).msg(0)
    selected_battle(s,trainers,0,'result');s.label('result')
    s.emit(220,0x800C).compare(0x800C,1).jump('won',1).msg(2);end(s)
    s.label('won').msg(1).msg(3).movement(BLUE,'leave').emit(95).emit(30,R22_DONE).emit(30,R22_HIDE).emit(101,BLUE).emit(82);end(s)
    s.label('done').emit(2)
    for z in range(265,269):
        m=([(12,266-z)] if z<266 else [(13,z-266)] if z>266 else [])+[(15,2),(3,1)];s.moves(f'walk{z}',m)
    return s.moves('face_blue',[(2,1)]).moves('leave',[(13,1),(15,2),(13,5)]).finish()


def route_init(reload=False):
    s=Script().emit(32,R22_DONE).jump('hide',1).emit(31,R22_HIDE)
    if reload:s.emit(32,R22_MIGRATED).jump('finish',1).emit(100,BLUE)
    s.jump('finish').label('hide').emit(30,R22_HIDE)
    return s.label('finish').emit(30,R22_MIGRATED).emit(2).finish()


def gate_guard(message,direction,interaction=False):
    s=Script().emit(96)
    if interaction:s.emit(104)
    s.msg(message)
    if not interaction:s.movement(255,'back').emit(95)
    end(s)
    if not interaction:s.moves('back',[(direction,1)])
    return s.finish()


def patch(rom):
    main=rom.loadArm9();data=main.sections[0].data=bytearray(main.sections[0].data);old_end=main.sections[1].ramAddress+len(main.sections[1].data)
    from shiny_charm import patch_engine,patch_item,unlock_shiny_locks
    engine=patch_engine(main)
    unlock_shiny_locks(rom,main,engine)
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in ['a/0/1/2','a/0/2/7','a/0/3/2']};scripts,texts,events=arcs.values();report={'engine':engine,'player_shiny':player_shiny_odds(main,int(engine['shiny_roll_hook'],16)),'experience':experience_hook(rom,main),'blue_properties':blue_properties_hook(main,int(engine['shiny_roll_hook'],16))}
    patch_item(rom,main,texts)
    original_texts=ndspy.narc.NARC(ndspy.rom.NintendoDSRom.fromFile(str(BASE)).files[rom.filenames.idOf('a/0/2/7')]);active={struct.unpack_from('<H',data,TABLE+m*24+10)[0] for m in range(540)};repaired={}
    for tid in sorted(active):
        if tid<len(original_texts.files):continue
        key,msg=decode_messages(texts.files[tid]);new=[repair_scroll(w) for w in msg]
        if new!=msg:repaired[tid]=len(texts.files);texts.files.append(encode_messages(key,new))
    for m in range(540):
        p=TABLE+24*m+10;tid=struct.unpack_from('<H',data,p)[0]
        if tid in repaired:struct.pack_into('<H',data,p,repaired[tid])
    mappings=[]
    def install(m,bank,lines=None,groups=None,init=None):
        rec=TABLE+m*24;old_sid,old_iid,old_tid=struct.unpack_from('<3H',data,rec+6);old_eid=struct.unpack_from('<H',data,rec+16)[0]
        sid=len(scripts.files);scripts.files.append(script_bank(bank));iid=old_iid
        if init is not None:iid=len(scripts.files);scripts.files.append(init)
        tid=old_tid
        if lines is not None:tid=len(texts.files);texts.files.append(encode_text(lines,PH))
        eid=old_eid
        if groups is not None:eid=len(events.files);events.files.append(events_encode(groups))
        struct.pack_into('<3H',data,rec+6,sid,iid,tid);struct.pack_into('<H',data,rec+16,eid);mappings.append(dict(map=m,script=sid,init=iid,text=tid,event=eid))
    def current(m):
        rec=TABLE+m*24;sid,iid,tid=struct.unpack_from('<3H',data,rec+6);eid=struct.unpack_from('<H',data,rec+16)[0];return split_bank(scripts.files[sid]),tid,events_decode(events.files[eid])
    tf=rom.filenames.idOf('a/0/5/5');pf=rom.filenames.idOf('a/0/5/6');trainers=ndspy.narc.NARC(rom.files[tf]);parties=ndspy.narc.NARC(rom.files[pf]);key,names=decode_messages(texts.files[729]);assert len(trainers.files)==743
    lab_trainers={54:741,133:742};route_trainers={}
    for stage,target,level in [('lab',lab_trainers,5),('route22',route_trainers,8)]:
        for species in [54,133]:
            for gender,override in [('male',1),('female',2)]:
                target[f'{species}_{gender}']=len(trainers.files);row=bytearray(trainers.files[742]);row[0]=0;row[3]=1 if stage=='lab' else 2;trainers.files.append(row)
                team=(struct.pack('<4H',0,9,21,0) if stage=='route22' else b'')+struct.pack('<BB3H',0,override,level,species,0)
                parties.files.append(team);names.append(names[742])
    lab_trainers[54]=lab_trainers['54_male'];lab_trainers[133]=lab_trainers['133_female']
    route_trainers[54]=route_trainers['54_male'];route_trainers[133]=route_trainers['133_female']
    rom.files[tf]=trainers.save();rom.files[pf]=parties.save();texts.files[729]=encode_messages(key,names)
    bank,tid,groups=current(505);bank[0]=oak_parcel(34,51,True);bank[12]=rival_battle(lab_trainers,battle_emitter=selected_battle);bank[16]=random_togepi_choice();install(505,bank)
    from player_pc import script as pc_script
    bank,tid,groups=current(506);bank[1]=pc_script(evolution_items=True,shiny_charm=True)
    key,pc_messages=decode_messages(texts.files[tid]);assert len(pc_messages)==40
    pc_messages.extend(decode_messages(encode_text(["That Key Item can't be discarded."],PH))[1]);newtid=len(texts.files);texts.files.append(encode_messages(key,pc_messages));struct.pack_into('<H',data,TABLE+506*24+10,newtid);install(506,bank)
    bank,tid,groups=current(504);lines=["Hi {PLAYER}! {RIVAL} is out at Grandpa's lab.","{RIVAL} is starting his journey, just like you. Good luck to both of you!","Spending time with your POKEMON makes them more friendly to you."]
    s=Script().emit(96).emit(104).compare(PARCEL_STATE,2).jump('after',1).msg(0);end(s);s.label('after').msg(1).msg(2);bank[0]=end(s).finish();install(504,bank,lines)
    bank,tid,groups=current(50);key,msg=decode_messages(texts.files[tid]);newidx=len(msg);msg.extend(decode_messages(encode_text(["The TRAINER HOUSE isn't open yet."],PH))[1]);newtid=len(texts.files);texts.files.append(encode_messages(key,msg));struct.pack_into('<H',data,TABLE+50*24+10,newtid);bank[7]=talk(newidx)
    for i,row in enumerate(groups[1]):
        if struct.unpack_from('<H',row)[0]==2:b=bytearray(row);struct.pack_into('<H',b,2,9);groups[1][i]=b
    install(50,bank,groups=groups)
    _,_,groups=current(27);groups[1]=[actor(BLUE,375,1,979,266,R22_HIDE,3)];groups[3]=[struct.pack('<Hhh5H',1,ROUTE_X,265,1,4,0,0,BOUNDARY)];groups[0]=[struct.pack('<HHiiiH2x',2,1,938,264,0,4)];bank=[rival_scene(route_trainers),talk(4),route_init(),route_init(True)];init=struct.pack('<BHHBHH',2,3,0,3,4,0)+b'\0\0';install(27,bank,R22_LINES,groups,init)
    # Intercept in front of the east-side guard, and push east back toward
    # Route 22. The native Johto-ending corridors remain inaccessible.
    _,_,groups=current(299);groups[1]=groups[1][:3]
    for i,row in enumerate(groups[1]):b=bytearray(row);struct.pack_into('<H',b,10,4+i);groups[1][i]=b
    groups[3]=[struct.pack('<Hhh5H',1,15,8,1,4,0,0,BOUNDARY),trigger(2,11,17,1,BOUNDARY,0),struct.pack('<Hhh5H',3,9,8,1,4,0,0,BOUNDARY)]
    lines=["This path leads to Johto. You can't go through here yet.","Only Trainers with all eight Kanto BADGEs may enter the POKEMON LEAGUE.","The path to MT.SILVER is closed right now."]
    bank=[gate_guard(0,15),gate_guard(1,13),gate_guard(2,15),gate_guard(1,13,True),gate_guard(2,15,True),gate_guard(0,15,True),command(2)];init=struct.pack('<BHHBHH',2,7,0,3,7,0)+b'\0\0';install(299,bank,lines,groups,init)
    for p,a in arcs.items():rom.files[rom.filenames.idOf(p)]=a.save()
    assert struct.unpack_from('<I',data,0xD2C68)[0]==old_end;main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',data,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    report.update(mappings=mappings,repaired_message_banks=repaired,rival_trainers=route_trainers,lab_trainers=lab_trainers,rival_party={'shared':{'species':21,'level':9},'starter_level':8,'rule':'saved lab choice; Togepi chooses Psyduck/Eevee uniformly; legacy Togepi keeps Eevee'},route22_position=[979,266],flags={'done':R22_DONE,'hide':R22_HIDE,'migration':R22_MIGRATED,'rival_picked':RIVAL_PICKED,'rival_psyduck':RIVAL_DUCK,'rival_female':RIVAL_FEMALE});return report


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-012.nds';assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    old=ndspy.rom.NintendoDSRom.fromFile(str(source));rom=ndspy.rom.NintendoDSRom.fromFile(str(source));report=patch(rom)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nRoute 22 corrections prototype 013\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner);assert rom.arm7==old.arm7
    target=PROJECT/'build/yellow-heartgold-prototype-013.nds';target.write_bytes(rom.save());patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/progression-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True);subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True);assert sha(decoded.read_bytes())==sha(target.read_bytes())
    report.update(version='013',base_version='012',input_sha256=INPUT_SHA,output_sha256=sha(target.read_bytes()),patch_sha256=sha(patchfile.read_bytes()),changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b]);(PROJECT/'build/progression-cleanup-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
