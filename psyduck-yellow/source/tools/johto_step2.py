"""Johto postgame, step 2a: Elm's call on the first Johto arrival (owner plan 2026-11-02, JOHTO-POSTGAME-PLAN.md).

johto_step1b.py sets the postgame variable to 5 when the player first arrives at Olivine's dock (map 330). Here a second frame row on that map (variable == 5) plays Elm's call as a
scripted ring-and-messages scene (the player already has the Pokegear from Mom), sets the Fly point of New Bark Town (pret FLAG_SYS_FLYPOINT_NEW_BARK = 0x9BB) and moves the variable to 6.
So Fly to New Bark Town is allowed only after the call. Later parts: the Town Map / Pokedex locks and Oak's upgrade scene.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step2.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.code
import ndspy.rom
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from map_edit import MapEdit
from opening import Script, end
from johto_step1b import OLIVINE_DOCK, add_frame_row

FLY_NEW_BARK = 0x9BB
MR_POKEMON = 143                           # Mr. Pokemon's house (object 1 = Oak, hidden by flag 405)
OAK_HIDE_FLAG = 405
OAK_UPGRADE_AT = 7                         # variable value that triggers Oak's upgrade scene (step 3 sets it after Mr. Pokemon's Mega Stone)
FANFARE_ITEM = 0x4A1
NAT_DEX_CMD = 477                          # script command (mode u8, result var u16): mode 1 = National Dex on, mode 2 = check; mode 0 is added here: National Dex off
BAD_MODE_CALL = 0x0204549C                 # `bl 0x0202551C` (the error call) of an unknown mode in that command's handler
GET_POKEDEX, POKEDEX_NAT_OFFSET = 0x0202A634, 0x337
ROUTINE_AT = 0x023DECC0                    # free space in overlay 129 (left over from the old Mega table's space)


def _bl(site, target):
    off = target - (site + 4)
    assert -0x400000 <= off < 0x400000
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xF800 | ((off >> 1) & 0x7FF))


def national_off(rom):
    """Mode 0 of the Pokedex command clears the National Dex byte (HeartGold has no way back, the vanilla game never needs one)."""
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    src = f"""
push {{lr}}
adds r0, r5, #0
adds r0, #0x80
ldr r0, [r0]
ldr r0, [r0, #0xc]
ldr r1, =0x{GET_POKEDEX | 1:X}
blx r1
movs r1, #0
ldr r2, =0x{POKEDEX_NAT_OFFSET:X}
strb r1, [r0, r2]
pop {{pc}}
"""
    raw = bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, addr=ROUTINE_AT)[0])
    at = ROUTINE_AT - perm.ramAddress
    assert not any(perm.data[at:at + len(raw) + 8]), 'the routine space is not free'
    perm.data[at:at + len(raw)] = raw
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    site = BAD_MODE_CALL - main.sections[0].ramAddress
    assert bytes(d[site:site + 4]) == _bl(BAD_MODE_CALL, 0x0202551C), 'the Pokedex command handler is not as expected'
    d[site:site + 4] = _bl(BAD_MODE_CALL, ROUTINE_AT | 1)
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return len(raw)


def patch(rom, var=0x4128):
    e = MapEdit(rom, OLIVINE_DOCK)

    def call(add):
        s = Script().emit(96)
        s.msg(add('... ... ...\rYour POKEGEAR is ringing!'))
        s.msg(add('ELM: Hello, {PLAYER}? This is PROF. ELM in NEW BARK TOWN.\rI heard from PROF. OAK that you are visiting JOHTO.'))
        s.msg(add('ELM: Could you stop by my LAB? I have something I would like you to see.'))
        s.msg(add('ELM: You can FLY to NEW BARK TOWN now. I will be waiting!'))
        s.emit(30, FLY_NEW_BARK).emit(NAT_DEX_CMD).data.append(0)
        s.emit(0x800C).emit(41, var, 6)
        return end(s).finish()
    add_frame_row(e, var, 5, e.script(call))
    e.save()
    # Oak's Pokedex upgrade at Mr. Pokemon's house (variable == OAK_UPGRADE_AT; step 3 sets it): National Dex on, variable 8
    e = MapEdit(rom, MR_POKEMON)

    def upgrade(add):
        s = Script().emit(96).emit(31, OAK_HIDE_FLAG).emit(100, 1)
        s.msg(add('OAK: Ah, {PLAYER}! I am visiting my old friend MR. POKEMON.\rYour POKEDEX only records KANTO. Let me see it.'))
        s.msg(add('OAK: ... ... ...\rThere! I have upgraded it.'))
        s.msg(add("{PLAYER}'s POKEDEX now records POKEMON from all regions!")).emit(78, FANFARE_ITEM).emit(79)
        s.emit(NAT_DEX_CMD).data.append(1)
        s.emit(0x800C).emit(41, var, OAK_UPGRADE_AT + 1)
        s.msg(add('OAK: Fill it well, {PLAYER}!')).emit(30, OAK_HIDE_FLAG).emit(101, 1)
        return end(s).finish()
    add_frame_row(e, var, OAK_UPGRADE_AT, e.script(upgrade))
    e.save()
    return dict(fly_flag=hex(FLY_NEW_BARK), routine_bytes=national_off(rom))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
