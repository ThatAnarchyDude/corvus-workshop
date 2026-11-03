"""Johto postgame, step 1a (owner plan 2026-11-02, JOHTO-POSTGAME-PLAN.md): the ending of the first Hall of Fame as in HeartGold, but waking in Pallet Town.

HeartGold's Hall of Fame script, credits and restart are untouched. After the credits the game continues in the New Bark Town player's house 2F (map 64); the Hall of Fame sets flag 0x964.
One new variable (POSTGAME) walks the player through the postgame start; every step is a level-script "frame" row (variable == value -> script):
 0 -> 1  map 64 (New Bark 2F): if 0x964 is set, fade out and warp to the Pallet bedroom (map 506) at (6,6);
 1 -> 2  map 506: wake-up text;
 2 -> 3  map 503 (Red's house 1F): Mom stops the player; if the Pokegear flag 0x9C is not set she gives the Pokegear (sets 0x9C);
 3 -> 4  map 49 (Pallet Town): Prof. Oak (the opening's town Oak, object 3) walks up, congratulates the player, hands over the S.S. Ticket and tells about the ferry from Vermilion.
POSTGAME == 4 means "ready for the ferry". The ferry, the closed ways into Johto and the Johto arrival are later parts of step 1/2.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step1.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.rom
from flag_alloc import used_flags
from map_edit import MapEdit
from opening import Script, end, HIDE_TOWN_OAK
from pokemon_tower import _frame_entry

NEW_BARK_2F, BEDROOM, HOUSE_1F, PALLET = 64, 506, 503, 49
GAME_CLEAR, POKEGEAR = 0x964, 0x9C
SS_TICKET = 456
WAKE_AT = (6, 6, 0)
FANFARE_ITEM = 0x4A1                                   # the jingle the Pokegear gift uses in HeartGold's Mom script


def free_variable(rom):
    seen = used_flags(rom)
    for v in range(0x4100, 0x4200):
        if v not in seen:
            return v
    raise RuntimeError('no free variable')


def add_frame_row(edit, var, value, script_id):
    header_id = struct.unpack_from('<H', edit.d, edit.at + 8)[0]
    edit.scripts.files[header_id] = _frame_entry(edit.scripts.files[header_id], var, value, script_id)


def patch(rom):
    var = free_variable(rom)
    report = dict(variable=hex(var))
    # 0 -> 1: New Bark Town player's house 2F (Johto) -> the Pallet bedroom, only after the Hall of Fame
    e = MapEdit(rom, NEW_BARK_2F)

    def redirect(add):
        s = Script().emit(32, GAME_CLEAR).jump('go', 1)
        s.emit(2)
        s.label('go').emit(41, var, 1).emit(96).emit(174, 6, 6, 0, 0).emit(175)
        s.emit(176, BEDROOM, 0, *WAKE_AT)
        s.emit(174, 6, 6, 1, 0).emit(175)
        return end(s).finish()
    add_frame_row(e, var, 0, e.script(redirect))
    e.save()
    # 1 -> 2: the Pallet bedroom
    e = MapEdit(rom, BEDROOM)

    def wake(add):
        s = Script().emit(96)
        s.msg(add('... You wake up in your room in Pallet Town. The POKEMON LEAGUE feels like a dream.'))
        s.emit(41, var, 2)
        return end(s).finish()
    add_frame_row(e, var, 1, e.script(wake))
    e.save()
    # 2 -> 3: Mom, downstairs
    e = MapEdit(rom, HOUSE_1F)

    def mom(add):
        s = Script().emit(96)
        s.msg(add('MOM: Welcome home, champion!\rI saw it all on TV.'))
        s.emit(32, POKEGEAR).jump('have', 1)
        s.msg(add('Wait, before you go out again... Take this with you. It is a POKEGEAR. That way I can reach you anywhere.'))
        s.emit(30, POKEGEAR).msg(add('{PLAYER} received the POKEGEAR!')).emit(78, FANFARE_ITEM).emit(79)
        s.label('have').msg(add('PROF. OAK is waiting outside. He says he has something for you.'))
        s.emit(41, var, 3)
        return end(s).finish()
    add_frame_row(e, var, 2, e.script(mom))
    e.save()
    # 3 -> 4: Prof. Oak in Pallet Town
    e = MapEdit(rom, PALLET)

    def oak(add):
        s = Script().emit(96).emit(105, 0x4000, 0x4001)
        s.emit(39, 0x4001, 2).emit(31, HIDE_TOWN_OAK).emit(100, 3)
        s.emit(339, 3, 0x4000, 0, 0x4001, 0)
        s.msg(add('OAK: {PLAYER}! Wait!')).movement(3, 'oak_approach').emit(95)
        s.movement(255, 'face_oak').emit(95)
        s.msg(add('OAK: Congratulations on entering the HALL OF FAME! That was a fine journey, from here to there.'))
        s.msg(add('OAK: But there is another region beyond the sea: JOHTO. The S.S. AQUA sails from VERMILION CITY to OLIVINE CITY.'))
        s.msg(add('OAK: Take this S.S. TICKET. It is your pass.'))
        s.emit(125, SS_TICKET, 1, 0x800C).msg(add('{PLAYER} received the S.S. TICKET!')).emit(78, FANFARE_ITEM).emit(79)
        s.msg(add('OAK: Go to the harbor in VERMILION CITY, and good luck!'))
        s.emit(41, var, 4).emit(30, HIDE_TOWN_OAK).emit(101, 3)
        end(s).moves('oak_approach', [(12, 1)]).moves('face_oak', [(1, 1)])
        return s.finish()
    add_frame_row(e, var, 3, e.script(oak))
    e.save()
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
