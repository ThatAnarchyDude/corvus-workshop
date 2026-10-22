"""Private Route 5 door plumbing; final buildings/connections remain unfinished."""
import struct
import ndspy.narc
from viridian_tutorial import TABLE
from opening import events_decode,events_encode
# Exterior points preserve Yellow coordinates, offset six tiles inside the DS cell.
# map13 warp index, x, z, destination, native destination anchor, terrain behavior
DOORS=((0,16,29,391,1,0x6F),(1,15,29,391,1,0x6F),(2,16,33,391,0,0x6E),(3,23,27,469,0,0x6E),(4,16,21,517,0,0x8069))

def patch_probe_doors(rom,*,diagnostic=False):
 if not diagnostic:raise ValueError('Unfinished diagnostic door layout must be explicitly requested')
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=('a/0/4/1','a/0/6/5','a/0/3/2');mat,lands,events=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];old=[list(a.files) for a in arcs]
 matrix_id=struct.unpack_from('<H',d,TABLE+13*24+4)[0];matrix=mat.files[matrix_id]
 if matrix[:5]!=bytes([1,2,0,0,0]) or len(matrix)!=9:raise ValueError('Expected the diagnostic two-cell Route 5 matrix')
 oldlands=struct.unpack_from('<2H',matrix,5);newlands=[]
 for row,index in enumerate(oldlands):
  raw=bytearray(lands.files[index])
  for _,x,z,_,_,behavior in DOORS:
   if z//32==row:struct.pack_into('<H',raw,20+2*(z%32*32+x),behavior)
  newlands.append(len(lands.files));lands.files.append(raw)
 nm=len(mat.files);mat.files.append(bytes([1,2,0,0,0])+struct.pack('<2H',*newlands));struct.pack_into('<H',d,TABLE+13*24+4,nm)
 changed=[]
 def install(m,g):
  if not d[TABLE+m*24+20]&1:raise ValueError('Refusing non-Kanto door changes')
  ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,TABLE+m*24+16,ne);changed.append(m)
 outside=[[],[],[struct.pack('<4HI',x,z,target,anchor,0) for _,x,z,target,anchor,_ in DOORS],[]]
 outside[0]=[struct.pack('<HHiiiH2x',1,0,23,29,0,4)];install(13,outside)
 for m,returns in ((517,{0:4}),(469,{0:3}),(391,{0:2,1:0})):
  eid=struct.unpack_from('<H',d,TABLE+m*24+16)[0];g=events_decode(events.files[eid])
  for index,anchor in returns.items():
   row=bytearray(g[2][index]);struct.pack_into('<2H',row,4,13,anchor);g[2][index]=bytes(row)
  install(m,g)
 for a,prefix,path in zip(arcs,old,paths):assert a.files[:len(prefix)]==prefix;rom.files[rom.filenames.idOf(path)]=a.save()
 rom.arm9=main.save(compress=True)
 return dict(private=True,changed_headers=sorted(changed),matrix=nm,lands=newlands,doors=[list(v) for v in DOORS],original_members_preserved=True,johto_unchanged=True,pending=['native round-trip tests','final building models','Yellow gate interior geometry','north/south city connections','save migration'])
