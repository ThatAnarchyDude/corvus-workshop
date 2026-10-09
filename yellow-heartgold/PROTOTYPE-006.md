# Pokémon Psyduck Yellow — evolution prototype 006

Prototype 006 adds **95 of each evolution item** to the player's shared PC storage, alongside the existing Potion and Rare Candy supplies. Open the bedroom PC to receive the upgrade. Existing quantities and deposited items are preserved. If storage is full or a matching stack would exceed 999, make room and reopen the PC; the upgrade resumes without duplicating items already granted. Withdraw and toss use HeartGold's native scrolling lists, allowing access to all ten storage slots. Pocket selection for deposits also uses a scrolling list.

| Item | Evolution |
| --- | --- |
| Thunder Stone | Eevee → Jolteon |
| Water Stone | Eevee → Vaporeon; Psyduck → Golduck |
| Fire Stone | Eevee → Flareon |
| Dawn Stone | Eevee → Espeon; Togepi → Togetic |
| Dusk Stone | Eevee → Umbreon |
| NeverMeltIce | Eevee → Glaceon |
| Leaf Stone | Eevee → Leafeon |

These include the requested custom evolution methods. HeartGold already contains Dawn and Dusk Stones. It has no Ice Stone, so NeverMeltIce gains a **Use** action while retaining its original Ice-type held-item boost, name, graphics, pocket and price. The original evolution tables remain unchanged: level, friendship, time and location methods still pass through the native engine. Unrelated Pokémon and items retain their original evolution behavior.

## Download and saves

Open the published browser builder, select the **original unmodified USA HeartGold .nds**, choose **Create my playable NDS**, then download **Pokemon-Psyduck-Yellow-prototype-006.nds**. The source stays on your device; the page distributes only a patch.

Back up your normal save before importing it or renaming it to match the new ROM, as required by your emulator. Prototype 004 and 005 normal saves use the same save layout. Do not transfer emulator save states between releases. Reopen the PC after importing a save to receive the evolution supplies. Already withdrawn Potion or Rare Candy supplies are not restored.

## Verification — October 9, 2026

- 71 local tests passed, with no skips. They execute the compiled Thumb hook for all six additional species/item rules, both native item contexts and nullable evolution-method pointers; they also check preserved arguments, registers and stack on the native fallback.
- Compiled PC-script tests cover new-game supplies, one-time grants, old-save inventory preservation, resumed grants after making space, stack limits, all seven withdrawals, full bags, cancellation, deposits and tossing.
- DeSmuME loaded existing normal saves. The PC upgrade preserved previously stored quantities, displayed all evolution items in a scrolling list and withdrew all seven item types into the normal bag.
- All seven Eevee item evolutions completed in DeSmuME. Live RAM checks confirmed the evolved species as the active follower, ownership in the National Dex and consumption of the selected item.
- Psyduck → Golduck and Togepi → Togetic also completed in DeSmuME, using native starter party records copied into isolated test states. These were controlled evolution fixtures, not new story playthroughs. Their evolved followers and Dex entries were checked.
- A normal prototype-006 save/reload was checked after evolution, including PC upgrade state and stored quantities.
- NeverMeltIce's correct archive member was verified through HeartGold's native item-ID mapping. Only its field-use, party-use and evolution flags changed; its held-effect bytes remained identical.
- The title archive, title overlay, original evolution tables, other map scripts and events remain intact. New bedroom script/text members are appended; earlier versions remain preserved.
- xdelta decoding reproduced the exact new ROM. The phone-width Chromium downloader rejected an incorrect input and downloaded the exact verified output without browser errors.

No Android emulator run or listening test was performed here. This remains the Pallet opening and bounded Route 1 prototype; the campaign and Pokémon Center integration have not advanced.

## Rebuild

With the supported original ROM and exact prototype-005 build available locally:

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/evolution_testing.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-006 --version 006
python3 yellow-heartgold/tools/check_repo_safety.py
```

See `releases/prototype-006/validation.json` for exact hashes and inspection results. Generated ROMs, saves, emulator fixtures and patches stay ignored under `build/`. Never add ROMs or saves to Git or public hosting.
