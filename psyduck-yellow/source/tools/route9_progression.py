"""Minimal functional Yellow Route9 using existing connected HG terrain."""
import struct
from collections import deque
import ndspy.narc
from opening import actor,events_decode,events_encode
from viridian_tutorial import TABLE
from forest_progression import SLOT_MAP
from route6_trainers import patch as install_trainers

TEMPLATES={'JrTrainerM':26,'JrTrainerF':27,'Youngster':8,'BugCatcher':4,'Hiker':25}
SPRITES={'JrTrainerM':345,'JrTrainerF':346,'Youngster':227,'BugCatcher':227,'Hiker':333}
FACING={'UP':0,'DOWN':1,'LEFT':2,'RIGHT':3}

def patch(rom,reference,original):
    trainer_report=install_trainers(rom,reference,map_name='Route9',expected_count=9,templates=TEMPLATES)
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+17*24
    paths=('a/0/3/2','a/0/3/7','a/0/4/1','a/0/6/5');events,wild,matrices,lands=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    eid=struct.unpack_from('<H',d,rec+16)[0];groups=events_decode(events.files[eid])
    native_trainers=[a for a in groups[1] if 3000<=struct.unpack_from('<H',a,10)[0]<4000];assert len(native_trainers)==6
    positions=[struct.unpack_from('<2H',a,24) for a in native_trainers]
    others=[a for a in groups[1] if a not in native_trainers]
    matrix=matrices.files[0];w,h,headers,heights,n=matrix[:5];off=5+n+w*h*(2*headers+heights)
    def permission(x,z):
        lid=struct.unpack_from('<H',matrix,off+2*(z//32*w+x//32))[0]
        return struct.unpack_from('<H',lands.files[lid],20+2*(z%32*32+x%32))[0]
    def floor(p):
        if not(1334<=p[0]<1440 and 128<=p[1]<164):return False
        v=permission(*p);return not(v&0x8000) and (v&255) not in (16,17,19,21)
    def next_steps(p):
        for dx,dz,ledge in ((1,0,56),(-1,0,57),(0,-1,58),(0,1,59)):
            q=(p[0]+dx,p[1]+dz)
            if floor(q):yield q
            elif 1334<=q[0]<1440 and 128<=q[1]<164 and permission(*q)&255==ledge:
                r=(q[0]+dx,q[1]+dz)
                if floor(r):yield r
    start=(1347,132);assert floor(start)
    reachable={start};queue=deque([start])
    while queue:
        for q in next_steps(queue.popleft()):
            if q not in reachable:reachable.add(q);queue.append(q)
    occupied=set(positions)|{struct.unpack_from('<2H',a,24) for a in others}|{(1347,143),(1348,143)}
    for entry in reference['trainers'][6:]:
        desired=(1344+round(entry['yellow_position'][0]*1.5),128+round(entry['yellow_position'][1]*1.5))
        candidates=[p for p in reachable if p[0]>=1352 and p not in occupied and sum(floor((p[0]+dx,p[1]+dz)) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))>=3 and all(abs(p[0]-q[0])+abs(p[1]-q[1])>=3 for q in occupied)]
        if not candidates:raise ValueError('No safe route trainer placement')
        p=min(candidates,key=lambda p:(abs(p[0]-desired[0])+abs(p[1]-desired[1]),p));positions.append(p);occupied.add(p)
    actors=[]
    for obj,(entry,battle,p) in enumerate(zip(reference['trainers'],trainer_report['trainers'],positions)):
        a=bytearray(actor(obj,SPRITES[entry['role']],3000+battle['id']-1,*p,facing=FACING[entry['facing']]))
        struct.pack_into('<H',a,6,1);struct.pack_into('<H',a,14,entry['vision']);actors.append(bytes(a))
    assert not any(struct.unpack_from('<H',a)[0] in (6,7,8) for a in others)
    # HG approach is two tiles wide; either native Cut tree opens one lane.
    od=original.loadArm9().sections[0].data;oe=ndspy.narc.NARC(original.files[original.filenames.idOf(paths[0])]);basegroups=events_decode(oe.files[struct.unpack_from('<H',od,rec+16)[0]])
    for obj,x in ((9,1347),(10,1348)):
        source=next(a for a in basegroups[1] if struct.unpack_from('<H',a,2)[0]==86 and struct.unpack_from('<H',a)[0]==obj-3)
        a=bytearray(source);struct.pack_into('<H',a,0,obj);struct.pack_into('<2H',a,24,x,143);actors.append(bytes(a))
    groups[1]=actors+others;ne=len(events.files);events.files.append(events_encode(groups));struct.pack_into('<H',d,rec+16,ne)
    raw=bytearray(wild.files[d[rec]]);assert len(raw)==196
    raw[0]=reference['grass_rate'];raw[1:6]=bytes(5)
    slots=[reference['grass'][i] for i in SLOT_MAP];raw[8:20]=bytes(s['level'] for s in slots)
    for period in range(3):struct.pack_into('<12H',raw,20+24*period,*(s['species'] for s in slots))
    for at in (0x5C,0x60,0xBC):struct.pack_into('<2H',raw,at,32,29)
    wid=len(wild.files);assert wid<255;wild.files.append(bytes(raw));d[rec]=wid
    for path,arc in ((paths[0],events),(paths[1],wild)):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=17,event=ne,wild=wid,trainers=trainer_report['trainers'],positions=positions,cut_trees=[[1347,143],[1348,143]],common=trainer_report['common'],common_sites=trainer_report['common_reference_sites'],terrain_preserved=True,topology_reference_reachable=len(reachable),native_test='pending',deferred=['exact Yellow terrain/decorative alignment','optional Teleport TM pickup conversion'])
