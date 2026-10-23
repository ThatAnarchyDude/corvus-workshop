"""TM34 Shock Wave -> Moonblast, TM58 Endure -> Dazzling Gleam, and Charge Beam for four more Legendaries (owner order 2026-10-23).

 - The TM move table (100 u16 move ids, TM01..TM92 then HM01..HM08) exists as ARM9 0x021000CC and as an identical copy in overlay 129;
   both are rewritten. Item names stay "TM034"/"TM058"; the campaign no longer hands out TM34 (Lt. Surge gives Thunderbolt, see vermilion_gym.py).
 - TM compatibility is a bit per TM (bit TM-1) in the 44-byte-per-species block a/0/2/8 file 14. For the two changed TMs every species'
   bit is recomputed:
     Dazzling Gleam (TM58): every species hg-engine's learnset data lists with Dazzling Gleam as a machine move in any game.
     Moonblast (TM34): no game teaches it by machine, so: every species that learns it by level-up or egg move, plus every Fairy-type species.
   Species are matched to the learnset data by name (forms share their base name; Novareon uses Umbreon's entry).
 - Thundurus, Tapu Koko, Regieleki and Miraidon (they learn Shock Wave by level-up, so they keep it) may also learn TM57 Charge Beam.

Usage: tm_fairy.py <in.nds> <out.nds> <hg-engine learnsets.json>
"""
import json
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
from prototype import decode_messages
from starter_eevee_line import BASES, FIRST

TABLE_PATTERN = struct.pack('<6H', 264, 337, 352, 347, 46, 92)     # TM01..TM06
SHOCK_WAVE_TM, ENDURE_TM, CHARGE_BEAM_TM = 34, 58, 57
CHARGE_BEAM_EXTRA = ('Thundurus', 'TapuKoko', 'Regieleki', 'Miraidon')
TM_BLOCK = 44
FAIRY = 9


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def patch(rom, learnsets_path):
    text = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    inv = {v: k for k, v in json.load(open(__file__.replace('tm_fairy.py', 'text-map.json'))).items()}
    bank = lambda i: [''.join(inv.get(w, '?') for w in r if w != 65535) for r in decode_messages(text.files[i])[1]]
    moves, species = bank(750), bank(237)
    move_id = {n: i for i, n in enumerate(moves)}
    moonblast, gleam = move_id['Moonblast'], move_id['Dazzling Gleam']
    shock, endure = move_id['Shock Wave'], move_id['Endure']
    # 1. TM move tables
    new_tables = {}
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(section.data)
    ov = rom.loadArm9Overlays()[129]
    ov.data = bytearray(ov.data)
    sites = []
    for label, data in (('arm9', section.data), ('overlay129', ov.data)):
        at = bytes(data).find(TABLE_PATTERN)
        assert at >= 0, label
        assert struct.unpack_from('<H', data, at + 2 * (SHOCK_WAVE_TM - 1))[0] == shock
        assert struct.unpack_from('<H', data, at + 2 * (ENDURE_TM - 1))[0] == endure
        struct.pack_into('<H', data, at + 2 * (SHOCK_WAVE_TM - 1), moonblast)
        struct.pack_into('<H', data, at + 2 * (ENDURE_TM - 1), gleam)
        sites.append((label, at))
    # 2. compatibility
    learn = json.load(open(learnsets_path))
    by_name = {norm(k.removeprefix('SPECIES_')): v for k, v in learn.items()}
    pers = ndspy.narc.NARC(rom.getFileByName('a/0/0/2'))
    addons = ndspy.narc.NARC(rom.getFileByName('a/0/2/8'))
    block = bytearray(addons.files[14])
    assert len(block) == len(species) * TM_BLOCK, (len(block), len(species))
    novareon_ids = {FIRST + 2 * 8, FIRST + 2 * 8 + 1}
    gleam_n = moon_n = 0
    def has_bit(sp, tm):
        return bool(block[sp * TM_BLOCK + (tm - 1) // 8] >> ((tm - 1) % 8) & 1)
    def put_bit(sp, tm, on):
        i, b = sp * TM_BLOCK + (tm - 1) // 8, (tm - 1) % 8
        block[i] = (block[i] | (1 << b)) if on else (block[i] & ~(1 << b) & 0xFF)
    for sp in range(len(species)):
        name = norm(species[sp])
        entry = by_name.get('umbreon') if sp in novareon_ids else by_name.get(name)
        machine = set(entry.get('MachineMoves', [])) if entry else set()
        natural = ({m['Move'] for m in entry.get('LevelMoves', [])} | set(entry.get('EggMoves', []))) if entry else set()
        fairy_type = pers.files[sp][6] == FAIRY or pers.files[sp][7] == FAIRY
        g = 'MOVE_DAZZLING_GLEAM' in machine
        m = 'MOVE_MOONBLAST' in natural or fairy_type
        put_bit(sp, ENDURE_TM, g)
        put_bit(sp, SHOCK_WAVE_TM, m)
        gleam_n += g
        moon_n += m
    extra = []
    for sp in range(len(species)):
        if norm(species[sp]) in {norm(n) for n in CHARGE_BEAM_EXTRA}:
            put_bit(sp, CHARGE_BEAM_TM, True)
            extra.append(species[sp])
    addons.files[14] = bytes(block)
    rom.setFileByName('a/0/2/8', addons.save())
    rom.arm9 = main.save(compress=True)
    ovs = rom.loadArm9Overlays()
    ovs[129].data = ov.data
    rom.files[ov.fileID] = ov.save(compress=False)
    return dict(tables=sites, moonblast_learners=moon_n, dazzling_gleam_learners=gleam_n, charge_beam_added=extra)


if __name__ == '__main__':
    src, dst, learnsets = sys.argv[1:4]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    print(patch(rom, learnsets))
    rom.saveToFile(dst)
