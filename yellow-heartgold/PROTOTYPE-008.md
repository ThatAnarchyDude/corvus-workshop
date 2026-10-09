# Pokémon Psyduck Yellow — Viridian fixes prototype 008

The Pokémon Center is available before Oak’s parcel is delivered. Prototype 007 accidentally placed an automatic “POKEMON CENTER” sign on the tile in front of its entrance. HeartGold checks those signs before processing doorway transitions, which could repeatedly stop a player approaching from the south. Prototype 008 removes that label event. The Mart’s label moves from its entrance approach to the existing sign beside the building. Door warps and native Center services are unchanged.

The escort cashier remains during the parcel conversation and while an unsuccessful full-bag gift is pending. After you collect the parcel, leave the Mart and return, only the two original counter clerks remain. The upper clerk buys and sells items after parcel delivery, including Poké Balls. His post-delivery interaction enables HeartGold’s native ball-sale flag (0x9A), normally set by the catching tutorial our opening replaces. The lower clerk has dialogue only and is reserved for a later role. Normal saves made inside the Mart keep their saved actors until you leave, so reloading does not interrupt the active conversation. Original script/event archive members remain preserved, and Johto remains unchanged.

## Playtest

Use the browser downloader with your original unmodified USA HeartGold ROM to create the full prototype 008 NDS locally. No full ROM or emulator save is published. Back up your normal save before importing it; do not transfer emulator save states between versions.

1. After receiving Oak’s Parcel, leave the Mart and approach the Center directly from the south. Walking north should enter it without the repeated label message. Test healing and both PC storage services.
2. Return to the Mart. There should be two counter cashiers and no extra escort actor. Leave and return again to check that the actor remains absent.
3. With an earlier save or a new game, check that the outside greeting, walking escort and parcel gift still complete. The Center should be accessible while the parcel is held, before delivery.
4. Save normally in Viridian, reload and repeat the entrance and cashier checks. Parcel progress, Running Shoes, Pokédex progress and evolution supplies should persist.

## Build

Requires the exact prototype 007 output and the supported original USA HeartGold ROM, both kept local and ignored.

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/mart_cleanup.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-008 --version 008
python3 yellow-heartgold/tools/check_repo_safety.py
```

Only appended Mart scripts/text and Viridian event assets are selected by updated map headers. The Center header, item data, starters, title and other maps remain unchanged. Exact hashes and verification scope are recorded in `releases/prototype-008/validation.json`.

Oak’s five Poké Balls are already available by speaking to him again after receiving the National Pokédex, as in prototype 007. This one-time gift is unchanged.

## Verification

88 tests passed with no skips. The browser downloader rejected an incorrect input and produced the exact verified NDS. Native DeSmuME checks on the final ROM confirmed direct entry from south of the Center, two counter cashiers, the upper clerk’s shop, the lower clerk’s dialogue and an actual Poké Ball purchase (bag quantity five to six). These checks start from a normal save positioned in Viridian using an ignored native-warp fixture; they are not a new-game quest playthrough. Android testing and save/reload after the new purchase remain unrun.
