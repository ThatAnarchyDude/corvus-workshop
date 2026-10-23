"""Yellow Route 4 on HeartGold terrain, cumulative from prototype 0018."""
import json,struct
import ndspy.narc
from build_rom import PROJECT
from opening import actor,events_decode,events_encode,script_bank,encode_text,talk
from parcel_quest import PH,split_bank
from prototype import decode_messages,encode_messages
from forest_progression import expanded_common,SLOT_MAP,pickup
from field_interaction_fixes import sign
from viridian_tutorial import TABLE

DATA=json.loads((PROJECT/'data/route4.json').read_text())
ITEM=118
ITEM_FLAG=0xB39


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7','a/0/5/7','a/1/3/1')
    scripts,texts,events,trainers,parties,wild,trtable,offsets=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    rec=TABLE+12*24;old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6);old_eid=struct.unpack_from('<H',d,rec+16)[0];old_wild=d[rec];g=events_decode(events.files[old_eid])
    t=DATA['trainer'];trainer=len(trainers.files);row=bytearray(trainers.files[t['template']]);row[0]=1;row[1]=t['class'];row[3]=3;row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0;trainers.files.append(row)
    parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in t['team']))
    key,names=decode_messages(texts.files[729]);names.append([65535]);texts.files[729]=encode_messages(key,names)
    key,bt=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0])
    while len(ofs)<2*(trainer+1):ofs.extend(struct.pack('<H',len(table)))
    struct.pack_into('<H',ofs,trainer*2,len(table))
    for kind,label in enumerate(('BattleText','EndBattleText','AfterBattleText')):
        table.extend(struct.pack('<2H',trainer,kind));bt.extend(decode_messages(encode_text([DATA['messages'][label]],PH))[1])
    texts.files[728]=encode_messages(key,bt);trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    tr=bytearray(actor(1,t['sprite'],3000+trainer-1,t['x'],t['z'],0,t['facing']));struct.pack_into('<H',tr,6,1);struct.pack_into('<H',tr,14,t['vision'])
    # This level-31 optional Lass is Yellow's actual team. Keep her off the
    # main eastbound path; no artificial progression barrier is introduced.
    g[1]=[tr,actor(3,87,2,1254,107,ITEM_FLAG,0)]
    g[0]=[struct.pack('<HHiiiH2x',1,0,1197,114,0,4)];g[3]=[]
    bank=[sign(0),pickup(ITEM,ITEM_FLAG,1,3)];sid=len(scripts.files);scripts.files.append(script_bank(bank));iid=len(scripts.files);scripts.files.append(bytes(4));tid=len(texts.files);texts.files.append(encode_text([DATA['messages']['route_sign'],'You found TM04 (WHIRLWIND)!','Your BAG is full. Make some room and come back.'],PH));eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid)
    dispatch=[]
    for trigger in (3000,5000):
        matches=[at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==trigger and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)]
        assert len(matches)==1;dispatch.append(matches[0])
    previous=struct.unpack_from('<H',d,dispatch[0]+2)[0];assert struct.unpack_from('<H',d,dispatch[1]+2)[0]==previous
    common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[previous],trainer))
    for at in dispatch:struct.pack_into('<H',d,at+2,common)
    w=bytearray(wild.files[old_wild]);slots=[DATA['wild_slots'][i] for i in SLOT_MAP];species=[p['species'] for p in slots];w[0]=DATA['encounter_rate'];w[1:6]=bytes(5);w[8:20]=bytes(p['level'] for p in slots)
    for period in range(3):struct.pack_into('<12H',w,20+period*24,*species)
    for at in (0x5C,0x60,0x64,0x68,0xBC):struct.pack_into('<2H',w,at,species[0],species[1])
    wid=len(wild.files);assert wid<255;wild.files.append(w);d[rec]=wid
    # Yellow's west-side Route 4 NPC belongs physically beside the Center on
    # HeartGold's Route 3. Preserve all existing Route 3 trainers and events.
    west=TABLE+11*24;wsid,wiid,wtid=struct.unpack_from('<3H',d,west+6);weid=struct.unpack_from('<H',d,west+16)[0];wg=events_decode(events.files[weid]);wb=split_bank(scripts.files[wsid]);key,lines=decode_messages(texts.files[wtid]);message=len(lines);lines.extend(decode_messages(encode_text([DATA['messages']['npc']],PH))[1]);entry=len(wb)+1;wb.append(talk(message));wg[1].append(actor(20,317,entry,1165,108,0,1));assert len({struct.unpack_from('<H',r)[0] for r in wg[1]})==len(wg[1])
    ns=len(scripts.files);scripts.files.append(script_bank(wb));nt=len(texts.files);texts.files.append(encode_messages(key,lines));ne=len(events.files);events.files.append(events_encode(wg));struct.pack_into('<H',d,west+6,ns);struct.pack_into('<H',d,west+10,nt);struct.pack_into('<H',d,west+16,ne)
    for path,arc in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=12,trainer=trainer,trainer_common=common,team=t['team'],optional_yellow_lass_level=31,script=sid,init=iid,text=tid,event=eid,wild=wid,tm=dict(item=ITEM,flag=ITEM_FLAG,actor=3,x=1254,z=107),west_npc=dict(map=11,actor=20,x=1165,z=108),original=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid,wild=old_wild))
