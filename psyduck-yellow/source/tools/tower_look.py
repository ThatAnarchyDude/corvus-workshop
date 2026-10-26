"""Pokemon Tower gets its own look: a recoloured copy of the Bell Tower interior texture bank (dark violet stone instead of brown wood).

The seven Tower floors (extension maps 540-546) are Bell Tower clones that point at area record 77 (map texture bank a/0/4/4 file 77). This adds a copy of that bank with every
palette tinted, a new area record that uses it, and points only the seven Tower records at it. The real Bell Tower (native maps 332-338) keeps the original bank.
Shapes, collision and scripts are unchanged; only palette colours differ.
NOT done: the building pieces (pillars, lamps, stairs; a/0/7/0 file 75) keep their brown/orange colours: a new a/0/7/0 index black-screens the map even as an unmodified copy.

Usage: tower_look.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import ndspy.texture
import map_header_extension as ext

OLD_AREA, FIRST, LAST = 0x4D, 540, 546
TINT = (0.82, 0.72, 1.0)       # violet-leaning grey, per channel multiplier on luminance
GAIN, LIFT = 0.80, 2          # darker overall, small lift (0-31 scale) so the blacks stay readable
KEEP = ('h_kage_pl',)          # the shadow texture stays as is


def tint(colors):
    out = []
    for c in colors:
        r, g, b = c.r, c.g, c.b
        y = 0.30 * r + 0.59 * g + 0.11 * b
        # keep a little of the original hue so grass-green or window-yellow bits do not turn to mud
        nr, ng, nb = (max(0, min(31, int((GAIN * y * t + LIFT) * 0.8 + o * 0.2 * GAIN))) for t, o in zip(TINT, (r, g, b)))
        out.append(type(c)(nr, ng, nb, c.a))
    return out


def patch(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    areas = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/2')])
    banks = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/4')])
    area = bytearray(areas.files[OLD_AREA])
    old_bank = struct.unpack_from('<H', area, 2)[0]
    tex = ndspy.texture.NSBTX(banks.files[old_bank])
    changed = []
    for name, pal in tex.palettes:
        if name in KEEP:
            continue
        pal.colors = tint(pal.colors)
        changed.append(name)
    new_bank = len(banks.files)
    banks.files.append(bytes(tex.save()))
    struct.pack_into('<H', area, 2, new_bank)
    new_area = len(areas.files)
    assert new_area < 256
    areas.files.append(bytes(area))
    rom.files[rom.filenames.idOf('a/0/4/2')] = areas.save()
    rom.files[rom.filenames.idOf('a/0/4/4')] = banks.save()
    ovs = rom.loadArm9Overlays({ext.OV})
    o = ovs[ext.OV]
    data = bytearray(o.data)
    start = ext.table_address(rom) - o.ramAddress
    for m in range(FIRST, LAST + 1):
        at = start + 24 * (m - ext.NATIVE_COUNT) + 1
        assert data[at] == OLD_AREA, (m, data[at])
        data[at] = new_area
    o.data = data
    rom.files[o.fileID] = o.save(compress=False)
    return dict(new_bank=new_bank, new_area=new_area, palettes=changed)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
