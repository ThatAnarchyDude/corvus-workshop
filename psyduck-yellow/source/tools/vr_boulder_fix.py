"""Victory Road's puzzle boulders become real Strength boulders (found 2026-10-28 while testing the Strength badge fix; the boulder puzzles could not work).

Problem: victoryroad_yellow.py built the puzzle from sprite 85 with script 10001 ("HG's own Strength boulders") and the barrier rocks from sprite 84. Live, it is the other way round: sprite 85 is the
brown, crumbling Rock Smash rock (script 10001 answers "It's a rugged rock, but a Pokemon may be able to smash it") and sprite 84 is the round grey Strength boulder (script 10002, "a big boulder ...
Would you like to use Strength?"). The engine's party menu only offers Strength when the player faces a sprite-84 object (a Rock Smash rock gives "You can't use that here."), so the three or four
"boulders" on each floor could not be pushed and the barriers could never open, while the barrier rocks (grey boulders) were pushable themselves. (The puzzles are optional shortcuts:
the Indigo exit is reachable from the Route 23 entry with every barrier closed.)
Fix: on maps 580-582 every sprite-85 actor with script 10001 becomes a sprite-84 actor with script 10002 (the puzzle boulder, same object id, position and flags), and every sprite-84 actor with script 0
(the barrier rocks, hide flags unchanged) becomes sprite 85 with script 0 (a Rock Smash rock nobody can smash or push). The switch triggers and scripts work on object ids and tiles, so they are unchanged.

Usage: vr_boulder_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode, events_encode

FLOORS = {580: (3, 2), 581: (3, 8), 582: (4, 2)}               # map: (puzzle boulders, barrier rocks) before the fix
ROCK_SMASH_SPRITE, STRENGTH_SPRITE = 85, 84
ROCK_SMASH_SCRIPT, STRENGTH_SCRIPT = 10001, 10002


def patch(rom):
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    records = ext.records(rom)
    report = {}
    for mid, expected in FLOORS.items():
        eid = struct.unpack_from('<H', records[mid - ext.NATIVE_COUNT], 16)[0]
        groups = events_decode(events.files[eid])
        boulders = rocks = 0
        actors = []
        for raw in groups[1]:
            a = bytearray(raw)
            sprite, script = struct.unpack_from('<H', a, 2)[0], struct.unpack_from('<H', a, 10)[0]
            if (sprite, script) == (ROCK_SMASH_SPRITE, ROCK_SMASH_SCRIPT):
                struct.pack_into('<H', a, 2, STRENGTH_SPRITE)
                struct.pack_into('<H', a, 10, STRENGTH_SCRIPT)
                boulders += 1
            elif (sprite, script) == (STRENGTH_SPRITE, 0):
                struct.pack_into('<H', a, 2, ROCK_SMASH_SPRITE)
                rocks += 1
            actors.append(bytes(a))
        assert (boulders, rocks) == expected, (mid, boulders, rocks)
        groups[1] = actors
        events.files[eid] = events_encode(groups)
        report[mid] = dict(boulders=boulders, barrier_rocks=rocks)
    rom.setFileByName('a/0/3/2', events.save())
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
