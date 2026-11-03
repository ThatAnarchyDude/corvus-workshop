"""Johto postgame, step 6b: scripted Johto wild battles (script command 589: Sudowoodo, the legendary beasts and the other fixed encounters) follow the Gym Leader curve (owner 2026-11-02: "Same as the Gym Leaders"):
level = 60 + 5 * Johto badges held (60 with none, 95 with seven, 100 with all eight). Every original level of these battles is 50 or lower, so the curve never lowers one.
Done in script data, no engine change: command 589 takes its level as a script variable when the argument is >= 0x4000, so each site `589 species level flag` (7 bytes, between `SetFlag 164` and `ClearFlag 164`) is replaced by a jump (6 bytes) to a routine
appended at the end of the script bank file. The routine counts the Johto badges (CheckBadge 0-7, command 294) into 0x8005, sets 0x8004 = 60 + 5 * count (SetVar 60, then AddVar 0x8005 five times), runs the same battle command with
level = variable 0x8004 and the original species and flag byte, and jumps back to the byte after the site. Sites whose level is already variable 0x8004 (Lugia / Ho-Oh style scripts) get the same routine. Scratch variables 0x8004-0x8006 are the
ones the Kanto Mart script uses.
Sites (bank: map, species, level): 21 (340) and 104 (244) variable species/level; 24 and 216 Suicune 40; 58 (154) Lapras 20; 90 (248) Electrode 23 x3; 106 (462) Moltres 50; 133-135 (524-526) Groudon / Kyogre / Rayquaza 50;
243 (40) Sudowoodo 20 x2; 750 variable species, level 40; 938 (88) Gyarados 30. Kanto, Tower and project extension banks are not touched.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step6_scripted.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import command

SITES = {21: [263], 24: [798], 58: [107], 90: [1922, 2022, 2122], 104: [318], 106: [57], 133: [178], 134: [178], 135: [233], 216: [1798], 243: [329, 763], 750: [1247], 938: [988]}
BEFORE, AFTER = bytes.fromhex('1e00a400'), bytes.fromhex('1f00a400')      # SetFlag 164 ... ClearFlag 164
COUNT_VAR, LEVEL_VAR, SCRATCH = 0x8005, 0x8004, 0x800C
JUMP = 22


def routine(species, flag, back_to, at):
    """The appended routine, assembled to run at file offset `at`; ends with a jump to file offset `back_to`."""
    code = bytearray()
    code += command(41, COUNT_VAR, 0)
    for badge in range(8):                                    # Johto badges are indices 0-7
        code += command(294, badge, SCRATCH) + command(39, COUNT_VAR, SCRATCH)
    code += command(41, LEVEL_VAR, 60)
    for _ in range(5):
        code += command(39, LEVEL_VAR, COUNT_VAR)
    code += struct.pack('<HHHB', 589, species, LEVEL_VAR, flag)
    here = at + len(code)
    code += struct.pack('<Hi', JUMP, back_to - (here + 6))
    return bytes(code)


def patch(rom):
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    report = {}
    for bank, sites in SITES.items():
        data = bytearray(scripts.files[bank])
        data += bytes(-len(data) % 4)
        for site in sites:
            assert bytes(data[site - 4:site]) == BEFORE and bytes(data[site:site + 2]) == bytes([0x4d, 0x02]) and bytes(data[site + 7:site + 11]) == AFTER, (bank, site)
            species, level, flag = struct.unpack_from('<HHB', data, site + 2)
            at = len(data)
            data += routine(species, flag, site + 7, at)
            data += bytes(-len(data) % 4)
            data[site:site + 7] = struct.pack('<Hi', JUMP, at - (site + 6)) + b'\0'
            report.setdefault(bank, []).append((site, species, level, flag, at))
        scripts.files[bank] = bytes(data)
    rom.setFileByName('a/0/1/2', scripts.save())
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    for bank, rows in patch(rom).items():
        print(bank, rows)
    rom.saveToFile(sys.argv[2])
