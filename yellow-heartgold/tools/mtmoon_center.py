"""Yellow's Route 3 clinic NPCs and one-time Magikarp sale; native HG services."""
import json
import struct
import ndspy.narc
from build_rom import PROJECT
from opening import Script, actor, events_decode, events_encode, encode_text, talk, end
from parcel_quest import PH, split_bank, append_bank
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

MAP=511
SOLD=0xB37
DATA=json.loads((PROJECT/'data/mtmoon-story.json').read_text())['center_messages']


def salesman(msg):
    s=Script().emit(73,1500).emit(96).emit(104).emit(32,SOLD).jump('sold',1)
    s.msg(msg).emit(63,0x800C).compare(0x800C,0).jump('decline',5)
    # Native HG command 112 reads an output halfword then a 32-bit amount.
    s.emit(112,0x800C);s.data.extend(struct.pack('<I',500))
    s.compare(0x800C,0).jump('poor',1)
    s.emit(332,0x800C).compare(0x800C,6).jump('full',1)
    s.emit(137,129,5,0,0,0,0x800C).compare(0x800C,0).jump('full',1)
    # Charge and commit only after the Pokémon has been successfully received.
    s.emit(111);s.data.extend(struct.pack('<I',500))
    s.emit(30,SOLD).emit(78,1185).msg(msg+4).emit(79)
    end(s)
    s.label('decline').msg(msg+1);end(s)
    s.label('poor').msg(msg+2);end(s)
    s.label('sold').msg(msg+3);end(s)
    s.label('full').msg(msg+5)
    return end(s).finish()


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2'];arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events=arcs.values();rec=TABLE+24*MAP
    old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6);old_eid=struct.unpack_from('<H',d,rec+16)[0]
    native_nurse=split_bank(scripts.files[old_sid])[0]
    # The verified Viridian clinic bank contains the native storage/root menus
    # and the shared Player PC item-storage branch. Clone it, retaining originals.
    clinic_sid,_,clinic_tid=struct.unpack_from('<3H',d,TABLE+24*501+6)
    key,lines=decode_messages(texts.files[clinic_tid]);offset=len(lines)
    added=[DATA['MtMoonPokecenterYoungsterText'],DATA['MtMoonPokecenterGentlemanText'],
           DATA['MtMoonPokecenterMagikarpSalesmanIGotADealText'],DATA['MtMoonPokecenterMagikarpSalesmanNoText'],
           DATA['MtMoonPokecenterMagikarpSalesmanNoMoneyText'],DATA['MtMoonPokecenterMagikarpSalesmanNoRefundsText'],
           '{PLAYER} received a MAGIKARP!', 'Your party is full. Make room for MAGIKARP and come back.']
    lines.extend(decode_messages(encode_text(added,PH))[1])
    bank,entry=append_bank(scripts.files[clinic_sid],[native_nurse,talk(offset),talk(offset+1),salesman(offset+2)])
    groups=events_decode(events.files[old_eid])
    # Nurse, native link/communication staff, entry init and warps remain intact.
    rows=[]
    for row in groups[1]:
        obj=struct.unpack_from('<H',row)[0]
        if obj>3:continue
        b=bytearray(row)
        if obj==0:struct.pack_into('<H',b,10,entry+1)
        rows.append(bytes(b))
    rows.extend([actor(4,315,entry+2,5,16,0,0),actor(5,331,entry+3,12,14,0,2),actor(6,333,entry+4,3,15,0,3)])
    groups[1]=rows
    groups[0].append(struct.pack('<HHiiiH2x',11,0,11,12,0,0))
    sid=len(scripts.files);scripts.files.append(bank);tid=len(texts.files);texts.files.append(encode_messages(key,lines));eid=len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<3H',d,rec+6,sid,old_iid,tid);struct.pack_into('<H',d,rec+16,eid)
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=MAP,script=sid,text=tid,event=eid,salesman_entry=entry+4,salesman_message=offset+2,
                species=129,level=5,price=500,sold_flag=hex(SOLD),player_pc_storage=True,
                originals=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid),
                native_nurse_preserved=True,native_communications_preserved=True)
