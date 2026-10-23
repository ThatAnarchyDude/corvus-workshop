"""Yellow's Fan Club Bike Voucher reward in the unchanged HG room."""
import struct
import ndspy.narc
from opening import Script,end,script_bank,encode_text
from parcel_quest import PH,split_bank
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
from cerulean_bike import VOUCHER
MAP=362
VOUCHER_GIVEN=0xA9E  # Persistent native-unused flag; below daily reset range 0xAA0.
LABELS=('ChairmanIntroText','ChairmanStoryText','ReceivedBikeVoucherText','ExplainBikeVoucherText','NoStoryText','ChairFinalText','BagFullText')
def chairman(first):
 s=Script().emit(73,1500).emit(96).emit(104).emit(32,VOUCHER_GIVEN).jump('repeat',1)
 s.msg(first).emit(63,0x800C).compare(0x800C,0).jump('decline',5).msg(first+1)
 s.emit(125,VOUCHER,1,0x800C).compare(0x800C,0).jump('full',1)
 s.emit(30,VOUCHER_GIVEN).emit(78,1185).msg(first+2).emit(79).msg(first+3);end(s)
 s.label('decline').msg(first+4);end(s)
 s.label('repeat').msg(first+5);end(s)
 s.label('full').msg(first+6);return end(s).finish()
def patch(rom,messages):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+MAP*24
 sid,iid,tid=struct.unpack_from('<3H',d,rec+6);scriptid=rom.filenames.idOf('a/0/1/2');textid=rom.filenames.idOf('a/0/2/7')
 scripts=ndspy.narc.NARC(rom.files[scriptid]);texts=ndspy.narc.NARC(rom.files[textid]);bank=split_bank(scripts.files[sid]);key,words=decode_messages(texts.files[tid]);first=len(words)
 lines=[messages[k] for k in LABELS];lines[2]='Received a BIKE VOUCHER!'
 _,added=decode_messages(encode_text(lines,PH));new_tid=len(texts.files);texts.files.append(encode_messages(key,words+added))
 # Keep native code and its internal relative branches at their original offsets.
 native=bytearray(scripts.files[sid]);native.extend(bytes(-len(native)%4));start=len(native);native.extend(chairman(first));struct.pack_into('<I',native,0,start-4)
 new_sid=len(scripts.files);scripts.files.append(bytes(native));struct.pack_into('<H',d,rec+6,new_sid);struct.pack_into('<H',d,rec+10,new_tid)
 rom.files[scriptid]=scripts.save();rom.files[textid]=texts.save();rom.arm9=main.save(compress=True)
 return {'map':MAP,'old_script':sid,'script':new_sid,'old_text':tid,'text':new_tid,'first_message':first,'voucher':VOUCHER,'given_flag':VOUCHER_GIVEN,'native_init_retained':iid,'geometry_events_warps_unchanged':True,'scope':'Chairman reward only; other Vermilion events pending'}