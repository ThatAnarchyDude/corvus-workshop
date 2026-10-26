"""Pokedex registration of species 700 and above no longer corrupts other entries' flags.

Problem (found by the live Pokedex pass, ROM 0104): Pokedex_SetLanguage (ARM9 0x02029BE0) stores one language byte per species at struct+0x144+species. That array was sized
for 493 species; with ids up to 1075 it runs over the 0x400-byte caught array (harmless, those bytes hold species above 2500) and then over the SEEN array at struct+0x400:
registering species 700+n overwrote seen-bytes n (species 8n+1..8n+8: Sylveon 700 set byte 0 to 2, wiping the seen bits of Bulbasaur, Venusaur... and marking Ivysaur seen),
and species 956+ reached the gender arrays at struct+0x500. The language bytes are not used by the Pokedex screens, so registering them is skipped for species >= 700.
Fix: the call `bl GetLanguageIndex` at 0x02029BE8 goes through a new routine that returns 6 (the value the function already treats as "nothing to store") for species >= 700.

Usage: dex_lang_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.code
import ndspy.rom
import map_header_extension as ext
from dex_fix import bl
from mega_starter import Gap

SITE, TARGET = 0x02029BE8, 0x02091278
LIMIT = 700                       # struct + 0x144 + 700 = 0x400, the start of the seen array
RESERVE = 24


def patch(rom):
    address, size = ext.reserve_code(rom, RESERVE)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    routine = gap.code(f'''push {{lr}}
ldr r3, lang
blx r3
ldr r1, limit
cmp r4, r1
blo done
movs r0, #6
done:
pop {{pc}}
.align 2
lang: .word {TARGET | 1}
limit: .word {LIMIT}
''')
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    at = SITE - section.ramAddress
    assert bytes(section.data[at:at + 4]) == bl(SITE, TARGET), bytes(section.data[at:at + 4]).hex()
    section.data[at:at + 4] = bl(SITE, routine)
    rom.arm9 = main.save(compress=True)
    return dict(routine=hex(routine), gap_used=gap.at - gap.start)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
