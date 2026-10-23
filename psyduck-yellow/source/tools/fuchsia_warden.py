"""Fuchsia: the Warden's HMs. HG's Kanto has no Safari Zone, so the Warden (map 481's NPC) gives HM04 Strength and HM03 Surf outright.

Yellow gives Strength for the Gold Teeth and Surf for the Safari Zone's secret house; both are deferred.
"""
import struct
from opening import Script, end
import yellow_text
from map_edit import MapEdit

MAP, GIVEN = 481, 0xA6C
HM_SURF, HM_STRENGTH = 422, 423


def patch(rom, source):
    m = lambda l: yellow_text.message(source, 'WardensHouse', l)
    edit = MapEdit(rom, MAP)

    def build(msg):
        thanks = msg(m('_WardensHouseWardenThanksText'))
        got4 = msg('{PLAYER} received HM04!')
        first = '\r'.join(m('_WardensHouseWardenHM04ExplanationText').split('\r')[:2])
        explain = msg(first + '\rOh yes, the SECRET HOUSE in the SAFARI ZONE is closed. Take the SURF HM as a gift!')
        got3 = msg('{PLAYER} received HM03!')
        full = msg(m('_WardensHouseWardenHM04NoRoomText'))
        again = msg('WARDEN: Use STRENGTH to move boulders, and SURF to cross the water!')
        s = Script().emit(96).emit(104).emit(32, GIVEN).jump('again', 1)
        s.msg(thanks)
        s.emit(125, HM_STRENGTH, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
        s.msg(got4)
        s.emit(125, HM_SURF, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
        s.emit(30, GIVEN).msg(explain).msg(got3)
        end(s)
        s.label('full').msg(full)
        end(s)
        s.label('again').msg(again)
        end(s)
        return s.finish()

    entry = edit.script(build)
    npc = next(a for a in edit.groups[1] if struct.unpack_from('<H', a, 10)[0] == 1)
    i = edit.groups[1].index(npc)
    edit.groups[1][i] = bytearray(npc)
    struct.pack_into('<H', edit.groups[1][i], 10, entry)
    edit.save()
    return dict(map=MAP, entry=entry, flag=GIVEN, hms=[HM_STRENGTH, HM_SURF])
