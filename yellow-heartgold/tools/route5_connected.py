"""PRIVATE compact Route5 in HG's connected main matrix. Not a release yet.

Owner-approved spacing reduction; only two Kanto main-matrix cells change.
Native coordinates remain global; no outdoor fade scripts or new executable hooks.
"""
import struct
import ndspy.narc
from route5_compact_layout import compact_layout
from route5_materials import native_materials,textured_model
from route5_mirror_materials import patch_probe_mirror_materials
from route5_props import PROPS,SCENERY
from opening import events_decode,events_encode
from viridian_tutorial import TABLE
ORIGIN=(1280,160);X_OFFSET=10
DOORS=((10,26,391,1,0x6f),(9,26,391,1,0x6f),(10,30,391,0,0x6e),(17,24,469,0,0x6e),(10,18,517,0,0x8069))
def matrix_offset(matrix,x,z):
 w,h,heads,alts,n=matrix[:5];assert 0<=x<w and 0<=z<h
 return 5+n+(2*w*h if heads else 0)+(w*h if alts else 0)+2*(z*w+x)
def patch_connected_probe(rom,source,*,diagnostic=False,native_trees=False,visible_ledges=False,north_access=False,native_fences=False,north_wall=False):
 if not diagnostic:raise ValueError('Unfinished connected terrain requires diagnostic=True')
 layout=compact_layout(source);main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 assert struct.unpack_from('<H',d,TABLE+13*24+4)[0]==0 and d[TABLE+13*24+1]==13
 mat=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')]);lands=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')]);oldmatrix=bytes(mat.files[0]);assert struct.unpack_from('<H',oldmatrix,matrix_offset(oldmatrix,40,5))[0]==153
 cells={(v['x']+X_OFFSET,v['y']):dict(v) for v in layout['cells']}
 if north_access:
  # Native HG city stairs meet Yellow's side roads. Connect them to the
  # central northern approach before the first ledge; preserve every ledge/door.
  for key in ((15,0),(24,0)):
   assert cells[key]['collision_tile'] in (0x50,0x3a) and not cells[key]['walkable']
   cells[key].update(walkable=True,collision_tile=0x2c)
 ledges={tuple((v['ledge'][0]+X_OFFSET,v['ledge'][1])) for v in layout['one_way_ledges']};permissions=[]
 for z in range(32):
  for x in range(32):
   c=cells.get((x,z),{});permissions.append(0x843b if (x,z) in ledges else 0x402 if c.get('collision_tile')==82 else 0x400 if c.get('walkable') else 0x8400)
 for x,z,_,_,behavior in DOORS:permissions[z*32+x+X_OFFSET]=behavior|0x400
 materials,bindings,count=native_materials(lands);trees=[(x,z) for (x,z),c in cells.items() if c.get("collision_tile")==0x50] if native_trees else [];fences=[(x,z,c["collision_tile"]) for (x,z),c in cells.items() if c.get("collision_tile") in (0x3a,0x55)] if native_fences else [];bmd=textured_model(permissions,materials,bindings,count,ground_y=32,trees=trees,visible_ledges=visible_ledges,fences=fences,north_wall=north_wall)
 # Source spacing cuts above all buildings total three rows; their geometry is retained.
 specs=[(m,x+4,z-3,1,1,1) for m,x,z in PROPS]+[(m,x+4,z-3,sx,sy,sz) for m,x,z,sx,sy,sz in SCENERY]
 props=b''.join(struct.pack('<12i',m,round((x-16)*65536),131072,round((z-16)*65536),0,0,0,round(sx*4096),round(sy*4096),round(sz*4096),0,0) for m,x,z,sx,sy,sz in specs)
 city=lands.files[133];ps,os,ms,bs,magic=struct.unpack_from('<5I',city);bdhc=city[20+ps+os+ms:];assert len(bdhc)==66 and bdhc[:4]==b'BDHC' and struct.unpack_from('<i',bdhc,44)[0]==-131072
 raw=struct.pack('<5I',2048,len(props),len(bmd),len(bdhc),0x1234)+struct.pack('<1024H',*permissions)+props+bmd+bdhc;lid=len(lands.files);lands.files.append(raw)
 temp=len(mat.files);mat.files.append(bytes([1,2,0,0,0])+struct.pack('<2H',lid,lid));struct.pack_into('<H',d,TABLE+13*24+4,temp)
 for p,a in (('a/0/4/1',mat),('a/0/6/5',lands)):rom.files[rom.filenames.idOf(p)]=a.save()
 rom.arm9=main.save(compress=True);mirror=patch_probe_mirror_materials(rom,diagnostic=True)
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);areas=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/2')]);lists=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/3')]);banks=[i for i,b in enumerate(areas.files) if struct.unpack_from('<H',b)[0]==12]
 assert all(d[TABLE+m*24+20]&1 for m in range(540) if d[TABLE+m*24+1] in banks),'Kanto-only graphics resource required'
 entries=list(struct.unpack('<'+'H'*(len(lists.files[12])//2),lists.files[12]));assert entries[0]==23
 entries=[entries[0]+3]+entries[1:]+list(mirror['model_remap'].values());lists.files[12]=struct.pack('<'+'H'*len(entries),*entries)
 # Preserve the native area bank for seamless Cerulean/Route5 resource sharing.
 d[TABLE+13*24+1]=13;struct.pack_into('<H',d,TABLE+13*24+4,0)
 mat=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')]);lands=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')]);matrix=bytearray(oldmatrix);struct.pack_into('<H',matrix,matrix_offset(matrix,40,5),mirror['lands'][0])
 # The relocated gate sits wholly in Route5. Remove only its obsolete Saffron prop,
 # and open the existing level-four road at the shared boundary.
 raw=bytearray(city);oldprops=[city[20+ps+i:20+ps+i+48] for i in range(0,os,48)];newprops=[p for p in oldprops if not (struct.unpack_from('<I',p)[0]==246 and struct.unpack_from('<i',p,4)[0]==327680)]
 assert len(oldprops)-len(newprops)==1
 for z in range(8):
  for x in (20,21):struct.pack_into('<H',raw,20+2*(z*32+x),0x400)
 cityraw=struct.pack('<5I',ps,48*len(newprops),ms,bs,magic)+raw[20:20+ps]+b''.join(newprops)+city[20+ps+os:];cityid=len(lands.files);lands.files.append(cityraw);struct.pack_into('<H',matrix,matrix_offset(matrix,40,6),cityid);mat.files[0]=bytes(matrix)
 events=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')]);changed=[]
 def install(m,g):
  assert d[TABLE+m*24+20]&1;ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,TABLE+m*24+16,ne);changed.append(m)
 outside=[[],[],[struct.pack('<4HI',ORIGIN[0]+x+X_OFFSET,ORIGIN[1]+z,target,anchor,0) for x,z,target,anchor,_ in DOORS],[]];outside[0]=[struct.pack('<HHiiiH2x',1,0,1307,186,2,4)];install(13,outside)
 for m,returns in ((517,{0:4}),(469,{0:3}),(391,{0:2,1:0})):
  g=events_decode(events.files[struct.unpack_from('<H',d,TABLE+m*24+16)[0]])
  for i,anchor in returns.items():v=bytearray(g[2][i]);struct.pack_into('<2H',v,4,13,anchor);g[2][i]=bytes(v)
  install(m,g)
 for p,a in (('a/0/4/1',mat),('a/0/6/5',lands),('a/0/4/3',lists),('a/0/3/2',events)):rom.files[rom.filenames.idOf(p)]=a.save()
 rom.arm9=main.save(compress=True)
 return dict(private=True,released=False,north_access=north_access,north_wall=north_wall,native_tree_count=len(trees),native_fence_count=len(fences),visible_ledge_count=40 if visible_ledges else 0,connected_main_matrix=True,removed_rows=list(layout['removed_spacing_rows']),dimensions=[20,32],x_offset=X_OFFSET,origin=list(ORIGIN),route_land=mirror['lands'][0],saffron_land=cityid,changed_kanto_cells=[[40,5],[40,6]],changed_headers=changed,grass_tiles=48,ledges=40,pending=['native seamless boundary tests','legacy save Continue','doors and heights','final trees/ledge geometry and gate interior'])
