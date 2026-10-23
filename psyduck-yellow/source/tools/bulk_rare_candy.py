"""Native Rare Candy quantity picker; moves and one evolution after the batch.

Runtime state lives in ITCM, never in the save. Each candy uses the native item
service; the first has already been removed by the native party dispatcher.
Only the Rare Candy caller scans intermediate learnsets. Actual Pokémon level
is never temporarily lowered, including during move-replacement summaries.
"""
import struct
import ndspy.code
import ndspy.narc
from starter_properties import append_code
from prototype import thumb_bl, decode_messages, encode_messages
from opening import encode_text
from parcel_quest import PH

APPLY_SITE = 0x02081AF8
LEARN_SITE = 0x02081CFE
LEVEL_SITE = 0x0207156C


def patch(rom):
    main = rom.loadArm9()
    data = main.sections[0].data = bytearray(main.sections[0].data)
    overlays = rom.loadArm9Overlays()
    ov = overlays[15]
    ov.data = bytearray(ov.data)
    itcm = main.sections[1]
    itcm.data.extend(bytes(-len(itcm.data) % 4))
    state = itcm.ramAddress + len(itcm.data)
    # phase, requested, scan level, final level, mon pointer, saved label.
    itcm.data.extend(bytes(24))
    addresses = {}
    def emit(name, source):
        address, _ = append_code(main, source + f"\n.align 2\nbatch: .word {state}\n")
        addresses[name] = address
        return address
    def redirect(site, target, original):
        off = site - 0x02000000
        assert data[off:off+4] == thumb_bl(site, original), hex(site)
        data[off:off+4] = thumb_bl(site, target)
    def ov_redirect(site, target, expected):
        off = site - ov.ramAddress
        assert ov.data[off:off+8] == expected, hex(site)
        ov.data[off:off+8] = bytes.fromhex('004b1847') + struct.pack('<I', target | 1)

    apply = emit('apply', r"""
push {r4, r5, r6, r7, lr}
sub sp, #28
str r0, [sp, #8]
str r1, [sp, #12]
str r2, [sp, #16]
str r3, [sp, #20]
ldr r0, [sp, #48]
str r0, [sp]
ldr r0, [sp, #52]
str r0, [sp, #4]
ldr r4, batch
movs r6, #1
ldr r0, [r4]
cmp r0, #2
bne apply_one
ldr r0, [sp, #8]
ldr r1, [sp, #16]
bl 0x02074644
str r0, [r4, #16]
movs r1, #161
movs r2, #0
bl 0x0206E540
movs r7, r0
adds r0, #1
str r0, [r4, #8]
movs r0, #100
subs r0, r0, r7
ldr r6, [r4, #4]
cmp r6, r0
bls bounded
movs r6, r0
bounded:
ldr r0, bag_pointer
ldr r0, [r0]
movs r1, #50
movs r2, #12
bl 0x02078550
adds r0, #1
cmp r6, r0
bls apply_one
movs r6, r0
apply_one:
ldr r0, [sp, #8]
ldr r1, [sp, #12]
ldr r2, [sp, #16]
ldr r3, [sp, #20]
bl 0x020908AC
str r0, [sp, #24]
subs r6, #1
beq applied
ldr r0, bag_pointer
ldr r0, [r0]
movs r1, #50
movs r2, #1
movs r3, #12
bl 0x02078434
cmp r0, #0
bne apply_one
applied:
ldr r0, [r4]
cmp r0, #2
bne apply_return
ldr r0, [r4, #16]
movs r1, #161
movs r2, #0
bl 0x0206E540
str r0, [r4, #12]
movs r0, #3
str r0, [r4]
apply_return:
ldr r0, [sp, #24]
add sp, #28
pop {r4, r5, r6, r7, pc}
.align 2
bag_pointer: .word BAGSTATE
""".replace('BAGSTATE', str(state + 20)))
    redirect(APPLY_SITE, apply, 0x020908AC)

    level = emit('learn_level', r"""
ldr r3, batch
ldr r2, [r3]
cmp r2, #3
bne actual
ldr r2, [r3, #16]
cmp r0, r2
bne actual
ldr r0, [r3, #8]
bx lr
actual:
movs r2, #0
ldr r3, original
bx r3
.align 2
original: .word 0x0206E541
""")
    redirect(LEVEL_SITE, level, 0x0206E540)
    learn = emit('learn_moves', r"""
push {r4, r5, r6, r7, lr}
sub sp, #4
movs r4, r0
movs r5, r1
movs r6, r2
ldr r7, batch
again:
movs r0, r4
movs r1, r5
movs r2, r6
bl 0x02071534
cmp r0, #0
bne finished
ldr r1, [r7]
cmp r1, #3
bne finished
ldr r1, [r7, #16]
cmp r1, r4
bne finished
ldr r1, [r7, #8]
ldr r2, [r7, #12]
cmp r1, r2
bhs finished
adds r1, #1
str r1, [r7, #8]
str r0, [r5]
b again
finished:
add sp, #4
pop {r4, r5, r6, r7, pc}
""")
    redirect(LEARN_SITE, learn, 0x02071534)

    # Relocate the eight original Use-entry instructions (no PC-relative load).
    original_use, _ = append_code(main, r"""
push {r3, r4, lr}
sub sp, #4
movs r4, r0
movs r1, #0
ldr r3, continuation
bx r3
.align 2
continuation: .word 0x021FB689
""")
    fid = rom.filenames.idOf('a/0/2/7')
    texts = ndspy.narc.NARC(rom.files[fid])
    key, messages = decode_messages(texts.files[10])
    label_index = len(messages)
    messages.extend(decode_messages(encode_text(['Use'], PH))[1])
    texts.files[10] = encode_messages(key, messages)
    rom.files[fid] = texts.save()
    picker = emit('picker', f"""
push {{r4, r5, r6, lr}}
movs r4, r0
ldr r5, batch
movs r0, #0
str r0, [r5]
ldr r0, view_offset
ldr r0, [r4, r0]
adds r0, #0x66
ldrh r0, [r0]
cmp r0, #50
beq candy
movs r0, r4
pop {{r4, r5, r6}}
pop {{r3}}
mov lr, r3
ldr r3, use_native
bx r3
candy:
movs r0, #1
str r0, [r5]
ldr r6, quantity_offset
movs r0, #1
strh r0, [r4, r6]
ldr r0, bag_offset
ldr r0, [r4, r0]
str r0, [r5, #20]
movs r1, #50
movs r2, #6
bl 0x02078550
adds r1, r6, #2
strh r0, [r4, r1]
movs r0, r4
bl 0x021FFF24
movs r0, r4
movs r1, #3
movs r2, #0
movs r3, #0
bl 0x021FD574
adds r2, r6, #2
ldrh r2, [r4, r2]
movs r0, r4
movs r1, #3
bl 0x02200300
movs r0, r4
movs r1, #3
bl 0x021FEDEC
ldr r6, label_offset
ldr r0, [r4, r6]
str r0, [r5, #16]
ldr r0, messages_offset
ldr r0, [r4, r0]
ldr r1, label_index
bl 0x0200BBA0
str r0, [r4, r6]
movs r0, r4
bl 0x021FF7C4
movs r0, r4
movs r1, #1
bl 0x021FF29C
movs r0, #5
pop {{r4, r5, r6, pc}}
.align 2
view_offset: .word 0x234
bag_offset: .word 0x238
quantity_offset: .word 0x680
label_offset: .word 0x314
messages_offset: .word 0x2f0
label_index: .word {label_index}
use_native: .word {original_use | 1}
""")
    ov_redirect(0x021FB680, picker, bytes.fromhex('18b581b0041c0021'))

    restore = emit('restore_label', r"""
push {r4, r5, r6, lr}
movs r4, r0
ldr r5, batch
ldr r6, label_offset
ldr r0, [r4, r6]
bl 0x02026380
ldr r0, [r5, #16]
str r0, [r4, r6]
movs r0, #0
str r0, [r5, #16]
pop {r4, r5, r6, pc}
.align 2
label_offset: .word 0x314
""")
    for name, site, first_call in [('confirm', 0x021FBF98, 0x021FEEA4), ('cancel', 0x021FBFC0, 0x021FED3C)]:
        trampoline, _ = append_code(main, f"""
push {{r4, lr}}
movs r4, r0
bl {first_call}
ldr r3, continuation
bx r3
.align 2
continuation: .word {site + 9}
""")
        action = f"""
movs r0, r4
bl {restore}
movs r0, #0
str r0, [r5]
movs r0, r4
pop {{r4, r5, r6}}
pop {{r3}}
mov lr, r3
ldr r3, native
bx r3
""" if name == 'cancel' else f"""
ldr r0, quantity_offset
ldrh r0, [r4, r0]
str r0, [r5, #4]
movs r0, r4
bl {restore}
movs r0, #2
str r0, [r5]
movs r0, r4
bl 0x02200428
movs r0, r4
bl 0x021FFF24
movs r0, r4
bl 0x021FF834
movs r0, r4
bl 0x021FED3C
movs r0, r4
pop {{r4, r5, r6}}
pop {{r3}}
mov lr, r3
ldr r3, use_native
bx r3
"""
        entry = emit(name, f"""
push {{r4, r5, r6, lr}}
movs r4, r0
ldr r5, batch
ldr r0, [r5]
cmp r0, #1
beq candy_action
movs r0, r4
pop {{r4, r5, r6}}
pop {{r3}}
mov lr, r3
ldr r3, native
bx r3
candy_action:
{action}
.align 2
quantity_offset: .word 0x680
native: .word {trampoline | 1}
use_native: .word {original_use | 1}
""")
        ov_redirect(site, entry, bytes.fromhex('10b5041c') + thumb_bl(site+4, first_call))

    cleanup = emit('party_cleanup', r"""
push {r4, r5, r6, lr}
movs r4, r0
movs r5, r1
bl 0x02079034
movs r6, r0
ldr r0, [r5]
cmp r0, #32
bne returned
movs r0, r4
bl 0x02007290
ldr r1, args_offset
ldr r0, [r0, r1]
adds r0, #0x27
ldrb r0, [r0]
cmp r0, #5
beq returned
ldr r1, batch
movs r0, #0
str r0, [r1]
returned:
movs r0, r6
pop {r4, r5, r6, pc}
.align 2
args_offset: .word 0x654
""")
    assert struct.unpack_from('<I', data, 0x1015a0)[0] == 0x02079035
    struct.pack_into('<I', data, 0x1015a0, cleanup | 1)
    struct.pack_into('<I', data, 0xd2c68, itcm.ramAddress + len(itcm.data))
    rom.arm9 = main.save(compress=True)
    rom.files[ov.fileID] = ov.save(compress=ov.compressed)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
    return dict(state=hex(state), routines={k:hex(v) for k,v in addresses.items()},
                quantity_label=label_index, evolution_after_batch=True,
                intermediate_moves=True, save_format_changed=False)
