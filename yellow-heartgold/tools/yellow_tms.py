"""Add Yellow's Bide reward without replacing HeartGold's existing TM34."""
import json
import struct

import ndspy.narc
import ndspy.code

from build_rom import PROJECT
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages, encode_messages, thumb_bl
from starter_properties import append_code

BIDE_ITEM = 115
BIDE_MOVE = 117
BIDE_COMPAT_INDEX = 100
ITEM_TABLE = 0x100194
MOVE_ENTRY = 0x02078000
INDEX_ENTRY = 0x0207804C
EXPECTED_ENTRY = bytes.fromhex('52229200904203d3')


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    old_end = main.sections[1].ramAddress + len(main.sections[1].data)
    assert struct.unpack_from('<I', d, 0xD2C68)[0] == old_end
    for site in (MOVE_ENTRY, INDEX_ENTRY):
        assert bytes(d[site-0x02000000:site-0x02000000+8]) == EXPECTED_ENTRY
    table = 0x021000CC
    assert struct.unpack_from('<6H', d, table-0x02000000) == (264,337,352,347,46,92)
    common = '''
cmp r0, #115
beq custom
movs r2, #82
lsls r2, r2, #2
cmp r0, r2
blo none
adds r1, r2, #0
adds r1, #99
cmp r0, r1
bhi none
subs r0, r0, r2
'''
    move, _ = append_code(main, common + f'''
lsls r0, r0, #1
ldr r1, moves
ldrh r0, [r1, r0]
bx lr
custom:
movs r0, #117
bx lr
none:
movs r0, #0
bx lr
.align 2
moves: .word {table}
''')
    index, _ = append_code(main, common + '''
bx lr
custom:
movs r0, #100
bx lr
none:
movs r0, #0
bx lr
''')
    for site, target in ((MOVE_ENTRY, move), (INDEX_ENTRY, index)):
        at = site - 0x02000000
        d[at:at+8] = bytes.fromhex('004b1847') + struct.pack('<I', target | 1)
    # Bag display normally derives a TM number by subtracting the native item
    # range. Supply TM34's number for this item in those two display paths;
    # the item ID and compatibility index used for teaching remain unchanged.
    overlays = rom.loadArm9Overlays()
    bag = overlays[15]
    display_hooks = []
    for site, expected, load in ((0x021FE920,bytes.fromhex('39888000'),'ldrh r1, [r7]'),
                                 (0x021FF5B2,bytes.fromhex('d95b8000'),'ldrh r1, [r3, r7]')):
        at = site-bag.ramAddress
        assert bytes(bag.data[at:at+4])==expected
        hook, _ = append_code(main, load+'''
cmp r1, #115
bne ordinary
ldr r1, native_tm34
ordinary:
lsls r0, r0, #2
bx lr
.align 2
native_tm34: .word 361
''')
        bag.data[at:at+4] = thumb_bl(site,hook)
        display_hooks.append(dict(site=hex(site),hook=hex(hook)))
    rom.files[bag.fileID] = bag.save(compress=bag.compressed)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
    struct.pack_into('<I', d, 0xD2C68,
                     main.sections[1].ramAddress + len(main.sections[1].data))

    # The native pocket has 101 entries and accepts item IDs from metadata.
    # Compatibility bit 100 is unused by the 92 existing TMs and eight HMs.
    personal_id = rom.filenames.idOf('a/0/0/2')
    personal = ndspy.narc.NARC(rom.files[personal_id])
    yellow = set(json.loads((PROJECT/'data/yellow-bide-compatibility.json').read_text())['species'])
    compatible = []
    for species, row in enumerate(personal.files):
        eligible = species in yellow if species <= 151 else any(row[28:44])
        if eligible:
            b = bytearray(row)
            b[40] |= 1 << 4
            personal.files[species] = bytes(b)
            compatible.append(species)
    rom.files[personal_id] = personal.save()

    items_id = rom.filenames.idOf('a/0/1/7')
    items = ndspy.narc.NARC(rom.files[items_id])
    assert struct.unpack_from('<4H', d, ITEM_TABLE+BIDE_ITEM*8) == (0,793,794,0)
    source = struct.unpack_from('<H', d, ITEM_TABLE+361*8)[0]
    item = bytearray(items.files[source])
    struct.pack_into('<H', item, 0, 0)  # Gift reward; no invented purchase price.
    item_index = len(items.files)
    items.files.append(item)
    _, icon, palette, _ = struct.unpack_from('<4H', d, ITEM_TABLE+354*8)
    struct.pack_into('<4H', d, ITEM_TABLE+BIDE_ITEM*8, item_index, icon, palette, 0)
    rom.files[items_id] = items.save()
    text_id = rom.filenames.idOf('a/0/2/7')
    texts = ndspy.narc.NARC(rom.files[text_id])
    for bank, line in ((222, 'TM34'),
                       (221, 'A single-use TM containing BIDE. The user endures attacks, then returns the damage twofold.')):
        key, messages = decode_messages(texts.files[bank])
        messages[BIDE_ITEM] = decode_messages(encode_text([line], PH))[1][0]
        texts.files[bank] = encode_messages(key, messages)
    rom.files[text_id] = texts.save()
    rom.arm9 = main.save(compress=True)
    return dict(item=BIDE_ITEM, move=BIDE_MOVE, compatibility_index=BIDE_COMPAT_INDEX,
                move_hook=hex(move), index_hook=hex(index), display_hooks=display_hooks,
                compatible_species=compatible,
                gen1_compatibility='Yellow', later_species='Existing TM-compatible species')
