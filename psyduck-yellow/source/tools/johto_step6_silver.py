"""Johto postgame, step 6a: Silver (the Johto rival) scales like a Gym Leader (owner 2026-11-02: "Scale like we've done with the Gym Leaders").
Every Silver record (HeartGold's class 23 'Rival' records that are Silver's, 24 ids: his starter-line variants of every battle) becomes a six-Pokemon roster [his starter's last stage, Weavile, Crobat, Magnezone, Gengar, Alakazam]
in the engine's real party layout, and its level follows the Gym Leader curve (owner correction 2026-11-02): 60 + 5 * Johto badges held = 60, 65, ... 95 for the eight leaders' fights (0..7 badges) and 100 once the eighth badge is held.
The Johto Elite Four, Lance and Red are level 100 (step 4) whatever the badges.
The level routine (overlay 129, in place at 0x023DED60, entered from the trainer party builder hook of step 5a) is rewritten to be driven only by the record's byte 2 instead of the 8-id leader table:
 0 = keep the record's own level, 1 = ordinary Johto trainer (level curve on the trainer's own level, step 5b), 2 = tier level 60 + 5 * badges, badges capped at 8 (Gym Leaders and Silver; the tier table at 0x023DED58 and its literal are no longer read).
The eight Gym Leader records get byte 2 = 2 (the id table at 0x023DED44 stays in the ROM but is no longer read). Kanto rival records 738-740 (Pikachu/Eevee/Togepi, class 23 too) are NOT Silver and are untouched.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step6_silver.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.rom
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
import johto_step5 as s5
import tower_scenes as ts

ROUTINE = 0x023DED60                                          # the level routine (step 5b rewrote it in place); it ends before the badge counter at 0x023DEDB0
COUNTER = 0x023DEDB0
OLD_FIRST = bytes.fromhex('19b5')                             # push {r0, r3, r4, lr}
LEADER_IDS = [20, 21, 30, 31, 34, 33, 32, 35]
VARIANTS = {                                                  # starter's last stage -> the Silver record ids that carry that variant
    'Meganium': [1, 263, 264, 265, 285, 288, 489, 735],
    'Typhlosion': [2, 266, 267, 268, 286, 289, 490, 736],
    'Feraligatr': [3, 269, 270, 271, 272, 287, 491, 737],
}
STARTER = {
    'Meganium': ('Meganium', 'Leftovers', ('Giga Drain', 'Earthquake', 'Synthesis', 'Sleep Powder')),
    'Typhlosion': ('Typhlosion', 'Leftovers', ('Flamethrower', 'Earthquake', 'Thunder Punch', 'Quick Attack')),
    'Feraligatr': ('Feraligatr', 'Leftovers', ('Surf', 'Earthquake', 'Ice Beam', 'Crunch')),
}
COMMON = [
    ('Weavile', 'Leftovers', ('Ice Punch', 'Night Slash', 'Brick Break', 'Aerial Ace')),
    ('Crobat', 'Leftovers', ('Air Slash', 'Cross Poison', 'Toxic', 'Roost')),
    ('Magnezone', 'Leftovers', ('Thunderbolt', 'Flash Cannon', 'Thunder Wave', 'Zap Cannon')),
    ('Gengar', 'Leftovers', ('Shadow Ball', 'Sludge Bomb', 'Thunderbolt', 'Hypnosis')),
    ('Alakazam', 'Leftovers', ('Psychic', 'Shadow Ball', 'Focus Blast', 'Recover')),
]
ASM = '''
push {r0, r3, r4, lr}
ldr r1, [r7, #0x4c]
ldr r2, [r7, #0x48]
movs r0, #0x34
muls r2, r0, r2
adds r1, r1, r2
adds r1, #0x2a
ldrb r1, [r1]
cmp r1, #0
beq store
cmp r1, #2
beq tier
bl 0x23dedb0
ldr r3, [sp, #4]
movs r1, #0x64
subs r1, r1, r3
muls r1, r4, r1
lsrs r1, r1, #3
adds r3, r3, r1
b store
tier:
bl 0x23dedb0
cmp r4, #8
ble ok
movs r4, #8
ok:
movs r3, #5
muls r3, r4, r3
adds r3, #0x3c
store:
str r3, [r7, #0x1c]
adds r2, r3, #0
pop {r0}
add sp, #4
pop {r4, pc}
'''


def records(rom):
    species, moves, items = s5.lookup(rom)
    book = ts.TrainerBook(rom)
    done = []
    for variant, ids in VARIANTS.items():
        team = [STARTER[variant]] + COMMON
        entries = b''.join(struct.pack('<BBHH', s5.IV, 0, s5.BASE_LEVEL, species[mon.lower()]) + struct.pack('<H', items[item.lower()])
                           + struct.pack('<4H', *(moves[m.lower()] for m in four)) + struct.pack('<H', 0) for mon, item, four in team)
        for tid in ids:
            row = bytearray(book.trainers.files[tid])
            assert row[1] == 23, (tid, row[1])                    # class 'Rival'
            row[0], row[2], row[3] = 3, 2, len(team)
            book.trainers.files[tid] = bytes(row)
            book.parties.files[tid] = entries
            done.append(tid)
    for tid in LEADER_IDS:
        row = bytearray(book.trainers.files[tid])
        row[2] = 2
        book.trainers.files[tid] = bytes(row)
    book.save()
    return sorted(done)


def routine(rom):
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    at = ROUTINE - perm.ramAddress
    assert bytes(perm.data[at:at + 2]) == OLD_FIRST, bytes(perm.data[at:at + 2]).hex()
    code = bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(ASM, addr=ROUTINE)[0])
    assert ROUTINE + len(code) <= COUNTER, hex(ROUTINE + len(code))
    pad = (COUNTER - ROUTINE - len(code)) // 2
    perm.data[at:at + COUNTER - ROUTINE] = code + bytes.fromhex('c046') * pad
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    listing = [f'{i.address:x}: {i.mnemonic} {i.op_str}' for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(code, ROUTINE)]
    return dict(size=len(code), spare=COUNTER - ROUTINE - len(code))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(routine(rom))
    print('silver records:', records(rom))
    rom.saveToFile(sys.argv[2])
