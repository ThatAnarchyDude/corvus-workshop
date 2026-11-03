"""Mt. Moon B2F (map 557): the Super Nerd and the Jessie/James ambush can no longer be walked around, the fossils really block their corridor, and Jessie and James walk up to the player.
Owner report 2026-11-02: both events are REQUIRED to get through Mt. Moon the first time, but the 2x scale left gaps (Yellow's 1-step corridors are 4 tiles wide here): the Super Nerd could be bypassed by walking behind him,
the fossils could be walked around or between, and the ambush (a trigger that only fired inside the fossil room once a fossil was taken, with Jessie and James standing still the whole time) could be skipped.
The B2F layout (tiles, ROM 0150): the fossil room (x 26-41, z 24-29) is entered only by the south corridor (x 32-35, z 30-31) and left only by the north corridor (x 32-35, z 22-23) to an enclosed area; the exit to the
ladder (up to B1F and Route 4) is reached only through the 2-wide corridor x 14-15, z 22-23 at that area's west end. So every route to Cerulean passes all three places, like Yellow's.
Changes (events, script bank and map-load script only; no collision or model change):
 - Super Nerd: a trigger over the whole south corridor (4 x 2 tiles) fires his fight while STAGE is 0; he faces south.
 - Fossils: each fossil is a pair of sprites; together they fill the 4-wide north corridor at z 23 (Dome x 32-33, Helix x 34-35). Taking one hides both of its sprites and the other pair (the Super Nerd takes it), as before.
 - Ambush: Jessie and James are hidden when the floor loads (map-load script sets their hide flags); a trigger over the 2x2 corridor to the ladder fires it when STAGE is 2 (a fossil was taken): they appear at the east end of the
   area, walk up to the player (Jessie down column 14, James down column 15) and then the old dialogue and battle run.
Usage: mtmoon_blockade.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from escort import music
from mtmoon_yellow import CHOICE, STAGE, STORY, trainer_arg
from opening import Script, command, end, events_decode, events_encode, script_bank
from parcel_quest import split_bank

B2F = 557
HIDE_J, HIDE_M, JESSIE, JAMES = 0xB33, 0xB34, 30, 31
FOSSIL_SECOND = {22: 32, 23: 33}                              # new actor ids: the second sprite of each fossil
FOSSIL_TILES = {22: [(32, 23), (33, 23)], 23: [(34, 23), (35, 23)]}
BOSS_TRIGGER = (32, 30, 4, 2)                                 # x, z, w, h in tiles: the whole south corridor
AMBUSH_TRIGGER = (14, 22, 2, 2)                               # the corridor to the exit ladder
STEP_LEFT, STEP_DOWN = 14, 13                                 # movement codes (12 up, 13 down, 14 left, 15 right)
MSG = bytes.fromhex('be0000bf00012d00')                       # emit(190, 0) emit(191, 1) emit(45): a Script.msg() call; the next byte is the message index


def first_message(script):
    i = bytes(script).find(MSG)
    assert i >= 0
    return script[i + len(MSG)]


def fossil_script(f, other, msg, mine, theirs):
    """mtmoon_yellow.fossil_script, removing both sprites of each fossil."""
    s = Script().emit(96).compare(STAGE, 0).jump('unbeaten', 1)
    s.compare(STAGE, 1).jump('done', 5)
    s.msg(msg).emit(63, 0x800C).compare(0x800C, 0).jump('done', 5)
    s.emit(125, f['item'], 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    s.emit(41, CHOICE, f['choice']).emit(41, STAGE, 2)
    s.emit(30, f['hide_flag'])
    for actor in mine:
        s.emit(101, actor)
    s.emit(78, 1185).msg(msg + 1).emit(79)
    s.msg(msg + 2)
    s.emit(30, other['hide_flag'])
    for actor in theirs:
        s.emit(101, actor)
    end(s)
    s.label('full').msg(msg + 3)
    end(s)
    s.label('unbeaten').msg(msg + 4)
    s.label('done')
    end(s)
    return s.finish()


def ambush_script(trainer, msg):
    s = Script().compare(STAGE, 2).jump('done', 5).emit(96)
    music(s, 1112)
    s.emit(31, HIDE_J).emit(100, JESSIE).emit(31, HIDE_M).emit(100, JAMES)
    s.movement(JESSIE, 'jessie_in').movement(JAMES, 'james_in').emit(95)
    s.msg(msg).msg(msg + 1)
    s.emit(213, trainer, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, trainer)
    music(s, 1112).msg(msg + 2).msg(msg + 3)
    s.emit(30, HIDE_M).emit(101, JAMES).emit(30, HIDE_J).emit(101, JESSIE)
    s.emit(41, STAGE, 3).emit(81, 0).emit(82)
    end(s)
    s.label('lost').emit(219)
    end(s)
    s.label('done').emit(2)
    s.moves('jessie_in', [(STEP_LEFT, 12), (STEP_DOWN, 2)])        # (26, 19) -> (14, 19) -> (14, 21)
    s.moves('james_in', [(STEP_LEFT, 11), (STEP_DOWN, 1)])         # (26, 20) -> (15, 20) -> (15, 21)
    return s.finish()


def patch(rom):
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    rec = ext.records(rom)[B2F - ext.NATIVE_COUNT]
    sid, iid = struct.unpack_from('<2H', rec, 6)
    eid = struct.unpack_from('<H', rec, 16)[0]
    g = events_decode(bytes(events.files[eid]))
    bank = split_bank(bytes(scripts.files[sid]))
    assert bytes(scripts.files[iid]) == bytes(4), 'B2F already has a map-load script'
    triggers = [struct.unpack_from('<Hhh5H', t, 0) for t in g[3]]
    boss = next(t for t in triggers if t[6] == 0)
    amb = next(t for t in triggers if t[6] == 2)
    assert len(triggers) == 2
    boss_id, amb_id = boss[0], amb[0]
    # ---- actors
    actors = {struct.unpack_from('<H', a, 0)[0]: bytearray(a) for a in g[1]}
    for aid in (21, 22, 23, JESSIE, JAMES):
        assert aid in actors, aid
    assert not set(FOSSIL_SECOND.values()) & set(actors)
    struct.pack_into('<h', actors[21], 12, 1)                  # the Super Nerd faces the player coming up the south corridor
    fossils = STORY['fossils']
    new_scripts = {}
    pair = {f['actor']: [f['actor'], FOSSIL_SECOND[f['actor']]] for f in fossils}
    for f, other in zip(fossils, fossils[::-1]):
        a = actors[f['actor']]
        sc = struct.unpack_from('<H', a, 10)[0]
        new_scripts[sc] = fossil_script(f, other, first_message(bank[sc - 1]), pair[f['actor']], pair[other['actor']])
        second = bytearray(a)
        struct.pack_into('<H', second, 0, FOSSIL_SECOND[f['actor']])
        for actor, (x, z) in zip((a, second), FOSSIL_TILES[f['actor']]):
            struct.pack_into('<2H', actor, 24, x, z)
        actors[FOSSIL_SECOND[f['actor']]] = second
    jj_trainer = trainer_arg(bank[amb_id - 1])
    new_scripts[amb_id] = ambush_script(jj_trainer, first_message(bank[amb_id - 1]))
    for sc, code in new_scripts.items():
        bank[sc - 1] = code
    bank.append(command(30, HIDE_J) + command(30, HIDE_M) + command(2))      # map-load script: Jessie and James stay hidden until the ambush
    init_id = len(bank)
    order = [struct.unpack_from('<H', a, 0)[0] for a in g[1]]
    g[1] = [bytes(actors[k]) for k in order] + [bytes(actors[k]) for k in FOSSIL_SECOND.values()]
    # ---- triggers
    g[3] = [struct.pack('<Hhh5H', boss_id, *BOSS_TRIGGER, 0, 0, STAGE), struct.pack('<Hhh5H', amb_id, *AMBUSH_TRIGGER, 0, 2, STAGE)]
    events.files[eid] = events_encode(g)
    scripts.files[sid] = script_bank(bank)
    scripts.files[iid] = struct.pack('<BHHB', 2, init_id, 0, 0) + b'\0\0'
    rom.setFileByName('a/0/3/2', events.save())
    rom.setFileByName('a/0/1/2', scripts.save())
    return dict(boss_script=boss_id, ambush_script=amb_id, trainer=jj_trainer, init_script=init_id, actors=sorted(actors), fossil_scripts=sorted(k for k in new_scripts if k not in (amb_id,)))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
