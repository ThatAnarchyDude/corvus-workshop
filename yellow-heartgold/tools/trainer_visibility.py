"""Keep Nugget Bridge trainers visible across HG's Cerulean map boundary.

HG uses script FFFF/eventFlag=owner-map aliases to retain a single native
actor across seamless map transitions. Alias IDs may repeat local city IDs:
native script lookup deliberately excludes aliases, which are map-qualified.
"""
import struct
import ndspy.narc
from opening import events_decode, events_encode, script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE
from starter_properties import append_code, CMD_TABLE
from prototype import thumb_bl

MARKER = 0x4D502552
CITY, ROUTE = 52, 28


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    ep, sp = 'a/0/3/2', 'a/0/1/2'
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf(ep)])
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf(sp)])
    city, route = TABLE + CITY * 24, TABLE + ROUTE * 24
    ceid = struct.unpack_from('<H', d, city + 16)[0]
    reid = struct.unpack_from('<H', d, route + 16)[0]
    cg, rg = events_decode(events.files[ceid]), events_decode(events.files[reid])
    aliases = []
    for obj in range(3):
        row = bytearray(next(a for a in rg[1] if struct.unpack_from('<H', a)[0] == obj))
        assert struct.unpack_from('<H', row, 6)[0] == 1
        assert struct.unpack_from('<i', row, 28)[0] == 3 * 65536
        struct.pack_into('<2H', row, 8, ROUTE, 0xFFFF)
        aliases.append(bytes(row))
    cg[1].extend(aliases)
    eid = len(events.files)
    events.files.append(events_encode(cg))
    struct.pack_into('<H', d, city + 16, eid)

    # Visual aliases must never become trainers with the sentinel script ID.
    # Only the native sight-classification call changes; real trainers retain
    # their types, vision distances, defeat flags and native approach behavior.
    site = 0x0206429A
    assert d[site - 0x02000000:site - 0x02000000 + 4] == thumb_bl(site, 0x0205F26C)
    guard, code = append_code(main, '''push {r3,lr}
ldr r1,[r0]
lsls r1,r1,#6
bmi alias
bl 0x0205F26C
pop {r3,pc}
alias:
movs r0,#0
pop {r3,pc}
''')
    d[site - 0x02000000:site - 0x02000000 + 4] = thumb_bl(site, guard)

    # Normal Continue restores an actor snapshot, so old saves lack the new
    # aliases. Run after native object loading, adding only missing aliases.
    # Scan map-qualified actors instead of deleting/recreating existing ones;
    # this preserves movement positions and avoids a visible transition blink.
    previous = struct.unpack_from('<I', d, CMD_TABLE + 4)[0]
    checks = ''.join(f'ldrb r2,[r1,#{i}]\ncmp r2,#{b}\nbne delegate\n'
                     for i, b in enumerate(struct.pack('<I', MARKER)))
    asm = '''push {r4,r5,r6,r7,lr}
sub sp,#4
movs r4,r0
ldr r1,[r4,#8]
cmp r1,#0
beq delegate
''' + checks + '''adds r1,#4
str r1,[r4,#8]
adds r4,#128
ldr r4,[r4]
ldr r5,[r4,#60]
adr r6,rows
movs r7,#0
alias_loop:
movs r1,r5
adds r1,#128
adds r1,#128
adds r1,#36
ldr r1,[r1]
ldr r2,[r5,#4]
scan:
cmp r2,#0
beq create
ldr r0,[r1]
movs r3,#1
tst r0,r3
beq next
lsls r0,r0,#6
bpl next
ldr r0,[r1,#8]
cmp r0,r7
bne next
ldr r0,[r1,#28]
cmp r0,#28
beq found
next:
adds r1,#128
adds r1,#128
adds r1,#44
subs r2,#1
b scan
create:
movs r0,r5
movs r1,r6
movs r2,#52
bl 0x0205E1D0
found:
adds r6,#32
adds r7,#1
cmp r7,#3
blo alias_loop
movs r0,#0
add sp,#4
pop {r4,r5,r6,r7,pc}
delegate:
movs r0,r4
ldr r3,previous
blx r3
add sp,#4
pop {r4,r5,r6,r7,pc}
.align 2
previous: .word ''' + str(previous) + '\nrows:\n' + ''.join(
        '.byte ' + ','.join(str(b) for b in row) + '\n' for row in aliases)
    hook, hcode = append_code(main, asm)
    struct.pack_into('<I', d, CMD_TABLE + 4, hook | 1)
    csid = struct.unpack_from('<H', d, city + 6)[0]
    bank = split_bank(scripts.files[csid])
    assert len(bank) == 16, 'Expected 0024 city bank and its first-frame refresh'
    bank[-1] = struct.pack('<HI', 1, MARKER) + bank[-1]
    sid = len(scripts.files)
    scripts.files.append(script_bank(bank))
    struct.pack_into('<H', d, city + 6, sid)
    for path, arc in ((ep, events), (sp, scripts)):
        rom.files[rom.filenames.idOf(path)] = arc.save()
    main.sections[1].data.extend(bytes(-len(main.sections[1].data) % 4))
    struct.pack_into('<I', d, 0xD2C68, main.sections[1].ramAddress + len(main.sections[1].data))
    assert len(main.sections[1].data) <= 0x8000
    rom.arm9 = main.save(compress=True)
    return dict(city=CITY, owner_map=ROUTE, actors=list(range(3)), event=eid,
                script=sid, aliases=[a.hex() for a in aliases],
                sight_guard=dict(site=hex(site), hook=hex(guard), bytes=len(code)),
                saved_actor_refresh=dict(marker=hex(MARKER), hook=hex(hook),
                                         bytes=len(hcode), previous=hex(previous)),
                terrain_unchanged=True, trainer_records_unchanged=True)
