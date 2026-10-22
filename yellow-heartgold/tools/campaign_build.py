"""Campaign-loop area builds. Usage: campaign_build.py <area> <source.nds> <output.nds> <yellow-reference-dir>."""
import sys
import ndspy.rom
import yellow_route_reference as yellow


def tower(rom, source):
    import pokemon_tower as t
    refs = {f: yellow.reference(source, name, t.TRAINER_COUNTS[f], extra_roles={}) for f, name in t.TRAINER_FLOORS.items()}
    return t.patch(rom, refs)


AREAS = {'tower': tower}

if __name__ == '__main__':
    area, src, dst, ref = sys.argv[1:5]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    report = AREAS[area](rom, ref)
    rom.saveToFile(dst)
    print(report)
