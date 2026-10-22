"""Yellow's readable PIPPI letter, added to the existing HG house table."""
import struct
import ndspy.narc
from opening import Script,end,encode_text,events_decode,events_encode
from parcel_quest import PH
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
from cerulean_robbery import land_start,append_mesh
from title_models import mesh
MAP=363
TABLE_CELLS=((6,5),(7,5),(6,6),(7,6))

def paper_mesh(height):
 tris=[]
 def quad(x,z,w,h,y,color):
  p=[(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)]
  for i,j,k in ((0,1,2),(0,2,3)):tris.append((tuple(v/64 for v in p[i]),tuple(v/64 for v in p[j]),tuple(v/64 for v in p[k]),color))
 quad(-149,-164,10,8,height,(248,243,225))
 for z,width in ((-162,6),(-160,6),(-158,4)):quad(-147,z,width,.4,height+.05,(64,73,91))
 return mesh(tris)

def patch(rom,message,*,paper_height=20.1):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+MAP*24
 paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/4/1','a/0/6/5');scripts,texts,events,matrices,lands=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 sid,iid,tid=struct.unpack_from('<3H',d,rec+6);eid=struct.unpack_from('<H',d,rec+16)[0]
 key,words=decode_messages(texts.files[tid]);first=len(words);_,added=decode_messages(encode_text([message],PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 native=scripts.files[sid];count=next(i for i in range(50) if struct.unpack_from('<H',native,i*4)[0]==0xFD13);assert count==2
 old_header=(4*count+5)&~3;new_header=old_header+4;bank=bytearray(new_header)+native[old_header:]
 for i in range(count):struct.pack_into('<I',bank,i*4,struct.unpack_from('<I',native,i*4)[0]+4)
 bank.extend(bytes(-len(bank)%4));struct.pack_into('<I',bank,count*4,len(bank)-count*4-4);bank.extend(end(Script().emit(73,1500).emit(96).msg(first)).finish());struct.pack_into('<H',bank,(count+1)*4,0xFD13)
 assert bank[new_header:new_header+len(native)-old_header]==native[old_header:]
 ns=len(scripts.files);scripts.files.append(bytes(bank));g=events_decode(events.files[eid]);assert not g[0]
 for x,z in TABLE_CELLS:g[0].append(struct.pack('<HHiiiH2x',count+1,0,x,z,0,4))
 ne=len(events.files);events.files.append(events_encode(g))
 old_mid=struct.unpack_from('<H',d,rec+4)[0];matrix=bytearray(matrices.files[old_mid]);assert matrix[:4]==bytes((1,1,0,0));at=5+matrix[4];old_lid=struct.unpack_from('<H',matrix,at)[0];land=bytearray(lands.files[old_lid]);start=land_start(land);ps,bs,ms=struct.unpack_from('<3I',land)
 for x,z in TABLE_CELLS:assert struct.unpack_from('<H',land,start+2*(32*z+x))[0]&0x8000
 model_start=start+ps+bs;old_model=bytes(land[model_start:model_start+ms]);new_model=append_mesh(old_model,paper_mesh(paper_height));land[model_start:model_start+ms]=new_model;struct.pack_into('<I',land,8,len(new_model))
 lid=len(lands.files);lands.files.append(bytes(land));struct.pack_into('<H',matrix,at,lid);mid=len(matrices.files);matrices.files.append(bytes(matrix))
 struct.pack_into('<H',d,rec+4,mid);struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<H',d,rec+10,nt);struct.pack_into('<H',d,rec+16,ne)
 for path,arc in zip(paths,(scripts,texts,events,matrices,lands)):rom.files[rom.filenames.idOf(path)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'map':MAP,'script':ns,'text':nt,'event':ne,'matrix':mid,'land':lid,'old_matrix':old_mid,'old_land':old_lid,'table_cells':TABLE_CELLS,'paper_height':paper_height,'native_room_props_collision_and_warps_unchanged':True,'native_render_and_interaction_pending':True}