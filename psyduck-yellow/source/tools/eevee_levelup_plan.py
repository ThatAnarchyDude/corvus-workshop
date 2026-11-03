"""Proposal (not applied): level-up lists for the 17 Eeveelutions + Novareon, and the extra TM/HM entries "all TMs/HMs of its own type" (owner order 2026-10-29, option 1: existing means only).
Layout of each level-up list (34 slots max): L0 signature move; L1 the shared Eevee moves (the approved Eevee list); then up to 20 type/role moves spread from L15 to L66.
Usage (from yellow-heartgold, PYTHONPATH=tools): eevee_levelup_plan.py <rom.nds>   -> data/eeveelution-levelup-plan.json and updates data/eevee-tm-plan.json"""
import json
import struct
import sys
import ndspy.narc
import ndspy.rom
from prototype import decode_messages

EEVEE_L1 = ['Tackle', 'Tail Whip', 'Quick Attack', 'Bite', 'Swift', 'Helping Hand', 'Baton Pass', 'Take Down', 'Charm', 'Double-Edge', 'Last Resort']
PICKS = {   # species: (type, signature L0, ordered picks)
    'Vaporeon': ('Water', 'Water Gun', 'Bubble;Water Pulse;Aqua Ring;Aqua Jet;Brine;Haze;Muddy Water;Scald;Soak;Surf;Aqua Tail;Waterfall;Hydro Pump;Dive;Whirlpool;Wave Crash;Hydro Cannon'),
    'Jolteon': ('Electric', 'Thunder Shock', 'Thunder Wave;Spark;Shock Wave;Charge Beam;Thunder Fang;Volt Switch;Double Kick;Discharge;Electro Ball;Wild Charge;Agility;Thunderbolt;Thunder;Volt Tackle'),
    'Flareon': ('Fire', 'Ember', 'Will-O-Wisp;Flame Wheel;Fire Fang;Flame Burst;Fire Spin;Lava Plume;Bulk Up;Flare Blitz;Flamethrower;Fire Blast;Overheat;Heat Wave;Sacred Fire;Fire Punch'),
    'Espeon': ('Psychic', 'Confusion', 'Psybeam;Psycho Cut;Calm Mind;Zen Headbutt;Reflect;Light Screen;Extrasensory;Power Swap;Psyshock;Stored Power;Psychic;Future Sight;Psych Up;Trick Room'),
    'Umbreon': ('Dark', 'Snarl', 'Pursuit;Feint Attack;Confuse Ray;Assurance;Payback;Taunt;Torment;Crunch;Knock Off;Night Slash;Dark Pulse;Foul Play;Thief;Embargo;Sucker Punch'),
    'Leafeon': ('Grass', 'Razor Leaf', 'Absorb;Leech Seed;Magical Leaf;Synthesis;Mega Drain;Sunny Day;Giga Drain;Energy Ball;Leaf Blade;Seed Bomb;Swords Dance;Wood Hammer;Solar Beam;Leaf Storm;Grass Knot'),
    'Glaceon': ('Ice', 'Icy Wind', 'Powder Snow;Ice Shard;Mist;Aurora Beam;Ice Fang;Haze;Icicle Spear;Avalanche;Frost Breath;Freeze-Dry;Ice Beam;Icicle Crash;Blizzard;Mirror Coat'),
    'Sylveon': ('Fairy', 'Disarming Voice', 'Fairy Wind;Draining Kiss;Misty Terrain;Moonlight;Light Screen;Play Rough;Skill Swap;Dazzling Gleam;Psych Up;Moonblast;Calm Mind'),
    'Brawleon': ('Fighting', 'Mach Punch', 'Comet Punch;Mega Punch;Karate Chop;Dizzy Punch;Bullet Punch;Sucker Punch;Revenge;Fire Punch;Ice Punch;Thunder Punch;Shadow Punch;Power-Up Punch;Sky Uppercut;Cross Chop;Hammer Arm;Meteor Mash;Jet Punch;Superpower;Dynamic Punch;Ice Hammer;Plasma Fists;Close Combat'),   # ALL punching moves: Focus Punch and Drain Punch come by TM01/TM60 (type TMs are added below); the other 17 punches are level-up. 22 picks, the most a 34-slot list can hold after L0 + 11 L1 entries.
    'Venomeon': ('Poison', 'Poison Sting', 'Acid;Smog;Toxic;Venoshock;Sludge;Poison Fang;Acid Spray;Sludge Bomb;Poison Jab;Toxic Spikes;Cross Poison;Gunk Shot;Belch'),
    'Duneon': ('Ground', 'Mud-Slap', 'Sand Attack;Mud Shot;Bulldoze;Dig;Mud Bomb;Earth Power;Drill Run;StompingTantrum;Sandstorm;Spikes;Earthquake;Shore Up'),
    'Zephyreon': ('Flying', 'Gust', 'Wing Attack;Aerial Ace;Air Cutter;Roost;Tailwind;Acrobatics;Pluck;Air Slash;Bounce;Drill Peck;Hurricane;Brave Bird'),
    'Chryseon': ('Bug', 'Bug Bite', 'String Shot;Struggle Bug;Silver Wind;Signal Beam;U-turn;Leech Life;X-Scissor;Pin Missile;Quiver Dance;Bug Buzz;Megahorn'),
    'Strateon': ('Rock', 'Rock Throw', 'Rock Tomb;Rollout;Smack Down;Ancient Power;Power Gem;Rock Slide;Stealth Rock;Rock Polish;Stone Edge;Rock Blast;Head Smash'),
    'Wraitheon': ('Ghost', 'Lick', 'Astonish;Night Shade;Shadow Sneak;Confuse Ray;Curse;Spite;Shadow Ball;Hex;Phantom Force;Shadow Claw;Destiny Bond'),
    'Wyrmeon': ('Dragon', 'Dragon Breath', 'Twister;Dragon Rage;Dragon Tail;Dragon Claw;Dragon Pulse;Dragon Dance;Dragon Rush;Outrage;Draco Meteor'),
    'Ferreon': ('Steel', 'Metal Claw', 'Iron Defense;Metal Sound;Bullet Punch;Iron Head;Gyro Ball;Flash Cannon;Iron Tail;Steel Wing;Meteor Mash;Heavy Slam;Autotomize;Smart Strike;Doom Desire'),
    'Novareon': (None, 'Swift', 'Psybeam;Signal Beam;Shadow Ball;Calm Mind;Cosmic Power;Stored Power;Psychic;Meteor Mash;Hyper Beam'),
}


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    text = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    inv = {v: k for k, v in json.load(open('tools/text-map.json')).items()}
    moves = [''.join(inv.get(w, '?') for w in row if w != 65535) for row in decode_messages(text.files[750])[1]]
    idx = {n: i for i, n in enumerate(moves) if n}
    md = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/1')])
    TY = 'Normal Fighting Flying Poison Ground Rock Bug Ghost Steel Fairy Fire Water Grass Electric Psychic Ice Dragon Dark'.split()
    d = bytes(rom.loadArm9().sections[0].data)
    tab = struct.unpack_from('<108H', d, d.find(struct.pack('<6H', 264, 337, 352, 347, 46, 92)))
    plan, missing = {}, []
    tmplan = json.load(open('data/eevee-tm-plan.json'))
    for sp, (ty, sig, picks) in PICKS.items():
        names = [p for p in picks.split(';')]
        for m in [sig] + names + EEVEE_L1:
            if m not in idx:
                missing.append((sp, m))
        names = [m for m in names if m in idx and m not in EEVEE_L1 and m != sig]
        names = names[:22]
        entries = [(0, sig)] + [(1, m) for m in EEVEE_L1] + [(round(15 + k * (51 / max(1, len(names) - 1))), m) for k, m in enumerate(names)]
        assert len(entries) <= 34, sp
        plan[sp] = entries
        if ty:
            for i in range(100):
                m = moves[tab[i]]
                if m in idx and TY[bytes(md.files[idx[m]])[4]] == ty:
                    tmplan[sp].append(m)
            tmplan[sp] = sorted(set(tmplan[sp]))
    # Brawleon is built on Hitmonchan (owner idea 2026-10-29): Hitmonchan's own list and TMs, plus every other punching move and a few Fighting moves.
    ls = bytes(ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/3')]).files[0])
    sp_names = [''.join(inv.get(w, '?') for w in row if w != 65535) for row in decode_messages(text.files[237])[1]]
    hit = sp_names.index('Hitmonchan')
    base = []
    for k in range(0, 136, 4):
        m, lv = struct.unpack_from('<HH', ls, hit * 136 + k)
        if m == 0xFFFF:
            break
        base.append((lv, moves[m]))
    base = [e for e in base if e[1] != 'Focus Punch']          # Focus Punch is TM01; frees a slot
    extra = [(10, 'Comet Punch'), (14, 'Karate Chop'), (18, 'Dizzy Punch'), (20, 'Sucker Punch'), (22, 'Revenge'), (26, 'Shadow Punch'), (30, 'Power-Up Punch'), (34, 'Sky Uppercut'),
             (38, 'Hammer Arm'), (42, 'Meteor Mash'), (46, 'Jet Punch'), (48, 'Cross Chop'), (50, 'Dynamic Punch'), (54, 'Ice Hammer'), (58, 'Plasma Fists'), (62, 'Superpower')]
    plan['Brawleon'] = sorted(base + extra, key=lambda e: e[0])
    assert len(plan['Brawleon']) <= 34 and all(m in idx for _, m in plan['Brawleon'])
    v = int.from_bytes(bytes(ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/8')]).files[14])[hit * 44:hit * 44 + 16], 'little')
    tmplan['Brawleon'] = sorted(set(tmplan['Brawleon']) | {moves[tab[i]] for i in range(100) if v >> i & 1})
    json.dump(plan, open('data/eeveelution-levelup-plan.json', 'w'), indent=1)
    json.dump(tmplan, open('data/eevee-tm-plan.json', 'w'), indent=1)
    print('missing move names:', missing)
    for sp, e in plan.items():
        print(sp, len(e), 'level-up entries;', len(tmplan[sp]), 'TM/HM')


if __name__ == '__main__':
    main(sys.argv[1])
