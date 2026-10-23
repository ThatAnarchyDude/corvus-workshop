"""Prototype 008: retire the escort cashier after parcel collection and exit."""
import json
import struct
import subprocess
import ndspy.narc
import ndspy.rom
from build_rom import BASE, EXPECTED, PROJECT, sha
from opening import Script, events_decode, events_encode, script_bank, talk, encode_text
from parcel_quest import CLERK_STATE, GUIDE_HIDE, dex_gate, append_bank, split_bank, PH, PARCEL_STATE, clerk_talk
from prototype import decode_messages, encode_messages

INPUT_SHA='28803b52062e6bc23c777d14092678255eb4412e46b1d87984d5eaef6609bcbf'
TABLE=0xF6BE0


def mart_init():
    # Preserve the guide while the parcel gift is pending (including full-bag
    # retries). Once collected, a subsequent map load leaves just the two shop
    # clerks. Do not remove the guide in the middle of its closing dialogue.
    s=Script().compare(CLERK_STATE,1).jump('visible',1)
    s.emit(30,GUIDE_HIDE).jump('done')
    s.label('visible').emit(31,GUIDE_HIDE).label('done')
    s.data.extend(dex_gate())
    return s.finish()


def upper_clerk():
    # Native marts suppress Poké Balls until HG's catching tutorial flag is set.
    # Our Yellow opening replaces that tutorial; enable sales after the parcel.
    s=Script().compare(PARCEL_STATE,2).jump('talk',5).emit(30,0x9A)
    s.label('talk');s.data.extend(clerk_talk())
    return s.finish()


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-007.nds'
    assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));previous=ndspy.rom.NintendoDSRom.fromFile(str(source))
    main=rom.loadArm9();data=bytearray(main.sections[0].data);rec=TABLE+500*24
    sid,iid,tid=struct.unpack_from('<3H',data,rec+6)
    file=rom.filenames.idOf('a/0/1/2');scripts=ndspy.narc.NARC(rom.files[file]);old=list(scripts.files)
    text_file=rom.filenames.idOf('a/0/2/7');texts=ndspy.narc.NARC(rom.files[text_file]);old_texts=list(texts.files)
    key,messages=decode_messages(texts.files[tid]);bottom_message=len(messages)
    messages.extend(decode_messages(encode_text(['Welcome! My colleague can help you with purchases.'],PH))[1])
    new_tid=len(texts.files);texts.files.append(encode_messages(key,messages))
    assert texts.files[:len(old_texts)]==old_texts
    rom.files[text_file]=texts.save();struct.pack_into('<H',data,rec+10,new_tid)
    entries=split_bank(scripts.files[sid]);entries[0]=talk(bottom_message);entries[1]=upper_clerk()
    bank,entry=append_bank(script_bank(entries),[mart_init()]);new_sid=len(scripts.files);scripts.files.append(bank)
    new_iid=len(scripts.files)
    # Only type 2 (map entry). A normal save made during the escort must retain
    # its actors on type 3 reload so the active scene can finish safely.
    scripts.files.append(struct.pack('<BHHBHH',2,entry+1,0,3,entry,0)+b'\0\0')
    struct.pack_into('<2H',data,rec+6,new_sid,new_iid)
    assert scripts.files[:len(old)]==old
    rom.files[file]=scripts.save()
    # Auto-read signs are checked before door transitions when walking north.
    # The added Center label occupied the approach tile, causing a read loop.
    event_file=rom.filenames.idOf('a/0/3/2')
    events=ndspy.narc.NARC(rom.files[event_file]);old_events=list(events.files)
    city=TABLE+50*24;eid=struct.unpack_from('<H',data,city+16)[0]
    groups=events_decode(events.files[eid]);labels=[]
    for row in groups[0]:
        script,kind,x,z,y,direction=struct.unpack('<HHiiiH2x',row)
        if script==6 and (x,z)==(1032,263):continue
        if script==5 and (x,z)==(1042,254):
            row=struct.pack('<HHiiiH2x',script,kind,1038,254,y,direction)
        labels.append(row)
    groups[0]=labels;new_event=len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<H',data,city+16,new_event)
    assert events.files[:len(old_events)]==old_events
    rom.files[event_file]=events.save();main.sections[0].data=data;rom.arm9=main.save(compress=True)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nViridian cleanup prototype 008\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    output=rom.save();target=PROJECT/'build/yellow-heartgold-prototype-008.nds';target.write_bytes(output)
    assert [i for i,(a,b) in enumerate(zip(previous.files,rom.files)) if a!=b]==sorted([file,event_file,text_file])
    assert rom.arm7==previous.arm7 and rom.arm9OverlayTable==previous.arm9OverlayTable
    for mapid in [501]:
        assert data[TABLE+mapid*24:TABLE+(mapid+1)*24]==previous.loadArm9().sections[0].data[TABLE+mapid*24:TABLE+(mapid+1)*24]
    patch=target.with_suffix('.xdelta');decoded=PROJECT/'build/mart-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(output)
    report=dict(version='008',input_sha256=INPUT_SHA,output_sha256=sha(output),patch_sha256=sha(patch.read_bytes()),original_script_members_preserved=True,center_header_unchanged=True,doorway_signs_cleared=True,city_event=new_event,mart_script=new_sid,mart_init=new_iid)
    (PROJECT/'build/mart-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
