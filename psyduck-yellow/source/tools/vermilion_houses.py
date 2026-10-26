"""Yellow's Pidgey-house speakers and HM advice, retaining HG interiors."""
import struct
import ndspy.narc
from opening import Script,end,encode_text,events_decode,events_encode
from parcel_quest import PH
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE

def dialogue(message,cry=None):
 s=Script().emit(73,1500).emit(96).emit(104).msg(message)
 if cry is not None:s.emit(76,cry,0).emit(77)
 return end(s).finish()

def patch(rom,messages):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=('a/0/1/2','a/0/2/7','a/0/3/2');scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];reports=[]
 for mid,labels,cries in ((363,('youngster','pidgey'),(None,16)),(364,('hm_advice',),(None,))):
  rec=TABLE+mid*24;sid,iid,tid=struct.unpack_from('<3H',d,rec+6);key,words=decode_messages(texts.files[tid]);first=len(words)
  _,added=decode_messages(encode_text([messages[label] for label in labels],PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
  bank=bytearray(scripts.files[sid]);original_len=len(bank)
  for entry,cry in enumerate(cries):
   bank.extend(bytes(-len(bank)%4));at=len(bank);bank.extend(dialogue(first+entry,cry));struct.pack_into('<I',bank,entry*4,at-entry*4-4)
  ns=len(scripts.files);scripts.files.append(bytes(bank));struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<H',d,rec+10,nt)
  report={'map':mid,'old_script':sid,'script':ns,'old_text':tid,'text':nt,'native_init':iid,'first_message':first,'original_script_length':original_len,'messages':labels}
  if mid==363:
   eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[eid]);assert len(g[1])==2
   for i,sprite in enumerate((315,1005)):
    row=bytearray(g[1][i]);struct.pack_into('<H',row,2,sprite);g[1][i]=bytes(row)
   ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,ne);report.update(old_event=eid,event=ne,sprites=[315,1005])
  reports.append(report)
 for path,arc in zip(paths,(scripts,texts,events)):rom.files[rom.filenames.idOf(path)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'maps':reports,'interior_geometry_and_warps_unchanged':True,'letter_interaction_pending':True}