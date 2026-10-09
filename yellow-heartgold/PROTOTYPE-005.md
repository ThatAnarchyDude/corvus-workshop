# Pokémon Psyduck Yellow — title prototype 005

Prototype 005 adds the new title screen to the tested prototype-004 Pallet opening. The on-screen logo reads Pokémon Psyduck Yellow Version in gold lettering. An original low-polygon 3D Psyduck bobs and paddles through a moving blue water surface, surrounded by three ripple rings. The camera stays above the water and moves gently between front and side views. Pressing A, Start, or touching the screen retains HeartGold's start behavior; the title cry is now Psyduck's. The title theme and upper-screen backdrop retain HeartGold's original presentation.

This changes only the title archive, title overlay and banner. Pallet scripts, starter properties, PC storage, trainers, encounters and saves retain prototype 004's payloads. The separate opening movie remains HeartGold's original movie; this change targets the title that follows it.

## Playtesting

Open the published standalone playtest builder in a current browser. Select the **original, unmodified USA HeartGold .nds**, press **Create my playable NDS**, then download **Pokemon-Psyduck-Yellow-prototype-005.nds**. The source remains on your device and is never uploaded. The published page contains a patch, not a ROM.

Start a new game to test the opening, or import a backed-up prototype-004 **normal save** through your emulator. The save filename must match the new ROM filename if the emulator locates saves by name. A prototype-004 save was successfully loaded and checked in this build. Emulator save states are different from normal saves and should not be reused across builds.

## Verification — October 9, 2026

- 64 local tests passed with no skips. New tests check model node offsets, joint sample bounds, wake height, GPU vertex/polygon limits and water texture memory.
- The original and patched ROM hashes are checked; xdelta decoding reproduces the exact new output. A repeat build is also checked.
- DeSmuME booted the new title. Screenshots at multiple times show different camera, paddle and water positions, with the new logo and blinking native touch-to-start prompt.
- Touching the title proceeded into the native new-game introduction. A separate fresh emulator boot loaded a prototype-004 normal save into Oak's lab, with Eevee in the party, its active follower and National Dex ownership intact.
- Chromium at phone width rejected a bad input and downloaded a file matching the new build's SHA-256 without browser errors.
- The tracked-tree check found no known ROM/save extensions or ROM ZIP contents.

No Android emulator run or listening test was performed here. The title cry's native species argument was changed from 250 (Ho-Oh) to 54 (Psyduck). The campaign remains limited to Pallet and the bounded first Route 1 grass path; this title change does not advance its story.

## Rebuild

With the supported original ROM and the exact prototype-004 build available locally:

```sh
yellow-heartgold/.venv/bin/python -m pip install -r yellow-heartgold/requirements.txt
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/title.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-005 --version 005
python3 yellow-heartgold/tools/check_repo_safety.py
```

The generated inputs and outputs remain ignored under `yellow-heartgold/build/`. See `releases/prototype-005/validation.json` for exact hashes and inspection results. Do not add ROMs or save files to Git.
