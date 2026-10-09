# Pokémon Psyduck Yellow — prototype 004

This release tests Pallet Town and the first Route 1 grass pathway. It is not the completed Yellow campaign. Use a new game, and back up earlier saves.

The downloadable page contains an xdelta modification patch and a local decoder, not a game ROM. Select the untouched USA HeartGold ROM, press **Create my playable NDS**, then download the verified result. Your original stays on your device and is never uploaded. The result runs in a DS emulator; Android still needs user playtesting.

## Implemented opening

- Oak walks into view after his warning. A Psyduck approaches from the grass; Oak throws a ball, waits for its shakes, collects it, and visibly escorts the player through Pallet and the lab entrance.
- The freestanding right table is one tile north. Its physical balls are Psyduck on the left, Togepi in the center, and Eevee on the right. Each uses field preview, cry and confirmation instead of the native Johto starter application.
- Psyduck is male, Eevee female, and Togepi retains its usual gender distribution. Eevee's rival picks Psyduck; the other choices produce an Eevee rival. The saved rival name and Blue's naming/world/battle artwork are used in Kanto.
- Level-5 starter receipt initializes the native follower immediately. National Dex mode is enabled without marking all Pokémon caught. Both rival-battle outcomes continue and heal the party.
- Shiny odds are 1/16,384. A separate 1/16,384 bonus gives all six IVs 31; otherwise IVs remain normally random. Both bonuses can occur together. A third ability slot has a 1/3 chance: Swift Swim, Anticipation or Super Luck. Supported evolutionary ability mappings persist; Espeon uses Synchronize because Magic Bounce is absent from Gen IV.
- Oak warning, escort and rival challenge select HeartGold's Oak, escort and rival music arrangements. Door, capture, menu, selection, receipt and cry commands accompany their events.

## Player's PC

The bedroom PC offers only the player's PC, with native Mailbox and Ball Capsule services, a Photo Album when available, plus shared item storage. It does not offer Pokémon storage or other Center services. Item storage starts with one Potion and 95 Rare Candy, supports withdrawal/deposit/toss, and persists in normal saves. This prototype supports ten item stacks, up to 999 each.

Pokémon Center PCs retain their normal HeartGold services. Stock HG has a player's PC but no separate PC item-storage menu; adding access to this same storage is reserved for the Center maps when that part of the game is implemented. Use the same saved variables, not a second inventory: item/quantity pairs 0x4152..0x4165, initialized once via 0x4166.

## Validation on October 9, 2026

- 60 local tests passed, with no skipped tests in this environment. Compiled PC bytecode tests exercise conservation, exact-quantity withdrawal, cancellation, full Bag, stack capacity and toss confirmation. Native ARM tests force rare starter combinations and establish that the real HG RNG can produce both rare bonuses.
- DeSmuME booted a fresh new game and displayed Blue's naming icon, then completed Oak's field capture and visible escort into the correct lab with all three balls.
- Separate live tests selected all three starters. Encrypted Pokémon checksums were valid; species, level, forced gender, follower positions and National Dex ownership matched. A live Togepi had Super Luck.
- Togepi defeated the rival and continued healed; Eevee and Psyduck lost and also continued healed. The battle result variables and healed HP were checked in live RAM.
- Normal save/reload preserved Eevee, its follower, starter state and National Dex. Route 1's north boundary displayed the opening-test closure message. No Route 1 trainer battle was added.
- The bedroom menu opened the native Mailbox and returned to the player-PC menu. Live storage checks withdrew the Potion and all 95 stored Rare Candy; the deposit flow uses the native Bag selection UI. Deposited Rare Candy survived a normal save/reload, and inventory conservation was checked in live RAM.
- Chromium at phone width rejected an incorrect input and generated/downloaded an NDS matching the release SHA-256, with no browser errors. A repeat build produced the same output. No Android emulator run was performed here.

## Known limits

Oak's capture is an animated field scene, not a reconstructed capture battle screen. The title banner is renamed; full title-screen artwork is deferred. Music commands are installed, but these automated tests did not listen to audio. Pokémon Center item-storage integration, later routes, gyms, acquisition coverage, and Johto postgame progression remain unfinished. Johto's native starter application and Silver assets are preserved rather than repurposed. Existing Kanto assets are retained for later relocation.

Normal saves can preserve established state, but revised opening events are tested with a new game. Do not transfer emulator save states between different builds.

## Build

From the repository root, with the supported original and exact prototype-003 input available locally:

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/escort.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download
python3 yellow-heartgold/tools/check_repo_safety.py
```

Original SHA-256: `65f02a56842b75aa92d775d56d657a56fe3fa993550b04dc20704ab82d760105`.

Output SHA-256: `4018c164fe5ba818134d457f5ac0b923e2b5fdf44d5035be73714680d3f035df`.

ROMs and save files belong only in ignored local directories. Earlier ROM ZIPs were removed from reachable history on all six existing remote branches using explicitly leased, atomic updates. Hosting caches and outside clones are outside that rewrite.
