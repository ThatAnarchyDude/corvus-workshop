"""Proposal (not applied): TM/HM compatibility for Eevee, the 17 Eeveelutions and Novareon, from each species' type and role (owner asked 2026-10-29).
Rule: every species = BASE (Eevee's current 23 TMs + a few shared extras) + its own ADD list. Names are checked against the ROM's real TM table (ARM9 0x021000CC, 100 TMs + HM01-08).
Output: data/eevee-tm-plan.json (species -> TM/HM names) and a printed summary. Usage (from yellow-heartgold, PYTHONPATH=tools): eevee_tm_plan.py <rom.nds>"""
import json
import struct
import sys
import ndspy.narc
import ndspy.rom
from prototype import decode_messages

EEVEE_CURRENT = ['Attract', 'Calm Mind', 'Captivate', 'Dig', 'Double Team', 'Facade', 'Frustration', 'Hidden Power', 'Iron Tail', 'Natural Gift', 'Protect', 'Rain Dance', 'Reflect', 'Rest', 'Return', 'Roar', 'Secret Power', 'Shadow Ball', 'Sleep Talk', 'Substitute', 'Sunny Day', 'Swagger', 'Toxic']
BASE_EXTRA = ['Giga Impact', 'Hyper Beam', 'Cut', 'Strength', 'Rock Smash', 'Flash', 'Thief', 'Shadow Claw']
ADD = {
    'Vaporeon': 'Surf Waterfall Water~Pulse Brine Whirlpool Ice~Beam Blizzard Hail Light~Screen Safeguard',
    'Jolteon': 'Thunderbolt Thunder Charge~Beam Thunder~Wave Light~Screen Energy~Ball Focus~Blast False~Swipe',
    'Flareon': 'Flamethrower Fire~Blast Overheat Will-O-Wisp Bulk~Up Brick~Break Rock~Slide',
    'Espeon': 'Psychic Dazzling~Gleam Dream~Eater Grass~Knot Light~Screen Psych~Up Skill~Swap Trick~Room Thunder~Wave',
    'Umbreon': 'Psychic Dark~Pulse Payback Taunt Torment Psych~Up Skill~Swap Thunder~Wave Light~Screen Will-O-Wisp Dream~Eater',
    'Leafeon': 'Solar~Beam Giga~Drain Energy~Ball Bullet~Seed Swords~Dance X-Scissor Grass~Knot Aerial~Ace',
    'Glaceon': 'Ice~Beam Blizzard Avalanche Hail Water~Pulse Focus~Blast Light~Screen',
    'Sylveon': 'Moonblast Dazzling~Gleam Psychic Light~Screen Safeguard Psych~Up Skill~Swap Energy~Ball',
    'Brawleon': 'Brick~Break Drain~Punch Focus~Punch Focus~Blast Bulk~Up Rock~Slide Stone~Edge Earthquake Poison~Jab Aerial~Ace Payback Swords~Dance',
    'Venomeon': 'Sludge~Bomb Poison~Jab Dark~Pulse Energy~Ball Will-O-Wisp Thunder~Wave Torment Psych~Up Light~Screen',
    'Duneon': 'Earthquake Rock~Slide Rock~Tomb Stone~Edge Sandstorm Stealth~Rock Brick~Break Gyro~Ball Bulk~Up Swords~Dance Dragon~Claw',
    'Zephyreon': 'Aerial~Ace Roost Steel~Wing Silver~Wind U-turn Pluck Swords~Dance Brick~Break Dragon~Claw Poison~Jab',
    'Chryseon': 'X-Scissor Silver~Wind U-turn Energy~Ball Giga~Drain Stealth~Rock Rock~Polish Poison~Jab Swords~Dance Light~Screen Safeguard',
    'Strateon': 'Stone~Edge Rock~Slide Rock~Tomb Stealth~Rock Earthquake Sandstorm Rock~Polish Gyro~Ball Flash~Cannon Avalanche Brick~Break Explosion',
    'Wraitheon': 'Dark~Pulse Will-O-Wisp Thunder~Wave Dream~Eater Skill~Swap Psych~Up Trick~Room Torment Taunt Light~Screen Energy~Ball Psychic',
    'Wyrmeon': 'Dragon~Claw Dragon~Pulse Earthquake Rock~Slide Stone~Edge Flamethrower Fire~Blast Thunderbolt Brick~Break Swords~Dance',
    'Ferreon': 'Flash~Cannon Gyro~Ball Steel~Wing Stealth~Rock Rock~Slide Earthquake Bulk~Up Brick~Break Explosion Thunder~Wave Light~Screen Rock~Polish',
    'Novareon': 'Psychic Flash~Cannon Dazzling~Gleam Charge~Beam Energy~Ball Thunderbolt Psych~Up Skill~Swap Trick~Room Dark~Pulse Focus~Blast Thunder~Wave Light~Screen',
}


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    text = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    inv = {v: k for k, v in json.load(open(__file__.replace('eevee_tm_plan.py', 'text-map.json'))).items()}
    moves = [''.join(inv.get(w, '?') for w in row if w != 65535) for row in decode_messages(text.files[750])[1]]
    d = bytes(rom.loadArm9().sections[0].data)
    tab = struct.unpack_from('<108H', d, d.find(struct.pack('<6H', 264, 337, 352, 347, 46, 92)))
    avail = {moves[tab[i]] for i in range(100)}
    plan = {}
    for name in ['Eevee'] + list(ADD):
        picks = EEVEE_CURRENT + BASE_EXTRA + ([m.replace('~', ' ') for m in ADD[name].split()] if name != 'Eevee' else [])
        bad = [m for m in picks if m not in avail]
        assert not bad, (name, bad)
        plan[name] = sorted(set(picks))
    json.dump(plan, open(__file__.replace('tools/eevee_tm_plan.py', 'data/eevee-tm-plan.json'), 'w'), indent=1)
    for n, l in plan.items():
        print(n, len(l))


if __name__ == '__main__':
    main(sys.argv[1])
