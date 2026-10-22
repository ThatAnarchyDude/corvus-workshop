# Pokémon Psyduck Yellow — Route 2 and Viridian Forest prototype 014

This cumulative checkpoint builds on prototype 013 and opens Route 2 and Viridian Forest after the old man's catching lesson. It retains the opening, parcel quest, National Pokédex, Pokégear reward, early Route 22 rival battle, starter properties and global shiny/Legendary rules from earlier builds. Pewter is the next development area; its entrance remains temporarily closed while its story and gym are prepared.

HeartGold's map graphics, collision data and warps are unchanged. Route 2's postgame trainers are removed. Grass encounters on both halves of Route 2 and in the Forest use Yellow's species, levels and exact weighted probabilities throughout morning, day and night. In Yellow, the Forest includes Caterpie, Metapod, Pidgey and a rare level-9 Pidgeotto; this is intentionally different from Red/Blue's tables. These changes cover grass encounters, not every optional HeartGold encounter feature such as Headbutt.

The five Forest trainers use these Yellow teams with HeartGold's battle mechanics:

| Trainer | Team |
| --- | --- |
| Bug Catcher | Caterpie 7, Caterpie 7 |
| Bug Catcher | Metapod 6, Caterpie 6, Metapod 6 |
| Lass | Nidoran♀ 6, Nidoran♂ 6 |
| Bug Catcher | Caterpie 8, Metapod 8 |
| Bug Catcher | Caterpie 10 |

Their battle, defeated and subsequent conversation text follows Yellow. Native trainer sight, approach, rewards and defeat flags are retained. Forest item balls contain two Potions and one Poké Ball, with hidden Potion and Antidote pickups using the native hidden-item system. Route 2 contains a Moon Stone and HP Up. Both Forest gatehouses now have Yellow's two informational NPCs. Yellow's tips can be read at the existing background-event positions; no new sign models or map redesign are included.

Per the owner's revised terrain instructions, 116 inherited Cut trees, Rock Smash rocks and Strength boulders are removed from 30 Kanto maps. The two specifically requested Cut trees beside Viridian's old man remain. Johto terrain is unchanged. Original event, script, trainer, party and encounter archive members remain preserved; active Kanto headers point to appended replacements. Yellow's required story gates are still in scope.

## Download and saves

The versioned browser download page contains a patch, not a ROM. Select the original unmodified USA HeartGold ROM; the page reconstructs and verifies the complete prototype locally. Do not select prototype 013 as its input: prototype 014 includes its changes already. Existing published versions remain separately available.

Back up ordinary emulator saves. Saves from earlier prototypes can be imported; emulator save states should not be transferred across builds. New area item and trainer flags are separate from the archived postgame records. Native checks use saves created through the game's normal saving operation, then boot the actual release ROM.

## Build and checks

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/forest_progression.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-014 --version 014
python3 yellow-heartgold/tools/check_repo_safety.py
```

See `releases/prototype-014/validation.json` for exact hashes, native checks and coverage limits. Testing does not establish that every forest path, trainer outcome or emulator is free of issues. The owner can test each checkpoint at their own pace while development continues through Giovanni's eighth badge.
