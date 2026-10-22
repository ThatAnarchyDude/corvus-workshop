"""Yellow Route2 aide supplies reusable Flash after ten owned species."""
import struct
import ndspy.narc
from opening import Script,end,encode_text
from parcel_quest import append_bank,PH
from prototype import decode_messages,encode_messages
from viridian_tutorial import TABLE
GIVEN=0xA60
FLASH=397

def aide(offset=0):
 s=Script().emit(96).emit(104).emit(32,GIVEN).jump('after',1).msg(offset)
 s.emit(246,0x800C).compare(0x800C,10).jump('notyet',0)
 s.emit(125,FLASH,1,0x800C).compare(0x800C,0).jump('full',1)
 s.emit(30,GIVEN).emit(78,1186).msg(offset+1).emit(79).jump('after')
 s.label('notyet').msg(offset+2);end(s)
 s.label('full').msg(offset+3);end(s)
 s.label('after').msg(offset+4);end(s)
 return s.finish()
LINES=["I'm one of PROF.OAK's AIDES! Catch at least 10 different POKEMON, and I will give you FLASH.","You have caught at least 10 kinds! Here is TM70 FLASH!","Please return when your POKEDEX records at least 10 caught species.","Please make room in your TMs pocket and speak to me again.","FLASH lights up dark caves such as ROCK TUNNEL. Teach it to a compatible POKEMON. Like the other TMs here, it can be reused."]
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+418*24
 scripts=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')]);texts=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')]);old_sid,init,old_tid=struct.unpack_from('<3H',d,rec+6)
 key,lines=decode_messages(texts.files[old_tid]);offset=len(lines);assert offset+5<256
 lines+=decode_messages(encode_text(LINES,PH))[1];tid=len(texts.files);texts.files.append(encode_messages(key,lines))
 old=scripts.files[old_sid];bank,count=append_bank(old,[aide(offset)]);target=count*4+4+struct.unpack_from('<I',bank,count*4)[0];struct.pack_into('<I',bank,0,target-4)
 sid=len(scripts.files);scripts.files.append(bytes(bank));struct.pack_into('<H',d,rec+6,sid);struct.pack_into('<H',d,rec+10,tid)
 rom.files[rom.filenames.idOf('a/0/1/2')]=scripts.save();rom.files[rom.filenames.idOf('a/0/2/7')]=texts.save();rom.arm9=main.save(compress=True)
 return dict(map=418,script=sid,original_script=old_sid,text=tid,original_text=old_tid,original_entries=count,message_offset=offset,flag=GIVEN,item=FLASH,required_owned_species=10,native_test='pending')

