"""Private connected Route6 terrain probe; city seams require native validation."""
import struct
import ndspy.narc
from ndspy import _common
from route5_materials import textured_model
from route5_connected import matrix_offset
from opening import actor,events_decode,events_encode,script_bank,encode_text
from field_interaction_fixes import sign
from parcel_quest import PH
from viridian_tutorial import TABLE

ORIGIN=(1280,256)
X_OFFSET=12

def native_materials(raw):
    ps,os,ms,bs,magic=struct.unpack_from('<5I',raw)
    # Native land130 stores 32 extra bytes before BMD. Never reinterpret that
    # prefix as a model or change the original land member.
    start=20+ps+os+(magic>>16)
    b=raw[start:start+ms]
    if b[:4]!=b'BMD0':raise ValueError('Unexpected native Route6 model position')
    declared=struct.unpack_from('<I',b,8)[0]
    if declared!=ms:raise ValueError('Native model length mismatch')
    mdlo=struct.unpack_from('<I',b,16)[0];entry=_common.loadInfoBlock(b,mdlo+8,4)[0]
    base=mdlo+struct.unpack('<I',entry[3])[0];mo,so=struct.unpack_from('<2I',b,base+8);m=b[base+mo:base+so]
    tx=struct.unpack_from('<H',m)[0];bindings={}
    for name,_,_,v in _common.loadInfoBlock(m,tx,4):
        at,n,_=struct.unpack('<HBB',v);bindings[name]=list(m[at:at+n])
    return m,bindings,len(_common.loadInfoBlock(m,4,4))

def patch(rom,layout,trainer_report,*,diagnostic=False,native_city_links=False):
    if not diagnostic:raise ValueError('Unvalidated terrain must remain a private diagnostic')
    assert layout['map']=='Route6' and layout['dimensions']==[20,32]
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+14*24
    assert d[rec+20]&1 and struct.unpack_from('<H',d,rec+4)[0]==0
    paths=('a/0/4/1','a/0/6/5','a/0/3/2','a/0/4/2','a/0/4/3','a/0/7/0','a/0/1/2','a/0/2/7')
    mat,lands,events,areas,lists,proptex,scripts,texts=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    matrix=bytearray(mat.files[0]);at=matrix_offset(matrix,40,8);assert struct.unpack_from('<H',matrix,at)[0]==130
    cells={(c['x']+X_OFFSET,c['y']):c for c in layout['cells']};ledges={(e['ledge'][0]+X_OFFSET,e['ledge'][1]) for e in layout['one_way_ledges']}
    permissions=[];water=[]
    for z in range(32):
        for x in range(32):
            c=cells.get((x,z),{});tile=c.get('collision_tile')
            p=0x843B if (x,z) in ledges else 0x402 if tile==82 else 0x410 if tile==20 else 0x400 if c.get('walkable') else 0x8400
            permissions.append(p)
            if tile==20:water.append((x,z))
    doors=((21,0,389,1,0x6F),(22,0,389,1,0x6F),(22,5,389,0,0x6E),(29,10,470,0,0x6E))
    for x,z,_,_,behavior in doors:permissions[z*32+x]=0x400|behavior
    # Yellow's southern road reaches x20/21; HG Vermilion's existing entrance
    # is x25/26. A short bend joins them without moving the ponds or trainers.
    spur={(x,31) for x in range(20,27)} if native_city_links else set()
    for x,z in spur:permissions[z*32+x]=0x400
    materials,bindings,count=native_materials(lands.files[130])
    fences=[(x,z,c['collision_tile']) for (x,z),c in cells.items() if c['collision_tile'] in (0x3A,0x55) and (x,z) not in spur]
    bmd=textured_model(permissions,materials,bindings,count,ground_y=32,visible_ledges=True,fences=fences,water_tiles=water)
    # Reuse existing native building models. 342 is the registered double-sided
    # gate clone already present in 0028; no new global building resources.
    specs=((342,21.859375,3.75,-1.28,1,.625),(290,30,9.5,1,1,1),(31,31.5,12.5,1,1,1))
    props=b''.join(struct.pack('<12i',m,round((x-16)*65536),131072,round((z-16)*65536),0,0,0,round(sx*4096),round(sy*4096),round(sz*4096),0,0) for m,x,z,sx,sy,sz in specs)
    raw=lands.files[133];ps,os,ms,bs,_=struct.unpack_from('<5I',raw);bdhc=raw[20+ps+os+ms:];assert len(bdhc)==66
    lid=len(lands.files);lands.files.append(struct.pack('<5I',2048,len(props),len(bmd),len(bdhc),0x1234)+struct.pack('<1024H',*permissions)+props+bmd+bdhc)
    struct.pack_into('<H',matrix,at,lid);mat.files[0]=bytes(matrix)
    changed_cells=[[40,8]]
    if native_city_links:
        # Native callback/RAM evidence confirms this city's permissions start
        # at offset20. Preserve its entire model, props and collision planes.
        cityat=matrix_offset(matrix,40,7);cityid=struct.unpack_from('<H',matrix,cityat)[0];assert cityid==135
        city=bytearray(lands.files[cityid]);assert struct.unpack_from('<I',city)[0]==2048
        for z in (29,30,31):
            for x in (21,22):struct.pack_into('<H',city,20+2*(32*z+x),0x600)
        # Deactivate the superseded native gate's remaining warp tile.
        struct.pack_into('<H',city,20+2*(32*29+20),0x600)
        newid=len(lands.files);lands.files.append(bytes(city));struct.pack_into('<H',matrix,cityat,newid);mat.files[0]=bytes(matrix);changed_cells.append([40,7])
    # Clone the graphics area and model list, protecting any shared Johto bank.
    area=bytearray(areas.files[d[rec+1]]);li=struct.unpack_from('<H',area)[0]
    values=list(struct.unpack('<'+'H'*(len(lists.files[li])//2),lists.files[li]));assert values[0]==len(values)-1
    if 342 not in values[1:]:values=[values[0]+1]+values[1:]+[342]
    newli=len(lists.files);assert newli==len(proptex.files)
    lists.files.append(struct.pack('<'+'H'*len(values),*values));proptex.files.append(proptex.files[li]);struct.pack_into('<H',area,0,newli)
    newarea=len(areas.files);assert newarea<256;areas.files.append(bytes(area));d[rec+1]=newarea
    eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[eid])
    g[0]=[struct.pack('<HHiiiH2x',1,0,1311,268,2,4)];g[1]=[];g[3]=[]
    sprites={'JrTrainerM':345,'JrTrainerF':346,'BugCatcher':227};facing={'RIGHT':3,'LEFT':2}
    for i,(t,battle) in enumerate(zip(layout['trainers'],trainer_report['trainers'])):
        x,z=t['position'];a=bytearray(actor(i,sprites[t['role']],3000+battle['id']-1,1280+X_OFFSET+x,256+z,facing=facing[t['facing']]))
        struct.pack_into('<H',a,6,1);struct.pack_into('<H',a,14,t['vision']);g[1].append(bytes(a))
    g[2]=[struct.pack('<4HI',1280+x,256+z,target,anchor,0) for x,z,target,anchor,_ in doors]
    ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,ne)
    sid=len(scripts.files);scripts.files.append(script_bank([sign(0)]));iid=len(scripts.files);scripts.files.append(bytes(4))
    tid=len(texts.files);texts.files.append(encode_text(['UNDERGROUND PATH\rCERULEAN CITY -\nVERMILION CITY'],PH));struct.pack_into('<3H',d,rec+6,sid,iid,tid)
    # Preserve native room geometry; update only exit destinations/anchors.
    for m,returns in ((389,{0:2,1:1}),(470,{0:3})):
        er=TABLE+m*24;g=events_decode(events.files[struct.unpack_from('<H',d,er+16)[0]])
        for i,anchor in returns.items():a=bytearray(g[2][i]);struct.pack_into('<2H',a,4,14,anchor);g[2][i]=bytes(a)
        ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,er+16,ne)
    for path,arc in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(private=True,released=False,land=lid,area=newarea,model_list=newli,water_tiles=len(water),actor_count=6,
                native_city_links=native_city_links,changed_main_cells=changed_cells,pending=['native renderer/walking/doors','city seam validation','legacy saves','native Surf'])
