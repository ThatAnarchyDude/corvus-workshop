"""Small Thumb-1 extensions in the ARM9's existing autoloaded ITCM section."""
import struct

from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from prototype import thumb_bl
from build_rom import PROJECT, sha

CMD_TABLE = 0xFAD00
GENERATION_VAR = 0x416B
FIRST_BLUE_TRAINER = 741


def append_code(main, source):
    itcm = main.sections[1]
    assert itcm.ramAddress == 0x01FF8000 and not itcm.bssSize
    itcm.data.extend(b'\0' * (-len(itcm.data) % 4))
    address = itcm.ramAddress + len(itcm.data)
    assembly = '\n'.join(line.split('@')[0] for line in source.splitlines())
    raw, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(assembly, addr=address)
    code = bytes(raw)
    itcm.data.extend(code)
    if len(itcm.data) >= 0x8000:
        raise ValueError('ITCM extension exceeds 32 KiB')
    return address, code


def patch(main):
    data = main.sections[0].data
    assert struct.unpack_from('<I', data, CMD_TABLE+4)[0] == 0x02040895
    old_end = main.sections[1].ramAddress + len(main.sections[1].data)
    assert old_end == 0x01FF8620
    source = (PROJECT/'asm/starter-properties.s').read_text()
    address, code = append_code(main, source)
    struct.pack_into('<I', data, CMD_TABLE+4, address | 1)
    # Native UpdateMonAbility is a literal-pointer tail call to UpdateBoxMonAbility.
    assert data[0x722D4:0x722D8] == bytes.fromhex('004b1847')
    assert struct.unpack_from('<I', data, 0x722D8)[0] == 0x020722DD
    ability_source = '''
push {r4, r5, r6, lr}
sub sp, #8
movs r4, r0
movs r1, #5
movs r2, #0
bl 0x0206E640
movs r5, r0
movs r0, r4
movs r1, #10
movs r2, #0
bl 0x0206E640
movs r6, r0
ldr r1, ability_table_ptr
table_loop:
ldrh r0, [r1]
cmp r0, #0
beq ordinary
cmp r0, r5
beq species_match
adds r1, #4
b table_loop
species_match:
ldrb r2, [r1, #2]
ldrb r0, [r1, #3]
cmp r0, r6
beq hidden
cmp r2, r6
bne ordinary
hidden:
cmp r2, #0
beq ordinary
str r2, [sp]
movs r0, r4
movs r1, #10
mov r2, sp
bl 0x0206ED70
b finished
ordinary:
movs r0, r4
bl 0x020722DC
finished:
add sp, #8
pop {r4, r5, r6, pc}
.align 2
ability_table_ptr: .word ability_table
ability_table:
.short 54
.byte 33,33
.short 55
.byte 33,33
.short 133
.byte 107,107
.short 134
.byte 93,107
.short 135
.byte 95,107
.short 136
.byte 62,107
.short 196
.byte 0,107
.short 197
.byte 39,107
.short 470
.byte 34,107
.short 471
.byte 115,107
.short 175
.byte 105,105
.short 176
.byte 105,105
.short 468
.byte 105,105
.short 0
.byte 0,0
'''
    ability, ability_code = append_code(main, ability_source)
    struct.pack_into('<I', data, 0x722D8, ability | 1)
    # Blue's class supplies Blue's battle artwork. Only appended rival trainers
    # take the saved rival-name branch; native Blue and Silver stay unchanged.
    name_source = f'''
cmp r0, #23
beq named
cmp r0, #110
bne normal
ldr r1, [r4, #24]
ldr r0, first_trainer
cmp r1, r0
blo normal
named:
bx lr
normal:
mov r0, lr
adds r0, #10
bx r0
.align 2
first_trainer: .word {FIRST_BLUE_TRAINER}
'''
    assert data[0x73414:0x73418] == bytes.fromhex('172804d1')
    name, name_code = append_code(main, name_source)
    data[0x73414:0x73418] = thumb_bl(0x02073414, name)
    # Move SDK's ITCM arena lower bound past the extension. All prior ITCM
    # code remains byte-identical, and future allocations cannot overwrite it.
    assert struct.unpack_from('<I', data, 0xD2C68)[0] == old_end
    end = main.sections[1].ramAddress + len(main.sections[1].data)
    struct.pack_into('<I', data, 0xD2C68, end)
    return dict(starter_hook=hex(address), starter_bytes=len(code),
                ability_hook=hex(ability), rival_name_hook=hex(name),
                itcm_end=hex(end), starter_code_sha256=sha(code),
                shiny_roll_denominator=16384, perfect_iv_roll_denominator=16384,
                hidden_ability_probability='1/3', hidden_ability_evolution_exception=
                'Espeon Magic Bounce is absent in Gen IV; evolution uses Synchronize')
