"""Bring Fairy-type move data in line with the owner's specification list (owner order 2026-10-23).

Compared with the list, every Fairy move in the ROM already matches on category, power, accuracy, PP and (where the data carries it) priority,
target and secondary-effect chance, except:
 - Moonblast: secondary-effect chance was 10%, the list says 30% (68 species learn it): fixed here.
 - Sparkly Swirl: ROM has the official 120 power / 85% accuracy, the list says 85 / 100: left alone (no species learns it, and the list
   differs from the official values; owner to confirm).
 - Alluring Voice: the ROM move has no battle effect (plain damage), the list says it confuses a target that had a stat rise this turn:
   needs a new battle script and no species learns it, so left alone.
Move data: a/0/1/1, 16 bytes per move (u16 effect, split, power, type, accuracy, pp, effect chance, u16 target, s8 priority, flags...).

Usage: fairy_moves.py <in.nds> <out.nds>
"""
import sys
import ndspy.narc
import ndspy.rom

MOONBLAST = 588
CHANCE_OFFSET = 7


def patch(rom):
    moves = ndspy.narc.NARC(rom.getFileByName('a/0/1/1'))
    rec = bytearray(moves.files[MOONBLAST])
    assert rec[4] == 9 and rec[3] == 95 and rec[CHANCE_OFFSET] == 10, 'unexpected Moonblast record'
    rec[CHANCE_OFFSET] = 30
    moves.files[MOONBLAST] = bytes(rec)
    rom.setFileByName('a/0/1/1', moves.save())
    return dict(moonblast_chance=30)


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
