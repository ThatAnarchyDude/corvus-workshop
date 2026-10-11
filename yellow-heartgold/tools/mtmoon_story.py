"""Yellow's fossil battle and exclusive choice on HeartGold's cave geometry.

Append new archives; preserve the original and foundation banks. The exit
check is a story gate, not a terrain obstacle. No Johto map or save layout edit.
Jessie/James and final release art remain separate unfinished work.
"""
import json
import struct
import ndspy.narc
from build_rom import PROJECT
from mtmoon import DATA as CAVE
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, end
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from forest_progression import expanded_common
from viridian_tutorial import TABLE

DATA = json.loads((PROJECT/'data/mtmoon-story.json').read_text())
MAP = 107
STAGE = 0x4140  # 0: battle pending; 1: choose fossil; 2: fossil chosen; 3: Rockets beaten.
CHOICE = 0x4141  # 1: Dome; 2: Helix. These saved vars are unused by native HG scripts.
BOSS = DATA['fossil_boss']['actor']
FOSSILS = DATA['fossils']


def battle_script(trainer, msg):
    s = Script().emit(96).compare(STAGE,0).jump('repeat',5)
    s.emit(105,0x4000,0x4001)
    # Automatic approach only occurs at the four tiles of the entry corridor.
    # Manual interaction faces the player without relocating either character.
    s.compare(0x4001,20).jump('manual',5)
    for x in range(10,14):s.compare(0x4000,x).jump(f'approach{x}',1)
    s.jump('manual')
    for x in range(10,14):
        s.label(f'approach{x}').movement(BOSS,f'walk{x}').emit(95).jump('fight')
    s.label('manual').emit(104)
    s.label('fight').msg(msg).emit(213,trainer,0)
    s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5)
    s.emit(36,trainer).emit(41,STAGE,1).msg(msg+1)
    # Return visibly to his fossil-watching position after an automatic approach.
    s.emit(105,0x4000,0x4001).compare(0x4001,20).jump('shared',5)
    for x in range(10,14):s.compare(0x4000,x).jump(f'return{x}',1)
    s.jump('shared')
    for x in range(10,14):
        s.label(f'return{x}').movement(BOSS,f'back{x}').emit(95).jump('shared')
    s.label('shared').msg(msg+2)
    end(s)
    s.label('repeat').compare(STAGE,1).jump('research',5).msg(msg+2)
    end(s)
    s.label('research').msg(msg+3)
    end(s)
    s.label('lost').emit(219)
    end(s)
    for x in range(10,14):
        s.moves(f'walk{x}',[(14,15-x),(3,1)])
        s.moves(f'back{x}',[(15,15-x),(2,1)])
    return s.finish()


def fossil_script(fossil, msg):
    other = next(f for f in FOSSILS if f != fossil)
    s = Script().emit(96).compare(STAGE,0).jump('unbeaten',1)
    s.compare(STAGE,1).jump('done',5)
    s.msg(msg).emit(63,0x800C).compare(0x800C,0).jump('done',5)
    s.emit(125,fossil['item'],1,0x800C).compare(0x800C,0).jump('full',1)
    # No irreversible state or disappearance until the native bag add succeeds.
    s.emit(41,CHOICE,fossil['choice']).emit(41,STAGE,2)
    s.emit(30,fossil['hide_flag']).emit(101,fossil['actor'])
    s.emit(78,1185).msg(msg+1).emit(79)
    s.emit(105,0x4000,0x4001).compare(0x4001,21).jump('collect',5)
    s.compare(0x4000,fossil['x']).jump('collect',5)
    s.movement(255,'step_back').emit(95)
    s.label('collect').movement(BOSS,'take_other').emit(95).msg(msg+2)
    s.emit(30,other['hide_flag']).emit(101,other['actor'])
    s.movement(BOSS,'back').emit(95)
    end(s)
    s.label('full').msg(msg+3)
    end(s)
    s.label('unbeaten').msg(msg+4)
    s.label('done');end(s)
    s.moves('step_back',[(13,1)])
    s.moves('take_other',[(13,1),(15,other['x']-16),(0,1)])
    s.moves('back',[(14,other['x']-16),(12,1),(2,1)])
    return s.finish()


def exit_script(msg):
    s = Script().emit(96).msg(msg).emit(105,0x4000,0x4001)
    s.compare(0x4001,23).jump('two',1)
    s.movement(255,'one').emit(95)
    end(s)
    s.label('two').movement(255,'two_steps').emit(95)
    end(s)
    return s.moves('one',[(12,1)]).moves('two_steps',[(12,2)]).finish()


def patch(rom):
    main = rom.loadArm9(); d = main.sections[0].data = bytearray(main.sections[0].data)
    paths = ['a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1']
    arcs = {p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,trainers,parties,trtable,offsets = arcs.values()
    trainer = len(trainers.files)
    boss = DATA['fossil_boss']
    row = bytearray(next(r for r in trainers.files if r[1] == boss['trainer_class']))
    row[0],row[3],row[16] = 1,3,0;row[4:12] = bytes(8);struct.pack_into('<I',row,12,1)
    trainers.files.append(row)
    parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in boss['team']))
    key,names = decode_messages(texts.files[729]);names.append([65535]);texts.files[729] = encode_messages(key,names)
    key,battletext = decode_messages(texts.files[728]);table = bytearray(trtable.files[0]);ofs = bytearray(offsets.files[0])
    while len(ofs)<2*(trainer+1):ofs.extend(struct.pack('<H',len(table)))
    struct.pack_into('<H',ofs,trainer*2,len(table))
    keys = ['MtMoonB2FSuperNerdTheyreBothMineText','MtMoonB2FSuperNerdOkIllShareText','MtMoonB2FSuperNerdTheresAPokemonLabText']
    for kind,k in enumerate(keys):
        table.extend(struct.pack('<2H',trainer,kind))
        battletext.extend(decode_messages(encode_text([CAVE['messages'][k]],PH))[1])
    texts.files[728] = encode_messages(key,battletext);trtable.files[0],offsets.files[0] = bytes(table),bytes(ofs)
    # Native trainer text dispatch must also recognize this new battle record.
    for trigger in (3000,5000):
        matches = [at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==trigger and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)]
        assert len(matches)==1
        at = matches[0];old_common = struct.unpack_from('<H',d,at+2)[0]
        if trigger == 3000:
            common = len(scripts.files);scripts.files.append(expanded_common(scripts.files[old_common],trainer))
        struct.pack_into('<H',d,at+2,common)
    rec = TABLE+MAP*24
    old_sid,old_iid,old_tid = struct.unpack_from('<3H',d,rec+6);old_eid = struct.unpack_from('<H',d,rec+16)[0]
    bank = split_bank(scripts.files[old_sid]);key,lines = decode_messages(texts.files[old_tid]);groups = events_decode(events.files[old_eid])
    new_lines = [CAVE['messages'][keys[0]],CAVE['messages'][keys[1]],
                 CAVE['messages']['MtMoonB2fSuperNerdEachTakeOneText'],CAVE['messages'][keys[2]]]
    boss_msg = len(lines);boss_script = len(bank)+1;bank.append(battle_script(trainer,boss_msg))
    groups[1].append(actor(BOSS,boss['sprite'],boss_script,boss['x'],boss['z'],0,2))
    for f in FOSSILS:
        msg = len(lines)+len(new_lines)
        new_lines.extend([CAVE['messages'][f"MtMoonB2F{f['name'].split()[0].title()}FossilYouWantText"],
                          '{PLAYER} got the '+f['name']+'!',CAVE['messages']['MtMoonB2FSuperNerdThenThisIsMineText'],
                          CAVE['messages']['MtMoonB2FYouHaveNoRoomText'],CAVE['messages'][keys[0]]])
        idx = len(bank)+1;bank.append(fossil_script(f,msg))
        groups[1].append(actor(f['actor'],87,idx,f['x'],f['z'],f['hide_flag'],0))
    exit_msg = len(lines)+len(new_lines)
    new_lines.append("We'll each take one! No being greedy! Choose a fossil before you leave.")
    exit_entry = len(bank)+1;bank.append(exit_script(exit_msg))
    lines.extend(decode_messages(encode_text(new_lines,PH))[1])
    # Story triggers do not add invisible collision or edit native terrain.
    groups[3].append(struct.pack('<Hhh5H',boss_script,10,20,4,1,0,0,STAGE))
    for value in (0,1):
        groups[3].append(struct.pack('<Hhh5H',exit_entry,20,22,5,2,0,value,STAGE))
    sid = len(scripts.files);scripts.files.append(script_bank(bank))
    tid = len(texts.files);texts.files.append(encode_messages(key,lines))
    eid = len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<H',d,rec+6,sid);struct.pack_into('<H',d,rec+10,tid);struct.pack_into('<H',d,rec+16,eid)
    # The inherited HG header uses a building backdrop. Both cave maps need
    # the native cave battle scenery; all adjacent map-header bits stay intact.
    for cave_map in (107,448):
        at=TABLE+cave_map*24+20
        word=struct.unpack_from('<I',d,at)[0]
        struct.pack_into('<I',d,at,(word & ~(31<<20)) | (9<<20))
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)] = arc.save()
    rom.arm9 = main.save(compress=True)
    return dict(map=MAP,trainer=trainer,team=boss['team'],stage_var=hex(STAGE),choice_var=hex(CHOICE),
                script=sid,text=tid,event=eid,boss_entry=boss_script,exit_entry=exit_entry,fossils=FOSSILS,
                original=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid),
                fossil_graphics='native item sprites; final fossil props pending',
                cave_battle_backgrounds=[107,448],
                rocket_scene_pending=True)
