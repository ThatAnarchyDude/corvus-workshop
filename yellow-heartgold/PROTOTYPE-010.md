# Pokémon Psyduck Yellow — Viridian catching tutorial prototype 010

Viridian’s old man is present from the start at the northern path. Before the parcel is delivered and Oak grants the Pokédex, he complains that he has not had his coffee and blocks passage. Once both requirements are met, approaching the path triggers his apology and catching demonstration. He then walks south and east to stand beside the path. His finished state persists; subsequent approaches do not repeat the demonstration.

The demonstration uses HeartGold’s native tutorial battle, including its automatic weakening and Poké Ball throw. It gives the demonstrator the old man’s name and a dedicated FireRed old-man back sprite, extracted locally from the previously supplied ROM. These substitutions are active only during this event. Johto’s tutorial names, back sprites and setup remain unchanged. The demo uses its own party and bag; the player’s Pokémon and Poké Balls are not used or awarded a captured tutorial Pokémon. The old man uses HeartGold’s field sprite. The original Yellow demonstration’s failed capture is not reproduced; this uses the working HeartGold lesson to show the capture process.

Two visible Pokédexes wait on the back table beside Oak’s PC. During parcel delivery, Oak walks north to collect them, takes a step away from the table, and the devices disappear. He returns to the player before granting the National Pokédex. If the player stood directly north of Oak, the player moves one tile aside to clear his path. Existing completed saves keep their Pokédex and do not replay that scene. Oak’s one-time five-ball gift remains available by speaking to him again.

The remaining starter ball says: “This is Oak's last starter. You should leave it here.” It no longer selects Blue’s dialogue. The original rival message remains intact.

## Playtest

Use the patch-only browser downloader with the original unmodified USA HeartGold NDS. It creates the full playable prototype on your device. Back up normal saves; do not transfer emulator save states between ROM versions.

1. Start a new game, choose a starter and complete the rival battle. Interact with the remaining ball and check the corrected text. Check the two Pokédexes on the back table.
2. Retrieve the parcel from Viridian. Before delivery, approach the northern path: the old man should complain about coffee and stop you. The Center and Mart should remain usable.
3. Return the parcel to Oak. Watch his walk to the table, the devices disappearing as he walks away, his return and the National Pokédex grant. Check that the devices stay absent when you leave and return.
4. Return to Viridian and approach the old man. Advance his dialogue, watch the full catching demo, and watch him walk aside. The player’s party and ball count should remain unchanged by the demonstration. Approach again, save normally, reload and check that he remains beside the path without repeating the lesson.

Route 2 and Viridian Forest remain closed at the existing prototype boundary beyond the old man. After this build passes the owner’s Android playtest, the next task is Yellow’s zero-badge progression through Route 2 and Viridian Forest, including encounters, trainers, dialogue and gates. The approved new-game intro is unchanged.

## Build

Requires the corrected prototype 009, original USA HeartGold and the supplied FireRed Rev 1 image, kept local and ignored.

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/viridian_tutorial.py yellow-heartgold/build/firered-source.gba
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-010 --version 010
python3 yellow-heartgold/tools/check_repo_safety.py
```

The builder appends separate active scripts, events, text, Pokédex textures and old-man battle graphics. Original map archive members and existing graphics remain preserved. The field graphics lookup is relocated with all existing records intact and one new record for the Pokédex; its two overlay pointers are updated without changing overlay size or BSS. ARM hooks preserve the original tutorial naming and back-sprite paths whenever the demo mode is off. The extension stays inside the existing ITCM allocation and updates the autoload-end pointer. Exact hashes and completed checks are in `releases/prototype-010/validation.json`.

## Completed verification

All 106 automated checks passed without skips. The browser rejected an incorrect input and produced the exact verified prototype NDS from the original USA HeartGold image. Native DeSmuME playtests confirmed Oak’s continuous walk, device removal and National Pokédex grant; corrected leftover-ball dialogue; the coffee gate; the complete old-man battle and walk aside; unchanged player party and ball count; and normal save/reload persistence for the missing devices and cleared gate. These checks used positioned normal-save fixtures, followed by fresh boots of the final unmodified prototype. A complete fresh-game quest and Android playtest remain for owner verification. Native audio calls are retained; no audible listening check was performed for this build.
