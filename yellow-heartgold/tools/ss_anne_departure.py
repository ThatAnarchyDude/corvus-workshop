"""One-time Anne departure state and gate closure; native geometry remains intact."""
import struct,json
from pathlib import Path
import ndspy.narc
from opening import Script,end,script_bank,encode_text,events_decode,events_encode
from parcel_quest import PH,append_bank
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
from ss_anne_boarding import ticket_gate,sailor_talk
CUT_GIVEN=0xA7F
DEPARTED=0xA7D
TEMP=0x4000

def arrival():
 s=Script().emit(41,TEMP,1).emit(32,DEPARTED).jump('done',1).emit(32,CUT_GIVEN).jump('done',5)
 s.emit(105,0x800C,0x800D).compare(0x800C,23).jump('done',5).compare(0x800D,18).jump('done',5)
 s.emit(96).emit(73,1752).msg(0).emit(75,1752)
 # Follow the previously walked native dock path, rather than walking through models.
 s.movement(255,'leave').emit(95).emit(723)
 s.data.extend(struct.pack('<BB3H',1,0,263,7,11))
 s.emit(30,DEPARTED).emit(97).label('done').emit(2)
 s.moves('leave',[(13,2),(14,11),(12,7)])
 return s.finish()

def guarded_gate(message):
 s=Script().emit(386,0x800C).compare(0x800C,0).jump('free',1).emit(32,DEPARTED).jump('closed',1)
 while len(s.data)%4:s.emit(0)
 s.data.extend(ticket_gate())
 s.label('free').emit(2)
 s.label('closed').emit(96).msg(message).movement(255,'back').emit(95);end(s);s.moves('back',[(12,1)])
 return s.finish()

def guarded_talk(message):
 s=Script().emit(32,DEPARTED).jump('closed',1);s.data.extend(sailor_talk());s.label('closed').emit(73,1500).emit(96).emit(104).msg(message)
 return end(s).finish()

def patch(rom):
 audit=json.loads(Path('yellow-heartgold/build/0031-source-audit-v1/audit.json').read_text());assert audit['candidate_departure_flag']=='0xa7d' and not audit['raw_script_matches'] and not audit['actor_matches']
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=('a/0/1/2','a/0/2/7','a/0/3/2');scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 at=TABLE+263*24;oldscript,_,oldtext=struct.unpack_from('<3H',d,at+6);oldevent=struct.unpack_from('<H',d,at+16)[0]
 key,words=decode_messages(texts.files[oldtext]);message=len(words);_,added=decode_messages(encode_text(['The S.S. ANNE has set sail!'],PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 bank,count=append_bank(scripts.files[oldscript],[guarded_gate(message),guarded_talk(message)]);assert count==4
 ns=len(scripts.files);scripts.files.append(bank);g=events_decode(events.files[oldevent]);coord=bytearray(g[3][0]);struct.pack_into('<H',coord,0,count+1);g[3][0]=bytes(coord)
 actor=bytearray(g[1][0]);assert struct.unpack_from('<H',actor,10)[0]==1
 struct.pack_into('<H',actor,10,count+2);g[1][0]=bytes(actor);ne=len(events.files);events.files.append(events_encode(g))
 for off,val in ((6,ns),(10,nt),(16,ne)):struct.pack_into('<H',d,at+off,val)
 at=TABLE+264*24;sid=len(scripts.files);scripts.files.append(script_bank([Script().emit(41,TEMP,0).emit(2).finish(),arrival()]));ini=len(scripts.files);scripts.files.append(struct.pack('<BHHBI',2,1,0,1,1)+bytes(1)+struct.pack('<3H',TEMP,0,2)+bytes(2));tid=len(texts.files);texts.files.append(encode_text(['The S.S. ANNE is setting sail!'],PH));struct.pack_into('<3H',d,at+6,sid,ini,tid)
 for path,archive in zip(paths,(scripts,texts,events)):rom.files[rom.filenames.idOf(path)]=archive.save()
 rom.arm9=main.save(compress=True)
 return dict(departed_flag=DEPARTED,cut_given_flag=CUT_GIVEN,arrival_only=[264,23,18],maps=[263,264],native_cinematic_opcode=723,native_cinematic_overlay=105,moving_ship_visual_pending=True,native_tests_pending=True)


