"""Return superseded small-gate saves to the native HeartGold room."""
import struct
import ndspy.narc
from opening import Script, script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE

def patch_small_room_save_return(rom):
    main=rom.loadArm9(); d=main.sections[0].data=bytearray(main.sections[0].data); rec=TABLE+391*24
    assert d[rec+20]&1
    fid=rom.filenames.idOf('a/0/1/2'); arc=ndspy.narc.NARC(rom.files[fid]); sid,iid=struct.unpack_from('<2H',d,rec+6)
    assert arc.files[iid]==bytes(4)
    bank=split_bank(arc.files[sid]); assert len(bank)==2
    # Immediate resume only schedules a scene; native guard position is 1,8.
    s=Script().emit(106,0,0x4000,0x4001).compare(0x4000,1).jump('valid',5).compare(0x4001,3).jump('valid',5).emit(41,0x4000,1).emit(2)
    s.label('valid').emit(41,0x4000,0).emit(41,0x4001,0).emit(2)
    resume=s.finish()
    s=Script().emit(96).emit(41,0x4000,0).emit(41,0x4001,0).emit(105,0x8004,0x8005).compare(0x8005,3).jump('south',4)
    for label,z,facing in (('north',6,1),('south',9,0)):
        s.label(label).emit(174,6,6,0,0).emit(175).emit(176,391,0,5,z,facing).emit(174,6,6,1,0).emit(175).emit(97).emit(2)
    ns=len(arc.files); arc.files.append(script_bank(bank+[resume,s.finish()])); ni=len(arc.files)
    arc.files.append(struct.pack('<BHHBI',3,3,0,1,1)+bytes(1)+struct.pack('<3H',0x4000,1,4)+bytes(2))
    struct.pack_into('<2H',d,rec+6,ns,ni); rom.arm9=main.save(compress=True); rom.files[fid]=arc.save()
    return dict(map=391,north=[5,6],south=[5,9],new_story_flags=False)
