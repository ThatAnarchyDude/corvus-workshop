"""Yellow's mandatory Jessie/James fossil ambush; private draft artwork.

The team and dialogue are Yellow's. Native Rocket graphics temporarily stand
in for the pair; do not publish this draft before their artwork is integrated.
"""
import struct
import ndspy.narc
from opening import Script,actor,events_decode,events_encode,script_bank,encode_text,end
from parcel_quest import PH,split_bank
from prototype import decode_messages,encode_messages
from forest_progression import expanded_common
from escort import music
from mtmoon import DATA as CAVE
from mtmoon_story import DATA,STAGE
from viridian_tutorial import TABLE

JESSIE=30
JAMES=31
HIDE_JESSIE=0xB33
HIDE_JAMES=0xB34


def ambush(trainer,msg):
    s=Script().compare(STAGE,2).jump('done',5).emit(96)
    music(s,1112).msg(msg)
    s.emit(105,0x4000,0x4001)
    for x in (20,21,23,24):s.compare(0x4000,x).jump(f'align{x}',1)
    s.jump('approach')
    for x in (20,21,23,24):s.label(f'align{x}').movement(255,f'player{x}').emit(95).jump('approach')
    s.label('approach').movement(255,'face_up').emit(95)
    s.movement(JESSIE,'jessie_in').movement(JAMES,'james_in').emit(95).msg(msg+1)
    s.emit(213,trainer,0);s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5)
    s.emit(36,trainer)
    music(s,1112).msg(msg+2).msg(msg+3)
    # Both walk to the visible exit before removal. No instantaneous entrance,
    # scene skip, new terrain barrier, or simultaneous collision at the door.
    s.movement(JAMES,'james_out').emit(95).emit(30,HIDE_JAMES).emit(101,JAMES)
    s.movement(JESSIE,'jessie_out').emit(95).emit(30,HIDE_JESSIE).emit(101,JESSIE)
    s.emit(41,STAGE,3).emit(81,0).emit(82)
    end(s)
    s.label('lost').emit(219);end(s)
    s.label('done').emit(2)
    for x in (20,21,23,24):s.moves(f'player{x}',[(15 if x<22 else 14,abs(x-22))])
    s.moves('face_up',[(0,1)])
    s.moves('jessie_in',[(13,1),(15,1),(1,1)])
    s.moves('james_in',[(14,1),(13,1),(1,1)])
    s.moves('james_out',[(13,2),(14,1)])
    s.moves('jessie_out',[(13,2),(15,1)])
    return s.finish()


def standby(msg):
    s=Script().emit(96).emit(104).msg(msg)
    return end(s).finish()


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1')
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,trainers,parties,trtable,offsets=arcs.values()
    trainer=len(trainers.files);row=bytearray(next(r for r in trainers.files if r[1]==55))
    row[0],row[3],row[16]=1,3,0;row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);trainers.files.append(row)
    parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in DATA['rocket_team']))
    key,names=decode_messages(texts.files[729]);names.extend(decode_messages(encode_text(['JESSIE & JAMES'],PH))[1]);texts.files[729]=encode_messages(key,names)
    key,bt=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0])
    while len(ofs)<(trainer+1)*2:ofs.extend(struct.pack('<H',len(table)))
    struct.pack_into('<H',ofs,trainer*2,len(table))
    for kind,k in enumerate(('MtMoonJessieJamesText2','MtMoonJessieJamesText3','MtMoonJessieJamesText4')):
        table.extend(struct.pack('<2H',trainer,kind));bt.extend(decode_messages(encode_text([CAVE['messages'][k]],PH))[1])
    texts.files[728]=encode_messages(key,bt);trtable.files[0],offsets.files[0]=bytes(table),bytes(ofs)
    for trigger in (3000,5000):
        matches=[at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==trigger and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)]
        assert len(matches)==1
        at=matches[0]
        if trigger==3000:
            common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[struct.unpack_from('<H',d,at+2)[0]],trainer))
        struct.pack_into('<H',d,at+2,common)
    rec=TABLE+107*24;old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6);old_eid=struct.unpack_from('<H',d,rec+16)[0]
    bank=split_bank(scripts.files[old_sid]);key,lines=decode_messages(texts.files[old_tid]);groups=events_decode(events.files[old_eid])
    msg=len(lines);lines.extend(decode_messages(encode_text([CAVE['messages'][f'MtMoonJessieJamesText{i}'] for i in range(1,5)],PH))[1])
    entry=len(bank)+1;bank.append(ambush(trainer,msg));talk_entry=len(bank)+1;bank.append(standby(msg))
    groups[1].extend([actor(JESSIE,221,talk_entry,20,20,HIDE_JESSIE,1),actor(JAMES,222,talk_entry,24,20,HIDE_JAMES,1)])
    groups[3].append(struct.pack('<Hhh5H',entry,20,22,5,1,0,2,STAGE))
    sid=len(scripts.files);scripts.files.append(script_bank(bank));tid=len(texts.files);texts.files.append(encode_messages(key,lines));eid=len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<H',d,rec+6,sid);struct.pack_into('<H',d,rec+10,tid);struct.pack_into('<H',d,rec+16,eid)
    for p,a in arcs.items():rom.files[rom.filenames.idOf(p)]=a.save()
    rom.arm9=main.save(compress=True)
    return dict(trainer=trainer,team=DATA['rocket_team'],map=107,script=sid,text=tid,event=eid,entry=entry,message=msg,
                hide_flags=[HIDE_JESSIE,HIDE_JAMES],original=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid),
                encounter_music=1112,exit_after_victory=True,artwork='Native Rocket placeholders; custom Jessie/James graphics pending',
                status='unpublished; native scene and artwork must be verified before release')
