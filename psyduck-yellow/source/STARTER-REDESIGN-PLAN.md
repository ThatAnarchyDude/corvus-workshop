# Starter redesign: ROM compatibility check (step 4 of the owner's plan), 2026-10-29, ROM 0116
Design source: the owner's proposal (Eevee, 17 standard Eeveelutions + Novareon, Psyduck/Golduck Water/Psychic). Nothing here is implemented.

## Moves: tier check (name found in the ROM's move table; data from a/0/1/1)
- CORE/EXPANDED (all present, with type/split/power in the table): every move named in the proposal except the four custom ones. The table reaches Gen 9 (Psychic Noise is id 920), so the "later-generation" moves exist as DATA: Scald 506, Flip Turn 815, Liquidation 713, Psychic Terrain 681, Expanding Force 800, Stored Power 503, Mystical Power 835, Aqua Step 875, Psychic Noise 920, Wave Crash 837, Cosmic Power 322, Meteor Mash 309.
- NOT YET PROVEN: whether the battle engine actually runs each move's special effect (data present is not the same as implemented). Suspicious from the table: Psyshock (effect 0, plain special damage: would hit Sp. Def, not Defense), Stored Power (effect 0, power 20: no boost scaling), Expanding Force (effect 0, no terrain boost), Hydro Cannon (effect 80 = recharge turn like Hyper Beam, so "ultimate finisher" costs a turn). Needs a live test per move before we rely on it.
- CUSTOM (not in the ROM): Eon Pulse, Mind Current, Starfall Pulse, Starfall Charge.
  - Eon Pulse (Normal, special 60, 100% own Sp. Atk +1) and Mind Current (Water special 80, 20% Sp. Def -1) can probably be DATA-ONLY clones of existing effects (Charge Beam, Shadow Ball) but need new move ids, names, text, and an animation pointer.
  - Starfall Pulse/Charge need a Stellar TYPE (the type table has 18 types, no Stellar) and an "always super effective" rule: real battle-code work. Keep for last.

## Items
Present: Black Belt 241, Soft Sand 237, Float Stone 539, Silver Powder 222, Hard Stone 238, Spell Tag 247, Dragon Scale 235, Metal Coat 233, Fairy Feather 2401, Dawn/Dusk/Leaf/Ice/Water/Thunder/Fire Stones, Poison Barb 245 (a possible Venomeon item), Sandwich 1830.
Venomeon's item is Toxic Orb (owner correction; it was misread as 'Toxic Stone'). Missing: Stellar Sandwich (a duplicate of Sandwich, as planned).

## Species
Already in the ROM (owner-confirmed 2026-10-29): starter Eevee 1561/Mega 1562, starter Psyduck 1563/Mega 1564, and the nine starter Eeveelutions with their Megas at 1565-1582 (Vaporeon, Jolteon, Flareon, Espeon, Umbreon, Leafeon, Glaceon, Sylveon, Novareon; each a normal+Mega pair). NOT in the ROM: Brawleon, Venomeon, Duneon, Zephyreon, Chryseon, Strateon, Wraitheon, Wyrmeon, Ferreon are 9 new species, each needing a normal and a starter version (18 new species) plus art (none yet), stats, learnsets, TM rows, dex entries, evolution rows and Mega-table decisions.

## Engine limits found
- The native evolution table holds at most 9 rows per species (56-byte rows file). Starter Eevee already uses all 9. 17 evolutions x two methods (use the item OR level up holding it) does not fit; the project's stone-shortcut table (ARM9) must grow, and "level up while holding" needs its own method.
- Level-up learnset has 34 slots per species (136 bytes): enough for the proposed lists.
- Surf: giving Psyduck Surf by level-up (L31) means the field Surf only needs the Soul Badge (Kanto Surf already follows the Soul Badge). Check this does not let Surf in before the intended point.

## Questions for the owner (decisions)
1. How does Psyduck (normal and starter) evolve into Golduck: Moon Stone as now, or something else?
2. Hydro Cannon recharges: keep as the finisher, or swap for Hydro Pump / Surf / Wave Crash?
3. Normal wild Eevee: does it get the same extended line, or only the starter Eevee?
4. Starter Golduck needs its own species (new row) plus the single Mega (Psyduckite): confirm one shared Mega form for both.

## Precedence rule (owner, 2026-10-29)
What is decided in this plan supersedes any contradictory or outdated information in the original "Eevee: New Horizons" plan/PDF.

## Owner decisions (2026-10-29)
1. Psyduck -> Golduck by Moon Stone (normal and starter). 2. Hydro Cannon stays the finisher (keeps its recharge turn). 3. EVERY Eevee (normal wild and starter) gets the extended line, Novareon included; only the starter Eevees (and their evolutions) and starter Psyduck/Golduck can Mega Evolve. 4. One shared Mega for starter Psyduck and starter Golduck.

## Step 1 draft: exact level-up lists (for the owner to approve; not implemented)
ALL Eevee (normal 133 and starter 1561, identical; owner correction 2026-10-29): L1 Tackle, Tail Whip; L5 Quick Attack; L8 Bite; L12 Swift; L16 Helping Hand; L20 Baton Pass; L24 Take Down; L28 Charm; L32 Double-Edge; L36 Last Resort. (Eon Pulse is a later custom swap for Swift.)
Psyduck (normal 54 and starter 1563, identical): L1 Scratch, Water Gun; L4 Tail Whip; L7 Confusion; L10 Disable; L13 Aqua Jet; L16 Psybeam; L19 Zen Headbutt; L22 Water Pulse; L25 Calm Mind; L28 Psychic; L31 Surf; L34 Aqua Tail; L37 Future Sight; L40 Hydro Pump; L43 Amnesia; L46 Extrasensory; L49 Ice Beam; L52 Psyshock; L55 Hydro Cannon.
Golduck (normal 55 and a NEW starter Golduck species): L0 Psychic; L36 Aqua Tail; L39 Calm Mind; L42 Zen Headbutt; L45 Surf; L48 Future Sight; L51 Ice Beam; L54 Hydro Pump; L57 Psyshock; L60 Amnesia; L63 Psychic; L66 Hydro Cannon.
OWNER APPROVED (2026-10-29; Psychic L28 and Surf L31 pacing confirmed): all three lists as written, with the Golduck catch-up fix below. PROBLEM FOUND (fix approved): a Psyduck that evolves before L31 would never be offered Psybeam/Water Pulse/Calm Mind/Surf etc. (they are only on Psyduck's list). Proposed fix (needs approval): Golduck's list ALSO carries Psyduck's entries up to L34 (Scratch, Water Gun, Confusion, Aqua Jet... Aqua Tail) at the same levels, then the owner's L36+ list. 25 entries, the table holds 34. Moves the Pokemon already knows are skipped automatically.

## Step 2 draft: combat identity + evolution quest per Eeveelution (owner to approve; nothing implemented)
Reference read: Eevee-New-Horizons.md/pdf (art, dex entries, one shared "Mega Eevee (type)" design, Eonite / Novareonite). It has NO moves, stats or evolution methods, so the roles and quests below are my proposals. Methods: every evolution works by USING the item on Eevee OR by levelling up while Eevee HOLDS it (owner rule). Source places are proposals using Kanto locations we already build.
| Evolution | Type | Item | Proposed source / quest | Combat identity (role) |
|---|---|---|---|---|
| Vaporeon | Water | Water Stone | Celadon Dept. Store (stone shelf) | bulky special wall; Water + Ice |
| Jolteon | Electric | Thunder Stone | Celadon Dept. Store | fast special sweeper |
| Flareon | Fire | Fire Stone | Celadon Dept. Store | physical Fire bruiser |
| Espeon | Psychic | Dawn Stone | Saffron City reward (Sabrina side) | fast special Psychic attacker |
| Umbreon | Dark | Dusk Stone | Lavender Town / Pokemon Tower | defensive status stalling |
| Leafeon | Grass | Leaf Stone | Celadon (Erika side) | physical Grass, high Defense |
| Glaceon | Ice | Ice Stone | Seafoam Islands | special Ice attacker |
| Sylveon | Fairy | Fairy Feather (2401) | Mt. Moon summit (Clefairy) | special Fairy support |
| Brawleon | Fighting | Black Belt (241) | Saffron Dojo, after beating the Karate Master (the owner's sidequest) | physical Fighting, priority + Sp.Def |
| Venomeon | Poison | Toxic Orb (272) | Pokemon Mansion, Cinnabar | poison/status attacker |
| Duneon | Ground | Soft Sand (237) | Diglett's Cave | slow physical Ground tank |
| Zephyreon | Flying | Float Stone (539) | Route 16/17 (Cycling Road end) | fast physical Flying |
| Chryseon | Bug | Silver Powder (222) | Viridian Forest (hidden) | pivot/utility Bug |
| Strateon | Rock | Hard Stone (238) | Rock Tunnel | defensive Rock, hazards |
| Wraitheon | Ghost | Spell Tag (247) | Pokemon Tower | special Ghost, status |
| Wyrmeon | Dragon | Dragon Scale (235) | Safari Zone | mixed Dragon attacker |
| Ferreon | Steel | Metal Coat (233) | Silph Co. | physical Steel wall |
| Novareon | Stellar | Stellar Sandwich (copy of Sandwich 1830, new id) | a sidequest reward (owner to name it) | special/flexible Stellar |
Engine status: use-an-item evolution = works (shortcut table, needs 18 more rows per Eevee id: 133 and 1561). Level up holding an item = needs a new method (check hg-engine's hold-item method first). Nine new species x (normal + starter) + Megas shared via the "Mega Eevee (type)" design. The item sources above need map/item-ball edits in the listed areas. Stellar type and Starfall moves wait for the custom-mechanics pass.
DECIDED (owner, 2026-10-29): the plain Sandwich is "traded" (in a sense) for the Stellar Sandwich, and only the Stellar Sandwich evolves an Eevee into Novareon. Still to design: who trades it, where, and what the plain Sandwich's own role becomes (today it is a Mart item, id 1830, that evolves the starter into Novareon).

## Step 2b draft: base stats and abilities (owner asked 2026-10-29; for review, not implemented)
Current ROM (HP/Atk/Def/SpA/SpD/Spe = total): Psyduck 50/52/48/65/50/55 = 320 (Damp; hidden Cloud Nine); Golduck 80/82/78/95/80/85 = 500 (Water/Psychic); Eevee 55/55/50/45/65/55 = 325. All eight existing Eeveelutions total 525 (one ability each, no hidden ability). Novareon currently copies Umbreon's 95/65/110/60/130/65, type Stellar.
PROPOSED (all of normal and starter versions identical):
- Psyduck 50/40/45/75/60/50 = 320 (decent Sp.Atk, good Sp.Def, moderate Speed). Reasoning (owner's reference data 2026-10-29): starter basic forms are 308-320 and Yellow's own two-stage starter Pikachu is 320 (Raichu 485), Eevee 325 (Eeveelutions 525). Same total as vanilla Psyduck, reshaped toward Sp.Atk/Sp.Def. Option B (350) was offered and not chosen; this one is the default unless the owner objects.
- Golduck 85/70/75/125/100/75 = 530 (the "powerhouse"; Water/Psychic). Was 540; lowered to stay at or under Swampert's 535. Abilities unchanged for now (owner: custom Golduck ability on hold).
- The nine new Eeveelutions, total 525 each, one-line role, ability 1 / ability 2 (existing abilities only; availability of each ability's effect in battle must be live-checked):
| Species | Type | Stats HP/Atk/Def/SpA/SpD/Spe | Role | Abilities |
|---|---|---|---|---|
| Brawleon | Fighting | 90/130/75/45/100/85 | physical bruiser, priority, Sp.Def | Iron Fist / Inner Focus (hidden: Guts) |
| Venomeon | Poison | 85/65/70/120/105/80 | special poison/status attacker | Poison Point / Synchronize |
| Duneon | Ground | 110/120/115/45/75/60 | slow physical tank | Sand Force / Sand Veil |
| Zephyreon | Flying | 65/110/70/60/90/130 | fast physical Flying | Super Luck / Keen Eye |
| Chryseon | Bug | 85/85/100/85/100/70 | pivot / utility | Shed Skin / Swarm |
| Strateon | Rock | 90/90/140/50/105/50 | defensive Rock, hazards | Sturdy / Solid Rock |
| Wraitheon | Ghost | 75/55/75/125/100/95 | special Ghost, status | Cursed Body / Pressure |
| Wyrmeon | Dragon | 85/110/80/110/70/70 | mixed Dragon attacker | Rough Skin / Moxie |
| Ferreon | Steel | 80/100/135/55/95/60 | physical Steel wall | Clear Body / Heavy Metal |
Notes: Venomeon avoids Poison Heal/Toxic Boost because a pure Poison type cannot be poisoned (they would never trigger, even with the Toxic Orb). Novareon stats (still Umbreon's) get their own proposal when the owner asks.
DONE ON OWNER ORDER (2026-10-29): Novareon (starter 1581) and Mega Novareon (1582) now have Beast Boost (ability 224) in all three ability slots "for now" (tools/novareon_ability.py, build 0117). Beast Boost's battle effect is not verified.

## Mega stats (owner approved 2026-10-29; not implemented)
Reference (owner's tables): final starters are 525-535 (Gen 7+ all 530); Megas add a flat +100. In the ROM today every Mega copies its base form's stats (no boost): 1562/1564/1566...1582 rows equal their bases.
DECIDED (owner, final 2026-10-29): Option 2 = a data-only script (tools/mega_bonus.py, not written yet) fills every Mega row as base form + 20 in EACH of the six stats, HP included = +120 BST (replaces the earlier +100 / 600 / 630 ideas). Eeveelution Megas 525 -> 645, Mega Eevee 325 -> 445, Mega Novareon 645, the single shared Mega Psyduck = Golduck 530 + 120 = 650. Re-run the script after any base-stat change.
RISKS to test live: (a) a Mega with higher base HP changes max HP when it Mega Evolves mid-battle (HG's Mega code may or may not recalculate HP; if it glitches, fall back to +20 on the five other stats); (b) DECIDED (owner, 2026-10-29): option B for ALL Megas, stock included: every Mega row (the 95 stock Megas and the project's own) becomes its OWN BASE FORM + 20 in each of the six stats (+120). The official stat spreads of the stock Megas (e.g. Mega Charizard X 634) are replaced (-> 534+120 = 654). The script needs the Mega table (species-to-Mega pairs, 106 entries) to find each Mega's base; multi-Mega species (Charizard X/Y, Mewtwo X/Y) each get base + 120. Watch for Megas with a changed ability/type, which keep their own type and ability but get the base's stats.
Open: none for the Mega spread (it is the flat +20 rule); do the Mega ability slots follow the base form or get a Mega-only ability.

## Step 3 draft: TM/HM/tutor compatibility for Psyduck and Golduck (checked against the ROM, 2026-10-29; not implemented)
Rule: Psyduck and Golduck, normal and starter, share one compatibility row (today Golduck has extras Psyduck lacks: Hyper Beam, Giga Impact, Focus Blast, Grass Knot, Rock Climb).
Owner's proposed pool, checked against the ROM's real 100 TM + 8 HM table:
- ALREADY a TM and already allowed for Golduck: Water Pulse (TM03), Surf (HM03), Waterfall (HM07), Rain Dance (TM18), Psychic (TM29), Calm Mind (TM04), Ice Beam (TM13), Blizzard (TM14), Brick Break (TM31), Focus Blast (TM52), Aerial Ace (TM40), Dig (TM28), Substitute (TM90), Protect (TM17), Rest (TM44), Sleep Talk (TM82), Toxic (TM06), Light Screen (TM16).
- IS a TM but Golduck cannot learn it yet (just switch the compatibility bit on): Shadow Ball (TM30), Rock Tomb (TM39), Reflect (TM33).
- NOT a TM, but on the approved level-up lists (no TM needed): Water Gun, Aqua Tail, Hydro Pump, Confusion, Psybeam, Zen Headbutt, Future Sight, Amnesia, Psyshock, Extrasensory, Disable.
- NOT a TM and NOT on any level-up list (need a TM slot or a tutor): Dive, Ice Punch, Signal Beam, Encore.
Engine facts: the TM table (ARM9 0x021000CC, copy in overlay 129) has 92 TMs + HM01-HM08 and 8 more entries (HM09-16, mostly placeholders). A TM's move can be swapped (done before for TM34/TM58); candidates with little use: TM21 Frustration, TM27 Return, TM43 Secret Power, TM49 Snatch, TM63 Embargo, TM78 Captivate, TM83 Natural Gift. Replacing one means recomputing that column's bit for every species and renaming the item.
Proposal: use TM43 -> Ice Punch, TM49 -> Signal Beam, TM63 -> Encore, TM78 -> Dive (Dive is also a Johto HM-style move: check its field use), all four for Psyduck/Golduck only where they fit, and decide the other species per move type later.
Still to design: the same table for Eevee, the 17 Eeveelutions and Novareon (owner has not given pools); suggested starting point is each species' type and role from the step 2 table.

## Step 3b draft: TM/HM compatibility for Eevee, the 17 Eeveelutions and Novareon (proposed from type + role; not applied; data in data/eevee-tm-plan.json, generator tools/eevee_tm_plan.py)
Rule: every species = the shared BASE below + its own list. Every TM name was checked against the ROM's real TM table. The four TM slots the owner will choose for Psyduck/Golduck (Ice Punch, Signal Beam, Encore, Dive) may change this table later; Snatch/Embargo/Captivate/Secret Power/Natural Gift are the likely replacement candidates, so nothing here depends on Snatch or Embargo.
BASE (Eevee and everything that evolves from it): Attract, Calm Mind, Captivate, Cut, Dig, Double Team, Facade, Flash, Frustration, Giga Impact, Hidden Power, Hyper Beam, Iron Tail, Natural Gift, Protect, Rain Dance, Reflect, Rest, Return, Roar, Rock Smash, Secret Power, Shadow Ball, Shadow Claw, Sleep Talk, Strength, Substitute, Sunny Day, Swagger, Thief, Toxic (Eevee itself = this only; its old 23 plus Giga Impact, Hyper Beam, Cut, Strength, Rock Smash, Flash, Thief, Shadow Claw, so the starter can carry the field HMs).
| Species | Total | Adds on top of BASE |
|---|---|---|
| Vaporeon | 41 | Blizzard, Brine, Hail, Ice Beam, Light Screen, Safeguard, Surf, Water Pulse, Waterfall, Whirlpool |
| Jolteon | 39 | Charge Beam, Energy Ball, False Swipe, Focus Blast, Light Screen, Thunder, Thunder Wave, Thunderbolt |
| Flareon | 38 | Brick Break, Bulk Up, Fire Blast, Flamethrower, Overheat, Rock Slide, Will-O-Wisp |
| Espeon | 40 | Dazzling Gleam, Dream Eater, Grass Knot, Light Screen, Psych Up, Psychic, Skill Swap, Thunder Wave, Trick Room |
| Umbreon | 42 | Dark Pulse, Dream Eater, Light Screen, Payback, Psych Up, Psychic, Skill Swap, Taunt, Thunder Wave, Torment, Will-O-Wisp |
| Leafeon | 39 | Aerial Ace, Bullet Seed, Energy Ball, Giga Drain, Grass Knot, Solar Beam, Swords Dance, X-Scissor |
| Glaceon | 38 | Avalanche, Blizzard, Focus Blast, Hail, Ice Beam, Light Screen, Water Pulse |
| Sylveon | 39 | Dazzling Gleam, Energy Ball, Light Screen, Moonblast, Psych Up, Psychic, Safeguard, Skill Swap |
| Brawleon | 43 | Aerial Ace, Brick Break, Bulk Up, Drain Punch, Earthquake, Focus Blast, Focus Punch, Payback, Poison Jab, Rock Slide, Stone Edge, Swords Dance |
| Venomeon | 40 | Dark Pulse, Energy Ball, Light Screen, Poison Jab, Psych Up, Sludge Bomb, Thunder Wave, Torment, Will-O-Wisp |
| Duneon | 42 | Brick Break, Bulk Up, Dragon Claw, Earthquake, Gyro Ball, Rock Slide, Rock Tomb, Sandstorm, Stealth Rock, Stone Edge, Swords Dance |
| Zephyreon | 41 | Aerial Ace, Brick Break, Dragon Claw, Pluck, Poison Jab, Roost, Silver Wind, Steel Wing, Swords Dance, U-turn |
| Chryseon | 42 | Energy Ball, Giga Drain, Light Screen, Poison Jab, Rock Polish, Safeguard, Silver Wind, Stealth Rock, Swords Dance, U-turn, X-Scissor |
| Strateon | 43 | Avalanche, Brick Break, Earthquake, Explosion, Flash Cannon, Gyro Ball, Rock Polish, Rock Slide, Rock Tomb, Sandstorm, Stealth Rock, Stone Edge |
| Wraitheon | 43 | Dark Pulse, Dream Eater, Energy Ball, Light Screen, Psych Up, Psychic, Skill Swap, Taunt, Thunder Wave, Torment, Trick Room, Will-O-Wisp |
| Wyrmeon | 41 | Brick Break, Dragon Claw, Dragon Pulse, Earthquake, Fire Blast, Flamethrower, Rock Slide, Stone Edge, Swords Dance, Thunderbolt |
| Ferreon | 43 | Brick Break, Bulk Up, Earthquake, Explosion, Flash Cannon, Gyro Ball, Light Screen, Rock Polish, Rock Slide, Stealth Rock, Steel Wing, Thunder Wave |
| Novareon | 44 | Charge Beam, Dark Pulse, Dazzling Gleam, Energy Ball, Flash Cannon, Focus Blast, Light Screen, Psych Up, Psychic, Skill Swap, Thunder Wave, Thunderbolt, Trick Room |
Changes versus today for the existing eight: Umbreon keeps Psychic; Jolteon keeps False Swipe; nothing real is dropped (the old '-', 'Pound', 'Karate Chop' entries are placeholder HM09-16 bits; Snatch is a likely replacement TM). Leafeon/Glaceon regain Reflect and Sylveon regains Captivate/Natural Gift from BASE. Every Eeveelution gains Cut/Strength/Rock Smash/Flash (they are all HM carriers now).

## Owner request 2026-10-29: each Eeveelution can access ALL moves of its own type (Brawleon also ALL punching moves)
Counts in the ROM's move table (moves with power, or status moves, by type; TMs/HMs of that type in brackets): Fighting 55 (7), Water 47 (7), Fire 45 (5), Electric 46 (4), Grass 57 (5), Ice 31 (4), Psychic 77 (8), Dark 50 (8), Fairy 29 (3), Poison 34 (3), Ground 29 (2), Flying 29 (4), Bug 32 (3), Rock 24 (6), Ghost 32 (2), Dragon 29 (2), Steel 35 (4), Normal 200 (28). Punch-named moves (Brawleon): Comet Punch, Mega Punch, Fire/Ice/Thunder Punch, Dizzy Punch, Mach Punch, Dynamic Punch, Focus Punch, Meteor Mash, Shadow Punch, Sky Uppercut, Hammer Arm, Sucker Punch, Drain Punch, Bullet Punch, Power-Up Punch, Ice Hammer, Plasma Fists, Jet Punch (20; Gen 4 has no "punch" flag in the move data, Iron Fist uses a list).
The count includes later-generation moves the battle engine may not run (Max Knuckle, Meteor Assault, Triple Arrows, Combat Torque, Upper Hand ...); each must be live-tested.
Means available today: TM/HM bits (only ~100 TM slots in total), the level-up list (34 slots, about 14 already used by Eevee's inherited moves), egg moves (only via hatching). Together they cannot reach "all moves of a type" for most types (Fighting: 7 TMs + roughly 20 level-up = about 27 of 55). The only route to "all" is a Move Tutor mechanism (not present in hg-engine; HG has a few fixed tutors): a custom NPC that teaches any move of an Eeveelution's own type (and Brawleon's punches). OWNER TO CHOOSE.

## Step 3c draft (owner chose option 1, existing means only): level-up lists + all type TMs for the Eeveelutions (not applied; data/eeveelution-levelup-plan.json, data/eevee-tm-plan.json; generator tools/eevee_levelup_plan.py)
Each list = L0 signature move; L1 the shared Eevee moves (Tackle, Tail Whip, Quick Attack, Bite, Swift, Helping Hand, Baton Pass, Take Down, Charm, Double-Edge, Last Resort); then the species' own picks from L15 to L66 (spread evenly; exact levels to be tuned). Every TM/HM of the species' own type is also allowed (counts in the table).
BRAWLEON: access to ALL 20 punching moves (checked by script): Focus Punch (TM01) and Drain Punch (TM60) by TM, the other 18 by level-up (Mach Punch at L0). Its list is full at 34 entries.
Coverage limits: only the moves that fit in 34 slots plus the type's TMs are reachable; the rest of each type's moves stay out of reach (option 2, a move tutor, was not chosen).
| Species | Level-up entries | TM/HM | Own picks (in learning order) |
|---|---|---|---|
| Vaporeon | 29 | 41 | L0 Water Gun; L15 Bubble, L18 Water Pulse, L21 Aqua Ring, L25 Aqua Jet, L28 Brine, L31 Haze, L34 Muddy Water, L37 Scald, L40 Soak, L44 Surf, L47 Aqua Tail, L50 Waterfall, L53 Hydro Pump, L56 Dive, L60 Whirlpool, L63 Wave Crash, L66 Hydro Cannon |
| Jolteon | 26 | 39 | L0 Thunder Shock; L15 Thunder Wave, L19 Spark, L23 Shock Wave, L27 Charge Beam, L31 Thunder Fang, L35 Volt Switch, L39 Double Kick, L42 Discharge, L46 Electro Ball, L50 Wild Charge, L54 Agility, L58 Thunderbolt, L62 Thunder, L66 Volt Tackle |
| Flareon | 26 | 38 | L0 Ember; L15 Will-O-Wisp, L19 Flame Wheel, L23 Fire Fang, L27 Flame Burst, L31 Fire Spin, L35 Lava Plume, L39 Bulk Up, L42 Flare Blitz, L46 Flamethrower, L50 Fire Blast, L54 Overheat, L58 Heat Wave, L62 Sacred Fire, L66 Fire Punch |
| Espeon | 26 | 40 | L0 Confusion; L15 Psybeam, L19 Psycho Cut, L23 Calm Mind, L27 Zen Headbutt, L31 Reflect, L35 Light Screen, L39 Extrasensory, L42 Power Swap, L46 Psyshock, L50 Stored Power, L54 Psychic, L58 Future Sight, L62 Psych Up, L66 Trick Room |
| Umbreon | 27 | 45 | L0 Snarl; L15 Pursuit, L19 Feint Attack, L22 Confuse Ray, L26 Assurance, L30 Payback, L33 Taunt, L37 Torment, L40 Crunch, L44 Knock Off, L48 Night Slash, L51 Dark Pulse, L55 Foul Play, L59 Thief, L62 Embargo, L66 Sucker Punch |
| Leafeon | 27 | 39 | L0 Razor Leaf; L15 Absorb, L19 Leech Seed, L22 Magical Leaf, L26 Synthesis, L30 Mega Drain, L33 Sunny Day, L37 Giga Drain, L40 Energy Ball, L44 Leaf Blade, L48 Seed Bomb, L51 Swords Dance, L55 Wood Hammer, L59 Solar Beam, L62 Leaf Storm, L66 Grass Knot |
| Glaceon | 26 | 38 | L0 Icy Wind; L15 Powder Snow, L19 Ice Shard, L23 Mist, L27 Aurora Beam, L31 Ice Fang, L35 Haze, L39 Icicle Spear, L42 Avalanche, L46 Frost Breath, L50 Freeze-Dry, L54 Ice Beam, L58 Icicle Crash, L62 Blizzard, L66 Mirror Coat |
| Sylveon | 23 | 39 | L0 Disarming Voice; L15 Fairy Wind, L20 Draining Kiss, L25 Misty Terrain, L30 Moonlight, L35 Light Screen, L40 Play Rough, L46 Skill Swap, L51 Dazzling Gleam, L56 Psych Up, L61 Moonblast, L66 Calm Mind |
| Brawleon | 34 | 43 | L0 Mach Punch; L15 Comet Punch, L17 Mega Punch, L20 Karate Chop, L22 Dizzy Punch, L25 Bullet Punch, L27 Sucker Punch, L30 Revenge, L32 Fire Punch, L34 Ice Punch, L37 Thunder Punch, L39 Shadow Punch, L42 Power-Up Punch, L44 Sky Uppercut, L47 Cross Chop, L49 Hammer Arm, L51 Meteor Mash, L54 Jet Punch, L56 Superpower, L59 Dynamic Punch, L61 Ice Hammer, L64 Plasma Fists, L66 Close Combat |
| Venomeon | 25 | 40 | L0 Poison Sting; L15 Acid, L19 Smog, L24 Toxic, L28 Venoshock, L32 Sludge, L36 Poison Fang, L40 Acid Spray, L45 Sludge Bomb, L49 Poison Jab, L53 Toxic Spikes, L58 Cross Poison, L62 Gunk Shot, L66 Belch |
| Duneon | 24 | 42 | L0 Mud-Slap; L15 Sand Attack, L20 Mud Shot, L24 Bulldoze, L29 Dig, L34 Mud Bomb, L38 Earth Power, L43 Drill Run, L47 StompingTantrum, L52 Sandstorm, L57 Spikes, L61 Earthquake, L66 Shore Up |
| Zephyreon | 24 | 42 | L0 Gust; L15 Wing Attack, L20 Aerial Ace, L24 Air Cutter, L29 Roost, L34 Tailwind, L38 Acrobatics, L43 Pluck, L47 Air Slash, L52 Bounce, L57 Drill Peck, L61 Hurricane, L66 Brave Bird |
| Chryseon | 23 | 42 | L0 Bug Bite; L15 String Shot, L20 Struggle Bug, L25 Silver Wind, L30 Signal Beam, L35 U-turn, L40 Leech Life, L46 X-Scissor, L51 Pin Missile, L56 Quiver Dance, L61 Bug Buzz, L66 Megahorn |
| Strateon | 23 | 43 | L0 Rock Throw; L15 Rock Tomb, L20 Rollout, L25 Smack Down, L30 Ancient Power, L35 Power Gem, L40 Rock Slide, L46 Stealth Rock, L51 Rock Polish, L56 Stone Edge, L61 Rock Blast, L66 Head Smash |
| Wraitheon | 23 | 43 | L0 Lick; L15 Astonish, L20 Night Shade, L25 Shadow Sneak, L30 Confuse Ray, L35 Curse, L40 Spite, L46 Shadow Ball, L51 Hex, L56 Phantom Force, L61 Shadow Claw, L66 Destiny Bond |
| Wyrmeon | 21 | 41 | L0 Dragon Breath; L15 Twister, L21 Dragon Rage, L28 Dragon Tail, L34 Dragon Claw, L40 Dragon Pulse, L47 Dragon Dance, L53 Dragon Rush, L60 Outrage, L66 Draco Meteor |
| Ferreon | 25 | 43 | L0 Metal Claw; L15 Iron Defense, L19 Metal Sound, L24 Bullet Punch, L28 Iron Head, L32 Gyro Ball, L36 Flash Cannon, L40 Iron Tail, L45 Steel Wing, L49 Meteor Mash, L53 Heavy Slam, L58 Autotomize, L62 Smart Strike, L66 Doom Desire |
| Novareon | 21 | 44 | L0 Swift; L15 Psybeam, L21 Signal Beam, L28 Shadow Ball, L34 Calm Mind, L40 Cosmic Power, L47 Stored Power, L53 Psychic, L60 Meteor Mash, L66 Hyper Beam |

## Brawleon built on Hitmonchan (owner idea 2026-10-29; replaces the earlier Brawleon list above)
Base = Hitmonchan's own level-up list and TM/HM set (read from the ROM: Drain Punch at L0, Mach Punch, Vacuum Wave, Detect, Bullet Punch, Quick Guard, Thunder/Ice/Fire Punch, Agility, Mega Punch, Close Combat, Counter; Focus Punch moved to TM01 to free a slot) plus every other punching move and a few Fighting moves. The shared Eevee L1 moves are dropped for Brawleon (the slots are needed; an evolving Eevee keeps the moves it already knows). All 20 punching moves are reachable (checked). 34 of 34 slots used, 47 TMs/HMs.
Brawleon level-up: L0 Drain Punch, L1 Feint, L1 Tackle, L1 Helping Hand, L1 Fake Out, L1 Focus Energy, L4 Mach Punch, L8 Vacuum Wave, L10 Comet Punch, L12 Detect, L14 Karate Chop, L16 Bullet Punch, L18 Dizzy Punch, L20 Sucker Punch, L21 Quick Guard, L22 Revenge, L24 Thunder Punch, L24 Ice Punch, L24 Fire Punch, L26 Shadow Punch, L28 Agility, L30 Power-Up Punch, L32 Mega Punch, L34 Sky Uppercut, L36 Close Combat, L38 Hammer Arm, L40 Counter, L42 Meteor Mash, L46 Jet Punch, L48 Cross Chop, L50 Dynamic Punch, L54 Ice Hammer, L58 Plasma Fists, L62 Superpower.
Ability proposal changed: Iron Fist (Hitmonchan's own hidden ability, +20% punching moves) / Inner Focus, replacing Guts / Inner Focus. Stats stay 90/130/75/45/100/85.

OWNER DECIDED (2026-10-29): Brawleon abilities = Iron Fist / Inner Focus, hidden ability Guts. (The existing eight Eeveelutions have no hidden ability today; whether the other new ones get one is open. Personal-data byte 26 holds the hidden ability.)

## Hidden abilities (owner order 2026-10-29: all starter Pokemon and every species in their line get one; proposal, not applied)
Facts: the project's hidden-ability helper (starter_properties.py, a code table keyed by species id, hidden chance 1/3) already has rows for the base species: Psyduck/Golduck Swift Swim (33), Eevee Anticipation (107), Vaporeon Hydration (93), Jolteon Quick Feet (95), Flareon Guts (62), Espeon none, Umbreon Inner Focus (39), Leafeon Chlorophyll (34), Glaceon Ice Body (115), Togepi/Togetic Super Luck (105). It has NO rows for Sylveon, Novareon, the nine new species, or (unchecked) the starter species ids 1561-1582 (they may map to their base species). Personal-data byte 26 holds a species' hidden ability.
| Species | Ability 1 / 2 | Proposed hidden ability |
|---|---|---|
| Psyduck, Golduck (normal+starter) | Damp / - | Swift Swim (existing row) |
| Eevee (all) | Run Away / - | Anticipation (existing row) |
| Vaporeon | Water Absorb | Hydration |
| Jolteon | Volt Absorb | Quick Feet |
| Flareon | Flash Fire | Guts |
| Espeon | Synchronize | Magic Bounce |
| Umbreon | Synchronize | Inner Focus |
| Leafeon | Leaf Guard | Chlorophyll |
| Glaceon | Snow Cloak | Ice Body |
| Sylveon | Cute Charm | Pixilate |
| Brawleon | Iron Fist / Inner Focus | Guts (owner decided) |
| Venomeon | Poison Point / Synchronize | Poison Touch |
| Duneon | Sand Force / Sand Veil | Sand Rush |
| Zephyreon | Super Luck / Keen Eye | Unburden |
| Chryseon | Shed Skin / Swarm | Compound Eyes |
| Strateon | Sturdy / Solid Rock | Rock Head |
| Wraitheon | Cursed Body / Pressure | Infiltrator |
| Wyrmeon | Rough Skin / Moxie | Multiscale |
| Ferreon | Clear Body / Heavy Metal | Filter |
| Novareon | Download / Tera Shell (owner DECIDED 2026-10-29; Protean/Libero rejected) | Beast Boost (the ROM still has Beast Boost in every slot until this is built). Tera Shell is Gen 9 (ability id 308): live-test it; fallback Purifying Salt or Trace |
All abilities exist in the ROM's ability list (Compound Eyes is spelled differently there: look it up). Whether the battle engine runs each effect (Magic Bounce, Pixilate, Poison Touch, Sand Rush, Infiltrator, Multiscale, Filter) is not verified: live-test before relying on them. Mega forms keep the base form's abilities for now.

OWNER DECIDED (2026-10-29): Novareon = Download / Tera Shell, hidden Beast Boost (Stellar combines all types, so Tera Shell fits; Beast Boost needs knock-outs so it is best as a hidden ability).

OWNER DECIDED (2026-10-29, final; supersedes the Download / Tera Shell / Beast Boost line above): Novareon = Ability 0 Adaptability, Ability 1 Tera Shell, Hidden Ability Good as Gold. Ability ids in the ROM: Adaptability 91, Tera Shell 308, Good as Gold 283. Tera Shell and Good as Gold are Gen 9 abilities: live-test both (fallbacks Purifying Salt / Magic Bounce). The ROM (0117) still has Beast Boost in every slot until this is built; change it at build time, after the tests, so Novareon is not left with abilities that do nothing.

OWNER CORRECTION (2026-10-29, final; supersedes the Adaptability / Tera Shell / Good as Gold line above): Novareon = Ability 0 Good as Gold, Ability 1 Tera Shell, Hidden Ability Adaptability. Ids: Good as Gold 283, Tera Shell 308, Adaptability 91. Test Good as Gold and Tera Shell live (Gen 9); Adaptability is a Gen 4 ability and should work, but check how it treats the Stellar type. The ROM (0117) still has Beast Boost in every slot until this is built after the tests.

## Owner decisions, 2026-10-29 (late)
- APPROVED: the nine new Eeveelutions' stats, abilities and level-up lists as drafted (Brawleon's is the Hitmonchan-based list).
- DEFERRED INDEFINITELY: the four TM replacements (Ice Punch, Signal Beam, Encore, Dive). Skip them; add those moves later.
- ORDER: first make the items and evolutions WORK; how each item is obtained (and who trades the Sandwich) comes after that.
- SKIPPED until the items/evolutions work: hidden abilities for the rest of the line (only Brawleon = Guts and Novareon = Adaptability are decided).
## Build order (stage-gated; each stage = one build, one live check, one checkpoint)
A. Data-only: the approved level-up lists (Eevee, Psyduck, Golduck, the eight existing Eeveelutions, Novareon), the Psyduck/Golduck stats (320 / 530), shared Psyduck+Golduck TM row (+ Shadow Ball, Rock Tomb, Reflect), the Eevee-line TM rows, for both normal and starter species ids.
B. Prove the evolution MECHANISM on existing species: use an item on Eevee (the stone/item shortcut table) and level up while holding an item (new method), e.g. Eevee -> Sylveon with Fairy Feather, Eevee -> Umbreon with Dusk Stone; make each planned item a valid evolution item in the bag.
C. New species (placeholder art until the art exists): the nine new Eeveelutions, normal and starter, their stats/abilities/learnsets/TM rows/evolution rows. Needs species-table room (see below).
D. Starter Golduck, normal Novareon, Stellar Sandwich, Megas (+120 script), then abilities/hidden abilities, then item sources in the map.
Risk for C: the expanded tables hold 1583 species and several code constants stop at 1582 (counts in ARM9 and overlays); more species need those raised or unused ids reused.

## Evolution methods, owner proposal 2026-11-01 (replaces the item column of the step 2 table for these species; 7 still undecided)
Jolteon: use Thunder Stone (83) | Flareon: use Fire Stone (82) | Vaporeon: use Water Stone (84) | Leafeon: use Leaf Stone (85) | Glaceon: use Ice Stone (849) | Espeon: use Sun Stone (80) | Umbreon: use Moon Stone (81; Psyduck also uses it) | Wraitheon: use Dusk Stone (108) | Sylveon: level up while holding Fairy Feather (2401) | Brawleon: level up while holding Black Belt (241) | Novareon: use Stellar Sandwich (new item, copy of Sandwich 1830).
UNDECIDED (owner, later): Venomeon, Duneon, Zephyreon, Chryseon, Strateon, Wyrmeon, Ferreon.
Engine notes (read from hg-engine's GetMonEvolutionInternal.c): the only built-in "level up holding an item" methods are day-only and night-only variants, so "level up holding X" is a new check; a species holds 9 evolution rows; use-item rows beyond the native table go in the project's shortcut table (it exists twice: ARM9 ITCM 0x940 and overlay 129 0x5A12, keep both in step); starter Eevee's rows must target the STARTER species (1565 + 2i), not the ordinary ones.

## Stage C built (ROM 0124, 2026-11-01)
Nine new Eeveelutions as ids 1536-1544 (ordinary) and 1545-1553 (starter) via tools/new_eeveelutions.py; Eevee rows rebuilt (stones, Sun, Moon, Dusk Stone->Wraitheon, starter +Stellar Sandwich; placeholder level row removed, not needed); hold table (18 rules) grown in place; three alias/form hooks chained for ids 1536-1553 (art alias = TEMPLATE species). Constraint for Stage D: 7 filler rows left (1554-1560) vs 10 wanted (9 starter Megas + normal Novareon); overlay 129 has ~16 bytes spare, new code needs another overlay or ARM9 space; Pokedex text for the new species is blank.

## Stage D2 (ROM 0127/0128, 2026-11-01)
Megas part 1: starter Brawleon, Zephyreon, Wraitheon, Venomeon, Duneon, Chryseon use filler rows 1554-1559 (row 1560 is the Novareon follower slot id). Strateon, Wyrmeon, Ferreon Megas wait for table growth (3 rows). Ordinary Novareon needs NO new row: species 500 (the Pokedex identity) is now a full copy of 1581 and ordinary Eevee evolves into it with the Stellar Sandwich; keep 500 in step with 1581 (abilities, stats).
Owner (2026-11-01): after all Eevee features are done, rename Novareon -> Stellareon (10 letters, the DS species-name limit) or Cosmeon. Touches: species names 237/238, Pokedex name bank 817, Novareonite item (3147) texts, dex text, release notes.
Owner (2026-11-01): with the species rename, Novareonite (item 3147) becomes Stellareonite (or Cosmonite if the species becomes Cosmeon).
DONE 2026-11-01 (ROM 0130): Novareon -> Stellareon, Novareonite -> Stellareonite (tools/rename_stellareon.py, text only). In this plan and the tool names "Novareon" still means Stellareon (ids 500 ordinary, 1581 starter, 1582 Mega).
