"""Bulk Rare Candy fix (owner report 2026-11-03: the starters learn no moves while levelling, for about 50 versions).
Cause: bulk_rare_candy.py (prototype 0018) hooks the level read inside the game's own level-up move function at 0x02071534 (site 0x0207156C) so that, while a batch of candies is applied, the function sees each intermediate level in turn
and offers every move on the way. Later the expanded hg-engine build turned 0x02071534 into a trampoline (`ldr r3,[pc]; bx r3`) to its own rewritten function in overlay 129 (0x023DB270), so the old body, and the hook in it, is dead code:
the rewritten function reads the real level only, the batch loop finds nothing at the final level and every intermediate move is skipped (checked: Psyduck, Eevee, Bulbasaur and the starter Eevee all go 5 -> 15 with the same moves). One candy at a time was never affected.
Fix: the rewritten function reads the level with GetMonData(mon, 0xA1) at 0x023DB2A4 (`blx r6`, r6 = 0x0206E541). That call now goes to the bulk routine `learn_level` (ITCM 0x01FFD76C: in a batch it returns the scan level for the batch's Pokemon, otherwise it tail-calls
GetMonData with r2 = 0), reached with a 4-byte BL (distance 0x3DE536, inside the Thumb BL range). Room for the BL: the leading `movs r2, #0` is dropped (learn_level sets r2 itself) and the three instructions before the call move up one halfword.
 0x023DB29C  movs r1, #0xA1 ; str r0, [sp, #0xC] ; ldr r0, [sp] ; bl 0x01FFD76C ; (next, unchanged) lsls r6, r0, #0x18
No other code changes; no save change.
Usage (from yellow-heartgold, PYTHONPATH=tools): bulk_candy_fix.py <in.nds> <out.nds>"""
import sys
import ndspy.code
import ndspy.rom
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from prototype import thumb_bl

SITE = 0x023DB29C                       # first instruction of the level read in the rewritten function
LEARN_LEVEL = 0x01FFD76C                # bulk_rare_candy's learn_level routine (ITCM)
LEARN_LEVEL_HEAD = bytes.fromhex('064b1a68032a')   # ldr r3, [pc, #0x18]; ldr r2, [r3]; cmp r2, #3


def asm(source, addr):
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(source, addr=addr)[0])


def patch(rom):
    main = rom.loadArm9()
    itcm = main.sections[1]
    head = bytes(itcm.data[LEARN_LEVEL - itcm.ramAddress:LEARN_LEVEL - itcm.ramAddress + 6])
    assert head == LEARN_LEVEL_HEAD, ('the bulk learn_level routine is not at 0x01FFD76C', head.hex())
    ovs = rom.loadArm9Overlays()
    ov = ovs[129]
    ov.data = bytearray(ov.data)
    at = SITE - ov.ramAddress
    original = asm('movs r2, #0\nmovs r1, #0xa1\nstr r0, [sp, #0xc]\nldr r0, [sp]\nblx r6', SITE)
    assert bytes(ov.data[at:at + 10]) == original, ('unexpected code at the level read', bytes(ov.data[at:at + 10]).hex())
    assert bytes(ov.data[at + 10:at + 12]) == asm('lsls r6, r0, #0x18', SITE + 10), 'the instruction after the call is not lsls r6, r0, #0x18'
    new = asm('movs r1, #0xa1\nstr r0, [sp, #0xc]\nldr r0, [sp]', SITE) + thumb_bl(SITE + 6, LEARN_LEVEL)
    assert len(new) == 10
    ov.data[at:at + 10] = new
    rom.files[ov.fileID] = ov.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(site=hex(SITE), bl_target=hex(LEARN_LEVEL), bytes=new.hex())


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
