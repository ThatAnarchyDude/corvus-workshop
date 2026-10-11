"""Yellow's Cerulean story and services, with original HG events archived."""
import json,struct
import ndspy.narc
from build_rom import PROJECT
from opening import Script,actor,events_decode,events_encode,script_bank,encode_text,talk,end,trigger
from parcel_quest import PH,split_bank,append_bank
from prototype import decode_messages,encode_messages,thumb_bl
from viridian_tutorial import TABLE
from forest_progression import expanded_common
from progression_cleanup import selected_battle
from starter_properties import append_code
from escort import music
from pewter_interiors import shop,cry_dialogue

DATA=json.loads((PROJECT/'data/cerulean.json').read_text());M=DATA['messages']
BLUE=30
RIVAL_DONE=0xB61
RIVAL_HIDE=0xB62
BULBA_GIVEN=0xB63
BULBA_HIDE=0xB64
THIEF_BEAT=0xB65
THIEF_HIDE=0xB66
POLICE_HIDE=0xB68
MISTY_TM=0xB69
RIVAL_STATE=0x4144
BILL_STATE=0x4145
CASCADE=9
CAVE_HIDE=0xB6A


def badge_house():
    s=Script().emit(73,1500).emit(96).emit(104).msg(0).label('menu').msg(1)
    s.emit(69);s.data.extend(bytes([1,1,0,1]));s.emit(0x8006)
    for i in range(9):s.emit(70,3+i,255,i)
    s.emit(71).emit(53)
    for i in range(8):s.compare(0x8006,i).jump(f'badge{i}',1)
    s.msg(2);end(s)
    for i in range(8):s.label(f'badge{i}').msg(12+i).jump('menu')
    return s.finish()


def random_dialogue(first,count,species=None):
    s=Script().emit(73,1500).emit(96).emit(104)
    if species is not None:s.emit(76,species,0).emit(77)
    s.emit(380,0x800C,count)
    for i in range(count):s.compare(0x800C,i).jump(f'text{i}',1)
    s.jump('text0')
    for i in range(count):s.label(f'text{i}').msg(first+i);end(s)
    return s.finish()


def misty(trainer,juniors):
    s=Script().emit(73,1500).emit(96).emit(104).emit(294,CASCADE,0x800C)
    s.compare(0x800C,1).jump('reward',1).msg(0).emit(213,trainer,0);s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5)
    s.emit(295,CASCADE).emit(36,trainer)
    for junior in juniors:s.emit(36,junior)
    s.msg(1).emit(78,1189).emit(79).msg(2)
    s.label('reward').emit(32,MISTY_TM).jump('advice',1)
    s.emit(125,119,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,MISTY_TM).emit(78,1185).msg(3).emit(79).msg(4);end(s)
    s.label('advice').msg(4);end(s)
    s.label('full').msg(5);end(s)
    s.label('lost').emit(219);return end(s).finish()


def guide():
    s=Script().emit(96).emit(104).emit(294,CASCADE,0x800C)
    s.compare(0x800C,1).jump('after',1).msg(6);end(s)
    s.label('after').msg(7);return end(s).finish()


def rival_scene(trainers):
    s=Script().emit(32,RIVAL_DONE).jump('done',1).emit(96).emit(105,0x4000,0x4001)
    music(s,1088)
    for x in range(1329,1333):s.compare(0x4000,x).jump('lane'+str(x),1)
    s.jump('lane1329')
    for x in range(1329,1333):s.label('lane'+str(x)).movement(BLUE,'approach'+str(x)).emit(95).jump('battle')
    s.label('battle').movement(255,'face').emit(95).msg(0)
    selected_battle(s,trainers,0,'result');s.label('result').emit(220,0x800C)
    s.compare(0x800C,1).jump('lost',5).msg(1).msg(3)
    music(s,1089)
    s.compare(0x4000,1329).jump('leave_right',1).movement(BLUE,'leave_left').emit(95).jump('finish')
    s.label('leave_right').movement(BLUE,'leave_right_path').emit(95)
    s.label('finish').emit(30,RIVAL_DONE).emit(30,RIVAL_HIDE).emit(101,BLUE).emit(41,RIVAL_STATE,1).emit(82);end(s)
    s.label('lost').msg(2).emit(219);end(s)
    s.label('done').emit(2)
    for x in range(1329,1333):
        moves=([(15,x-1329)] if x>1329 else [])+[(13,3),(1,1)]
        s.moves('approach'+str(x),moves)
    return s.moves('face',[(0,1)]).moves('leave_left',[(14,1),(13,6)]).moves('leave_right_path',[(15,1),(13,6)]).finish()


def city_init():
    s=Script().emit(32,RIVAL_DONE).jump('rival_hidden',1).emit(31,RIVAL_HIDE).jump('bill')
    s.label('rival_hidden').emit(30,RIVAL_HIDE).emit(41,RIVAL_STATE,1)
    s.label('bill').compare(BILL_STATE,1).jump('opened',1).emit(31,POLICE_HIDE).jump('finish')
    s.label('opened').emit(30,POLICE_HIDE)
    s.label('finish').emit(32,0x964).jump('champion',1).emit(31,CAVE_HIDE).emit(2)
    return s.label('champion').emit(30,CAVE_HIDE).emit(2).finish()


def melanie():
    s=Script().emit(73,1500).emit(96).emit(104).emit(32,BULBA_GIVEN).jump('after',1).msg(0)
    # Yellow checked its special Pikachu happiness. In this three-starter game
    # use native friendship of the current lead, keeping Yellow's threshold.
    s.emit(382,0x800C,0).compare(0x800C,147).jump('done',0)
    s.msg(1).emit(63,0x800C).compare(0x800C,0).jump('decline',5)
    s.emit(332,0x800C).compare(0x800C,6).jump('full',1)
    s.emit(137,1,10,0,0,0,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,BULBA_GIVEN).emit(30,BULBA_HIDE).emit(101,2).emit(78,1185).msg(2).emit(79);end(s)
    s.label('after').msg(3);end(s)
    s.label('decline').msg(4);end(s)
    s.label('full').msg(8);end(s)
    s.label('done');return end(s).finish()


def thief(trainer):
    s=Script().emit(73,1500).emit(96).emit(104).emit(32,THIEF_BEAT).jump('reward',1)
    s.msg(0).emit(213,trainer,0);s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5).emit(30,THIEF_BEAT).msg(1)
    s.label('reward').msg(2).emit(125,355,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,THIEF_HIDE).emit(78,1185).msg(3).emit(79).movement(31,'leave').emit(95).emit(101,31);end(s)
    s.label('full').msg(4);end(s)
    s.label('lost').emit(219);end(s)
    return s.moves('leave',[(15,3),(13,5)]).finish()


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1')
    scripts,texts,events,trainers,parties,trtable,offsets=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    report={'maps':[],'trainers':[]};key,names=decode_messages(texts.files[729]);btkey,bt=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0])
    def trainer(template,team,dialogue,name=None):
        tid=len(trainers.files);row=bytearray(trainers.files[template]);row[0]=1;row[3]=len(team);row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0;trainers.files.append(row)
        parties.files.append(b''.join(struct.pack('<BB3H4H',0,gender,level,species,0,*moves) for species,level,moves,gender in team));names.append(names[template] if name is None else decode_messages(encode_text([name],PH))[1][0])
        while len(ofs)<2*(tid+1):ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,tid*2,len(table))
        for kind,text in enumerate(dialogue):table.extend(struct.pack('<2H',tid,kind));bt.extend(decode_messages(encode_text([text],PH))[1])
        report['trainers'].append(dict(id=tid,template=template,team=team));return tid
    female=trainer(297,[(118,19,[64,39,48,0],0)],[M['CeruleanGym'+x+'1'] for x in ('BattleText','EndBattleText','AfterBattleText')])
    swimmer=trainer(16,[(116,16,[145,0,0,0],0),(90,16,[33,110,0,0],0)],[M['CeruleanGym'+x+'2'] for x in ('BattleText','EndBattleText','AfterBattleText')])
    leader=trainer(254,[(120,18,[33,55,0,0],0),(121,21,[33,55,106,61],0)],[M['CeruleanGymMistyTM11ExplanationText']]*3)
    blue={};blue_first=len(trainers.files)
    for species in (54,133):
        for gender,value in [('male',1),('female',2)]:
            team=[(21,18,[64,45,43,31],0),(27,15,[10,28,0,0],0),(19,15,[33,39,98,158],0),(species,17,[10,39,55,50] if species==54 else [33,39,28,45],value)]
            blue[f'{species}_{gender}']=trainer(742,team,[M['CeruleanCityRivalPreBattleText'],M['CeruleanCityRivalDefeatedText'],M['CeruleanCityRivalIWentToBillsText']])
    blue[54]=blue['54_male'];blue[133]=blue['133_female']
    rocket=trainer(12,[(66,17,[2,67,43,0],0),(96,17,[1,95,50,93],0)],[M['CeruleanCityRocketText'],M['CeruleanCityRocketIGiveUpText'],M['CeruleanCityRocketIllReturnTheTMText']])
    texts.files[729]=encode_messages(key,names);texts.files[728]=encode_messages(btkey,bt);trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    # Preserve Blue's saved starter seed/rare rolls across his new records.
    site=0x02073440;at=site-0x02000000;old_hook=site+4+((int.from_bytes(d[at:at+2],'little')&2047)<<12)+((int.from_bytes(d[at+2:at+4],'little')&2047)<<1)
    # Sign-extend Thumb BL displacement.
    if old_hook-site-4 & (1<<22):old_hook-=1<<23
    source=(PROJECT/'asm/blue-starter-properties.s').read_text().replace('bl 0x02073604',f'bl {old_hook}').replace('first_trainer: .word 741',f'first_trainer: .word {blue_first}').replace('adds r1, #9','adds r1, #3').replace('bl 0x0201FD44\nlsls r0, r0, #20','bl 0x01FFCA64\nlsls r0, r0, #20').replace('cmp r0, #8','cmp r0, #16')
    hook,_=append_code(main,source);d[at:at+4]=thumb_bl(site,hook)
    # Yellow's Cascade Badge unlocks Cut. Preserve the existing Hive Badge
    # alternative and every native tree/map check, without granting badges.
    cut_site=0x02067F82;cut_at=cut_site-0x02000000
    assert d[cut_at:cut_at+4]==thumb_bl(cut_site,0x02028F98)
    cut_hook,_=append_code(main,'''push {r4,lr}
movs r4,r0
bl 0x02028F98
cmp r0,#0
bne done
movs r0,r4
movs r1,#9
bl 0x02028F98
done:
pop {r4,pc}
nop
''')
    d[cut_at:cut_at+4]=thumb_bl(cut_site,cut_hook)
    # Expand only the native common trainer dispatch aliases.
    dispatch=[]
    for trigger_id in (3000,5000):
        matches=[i for i in range(0,len(d)-6,2) if struct.unpack_from('<H',d,i)[0]==trigger_id and struct.unpack_from('<H',d,i+4)[0]==40 and struct.unpack_from('<H',d,i+2)[0]<len(scripts.files)]
        assert len(matches)==1;dispatch.append(matches[0])
    previous=struct.unpack_from('<H',d,dispatch[0]+2)[0];common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[previous],rocket))
    for pos in dispatch:struct.pack_into('<H',d,pos+2,common)
    def current(mid):
        rec=TABLE+mid*24;sid,iid,tid=struct.unpack_from('<3H',d,rec+6);eid=struct.unpack_from('<H',d,rec+16)[0]
        return events_decode(events.files[eid]),split_bank(scripts.files[sid]),(sid,iid,tid,eid)
    def install(mid,g,bank,lines,init=None,encoded=False):
        rec=TABLE+mid*24;old=tuple(struct.unpack_from('<3H',d,rec+6))+(struct.unpack_from('<H',d,rec+16)[0],)
        sid=len(scripts.files);scripts.files.append(bank if encoded else script_bank(bank));iid=len(scripts.files);scripts.files.append(init if init is not None else bytes(4));tid=len(texts.files);texts.files.append(lines if isinstance(lines,bytes) else encode_text(lines,PH));eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid);report['maps'].append(dict(map=mid,script=sid,init=iid,text=tid,event=eid,original=old));return sid
    g,_,_=current(427);actors={struct.unpack_from('<H',v)[0]:v for v in g[1]};g[1]=[]
    for obj,script in ((0,2),(2,3000+female-1),(5,3000+swimmer-1),(6,1)):
        row=bytearray(actors[obj]);struct.pack_into('<H',row,8,0);struct.pack_into('<H',row,10,script);g[1].append(bytes(row))
    g[0]=[struct.pack('<HHiiiH2x',3,0,8,21,0,0),struct.pack('<HHiiiH2x',3,0,12,21,0,0)];g[3]=[]
    labels=('CeruleanGymMistyPreBattleText','CeruleanGymMistyReceivedCascadeBadgeText','CeruleanGymMistyCascadeBadgeInfoText','CeruleanGymMistyReceivedTM11Text','CeruleanGymMistyTM11ExplanationText','CeruleanGymMistyTM11NoRoomText','CeruleanGymGymGuideChampInMakingText','CeruleanGymGymGuideBeatMistyText')
    install(427,g,[misty(leader,[female,swimmer]),guide(),talk(8)],[M[x] for x in labels]+['CERULEAN CITY POKEMON GYM\rLEADER: MISTY\rWinning trainers: {RIVAL}'])
    g,_,_=current(52);g[1]=[actor(0,322,2,1307,119),actor(1,325,3,1297,127),actor(3,332,4,1314,136),actor(4,323,5,1326,116),actor(5,330,6,1300,139),actor(BLUE,375,1,1329,102,RIVAL_HIDE,1),actor(32,349,7,1305,117,POLICE_HIDE,1),actor(33,322,8,1290,108,CAVE_HIDE),actor(34,327,14,1302,146,0,2),actor(35,1019,15,1301,146,0,3)]
    g[3]=[trigger(1,1329,106,4,RIVAL_STATE,0)]
    g[0]=[struct.pack('<HHiiiH2x',sid,0,x,z,0,4) for sid,x,z in ((9,1321,135),(10,1309,137),(11,1317,123),(12,1295,144))]
    # Retain original native hidden item event, which does not trigger on touch.
    oldbg=current(52)[0][0];g[0].extend(v for v in oldbg if struct.unpack_from('<H',v,2)[0]==2)
    labels=('CeruleanCityRivalPreBattleText','CeruleanCityRivalDefeatedText','CeruleanCityRivalVictoryText','CeruleanCityRivalIWentToBillsText','CeruleanCityCooltrainerMText','CeruleanCitySuperNerd2Text','CeruleanCityCooltrainerF2Text','CeruleanCityGuardText','CeruleanCitySuperNerd3Text','CeruleanCityGymSign','CeruleanCitySignText','CeruleanCityTrainerTipsText','CeruleanCityBikeShopSign')
    extra=('CeruleanCityCooltrainerF1ElectrodeUseSonicboomText','CeruleanCityCooltrainerF1ElectrodePunchText','CeruleanCityCooltrainerF1ElectrodeWithdrawText','CeruleanCityElectrodeTookASnoozeText','CeruleanCityElectrodeIsLoafingAroundText','CeruleanCityElectrodeTurnedAwayText','CeruleanCityElectrodeIgnoredOrdersText')
    bank=[rival_scene(blue),talk(4),talk(5),talk(4),talk(4),talk(6),talk(7),talk(8),talk(9),talk(10),talk(11),talk(12),city_init(),random_dialogue(13,3),random_dialogue(16,4,101)]
    install(52,g,bank,[M[x] for x in labels+extra],struct.pack('<BHHBHH',2,13,0,3,13,0)+b'\0\0')
    # Melanie's care home uses HG's western house, which already has Pokémon.
    g,_,_=current(431);g[1]=[actor(0,330,1,5,6),actor(2,428,2,2,6,BULBA_HIDE),actor(3,1006,3,5,3),actor(4,456,4,8,6)]
    labels=('MelanieText1','MelanieText2','MelanieText3','MelanieText4','MelanieText5','MelanieBulbasaurText','MelanieOddishText','MelanieSandshrewText')
    install(431,g,[melanie(),cry_dialogue(5,1),cry_dialogue(6,43),cry_dialogue(7,27)],[M[x] for x in labels]+['Your party is full. Make room for BULBASAUR and come back.'])
    # Native HG clinic services and Player PC item storage remain available.
    g,native,old=current(428);clinic_sid,_,clinic_tid=struct.unpack_from('<3H',d,TABLE+501*24+6);key,lines=decode_messages(texts.files[clinic_tid]);base=len(lines)
    lines.extend(decode_messages(encode_text([M['CeruleanPokecenterSuperNerdText'],M['CeruleanPokecenterGentlemanText']],PH))[1]);bank,entry=append_bank(scripts.files[clinic_sid],[native[0],talk(base),talk(base+1)])
    for i,row in enumerate(g[1]):
        obj=struct.unpack_from('<H',row)[0]
        if obj in (0,4,5):row=bytearray(row);struct.pack_into('<H',row,10,entry+(1 if obj==0 else 2 if obj==4 else 3));g[1][i]=bytes(row)
    g[0].append(struct.pack('<HHiiiH2x',11,0,11,12,0,0));install(428,g,bank,encode_messages(key,lines),scripts.files[old[1]],True)
    g,_,old=current(426);g[1]=g[1][:4];install(426,g,[shop(),talk(2),talk(0),talk(1)],[M['CeruleanMartCooltrainerMText'],M['CeruleanMartCooltrainerFText'],'Please speak to the clerk at the upper counter to buy or sell items.'],scripts.files[old[1]])
    g,_,_=current(430);g[1]=[actor(0,331,1,5,3)]
    badge_names=('BOULDER','CASCADE','THUNDER','RAINBOW','SOUL','MARSH','VOLCANO','EARTH')
    lines=[M['CeruleanBadgeHouseMiddleAgedManText'],M['CeruleanBadgeHouseMiddleAgedManWhichBadgeText'],M['CeruleanBadgeHouseMiddleAgedManVisitAnyTimeText']]+[x+' BADGE' for x in badge_names]+['CANCEL']+[M['CeruleanBadgeHouse'+x.title()+'BadgeText'] for x in badge_names]
    install(430,g,[badge_house()],lines)
    # The stolen-Dig quest is restored when the later Bill event opens the
    # robbed-house gate. Its native HG north-house interior remains usable.
    g,_,_=current(429);g[1]=[actor(0,347,1,5,5),actor(1,329,2,8,6)]
    labels=('CeruleanTrashedHouseFishingGuruTheyStoleATMText','CeruleanTrashedHouseFishingGuruWhatsLostIsLostText','CeruleanTrashedHouseGirlText')
    s=Script().emit(96).emit(104).emit(128,355,1,0x800C).compare(0x800C,1).jump('after',1).msg(0);end(s);s.label('after').msg(1);install(429,g,[end(s).finish(),talk(2)],[M[x] for x in labels])
    for path,arc in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=arc.save()
    struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    report.update(gym=dict(misty=leader,juniors=[female,swimmer],badge=CASCADE,tm_item=119,tm_flag=MISTY_TM,cut_hook=hex(cut_hook),cut_check_site=hex(cut_site)),rival=dict(trainers=blue,first=blue_first,properties_hook=hex(hook),previous_properties_hook=hex(old_hook),state=RIVAL_STATE,hide=RIVAL_HIDE,done=RIVAL_DONE,trigger=[1329,106,4]),bulbasaur=dict(species=1,level=10,lead_friendship_threshold=147,given=BULBA_GIVEN,hide=BULBA_HIDE),thief=dict(trainer=rocket,implemented=False,requires_bill=BILL_STATE),common_bank=common)
    return report
