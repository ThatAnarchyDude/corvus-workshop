"""Route 22's League Reception Gate (map 299) lets Kanto trainers with all eight Kanto badges walk north to Victory Road.

The earlier cleanup blocked every arm. The east arm (from Route 22) is opened, the north arm checks the eight Kanto
badges (HG badge ids 8-15), the south arm (Route 26, Johto) stays closed with the "leads to Johto" line until the Hall of Fame (flag 0x964).
"""
import struct
from opening import Script, end
from map_edit import MapEdit

MAP, BOUNDARY, GAME_CLEAR = 299, 16747, 0x964
JOHTO_LINE, BADGE_LINE = 0, 1                    # indices in the gate's existing message bank
KANTO_BADGES = range(8, 16)


def badge_guard():
    s = Script().emit(96)
    for badge in KANTO_BADGES:
        s.emit(294, badge, 0x800C).compare(0x800C, 0).jump('block', 1)
    s.emit(97).emit(2)
    s.label('block').msg(BADGE_LINE).movement(255, 'back').emit(95)
    end(s)
    s.moves('back', [(13, 1)])
    return s.finish()


def south_guard():
    s = Script().emit(32, GAME_CLEAR).jump('open', 1)       # the Hall of Fame opens the way to Johto
    s.emit(96).msg(JOHTO_LINE).movement(255, 'back').emit(95)
    end(s)
    s.moves('back', [(13, 1)])
    s.label('open').emit(2)
    return s.finish()


def patch(rom, source=None):
    edit = MapEdit(rom, MAP)
    badge, south = edit.script(lambda msg: badge_guard()), edit.script(lambda msg: south_guard())
    triggers = []
    for t in edit.groups[3]:
        script, x, z = struct.unpack_from('<Hhh', t)
        if (x, z) == (15, 8):
            continue                                     # east arm: open
        if (x, z) == (11, 17):
            t = struct.pack('<Hhh5H', south, x, z, *struct.unpack_from('<5H', t, 6))
        triggers.append(t)
    triggers.append(struct.pack('<Hhh5H', badge, 9, 4, 5, 1, 0, 0, BOUNDARY))
    edit.groups[3] = triggers
    edit.save()
    return dict(map=MAP, badge_script=badge, south_script=south, badges=list(KANTO_BADGES))
