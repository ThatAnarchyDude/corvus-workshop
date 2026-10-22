"""Yellow captain's one-time Cut reward in the isolated Kanto cabin copy."""
import json,struct
from pathlib import Path
import ndspy.narc
from opening import Script,end,script_bank,encode_text,events_decode,events_encode,actor
from parcel_quest import PH
from viridian_tutorial import TABLE
GIVEN=0xA7F
HM_CUT=420
MESSAGES=["CAPTAIN: Ooargh... I feel hideous... Urrp! Seasick...\r{PLAYER} rubbed the CAPTAIN's back!\rRub-rub... Rub-rub...", "CAPTAIN: Whew! Thank you! I feel much better!\rYou want to see my CUT technique?\rI could show you if I wasn't ill...\rI know! You can have this!\rTeach it to your Pokemon and you can see it CUT anytime!", "{PLAYER} received HM01 (CUT)!", "CAPTAIN: Whew!\rNow that I'm not sick anymore, I guess it's time.", "Oh no! You have no room for this!"]
def captain():
 s=Script().emit(73,1500).emit(96).emit(32,GIVEN).jump('repeat',1)
 s.msg(0).emit(78,1183).emit(79).emit(104).msg(1).emit(125,HM_CUT,1,0x800C).compare(0x800C,0).jump('full',1)
 s.emit(30,GIVEN).emit(78,1185).msg(2).emit(79);end(s)
 s.label('repeat').emit(104).msg(3);end(s)
 s.label('full').msg(4);return end(s).finish()
def patch(rom):
 audit=json.loads(Path('yellow-heartgold/build/0030-captain-flag-audit-v1/audit.json').read_text())
 assert not audit['raw_script_members'] and not audit['actor_flags'] and not audit['project_uses'] and audit['below_daily_base']
 assert len(audit['source_refs'])==1 and '#define FLAG_UNK_A7F' in audit['source_refs'][0]['text']
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+255*24
 sp,tp,ep='a/0/1/2','a/0/2/7','a/0/3/2';scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in (sp,tp,ep)]
 sid=len(scripts.files);scripts.files.append(script_bank([captain()]));tid=len(texts.files);texts.files.append(encode_text(MESSAGES,PH))
 eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[eid]);assert not g[1] and len(g[2])==1
 g[1]=[actor(0,236,1,9,4,facing=0)];ne=len(events.files);events.files.append(events_encode(g))
 struct.pack_into('<H',d,rec+6,sid);struct.pack_into('<H',d,rec+10,tid);struct.pack_into('<H',d,rec+16,ne)
 for path,arc in zip((sp,tp,ep),(scripts,texts,events)):rom.files[rom.filenames.idOf(path)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'map':255,'script':sid,'text':tid,'event':ne,'gift_flag':GIVEN,'hm':HM_CUT,'flag_commits_only_after_native_add_success':True,'full_bag_retry':True,'rub_animation_and_music_pending':True,'campaign_connection_pending':True,'native_gift_tests_pending':True}
