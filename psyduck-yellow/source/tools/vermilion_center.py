"""Yellow training advice and Chansey in Vermilion's native HG Center."""
import struct
import ndspy.narc
from opening import encode_text,events_decode,events_encode
from prototype import decode_messages,encode_messages
from parcel_quest import PH
from viridian_tutorial import TABLE
from vermilion_houses import dialogue

def patch(rom,messages):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+358*24;sid,iid,tid=struct.unpack_from('<3H',d,rec+6);eid=struct.unpack_from('<H',d,rec+16)[0]
 paths=('a/0/1/2','a/0/2/7','a/0/3/2');scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];key,words=decode_messages(texts.files[tid]);first=len(words);_,added=decode_messages(encode_text(messages,PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 native=scripts.files[sid];assert struct.unpack_from('<H',native,16)[0]==0xFD13;bank=bytearray(native)
 for entry,msg,cry in ((1,first,None),(3,first+1,113)):
  bank.extend(bytes(-len(bank)%4));at=len(bank);bank.extend(dialogue(msg,cry));struct.pack_into('<I',bank,entry*4,at-entry*4-4)
 assert bank[:4]==native[:4] and bank[8:12]==native[8:12] and bank[16:len(native)]==native[16:]
 ns=len(scripts.files);scripts.files.append(bytes(bank));g=events_decode(events.files[eid]);assert len(g[1])==7
 row=bytearray(g[1][6]);assert struct.unpack_from('<H',row,10)[0]==4;struct.pack_into("<2H",row,2,1021,0);g[1][6]=bytes(row);ne=len(events.files);events.files.append(events_encode(g))
 struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<H',d,rec+10,nt);struct.pack_into('<H',d,rec+16,ne)
 for path,arc in zip(paths,(scripts,texts,events)):rom.files[rom.filenames.idOf(path)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'map':358,'script':ns,'text':nt,'event':ne,'old_script':sid,'old_text':tid,'old_event':eid,'native_nurse_and_link_services_unchanged':True,'native_room_props_and_warps_unchanged':True,'chansey_sprite':1021,'chansey_species':113,'poison_dialogue_pending':True,'native_gameplay_pending':True}