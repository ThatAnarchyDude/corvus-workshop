"""Yellow captain-room scenery dialogue on native bin and desk."""
import struct
import ndspy.narc
from opening import Script,end,encode_text,events_decode,events_encode
from prototype import decode_messages,encode_messages
from parcel_quest import PH,append_bank
from viridian_tutorial import TABLE
MAP=255
MESSAGES=["Yuck! Shouldn't have looked!", "How to Conquer Seasickness...\rThe CAPTAIN's reading this!"]
TARGETS=((8,4,2),(9,5,3),(10,5,3))
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);at=TABLE+MAP*24
 sid,_,tid=struct.unpack_from('<3H',d,at+6);eid=struct.unpack_from('<H',d,at+16)[0]
 paths=('a/0/1/2','a/0/2/7','a/0/3/2');scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 original=scripts.files[sid];assert struct.unpack_from('<H',original,4)[0]==0xFD13
 key,words=decode_messages(texts.files[tid]);first=len(words);_,added=decode_messages(encode_text(MESSAGES,PH))
 nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 ns=len(scripts.files);bank,count=append_bank(original,[end(Script().emit(73,1500).emit(96).msg(first+i)).finish() for i in range(2)]);assert count==1;scripts.files.append(bank)
 g=events_decode(events.files[eid]);assert not g[0] and len(g[1])==1 and len(g[2])==1
 g[0]=[struct.pack('<HHiiiH2x',entry,0,x,z,0,4) for x,z,entry in TARGETS]
 ne=len(events.files);events.files.append(events_encode(g))
 for offset,value in ((6,ns),(10,nt),(16,ne)):struct.pack_into('<H',d,at+offset,value)
 for p,arc in zip(paths,(scripts,texts,events)):rom.files[rom.filenames.idOf(p)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'map':MAP,'old_script':sid,'script':ns,'old_text':tid,'text':nt,'old_event':eid,'event':ne,'targets':TARGETS,'first_message':first,'native_geometry_unchanged':True,'native_interaction_pending':True}

