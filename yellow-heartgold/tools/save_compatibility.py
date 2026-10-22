"""Repair 0021 flag bounds and preserve custom flags at daily rollover.

Existing B00..B5F addresses stay stable, including native Blue seed offsets.
AA0..AFF still reset daily; the reserved B00..B5F extension does not.
New Cerulean flags move to unused A80..A8A, outside the daily range.
"""
import struct
import ndspy.narc
from opening import events_decode, events_encode
from starter_properties import append_code

NUM_FLAGS = 0xB60
RELOCATIONS = {n: n - 0xE0 for n in range(0xB60, 0xB6B)}
RECOVERED = 0xA8B

def assert_persistent(flag):
    if not 0 < flag < NUM_FLAGS:
        raise ValueError(f'Persistent flag {flag:#x} exceeds HeartGold save bounds')

def flag_or(flag, register='r5', clear=False):
    assert_persistent(flag)
    offset = 0x2E0 + flag // 8
    instruction = 'bics' if clear else 'orrs'
    return f'ldr r1, ={offset}\nldrb r0, [{register}, r1]\nmovs r2, #{1 << (flag % 8)}\n{instruction} r0, r2\nstrb r0, [{register}, r1]\n'

def var_set(var, value):
    return f'ldr r1, ={2 * (var - 0x4000)}\nmovs r0, #{value}\nstrh r0, [r5, r1]\n'

def recovery_source():
    # SaveArray_Get is called directly to avoid recursion through our hook.
    s = '''push {r4,r5,r6,r7,lr}
sub sp, #4
movs r4, r0
movs r1, #4
bl 0x020272C8
movs r5, r0
ldr r1, =0x431
ldrb r0, [r5,r1]
movs r1, #8
tst r0,r1
beq recover
b done
recover:
movs r0,r4
movs r1,#1
bl 0x020272C8
adds r0,#35
ldrb r6,[r0]
ldr r1, =0x313
ldrb r0,[r5,r1]
movs r1,#16
tst r0,r1
beq badge_evidence
'''+flag_or(0xB45)+'''
b parcel_complete
badge_evidence:
cmp r6,#0
bne parcel_complete
ldr r1, =0x2D4
ldrh r0,[r5,r1]
cmp r0,#2
beq parcel_complete
b items
parcel_complete:
'''
    for v, n in ((0x4169,1),(0x416A,2),(0x416D,2),(0x416F,2),(0x416E,2),(0x4168,1)):
        s += var_set(v,n)
    for f in (0x6A,0x6B,0xB52,0xB50,0xB53,0xB55,0xB56,0xB57,
              0xB58,0xB59,0xB5A,0xB5E,0xB5F,0xB46):
        s += flag_or(f)
    s += flag_or(0xB5C,clear=True)
    # These bytes enable acquired/National Dex; seen/caught arrays are retained.
    s += '''movs r0,r4
movs r1,#6
bl 0x020272C8
ldr r1, =0x336
adds r1,r0,r1
movs r0,#1
strb r0,[r1]
strb r0,[r1,#1]
movs r0,#1
tst r0,r6
beq items
'''
    for f in (0xB4F,0xB4C,0xB54,0xB43,0xB44):
        s += flag_or(f)
    s += flag_or(0xB4D,clear=True)
    # Existing type-3 reload services safely update already-present actors and
    # create the standing old man/granddaughter when only blockers were saved.
    s += flag_or(0xB4E,clear=True)+flag_or(0xB47,clear=True)
    s += '''items:
movs r0,r4
movs r1,#3
bl 0x020272C8
movs r7,r0
ldr r6, =480
item_loop:
ldrh r0,[r7]
ldrh r1,[r7,#2]
cmp r1,#0
beq next_item
cmp r0,#115
bne misty_item
'''+flag_or(0xB22)+'''b next_item
misty_item:
cmp r0,#119
bne bike_item
'''+flag_or(0xA89)+'''b next_item
bike_item:
ldr r1, =450
cmp r0,r1
bne next_item
'''+flag_or(0xA80)+'''next_item:
adds r7,#4
subs r6,#1
bne item_loop
ldr r1, =0x288
ldrh r0,[r5,r1]
cmp r0,#1
bne marked
'''+flag_or(0xA81)+flag_or(0xA82)+'''marked:
'''+flag_or(RECOVERED)+'''done:
movs r0,r5
add sp,#4
pop {r4,r5,r6,r7,pc}
.ltorg
'''
    return s

def patch(rom):
    main=rom.loadArm9(); d=main.sections[0].data=bytearray(main.sections[0].data)
    sf=rom.filenames.idOf('a/0/1/2'); scripts=ndspy.narc.NARC(rom.files[sf]); changes=0
    for i, raw in enumerate(scripts.files):
        b=bytes(raw)
        for old,new in RELOCATIONS.items():
            assert_persistent(new)
            for op in (30,31,32):
                needle=struct.pack('<HH',op,old); changes+=b.count(needle)
                b=b.replace(needle,struct.pack('<HH',op,new))
        scripts.files[i]=b
    ef=rom.filenames.idOf('a/0/3/2'); events=ndspy.narc.NARC(rom.files[ef]); objects=0
    for i,raw in enumerate(events.files):
        g=events_decode(raw); changed=False
        for j,row in enumerate(g[1]):
            old=struct.unpack_from('<H',row,8)[0]
            if old in RELOCATIONS:
                b=bytearray(row);struct.pack_into('<H',b,8,RELOCATIONS[old]);g[1][j]=bytes(b);changed=True;objects+=1
        if changed:events.files[i]=events_encode(g)
    rom.files[sf]=scripts.save();rom.files[ef]=events.save()
    assert d[0x40480:0x40482]==bytes.fromhex('1822')
    d[0x40480:0x40482]=bytes.fromhex('0c22')
    # Invalid persistent IDs now return NULL, never a checksum address. Valid
    # and temporary flags retain the native function and its address contract.
    assert d[0x5045C:0x50464]==bytes.fromhex('38b5051c002901d1')
    guard,code=append_code(main,'''ldr r3, =0xB60
cmp r1,r3
blo original
ldr r3, =0x4000
cmp r1,r3
bhs original
movs r0,#0
bx lr
original:
push {r3,r4,r5,lr}
movs r5,r0
cmp r1,#0
bne nonzero
movs r0,#0
pop {r3,r4,r5,pc}
nonzero:
ldr r3, =0x02050469
bx r3
.ltorg
''')
    d[0x5045C:0x50464]=bytes.fromhex('004b1847')+struct.pack('<I',guard|1)
    recovery,recovery_code=append_code(main,recovery_source())
    assert d[0x503D0:0x503D8]==bytes.fromhex('014b04211847c046')
    d[0x503D0:0x503D8]=bytes.fromhex('004b1847')+struct.pack('<I',recovery|1)
    # Continue restores a saved actor list without consulting event hide flags.
    # Repair before restoration, so stale clerks/guards do not remain on screen.
    assert d[0x5E648:0x5E650]==bytes.fromhex('f8b5061c0d1c171c')
    restore_native,_=append_code(main,'''push {r3,r4,r5,r6,r7,lr}
movs r6,r0
movs r5,r1
movs r7,r2
ldr r3, =0x0205E651
bx r3
.ltorg
''')
    restore,restore_code=append_code(main,f'''push {{r4,r5,r6,r7,lr}}
sub sp,#12
movs r4,r0
movs r5,r1
movs r6,r2
ldr r1, =0x128
ldr r0,[r4,r1]
ldr r0,[r0,#12]
bl 0x020503D0
movs r7,r0
movs r0,r5
str r0,[sp]
movs r0,r6
str r0,[sp,#4]
restore_loop:
cmp r6,#0
beq restore_done
ldrh r1,[r5,#22]
ldr r0, =0xB60
cmp r1,r0
blo supported
adds r0,#11
cmp r1,r0
bhs supported
subs r1,#224
strh r1,[r5,#22]
supported:
ldr r0, =0xB00
cmp r1,r0
blo new_range
adds r0,#96
cmp r1,r0
blo check_flag
new_range:
ldr r0, =0xA80
cmp r1,r0
blo restore_next
adds r0,#11
cmp r1,r0
bhs restore_next
check_flag:
lsrs r0,r1,#3
ldr r2, =0x2E0
adds r0,r0,r2
ldrb r0,[r7,r0]
movs r2,#7
ands r1,r2
movs r2,#1
lsls r2,r1
tst r0,r2
beq restore_next
ldr r0,[r5]
movs r1,#1
bics r0,r1
str r0,[r5]
restore_next:
adds r5,#80
subs r6,#1
b restore_loop
restore_done:
movs r0,r4
ldr r1,[sp]
ldr r2,[sp,#4]
add sp,#12
pop {{r4,r5,r6,r7}}
pop {{r3}}
mov lr,r3
ldr r3, ={restore_native | 1}
bx r3
.ltorg
''')
    d[0x5E648:0x5E650]=bytes.fromhex('004b1847')+struct.pack('<I',restore|1)
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4))
    struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
    rom.arm9=main.save(compress=True)
    return dict(relocations={hex(a):hex(b) for a,b in RELOCATIONS.items()},script_operands=changes,object_flags=objects,
                daily_reset_bytes=12,protected_flags=['0xB00','0xB5F'],bounds_hook=hex(guard),
                recovery_hook=hex(recovery),recovery_bytes=len(recovery_code),recovery_marker=hex(RECOVERED),
                actor_restore_hook=hex(restore),actor_restore_trampoline=hex(restore_native),
                actor_restore_bytes=len(restore_code))
