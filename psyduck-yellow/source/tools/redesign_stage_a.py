"""Stage A of the starter redesign (owner-approved 2026-10-29), data only:
 - level-up lists: ALL Eevee (133, 1561) the approved list; Psyduck (54, 1563) the approved list; Golduck (55) the approved list WITH the catch-up entries (Psyduck's moves up to L34), Eevee's eight existing evolutions and Novareon from data/eeveelution-levelup-plan.json (normal and starter ids);
 - base stats: Psyduck (54, 1563) 50/40/45/75/60/50 = 320, Golduck (55) 85/70/75/125/100/75 = 530 (personal data byte order: HP, Atk, Def, Spe, SpA, SpD);
 - TM/HM rows (a/0/2/8 file 14): Psyduck/Golduck share one row (union of both plus Shadow Ball, Rock Tomb, Reflect), the Eevee line from data/eevee-tm-plan.json (names -> bits; the placeholder HM09-16 bits are kept).
The nine NEW Eeveelutions (no species yet) are skipped. Usage (from yellow-heartgold, PYTHONPATH=tools): redesign_stage_a.py <in.nds> <out.nds>"""
import json
import struct
import sys
import ndspy.narc
import ndspy.rom
from prototype import decode_messages

EEVEE = [(1, 'Tackle'), (1, 'Tail Whip'), (5, 'Quick Attack'), (8, 'Bite'), (12, 'Swift'), (16, 'Helping Hand'), (20, 'Baton Pass'), (24, 'Take Down'), (28, 'Charm'), (32, 'Double-Edge'), (36, 'Last Resort')]
PSYDUCK = [(1, 'Scratch'), (1, 'Water Gun'), (4, 'Tail Whip'), (7, 'Confusion'), (10, 'Disable'), (13, 'Aqua Jet'), (16, 'Psybeam'), (19, 'Zen Headbutt'), (22, 'Water Pulse'), (25, 'Calm Mind'), (28, 'Psychic'), (31, 'Surf'), (34, 'Aqua Tail'),
           (37, 'Future Sight'), (40, 'Hydro Pump'), (43, 'Amnesia'), (46, 'Extrasensory'), (49, 'Ice Beam'), (52, 'Psyshock'), (55, 'Hydro Cannon')]
GOLDUCK_OWN = [(0, 'Psychic'), (36, 'Aqua Tail'), (39, 'Calm Mind'), (42, 'Zen Headbutt'), (45, 'Surf'), (48, 'Future Sight'), (51, 'Ice Beam'), (54, 'Hydro Pump'), (57, 'Psyshock'), (60, 'Amnesia'), (63, 'Psychic'), (66, 'Hydro Cannon')]
GOLDUCK = [(0, 'Psychic')] + [e for e in PSYDUCK if e[0] <= 34] + GOLDUCK_OWN[1:]
# stats in personal-data order HP, Atk, Def, Spe, SpA, SpD
STATS = {54: (50, 40, 45, 50, 75, 60), 1563: (50, 40, 45, 50, 75, 60), 55: (85, 70, 75, 75, 125, 100)}
LINE = {'Vaporeon': 134, 'Jolteon': 135, 'Flareon': 136, 'Espeon': 196, 'Umbreon': 197, 'Leafeon': 470, 'Glaceon': 471, 'Sylveon': 750, 'Novareon': 1581}
STARTER_IDS = {'Eevee': 1561, 'Vaporeon': 1565, 'Jolteon': 1567, 'Flareon': 1569, 'Espeon': 1571, 'Umbreon': 1573, 'Leafeon': 1575, 'Glaceon': 1577, 'Sylveon': 1579, 'Novareon': 1581}


def main(src, dst):
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    text = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    inv = {v: k for k, v in json.load(open('tools/text-map.json')).items()}
    moves = [''.join(inv.get(w, '?') for w in row if w != 65535) for row in decode_messages(text.files[750])[1]]
    idx = {n: i for i, n in enumerate(moves) if n}
    lid = rom.filenames.idOf('a/0/3/3')
    ls = bytearray(ndspy.narc.NARC(rom.files[lid]).files[0])

    def put(sp, entries):
        assert len(entries) <= 34, (sp, len(entries))
        row = bytearray()
        for lv, m in sorted(entries, key=lambda e: e[0]):
            row += struct.pack('<HH', idx[m], lv)
        row += struct.pack('<HH', 0xFFFF, 0) * (34 - len(entries))
        ls[sp * 136:(sp + 1) * 136] = row
    for sp in (133, 1561):
        put(sp, EEVEE)
    for sp in (54, 1563):
        put(sp, PSYDUCK)
    put(55, GOLDUCK)
    plan = json.load(open('data/eeveelution-levelup-plan.json'))
    for name, sp in LINE.items():
        if name in plan:
            put(sp, [(lv, m) for lv, m in plan[name]])
            if name in STARTER_IDS and STARTER_IDS[name] != sp:
                put(STARTER_IDS[name], [(lv, m) for lv, m in plan[name]])
    for name, sid in STARTER_IDS.items():
        if name in plan and name != 'Eevee':
            put(sid, [(lv, m) for lv, m in plan[name]])
    nl = ndspy.narc.NARC(rom.files[lid])
    nl.files[0] = bytes(ls)
    rom.files[lid] = nl.save()
    # stats
    pid = rom.filenames.idOf('a/0/0/2')
    pe = ndspy.narc.NARC(rom.files[pid])
    for sp, st in STATS.items():
        row = bytearray(pe.files[sp])
        row[0:6] = bytes(st)
        pe.files[sp] = bytes(row)
    rom.files[pid] = pe.save()
    # TM rows
    d = bytes(rom.loadArm9().sections[0].data)
    tab = struct.unpack_from('<108H', d, d.find(struct.pack('<6H', 264, 337, 352, 347, 46, 92)))
    bit = {}
    for i in range(100):
        bit.setdefault(moves[tab[i]], i)
    tid = rom.filenames.idOf('a/0/2/8')
    tn = ndspy.narc.NARC(rom.files[tid])
    tm = bytearray(tn.files[14])

    def getv(sp):
        return int.from_bytes(tm[sp * 44:sp * 44 + 16], 'little')

    def setv(sp, v):
        tm[sp * 44:sp * 44 + 16] = v.to_bytes(16, 'little')
    extra = sum(1 << bit[m] for m in ('Shadow Ball', 'Rock Tomb', 'Reflect'))
    duck = getv(54) | getv(55) | extra
    for sp in (54, 55, 1563):
        setv(sp, duck | (getv(sp) & ~((1 << 100) - 1)))
    tmplan = json.load(open('data/eevee-tm-plan.json'))
    for name, sp_list in {'Eevee': (133, 1561), **{n: (LINE[n], STARTER_IDS.get(n, LINE[n])) for n in LINE}}.items():
        if name not in tmplan:
            continue
        mask = sum(1 << bit[m] for m in tmplan[name])
        for sp in set(sp_list):
            setv(sp, mask | (getv(sp) & ~((1 << 100) - 1)))
    tn.files[14] = bytes(tm)
    rom.files[tid] = tn.save()
    rom.saveToFile(dst)
    print('wrote', dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
