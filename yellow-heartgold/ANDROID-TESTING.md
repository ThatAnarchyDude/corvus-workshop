# Android testing — prototype 001

This is an experimental HeartGold-based feature prototype, not the completed Yellow remake. Start a NEW game. The opening remains New Bark Town and Professor Elm’s lab.

## Files

- `build/yellow-heartgold-prototype-001.nds`: generated game file to open in a DS emulator.
- `build/yellow-heartgold-prototype-001.xdelta`: approximately 675 KiB patch for the original US HeartGold ROM.
- `build/prototype-report.json`: hashes and static verification status.

## Android

1. If using the `.nds` file, put it in a folder accessible to your emulator and open it in a DS emulator such as melonDS for Android. No patching step is needed for this file.
2. If using the smaller patch, use an Android patcher that supports xdelta (such as UniPatcher). Select the patch and your ORIGINAL `Pokemon - HeartGold Version (USA).nds`, then create a new output `.nds` file. Do not patch an already modified game. Load the output in your emulator.
3. Begin a new game with a separate save file. The game still displays HeartGold’s original title. Choose a starter in Elm’s lab; the three choices should be Pikachu, Eevee and Togepi.

Required original SHA-256: `65f02a56842b75aa92d775d56d657a56fe3fa993550b04dc20704ab82d760105`.
Output SHA-256: see the accompanying `prototype-report.json`.

## Implemented changes

- Level-5 starter creation, selection-screen species/cry table and selection text changed together.
- Chosen Pokémon enters party slot 1; the original lab scene initializes following immediately.
- Main follower initialization and refresh now explicitly select party slot 1, including a fainted lead, instead of searching for the first conscious Pokémon. Original empty-party guards and map restrictions remain. Egg behavior and scripted exceptions need further testing.
- Pokédex and National mode are granted immediately after choosing a starter. Seen/caught entries remain normal; the patch does not fill the Pokédex.
- Togepi learns Tackle at level 1 so its level-5 starter can attack. This also changes the learnset for other Togepi in this prototype.
- First-rival branch checks and level-5 parties adapted to the three starters. Later rival battles are not yet adapted.

## Phone test checklist

Test all three choices from fresh saves: correct name, sprite and cry; confirmation/cancellation; party species and level; usable moves; immediate following; leaving the lab; Pokédex/National mode; first rival battle; in-game save and reload. After catching another Pokémon, reorder the party and verify the follower changes. Test a fainted lead as well. Report emulator/version, starter, action, screenshot and whether it reproduces after loading a normal save.

## Scope and verification limits

Yellow’s Kanto opening/story, gym teams, 493-species acquisition plan, Johto postgame and order-based gym scaling are NOT in this build. This prototype retains most original HeartGold story/content. Do not use it as a complete campaign release.

Static tests verify the starter tables/text, follower branch instructions, Dex script call/return layout, Togepi’s opening move, first rival teams/branches and patch-site rejection. Reload verification confirms only the expected ROM components changed. Applying the xdelta patch was tested and produced the exact built ROM hash. Emulator checks passed for boot, new game, room transitions, all three starter previews/receipts with immediate followers, National Dex runtime flags and UI, and normal save/restart/Continue reload. Party reordering, fainted leads and first rival combat remain untested in gameplay; consult `build/validation.json` for the completed gameplay checks and remaining untested behavior. Android compatibility has not been independently tested on a physical phone.
