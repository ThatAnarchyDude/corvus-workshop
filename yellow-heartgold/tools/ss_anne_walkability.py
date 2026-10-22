"""Terrain-component doorway audit; native rendering/height/actor checks remain separate."""
import struct
from collections import deque
import ndspy.narc
from opening import events_decode
from viridian_tutorial import TABLE
MAPS=(254,255,256,257,258,259,260,261)

def terrain(raw):
    size,objects,model,collision,extension=struct.unpack_from('<5I',raw)
    offset=20+(extension>>16)
    assert size==2048 and raw[offset+size+objects:offset+size+objects+4]==b'BMD0'
    assert raw[offset+size+objects+model:offset+size+objects+model+4]==b'BDHC'
    return struct.unpack_from('<1024H',raw,offset)

def matrix_grid(raw,lands):
    w,h,heads,alts,n=raw[:5];count=w*h;start=5+n+count*2*bool(heads)+count*bool(alts)
    assert start+2*count==len(raw)
    modelids=struct.unpack_from('<'+'H'*count,raw,start);width,height=w*32,h*32;grid=[0x8000]*(width*height)
    for i,mid in enumerate(modelids):
        if mid==65535:continue
        values=terrain(lands.files[mid])
        for z in range(32):
            target=(z+(i//w)*32)*width+(i%w)*32;grid[target:target+32]=values[z*32:z*32+32]
    return width,height,grid

def components(width,height,grid):
    labels={};bounded=set();groups=[]
    for z in range(height):
        for x in range(width):
            if (x,z) in labels or grid[z*width+x]&0x8000:continue
            ident=len(groups);labels[(x,z)]=ident;queue=deque([(x,z)]);seen=[]
            while queue:
                point=queue.popleft();seen.append(point);px,pz=point
                for tx,tz in ((px-1,pz),(px+1,pz),(px,pz-1),(px,pz+1)):
                    if 0<=tx<width and 0<=tz<height and (tx,tz) not in labels and not grid[tz*width+tx]&0x8000:
                        labels[(tx,tz)]=ident;queue.append((tx,tz))
            border=any(px in (0,width-1) or pz in (0,height-1) for px,pz in seen)
            if not border:bounded.add(ident)
            groups.append(dict(tiles=len(seen),touches_matrix_border=border))
    return labels,bounded,groups

def audit(rom):
    data=rom.loadArm9().sections[0].data;events,matrices,lands=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in ('a/0/3/2','a/0/4/1','a/0/6/5')]
    records={}
    for mid in MAPS:
        at=TABLE+mid*24;matrix=struct.unpack_from('<H',data,at+4)[0];eid=struct.unpack_from('<H',data,at+16)[0]
        # Old private candidate has no bridge clone; exclude its unused placeholder.
        if mid==258 and eid==0:continue
        width,height,grid=matrix_grid(matrices.files[matrix],lands);labels,bounded,groups=components(width,height,grid)
        warps=[struct.unpack('<6H',raw) for raw in events_decode(events.files[eid])[2]]
        records[mid]=dict(labels=labels,bounded=bounded,warps=warps,groups=groups,grid=grid,width=width)
    def component(mid,x,z):
        record=records[mid];labels=record['labels'];bounded=record['bounded']
        direct=labels.get((x,z))
        if direct in bounded:return mid,direct
        neighbors={labels.get(p) for p in ((x-1,z),(x+1,z),(x,z-1),(x,z+1))}&bounded
        assert len(neighbors)==1,('Doorway lacks unambiguous enclosed approach',mid,x,z,neighbors)
        return mid,next(iter(neighbors))
    nodes=set();edges=[];facing_mismatches=[]
    for mid,record in records.items():
        for index,(x,z,dest,anchor,*_) in enumerate(record['warps']):
            assert dest in records and anchor<len(records[dest]['warps'])
            arrival=records[dest]['warps'][anchor];assert arrival[2]==mid
            source_face=record['grid'][z*record['width']+x]&255;destination=records[dest];destination_face=destination['grid'][arrival[1]*destination['width']+arrival[0]]&255
            if source_face in (0x65,0x69) and destination_face != (0x69 if source_face==0x65 else 0x65):facing_mismatches.append(dict(map=mid,warp=index,destination=dest,source_face=source_face,destination_face=destination_face))
            source=component(mid,x,z);target=component(dest,*arrival[:2]);nodes|={source,target};edges.append((source,target))
    start=component(256,24,18);reached={start}
    while True:
        expanded=reached|{target for source,target in edges if source in reached}
        if expanded==reached:break
        reached=expanded
    cabins={mid:len({node for node in nodes if node[0]==mid}) for mid in (259,260,261)}
    assert cabins=={259:6,260:6,261:5}
    return dict(door_facing_mismatches=facing_mismatches,logical_components=len(nodes),reachable_components=len(reached),unreachable_components=sorted(nodes-reached),cabins_by_map=cabins,
        native_collision_height_actor_walkability_verified=False,scope='Variable-length native terrain headers and door-connected enclosed components; not a substitute for gameplay.')

