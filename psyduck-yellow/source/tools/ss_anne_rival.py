"""Yellow's S.S. Anne rival battle on the copied Kanto second-floor landing."""
import struct
import ndspy.narc
from opening import Script,end,actor,events_decode,events_encode,encode_text
from parcel_quest import PH,append_bank
from prototype import decode_messages,encode_messages
from progression_cleanup import selected_battle
from escort import music
from viridian_tutorial import TABLE
from ss_anne_departure import CUT_GIVEN
DONE=0xA7B
HIDE=0xA79
BLUE=0
MESSAGES=[
 '{RIVAL}: Bonjour! {PLAYER}!\rImagine seeing you here!\r{PLAYER}, were you really invited?\rSo how is your POKEDEX coming?\rI already caught 40 kinds, pal!\rDifferent kinds are everywhere!\rCrawl around in grassy areas!',
 "Humph!\rAt least you are raising your Pokemon!",
 '{PLAYER}! What are you, seasick?\rYou should shape up, pal!',
 '{RIVAL}: I heard there was a CUT master on board.\rBut he was just a seasick old man!\rBut CUT itself is really useful!\rYou should go see him! Smell ya!']

def scene(trainers):
 s=Script().emit(32,DONE).jump('done',1).emit(32,CUT_GIVEN).jump('done',1).emit(96).emit(31,HIDE).emit(100,BLUE)
 music(s,1088);s.movement(255,'face').emit(95).msg(0)
 # Owner-approved optional battle: native BATTLE_TYPE_11 restores the field
 # and heals the entire party after loss, preserving the actual result.
 selected_battle(s,trainers,1,'result');s.label('result').emit(220,0x800C).compare(0x800C,1).jump('lost',5)
 s.msg(1).jump('outro')
 s.label('lost').msg(2)
 s.label('outro').msg(3);music(s,1089);s.movement(BLUE,'leave').emit(95).emit(30,DONE).emit(30,HIDE).emit(101,BLUE).emit(82);end(s)
 s.label('done').emit(2)
 s.moves('face',[(2,1)]).moves('leave',[(14,6),(12,6)])
 return s.finish()

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);at=TABLE+254*24
 paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1')
 scripts,texts,events,trainers,parties,trtable,offsets=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 for flag in (DONE,HIDE):
  assert not any(struct.pack('<H',flag) in raw for raw in scripts.files)
  assert not any(struct.pack('<H',flag) in a for raw in events.files for a in events_decode(raw)[1])
 assert len(trainers.files)==809 and len(parties.files)==809
 namekey,names=decode_messages(texts.files[729]);assert len(names)==809
 textkey,lines=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0]);ids={};added=[]
 for species in (54,133):
  for gender,value in (('male',1),('female',2)):
   tid=len(trainers.files);row=bytearray(trainers.files[742]);assert row[1]==110
   row[0]=1;row[3]=4;row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0
   team=[(21,19,[64,45,43,31],0),(19,16,[33,39,98,158],0),(27,18,[10,28,163,0],0),(species,20,[10,39,55,50] if species==54 else [33,39,28,45],value)]
   trainers.files.append(bytes(row));parties.files.append(b''.join(struct.pack('<BB3H4H',0,g,level,mon,0,*moves) for mon,level,moves,g in team));names.append(names[742])
   while len(ofs)<2*(tid+1):ofs.extend(struct.pack('<H',len(table)))
   assert len(table)<65536;struct.pack_into('<H',ofs,tid*2,len(table))
   for kind,index in enumerate((0,1,3)):table.extend(struct.pack('<2H',tid,kind));lines.extend(decode_messages(encode_text([MESSAGES[index]],PH))[1])
   ids[f'{species}_{gender}']=tid;added.append(dict(id=tid,species=species,gender=gender,team=team))
 ids[54]=ids['54_male'];ids[133]=ids['133_female']
 texts.files[729]=encode_messages(namekey,names);texts.files[728]=encode_messages(textkey,lines);trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
 oldscript=struct.unpack_from('<H',d,at+6)[0];oldevent=struct.unpack_from('<H',d,at+16)[0]
 bank,count=append_bank(scripts.files[oldscript],[scene(ids),Script().emit(30,HIDE).emit(2).finish()]);sid=len(scripts.files);scripts.files.append(bank);ini=len(scripts.files);scripts.files.append(struct.pack('<BHHB',2,count+2,0,0));tid=len(texts.files);texts.files.append(encode_text(MESSAGES,PH))
 groups=events_decode(events.files[oldevent]);assert not groups[0] and not groups[1] and not groups[3]
 groups[1]=[actor(BLUE,375,count+1,48,16,HIDE,3)];groups[3]=[struct.pack('<Hhh5H',count+1,49,16,1,1,0,0,0)];eid=len(events.files);events.files.append(events_encode(groups))
 struct.pack_into('<3H',d,at+6,sid,ini,tid);struct.pack_into('<H',d,at+16,eid)
 for path,archive in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=archive.save()
 rom.arm9=main.save(compress=True)
 return dict(map=254,scene_script=count+1,trainers=added,done_flag=DONE,hide_flag=HIDE,trigger=[49,16],actor=[48,16],native_tests_pending=True,legacy_cut_saves_skip_encounter=True,starter_properties_shared=True,optional_battle=True,native_loss_party_heal=True)
