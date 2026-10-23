"""Make the starter species look and animate exactly like the ordinary Pokemon they copy.

Three per-species display tables were never extended for the starter species (Eevee 1561/1562, Psyduck 1563/1564, the
starter Eevee line 1565-1582), so the game read past their ends:
 - a/1/8/0 file 0 ("spriteoffsets": 89 bytes per species = front/back animation ids, sprite Y offset, shadow). It stopped at
   species 1534. It drives the summary-screen animation and placement, the ball entrance animation and the evolution scene.
   Species 1535-1560 (unused here) get Bulbasaur's entry, hg-engine's own placeholder; each starter species gets an exact
   copy of the entry of the ordinary species it copies (Mega Eevee/Mega Psyduck: the ordinary Eevee/Psyduck).
 - a/1/4/1 (overworld follower flags, 4 bytes per species) stopped at species 1560: same copies appended.
The Mega species are new Pokemon and keep their custom art (Mega Eevee's for every Eeveelution's Mega, Mega Psyduck's,
Novareon's); the non-Mega starter species already copy their originals' sprites.
Also the Mega species' shiny palettes (a/0/0/4, file 5 of each) were stored LZ10-compressed, which the game cannot read, so a
shiny Mega drew as a solid black silhouette; they are now stored raw like every other palette.

Usage: starter_display_fix.py <in.nds> <out.nds>
"""
import sys
import ndspy.lz10
import ndspy.narc
import ndspy.rom
from starter_eevee_line import BASES, FIRST

ENTRY = 89
OFFSETS_COUNT = 1535
EEVEE, PSYDUCK = 133, 54
STARTER_EEVEE, STARTER_PSYDUCK = FIRST - 4, FIRST - 2            # 1561, 1563
FOLLOW_COUNT = 1561
PLACEHOLDER = 1                                                  # Bulbasaur


def original_of(species):
    """The ordinary species whose display data a starter species copies."""
    if species in (STARTER_EEVEE, STARTER_EEVEE + 1):
        return EEVEE
    if species in (STARTER_PSYDUCK, STARTER_PSYDUCK + 1):
        return PSYDUCK
    assert FIRST <= species < FIRST + 2 * len(BASES), species
    return BASES[(species - FIRST) // 2]


def patch(rom):
    species = list(range(STARTER_EEVEE, FIRST + 2 * len(BASES)))
    offsets = ndspy.narc.NARC(rom.getFileByName('a/1/8/0'))
    table = bytearray(offsets.files[0])
    assert len(table) == OFFSETS_COUNT * ENTRY, len(table)
    table += table[PLACEHOLDER * ENTRY:(PLACEHOLDER + 1) * ENTRY] * (STARTER_EEVEE - OFFSETS_COUNT)
    for s in species:
        o = original_of(s)
        table += table[o * ENTRY:(o + 1) * ENTRY]
    assert len(table) == (species[-1] + 1) * ENTRY
    offsets.files[0] = bytes(table)
    rom.setFileByName('a/1/8/0', offsets.save())
    follow = ndspy.narc.NARC(rom.getFileByName('a/1/4/1'))
    assert len(follow.files) == FOLLOW_COUNT
    follow.files.extend(follow.files[original_of(s)] for s in species)
    rom.setFileByName('a/1/4/1', follow.save())
    gfx = ndspy.narc.NARC(rom.getFileByName('a/0/0/4'))
    fixed = []
    for s in species:
        for k in (4, 5):
            f = bytes(gfx.files[s * 6 + k])
            if f[0] == 0x10:                                     # LZ10 header instead of RLCN
                raw = ndspy.lz10.decompress(f)
                assert raw[:4] == b'RLCN', (s, k)
                gfx.files[s * 6 + k] = raw
                fixed.append((s, k))
            else:
                assert f[:4] == b'RLCN', (s, k)
    rom.setFileByName('a/0/0/4', gfx.save())
    return dict(offsets_entries=len(table) // ENTRY, follower_entries=len(follow.files), palettes_decompressed=fixed)


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
