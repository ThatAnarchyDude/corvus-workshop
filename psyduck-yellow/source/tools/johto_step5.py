"""Johto postgame, step 5a: the eight Johto Gym Leaders scale with the Johto badges (owner plan 2026-11-02; README.md "Confirmed gym balance requirements").

Rule: a leader's team level is B + floor((100 - B) * (n - 1) / 7), n = Johto badges already held + 1 (at most 8), B = 65 (the top level of the Kanto League teams). Every Pokemon of the team is at that level:
65, 70, 75, 80, 85, 90, 95, 100. The eighth challenger (all other seven badges held) therefore always fields six level-100 Pokemon.
 - Each leader has ONE record with a six-Pokemon roster (on-type, fully evolved, signature Pokemon kept: Pidgeot, Scyther, Miltank, Gengar, Poliwrath, Steelix, Dewgong, Kingdra), written in the
   engine's real party layout (item, four moves, ball seal LAST). The record is the original HeartGold id, so the gym scripts and Clair's shared trainer script are untouched;
 - the level is set by a small routine (overlay 129) that replaces the "keep the party Pokemon's level" step of the engine's trainer party builder (overlay 131, entered from ARM9 0x02073604; the ARM9
   body of that function is dead code): for the eight leader ids it counts the Johto badge bits of the player profile and picks the tier level, otherwise the record's own level stays. The same routine is the place where step 5b
   (ordinary Johto trainers, level curve on each trainer's original level) will go;
 - trainer_layout_fix: found 2026-11-02, the engine reads a type-1/3 party Pokemon as [iv, ability, level, species, (item), four moves, ball seal]; the project tools wrote [.., species, 0, four moves] (the
   ball seal first), so every Yellow trainer Pokemon had an empty first move slot and lost its fourth move (the move list shifted by one, the fourth move became the "ball seal"). Fixed for every record.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step5.py <in.nds> <out.nds>"""
import json
import struct
import sys
import ndspy.code
import ndspy.narc
import ndspy.rom
import tower_scenes as ts
from mega_starter import Gap
from prototype import decode_messages
import map_header_extension as ext

BASE_LEVEL = 65
TIER_LEVELS = [BASE_LEVEL + (100 - BASE_LEVEL) * k // 7 for k in range(8)]
BUILDER_OVERLAY = 131                                         # the engine's own trainer party builder (ARM9 0x02073604 jumps into it); it shares RAM with overlay 130
SITE = 0x023C83BE                                             # in that builder: `str r3,[r7,#0x1c]; ldr r2,[r7,#0x1c]` = keep the party Pokemon's level (r3), r7 = its frame
SITE_BYTES = bytes.fromhex('fb61fa69')
SAVE_POINTER_AT = 0x272C4                                     # ARM9 literal: address of the global SaveData pointer (as shiny_charm.py reads it)
PROFILE = 0x02028E9C                                          # (SaveData*) -> player profile; the Johto badge byte sits at profile + 0x1A (TestBadge 0x02028F98)
HOOK_AT = 0x023DED44                                          # free overlay-129 space (208 bytes) left by johto_step3c.py
HOOK_END = 0x023DEE14
IV = 200                                                      # (iv * 31) / 255 = 24 for every leader Pokemon

# leader id: (name, [(species, held item, (four moves))])
LEADERS = {
    20: ('FALKNER', [('Pidgeot', 'Leftovers', ('Brave Bird', 'Quick Attack', 'Steel Wing', 'Roost')),
                     ('Fearow', 'Sharp Beak', ('Drill Peck', 'Return', 'U-turn', 'Aerial Ace')),
                     ('Dodrio', 'Leftovers', ('Brave Bird', 'Return', 'Pluck', 'Roost')),
                     ('Noctowl', 'Leftovers', ('Air Slash', 'Psychic', 'Hypnosis', 'Roost')),
                     ('Xatu', 'Leftovers', ('Psychic', 'Air Slash', 'Calm Mind', 'Roost')),
                     ('Honchkrow', 'Life Orb', ('Brave Bird', 'Sucker Punch', 'Night Slash', 'Roost'))]),
    21: ('BUGSY', [('Scyther', 'Leftovers', ('X-Scissor', 'Aerial Ace', 'Swords Dance', 'Night Slash')),
                   ('Scizor', 'Leftovers', ('Bullet Punch', 'X-Scissor', 'Swords Dance', 'Roost')),
                   ('Heracross', 'Life Orb', ('Megahorn', 'Close Combat', 'Stone Edge', 'Earthquake')),
                   ('Beedrill', 'Leftovers', ('X-Scissor', 'Poison Jab', 'Pursuit', 'Aerial Ace')),
                   ('Ariados', 'Leftovers', ('Megahorn', 'Poison Jab', 'Sucker Punch', 'Toxic Spikes')),
                   ('Yanmega', 'Leftovers', ('Bug Buzz', 'Air Slash', 'Hypnosis', 'Giga Drain'))]),
    30: ('WHITNEY', [('Miltank', 'Leftovers', ('Body Slam', 'Milk Drink', 'Earthquake', 'Heal Bell')),
                     ('Clefable', 'Leftovers', ('Moonlight', 'Ice Beam', 'Thunderbolt', 'Metronome')),
                     ('Blissey', 'Leftovers', ('Soft-Boiled', 'Seismic Toss', 'Thunder Wave', 'Toxic')),
                     ('Snorlax', 'Leftovers', ('Return', 'Earthquake', 'Rest', 'Crunch')),
                     ('Ursaring', 'Life Orb', ('Facade', 'Crunch', 'Close Combat', 'Earthquake')),
                     ('Tauros', 'Leftovers', ('Return', 'Earthquake', 'Rock Slide', 'Pursuit'))]),
    31: ('MORTY', [('Gengar', 'Leftovers', ('Shadow Ball', 'Sludge Bomb', 'Thunderbolt', 'Hypnosis')),
                   ('Dusknoir', 'Leftovers', ('Shadow Punch', 'Earthquake', 'Will-O-Wisp', 'Pain Split')),
                   ('Mismagius', 'Life Orb', ('Shadow Ball', 'Psychic', 'Thunderbolt', 'Calm Mind')),
                   ('Banette', 'Leftovers', ('Shadow Claw', 'Sucker Punch', 'Will-O-Wisp', 'Thunder Wave')),
                   ('Drifblim', 'Leftovers', ('Shadow Ball', 'Thunderbolt', 'Calm Mind', 'Rest')),
                   ('Spiritomb', 'Leftovers', ('Shadow Sneak', 'Sucker Punch', 'Pursuit', 'Rain Dance'))]),
    34: ('CHUCK', [('Poliwrath', 'Leftovers', ('Close Combat', 'Waterfall', 'Ice Punch', 'Earthquake')),
                   ('Primeape', 'Black Belt', ('Close Combat', 'Ice Punch', 'Earthquake', 'Stone Edge')),
                   ('Machamp', 'Leftovers', ('Close Combat', 'Stone Edge', 'Earthquake', 'Bullet Punch')),
                   ('Hitmonlee', 'Leftovers', ('High Jump Kick', 'Blaze Kick', 'Stone Edge', 'Earthquake')),
                   ('Hariyama', 'Leftovers', ('Close Combat', 'Knock Off', 'Earthquake', 'Bullet Punch')),
                   ('Lucario', 'Life Orb', ('Aura Sphere', 'Close Combat', 'Extreme Speed', 'Dragon Pulse'))]),
    33: ('JASMINE', [('Steelix', 'Leftovers', ('Iron Head', 'Earthquake', 'Stone Edge', 'Rock Slide')),
                     ('Magnezone', 'Leftovers', ('Thunderbolt', 'Flash Cannon', 'Thunder Wave', 'Toxic')),
                     ('Skarmory', 'Leftovers', ('Brave Bird', 'Steel Wing', 'Spikes', 'Roost')),
                     ('Forretress', 'Leftovers', ('Gyro Ball', 'Spikes', 'Rapid Spin', 'Explosion')),
                     ('Bronzong', 'Leftovers', ('Gyro Ball', 'Earthquake', 'Psychic', 'Toxic')),
                     ('Metagross', 'Life Orb', ('Meteor Mash', 'Earthquake', 'Zen Headbutt', 'Hammer Arm'))]),
    32: ('PRYCE', [('Dewgong', 'Leftovers', ('Surf', 'Ice Beam', 'Rest', 'Toxic')),
                   ('Mamoswine', 'Leftovers', ('Earthquake', 'Ice Shard', 'Icicle Crash', 'Stone Edge')),
                   ('Lapras', 'Leftovers', ('Surf', 'Ice Beam', 'Thunderbolt', 'Sing')),
                   ('Abomasnow', 'Leftovers', ('Blizzard', 'Wood Hammer', 'Earthquake', 'Ice Shard')),
                   ('Weavile', 'Life Orb', ('Ice Punch', 'Night Slash', 'Brick Break', 'Icicle Crash')),
                   ('Cloyster', 'Leftovers', ('Icicle Spear', 'Hydro Pump', 'Spikes', 'Rock Blast'))]),
    35: ('CLAIR', [('Kingdra', 'Leftovers', ('Waterfall', 'Dragon Dance', 'Outrage', 'Hydro Pump')),
                   ('Dragonite', 'Leftovers', ('Outrage', 'Extreme Speed', 'Earthquake', 'Fire Punch')),
                   ('Gyarados', 'Leftovers', ('Waterfall', 'Dragon Dance', 'Earthquake', 'Stone Edge')),
                   ('Flygon', 'Leftovers', ('Earthquake', 'Dragon Claw', 'U-turn', 'Fire Punch')),
                   ('Salamence', 'Life Orb', ('Dragon Claw', 'Fly', 'Earthquake', 'Fire Blast')),
                   ('Garchomp', 'Leftovers', ('Outrage', 'Earthquake', 'Stone Edge', 'Swords Dance'))]),
}


def lookup(rom):
    arc = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    chars = {v: k for k, v in json.load(open('tools/text-map.json')).items()}

    def table(bank):
        rows = decode_messages(arc.files[bank])[1]
        return {''.join(chars.get(c, '?') for c in r if c != 0xFFFF).lower(): i for i, r in reversed(list(enumerate(rows)))}
    return table(237), table(750), table(222)               # species, moves, items


def trainer_layout_fix(rom):
    """[iv, ab, level, species, (cb), four moves, (item)] -> the engine's [.., species, (item), four moves, ball seal]. Original HeartGold entries are never touched (they already have a nonzero first
    move and a zero ball seal); an entry that has a leading zero (type 1) or a nonzero last halfword (type 3) is a project-written one."""
    book = ts.TrainerBook(rom)
    fixed1 = fixed3 = 0
    for tid in range(len(book.trainers.files)):
        row, party = bytearray(book.trainers.files[tid]), bytearray(book.parties.files[tid])
        kind, count = row[0], row[3]
        if not count or not kind & 1:
            continue
        size = 8 + 8 + (2 if kind & 2 else 0)
        if len(party) != count * size:
            continue
        for i in range(count):
            at = 16 * 0 + i * size + 6
            h = list(struct.unpack_from('<%dH' % ((size - 6) // 2), party, at))
            if kind & 2:                                    # [item, m1..m4, cb] expected; project layout was [cb, m1..m4, item]
                if h[5] != 0:
                    h = [h[5], h[1], h[2], h[3], h[4], 0]
                    fixed3 += 1
                else:
                    continue
            else:                                           # [m1..m4, cb] expected; project layout was [cb, m1..m4]
                if h[0] == 0 and any(h[1:]):
                    h = [h[1], h[2], h[3], h[4], 0]
                    fixed1 += 1
                else:
                    continue
            struct.pack_into('<%dH' % len(h), party, at, *h)
        book.parties.files[tid] = bytes(party)
    book.save()
    return dict(type1_entries=fixed1, type3_entries=fixed3)


def check_layout(rom):
    book = ts.TrainerBook(rom)
    bad = 0
    for tid in range(len(book.trainers.files)):
        row, party = book.trainers.files[tid], book.parties.files[tid]
        kind, count = row[0], row[3]
        if not count or not kind & 1:
            continue
        size = 16 + (2 if kind & 2 else 0)
        for i in range(count):
            h = struct.unpack_from('<%dH' % ((size - 6) // 2), party, i * size + 6)
            last = h[-1]
            first = h[1] if kind & 2 else h[0]
            if last != 0 or first == 0:
                bad += 1
    return bad


def leaders(rom):
    species, moves, items = lookup(rom)
    book = ts.TrainerBook(rom)
    report = {}
    for tid, (name, team) in LEADERS.items():
        row = bytearray(book.trainers.files[tid])
        assert row[0] == 3, (tid, row[0])
        entries = []
        for mon, item, four in team:
            entries.append(struct.pack('<BBHH', IV, 0, BASE_LEVEL, species[mon.lower()]) + struct.pack('<H', items[item.lower()])
                           + struct.pack('<4H', *(moves[m.lower().replace('high jump kick', 'high jump kick')] for m in four)) + struct.pack('<H', 0))
        row[3] = len(team)
        book.trainers.files[tid] = bytes(row)
        book.parties.files[tid] = b''.join(entries)
        report[name] = tid
    book.save()
    return report


def scaling_hook(rom):
    main = rom.loadArm9()
    save_pointer = struct.unpack_from('<I', main.sections[0].data, SAVE_POINTER_AT)[0]
    ovs = rom.loadArm9Overlays()
    perm, builder = ovs[129], ovs[BUILDER_OVERLAY]
    perm.data, builder.data = bytearray(perm.data), bytearray(builder.data)
    gap = Gap(perm, HOOK_AT, HOOK_END - HOOK_AT)
    assert not any(perm.data[HOOK_AT - perm.ramAddress:HOOK_END - perm.ramAddress]), 'the hook space is not free'
    ids = gap.put(b''.join(struct.pack('<H', tid) for tid in LEADERS) + bytes(2))
    tiers = gap.put(bytes(TIER_LEVELS))
    hook = gap.code(f'''
push {{r0, r4, lr}}
ldr r1, [r7, #0x50]
ldr r1, [r1, #0x18]
ldr r0, ids
scan:
ldrh r2, [r0]
cmp r2, #0
beq finish
adds r0, #2
cmp r2, r1
bne scan
ldr r0, save
ldr r0, [r0]
ldr r2, profile
blx r2
ldrb r0, [r0, #0x1a]
movs r4, #0
count:
cmp r0, #0
beq tier
movs r1, #1
ands r1, r0
adds r4, r4, r1
lsrs r0, r0, #1
b count
tier:
cmp r4, #7
ble ok
movs r4, #7
ok:
ldr r0, tiers
ldrb r3, [r0, r4]
finish:
str r3, [r7, #0x1c]
adds r2, r3, #0
pop {{r0, r4, pc}}
.align 2
ids: .word {ids}
save: .word {save_pointer}
profile: .word {PROFILE | 1}
tiers: .word {tiers}
''')
    at = SITE - builder.ramAddress
    assert bytes(builder.data[at:at + 4]) == SITE_BYTES, bytes(builder.data[at:at + 4]).hex()
    displacement = hook - SITE - 4
    assert displacement % 2 == 0 and -(1 << 22) <= displacement < (1 << 22)
    builder.data[at:at + 4] = struct.pack('<HH', 0xF000 | ((displacement >> 12) & 0x7FF), 0xF800 | ((displacement >> 1) & 0x7FF))
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.files[builder.fileID] = builder.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    return dict(hook=hex(hook), site=hex(SITE), gap_left=gap.end - gap.at, tiers=TIER_LEVELS)


def patch(rom):
    report = dict(layout_fix=trainer_layout_fix(rom))
    report['layout_bad_after'] = check_layout(rom)
    report['leaders'] = leaders(rom)
    report['hook'] = scaling_hook(rom)
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
