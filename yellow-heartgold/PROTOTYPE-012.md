# Pokémon Psyduck Yellow — adventure preparation prototype 012

Viridian’s two outer north paths now have native HeartGold Cut trees at the spots identified in the owner’s recording. They stay through the old man’s catching tutorial and disappear only when Cut is used, following HeartGold’s normal tree reset behavior on map re-entry.

The old man’s granddaughter replaces one invisible barrier beside him. Before the lesson she stands still and explains that he needs his coffee. After the lesson she walks south out of the way and starts wandering nearby. The remaining temporary invisible obstacles are removed immediately. Their former tiles remain passable after a normal save reload. The side trees remain in place.

The cashier ends the parcel request with: “Come back here once it's delivered and I'll give you something that will help you A LOT on your travels.” After parcel delivery, the next interaction with the upper Mart cashier thanks the player, grants the native Pokégear and its Town Map card, then opens the normal HeartGold shop. The reward is given once; existing contacts, settings and cards are preserved. Kanto is unlocked on the map, which opens around the player’s current Kanto location. The lower cashier remains reserved for later use.

A police officer guards the western Viridian exit until Oak’s Parcel has been delivered. He gives the owner’s warning about terrifyingly strong Pokémon. The west-exit trigger prevents bypassing him before delivery and allows passage afterward. He is gone on the first Viridian entry after delivery. A saved older Viridian game receives the new actors once without resetting the old man’s tutorial completion.

Blue’s approved touch-screen portrait, the shiny Eevee intro, Oak’s lab and parcel events, Pokémon Center services, HeartGold shop progression and Johto remain intact. Route 2 and Viridian Forest are still the next build.

## Playtest

Back up normal saves. Use the download page with your original unmodified USA HeartGold file to create the playable NDS locally. Avoid transferring emulator save states between versions.

1. Before parcel delivery, inspect both Cut trees, talk to the granddaughter and try the center and west exits. You should remain blocked.
2. Check the cashier’s new promise when receiving Oak’s Parcel.
3. Deliver the parcel and receive the National Pokédex. Return to Viridian: the western guard should be gone.
4. Watch the catching lesson. The granddaughter should walk aside, then wander. Check every former invisible barrier position and confirm both Cut trees remain.
5. Talk to the upper Mart cashier. Receive the Pokégear, then check the normal shop and the Town Map’s Kanto position. Later interactions should not repeat the reward.
6. Save normally and reload. Tutorial completion, open center passage, the granddaughter’s wandering and the Pokégear reward should persist.

## Build and verification

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/adventure_ready.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-012 --version 012
python3 yellow-heartgold/tools/check_repo_safety.py
```

Builds from verified prototype 011 and the original USA HeartGold ROM. The builder clones the two affected land chunks and clears only the seven added collision bits. Native sprites and standard Cut events are reused; a fully transparent local model provides removable obstacle collisions. Original archive members are preserved. No ROMs, saves or standalone extracted proprietary art are committed.

All 128 automated checks passed with no skips. Native emulator checks used continuous fresh boots and normal-save fixtures at Viridian or the Mart. They checked the native Cut message, cutting the right tree and walking through its former tile, the lesson and granddaughter movements, removal of the temporary barriers, the western guard dialogue, the Pokégear gift and normal shop, and a Town Map displaying Kanto centered on Viridian. A normal save reload retained the open passage, both trees, wandering granddaughter and Pokégear reward. The returning cashier opened the normal shop without repeating the gift. Live actor checks confirmed the western guard was present before delivery and absent after delivery. The browser rebuilt the exact verified output and rejected incorrect input without errors.

The native Cut test used an isolated save fixture with Cut and the required HeartGold badge; those test grants are absent from the released game. The full new-game parcel quest, audible sound verification and Android playtesting were not repeated locally in this build. Detailed hashes and evidence are in `releases/prototype-012/validation.json`.
