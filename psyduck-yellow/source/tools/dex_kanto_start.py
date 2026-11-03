"""New Game: Oak gives the regional (Kanto) Pokedex, NOT the National one (owner 2026-11-03: "I started a New Game, and Oak gave me the National Pokedex").
The Johto postgame plan (JOHTO-POSTGAME-PLAN.md) keeps the Pokedex Kanto-only until Oak's upgrade at Mr. Pokemon's house (johto_step2.py: Oak's scene turns National on with command 477 mode 1), but the lab's starter script (opening.grant:
`GivePokedex ; SetFlag 0x6B ; command 477 mode 1 (National on) -> var 0x800C`) still switched National mode on at the very start. Command 477's mode byte is changed from 1 (on) to 0 (the project's own "off" routine, ov129 0x23DECC0, already used by Elm's call):
a same-size in-place change in the active lab script bank (the bank of map 505). The regional Pokedex is Kanto's 151 (dex_kanto.py), so the Pokedex starts as the Kanto dex; species outside it still register and show after the upgrade.
Usage (from yellow-heartgold, PYTHONPATH=tools): dex_kanto_start.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.narc
import ndspy.rom
from viridian_tutorial import TABLE

LAB_MAP = 505
GRANT = bytes.fromhex('2301' '1e006b00' 'dd01' '01' '0c80')       # GivePokedex(291) ; SetFlag 0x6B ; command 477 mode 1, result var 0x800C


def patch(rom):
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    fid = struct.unpack_from('<H', d, TABLE + LAB_MAP * 24 + 6)[0]
    arc = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    bank = bytearray(arc.files[fid])
    assert bank.count(GRANT) == 1, ('expected exactly one Pokedex grant in the lab bank', bank.count(GRANT))
    at = bank.index(GRANT) + len(GRANT) - 3
    assert bank[at] == 1
    bank[at] = 0
    arc.files[fid] = bytes(bank)
    rom.files[rom.filenames.idOf('a/0/1/2')] = arc.save()
    return dict(script_file=fid, offset=at)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
