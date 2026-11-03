# Evolutions and move pools: Eevee line and Psyduck line (read from ROM 0116, 2026-10-29)

## How evolution works in this ROM (two layers)
1. Native table (a/0/3/4): method, parameter, target. Methods seen: 7 = use an item, 2 = friendship (day), 3 = friendship (night), 31 = level up knowing a move of a type (9 = Fairy).
2. Stone shortcuts the project added (ARM9 table, `evolution_testing.py` / `psyduck_evolution.py`): these let a stone evolve a Pokemon that the native table would evolve another way.
Normal Eevee (133) and starter Eevee (1561) both use them (the owner evolved the starter Eevee into Umbreon with a Dusk Stone).

## Eevee (normal 133 / starter 1561) -> every route today
| Evolution | Native method | Extra stone shortcut |
|---|---|---|
| Vaporeon | Water Stone | - |
| Jolteon | Thunder Stone | - |
| Flareon | Fire Stone | - |
| Espeon | friendship, daytime | Dawn Stone |
| Umbreon | friendship, night | Dusk Stone |
| Leafeon | Leaf Stone | - |
| Glaceon | Ice Stone | Never-Melt Ice |
| Sylveon | level up knowing a Fairy-type move | - |
| Novareon (starter only) | Sandwich | - |
The starter line (species 1565-1582) mirrors this, each starter evolution being its own species.

## Psyduck line today
| Pokemon | Evolves | Notes |
|---|---|---|
| Psyduck (54) | Moon Stone -> Golduck (55) | the Water Stone and level routes were removed |
| Starter Psyduck (1563) | NOTHING | no evolution row |
| Golduck (55) | - | no Mega |
| Starter Golduck | DOES NOT EXIST | would be a new species |
| Mega Psyduck | starter Psyduck only (1564) | Psyduckite |

## Level-up moves
Psyduck: L1 Scratch, Tail Whip; L3 Water Gun; L6 Confusion; L9 Fury Swipes; L12 Water Pulse; L15 Disable; L18 Zen Headbutt; L21 Screech; L24 Aqua Tail; L27 Soak; L30 Psych Up; L34 Amnesia; L39 Wonder Room.
Golduck: L1 Scratch, Tail Whip, Water Gun, Confusion, Aqua Jet; L9 Fury Swipes; L12 Water Pulse; L15 Disable; L18 Zen Headbutt; L21 Screech; L24 Aqua Tail; L27 Soak; L30 Psych Up; L36 Amnesia; L40 Hydro Pump; L45 Wonder Room.
Psychic-type attacks they get: Confusion, Zen Headbutt (and TM Psychic, Calm Mind). Nothing like Psybeam, Psyshock, Future Sight, Extrasensory.
Eevee: L1 Tackle, Tail Whip, Growl, Helping Hand, Covet; L5 Sand Attack; L10 Quick Attack; L15 Baby-Doll Eyes; L20 Swift; L25 Bite; L30 Copycat; L35 Baton Pass; L40 Take Down; L45 Charm; L50 Double-Edge; L55 Last Resort.
Eeveelution level-up lists are in the ROM (learnset file a/0/3/3, 136 bytes per species); each has a type move at L0 plus a set of types moves from L20 to L50.
