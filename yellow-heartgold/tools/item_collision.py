"""Ground item balls cannot be skipped by the native pass-through object flag."""
import struct
from prototype import thumb_bl
from starter_properties import append_code

SITE=0x02060C34
NATIVE=0x0205F220


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    assert d[SITE-0x02000000:SITE-0x02000000+4]==thumb_bl(SITE,NATIVE)
    address,_=append_code(main,f'ldr r2,[r0,#16]\ncmp r2,#87\nbeq solid\nldr r3,native\nbx r3\nsolid:\nmovs r0,#0\nbx lr\n.align 2\nnative: .word {NATIVE|1}\n')
    d[SITE-0x02000000:SITE-0x02000000+4]=thumb_bl(SITE,address)
    struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));rom.arm9=main.save(compress=True)
    return dict(collision_hook=hex(SITE),hook=hex(address),item_sprite=87,inactive_objects_and_height_checks_preserved=True,all_other_objects_use_native_flags=True)
