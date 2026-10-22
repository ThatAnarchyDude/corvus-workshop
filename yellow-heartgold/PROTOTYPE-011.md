# Pokémon Psyduck Yellow — opening corrections prototype 011

The old man now lies face-up in the center lane between Viridian’s two vertical tree rows, rather than standing in the right-hand side lane. Seven invisible collision tiles close the two side lanes and the spaces beside him. They leave one center passage occupied by the old man. Before parcel delivery and the National Pokédex, his coffee dialogue stops the player. Afterward he stands up, gives the catching lesson, lets the player make room and walks south and east beside the path. Completed normal saves preserve completion; older Viridian saves migrate the two actor positions once.

Blue’s full FireRed portrait appears inside the same touch-screen rectangle used for the selected player during Oak’s introduction and name confirmation. Oak stays on the upper screen. Player portraits and the naming keyboard resources remain intact. Blue’s graphics are appended to a separate background character bank and two screen layouts, one for each player gender.

Shiny Eevee’s 80×80 sprite uses the original Marill cell origin and the native release movement. The sparkle animation and final rest pose now both retain Marill’s final position transform, preventing a jump when the sparkles finish. The Eevee cry and shiny sound remain in place.

Route 2 and Viridian Forest remain closed beyond the old man’s passage. Once these corrections pass Android playtesting, the next prototype implements Yellow’s zero-badge Route 2 and Viridian Forest encounters, trainers, dialogue and traversal. HeartGold shop progression and Johto are preserved.

## Playtest

Use the browser downloader with the original unmodified USA HeartGold image. It generates the playable NDS locally. Back up normal saves and avoid transferring emulator save states between ROM versions.

1. Start a new game. Watch Eevee’s release, sparkles and rest pose for any change in position.
2. Name the player and check Blue’s introduction and rival-name confirmation on the touch screen. Test rejecting the rival name and entering another one.
3. Before returning Oak’s Parcel, attempt all three northbound lanes in Viridian. The side lanes and spaces beside the lying old man should block movement. The center should trigger the coffee complaint.
4. Deliver the parcel and receive the National Pokédex. Return to the center lane. Watch him stand, teach catching and walk aside. Walk through the center, then save normally and reload to confirm completion persists.

## Build

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/opening_corrections.py yellow-heartgold/build/firered-source.gba
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-011 --version 011
python3 yellow-heartgold/tools/check_repo_safety.py
```

Requires the verified local prototype 010, original USA HeartGold and previously supplied FireRed Rev 1 ROM. The lying pose is extracted locally from FireRed; no standalone ROM graphics are published. Original land archive members, lab events and Johto models are preserved. Two cloned land members are referenced only by the affected overworld cells; all original movement permissions remain unchanged except the seven barriers. Validation evidence and unrun checks are recorded in `releases/prototype-011/validation.json`.

## Verification

All 116 automated checks passed with no skips. The mobile browser rejected an incorrect input and reconstructed the exact verified output from the original USA HeartGold image without browser errors. Continuous fresh-boot emulator runs checked both Blue panel layouts, name rejection and replacement, completion to the bedroom, and Eevee’s sparkles and rest pose. Normal-save fixtures checked all three coffee-gate approaches, the native catching lesson, walking aside and persistence after save reload.

The full parcel quest was not replayed from a new game in this build. Android playtesting and audible sound verification remain with the owner. Internal emulator snapshot resumes failed locally during overlay transitions; final native checks used continuous fresh boots and normal in-game saves.
