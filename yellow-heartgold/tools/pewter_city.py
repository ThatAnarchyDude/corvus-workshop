"""Pewter's Yellow outdoor NPCs and walking guides on HeartGold's geometry."""
import json
import struct

import ndspy.narc

from build_rom import PROJECT
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, talk, end
from parcel_quest import PH, BOUNDARY
from viridian_tutorial import TABLE

DATA = json.loads((PROJECT/'data/pewter-city.json').read_text())
ROUTE_GUIDE = 12
MUSEUM_GUIDE = 13


def route_guide():
    s = Script().emit(96).emit(294,8,0x800C).compare(0x800C,1).jump('next',1)
    s.msg(0).emit(105,0x4000,0x4001)
    s.compare(0x4000,1085).jump('beside',1).jump('rows')
    s.label('beside').movement(255,'mv_beside').emit(95)
    s.label('rows')
    for z in range(104,108):s.compare(0x4001,z).jump(f'align{z}',1)
    s.jump('align106')
    for z in range(104,108):
        s.label(f'align{z}').movement(255,f'line{z}').emit(95).jump('escort')
    s.label('escort').movement(ROUTE_GUIDE,'mv_escort').movement(255,'mv_escort').emit(95)
    s.msg(1).movement(ROUTE_GUIDE,'return').emit(95)
    end(s)
    s.label('next').msg(2).movement(255,'back').emit(95)
    end(s)
    for z in range(104,108):
        s.moves(f'line{z}',[(13,106-z)] if z<106 else [(12,z-106)] if z>106 else [(2,1)])
    return s.moves('mv_beside',[(15,1)]).moves('mv_escort',[(14,31),(12,13),(14,6),(0,1)]).moves('return',[(13,1),(15,6),(13,12),(15,31),(2,1)]).moves('back',[(14,1)]).finish()


def museum_guide():
    s = Script().emit(96).emit(104).msg(3).emit(63,0x800C)
    s.compare(0x800C,0).jump('seen',1).msg(5).emit(105,0x4000,0x4001)
    s.compare(0x4000,1041).jump('west',1).compare(0x4000,1043).jump('east',1)
    s.compare(0x4001,84).jump('north',1).jump('south')
    for side in ('west','east','north','south'):
        s.label(side).movement(255,'mv_'+side).emit(95).jump('walk')
    s.label('walk').movement(MUSEUM_GUIDE,'mv_walk').movement(255,'mv_walk').emit(95)
    s.msg(6).movement(MUSEUM_GUIDE,'return').emit(95)
    end(s)
    s.label('seen').msg(4)
    end(s)
    s.moves('mv_west',[(3,1)]).moves('mv_east',[(13,1),(14,2),(12,1)])
    s.moves('mv_north',[(14,1),(13,1)]).moves('mv_south',[(14,1),(12,1)])
    return s.moves('mv_walk',[(15,7),(12,6),(0,1)]).moves('return',[(13,6),(14,7),(3,1)]).finish()


def repel_garden():
    s = Script().emit(96).emit(104).msg(9).emit(63,0x800C)
    s.compare(0x800C,0).jump('yes',1).msg(11)
    end(s)
    s.label('yes').msg(10)
    return end(s).finish()


def patch(rom):
    main=rom.loadArm9()
    d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events=arcs.values()
    rec=TABLE+51*24
    old_event=struct.unpack_from('<H',d,rec+16)[0]
    groups=events_decode(events.files[old_event])
    rows=[]
    for row in groups[1]:
        obj=struct.unpack_from('<H',row)[0]
        if obj in (4,5):rows.append(row)  # Preserve HG's two Apricorn trees.
        elif obj in (0,1,2):
            b=bytearray(row)
            struct.pack_into('<H',b,2,(320,318,331)[obj])
            struct.pack_into('<2H',b,8,0,(3,4,5)[obj])
            rows.append(b)
    rows.extend([actor(ROUTE_GUIDE,318,1,1085,106,0,2),
                 actor(MUSEUM_GUIDE,331,2,1042,85,0,3)])
    groups[1]=rows
    groups[0]=[struct.pack('<HHiiiH2x',sid,1,x,z,0,4) for sid,x,z in
               ((6,1045,112),(9,1045,95),(10,1064,105),(8,1051,81))]
    groups[3]=[struct.pack('<Hhh5H',1,1086,104,1,4,0,0,BOUNDARY)]
    labels=['PewterCityYoungsterYoureATrainerFollowMeText','PewterCityYoungsterGoTakeOnBrockText',None,
            'PewterCitySuperNerd1DidYouCheckOutMuseumText','PewterCitySuperNerd1WerentThoseFossilsAmazingText',
            'PewterCitySuperNerd1YouHaveToGoText','PewterCitySuperNerd1ItsRightHereText',
            'PewterCityCooltrainerFText','PewterCityCooltrainerMText',
            'PewterCitySuperNerd2DoYouKnowWhatImDoingText','PewterCitySuperNerd2ThatsRightText',
            'PewterCitySuperNerd2ImSprayingRepelText','PewterCityTrainerTipsText',
            'PewterCityPoliceNoticeSignText','PewterCityMuseumSignText','PewterCityGymSignText','PewterCitySignText']
    lines=[DATA['messages'][label] if label else 'Route 3 is the next area being prepared. Please explore PEWTER CITY for now.' for label in labels]
    # Reuse existing boards rather than inventing additional scenery.
    lines[12]+='\r'+lines[13]
    bank=[route_guide(),museum_guide(),talk(7),talk(8),repel_garden(),talk(12),talk(13),talk(14),talk(15),talk(16)]
    sid=len(scripts.files);scripts.files.append(script_bank(bank))
    iid=len(scripts.files);scripts.files.append(bytes(4))
    tid=len(texts.files);texts.files.append(encode_text(lines,PH))
    eid=len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<3H',d,rec+6,sid,iid,tid)
    struct.pack_into('<H',d,rec+16,eid)
    # Remove 014's development limit now that Pewter is being converted.
    route_rec=TABLE+414*24
    route_event=struct.unpack_from('<H',d,route_rec+16)[0]
    route=events_decode(events.files[route_event])
    boundary=[row for row in route[3] if struct.unpack_from('<hh',row,2)==(1024,128)]
    assert len(boundary)==1
    route[3]=[row for row in route[3] if row not in boundary]
    new_route_event=len(events.files);events.files.append(events_encode(route))
    struct.pack_into('<H',d,route_rec+16,new_route_event)
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=51,script=sid,text=tid,event=eid,original_event=old_event,
                route2_event=new_route_event,guide_trigger=[1086,104,1,4])
