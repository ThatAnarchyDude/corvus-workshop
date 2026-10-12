"""Yellow's Nugget Bridge on retained HG terrain, cumulative from 0022."""
import json,struct
import ndspy.narc
from build_rom import PROJECT
from opening import Script,actor,events_decode,events_encode,script_bank,encode_text,end,trigger
from parcel_quest import PH,split_bank
from prototype import decode_messages,encode_messages
from forest_progression import expanded_common,SLOT_MAP,pickup
from viridian_tutorial import TABLE
from starter_properties import CMD_TABLE,append_code
from cerulean import rival_scene,RIVAL_HIDE,RIVAL_STATE
from cerulean_tm import patch as tm_patch
from save_compatibility import assert_persistent
DATA=json.loads((PROJECT/'data/route24.json').read_text())
MAP=28
NUGGET_GIVEN,ROCKET_BEAT,CHARMANDER_GIVEN,TM_TAKEN,ROUTE_REFRESHED,BLUE_REFRESHED=range(0xA8D,0xA93)
ROUTE_REFRESH_STATE,BLUE_REFRESH_STATE,NUGGET_STATE=0x4146,0x4147,0x4148
TM_ITEM=122
RECRUITER=6

def recruiter(trainers,rocket):
    s=Script().emit(96).emit(105,0x4000,0x4001).emit(32,ROCKET_BEAT).jump('after',1)
    for trainer in trainers:s.emit(38,trainer).jump('not_ready',5)
    s.compare(0x4001,74).jump('greet',5)
    for x in range(1325,1330):s.compare(0x4000,x).jump('align'+str(x),1)
    s.jump('greet')
    for x in range(1325,1330):s.label('align'+str(x)).movement(RECRUITER,'approach'+str(x)).emit(95).jump('greet')
    s.label('greet').emit(32,NUGGET_GIVEN).jump('join',1).msg(0).msg(1)
    s.emit(125,92,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,NUGGET_GIVEN).emit(78,1185).msg(2).emit(79)
    s.label('join').msg(3).emit(213,rocket,0);s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5)
    s.emit(36,rocket).emit(30,ROCKET_BEAT).emit(41,NUGGET_STATE,1).msg(4).msg(5).jump('return')
    s.label('after').msg(5);end(s)
    s.label('not_ready').msg(6).jump('back')
    s.label('full').msg(7).jump('return_back')
    s.label('lost').emit(219);end(s)
    s.label('return_back').emit(41,0x8006,1).jump('return_start')
    s.label('return').emit(41,0x8006,0)
    s.label('return_start').compare(0x4001,74).jump('finish',5)
    for x in range(1325,1330):s.compare(0x4000,x).jump('restore_branch'+str(x),1)
    s.jump('finish')
    for x in range(1325,1330):s.label('restore_branch'+str(x)).movement(RECRUITER,'restore'+str(x)).emit(95).jump('finish')
    s.label('finish').compare(0x8006,1).jump('back',1);end(s)
    s.label('back').compare(0x4001,74).jump('done',5).movement(255,'back_step').emit(95)
    s.label('done');end(s)
    for x in range(1325,1330):
        s.moves('approach'+str(x),([(14,1327-x)] if x<1327 else [(15,x-1327)] if x>1327 else [])+[(1,1)])
        s.moves('restore'+str(x),([(15,1327-x)] if x<1327 else [(14,x-1327)] if x>1327 else [])+[(1,1)])
    return s.moves('back_step',[(13,1)]).finish()

def damian():
    s=Script().emit(73,1500).emit(96).emit(104).emit(32,CHARMANDER_GIVEN).jump('after',1).msg(8)
    s.emit(63,0x800C).compare(0x800C,0).jump('decline',5)
    s.emit(137,4,10,0,0,0,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,CHARMANDER_GIVEN).emit(76,4,0).emit(77).emit(78,1185).msg(9).emit(79);end(s)
    s.label('after').msg(11);end(s)
    s.label('decline').msg(10);end(s)
    s.label('full').msg(12);return end(s).finish()

def refresh_hook(main,ids,marker):
    d=main.sections[0].data;previous=struct.unpack_from('<I',d,CMD_TABLE+4)[0]
    checks=''.join(f'ldrb r2,[r1,#{i}]\ncmp r2,#{value}\nbne delegate\n' for i,value in enumerate(struct.pack('<I',marker)))
    if len(ids)>16 and ids==list(range(len(ids))):
        calls=f'movs r6,#0\nloop:\nmovs r0,r5\nmovs r1,r6\nbl 0x0205EE60\ncmp r0,#0\nbeq next\nbl 0x0205E3CC\nnext:\nadds r6,#1\ncmp r6,#{len(ids)}\nblo loop\n'
    else:
        calls=''.join(f'movs r0,r5\nmovs r1,#{i}\nbl 0x0205EE60\ncmp r0,#0\nbeq next{i}\nbl 0x0205E3CC\nnext{i}:\n' for i in ids)
    source='''push {r4,r5,r6,lr}
movs r4,r0
ldr r1,[r4,#8]
cmp r1,#0
beq delegate
'''+checks+'''adds r1,#4
str r1,[r4,#8]
adds r4,#128
ldr r4,[r4]
ldr r5,[r4,#60]
'''+calls+'''movs r0,#0
pop {r4,r5,r6,pc}
delegate:
movs r0,r4
ldr r3,previous
blx r3
pop {r4,r5,r6,pc}
.align 2
previous: .word '''+str(previous)+'\n'
    address,code=append_code(main,source);struct.pack_into('<I',d,CMD_TABLE+4,address|1)
    return dict(hook=hex(address),bytes=len(code),marker=hex(marker),removed_ids=ids,previous=hex(previous))

def refresh_script(flag,state,marker,actors):
    s=Script().emit(32,flag).jump('done',1).emit(1);s.data.extend(struct.pack('<I',marker))
    for obj,hide in actors:
        if hide:s.emit(32,hide).jump('skip'+str(obj),1)
        s.emit(100,obj)
        if hide:s.label('skip'+str(obj))
    return s.emit(30,flag).label('done').emit(41,state,1).emit(2).finish()

def init_header(reset,refresh,state):
    return struct.pack('<BHHBHHBI',2,reset,0,3,reset,0,1,1)+b'\0'+struct.pack('<4H',state,0,refresh,0)

def patch(rom):
    flags=(NUGGET_GIVEN,ROCKET_BEAT,CHARMANDER_GIVEN,TM_TAKEN,ROUTE_REFRESHED,BLUE_REFRESHED)
    for flag in flags:
        assert_persistent(flag);assert not 0xAA0<=flag<0xB00,'Daily flags must not be used for progression'
    tm=dict(item=TM_ITEM,move=86,index=105,number=45,name='THUNDER WAVE',key='THUNDER_WAVE',template=400,later_index=72,description='A weak electric charge paralyzes the target.')
    report={'tm':tm_patch(rom,(tm,),{'THUNDER_WAVE':DATA['thunder_wave_compatible_species']},'Thunder Wave')}
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7','a/0/5/7','a/1/3/1')
    scripts,texts,events,trainers,parties,wild,trtable,offsets=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    key,names=decode_messages(texts.files[729]);bkey,btexts=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0]);records=[]
    for t in DATA['trainers']:
        tid=len(trainers.files);assert 0x550+tid<0xAA0
        row=bytearray(trainers.files[t['template']]);row[0]=1;row[1]=t['trainer_class'];row[3]=len(t['team']);row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0;trainers.files.append(row)
        parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in t['team']));names.append([65535])
        while len(ofs)<2*(tid+1):ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,tid*2,len(table))
        for kind,suffix in enumerate(('BattleText','EndBattleText','AfterBattleText')):
            label=t['dialogue']+suffix;line=DATA['messages'].get(label,DATA['messages']['Route24CooltrainerM1DefeatedText'] if kind==1 else DATA['messages']['Route24CooltrainerM1YouCouldBecomeATopLeaderText'])
            table.extend(struct.pack('<2H',tid,kind));btexts.extend(decode_messages(encode_text([line],PH))[1])
        records.append(dict(id=tid,defeat_flag=0x550+tid,**t))
    texts.files[729]=encode_messages(key,names);texts.files[728]=encode_messages(bkey,btexts);trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    rec=TABLE+MAP*24;old=tuple(struct.unpack_from('<3H',d,rec+6))+(struct.unpack_from('<H',d,rec+16)[0],d[rec]);g=events_decode(events.files[old[3]]);g[0]=[];g[1]=[]
    for obj,t in enumerate(records[:6]):
        b=bytearray(actor(obj,t['sprite'],3000+t['id']-1,t['x'],t['z'],0,t['facing']));struct.pack_into('<H',b,6,1);struct.pack_into('<H',b,14,4);struct.pack_into('<i',b,28,3*65536);g[1].append(bytes(b))
    for obj,sprite,entry,x,z,hide in [(6,345,1,1327,73,0),(7,87,3,1327,66,TM_TAKEN),(8,317,2,1320,66,0)]:
        b=bytearray(actor(obj,sprite,entry,x,z,hide,1));struct.pack_into('<i',b,28,3*65536);g[1].append(bytes(b))
    g[3]=[trigger(1,1325,74,5,NUGGET_STATE,0)]
    marker=0x4D502328;refresh=refresh_hook(main,list(range(9)),marker)
    reset=Script().emit(41,ROUTE_REFRESH_STATE,0).emit(41,NUGGET_STATE,0).emit(32,ROCKET_BEAT).jump('done',5).emit(41,NUGGET_STATE,1).label('done').emit(2).finish()
    bank=[recruiter([t['id'] for t in records[:5]],records[6]['id']),damian(),pickup(TM_ITEM,TM_TAKEN,13,7),refresh_script(ROUTE_REFRESHED,ROUTE_REFRESH_STATE,marker,[(i,TM_TAKEN if i==7 else 0) for i in range(9)]),reset]
    m=DATA['messages'];lines=[m['Route24CooltrainerM1YouBeatOurContestText'],m['Route24CooltrainerM1YouJustEarnedAPrizeText'],m['Route24CooltrainerM1ReceivedNuggetText'],m['Route24CooltrainerM1JoinTeamRocketText'],m['Route24CooltrainerM1DefeatedText'],m['Route24CooltrainerM1YouCouldBecomeATopLeaderText'],'Please beat all five contest trainers first.',m['Route24CooltrainerM1NoRoomText'],m['Route24DamianText1'],m['Route24DamianText2'],m['Route24DamianText3'],m['Route24DamianText4'],'Your party is full. Make room for CHARMANDER and come back.','You found TM45 (THUNDER WAVE)!','Your BAG is full. Make room and come back.']
    sid=len(scripts.files);scripts.files.append(script_bank(bank));iid=len(scripts.files);scripts.files.append(init_header(5,4,ROUTE_REFRESH_STATE));tid=len(texts.files);texts.files.append(encode_text(lines,PH));eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid)
    w=bytearray(wild.files[old[4]]);slots=[DATA['wild_slots'][i] for i in SLOT_MAP];species=[p['species'] for p in slots];w[0]=25;w[1:6]=bytes(5);w[8:20]=bytes(p['level'] for p in slots)
    for period in range(3):struct.pack_into('<12H',w,20+24*period,*species)
    for at in (0x5C,0x60,0x64,0x68,0xBC):struct.pack_into('<2H',w,at,species[0],species[1])
    wid=len(wild.files);assert wid<255;wild.files.append(w);d[rec]=wid
    dispatch=[]
    for code in (3000,5000):
        hits=[at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==code and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)];assert len(hits)==1;dispatch.append(hits[0])
    previous=struct.unpack_from('<H',d,dispatch[0]+2)[0];common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[previous],records[-1]['id']))
    for at in dispatch:struct.pack_into('<H',d,at+2,common)
    city=TABLE+52*24;csid,ciid=struct.unpack_from('<2H',d,city+6);ceid=struct.unpack_from('<H',d,city+16)[0];cg=events_decode(events.files[ceid]);cb=split_bank(scripts.files[csid])
    blue={f'{s}_{gender}':n for s,gender,n in [(54,'male',782),(54,'female',783),(133,'male',784),(133,'female',785)]};blue.update({54:782,133:785})
    cb[0]=rival_scene(blue,range(1325,1330));cb[12]=Script().emit(41,BLUE_REFRESH_STATE,0).finish()+cb[12]
    for i,b in enumerate(cg[1]):
        if struct.unpack_from('<H',b)[0]==30:
            b=bytearray(b);struct.pack_into('<2H',b,24,1329,96);struct.pack_into('<i',b,28,3*65536);cg[1][i]=bytes(b)
    cg[3]=[trigger(1,1325,100,5,RIVAL_STATE,0)]
    bmarker=0x4D502352;brefresh=refresh_hook(main,[30],bmarker)
    cb.append(refresh_script(BLUE_REFRESHED,BLUE_REFRESH_STATE,bmarker,[(30,RIVAL_HIDE)]));newcsid=len(scripts.files);scripts.files.append(script_bank(cb));newciid=len(scripts.files);scripts.files.append(init_header(13,len(cb),BLUE_REFRESH_STATE));newceid=len(events.files);events.files.append(events_encode(cg));struct.pack_into('<2H',d,city+6,newcsid,newciid);struct.pack_into('<H',d,city+16,newceid)
    for path,a in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=a.save()
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    report.update(map=MAP,script=sid,init=iid,text=tid,event=eid,wild=wid,original=old,trainers=records,common=common,flags=list(flags),refresh=refresh,blue_bridge=dict(map=52,script=newcsid,init=newciid,event=newceid,old=(csid,ciid,ceid),trigger=[1325,100,5],actor=[1329,96,3],refresh=brefresh),terrain_unchanged=True)
    return report
