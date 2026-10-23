"""Route 22's second rival battle (Yellow's pre-League fight, Silph-style records and a sixth Blue-hook range).

After the first Route 22 scene is done and all eight Kanto badges are held, stepping onto the column just west of the
first trigger brings Blue back to the same spot for the Lv47 team. Optional: a loss heals the party, as with the other
Blue fights. Text is Yellow's.
"""
import struct
import ndspy.narc
import tower_scenes as ts
import blue_properties_shared as shared
import yellow_text
from map_edit import MapEdit
from opening import Script, end
from escort import music
from progression_cleanup import selected_battle, BLUE, R22_DONE, R22_HIDE

MAP, DONE, STATE = 27, 0xA63, 0x4177
SILPH_FIRST = 977                                      # first Silph rival record (tools/silph.py)
ROUTE_X = 981
KANTO_BADGES = range(8, 16)
RANGES = ((741, 9), (782, 3), (809, 3), (856, 3))


def hook(firsts):
    blocks = '\n'.join(f'''movs r0,r3
ldr r1,range{i}
subs r0,r0,r1
cmp r0,#{span}
bls yes''' for i, (_, span) in enumerate(firsts))
    words = '\n'.join(f'range{i}: .word {first}' for i, (first, _) in enumerate(firsts))
    return lambda target: shared.assemble(f'{blocks}\nmovs r0,#0\nbx lr\nyes:\nmovs r0,#1\nbx lr\n.align 2\n{words}\n', target)


def extend_hook(rom, silph_first, new_first):
    main = rom.loadArm9()
    itcm = main.sections[1]
    target = shared.OLD + ts.FREE_FROM
    at = target - itcm.ramAddress
    old = hook(RANGES + ((silph_first, 3),))(target)
    assert bytes(itcm.data[at:at + len(old)]) == old, 'Blue helper is not the Silph-step helper'
    new = hook(RANGES + ((silph_first, 3), (new_first, 3)))(target)
    assert len(new) <= ts.OLD_WRAPPER_BYTES - ts.FREE_FROM
    itcm.data = bytearray(itcm.data)
    itcm.data[at:at + len(new)] = new
    rom.arm9 = main.save(compress=True)


def scene(trainers, base):
    s = Script().emit(32, R22_DONE).jump('go', 1)
    s.emit(2)
    s.label('go').emit(32, DONE).jump('end', 1)
    for badge in KANTO_BADGES:
        s.emit(294, badge, 0x800C).compare(0x800C, 0).jump('end', 1)
    s.emit(96).emit(105, 0x4000, 0x4001).emit(31, R22_HIDE).emit(100, BLUE)
    music(s, 1088)
    for z in range(265, 269):
        s.compare(0x4001, z).jump(f'approach{z}', 1)
    s.jump('approach266')
    for z in range(265, 269):
        s.label(f'approach{z}').movement(BLUE, f'walk{z}').emit(95).jump('battle')
    s.label('battle').movement(255, 'face_blue').emit(95).msg(base)
    selected_battle(s, trainers, 1, 'result')
    s.label('result').emit(220, 0x800C).compare(0x800C, 1).jump('won', 1).msg(base + 2).jump('outro')
    s.label('won').msg(base + 1)
    s.label('outro').msg(base + 3).movement(BLUE, 'leave').emit(95).emit(30, DONE).emit(30, R22_HIDE).emit(101, BLUE).emit(41, STATE, 1).emit(81, 0).emit(82)
    end(s)
    s.label('end').emit(2)
    for z in range(265, 269):
        walk = ([(12, 266 - z)] if z < 266 else [(13, z - 266)] if z > 266 else []) + [(15, 1), (3, 1)]
        s.moves(f'walk{z}', walk)
    return s.moves('face_blue', [(2, 1)]).moves('leave', [(13, 1), (15, 2), (13, 5)]).finish()


def patch(rom, source):
    yellow = ts.Yellow(source)
    book = ts.TrainerBook(rom)
    book.assert_unused((DONE, STATE))
    t = lambda label: yellow_text.message(source, 'Route22', label)
    lines = [t('_Route22RivalBeforeBattleText2'), t('_Route22Rival2DefeatedText'), t('_Route22Rival2VictoryText'), t('_Route22RivalAfterBattleText2')]
    pairs = yellow.rival_team(7)                       # Route 22, first of three Eevee-evolution variants (Jolteon)
    first, ids = len(book.trainers.files), {}
    for species in (54, 133):
        for gender, value in (('male', 1), ('female', 2)):
            team = [yellow.mon(n, lv) | dict(gender=0) for lv, n in pairs[:-1]]
            starter = yellow.mon('GOLDUCK' if species == 54 else pairs[-1][1], pairs[-1][0]) | dict(gender=value)
            if species == 54:
                starter['species'] = 55
            body = b''.join(struct.pack('<BB3H4H', 0, m['gender'], m['level'], m['species'], 0, *m['moves']) for m in team + [starter])
            ids[f'{species}_{gender}'] = book.new(742, body, [lines[0], lines[1], lines[3]], book.names[742], len(team) + 1)
    ids[54], ids[133] = ids['54_male'], ids['133_female']
    book.save()
    ts._cover_common(rom, max(ids.values()))
    extend_hook(rom, SILPH_FIRST, first)
    edit = MapEdit(rom, MAP)
    base = edit.message(lines[0])
    for line in lines[1:]:
        edit.message(line)
    entry = edit.script(lambda msg: scene(ids, base))
    edit.groups[3].append(struct.pack('<Hhh5H', entry, ROUTE_X, 265, 1, 4, 0, 0, STATE))
    edit.save()
    return dict(map=MAP, entry=entry, rival_first=first, team=pairs, flag=DONE, state=STATE)
