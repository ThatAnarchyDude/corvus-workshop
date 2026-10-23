"""Yellow Vermilion Mart conversations, preserving both native clerks."""
import struct
import ndspy.narc
from opening import Script,end,encode_text
from prototype import decode_messages,encode_messages
from parcel_quest import PH
from viridian_tutorial import TABLE

def patch(rom,messages):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+360*24;sid,iid,tid=struct.unpack_from('<3H',d,rec+6)
 sp,tp='a/0/1/2','a/0/2/7';scripts=ndspy.narc.NARC(rom.files[rom.filenames.idOf(sp)]);texts=ndspy.narc.NARC(rom.files[rom.filenames.idOf(tp)]);key,words=decode_messages(texts.files[tid]);first=len(words);_,added=decode_messages(encode_text(messages,PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 native=scripts.files[sid];assert struct.unpack_from('<H',native,16)[0]==0xFD13;bank=bytearray(native)
 for entry in (2,3):
  bank.extend(bytes(-len(bank)%4));at=len(bank);bank.extend(end(Script().emit(73,1500).emit(96).emit(104).msg(first+entry-2)).finish());struct.pack_into('<I',bank,entry*4,at-entry*4-4)
 assert bank[:8]==native[:8] and bank[16:len(native)]==native[16:]
 ns=len(scripts.files);scripts.files.append(bytes(bank));struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<H',d,rec+10,nt)
 rom.files[rom.filenames.idOf(sp)]=scripts.save();rom.files[rom.filenames.idOf(tp)]=texts.save();rom.arm9=main.save(compress=True)
 return {'map':360,'script':ns,'text':nt,'old_script':sid,'old_text':tid,'native_clerks_room_events_and_services_retained':True,'yellow_inventory_conversion_pending':True,'native_dialogue_test_pending':True}