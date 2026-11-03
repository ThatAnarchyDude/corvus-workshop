"""Johto postgame, step 1c: the other ways into Johto stay closed until the first S.S. Aqua arrival (flag ARRIVED from johto_step1b.py).
 - Route 22's League Reception Gate (map 299): its south arm to Route 26 used the Hall of Fame flag 0x964 (gate299.py); the check in the gate's script bank (1222) now tests ARRIVED instead.
 - The Saffron Magnet Train station (map 400): the attendant's script (bank 834 script 1; native: power restored flag 0x118 and a Pass) gets a prelude that refuses until ARRIVED, then runs the native script.
 - Bug fix: the south arm's "closed" bounce walked the player one step further south (movement 13 instead of 12), so the gate never held.
 - Fly: HeartGold only offers visited towns, and no Johto town is visited until the ferry arrival (checked by design; step 2 adds New Bark Town after Elm's call).
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step1c.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.narc
import ndspy.rom
from map_edit import MapEdit
from opening import Script, end
from viridian_tutorial import TABLE
from johto_step1b import script_ranges

GATE, STATION = 299, 400
GAME_CLEAR = 0x964
ARRIVED = 0xA6B


def patch(rom, arrived=ARRIVED):
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2'))
    d = bytes(rom.loadArm9().sections[0].data)
    bank = struct.unpack_from('<H', d, TABLE + 24 * GATE + 6)[0]
    raw = bytearray(scripts.files[bank])
    pat = struct.pack('<HH', 0x20, GAME_CLEAR)
    assert raw.count(pat) == 1, 'the gate script does not check the Hall of Fame flag exactly once'
    at = raw.find(pat)
    struct.pack_into('<H', raw, at + 2, arrived)
    # the closed message's bounce used the north arm's "walk down 1" (13), which pushed the player further SOUTH, into Johto; this arm's way back is up (12)
    assert bytes(raw[472:480]) == bytes.fromhex('0d000100fe000000'), 'south-arm bounce data moved'
    struct.pack_into('<H', raw, 472, 12)
    scripts.files[bank] = bytes(raw)
    rom.setFileByName('a/0/1/2', scripts.save())
    e = MapEdit(rom, STATION)
    starts, ends = script_ranges(e.bank)
    assert starts[0] == 155, starts
    block = bytes(e.bank[starts[0]:ends[0]])

    def build(add):
        s = Script().emit(96).emit(104).emit(32, arrived).jump('native', 1)
        s.msg(add('The MAGNET TRAIN is not running right now.'))
        end(s)
        s.data.extend(b'\0' * (-len(s.data) % 4))
        s.labels['native'] = len(s.data)
        s.data.extend(block)
        return s.finish()
    new_id = e.script(build)
    row = bytearray(e.groups[1][0])
    assert struct.unpack_from('<H', row, 10)[0] == 1
    struct.pack_into('<H', row, 10, new_id)
    e.groups[1][0] = bytes(row)
    e.save()
    return dict(gate_bank=bank, gate_flag_at=at, station_script=new_id)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
