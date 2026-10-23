"""Private native Underground house/sign placement; Route 5 scenery unfinished."""
import struct
import ndspy.narc
from viridian_tutorial import TABLE
# Native land153: Underground warp(26,25), pivot(27,24.5);
# sign event(28,26), pivot(28.5,26.5). Translate those measured anchors.
PROPS=((290,24,26.5),(31,23.5,29.5))
# Mirror the native left-side house doorway to Yellow's right-side entrance.
# Door leaf center:15.8125+0.6875=16.5, z20.640625+0.6875*1.25=21.5.
SCENERY=((276,16,20.640625,-1,1,1.25),(286,15.8125,21.421875,-1,1,1.25),(246,15.859375,32,-1.28,1,.5))

def patch_probe_props(rom,*,diagnostic=False,scenery=False):
 if not diagnostic:raise ValueError('Unfinished prop placement requires diagnostic=True')
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);assert d[TABLE+13*24+20]&1
 paths=('a/0/4/1','a/0/6/5');mat,lands=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];old=[list(mat.files),list(lands.files)]
 mid=struct.unpack_from('<H',d,TABLE+13*24+4)[0];matrix=mat.files[mid]
 if matrix[:5]!=bytes([1,2,0,0,0]) or len(matrix)!=9:raise ValueError('Expected private two-cell terrain')
 specs=[(m,x,z,1,1,1) for m,x,z in PROPS]+(list(SCENERY) if scenery else [])
 ids=[]
 for row,lid in enumerate(struct.unpack_from('<2H',matrix,5)):
  raw=lands.files[lid];ps,os,ms,bs,magic=struct.unpack_from('<5I',raw);assert os==0,'Avoid replacing an existing prop set'
  props=b''.join(struct.pack('<12i',model,round((x-16)*65536),0,round((z-row*32-16)*65536),0,0,0,round(sx*4096),round(sy*4096),round(sz*4096),0,0) for model,x,z,sx,sy,sz in specs if int(z)//32==row)
  ids.append(len(lands.files));lands.files.append(struct.pack('<5I',ps,len(props),ms,bs,magic)+raw[20:20+ps]+props+raw[20+ps:])
 newmid=len(mat.files);mat.files.append(matrix[:5]+struct.pack('<2H',*ids));struct.pack_into('<H',d,TABLE+13*24+4,newmid)
 for arc,p,prefix in zip((mat,lands),paths,old):assert arc.files[:len(prefix)]==prefix;rom.files[rom.filenames.idOf(p)]=arc.save()
 rom.arm9=main.save(compress=True)
 return dict(private=True,final_art=False,matrix=newmid,lands=ids,props=[{'model':m,'pivot':[x,z]} for m,x,z in PROPS],scenery_probe=scenery,pending=['Day Care model and door alignment','gate model','trees','ledge geometry','city connections','save migration'])
