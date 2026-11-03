"""Johto postgame, step 5b (trainers): every ordinary Johto trainer's level follows the Johto badges (owner 2026-11-02, JOHTO-POSTGAME-PLAN.md).

Rule: 0 Johto badges = the record's own (original HeartGold) level, 8 badges = level 100, in eight even steps: level = O + floor((100 - O) * min(badges, 8) / 8). Team sizes do not change.
 - Which trainers: record byte 2 (0 in every record, never read by the party builder) is set to 1 on the original HeartGold trainer records that are untouched by this project and are named (TrainerBattle
   command or shared-script actor 3000/5000 + id - 1) only on Johto maps (map header byte 20 bit 0 clear). Kanto trainers, the project's own records, the Gym Leaders (own tiers, step 5a) and ids that appear on
   both a Johto and a Kanto map are never flagged. Phone-rematch records are not named by any map and stay as they are (deferred);
 - the level routine of step 5a (overlay 129, called from the engine's trainer party builder in overlay 131) is rewritten in place: leader ids -> tier table; otherwise a flagged row -> the curve above;
   everything else keeps its level. The flag is read from the copy of the record inside BattleSetup (battler * 0x34 + 0x2A).
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step5b.py <in.nds> <out.nds> [original HeartGold .nds]"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import tower_scenes as ts
from build_rom import BASE
from mega_starter import Gap
from opening import events_decode
from viridian_tutorial import TABLE
import map_header_extension as ext
import johto_step5 as s5

ROUTINE_AT, ROUTINE_END = 0x023DED60, 0x023DEE14             # step 5a's routine and the free space behind it
IDS_AT, TIERS_AT = 0x023DED44, 0x023DED58                     # step 5a's leader id list (halfwords, 0-terminated) and tier table (8 bytes)
ORIGINAL_TRAINERS = 738                                       # HeartGold's own records are ids 0..737
FLAG_BYTE = 2


def referenced(rom):
    """{trainer id: set of map ids} for every TrainerBattle command (opcode 213) and shared trainer-script actor."""
    d = bytes(rom.loadArm9().sections[0].data)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    records = [d[TABLE + 24 * m:TABLE + 24 * m + 24] for m in range(540)] + [bytes(r) for r in ext.records(rom)]
    seen = {}
    for m, record in enumerate(records):
        sid, eid = struct.unpack_from('<H', record, 6)[0], struct.unpack_from('<H', record, 16)[0]
        ids = set()
        bank = bytes(scripts.files[sid])
        at = bank.find(b'\xd5\x00')
        while at >= 0:
            ids.add(struct.unpack_from('<H', bank, at + 2)[0])
            at = bank.find(b'\xd5\x00', at + 1)
        for actor in events_decode(events.files[eid])[1]:
            script = struct.unpack_from('<H', actor, 10)[0]
            for first in (3000, 5000):
                if first <= script < first + 1100:
                    ids.add(script - first + 1)
        for tid in ids:
            seen.setdefault(tid, set()).add((m, record[20] & 1))
    return seen


def johto_trainers(rom, original):
    book, src = ts.TrainerBook(rom), ts.TrainerBook(original)
    seen = referenced(rom)
    flagged = []
    for tid, where in sorted(seen.items()):
        if not 0 < tid < ORIGINAL_TRAINERS or tid in s5.LEADERS:
            continue
        if {kanto for _, kanto in where} != {0}:
            continue                                             # not on a Johto map only
        if book.trainers.files[tid] != src.trainers.files[tid] or book.parties.files[tid] != src.parties.files[tid]:
            continue                                             # rewritten by this project
        flagged.append(tid)
    return flagged


def mark(rom, flagged):
    book = ts.TrainerBook(rom)
    for tid in flagged:
        row = bytearray(book.trainers.files[tid])
        assert row[FLAG_BYTE] == 0
        row[FLAG_BYTE] = 1
        book.trainers.files[tid] = bytes(row)
    book.save()


def routine(rom):
    main = rom.loadArm9()
    save_pointer = struct.unpack_from('<I', main.sections[0].data, s5.SAVE_POINTER_AT)[0]
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    lo, hi = ROUTINE_AT - perm.ramAddress, ROUTINE_END - perm.ramAddress
    old = bytes(perm.data[lo:hi])
    assert old[:2] == bytes.fromhex('11b5'), 'step 5a routine not found'      # push {r0, r4, lr}
    assert struct.unpack_from('<%dH' % len(s5.LEADERS), perm.data, IDS_AT - perm.ramAddress) == tuple(s5.LEADERS), 'unexpected leader id list'
    assert bytes(perm.data[TIERS_AT - perm.ramAddress:TIERS_AT - perm.ramAddress + 8]) == bytes(s5.TIER_LEVELS), 'unexpected tier table'
    perm.data[lo:hi] = bytes(hi - lo)
    gap = Gap(perm, ROUTINE_AT, ROUTINE_END - ROUTINE_AT)
    entry = gap.code(f'''
push {{r0, r3, r4, lr}}
ldr r1, [r7, #0x50]
ldr r1, [r1, #0x18]
ldr r0, ids
scan:
ldrh r2, [r0]
cmp r2, #0
beq other
adds r0, #2
cmp r2, r1
bne scan
bl count
cmp r4, #7
ble ok
movs r4, #7
ok:
ldr r0, tiers
ldrb r3, [r0, r4]
b finish
other:
ldr r1, [r7, #0x4c]
ldr r2, [r7, #0x48]
movs r0, #0x34
muls r2, r0, r2
adds r1, r1, r2
adds r1, #0x2a
ldrb r1, [r1]
cmp r1, #0
beq finish
bl count
ldr r3, [sp, #4]
movs r1, #100
subs r1, r1, r3
muls r1, r4, r1
lsrs r1, r1, #3
adds r3, r3, r1
finish:
str r3, [r7, #0x1c]
adds r2, r3, #0
pop {{r0}}
add sp, #4
pop {{r4, pc}}
count:
push {{lr}}
ldr r0, save
ldr r0, [r0]
ldr r2, profile
blx r2
ldrb r0, [r0, #0x1a]
movs r4, #0
bits:
cmp r0, #0
beq counted
movs r1, #1
ands r1, r0
adds r4, r4, r1
lsrs r0, r0, #1
b bits
counted:
pop {{pc}}
.align 2
ids: .word {IDS_AT}
save: .word {save_pointer}
profile: .word {s5.PROFILE | 1}
tiers: .word {TIERS_AT}
''')
    assert entry == ROUTINE_AT, hex(entry)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(routine=hex(entry), gap_left=gap.end - gap.at)


def patch(rom, original):
    flagged = johto_trainers(rom, original)
    mark(rom, flagged)
    return dict(flagged=len(flagged), routine=routine(rom), first=flagged[:12])


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    original = ndspy.rom.NintendoDSRom.fromFile(sys.argv[3] if len(sys.argv) > 3 else str(BASE))
    print(patch(rom, original))
    rom.saveToFile(sys.argv[2])
