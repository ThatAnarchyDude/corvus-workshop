"""Make the regional Pokedex the Kanto dex (owner order 2026-10-23): species 1-151 in national order, Johto visible only in National mode.

The regional dex is two things: the number table a/1/3/8 (u16 per species id: its regional number, 0 = not in the regional dex) and the regional sort list
a/2/1/4 file 12 (the species ids in regional order). Both held Johto's 256 species (Chikorita = 1 ... Celebi = 251 ...). They now hold Kanto's 151
(Bulbasaur = 1 ... Mew = 151, the same numbers as the National dex), so the regional view lists and counts Kanto and the National view still lists everything.
The region label "JOHTO" on the National/regional switch comes from the Pokedex text bank (a/0/2/7 bank 802, entry 65); see TEXT below.

The Pokedex app (overlay 18, Pokedex_Init at 0x021E5AA0) opens in National mode when the National Dex is on and no mode was remembered yet (a stored
mode of 2). That default is changed to the regional (Kanto) view: in the National-Dex branch the byte stored for "no remembered mode" is 0 instead of 1.

Usage: dex_kanto.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom

KANTO = 151


INIT_FIX = 0x021E5AFC                       # `strb r2,[r4,r0]` and the `b` after it in the National-Dex branch of Pokedex_Init
INIT_OLD = bytes.fromhex('2254' '08e0')     # strb r2,[r4,r0] ; b #0x021e5b12
INIT_NEW = bytes.fromhex('0022' '2254')     # movs r2,#0 ; strb r2,[r4,r0] ; (falls into the other branch, which stores 0 again and rejoins at 0x021e5b12)


def default_to_regional(rom):
    ov = rom.loadArm9Overlays()[18]
    ov.data = bytearray(ov.data)
    at = INIT_FIX - ov.ramAddress
    assert bytes(ov.data[at:at + 4]) == INIT_OLD, bytes(ov.data[at:at + 4]).hex()
    ov.data[at:at + 4] = INIT_NEW
    rom.files[ov.fileID] = ov.save(compress=False)


def patch(rom, relabel=True):
    numbers = ndspy.narc.NARC(rom.getFileByName('a/1/3/8'))
    old = struct.unpack('<%dH' % (len(numbers.files[0]) // 2), bytes(numbers.files[0]))
    assert sum(1 for v in old if v) == 256 and max(old) == 256, 'regional table is not the 256-species Johto dex'
    new = [i if 1 <= i <= KANTO else 0 for i in range(len(old))]
    numbers.files[0] = struct.pack('<%dH' % len(new), *new)
    rom.setFileByName('a/1/3/8', numbers.save())
    lists = ndspy.narc.NARC(rom.getFileByName('a/2/1/4'))
    cur = struct.unpack('<%dH' % (len(lists.files[12]) // 2), bytes(lists.files[12]))
    assert len(cur) == 256 and cur[0] == 152, 'regional sort list is not the Johto list'
    lists.files[12] = struct.pack('<%dH' % KANTO, *range(1, KANTO + 1))
    rom.setFileByName('a/2/1/4', lists.save())
    default_to_regional(rom)
    return dict(regional_species=KANTO, default_mode='regional (Kanto)')


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom))
    rom.saveToFile(dst)
