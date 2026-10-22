"""Private diagnostic Route 5 terrain compiler; not final graphics or release layout.

Original archives and matrix 0 stay intact. Production entry/exit integration,
HG-style textures/props, doors and save migration must precede release.
"""
import struct
import ndspy.narc
from viridian_tutorial import TABLE
from opening import events_encode
from title_models import model,fifo,vertex,rgb

def patch_probe(rom,layout,*,diagnostic=False):
    if not diagnostic:raise ValueError('Diagnostic terrain must be explicitly requested')
    if layout.get('dimensions')!=[20,36]:raise ValueError('Wrong Yellow Route 5 dimensions')
    positions={(c['x'],c['y']) for c in layout['cells']}
    if len(layout['cells'])!=720 or positions!={(x,y) for y in range(36) for x in range(20)}:raise ValueError('Incomplete or duplicate source grid')
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    assert d[TABLE+13*24+20]&1, 'Refusing a non-Kanto target'
    paths=('a/0/4/1','a/0/6/5','a/0/3/2');mat,lands,events=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];prefix=[list(a.files) for a in arcs]
    mid=struct.unpack_from('<H',d,TABLE+517*24+4)[0];m=mat.files[mid];w,h,heads,alts,n=m[:5];off=5+n+(2*w*h if heads else 0)+(w*h if alts else 0);lid=struct.unpack_from('<H',m,off)[0];template=lands.files[lid]
    ps,os,ms,bs,magic=struct.unpack_from('<5I',template);assert ps==2048 and magic==0x1234
    bdhc=template[20+ps+os+ms:20+ps+os+ms+bs];assert len(bdhc)==bs
    cells={(c['x']+6,c['y']):c for c in layout['cells']}
    ledge={(v['ledge'][0]+6,v['ledge'][1]) for v in layout['one_way_ledges']};ids=[]
    for row in (0,1):
     permissions=[];commands=[(0x29,[(31<<16)|0xc0]),(0x40,[1])]
     def color(x,z):
      if (x,z) in ledge:return (190,140,55)
      if cells.get((x,z),{}).get('collision_tile')==0x52:return (45,130,65)
      return (100,180,105) if cells.get((x,z),{}).get('walkable') else (45,60,50)
     for z in range(32):
      globalz=z+row*32
      for x in range(32):permissions.append(0x803B if (x,globalz) in ledge else 2 if cells.get((x,globalz),{}).get('collision_tile')==0x52 else 0 if cells.get((x,globalz),{}).get('walkable') else 0x8000)
      x=0
      while x<32:
       end=x+1;c=color(x,globalz)
       while end<32 and color(end,globalz)==c:end+=1
       commands.append((0x20,[rgb(c)]))
       for px,pz in ((x,z),(end,z),(end,z+1),(x,z+1)):commands.append(vertex(((px-16)/8,0,(pz-16)/8)))
       x=end
     commands.append((0x41,[]));bmd=bytearray(model('Route5Probe',[fifo(commands)],[(0,0,0)],scale=128));mdl=struct.unpack_from('<I',bmd,16)[0]+48;struct.pack_into('<6h',bmd,mdl+44,-8192,0,-8192,16384,4096,16384)
     raw=struct.pack('<5I',2048,0,len(bmd),len(bdhc),magic)+struct.pack('<1024H',*permissions)+bmd+bdhc
     ids.append(len(lands.files));lands.files.append(raw)
    newmatrix=len(mat.files);mat.files.append(bytes([1,2,0,0,0])+struct.pack('<2H',*ids));struct.pack_into('<H',d,TABLE+13*24+4,newmatrix)
    ne=len(events.files);events.files.append(events_encode([[],[],[],[]]));struct.pack_into('<H',d,TABLE+13*24+16,ne)
    for a,old,p in zip(arcs,prefix,paths):assert a.files[:len(old)]==old;rom.files[rom.filenames.idOf(p)]=a.save()
    rom.arm9=main.save(compress=True)
    return dict(private=True,final_art=False,matrix=newmatrix,lands=ids,dimensions=[20,36],native_grass_tiles=sum(c['collision_tile']==0x52 for c in layout['cells']),native_ledges=len(ledge),original_members_preserved=True,johto_unchanged=True,pending=['HG textures and props','doors','region connections','save migration'])
