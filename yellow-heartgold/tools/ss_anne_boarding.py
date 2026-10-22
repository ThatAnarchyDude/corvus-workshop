"""Kanto S.S. Anne boarding via copied native port rooms, with a non-consuming ticket check."""
import json,struct
from pathlib import Path
import ndspy.narc
from opening import Script,end,script_bank,encode_text,actor,events_decode,events_encode
from parcel_quest import PH
from viridian_tutorial import TABLE
TICKET=456
PORT=263
DOCK=264
SHIP=256
MESSAGES=[
 'Welcome to S.S. ANNE!',
 'Welcome to S.S. ANNE!\rExcuse me, do you have a ticket?',
 '{PLAYER} flashed the S.S.TICKET!\rGreat! Welcome to S.S.ANNE!',
 "{PLAYER} doesn't have the needed S.S.TICKET.\rSorry!\rYou need a ticket to get aboard."]

def ticket_gate():
    # The choke point is entered southbound. Northbound return travel is free.
    s=Script().emit(386,0x800C).compare(0x800C,0).jump('leaving',1).emit(96).msg(1)
    s.emit(128,TICKET,1,0x800C).compare(0x800C,0).jump('missing',1)
    s.msg(2);end(s)
    s.label('missing').msg(3).movement(255,'back').emit(95);end(s)
    s.label('leaving').emit(2)
    s.moves('back',[(12,1)])
    return s.finish()

def sailor_talk():return end(Script().emit(73,1500).emit(96).emit(104).msg(0)).finish()

def warp(x,z,dest,anchor):return struct.pack('<6H',x,z,dest,anchor,0,0)

def patch(rom):
    audit=json.loads(Path('yellow-heartgold/build/0030-boarding-slots-v1/audit.json').read_text())
    assert not any(audit[k] for k in ('incoming','matrix_refs','raw_warp_matches','source_refs'))
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/4/1');scripts,texts,events,matrices=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    sid=len(scripts.files);scripts.files.append(script_bank([sailor_talk(),ticket_gate()]))
    empty=len(scripts.files);scripts.files.append(script_bank([Script().emit(2).finish()]));init=len(scripts.files);scripts.files.append(b'\0')
    tid=len(texts.files);texts.files.append(encode_text(MESSAGES,PH))
    clone_rows=[]
    for target,source in ((PORT,386),(DOCK,387)):
        at=TABLE+target*24;assert bytes(d[at:at+24]).hex()==audit['placeholder_headers'][str(target)]
        row=bytearray(d[TABLE+source*24:TABLE+(source+1)*24]);oldmatrix=struct.unpack_from('<H',row,4)[0];raw=matrices.files[oldmatrix]
        assert raw[2]==0,'Native port matrix has owned map headers; explicit rewrite required'
        nm=len(matrices.files);matrices.files.append(raw)
        if target==PORT:
            # Native row9 has a single walkable opening atx7. Actor is beside it.
            g=[[],[actor(0,348,1,6,8,facing=3)],[warp(7,2,54,7),warp(7,11,DOCK,0)],
                [struct.pack('<Hhh5H',2,7,9,1,1,0,0,0)]]
        else:g=[[],[],[warp(12,12,PORT,1),warp(23,17,SHIP,10)],[]]
        ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<4H',row,4,nm,sid if target==PORT else empty,init,tid);struct.pack_into('<H',row,16,ne)
        oldmove=struct.unpack_from('<H',row,2)[0]&15;struct.pack_into('<H',row,2,oldmove|(40<<4)|(9<<10));row[18]=235;row[19]=(row[19]&0xF0)|9
        struct.pack_into('<I',row,20,struct.unpack_from('<I',row,20)[0]|1);d[at:at+24]=row
        clone_rows.append(dict(map=target,donor=source,matrix=nm,event=ne,script=struct.unpack_from('<H',row,6)[0]))
    # Only Vermilion's port warp changes; preserve all city actors/events/otherwarps.
    cityrec=TABLE+54*24;city=events_decode(events.files[struct.unpack_from('<H',d,cityrec+16)[0]])
    assert struct.unpack('<6H',city[2][7])==(1309,340,386,0,0,0)
    city[2][7]=warp(1309,340,PORT,0);ce=len(events.files);events.files.append(events_encode(city));struct.pack_into('<H',d,cityrec+16,ce)
    shiprec=TABLE+SHIP*24;ship=events_decode(events.files[struct.unpack_from('<H',d,shiprec+16)[0]])
    assert len(ship[2])==10 and not any(struct.unpack_from('<2H',w)==(24,19) for w in ship[2])
    ship[2].append(warp(24,19,DOCK,1));se=len(events.files);events.files.append(events_encode(ship));struct.pack_into('<H',d,shiprec+16,se)
    for p,arc in zip(paths,(scripts,texts,events,matrices)):rom.files[rom.filenames.idOf(p)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(clones=clone_rows,city_event=ce,ship_event=se,ticket=TICKET,ticket_consumed=False,persistent_flag_writes=False,
        northbound_return_unrestricted=True,original_aqua_and_port_resources_preserved=True,
        departure_and_full_story_pending=True,native_test_pending=True)
