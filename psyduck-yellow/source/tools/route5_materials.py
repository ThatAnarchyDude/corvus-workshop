"""Private flat Route 5 material probe; native textures, unfinished scenery.

Clone land/matrix members only. Keep permissions, doors and original resources.
This intentionally does not claim finished ledge geometry or building placement.
"""
import struct
import ndspy.narc
from ndspy import _common
from title_models import model,fifo,vertex,container,single_block
from viridian_tutorial import TABLE

def native_materials(lands):
 raw=lands.files[153];ps,os,ms,_,_=struct.unpack_from('<5I',raw)
 b=raw[20+ps+os:20+ps+os+ms];mdlo=struct.unpack_from('<I',b,16)[0]
 entries=_common.loadInfoBlock(b,mdlo+8,4);base=mdlo+struct.unpack('<I',entries[0][3])[0]
 mo,so=struct.unpack_from('<2I',b,base+8);m=b[base+mo:base+so]
 tx=struct.unpack_from('<H',m)[0];bindings={}
 for name,_,_,v in _common.loadInfoBlock(m,tx,4):
  at,n,_=struct.unpack('<HBB',v);bindings[name]=list(m[at:at+n])
 return m,bindings,len(_common.loadInfoBlock(m,4,4))

def textured_model(permissions,materials,bindings,count,ground_y=0,trees=(),visible_ledges=False,fences=(),north_wall=False,water_tiles=()):
 if north_wall and not visible_ledges:raise ValueError('Northern wall uses the native cliff material; enable visible ledges')
 def mesh(tiles,width,height,y):
  commands=[(0x20,[0x7fff]),(0x21,[511<<10]),(0x40,[1])]
  for x,z,w,h in tiles:
   # 16 native world units per walking tile; repeat the existing texture.
   for px,pz,u,v in ((x,z,0,0),(x,z+h,0,height),(x+w,z+h,width,height),(x+w,z,width,0)):
    commands.append((0x22,[(u*16&65535)|((v*16&65535)<<16)]));commands.append(vertex(((px-16)/8,y/8,(pz-16)/8)))
  commands.append((0x41,[]));return fifo(commands)
 grass=[(i%32,i//32,1,1) for i,p in enumerate(permissions) if p&0xff==2 and not p&0x8000]
 ledges=[(i%32,i//32,1,1) for i,p in enumerate(permissions) if p&0x80ff==0x803B]
 shapes=[mesh([(0,0,32,32)],512,512,0),mesh(grass,16,16,.004),mesh(ledges,32,32,.004)]
 names=['grass01gs','egrass','cliff01gs']
 if visible_ledges:
  commands=[(0x20,[0x7fff]),(0x21,[511<<10]),(0x40,[1])]
  # A low native cliff billboard stays inside each blocked ledge cell.
  # The ground collider and tested one-way permission remain unchanged.
  for x,z,_,_ in ledges:
   left=(x-16)/8;right=(x+1-16)/8;front=(z+.875-16)/8
   top=8/128;back=front-8/128
   for point,u,v in (((left,0,front),8,32),((right,0,front),24,32),((right,top,back),24,16),((left,top,back),8,16)):
    commands.append((0x22,[(u*16&65535)|((v*16&65535)<<16)]));commands.append(vertex(point))
  if north_wall:
   # Fill the exposed sixteen-world-unit visual step beneath Cerulean.
   # Native stair openings remain clear; this does not alter any collider.
   for x in range(32):
    if x in (11,12,13,26,27,28):continue
    left=(x-16)/8;right=(x+1-16)/8;front=-2
    for point,u,v in (((left,0,front),8,31),((right,0,front),24,31),((right,16/128,front),24,22),((left,16/128,front),8,22)):
     commands.append((0x22,[(u*16&65535)|((v*16&65535)<<16)]));commands.append(vertex(point))
  commands.append((0x41,[]));shapes[2]=fifo(commands);names[2]='allpeakgs'
 nodes=[(0,ground_y,0),(0,0,0),(0,0,0)]
 if trees:
  # Native Route5 tree01gs is two trees across a 64x64 texture. The original
  # canopy quad rises49.34375 and leans40.765625 world units for its64 width.
  # Use one half of that quad, uniformly scaled to one Yellow walking tile.
  commands=[(0x20,[0x7fff]),(0x21,[511<<10]),(0x40,[1])]
  for x,z in trees:
   left=(x-16)/8;right=(x+1-16)/8;front=(z+1-16)/8
   top=24.671875/128;back=front-20.3828125/128
   for point,u,v in (((left,0,front),0,64),((right,0,front),32,64),((right,top,back),32,0),((left,top,back),0,0)):
    commands.append((0x22,[(u*16&65535)|((v*16&65535)<<16)]));commands.append(vertex(point))
  commands.append((0x41,[]));shapes.append(fifo(commands));nodes.append((0,0,0));names.append('tree01gs')
 if fences:
  # Native fence_a pickets are slanted billboards. Each source boundary
  # remains blocked by its original permission, including the gate approach.
  commands=[(0x20,[0x7fff]),(0x21,[511<<10]),(0x40,[1])]
  for x,z,kind in fences:
   width=8 if kind==0x3a else 16
   left=(x+.5-16)/8-width/256;right=left+width/128
   front=(z+.8-16)/8;top=11.3125/128;back=front-11.3125/128
   for point,u,v in (((left,0,front),0,16),((right,0,front),width,16),((right,top,back),width,0),((left,top,back),0,0)):
    commands.append((0x22,[(u*16&65535)|((v*16&65535)<<16)]));commands.append(vertex(point))
  commands.append((0x41,[]));shapes.append(fifo(commands));nodes.append((0,0,0));names.append('fence_a')
 if water_tiles:
  # Reuse the native Route6 pond texture; no effect on existing Route5 builds.
  if 'pond_on' not in bindings:raise ValueError('Native pond texture required')
  shapes.append(mesh([(x,z,1,1) for x,z in water_tiles],16,16,.008));nodes.append((0,0,0));names.append('pond_on')
 b=model('Route5Native',[*shapes],nodes,scale=128);base=struct.unpack_from('<I',b,16)[0]+48;payload=bytearray(b[base:]);sbc,mo,so,en=struct.unpack_from('<4I',payload,4)
 # Use the complete original material section, preserving native external bindings.
 delta=len(materials)-(so-mo);payload[mo:so]=materials
 struct.pack_into('<I',payload,0,len(payload));struct.pack_into('<2I',payload,12,so+delta,en+delta);payload[24]=count
 sb=payload[sbc:mo];at=8
 for i,name in enumerate(names):
  if i:at+=6
  assert sb[at:at+2]==bytes([4,0]);sb[at+1]=bindings[name][0];at+=6
 payload[sbc:mo]=sb
 struct.pack_into('<6h',payload,44,-8192,0,-8192,16384,4096,16384)
 return container(b'BMD0',[single_block(b'MDL0','Route5Native',payload)],2)

def patch_probe_materials(rom,*,diagnostic=False):
 if not diagnostic:raise ValueError('Unfinished native material probe requires diagnostic=True')
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);assert d[TABLE+13*24+20]&1
 paths=('a/0/4/1','a/0/6/5');mat,lands=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 old=[list(mat.files),list(lands.files)];mid=struct.unpack_from('<H',d,TABLE+13*24+4)[0];matrix=mat.files[mid]
 if matrix[:5]!=bytes([1,2,0,0,0]) or len(matrix)!=9:raise ValueError('Expected the private two-cell Route 5 matrix')
 materials,bindings,count=native_materials(lands);ids=[]
 for lid in struct.unpack_from('<2H',matrix,5):
  raw=lands.files[lid];ps,os,ms,bs,magic=struct.unpack_from('<5I',raw);assert ps==2048 and magic==0x1234
  permissions=struct.unpack_from('<1024H',raw,20);bmd=textured_model(permissions,materials,bindings,count)
  start=20+ps;props=raw[start:start+os];bdhc=raw[start+os+ms:start+os+ms+bs]
  ids.append(len(lands.files));lands.files.append(struct.pack('<5I',ps,os,len(bmd),bs,magic)+raw[20:start]+props+bmd+bdhc)
 newmid=len(mat.files);mat.files.append(matrix[:5]+struct.pack('<2H',*ids));struct.pack_into('<H',d,TABLE+13*24+4,newmid)
 for arc,p,prefix in zip((mat,lands),paths,old):assert arc.files[:len(prefix)]==prefix;rom.files[rom.filenames.idOf(p)]=arc.save()
 rom.arm9=main.save(compress=True)
 return dict(private=True,final_art=False,matrix=newmid,lands=ids,materials=['grass01gs','egrass','cliff01gs'],pending=['building props','visible ledge geometry','city connections','save migration'])
