"""Campaign-loop area builds. Usage: campaign_build.py <area> <source.nds> <output.nds> <yellow-reference-dir>."""
import sys
import ndspy.rom
import yellow_route_reference as yellow


def tower(rom, source):
    import pokemon_tower as t
    refs = {f: yellow.reference(source, name, t.TRAINER_COUNTS[f], extra_roles={}) for f, name in t.TRAINER_FLOORS.items()}
    return t.patch(rom, refs, source)


def celadon(rom, source):
    import celadon_gym
    return celadon_gym.patch(rom, source)


def hideout(rom, source):
    import rocket_hideout
    return rocket_hideout.patch(rom, source)


def routes(rom, source):
    import route_progression
    return [route_progression.patch(rom, source, n) for n in (8, 11, 12, 13, 14, 15, 16, 17, 18)]


def snorlax(rom, source):
    import snorlax as s
    return s.patch(rom, source)


def fuchsia(rom, source):
    import fuchsia_gym
    return fuchsia_gym.patch(rom, source)


def warden(rom, source):
    import fuchsia_warden
    return fuchsia_warden.patch(rom, source)


def gyms(rom, source):
    import kanto_gyms
    return kanto_gyms.patch(rom, source)


def league(rom, source):
    import league as l
    return l.patch(rom, source)


def silph(rom, source):
    import silph as s
    return s.patch(rom, source)


def victory_road(rom, source):
    import victory_road as v
    return v.patch(rom, source)


def gate299(rom, source):
    import gate299 as g
    return g.patch(rom, source)


def route22_rival(rom, source):
    import route22_rival as r
    return r.patch(rom, source)


AREAS = {'route22_rival': route22_rival, 'gate299': gate299, 'victory_road': victory_road, 'silph': silph, 'league': league, 'gyms': gyms, 'warden': warden, 'fuchsia': fuchsia, 'tower': tower, 'celadon': celadon, 'hideout': hideout, 'routes': routes, 'snorlax': snorlax}

if __name__ == '__main__':
    area, src, dst, ref = sys.argv[1:5]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    report = AREAS[area](rom, ref)
    rom.saveToFile(dst)
    print(report)
