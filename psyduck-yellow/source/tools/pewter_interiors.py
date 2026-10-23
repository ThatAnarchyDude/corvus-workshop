"""Yellow's Pewter houses, shop and clinic within preserved HG interiors."""
import json
import struct

import ndspy.narc

from build_rom import PROJECT
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, talk, end
from parcel_quest import PH, split_bank
from viridian_tutorial import TABLE

DATA=json.loads((PROJECT/'data/pewter-interiors.json').read_text())['messages']


def cry_dialogue(index,species):
    s=Script().emit(73,1500).emit(96).emit(104).emit(76,species,0).msg(index).emit(77)
    return end(s).finish()


def shop():
    # Standard HG stock and badge unlocks; no fixed Yellow inventory override.
    s=Script().emit(73,1500).emit(96).emit(104).emit(20,2011).emit(50)
    return end(s.emit(41,0x8004,1).emit(20,2048)).finish()


def jigglypuff():
    s=Script().emit(73,1500).emit(96).emit(104).emit(76,39,0).msg(2).emit(77)
    # Use HG's native Poké Lullaby; retain its radio track for other services.
    s.emit(81,0).emit(80,1099)
    for i in range(16):
        s.movement(5,f'turn{i}').emit(95).emit(3,24,0x800C)
    s.emit(81,0).emit(82)
    end(s)
    for i in range(16):s.moves(f'turn{i}',[((1,2,0,3)[i%4],1)])
    return s.finish()


def patch(rom):
    main=rom.loadArm9()
    d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events=arcs.values()
    report={'maps':[]}
    for mapid in (472,474,475,477):
        rec=TABLE+mapid*24
        old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6)
        old_eid=struct.unpack_from('<H',d,rec+16)[0]
        groups=events_decode(events.files[old_eid])
        native=split_bank(scripts.files[old_sid])
        if mapid==472:
            lines=[DATA['_PewterNidoranHouseMiddleAgedManText'],DATA['_PewterNidoranHouseNidoranText'],DATA['_PewterNidoranHouseLittleBoyText']]
            bank=[talk(0),cry_dialogue(1,32),talk(2)]
            groups[1].append(actor(2,315,3,6,5,0,2))
        elif mapid==474:
            lines=[DATA['_PewterMartYoungsterText'],DATA['_PewterMartSuperNerdText'],
                   'Please speak to the clerk at the upper counter to buy or sell items.']
            bank=[shop(),talk(2),talk(0),talk(1)]
            groups[1]=[row for row in groups[1] if struct.unpack_from('<H',row)[0]<4]
            for row in groups[1]:
                obj=struct.unpack_from('<H',row)[0]
                if obj in (2,3):
                    b=bytearray(row);struct.pack_into('<H',b,2,315 if obj==2 else 317)
                    groups[1][groups[1].index(row)]=b
        elif mapid==475:
            lines=[DATA['_PewterPokecenterGentlemanText'],DATA['_PewterPokecenterText3'],DATA['_PewterPokecenterJigglypuffText']]
            bank=[native[0],talk(0),talk(1),jigglypuff()]
            groups[1]=[row for row in groups[1] if struct.unpack_from('<H',row)[0]!=4]
            for i,row in enumerate(groups[1]):
                obj=struct.unpack_from('<H',row)[0]
                if obj==6:
                    b=bytearray(row);struct.pack_into('<H',b,2,341);groups[1][i]=b
            # Native nurse, link receptionists, PC background and both warps
            # remain; Haunter/Xatu trade is archived with the former bank.
        else:
            lines=[DATA['_PewterSpeechHouseGamblerText'],DATA['_PewterSpeechHouseYoungsterText']]
            bank=[talk(0),talk(1)]
            groups[1].append(actor(1,315,2,6,5,0,3))
        sid=len(scripts.files);scripts.files.append(script_bank(bank))
        tid=len(texts.files);texts.files.append(encode_text(lines,PH))
        eid=len(events.files);events.files.append(events_encode(groups))
        # The clinic's shared-service init is still needed for communications
        # and ordinary recovery. The Mart's standard entry init is retained.
        struct.pack_into('<3H',d,rec+6,sid,old_iid,tid)
        struct.pack_into('<H',d,rec+16,eid)
        report['maps'].append(dict(map=mapid,script=sid,text=tid,event=eid,
                                   original_script=old_sid,original_event=old_eid))
    # Prototype 015 sent a selection SE to PlayBGM. Correct the active gym
    # without rewriting its archived script or the immutable published ROM.
    rec=TABLE+473*24
    old_sid=struct.unpack_from('<H',d,rec+6)[0]
    bank=split_bank(scripts.files[old_sid])
    assert bank[0][:4]==struct.pack('<2H',80,1500)
    bank[0]=struct.pack('<H',73)+bank[0][2:]
    sid=len(scripts.files);scripts.files.append(script_bank(bank))
    struct.pack_into('<H',d,rec+6,sid)
    report['brock_select_sound']={'original_script':old_sid,'script':sid,'opcode':73,'sound':1500}
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return report
