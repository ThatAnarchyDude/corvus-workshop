"""Real-3DS crash 2026-11-02 (owner photo, ROM 0138, entering Cerulean from Route 4): Data Abort, PC 0x0202407E, ADDR 0, r0 = 0.
The engine's 2D sprite animation lookup (ARM9 0x0202403C: r0 = animation data, r1 = sprite resource, r2 = sequence index) returns NULL when the index is >= the resource's count (here index 11, count 1) and
then executes `ldr r0, [r0]` at 0x0202407E. DeSmuME reads address 0 without complaint (ITCM mirror); the 3DS under nds-bootstrap aborts.
Patch: the 4 bytes `ldr r0,[r0]; movs r5,#0` at 0x0202407E become `bl stub` (stub in the free tail of the step-5c getter chunk of overlay 129).
 mode 'guard': stub = `cmp r0,#0; beq skip; ldr r0,[r0]; skip: movs r5,#0; bx lr` (a NULL pointer reads as 0)
 mode 'hang' : TEST ONLY for the emulator, the stub spins forever on NULL (a frozen emulator proves the NULL path runs in the emulator too)
Usage (from yellow-heartgold, PYTHONPATH=tools): null_guard.py <in.nds> <out.nds> [guard|hang]"""
import sys
import ndspy.code
import ndspy.rom
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from mega_starter import Gap

SITE = 0x0202407E
SITE_BYTES = bytes.fromhex('00680025')                        # ldr r0,[r0]; movs r5,#0
CHUNK_A = (0x023DEBA0, 0x023DEBFC)                            # step 5c's getter chunk up to its K byte


def patch(rom, mode):
    main = rom.loadArm9()
    arm9 = main.sections[0]
    arm9.data = bytearray(arm9.data)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    at = SITE - arm9.ramAddress
    assert bytes(arm9.data[at:at + 4]) == SITE_BYTES, bytes(arm9.data[at:at + 4]).hex()
    lo, hi = (a - perm.ramAddress for a in CHUNK_A)
    used = max(i for i in range(lo, hi) if perm.data[i]) + 1   # first byte after the getter's code
    start = (perm.ramAddress + used + 3) & ~3
    gap = Gap(perm, start, CHUNK_A[1] - start)
    if mode == 'guard':
        stub = gap.code('''
cmp r0, #0
beq skip
ldr r0, [r0]
skip:
movs r5, #0
bx lr
''')
    else:
        stub = gap.code('''
cmp r0, #0
bne ok
hang:
b hang
ok:
ldr r0, [r0]
movs r5, #0
bx lr
''')
    call = bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(f'bl {stub}', addr=SITE)[0])
    assert len(call) == 4, call.hex()
    arm9.data[at:at + 4] = call
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return dict(mode=mode, stub=hex(stub), call=call.hex(), left=gap.end - gap.at)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3] if len(sys.argv) > 3 else 'guard'))
    rom.saveToFile(sys.argv[2])
