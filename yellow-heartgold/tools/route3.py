"""Yellow Route 3 on native HeartGold geometry, cumulative from 0016."""
import json
import struct
import subprocess
import ndspy.narc
import ndspy.rom
from ndspy import _common
from build_rom import BASE, EXPECTED, PROJECT, sha
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, talk
from parcel_quest import PH, BOUNDARY, split_bank
from pewter_city import route_guide
from pewter_museum import TICKET
from forest_progression import expanded_common, SLOT_MAP
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

DATA=json.loads((PROJECT/'data/route3.json').read_text())
INPUT_SHA='05ed484e1ddff00944063733031e2e3b4921c1e9cf145d58252fbd0c7b342242'
MAP=11


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7','a/0/5/7','a/1/3/1']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,trainers,parties,wild,trtable,offsets=arcs.values()
    rec=TABLE+24*MAP;old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6)
    old_eid=struct.unpack_from('<H',d,rec+16)[0];old_wild=d[rec]
    groups=events_decode(events.files[old_eid]);original_rows={struct.unpack_from('<H',r)[0]:r for r in groups[1]}
    namekey,names=decode_messages(texts.files[729]);textkey,battle_text=decode_messages(texts.files[728])
    table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0]);added=[];rows=[]
    for entry in DATA['trainers']:
        tid=len(trainers.files);assert tid<1000
        row=bytearray(trainers.files[entry['template']]);row[0]=1;row[1]=entry['trainer_class'];row[3]=len(entry['team']);row[4:12]=bytes(8)
        struct.pack_into('<I',row,12,1);row[16]=0;trainers.files.append(row)
        parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,p['level'],p['species'],0,*p['moves']) for p in entry['team']))
        names.append([0xFFFF])  # Yellow's route trainers have no personal names.
        while len(ofs)<2*(tid+1):ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,tid*2,len(table))
        for kind,suffix in enumerate(('BattleText','EndBattleText','AfterBattleText')):
            table.extend(struct.pack('<2H',tid,kind))
            battle_text.extend(decode_messages(encode_text([DATA['messages'][entry['dialogue']+suffix]],PH))[1])
        b=bytearray(original_rows[entry['actor']]);struct.pack_into('<H',b,2,entry['sprite'])
        struct.pack_into('<3H',b,6,1,0,3000+tid-1);struct.pack_into('<hH',b,12,entry['facing'],3)
        struct.pack_into('<H',b,4,0)  # Stationary trainer with native line of sight.
        assert struct.unpack_from('<2H',b,24)==(entry['x'],entry['z'])
        rows.append(b);added.append(dict(id=tid,defeat_flag=0x550+tid,**entry))
    texts.files[729]=encode_messages(namekey,names);texts.files[728]=encode_messages(textkey,battle_text)
    trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    triggers=[]
    for trigger in (3000,5000):
        matches=[at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==trigger and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)]
        assert len(matches)==1;triggers.append(matches[0])
    old_common=struct.unpack_from('<H',d,triggers[0]+2)[0]
    assert struct.unpack_from('<H',d,triggers[1]+2)[0]==old_common
    common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[old_common],added[-1]['id']))
    for at in triggers:struct.pack_into('<H',d,at+2,common)
    rows.append(actor(5,317,1,1165,114,0,1));groups[1]=rows
    # Yellow has a route sign and no Route 3 item pickups. Inherited HG item
    # events remain in their original archive, but are not active on this map.
    groups[0]=[struct.pack('<HHiiiH2x',2,1,1168,121,0,4)];groups[3]=[]
    sid=len(scripts.files);scripts.files.append(script_bank([talk(0),talk(1)]))
    iid=len(scripts.files);scripts.files.append(bytes(4))
    textid=len(texts.files);texts.files.append(encode_text([DATA['messages']['Route3Text1'],DATA['messages']['Route3SignText']],PH))
    eid=len(events.files);events.files.append(events_encode(groups));struct.pack_into('<3H',d,rec+6,sid,iid,textid);struct.pack_into('<H',d,rec+16,eid)
    w=bytearray(wild.files[old_wild]);assert len(w)==196
    slots=[DATA['wild_slots'][i] for i in SLOT_MAP];w[0]=DATA['encounter_rate'];w[1:6]=bytes(5);w[8:20]=bytes(p['level'] for p in slots)
    species=[p['species'] for p in slots]
    for period in range(3):struct.pack_into('<12H',w,20+24*period,*species)
    for at in (0x5C,0x60,0x64,0x68,0xBC):struct.pack_into('<2H',w,at,species[0],species[1])
    wid=len(wild.files);assert wid<255;wild.files.append(w);d[rec]=wid
    # Preserve Yellow's Brock story gate. On returning from the gym with the
    # badge, city init disables the old development trigger; museum reset stays.
    city=TABLE+51*24;city_sid,city_iid,city_tid=struct.unpack_from('<3H',d,city+6)
    bank=split_bank(scripts.files[city_sid]);bank[0]=route_guide(open_after_brock=True)
    assert bank[-1][:6]==struct.pack('<3H',31,TICKET,2)
    init=Script().emit(31,TICKET).emit(294,8,0x800C).compare(0x800C,1).jump('done',5)
    init.emit(41,BOUNDARY,1).label('done').emit(2);bank[-1]=init.finish()
    new_city_sid=len(scripts.files);scripts.files.append(script_bank(bank))
    city_key,city_lines=decode_messages(texts.files[city_tid]);city_lines[2]=decode_messages(encode_text(['The road ahead leads to ROUTE 3 and MT. MOON. Good luck!'],PH))[1][0]
    new_city_tid=len(texts.files);texts.files.append(encode_messages(city_key,city_lines))
    struct.pack_into('<H',d,city+6,new_city_sid);struct.pack_into('<H',d,city+10,new_city_tid)
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=MAP,script=sid,init=iid,text=textid,event=eid,wild=wid,trainers=added,trainer_common=common,original_common=old_common,
                originals=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid,wild=old_wild),city_script=new_city_sid,city_text=new_city_tid,city_init=city_iid)


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-0016.nds'
    assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    old=ndspy.rom.NintendoDSRom.fromFile(str(source));rom=ndspy.rom.NintendoDSRom.fromFile(str(source));report=patch(rom)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nRoute 3 checkpoint 0017\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    target=PROJECT/'build/yellow-heartgold-prototype-0017.nds';target.write_bytes(rom.save())
    patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/route3-0017-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True)
    subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(target.read_bytes())
    report.update(version='0017',input_sha256=INPUT_SHA,output_sha256=sha(target.read_bytes()),patch_sha256=sha(patchfile.read_bytes()),
                  changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b])
    (PROJECT/'build/route3-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':build()
