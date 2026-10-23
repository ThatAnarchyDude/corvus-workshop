"""Yellow Route 25 and Bill's separation scene on retained HeartGold maps."""
import json,struct
import ndspy.narc
from build_rom import PROJECT
from opening import Script,actor,events_decode,events_encode,script_bank,encode_text,end,talk
from parcel_quest import PH
from prototype import decode_messages,encode_messages
from forest_progression import expanded_common,SLOT_MAP,pickup
from viridian_tutorial import TABLE
from route24 import refresh_hook,refresh_script,init_header
from cerulean_tm import patch as tm_patch
from cerulean import BILL_STATE
from save_compatibility import assert_persistent

DATA=json.loads((PROJECT/'data/route25.json').read_text())
ROUTE_REFRESHED,TM_TAKEN,SEPARATED,TICKET_GIVEN,HOUSE_REFRESHED,HIDE_MON,HIDE_EMERGING,HIDE_BILL=range(0xA94,0xA9C)
# 4152..4165 are the bedroom PC's storage slots; never use them as scenes.
ROUTE_FRAME,HOUSE_FRAME,PHASE=0x414A,0x414B,0x414C
TM_ITEM,TICKET=123,456
MON,EMERGING,BILL=0,1,2
HIDDEN=(dict(script=8107,item=38,name='ETHER',x=1393,z=43),
        dict(script=8199,item=40,name='ELIXIR',x=1339,z=40))

def ticket(s):
    s.emit(32,TICKET_GIVEN).jump('after',1).msg(4)
    s.emit(125,TICKET,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,TICKET_GIVEN).emit(78,1186).msg(5).emit(79).msg(6);end(s)
    s.label('after').msg(7);end(s)
    s.label('full').msg(8);return end(s)

def bill_talk():
    return ticket(Script().emit(73,1500).emit(96).emit(104)).finish()

def ask_bill():
    s=Script().emit(73,1500).emit(96).emit(104).msg(0).emit(63,0x800C)
    s.compare(0x800C,0).jump('help',1).msg(2)
    s.label('help').msg(1).emit(105,0x4000,0x4001)
    # If addressed from above, visibly walk around the player instead.
    s.compare(0x4000,4).jump('check_north',1).jump('direct')
    s.label('check_north').compare(0x4001,5).jump('around',1)
    s.label('direct').movement(MON,'enter').emit(95).jump('inside')
    s.label('around').movement(MON,'detour').emit(95)
    s.label('inside').emit(30,HIDE_MON).emit(101,MON).emit(41,PHASE,1);end(s)
    return s.moves('enter',[(12,3)]).moves('detour',[(15,1),(12,2),(14,1),(12,1)]).finish()

def computer():
    s=Script().emit(73,1547).emit(96).emit(32,SEPARATED).jump('collection',1)
    s.compare(PHASE,1).jump('ready',1).msg(9);end(s)
    s.label('ready').msg(10)
    # Yellow's switch, tink/shrink/tink sequence, using HG's native effects.
    s.emit(81,0).emit(73,1548).emit(75,1548).emit(3,32,0x800C)
    s.emit(73,1613).emit(75,1613).emit(3,80,0x800C)
    # FlashEffect (181) enables the field move's darkness mask permanently.
    # A short native white fade provides the machine flash and restores it.
    s.emit(174,3,3,0,0x7FFF).emit(175).emit(73,1614).emit(75,1614)
    s.emit(174,3,3,1,0x7FFF).emit(175).emit(3,48,0x800C)
    s.emit(73,1613).emit(75,1613).emit(3,32,0x800C).emit(78,1188).emit(79).emit(82)
    s.emit(31,HIDE_EMERGING).emit(100,EMERGING)
    s.movement(EMERGING,'exit').emit(95)
    s.emit(30,HIDE_EMERGING).emit(101,EMERGING).emit(31,HIDE_BILL).emit(100,BILL)
    s.emit(30,SEPARATED).emit(41,PHASE,2).emit(41,BILL_STATE,1)
    ticket(s)
    s.label('collection').msg(11).label('menu').msg(12)
    s.emit(69);s.data.extend(bytes([1,1,1,1]));s.emit(0x8006)
    for i in range(5):s.emit(70,13+i,255,i)
    s.emit(71).emit(53)
    for i in range(4):s.compare(0x8006,i).jump('portrait'+str(i),1)
    end(s)
    for i,species in enumerate((133,136,135,134)):
        s.label('portrait'+str(i)).emit(452,species,0).emit(76,species,0).emit(77).msg(13+i).emit(453).jump('menu')
    return s.moves('exit',[(13,2),(14,6),(13,2),(2,1)]).finish()

def house_init():
    s=Script().emit(41,HOUSE_FRAME,0).emit(30,HIDE_EMERGING).emit(32,SEPARATED).jump('helped',1)
    s.emit(30,HIDE_BILL).compare(PHASE,1).jump('waiting',1).emit(31,HIDE_MON).emit(2)
    s.label('waiting').emit(30,HIDE_MON).emit(2)
    return s.label('helped').emit(30,HIDE_MON).emit(31,HIDE_BILL).emit(41,BILL_STATE,1).emit(41,PHASE,2).emit(2).finish()

def patch(rom):
    flags=(ROUTE_REFRESHED,TM_TAKEN,SEPARATED,TICKET_GIVEN,HOUSE_REFRESHED,HIDE_MON,HIDE_EMERGING,HIDE_BILL)
    for f in flags:
        assert_persistent(f);assert f<0xAA0
    tm=dict(item=TM_ITEM,move=69,index=106,number=19,name='SEISMIC TOSS',key='SEISMIC_TOSS',template=349,later_index=30,description="The target is thrown using gravity. Damage equals the user's level.")
    report={'tm':tm_patch(rom,(tm,),{'SEISMIC_TOSS':DATA['seismic_toss_compatible_species']},'HeartGold Brick Break compatibility')}
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7','a/0/5/7','a/1/3/1','a/0/4/1','a/0/6/5')
    scripts,texts,events,trainers,parties,wild,trtable,offsets,matrices,lands=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    key,names=decode_messages(texts.files[729]);bkey,btexts=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0]);records=[]
    for t in DATA['trainers']:
        tid=len(trainers.files);assert 0x550+tid<0xAA0
        row=bytearray(trainers.files[t['template']]);row[0]=1;row[1]=t['trainer_class'];row[3]=len(t['team']);row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0;trainers.files.append(row)
        parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in t['team']));names.append([65535])
        while len(ofs)<2*(tid+1):ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,tid*2,len(table))
        for kind,suffix in enumerate(('BattleText','EndBattleText','AfterBattleText')):
            table.extend(struct.pack('<2H',tid,kind));btexts.extend(decode_messages(encode_text([DATA['messages'][t['dialogue']+suffix]],PH))[1])
        records.append(dict(id=tid,defeat_flag=0x550+tid,**t))
    texts.files[729]=encode_messages(key,names);texts.files[728]=encode_messages(bkey,btexts);trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    def install(mid,g,bank,lines,init):
        rec=TABLE+mid*24;old=dict(script=struct.unpack_from('<H',d,rec+6)[0],init=struct.unpack_from('<H',d,rec+8)[0],text=struct.unpack_from('<H',d,rec+10)[0],event=struct.unpack_from('<H',d,rec+16)[0])
        sid=len(scripts.files);scripts.files.append(script_bank(bank));iid=len(scripts.files);scripts.files.append(init);tid=len(texts.files);texts.files.append(encode_text(lines,PH));eid=len(events.files);events.files.append(events_encode(g))
        struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid)
        return dict(map=mid,script=sid,init=iid,text=tid,event=eid,original=old)
    rec=TABLE+29*24;old_eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[old_eid]);g[1]=[];g[3]=[]
    for obj,t in enumerate(records):
        b=bytearray(actor(obj,t['sprite'],3000+t['id']-1,t['x'],t['z'],0,t['facing']));struct.pack_into('<H',b,6,1);struct.pack_into('<H',b,14,t['vision']);g[1].append(bytes(b))
    # HG's old ball was placed on a wall tile in this retained matrix.
    # Put Yellow's reward in the walkable alcove above its Camper instead.
    g[1].append(actor(9,87,1,1368,36,TM_TAKEN,0))
    # Native hidden-item IDs drive both A-button pickups and Dowsing. Reuse
    # Route 25's old ID and an unused one; never share rewards with Johto.
    for map_id in range(540):
        if map_id==29:continue
        eid=struct.unpack_from('<H',d,TABLE+map_id*24+16)[0]
        for bg in events_decode(events.files[eid])[0]:
            sid,kind=struct.unpack_from('<2H',bg)
            assert kind!=2 or sid not in {v['script'] for v in HIDDEN},(map_id,sid)
    itcm=main.sections[1].data
    prefix=struct.pack('<HBBHH',17,1,0,0,0)+struct.pack('<HBBHH',92,1,0,0,1)+struct.pack('<HBBHH',92,1,0,0,225)
    assert itcm.count(prefix)==1;hidden_table=itcm.index(prefix)
    for reward in HIDDEN:
        rows=[at for at in range(hidden_table,hidden_table+231*8,8) if struct.unpack_from('<H',itcm,at+6)[0]==reward['script']-8000]
        assert len(rows)==1;struct.pack_into('<H',itcm,rows[0],reward['item'])
    g[0]=[struct.pack('<HHiiiH2x',2,0,1405,38,0,4)]+[struct.pack('<HHiiiH2x',v['script'],2,v['x'],v['z'],0,4) for v in HIDDEN]
    marker=0x4D502429;refresh=refresh_hook(main,list(range(32)),marker)
    bank=[pickup(TM_ITEM,TM_TAKEN,0,9),talk(2),refresh_script(ROUTE_REFRESHED,ROUTE_FRAME,marker,[(i,TM_TAKEN if i==9 else 0) for i in range(10)]),Script().emit(41,ROUTE_FRAME,0).emit(2).finish()]
    route=install(29,g,bank,['You found TM19 (SEISMIC TOSS)!','Your BAG is full. Make room and come back.',DATA['messages']['Route25BillSignText']],init_header(4,3,ROUTE_FRAME))
    old_wid=d[rec];w=bytearray(wild.files[old_wid]);slots=[DATA['wild_slots'][i] for i in SLOT_MAP];species=[p['species'] for p in slots];w[0]=15;w[1:6]=bytes(5);w[8:20]=bytes(p['level'] for p in slots)
    for period in range(3):struct.pack_into('<12H',w,20+24*period,*species)
    for at in (0x5C,0x60,0x64,0x68,0xBC):struct.pack_into('<2H',w,at,species[0],species[1])
    wid=len(wild.files);assert wid<255;wild.files.append(w);d[rec]=wid
    dispatch=[]
    for code in (3000,5000):
        hits=[at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==code and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)];assert len(hits)==1;dispatch.append(hits[0])
    previous=struct.unpack_from('<H',d,dispatch[0]+2)[0];common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[previous],records[-1]['id']))
    for at in dispatch:struct.pack_into('<H',d,at+2,common)
    # HG's Sea Cottage already contains both separation chambers and a PC.
    # Open only the four chamber-door floor tiles needed for visible entry.
    hrec=TABLE+440*24;old_mid=struct.unpack_from('<H',d,hrec+4)[0];matrix=bytearray(matrices.files[old_mid]);assert matrix[:4]==bytes([1,1,0,0]);at=5+matrix[4];old_lid=struct.unpack_from('<H',matrix,at)[0];land=bytearray(lands.files[old_lid]);opened=[]
    for x,z in ((4,3),(4,4),(10,3),(10,4)):
        p=20+2*(z*32+x);value=struct.unpack_from('<H',land,p)[0];assert value==0x8000;struct.pack_into('<H',land,p,0x0600);opened.append(dict(x=x,z=z,previous=value))
    lid=len(lands.files);lands.files.append(land);struct.pack_into('<H',matrix,at,lid);mid=len(matrices.files);matrices.files.append(matrix);struct.pack_into('<H',d,hrec+4,mid)
    old_eid=struct.unpack_from('<H',d,hrec+16)[0];g=events_decode(events.files[old_eid]);g[0]=[struct.pack('<HHiiiH2x',3,0,2,7,0,4)];g[3]=[]
    g[1]=[actor(MON,1003,1,4,6,HIDE_MON,1),actor(EMERGING,235,2,10,3,HIDE_EMERGING,1),actor(BILL,235,2,4,7,HIDE_BILL,2)]
    hmarker=0x4D5024BC;hrefresh=refresh_hook(main,list(range(32)),hmarker)
    m=DATA['messages'];labels=('BillsHouseBillImNotAPokemonText','BillsHouseBillUseSeparationSystemText','BillsHouseBillNoYouGottaHelpText','BillsHouseBillDontLeaveText','BillsHouseBillThankYouText')
    lines=[m[k] for k in labels]+['{PLAYER} received an S.S. TICKET!',m['BillsHouseBillWhyDontYouGoInsteadOfMeText'],m['BillsHouseBillCheckOutMyRarePokemonText'],'You have too much stuff, bud! Make room for the S.S. TICKET and talk to me again.',m['BillsHouseMonitorText'],m['BillsHouseInitiatedText'],m['BillsHousePokemonListText1'],m['BillsHousePokemonListText2'],'EEVEE','FLAREON','JOLTEON','VAPOREON','CANCEL']
    bank=[ask_bill(),bill_talk(),computer(),refresh_script(HOUSE_REFRESHED,HOUSE_FRAME,hmarker,[(MON,HIDE_MON),(EMERGING,HIDE_EMERGING),(BILL,HIDE_BILL)]),house_init()]
    house=install(440,g,bank,lines,init_header(5,4,HOUSE_FRAME))
    for path,a in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=a.save()
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    report.update(route=route,wild=wid,trainers=records,common=common,refresh=refresh,flags=list(flags),hidden=[dict(v,flag=0x320+v['script']-8000) for v in HIDDEN],hidden_table=hex(main.sections[1].ramAddress+hidden_table),house=dict(**house,matrix=mid,land=lid,original_matrix=old_mid,original_land=old_lid,opened_chambers=opened,refresh=hrefresh,ticket_item=TICKET,phase_var=PHASE,cerulean_bill_state=BILL_STATE),johto_unchanged=True,outdoor_terrain_unchanged=True)
    return report
