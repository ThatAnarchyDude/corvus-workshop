# Pokémon Psyduck Yellow — Yellow shop rules prototype 009

Yellow uses fixed inventories per town instead of HeartGold’s badge-based stock. Viridian sells regular Poké Balls, Potions, Antidotes, Parlyz Heals and Burn Heals. Great Balls appear in Lavender and Celadon shops; Ultra Balls appear in Fuchsia, Cinnabar and Indigo Plateau shops. Those inventories do not check badge counts. Reaching each town still follows the story and route requirements.

Prototype 009 makes Viridian’s upper cashier use its fixed Yellow inventory, including after additional badges. The lower cashier remains reserved, and the escort still disappears after collecting the parcel and leaving. Shop access still opens after parcel delivery. Oak’s five-ball gift remains available by talking to him again after the Pokédex scene.

Future Kanto towns will use the recorded Yellow ball inventories as they are adapted; they remain closed in this prototype. See `data/yellow-ball-sales.json` for the source revision and mapping. Johto’s shops and original Kanto archives retain their native behavior.

## Download and saves

Use the browser downloader with the original unmodified USA HeartGold NDS. It creates the full playable NDS locally. Back up your normal save before importing it; do not transfer emulator save states between builds. This change adds no saved variables or item slots.

## Build and verification

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/yellow_marts.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-009 --version 009
python3 yellow-heartgold/tools/check_repo_safety.py
```

The incremental builder requires the exact prototype-008 output and pristine USA base ROM locally. Only a new Mart script-bank copy and its map pointer change; an ITCM wrapper routes a unique stock parameter to a fixed item list. Other parameters restore the script cursor and tail-call the original native handler with its original context and stack. Existing native inventories, shop prices, shared scripts, title and other maps remain intact.

90 tests passed without skips, including native Thumb dispatch and fallback register/stack/script-cursor checks. The browser rejected an incorrect input and created the exact verified output. DeSmuME on the final ROM showed all five Yellow Viridian items and no Great/Ultra Balls. It used the normal Viridian fixture from prototype 008 and a fresh boot. Android testing, a new-game playthrough and save/reload of this build remain unrun. No new town is opened in this release.
