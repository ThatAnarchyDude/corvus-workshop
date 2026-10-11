"""Remaining Yellow cave rewards, with native hidden-item/Dowsing behavior."""
import struct
import ndspy.narc
from opening import actor,events_decode,events_encode,script_bank,encode_text
from parcel_quest import PH,split_bank
from prototype import decode_messages,encode_messages
from forest_progression import pickup
from viridian_tutorial import TABLE

VISIBLE=(
    dict(map=107,actor=24,item=45,name='HP UP',flag=0xB35,x=24,z=21),
    dict(map=107,actor=25,item=116,name='TM12 (WATER GUN)',flag=0xB36,x=3,z=4),
    dict(map=448,actor=26,item=117,name='TM01 (MEGA PUNCH)',flag=0xB38,x=7,z=6),
)
HIDDEN=(
    dict(map=448,script=8195,item=81,name='MOON STONE',x=3,z=6),
    dict(map=107,script=8198,item=38,name='ETHER',x=11,z=22),
)


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2');arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events=arcs.values()
    # Reuse Mt. Moon's archived hidden-item ID and an unused ID. No currently
    # active background event elsewhere may share either reward's save flag.
    for m in range(540):
        if m in (107,448):continue
        eid=struct.unpack_from('<H',d,TABLE+m*24+16)[0]
        for bg in events_decode(events.files[eid])[0]:
            sid,kind=struct.unpack_from('<2H',bg)
            assert kind!=2 or sid not in (8195,8198),(m,sid)
    itcm=main.sections[1].data
    prefix=struct.pack('<HBBHH',17,1,0,0,0)+struct.pack('<HBBHH',92,1,0,0,1)+struct.pack('<HBBHH',92,1,0,0,225)
    assert itcm.count(prefix)==1,'The verified Forest native hidden table is required'
    table_at=itcm.index(prefix);address=main.sections[1].ramAddress+table_at
    assert d.count(struct.pack('<I',address))==2
    for reward in HIDDEN:
        index=reward['script']-8000
        rows=[at for at in range(table_at,table_at+231*8,8) if struct.unpack_from('<H',itcm,at+6)[0]==index]
        assert len(rows)==1
        struct.pack_into('<H',itcm,rows[0],reward['item'])
    mappings=[]
    for m in (107,448):
        rec=TABLE+m*24;old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6);old_eid=struct.unpack_from('<H',d,rec+16)[0]
        bank=split_bank(scripts.files[old_sid]);key,lines=decode_messages(texts.files[old_tid]);groups=events_decode(events.files[old_eid])
        for reward in VISIBLE:
            if reward['map']!=m:continue
            msg=len(lines);lines.extend(decode_messages(encode_text([f"You found a {reward['name']}!",'Your BAG is full. Make some room and come back.'],PH))[1])
            entry=len(bank)+1;bank.append(pickup(reward['item'],reward['flag'],msg,reward['actor']))
            groups[1].append(actor(reward['actor'],87,entry,reward['x'],reward['z'],reward['flag'],0))
        for reward in HIDDEN:
            if reward['map']==m:groups[0].append(struct.pack('<HHiiiH2x',reward['script'],2,reward['x'],reward['z'],0,4))
        sid=len(scripts.files);scripts.files.append(script_bank(bank));tid=len(texts.files);texts.files.append(encode_messages(key,lines));eid=len(events.files);events.files.append(events_encode(groups))
        struct.pack_into('<H',d,rec+6,sid);struct.pack_into('<H',d,rec+10,tid);struct.pack_into('<H',d,rec+16,eid)
        mappings.append(dict(map=m,script=sid,text=tid,event=eid,original=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid)))
    for p,a in arcs.items():rom.files[rom.filenames.idOf(p)]=a.save()
    rom.arm9=main.save(compress=True)
    return dict(visible=VISIBLE,hidden=[dict(r,flag=0x320+r['script']-8000) for r in HIDDEN],
                hidden_table=hex(address),mappings=mappings,native_dowsing_behavior=True)
