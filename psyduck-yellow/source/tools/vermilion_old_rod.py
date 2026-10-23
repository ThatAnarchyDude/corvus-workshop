"""Yellow's one-time Old Rod gift in Vermilion's unchanged HG fishing house."""
import struct
import ndspy.narc
from opening import Script,end,encode_text
from parcel_quest import PH
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
MAP=361
OLD_ROD=445
ROD_GIVEN=0xA9F  # Kanto-only persistent flag, not Johto's shared 0x75.
LABELS=('DoYouLikeToFishText','TakeThisText','FishingIsAWayOfLifeText','ThatsSoDisappointingText','HowAreTheFishBitingText','NoRoomText')
def guru(first):
 s=Script().emit(73,1500).emit(96).emit(104).emit(190);s.data.append(0)
 s.emit(32,ROD_GIVEN).jump('repeat',1).emit(128,OLD_ROD,1,0x800C).compare(0x800C,1).jump('repeat',1)
 s.msg(first).emit(63,0x800C).compare(0x800C,0).jump('decline',5)
 s.emit(125,OLD_ROD,1,0x800C).compare(0x800C,0).jump('full',1).emit(30,ROD_GIVEN)
 s.msg(first+1).emit(78,1185).msg(first+6).emit(79).msg(first+2);end(s)
 s.label('decline').msg(first+3);end(s)
 s.label('repeat').msg(first+4);end(s)
 s.label('full').msg(first+5);return end(s).finish()
def patch(rom,messages):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+MAP*24;sid,iid,tid=struct.unpack_from('<3H',d,rec+6)
 scriptid=rom.filenames.idOf('a/0/1/2');textid=rom.filenames.idOf('a/0/2/7');scripts=ndspy.narc.NARC(rom.files[scriptid]);texts=ndspy.narc.NARC(rom.files[textid]);key,words=decode_messages(texts.files[tid]);first=len(words)
 lines=[messages[k] for k in LABELS]+['{PLAYER} received an OLD ROD!'];_,added=decode_messages(encode_text(lines,PH));nt=len(texts.files);texts.files.append(encode_messages(key,words+added))
 native=bytearray(scripts.files[sid]);native.extend(bytes(-len(native)%4));at=len(native);native.extend(guru(first));struct.pack_into('<I',native,0,at-4);ns=len(scripts.files);scripts.files.append(bytes(native));struct.pack_into('<H',d,rec+6,ns);struct.pack_into('<H',d,rec+10,nt)
 rom.files[scriptid]=scripts.save();rom.files[textid]=texts.save();rom.arm9=main.save(compress=True)
 return {'map':MAP,'old_script':sid,'script':ns,'old_text':tid,'text':nt,'first_message':first,'rod':OLD_ROD,'given_flag':ROD_GIVEN,'johto_rod_flag_unchanged':0x75,'native_init_retained':iid,'geometry_events_warps_unchanged':True}