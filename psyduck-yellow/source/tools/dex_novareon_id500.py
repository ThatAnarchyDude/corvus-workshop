"""Novareon's Pokedex identity moves from species id 1581 to the unused id 500 so the Pokedex's SIZE page works (owner request 2026-10-23: the SIZE tab froze the game).

Found by experiment (2026-10-23): the SIZE page misbehaves for every species id above 1075 (a stock form id such as 1534 or 1100 also garbles it), while 1075 and below work.
Ids 494-543 are the unused gap between Gen 4 and Gen 5, so id 500 is a free id below the limit. The first Pokedex attempt used it and the National list skipped it
because the Pokedex's range test (ARM9 0x0202940C: "is this id in the 494-543 gap?") rejected it; that test now lets 500 through.
 - dex_novareon.py's species wrapper and number routine keep working: its alias table now sends species 1581 and 1582 to 500, and the number routine's special case is
   id 500 (-> National No. 1026).
 - id 500 gets copies of everything the Pokedex reads by species: personal data, battle sprites and palettes, icon, sprite offsets, follower flags, names, the Pokedex text rows
   (category, name, height, weight, entry), height/weight/shape arrays, footprint and the three Pokedex-app NARCs.
 - The National list's last entry (1026) is 500 instead of 1581.

Usage: dex_novareon_id500.py <in.nds> <out.nds>
"""
import re
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap
from prototype import decode_messages, encode_messages

DEX, NOVAREON, MEGA_NOVAREON = 500, 1581, 1582
FIRST_FORM = 1076
HOLE_CHECK = 0x0202940C
NUMBER_HOOK = 0x020FF114
ENTRY = 89
BANKS = (237, 238, 803, 812, 813, 814, 815, 816, 817, 823)


def patch(rom):
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    original = bytes(addons.files[12])
    address, size = ext.reserve_code(rom, 48)                     # first: it rewrites overlay 129 (the header table moves up)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    # 1. alias tables: the copy that maps Novareon to itself (dex_novareon.py's) now maps it to 500
    changed = 0
    for m in re.finditer(re.escape(original[:64]), bytes(perm.data)):
        at = m.start()
        if struct.unpack_from('<H', perm.data, at + 2 * (NOVAREON - FIRST_FORM))[0] == NOVAREON:
            struct.pack_into('<H', perm.data, at + 2 * (NOVAREON - FIRST_FORM), DEX)
            struct.pack_into('<H', perm.data, at + 2 * (MEGA_NOVAREON - FIRST_FORM), DEX)
            changed += 1
    assert changed == 1, changed
    # 2. the number routine's special case: id 1581 -> id 500
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    base = section.ramAddress
    routine = struct.unpack_from('<I', section.data, NUMBER_HOOK - base + 4)[0] & ~1
    at = routine - perm.ramAddress
    literals = [at + k for k in range(0, 0x60, 4) if struct.unpack_from('<I', perm.data, at + k)[0] == NOVAREON]
    assert len(literals) == 1, literals
    struct.pack_into('<I', perm.data, literals[0], DEX)
    # 3. the gap test lets id 500 through (a routine in the fresh gap; the original function entry becomes a jump to it)
    gap = Gap(perm, address, size)
    routine_gap = gap.code('''movs r1, #0xf7
lsls r1, r1, #1
cmp r0, r1
blo ret0
adds r1, #0x32
cmp r0, r1
bhs ret0
movs r1, #0xfa
lsls r1, r1, #1
cmp r0, r1
beq ret0
movs r0, #1
bx lr
ret0:
movs r0, #0
bx lr
''')
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    at = HOLE_CHECK - base
    assert bytes(section.data[at:at + 4]) == bytes.fromhex('f7214900'), bytes(section.data[at:at + 4]).hex()
    section.data[at:at + 8] = bytes.fromhex('004b1847') + struct.pack('<I', routine_gap | 1)      # ldr r3,[pc,#0]; bx r3; .word routine
    rom.arm9 = main.save(compress=True)
    # 4. species 500 = a copy of 1581's data
    def copy_one(path, per=1):
        narc = ndspy.narc.NARC(rom.getFileByName(path))
        for k in range(per):
            narc.files[DEX * per + k] = bytes(narc.files[NOVAREON * per + k])
        rom.setFileByName(path, narc.save())
    for path, per in (('a/0/0/2', 1), ('a/0/0/4', 6), ('a/0/0/5', 4), ('a/1/4/1', 1), ('a/0/6/9', 1), ('a/2/5/6', 1), ('a/2/4/8', 1), ('a/2/2/1', 1)):
        copy_one(path, per)
    icons = ndspy.narc.NARC(rom.getFileByName('a/0/2/0'))
    icons.files[7 + DEX] = bytes(icons.files[7 + NOVAREON])
    rom.setFileByName('a/0/2/0', icons.save())
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    banks = bytearray(addons.files[9])
    banks[DEX] = banks[NOVAREON]
    addons.files[9] = bytes(banks)
    rom.setFileByName('a/0/2/8', addons.save())
    offsets = ndspy.narc.NARC(rom.getFileByName('a/1/8/0'))
    table = bytearray(offsets.files[0])
    table[DEX * ENTRY:(DEX + 1) * ENTRY] = table[NOVAREON * ENTRY:(NOVAREON + 1) * ENTRY]
    offsets.files[0] = bytes(table)
    rom.setFileByName('a/1/8/0', offsets.save())
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    for bank in BANKS:
        key, rows = decode_messages(texts.files[bank])
        rows[DEX] = rows[NOVAREON]
        texts.files[bank] = encode_messages(key, rows)
    rom.setFileByName('a/0/2/7', texts.save())
    lists = ndspy.narc.NARC(rom.getFileByName('a/2/1/4'))
    for index, width in ((0, 4), (1, 4), (2, 1)):
        raw = bytearray(lists.files[index])
        raw[DEX * width:(DEX + 1) * width] = raw[NOVAREON * width:(NOVAREON + 1) * width]
        lists.files[index] = bytes(raw)
    cur = list(struct.unpack('<%dH' % (len(lists.files[11]) // 2), bytes(lists.files[11])))
    assert len(cur) == 1026 and cur[-1] == NOVAREON, (len(cur), cur[-1])
    cur[-1] = DEX
    lists.files[11] = struct.pack('<%dH' % len(cur), *cur)
    rom.setFileByName('a/2/1/4', lists.save())
    return dict(gap_test=hex(routine_gap), list_entries=len(cur))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
