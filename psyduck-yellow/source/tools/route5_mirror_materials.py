"""Private mirrored building material copies; originals and Johto remain intact."""
import struct
import ndspy.narc
from ndspy import _common
from viridian_tutorial import TABLE

def double_sided_model(raw):
 b=bytearray(raw);off=struct.unpack_from('<I',b,16)[0];changes=[]
 for name,_,_,v in _common.loadInfoBlock(b,off+8,4):
  base=off+struct.unpack('<I',v)[0];mat=base+struct.unpack_from('<I',b,base+8)[0]
  for material,_,_,p in _common.loadInfoBlock(b,mat+4,4):
   at=mat+struct.unpack('<I',p)[0]+12;old=struct.unpack_from('<I',b,at)[0];new=old|0xc0;struct.pack_into('<I',b,at,new);changes.append((at,old,new))
 return bytes(b),changes

def patch_probe_mirror_materials(rom,*,diagnostic=False):
 if not diagnostic:raise ValueError('Private mirror correction requires diagnostic=True')
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);assert d[TABLE+13*24+20]&1
 paths=('a/0/4/0','a/0/4/2','a/0/4/3','a/0/4/1','a/0/6/5','a/1/0/7','a/0/7/0');models,areas,lists,mat,lands,metadata,proptex=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];old=[list(a.files) for a in (models,areas,lists,mat,lands,metadata,proptex)]
 remap={};changes={}
 for model in (276,286,246):
  assert len(metadata.files)==len(models.files),'Building models and metadata must align'
  metadata.files.append(metadata.files[model])
  fixed,edits=double_sided_model(models.files[model]);remap[model]=len(models.files);models.files.append(fixed);changes[model]=edits
 area=bytearray(areas.files[d[TABLE+13*24+1]]);li=struct.unpack_from('<H',area)[0];original=list(struct.unpack('<'+'H'*(len(lists.files[li])//2),lists.files[li]));assert original[0]==len(original)-1
 entries=[original[0]]+[remap.get(v,v) for v in original[1:]];newli=len(lists.files);lists.files.append(struct.pack('<'+'H'*len(entries),*entries));struct.pack_into('<H',area,0,newli)
 assert len(proptex.files)==newli,'Prop texture banks and model lists must align'
 proptex.files.append(proptex.files[li])
 newarea=len(areas.files);assert newarea<256;areas.files.append(bytes(area));d[TABLE+13*24+1]=newarea
 mid=struct.unpack_from('<H',d,TABLE+13*24+4)[0];matrix=mat.files[mid];assert matrix[:5]==bytes([1,2,0,0,0]);ids=[]
 for lid in struct.unpack_from('<2H',matrix,5):
  raw=bytearray(lands.files[lid]);ps,os=struct.unpack_from('<2I',raw)
  for at in range(20+ps,20+ps+os,48):
   model=struct.unpack_from('<I',raw,at)[0]
   if model in remap:struct.pack_into('<I',raw,at,remap[model])
  ids.append(len(lands.files));lands.files.append(bytes(raw))
 newmid=len(mat.files);mat.files.append(matrix[:5]+struct.pack('<2H',*ids));struct.pack_into('<H',d,TABLE+13*24+4,newmid)
 for a,p,prefix in zip((models,areas,lists,mat,lands,metadata,proptex),paths,old):assert a.files[:len(prefix)]==prefix;rom.files[rom.filenames.idOf(p)]=a.save()
 # Native shape lookup is indexed by building ID; preserve every existing record.
 fid=rom.filenames.idOf('fielddata/build_model/bm_field_matshp.dat');lookup=rom.files[fid]
 count,shapes=struct.unpack_from('<2H',lookup);assert len(lookup)==4+4*(count+shapes) and count==min(remap.values())
 table=lookup[4:4+4*count];body=lookup[4+4*count:]
 rom.files[fid]=struct.pack('<2H',count+len(remap),shapes)+table+b''.join(table[m*4:m*4+4] for m in remap)+body
 rom.arm9=main.save(compress=True)
 return dict(private=True,final_art=False,model_remap=remap,area=newarea,model_list=newli,matrix=newmid,lands=ids,material_changes=changes)
