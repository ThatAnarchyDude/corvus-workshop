"""Route the new port copy back to the untouched native port after the Hall of Fame."""
import struct
import ndspy.narc
from opening import Script
from parcel_quest import append_bank
from viridian_tutorial import TABLE
GAME_CLEAR=0x964
STATE=0x4000  # Native map-temporary variable, cleared on map transitions.

def dispatch():
    s=Script().emit(41,STATE,1).emit(32,GAME_CLEAR).jump('native',1).emit(2)
    s.label('native').emit(96).emit(174,6,6,0,0).emit(175).emit(176,386,0,7,3,0).emit(174,6,6,1,0).emit(175).emit(97).emit(2)
    return s.finish()

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);at=TABLE+263*24
    fid=rom.filenames.idOf('a/0/1/2');scripts=ndspy.narc.NARC(rom.files[fid]);old=struct.unpack_from('<H',d,at+6)[0]
    reset=Script().emit(41,STATE,0).emit(2).finish();bank,count=append_bank(scripts.files[old],[reset,dispatch()]);assert count==2
    ns=len(scripts.files);scripts.files.append(bank);ni=len(scripts.files)
    scripts.files.append(struct.pack('<BHHBI',2,count+1,0,1,1)+bytes(1)+struct.pack('<3H',STATE,0,count+2)+bytes(2))
    struct.pack_into('<2H',d,at+6,ns,ni);rom.files[fid]=scripts.save();rom.arm9=main.save(compress=True)
    return dict(map=263,script=ns,init=ni,native_port=386,native_hall_of_fame_flag=GAME_CLEAR,
        temp_variable=STATE,no_persistent_flag_changes=True,no_johto_resource_changes=True,native_tests_pending=True)
