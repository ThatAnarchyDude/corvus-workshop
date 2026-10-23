"""Generation-IV engine extensions for shiny odds, Shiny Charm and HGSS Legendary IVs.

Inventory checks happen during generation, never during shiny rendering. No
existing Pokémon changes colour when the charm is withdrawn or deposited.
"""
import struct
from starter_properties import append_code
from prototype import thumb_bl
import ndspy.narc
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages,encode_messages
ITEM=114
LEGENDARIES=(144,145,146,150,243,244,245,249,250,380,381,382,383,384,483,484,487)


def redirect(main,site,source):
    """Relocate eight position-independent entry bytes, then tail-call native code."""
    data=main.sections[0].data;offset=site-0x02000000
    original=bytes(data[offset:offset+8])
    if site==0x0206EC40:
        expected=bytes.fromhex('70b5051c a8880c1c'.replace(' ',''))
        assert original==expected,(original.hex(),expected.hex())
    tramp,_=append_code(main, '.byte '+','.join(str(x) for x in original)+f'\nldr r3, target\nbx r3\n.align 2\ntarget: .word {site+8|1}')
    entry,_=append_code(main,source.replace('NATIVE',hex(tramp)))
    # Neither relocated prologue uses r3 before the original reads incoming r3;
    # CreateMon saved its arguments in its first instruction.
    data[offset:offset+8]=bytes.fromhex('004b1847')+struct.pack('<I',entry|1)
    return entry,tramp


def patch_engine(main):
    d=main.sections[0].data
    assert d[0x70080:0x70082]==bytes.fromhex('0828');d[0x70080:0x70082]=bytes.fromhex('1028')
    assert d[0x6DF3C:0x6DF40]==bytes.fromhex('0828e6d3');d[0x6DF3E:0x6DF40]=bytes.fromhex('c046')
    save_pointer=struct.unpack_from('<I',d,0x272C4)[0]
    owned,_=append_code(main,f'''
push {{r4, lr}}
ldr r0, save_pointer
ldr r0, [r0]
cmp r0, #0
beq absent
bl 0x0207879C
ldr r1, key_offset
adds r0, r0, r1
movs r2, #50
scan:
ldrh r1, [r0]
cmp r1, #114
bne next
ldrh r1, [r0, #2]
cmp r1, #0
bne present
next:
adds r0, #4
subs r2, #1
bne scan
absent:
movs r0, #0
pop {{r4, pc}}
present:
movs r0, #1
pop {{r4, pc}}
.align 2
save_pointer: .word {save_pointer}
key_offset: .word 660
''')
    roll,_=append_code(main,f'''
push {{r4, lr}}
bl 0x0201FD44
movs r4, r0
bl {owned}
cmp r0, #0
beq normal
movs r0, #1
lsls r0, r0, #11
bics r4, r0
normal:
movs r0, r4
pop {{r4, pc}}
''')
    legendary,_=append_code(main,'''
ldr r1, species_table
scan:
ldrh r2, [r1]
cmp r2, #0
beq absent
cmp r0, r2
beq present
adds r1, #2
b scan
absent:
movs r0, #0
bx lr
present:
movs r0, #1
bx lr
.align 2
species_table: .word table
table: .hword '''+','.join(map(str,LEGENDARIES+(0,))))
    # Alter only the high PID half; preserve gender and ordinary ability parity.
    # Native reshuffling/encryption handles any change in substructure ordering.
    boost,_=append_code(main,f'''
push {{r4, r5, r6, lr}}
movs r4, r0
bl {owned}
cmp r0, #0
beq done
movs r0, r4
movs r1, #7
movs r2, #0
bl 0x0206E540
movs r5, r0
ldr r6, [r4]
lsrs r1, r5, #16
eors r5, r1
lsrs r1, r6, #16
eors r5, r1
eors r5, r6
lsls r5, r5, #16
lsrs r5, r5, #16
cmp r5, #16
blo done
cmp r5, #32
bhs done
movs r1, #1
lsls r1, r1, #20
eors r1, r6
movs r0, r4
bl 0x0207235C
movs r0, r4
bl 0x0206E250
done:
pop {{r4, r5, r6, pc}}
''')
    # CreateMon's first eight bytes save incoming r0-r3 before clobbering r3,
    # so a literal jump through r3 WOULD lose fixedIV. Use r12 trampoline.
    # Mark unassigned-OT creations until the native gift/egg/wild setup has
    # supplied their actual trainer ID. Bit 3 is unused in HG's box header.
    pending,_=append_code(main,f'''
ldrh r1, [r0, #4]
movs r2, #8
tst r1, r2
bne resolve
bx lr
resolve:
bics r1, r2
strh r1, [r0, #4]
ldr r3, boost
bx r3
.align 2
boost: .word {boost|1}
''')
    constructor_source=f'''
push {{r4, r5, r6, lr}}
sub sp, #32
movs r4, r0
movs r5, r1
movs r6, r3
str r2, [sp, #16]
ldr r0, [sp, #48]
str r0, [sp]
ldr r0, [sp, #52]
str r0, [sp, #4]
ldr r0, [sp, #56]
str r0, [sp, #8]
ldr r0, [sp, #60]
str r0, [sp, #12]
movs r0, r5
bl {legendary}
cmp r0, #0
beq ordinary_iv
movs r6, #31
ordinary_iv:
movs r0, r4
movs r1, r5
ldr r2, [sp, #16]
movs r3, r6
bl NATIVE
ldr r0, [sp, #8]
cmp r0, #0
beq mark_pending
movs r0, r4
bl {boost}
b finished
mark_pending:
ldrh r0, [r4, #4]
movs r1, #8
orrs r0, r1
strh r0, [r4, #4]
finished:
add sp, #32
pop {{r4, r5, r6, pc}}
'''
    # Preserve incoming r3 by using an r12 literal jump with a 12-byte entry.
    # Original prologue is copied into a trampoline and jumps via r3 AFTER
    # saving the original r3, which is then unused by the remainder.
    at=0x6DE38
    original=bytes(d[at:at+16]);assert original[-4:]==thumb_bl(0x0206DE44,0x0206DCE4)
    # Relocate BL as an actual assembled instruction rather than raw offset.
    tramp2,_=append_code(main,'.byte '+','.join(map(str,original[:12]))+'\nbl 0x0206DCE4\nldr r3,target\nbx r3\n.align 2\ntarget: .word 0x0206DE49')
    # Keystone does not advance its absolute BL origin for a .byte prefix.
    pos=tramp2-main.sections[1].ramAddress+12
    main.sections[1].data[pos:pos+4]=thumb_bl(tramp2+12,0x0206DCE4)
    constructor,_=append_code(main,constructor_source.replace('NATIVE',hex(tramp2)))
    d[at:at+16]=bytes.fromhex('08b4024b9c4608bc60470000')+struct.pack('<I',constructor|1)
    setter_source=f'''
push {{r4, r5, r6, lr}}
sub sp, #8
movs r4, r0
movs r5, r1
movs r6, r2
cmp r5, #175
beq iv_check
cmp r5, #70
blo native
cmp r5, #75
bhi native
iv_check:
movs r1, #5
movs r2, #0
bl 0x0206E540
bl {legendary}
cmp r0, #0
beq native
movs r0, #31
cmp r5, #175
bne store
ldr r0, packed
store:
str r0, [sp]
mov r6, sp
native:
movs r0, r4
movs r1, r5
movs r2, r6
bl NATIVE
ldrh r0, [r4, #4]
movs r1, #8
tst r0, r1
beq finished
movs r0, r4
movs r1, #7
movs r2, #0
bl 0x0206E540
cmp r0, #0
beq finished
movs r0, r4
bl {pending}
finished:
add sp, #8
pop {{r4, r5, r6, pc}}
.align 2
packed: .word 0x3fffffff
'''
    setter,tramp=redirect(main,0x0206EC40,setter_source)
    party_source=f'''
push {{r4, r5, r6, lr}}
movs r4, r0
movs r5, r1
movs r0, r1
bl {pending}
movs r0, r4
movs r1, r5
bl NATIVE
pop {{r4, r5, r6, pc}}
'''
    party,party_tramp=redirect(main,0x02074524,party_source)
    return dict(base_shiny_denominator=4096,charm_shiny_denominator=2048,item_id=ITEM,owned_hook=hex(owned),shiny_roll_hook=hex(roll),legendary_hook=hex(legendary),generation_hook=hex(constructor),generation_trampoline=hex(tramp2),setter_hook=hex(setter),setter_trampoline=hex(tramp),charm_boost_hook=hex(boost),pending_hook=hex(pending),party_hook=hex(party),party_trampoline=hex(party_tramp),legendary_species=list(LEGENDARIES),unlocked_constructor_site='0x0206df3e',save_pointer=hex(save_pointer))


def patch_item(rom,main,texts):
    items=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/7')]);d=main.sections[0].data;table=0x100194
    assert struct.unpack_from('<4H',d,table+ITEM*8)==(0,793,794,0)
    source=struct.unpack_from('<H',d,table+459*8)[0]
    item=bytearray(items.files[source]);item[10:14]=bytes(4)
    idx=len(items.files);items.files.append(item)
    _,icon,palette,_=struct.unpack_from('<4H',d,table+224*8)
    struct.pack_into('<4H',d,table+ITEM*8,idx,icon,palette,0)
    rom.files[rom.filenames.idOf('a/0/1/7')]=items.save()
    for bank,line in [(222,'Shiny Charm'),(221,'A sparkling charm. Carry it in your Bag to double the chance of meeting shiny POKEMON.')]:
        key,messages=decode_messages(texts.files[bank]);messages[ITEM]=decode_messages(encode_text([line],PH))[1][0];texts.files[bank]=encode_messages(key,messages)


def unlock_shiny_locks(rom,main,engine):
    """Remove native anti-shiny rejection and roll previously fixed NPC trades."""
    import ndspy.code
    from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
    assembler=Ks(KS_ARCH_ARM,KS_MODE_THUMB)
    d=main.sections[0].data
    changes=[]
    for site,expected,target,label in [
        (0x0206D15A,'09d0',0x0206D170,'Ranger Manaphy hatch'),
        (0x0204C05A,'0bd0',0x0204C074,'Mystery Gift random PID'),
        (0x0204B8E2,'e8d0',None,'Pokewalker transfer')]:
        at=site-0x02000000;assert d[at:at+2]==bytes.fromhex(expected)
        d[at:at+2]=bytes(assembler.asm(f'b {target}',addr=site)[0]) if target else bytes.fromhex('c046')
        changes.append(dict(site=hex(site),path=label))
    # Gift data has its PID replaced after the normal constructor.
    boost=int(engine['charm_boost_hook'],16)
    gift,_=append_code(main,f'''push {{r4, lr}}
movs r4, r0
bl 0x0207235C
movs r0, r4
bl {boost}
pop {{r4, pc}}''')
    site=0x0204C078;assert d[site-0x2000000:site-0x2000000+4]==thumb_bl(site,0x0207235C)
    d[site-0x2000000:site-0x2000000+4]=thumb_bl(site,gift)
    # Trades originally used a fixed non-shiny PID and asserted non-shininess.
    # Keep low PID bits (gender/ability) and trade identity; independently roll
    # the high half, then recalculate stats after the possible nature change.
    roll=int(engine['shiny_roll_hook'],16)
    trade,_=append_code(main,f'''push {{r4, r5, r6, lr}}
movs r4, r0
bl {roll}
lsls r0, r0, #20
lsrs r6, r0, #20
movs r0, r4
movs r1, #7
movs r2, #0
bl 0x0206E540
movs r5, r0
lsrs r1, r5, #16
eors r5, r1
ldr r1, [r4]
lsls r1, r1, #16
lsrs r1, r1, #16
eors r5, r1
cmp r6, #0
beq shiny
ldr r0, [r4]
lsrs r0, r0, #16
eors r0, r5
lsls r0, r0, #16
lsrs r0, r0, #16
cmp r0, #16
bhs unchanged
movs r0, #16
eors r5, r0
shiny:
lsls r5, r5, #16
orrs r1, r5
movs r0, r4
bl 0x0207235C
movs r0, r4
bl 0x0206E250
unchanged:
movs r0, #0
pop {{r4, r5, r6, pc}}''')
    # Kenya/Shuckie return quests identify the original PID. Accept only
    # the original or our exact two high-half transformations; keep every
    # other native identity check (OT, species, nickname, language) intact.
    identity,_=append_code(main,"""push {r4, r5, r6, lr}
bl 0x0206E540
ldr r1, [r5, #56]
cmp r0, r1
beq identity_done
lsls r2, r1, #16
lsrs r2, r2, #16
ldr r3, [r5, #32]
lsrs r6, r3, #16
eors r3, r6
eors r3, r2
lsls r3, r3, #16
orrs r3, r2
cmp r0, r3
beq matched
movs r2, #1
lsls r2, r2, #20
eors r3, r2
cmp r0, r3
bne identity_done
matched:
movs r0, r1
identity_done:
pop {r4, r5, r6, pc}""")
    site=0x0206DA20;at=site-0x2000000;assert d[at:at+4]==thumb_bl(site,0x0206E540);d[at:at+4]=thumb_bl(site,identity)
    overlays=rom.loadArm9Overlays()
    for site,expected in [(0x0222A020,'ead0'),(0x022367EA,'e8d0')]:
        o=overlays[80];at=site-o.ramAddress;assert o.data[at:at+2]==bytes.fromhex(expected);o.data[at:at+2]=bytes.fromhex('c046');changes.append(dict(site=hex(site),overlay=80,path='Pokewalker generation'))
    o=overlays[23];site=0x02259D6C;at=site-o.ramAddress;assert o.data[at:at+4]==thumb_bl(site,0x0207003C);o.data[at:at+4]=thumb_bl(site,trade)
    for idx in [23,80]:o=overlays[idx];rom.files[o.fileID]=o.save(compress=True)
    rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    engine.update(unlocked_shiny_locks=changes,npc_trade_hook=hex(trade),mystery_gift_hook=hex(gift),trade_identity_hook=hex(identity))
