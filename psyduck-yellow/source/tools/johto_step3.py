"""Johto postgame, step 3a: Elm's lab starter, the Mega Ring, Mr. Pokemon's Mega Stone and the Mega unlock (owner plan 2026-11-02, JOHTO-POSTGAME-PLAN.md).

After Elm's call (postgame variable 0x4128 == 6) Elm's talk script (map 61, object 0) offers the three Johto starters through a choice menu, gives the chosen one (level 5, as in HeartGold), the MEGA RING (item 696)
and sends the player to Mr. Pokemon (variable 7, a second variable remembers the choice). Entering Mr. Pokemon's house at 7 plays Oak's Pokedex upgrade (johto_step2.py, variable 8); then Mr. Pokemon's talk script
(map 143, object 0) at 8 hands over the Mega Stone of the chosen starter (Meganiumite / Feraligite), sets the Mega flag 0x9D6 (the engine's Mega Evolution switch) and moves the variable to 9.
Typhlosion has no Mega Stone yet (custom Mega Typhlosion is step 3c): Mr. Pokemon says so, and the Mega unlock still happens.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step3.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.rom
from flag_alloc import used_flags
from map_edit import MapEdit
from opening import Script, end

ELM_LAB, MR_POKEMON = 61, 143
STARTERS = (('CHIKORITA', 152), ('CYNDAQUIL', 155), ('TOTODILE', 158))
STONES = ((2563, 'MEGANIUMITE'), None, (2564, 'FERALIGITE'))   # (Typhlosion: custom stone in step 3c)
MEGA_RING, MEGA_FLAG = 696, 0x9D6
FANFARE_ITEM = 0x4A1
START_LEVEL = 5
NATIVE_FIRST_VISIT = 0x4107                  # Mr. Pokemon's house: HeartGold's own first-visit scene (Mystery Egg, Oak) fires while this is 0; Elm's script sets it to 1


def free_variable(rom, taken=()):
    seen = used_flags(rom) | set(taken)
    for v in range(0x4100, 0x4200):
        if v not in seen:
            return v
    raise RuntimeError('no free variable')


def set_talk_script(edit, obj, script_id):
    row = bytearray(edit.groups[1][obj])
    struct.pack_into('<H', row, 10, script_id)
    edit.groups[1][obj] = bytes(row)


def mr_pokemon_scene(rom, var, choice, stones=STONES):
    """Mr. Pokemon (map 143, object 0): the Mega Stone of the chosen starter, the Mega unlock (step 3c passes the Typhlosion stone too)."""
    e = MapEdit(rom, MR_POKEMON)

    def mr_pokemon(add):
        s = Script().emit(96).emit(104)
        s.compare(var, 8).jump('stone', 1).compare(var, 8).jump('later', 2)
        s.msg(add('MR. POKEMON: Ah, I am glad to see you!\rWe will talk when you are ready.'))
        end(s)
        s.label('later').msg(add('MR. POKEMON: MEGA EVOLUTION is a wonderful thing.\rTake good care of your partner!'))
        end(s)
        s.label('stone')
        s.msg(add('MR. POKEMON: PROF. ELM told me about you!\rYou have a MEGA RING.\rThen you need a MEGA STONE for your partner.'))
        for k, stone in enumerate(stones):
            s.compare(choice, k + 1).jump(f'stone{k}', 1)
        s.jump('flag')
        for k, stone in enumerate(stones):
            s.label(f'stone{k}')
            if stone is None:
                s.msg(add('MR. POKEMON: Hmm. There is no MEGA STONE for TYPHLOSION that I know of.\rI will keep looking. For now, MEGA EVOLUTION is yours to use!'))
                s.jump('flag')
                continue
            s.emit(125, stone[0], 1, 0x800C).compare(0x800C, 0).jump('full', 1)
            s.msg(add(f'{{PLAYER}} received {stone[1]}!')).emit(78, FANFARE_ITEM).emit(79)
            s.jump('flag')
        s.label('flag').emit(30, MEGA_FLAG)
        s.msg(add('MR. POKEMON: Hold the MEGA STONE and you can MEGA EVOLVE once per battle.'))
        s.emit(41, var, 9)
        end(s)
        s.label('full').msg(add('MR. POKEMON: Your BAG is full.\rCome back with a free spot.'))
        return end(s).finish()
    set_talk_script(e, 0, e.script(mr_pokemon))
    e.save()


def patch(rom, var=0x4128):
    choice = free_variable(rom, (var,))
    report = dict(choice_var=hex(choice))
    # Elm: the starter, the Mega Ring
    e = MapEdit(rom, ELM_LAB)

    def elm(add):
        s = Script().emit(96).emit(104)
        s.compare(var, 6).jump('early', 0).compare(var, 6).jump('first', 1)
        s.msg(add('ELM: MR. POKEMON lives past CHERRYGROVE CITY, on ROUTE 30.\rHe has MEGA STONES. Go and see him!'))
        end(s)
        s.label('early').msg(add('ELM: I am busy with my research right now.'))
        end(s)
        s.label('first')
        s.msg(add('ELM: {PLAYER}, thank you for coming!\rI have studied POKEMON that can MEGA EVOLVE.\rThis is a MEGA RING. It lets a POKEMON MEGA EVOLVE in battle.'))
        s.msg(add('ELM: And you should have a partner from JOHTO, too.\rChoose one of these three POKEMON!'))
        s.emit(332, 0x800C).compare(0x800C, 6).jump('full', 1)
        s.emit(746).emit(45).data.append(add('Which POKEMON will you choose?'))
        s.emit(750).data.extend(bytes([1, 1, 0, 1]))
        s.emit(0x800C)
        for k, (name, _) in enumerate(STARTERS):
            s.emit(751, add(name), 255, k)
        s.emit(752).emit(53).emit(747)
        for k, (name, species) in enumerate(STARTERS):
            s.compare(0x800C, k).jump(f'give{k}', 1)
        s.jump('first')
        for k, (name, species) in enumerate(STARTERS):
            s.label(f'give{k}')
            s.emit(41, choice, k + 1)
            s.emit(137, species, START_LEVEL, 0, 0, 0, 0x800C).compare(0x800C, 0).jump('full', 1)
            s.msg(add(f'{{PLAYER}} received {name}!')).emit(78, FANFARE_ITEM).emit(79)
            s.jump('ring')
        s.label('ring')
        s.emit(125, MEGA_RING, 1, 0x800C)
        s.msg(add('{PLAYER} received the MEGA RING!')).emit(78, FANFARE_ITEM).emit(79)
        s.msg(add('ELM: I have no MEGA STONES, sadly. MR. POKEMON does!\rHe lives past CHERRYGROVE CITY, on ROUTE 30.'))
        s.emit(41, var, 7).emit(41, NATIVE_FIRST_VISIT, 1)
        end(s)
        s.label('full').msg(add('ELM: Your party is full.\rCome back with a free spot.'))
        return end(s).finish()
    set_talk_script(e, 0, e.script(elm))
    e.save()
    mr_pokemon_scene(rom, var, choice)
    report['choice'] = 'chosen starter 1/2/3 in the variable'
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
