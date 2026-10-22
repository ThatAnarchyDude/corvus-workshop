"""Private Yellow-sized Route 5 gate probe; original native resources retained.

Requires the verified local Yellow gate topology. This is diagnostic geometry,
not a released checkpoint, and does not alter the other three gates or Johto.
"""
import struct
import ndspy.narc
from ndspy import _common
from opening import events_decode,events_encode
from viridian_tutorial import TABLE
from route5_mirror_materials import double_sided_model
from title_models import model,fifo,vertex,container,single_block

def compact_model(raw,cells,*,two_sided=False,solid_surfaces=False,shared_matrix=False,unlit_surfaces=False,flat_vertex_colors=False):
 ps,os,ms,bs,_=struct.unpack_from('<5I',raw)
 b=raw[20+ps+os:20+ps+os+ms];md=struct.unpack_from('<I',b,16)[0]
 base=md+struct.unpack('<I',_common.loadInfoBlock(b,md+8,4)[0][3])[0]
 mo,so=struct.unpack_from('<2I',b,base+8);materials=b[base+mo:base+so]
 tx=struct.unpack_from('<H',materials)[0];bindings={}
 for name,_,_,value in _common.loadInfoBlock(materials,tx,4):
  at,n,_=struct.unpack('<HBB',value);bindings[name]=list(materials[at:at+n])
 def quads(items,solid=False,unlit=False,flat=False):
  commands=[(0x20,[0x7fff]),(0x21,[511<<10]),(0x40,[1])]
  if flat:commands=[(0x20,[0x7fff]),(0x40,[1])]
  if solid:commands=[(0x29,[(31<<16)|0xc0]),(0x2a,[0]),(0x20,[0x7fff]),(0x40,[1])]
  if unlit and not solid:commands=[(0x29,[(31<<16)|0xc0]),(0x20,[0x7fff]),(0x40,[1])]
  for points in items:
   for x,y,z,u,v in points:
    commands.extend([(0x22,[(u*16&65535)|((v*16&65535)<<16)]),vertex(((x-16)/8,y/128,(z-16)/8))])
  commands.append((0x41,[]));return fifo(commands)
 floor=quads([[(0,0,0,0,0),(0,0,6,0,96),(8,0,6,128,96),(8,0,0,128,0)]])
 walls=[];counters=[]
 for c in cells:
  if c['walkable']:continue
  x,z=c['x'],c['y'];counter=c['collision_tile']==0x17;rise=12 if counter else 20
  # Private billboard geometry follows the source's blocked cells. All source
  # walking/warp cells remain clear; floor height is native gate world Y16.
  points=[(x,0,z+1,0,32),(x+1,0,z+1,16,32),(x+1,rise,z+.25,16,0),(x,rise,z+.25,0,0)]
  (counters if counter else walls).append(points)
 shapes=[floor,quads(walls,solid_surfaces,unlit_surfaces,flat_vertex_colors),quads(counters,solid_surfaces,unlit_surfaces,flat_vertex_colors)]
 b=model('YellowGateProbe',shapes,[(0,16,0),(0,0,0),(0,0,0)],scale=128)
 base=struct.unpack_from('<I',b,16)[0]+48;payload=bytearray(b[base:]);sbc,mo,so,en=struct.unpack_from('<4I',payload,4)
 delta=len(materials)-(so-mo);payload[mo:so]=materials
 struct.pack_into('<I',payload,0,len(payload));struct.pack_into('<2I',payload,12,so+delta,en+delta)
 payload[24]=len(_common.loadInfoBlock(materials,4,4));sb=payload[sbc:mo];at=8
 for i,name in enumerate(('gate_f1','gate_w1','gate_counter')):
  if i:at+=6
  assert sb[at:at+2]==bytes([4,0]);sb[at+1]=bindings[name][0];at+=6
 payload[sbc:mo]=sb
 if shared_matrix:
  # Diagnostic: keep all room surfaces on the native gate's single root matrix.
  shared=bytes([0x26,0,0,0,0,2,0,1,0x0b])+b''.join(bytes([4,bindings[name][0],5,i]) for i,name in enumerate(('gate_f1','gate_w1','gate_counter')))+bytes([0x2b,1])
  shared+=bytes(-len(shared)%4);delta=len(shared)-(mo-sbc);payload[sbc:mo]=shared
  struct.pack_into('<I',payload,0,len(payload));struct.pack_into('<3I',payload,8,mo+delta,so+len(materials)-(so-mo)+delta,en+len(materials)-(so-mo)+delta)
 struct.pack_into('<6h',payload,44,-8192,0,-8192,4096,2048,3072)
 result=container(b'BMD0',[single_block(b'MDL0','YellowGateProbe',payload)],2)
 return double_sided_model(result)[0] if two_sided else result

def patch_small_gate(rom,topology,*,diagnostic=False,two_sided=False,solid_surfaces=False,shared_matrix=False,unlit_surfaces=False,flat_vertex_colors=False,yellow_anchors=False):
 if not diagnostic:raise ValueError('Unfinished gate geometry requires diagnostic=True')
 if topology['map']!='Route5Gate' or topology['dimensions']!=[8,6]:raise ValueError('Expected verified Yellow Route 5 gate')
 cells=topology['cells'];assert len(cells)==48 and len({(c['x'],c['y']) for c in cells})==48
 assert topology['walkable_count']==22 and not topology['one_way_ledges']
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+391*24
 assert d[rec+20]&1,'Kanto-only gate required'
 paths=('a/0/4/1','a/0/6/5','a/0/3/2');mat,lands,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 mid=struct.unpack_from('<H',d,rec+4)[0];matrix=mat.files[mid];assert matrix[:4]==b'\1\1\0\0'
 lid=struct.unpack_from('<H',matrix,5+matrix[4])[0];raw=lands.files[lid]
 ps,os,ms,bs,magic=struct.unpack_from('<5I',raw);assert ps==2048 and bs==66
 permissions=[0x8000]*1024
 for c in cells:
  permissions[c['y']*32+c['x']]=0x600 if c['walkable'] else 0x8080 if c['collision_tile']==0x17 else 0x8000
 for x in (3,4):permissions[x]=0x66e;permissions[5*32+x]=0x665
 bmd=compact_model(raw,cells,two_sided=two_sided,solid_surfaces=solid_surfaces,shared_matrix=shared_matrix,unlit_surfaces=unlit_surfaces,flat_vertex_colors=flat_vertex_colors);bdhc=bytearray(raw[20+ps+os+ms:]);assert bdhc[:4]==b'BDHC'
 # Extend the existing flat collider across this matrix cell; retain its plane.
 struct.pack_into('<4i',bdhc,16,-1048576,-1048576,1048576,1048576)
 newland=len(lands.files);lands.files.append(struct.pack('<5I',ps,0,len(bmd),bs,magic)+struct.pack('<1024H',*permissions)+bmd+bdhc)
 newmatrix=len(mat.files);mat.files.append(matrix[:-2]+struct.pack('<H',newland));struct.pack_into('<H',d,rec+4,newmatrix)
 eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[eid]);assert len(g[1])==1 and len(g[2])==2
 actor=bytearray(g[1][0]);struct.pack_into('<2H',actor,24,1,3);g[1]=[bytes(actor)]
 g[2]=[struct.pack('<4HI',x,z,13,anchor,0) for x,z,anchor in ((3,5,2),(3,0,1 if yellow_anchors else 0),(4,5,2),(4,0,0))]
 g[3]=[struct.pack('<Hhh5H',2,3,3,2,1,0,0,0)]
 newevent=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,newevent)
 if yellow_anchors:
  outside_rec=TABLE+13*24;assert d[outside_rec+20]&1
  outside=events_decode(events.files[struct.unpack_from('<H',d,outside_rec+16)[0]])
  assert [struct.unpack('<4HI',w) for w in outside[2][:2]]==[(1300,186,391,1,0),(1299,186,391,1,0)]
  w=bytearray(outside[2][0]);struct.pack_into('<H',w,6,3);outside[2][0]=bytes(w)
  ne=len(events.files);events.files.append(events_encode(outside));struct.pack_into('<H',d,outside_rec+16,ne)
 for p,a in zip(paths,(mat,lands,events)):rom.files[rom.filenames.idOf(p)]=a.save()
 rom.arm9=main.save(compress=True)
 return dict(private=True,released=False,map=391,dimensions=[8,6],land=newland,matrix=newmatrix,event=newevent,original_land=lid,original_matrix=mid,walkable_tiles=22,guard=[1,3],trigger=[3,3,2,1],pending=['native interior renderer and texture checks','both entrance/return pairs','no-drink and one-drink guard checks','legacy interior save handling'])
