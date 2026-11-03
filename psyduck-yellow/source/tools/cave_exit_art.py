"""Exit art for the rebuilt caves (second pass after mtmoon_ladders.py / rock_vr_ladders.py): a glowing pad on every exit to the outside of Mt. Moon, Rock Tunnel and Victory Road (cave_ladders.patch_exits).
Owner 2026-11-02: exits to the outside had no art, so the way out of a cave was as hard to see as the ladders were. Usage: cave_exit_art.py <in.nds> <out.nds> <pokeyellow source>"""
import sys
import ndspy.rom
import cave_ladders as cl
import mtmoon_ladders as moon
import rock_vr_ladders as rv

if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    for spec in moon.specs(sys.argv[3]) + rv.rock_specs(sys.argv[3]) + rv.vr_specs(sys.argv[3]):
        print(cl.patch_exits(rom, spec))
    rom.saveToFile(sys.argv[2])
