"""Restore the removed Vermilion Cut tree and align direct Cut with menu badges."""
import struct
import ndspy.narc
from opening import Script,events_decode,events_encode
from parcel_quest import append_bank
from viridian_tutorial import TABLE

def cut_badge_helper():
    # Preserve Hive; Cascade already unlocks menu Cut in the existing campaign.
    s=Script().emit(294,1,0x800C).compare(0x800C,0).jump('done',5)
    s.emit(294,9,0x800C).label('done').emit(27)
    return s.finish()

def patch(rom,original):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    eventpath='a/0/3/2';scriptpath='a/0/1/2'
    events=ndspy.narc.NARC(rom.files[rom.filenames.idOf(eventpath)])
    scripts=ndspy.narc.NARC(rom.files[rom.filenames.idOf(scriptpath)])
    od=original.loadArm9().sections[0].data;oe=ndspy.narc.NARC(original.files[original.filenames.idOf(eventpath)])
    rec=TABLE+54*24;oldid=struct.unpack_from('<H',d,rec+16)[0]
    groups=events_decode(events.files[oldid]);native=events_decode(oe.files[struct.unpack_from('<H',od,rec+16)[0]])
    tree=next(row for row in native[1] if struct.unpack_from('<2H',row)==(11,86))
    assert struct.unpack_from('<H',tree,10)[0]==10000 and struct.unpack_from('<2H',tree,24)==(1300,319)
    assert not any(struct.unpack_from('<H',row)[0]==11 for row in groups[1])
    groups[1].append(tree);eid=len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<H',d,rec+16,eid)
    old=scripts.files[146]
    assert old==ndspy.narc.NARC(original.files[original.filenames.idOf(scriptpath)]).files[146]
    needle=struct.pack('<3H',294,1,0x800C);assert old.count(needle)==1
    bank,count=append_bank(old,[cut_badge_helper()]);assert count==19
    at=old.index(needle)+4;target=count*4+4+struct.unpack_from('<I',bank,count*4)[0]
    bank[at:at+6]=struct.pack('<Hi',26,target-at-6)
    sid=len(scripts.files);scripts.files.append(bytes(bank))
    dispatch=struct.pack('<3H',10000,146,211)
    assert d.count(dispatch)==1
    site=d.index(dispatch);struct.pack_into('<H',d,site+2,sid)
    rom.files[rom.filenames.idOf(eventpath)]=events.save();rom.files[rom.filenames.idOf(scriptpath)]=scripts.save()
    rom.arm9=main.save(compress=True)
    return dict(map=54,tree_id=11,position=[1300,319],event=eid,original_event=oldid,
                script=sid,original_script=146,dispatch_offset=site,call_offset=at,helper_offset=target,
                accepted_cut_badges=[1,9],scope='shared Cut badge check only; original Hive alternative preserved',
                no_johto_map_event_encounter_edits=True,native_test='pending')
