"""Yellow's first gym in the existing HeartGold gym, preserving archived events."""
import json
import struct

import ndspy.narc

from build_rom import PROJECT
from forest_progression import expanded_common
from opening import Script, events_decode, events_encode, script_bank, encode_text, talk, end
from parcel_quest import PH
from progression_cleanup import R22_DONE, R22_HIDE
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE
from yellow_tms import BIDE_ITEM

GYM_MAP = 473
BOULDER = 8
TM_GIVEN = 0xB22
DATA = json.loads((PROJECT/'data/pewter-gym.json').read_text())


def brock_script(trainer, junior):
    s = Script().emit(80,1500).emit(96).emit(104)
    s.emit(294,BOULDER,0x800C).compare(0x800C,1).jump('after',1)
    s.msg(0).emit(213,trainer,0)
    s.data.extend(bytes(2))
    s.emit(220,0x800C).compare(0x800C,1).jump('lost',5)
    s.emit(295,BOULDER).emit(39,0x4135,1).emit(36,trainer).emit(36,junior)
    # Yellow retires the optional early Route22 encounter after Brock.
    s.emit(30,R22_DONE).emit(30,R22_HIDE)
    s.msg(1).emit(78,1189).emit(79).msg(2)
    s.label('after').emit(32,TM_GIVEN).jump('advice',1)
    s.msg(3).emit(125,BIDE_ITEM,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,TM_GIVEN).emit(78,1185).msg(4).emit(79).msg(5)
    end(s)
    s.label('full').msg(6)
    end(s)
    s.label('advice').msg(7)
    end(s)
    s.label('lost').emit(219)
    return end(s).finish()


def guide_script():
    s = Script().emit(96).emit(104).emit(294,BOULDER,0x800C)
    s.compare(0x800C,1).jump('after',1).msg(8).emit(63,0x800C)
    s.compare(0x800C,0).jump('yes',1).msg(11).jump('help')
    s.label('yes').msg(9)
    s.label('help').msg(10)
    end(s)
    s.label('after').msg(12)
    return end(s).finish()


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    paths = ['a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1']
    arcs = {p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,trainers,parties,trtable,offsets = arcs.values()
    key,names = decode_messages(texts.files[729])
    msgkey,trmessages = decode_messages(texts.files[728])
    table = bytearray(trtable.files[0])
    ofs = bytearray(offsets.files[0])
    added = []
    for entry in DATA['trainers']:
        trainer = len(trainers.files)
        row = bytearray(trainers.files[entry['original_hg']])
        row[0] = 1  # Explicit Yellow moves, without held items.
        row[3] = len(entry['team'])
        row[4:12] = bytes(8)
        struct.pack_into('<I',row,12,1)
        row[16] = 0
        trainers.files.append(row)
        parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in entry['team']))
        names.append(names[entry['original_hg']])
        while len(ofs)<2*(trainer+1):
            ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,trainer*2,len(table))
        for kind,suffix in enumerate(('BattleText','EndBattleText','AfterBattleText')):
            table.extend(struct.pack('<2H',trainer,kind))
            label = 'PewterGymCooltrainerM'+suffix
            # Brock uses his local story dialogue; three valid entries still
            # protect incidental native trainer-text lookups for his record.
            text = DATA['messages'][label] if entry['role']=='junior' else DATA['messages']['PewterGymBrockPostBattleAdviceText']
            trmessages.extend(decode_messages(encode_text([text],PH))[1])
        added.append(dict(id=trainer,**entry))
    texts.files[729] = encode_messages(key,names)
    texts.files[728] = encode_messages(msgkey,trmessages)
    trtable.files[0],offsets.files[0] = bytes(table),bytes(ofs)
    junior,brock = [x['id'] for x in added]

    needle = struct.pack('<3H',3000,1030,40)
    assert d.count(needle)==1
    common = len(scripts.files)
    scripts.files.append(expanded_common(scripts.files[1030],brock))
    for trigger in (3000,5000):
        needle = struct.pack('<3H',trigger,1030,40)
        assert d.count(needle)==1
        struct.pack_into('<H',d,d.index(needle)+2,common)

    rec = TABLE+GYM_MAP*24
    old_event = struct.unpack_from('<H',d,rec+16)[0]
    groups = events_decode(events.files[old_event])
    actors = []
    for row in groups[1]:
        obj = struct.unpack_from('<H',row)[0]
        if obj==3:continue  # Yellow has one junior trainer, not HG's extra Hiker.
        b = bytearray(row)
        if obj==0:struct.pack_into('<H',b,10,2)
        elif obj==1:struct.pack_into('<2H',b,8,0,1)
        elif obj==2:struct.pack_into('<H',b,10,3000+junior-1)
        actors.append(b)
    groups[1] = actors
    for i,row in enumerate(groups[0]):
        b = bytearray(row)
        struct.pack_into('<H',b,0,3)
        groups[0][i] = b
    labels = ['PewterGymBrockPreBattleText','PewterGymBrockReceivedBoulderBadgeText',
              'PewterGymBrockBoulderBadgeInfoText','PewterGymBrockWaitTakeThisText',
              'PewterGymReceivedTM34Text','TM34ExplanationText','PewterGymTM34NoRoomText',
              'PewterGymBrockPostBattleAdviceText','PewterGymGuidePreAdviceText',
              'PewterGymGuideBeginAdviceText','PewterGymGuideAdviceText',
              'PewterGymGuideFreeServiceText','PewterGymGuidePostBattleText']
    lines = [DATA['messages'][x] for x in labels]+['PEWTER CITY POKEMON GYM\rLEADER: BROCK\rWinning trainers: {RIVAL}']
    sid = len(scripts.files)
    scripts.files.append(script_bank([brock_script(brock,junior),guide_script(),talk(13)]))
    iid = len(scripts.files)
    scripts.files.append(bytes(4))
    tid = len(texts.files)
    texts.files.append(encode_text(lines,PH))
    eid = len(events.files)
    events.files.append(events_encode(groups))
    struct.pack_into('<3H',d,rec+6,sid,iid,tid)
    struct.pack_into('<H',d,rec+16,eid)
    for path,archive in arcs.items():
        rom.files[rom.filenames.idOf(path)] = archive.save()
    rom.arm9 = main.save(compress=True)
    return dict(map=GYM_MAP,trainers=added,script=sid,text=tid,event=eid,
                original_event=old_event,common_bank=common,tm_flag=TM_GIVEN)
