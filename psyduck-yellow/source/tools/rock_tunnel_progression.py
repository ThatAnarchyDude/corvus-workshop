"""Yellow Rock Tunnel trainers/wilds on native HG floors and ladder connections."""
import struct
from collections import deque
import ndspy.narc
from opening import actor,events_decode,events_encode
from viridian_tutorial import TABLE
from route6_trainers import patch as install_trainers
from forest_progression import SLOT_MAP
from route10_progression import TEMPLATES,SPRITES,FACING

def patch(rom,references):
 reports=[]
 for name,m,count in (('RockTunnel1F',108,7),('RockTunnelB1F',452,8)):
  ref=references[name];train=install_trainers(rom,ref,map_name=name,expected_count=count,templates=TEMPLATES)
  main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+m*24
  events=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')]);wild=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/7')]);matrices=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')]);lands=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
  oldevent=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[oldevent]);assert not any(3000<=struct.unpack_from('<H',a,10)[0]<4000 for a in g[1])
  mat=matrices.files[struct.unpack_from('<H',d,rec+4)[0]];w,h,headers,heights,n=mat[:5];off=5+n+w*h*(2*headers+heights)
  def floor(p):
   x,y=p
   if not (5<=x<49 and 5<=y<38):return False
   lid=struct.unpack_from('<H',mat,off+2*(y//32*w+x//32))[0]
   if lid==65535:return False
   v=struct.unpack_from('<H',lands.files[lid],20+2*(y%32*32+x%32))[0]
   return not v&0x8000 and v&255 not in (16,17,19,21)
  floor_set={(x,y) for y in range(5,38) for x in range(5,49) if floor((x,y))}
  others={tuple(struct.unpack_from('<2H',a,24)) for a in g[1]};warps={tuple(struct.unpack_from('<2H',a)) for a in g[2]};occupied=set(others);ids={struct.unpack_from('<H',a)[0] for a in g[1]};positions=[]
  def signature(block):
   unseen=floor_set-block;out=[]
   while unseen:
    start=min(unseen);seen={start};q=deque([start]);unseen.remove(start)
    while q:
     x,y=q.popleft()
     for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
      if p in unseen:unseen.remove(p);seen.add(p);q.append(p)
    markers=warps&seen
    if markers:out.append(tuple(sorted(markers)))
   return sorted(out)
  original_signature=signature(others)
  accessible=set(warps)&(floor_set-others);q=deque(accessible)
  while q:
   x,y=q.popleft()
   for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if p in floor_set-others and p not in accessible:accessible.add(p);q.append(p)
  for entry,battle in zip(ref['trainers'],train['trainers']):
   desired=(entry['yellow_position'][0]+5,entry['yellow_position'][1]+3)
   candidates=sorted((p for p in accessible if p not in occupied and sum((p[0]+dx,p[1]+dy) in floor_set for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))>=3 and all(abs(p[0]-q[0])+abs(p[1]-q[1])>=3 for q in occupied|warps)),key=lambda p:(abs(p[0]-desired[0])+abs(p[1]-desired[1]),p))
   p=next((p for p in candidates if signature(occupied|{p})==original_signature),None)
   if p is None:raise ValueError('No route-safe tunnel trainer position')
   occupied.add(p);positions.append(p);obj=next(i for i in range(32) if i not in ids);ids.add(obj)
   a=bytearray(actor(obj,SPRITES[entry['role']],3000+battle['id']-1,*p,facing=FACING[entry['facing']]))
   struct.pack_into('<H',a,6,1);struct.pack_into('<H',a,14,entry['vision']);g[1].append(bytes(a))
  eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,eid)
  row=bytearray(wild.files[d[rec]]);assert len(row)==196;row[:6]=bytes([ref['grass_rate'],0,0,0,0,0]);slots=[ref['grass'][i] for i in SLOT_MAP];row[8:20]=bytes(p['level'] for p in slots)
  for period in range(3):struct.pack_into('<12H',row,20+24*period,*(p['species'] for p in slots))
  for at in (0x5C,0x60,0x64,0x68,0xBC):struct.pack_into('<2H',row,at,slots[0]['species'],slots[1]['species'])
  wid=len(wild.files);assert wid<255;wild.files.append(bytes(row));d[rec]=wid
  rom.files[rom.filenames.idOf('a/0/3/2')]=events.save();rom.files[rom.filenames.idOf('a/0/3/7')]=wild.save();rom.arm9=main.save(compress=True)
  reports.append(dict(map=m,name=name,event=eid,original_event=oldevent,wild=wid,trainers=train['trainers'],positions=positions,common_sites=train['common_reference_sites'],warp_components_preserved=True,terrain_and_ladders_preserved=True,native_test='pending'))
 return reports

