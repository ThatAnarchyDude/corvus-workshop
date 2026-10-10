# Pokémon Psyduck Yellow — Pewter gym checkpoint 015

This cumulative checkpoint builds on prototype 014 and opens Pewter from the north end of Route 2. It completes Brock's gym and adapts Pewter's outdoor conversations and walking guides to HeartGold's existing geometry. Optional museum, house, Mart and Pokémon Center event conversions remain in progress; this is not a completed Pewter City or Kanto release. Native healing, PC and shop services still use HeartGold's behavior. Route 3 is temporarily the next development boundary.

The gym uses Yellow's teams and explicit moves with HeartGold's battle mechanics:

| Trainer | Pokémon | Moves |
| --- | --- | --- |
| Junior trainer | Diglett 11 | Scratch |
| Junior trainer | Sandshrew 11 | Scratch, Sand Attack |
| Brock | Geodude 12 | Tackle, Defense Curl |
| Brock | Onix 14 | Tackle, Screech, Bide |

Onix does not have Bind at level 14 in Yellow. Winning awards the Boulder Badge and retires the optional early Route 22 rival encounter, as Yellow does. Brock then gives a disposable Bide TM34 and explains its use. Losing follows normal blackout behavior and awards neither badge nor TM. Once Brock is defeated, the junior trainer cannot initiate a new battle. A full bag leaves the TM collectible on a later conversation.

Bide uses an unused native item record and compatibility bit. It works through the ordinary TM pocket and teaching menu, displays “Bide / No.34,” and is consumed when taught. Yellow's first 151 species use Yellow's Bide compatibility; later species/forms that already support TMs can also learn it. HeartGold's original TM34 Shock Wave and every existing TM/HM remain available separately. The native 101-slot TM pocket and save format are unchanged.

Golduck is now Water/Psychic for player, rival and wild Pokémon, including existing Golduck in ordinary saves. Psyduck remains Water. No stats, moves, learnsets or evolution requirements were changed by this typing edit. Golduck's move changes are reserved until Kanto is complete. The agreed future Blue Eevee evolutions are recorded in `INTRO-UPDATE-PLAN.md`; later rival encounters using evolved starters have not yet been added.

Existing opening, parcel, National Pokédex, Pokégear, starter properties, shiny odds, Legendary IV rules, PC supplies and Forest changes carry forward. Johto's map headers and terrain are preserved. Original HG gym and outdoor script/event records remain archived in the ROM; active headers point to appended replacements. The specifically requested Viridian Cut trees remain.

## Download and saves

Use the new versioned browser page and select the original unmodified USA HeartGold ROM. It creates and verifies the complete playable NDS locally; the published page contains a patch, not a ROM. Prototype 014 is not the input. Earlier published downloads remain unchanged.

Back up ordinary saves before importing them. Do not transfer emulator save states between builds. Native checks include a normal in-game save and fresh boot after Brock's reward. They do not prove compatibility with every older save or emulator.

## Build and checks

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/pewter_progression.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-015 --version 015
python3 yellow-heartgold/tools/check_repo_safety.py
```

Exact output hashes, action traces, native outcomes and coverage limits are recorded in `releases/prototype-015/validation.json`. Native gym victory tests use level-20 Golduck to isolate script completion; they are not an opening-level balance test. A level-1 Psyduck fixture checks the loss branch. Fixtures use native GiveMon, ReturnLoanMon, warp and save commands, followed by the unmodified release ROM. No RAM or save bytes are edited.
