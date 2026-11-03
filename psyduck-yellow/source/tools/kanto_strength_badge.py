"""Either the Plain Badge or Yellow's Rainbow Badge unlocks Strength (found 2026-10-28: a Kanto-only player could never use Strength: the Warden's HM04, Victory Road's boulder shortcuts).

Problem: HG gates Strength on the Johto Plain Badge (badge 2) in two places, and a Kanto-only player never owns it: the party menu's field-move check answers "This can't be used until
a new Badge is obtained." (seen live with the five Kanto badges and a level 29 Machop), and the shared boulder script (std script 10001, one CheckBadge 2 call) sends such a player
to the "a POKEMON may be able to push it aside" text. Every Strength boulder is therefore unusable (Victory Road's boulder shortcuts; the Kanto path itself never needs Strength). Surf (Soul) and Cut (Cascade)
already accept a Kanto badge; Strength was missed.
Fix, in the same shape as the Cut and Surf patches: (1) the party menu check (ARM9 0x020681DA, "bl TestBadge" with badge 2) calls a small routine in overlay 129 that tests badge 2 and, when
it is missing, the Rainbow Badge (11, Yellow's Strength badge); (2) the std script bank's one "CheckBadge 2" becomes a local call to a new helper script at the end of the bank that checks
badge 2 and then badge 11. Everything else (Plain alone still works, no badge is granted, other HM checks) is unchanged.

Usage: kanto_strength_badge.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from mega_starter import Gap
from opening import Script
from parcel_quest import append_bank

PLAIN, RAINBOW = 2, 11
MENU_SITE = 0x020681DA                 # movs r1,#2 (0x020681D8); bl TestBadge
TEST_BADGE = 0x02028F98
STD_BANK_FIRST_ID, STD_BANK_TEXT = 10000, 211      # dispatch triple (first id, script file, text bank); the file is whatever earlier tools left there


def _bl(site, target):
    off = (target - (site + 4)) >> 1
    assert target % 2 == 0 and -(1 << 21) <= off < (1 << 21), (hex(site), hex(target))
    return struct.pack('<HH', 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


def patch(rom):
    address, size = ext.reserve_code(rom, 24 * 2)                  # first: it rewrites overlay 129 (the header table moves up)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    hook = gap.code(f'''
push {{r4, lr}}
adds r4, r0, #0
ldr r3, test
blx r3
cmp r0, #0
bne done
adds r0, r4, #0
movs r1, #{RAINBOW}
ldr r3, test
blx r3
done:
pop {{r4, pc}}
.align 2
test: .word {TEST_BADGE | 1}
''')
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    base = section.ramAddress
    at = MENU_SITE - base
    assert bytes(section.data[at - 2:at]) == bytes((PLAIN, 0x21)), bytes(section.data[at - 2:at]).hex()       # movs r1,#2
    assert bytes(section.data[at:at + 4]) == _bl(MENU_SITE, TEST_BADGE), bytes(section.data[at:at + 4]).hex()
    section.data[at:at + 4] = _bl(MENU_SITE, hook)
    hits = [i for i in range(0, len(section.data) - 6, 2) if struct.unpack_from('<3H', section.data, i)[::2] == (STD_BANK_FIRST_ID, STD_BANK_TEXT)]
    assert len(hits) == 1, hits
    bank_file = struct.unpack_from('<H', section.data, hits[0] + 2)[0]
    rom.arm9 = main.save(compress=True)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    old = bytes(scripts.files[bank_file])
    needle = struct.pack('<3H', 294, PLAIN, 0x800C)                # CheckBadge 2 -> 0x800C
    assert old.count(needle) == 1, old.count(needle)
    helper = Script().emit(294, PLAIN, 0x800C).compare(0x800C, 0).jump('done', 5)
    helper.emit(294, RAINBOW, 0x800C).label('done').emit(27)
    bank, count = append_bank(old, [helper.finish()])
    call = old.index(needle) + 4                                   # +4: the bank's header grew by one entry
    target = count * 4 + 4 + struct.unpack_from('<I', bank, count * 4)[0]
    bank[call:call + 6] = struct.pack('<Hi', 26, target - call - 6)   # call the helper (it leaves the result in 0x800C), then the script's own compare runs
    scripts.files[bank_file] = bytes(bank)
    rom.setFileByName('a/0/1/2', scripts.save())
    return dict(menu_site=hex(MENU_SITE), hook=hex(hook), std_bank_file=bank_file, helper_script_index=count, accepted_badges=[PLAIN, RAINBOW], gap_left=gap.end - gap.at)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
