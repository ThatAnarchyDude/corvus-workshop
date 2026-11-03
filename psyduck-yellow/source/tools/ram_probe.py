"""TEST ONLY: boot a fixture ROM (the .dsv next to it is the save), wait for a battle to start, then find and decrypt every Gen-4 party Pokemon structure in main RAM (py-desmume) and print species, level, nature, IVs, EVs, moves and the
real battle stats. A party Pokemon is 236 bytes: PID u32, 2 spare bytes, checksum u16, four 32-byte blocks shuffled by PID and encrypted with the checksum (LCG 0x41C64E6D / 0x6073), then a 100-byte battle block encrypted with the PID.
(Found 2026-11-02: these structures are encrypted in RAM, so plain pattern scans for stats find nothing.) Usage: ram_probe.py <rom.nds> <wait frames> <min level> <out.json>   (py-desmume venv)"""
import json
import os
import struct
import sys
from desmume.controls import Keys, keymask
from desmume.emulator import DeSmuME

ORDERS = ['ABCD', 'ABDC', 'ACBD', 'ACDB', 'ADBC', 'ADCB', 'BACD', 'BADC', 'BCAD', 'BCDA', 'BDAC', 'BDCA', 'CABD', 'CADB', 'CBAD', 'CBDA', 'CDAB', 'CDBA', 'DABC', 'DACB', 'DBAC', 'DBCA', 'DCAB', 'DCBA']
NATURES = ['Hardy', 'Lonely', 'Brave', 'Adamant', 'Naughty', 'Bold', 'Docile', 'Relaxed', 'Impish', 'Lax', 'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive', 'Modest', 'Mild', 'Quiet', 'Bashful', 'Rash', 'Calm', 'Gentle', 'Sassy', 'Careful', 'Quirky']


def decrypt(data, seed):
    out = bytearray(len(data))
    for i in range(0, len(data), 2):
        seed = (seed * 0x41C64E6D + 0x6073) & 0xFFFFFFFF
        out[i:i + 2] = struct.pack('<H', struct.unpack_from('<H', data, i)[0] ^ (seed >> 16))
    return bytes(out)


def decode(raw):
    pid, _, checksum = struct.unpack_from('<IHH', raw, 0)
    blocks = decrypt(raw[8:0x88], checksum)
    if sum(struct.unpack('<64H', blocks)) & 0xFFFF != checksum:
        return None
    order = ORDERS[((pid >> 13) & 31) % 24]
    block = {order[i]: blocks[i * 32:(i + 1) * 32] for i in range(4)}
    species, item = struct.unpack_from('<2H', block['A'], 0)
    evs = list(block['A'][0x10:0x16])
    moves = list(struct.unpack_from('<4H', block['B'], 0))
    iv = struct.unpack_from('<I', block['B'], 0x10)[0]
    ivs = [(iv >> (5 * i)) & 31 for i in range(6)]
    battle = decrypt(raw[0x88:0xEC], pid)
    status, level, capsule, hp, mx, atk, dfn, spe, spa, spd = struct.unpack_from('<IBBHHHHHHH', battle, 0)
    return dict(pid=hex(pid), species=species, item=item, level=level, nature=NATURES[pid % 25], ivs=ivs, evs=evs, moves=moves, hp=mx, atk=atk, defense=dfn, spe=spe, spa=spa, spd=spd)


if __name__ == '__main__':
    rom, wait, minlevel, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    emu = DeSmuME()
    emu.open(rom)
    assert emu.backup.import_file(os.path.splitext(rom)[0] + '.dsv')
    emu.reset()

    def run(n, key=None):
        if key:
            emu.input.keypad_add_key(keymask(getattr(Keys, 'KEY_' + key.upper())))
        for _ in range(n):
            emu.cycle(False)
        if key:
            emu.input.keypad_rm_key(keymask(getattr(Keys, 'KEY_' + key.upper())))
    run(900); run(30, 'a'); run(60); run(30, 'a'); run(60); run(30, 'a'); run(120); run(30, 'a'); run(700); run(20, 'b'); run(60)
    run(wait)
    ram = bytes(emu.memory.unsigned[0x02000000:0x02400000])
    found, seen = [], set()
    for p in range(0, len(ram) - 0xEC, 4):
        if ram[p + 4:p + 6] != b'\0\0' or ram[p:p + 4] == b'\0\0\0\0':
            continue
        r = decode(ram[p:p + 0xEC])
        if r and 1 <= r['species'] < 1600 and minlevel <= r['level'] <= 100 and (r['pid'], r['species']) not in seen:
            seen.add((r['pid'], r['species']))
            r['addr'] = hex(0x02000000 + p)
            found.append(r)
    json.dump(found, open(out, 'w'), indent=1)
    print(len(found), 'party Pokemon found')
    for r in found:
        print('MON', r['addr'], 'sp', r['species'], 'L', r['level'], r['nature'], 'IV', r['ivs'], 'EV', r['evs'], 'item', r['item'], 'moves', r['moves'], 'stats', r['hp'], r['atk'], r['defense'], r['spe'], r['spa'], r['spd'])
