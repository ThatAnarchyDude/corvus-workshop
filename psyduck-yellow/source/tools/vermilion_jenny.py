"""Owner-approved Jenny gift: requires a free party slot; no PC delivery."""
import struct
import ndspy.narc
from opening import Script,end,encode_text,events_decode,events_encode,actor
from parcel_quest import PH,append_bank
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
GIVEN=0xA87
THUNDER=10
SPECIES=7
LEVEL=10

def jenny(first):
 s=Script().emit(73,1500).emit(96).emit(104).emit(32,GIVEN).jump('repeat',1).emit(294,THUNDER,0x800C).compare(0x800C,0).jump('before',1)
 s.emit(332,0x800C).compare(0x800C,6).jump('full',1)
 s.msg(first+1).emit(63,0x800C).compare(0x800C,0).jump('decline',5)
 # Owner-approved party-only gift; completed flag is committed only after success.
 # Native GiveMon failure remains retryable; storage is never accessed.
 s.emit(137,SPECIES,LEVEL,0,0,0,0x800C).compare(0x800C,0).jump('full',1).emit(30,GIVEN).emit(78,1185).msg(first+5).emit(79).msg(first+2);end(s)
 s.label('before').msg(first);end(s)
 s.label('decline').msg(first+3);end(s)
 s.label('repeat').msg(first+4);end(s)
 s.label('full').msg(first+6);return end(s).finish()

def patch(rom,messages):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+54*24;sid,iid,tid=struct.unpack_from('<3H',d,rec+6);eid=struct.unpack_from('<H',d,rec+16)[0]
 paths=('a/0/1/2','a/0/2/7','a/0/3/2');scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 assert not any(struct.pack('<H',GIVEN) in raw for raw in scripts.files)
 for raw in events.files:
  if raw:
   try:groups=events_decode(raw)
   except (struct.error,IndexError):continue
   assert not any(struct.unpack_from('<H',row,8)[0]==GIVEN for row in groups[1])
 key,words=decode_messages(texts.files[tid]);first=len(words);lines=messages+['{PLAYER} received SQUIRTLE!','Oops. You already have a full party with you. Please, come back when you have a free spot?'];_,added=decode_messages(encode_text(lines,PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 bank,count=append_bank(scripts.files[sid],[jenny(first)]);ns=len(scripts.files);scripts.files.append(bank)
 g=events_decode(events.files[eid]);obj=max(struct.unpack_from('<H',row)[0] for row in g[1])+1;g[1].append(actor(obj,34,count+1,1305,312,facing=1));ne=len(events.files);events.files.append(events_encode(g))
 struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<H',d,rec+10,nt);struct.pack_into('<H',d,rec+16,ne)
 for path,arc in zip(paths,(scripts,texts,events)):rom.files[rom.filenames.idOf(path)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'map':54,'old_script':sid,'script':ns,'old_text':tid,'text':nt,'old_event':eid,'event':ne,'flag':GIVEN,'badge':THUNDER,'species':SPECIES,'level':LEVEL,'actor':obj,'position':[1305,312],'native_police_sprite_placeholder':34,'party_only_gift_approved':True,'pc_delivery':False,'release_pending_native_tests_and_final_artwork':True,'native_test_pending':True}