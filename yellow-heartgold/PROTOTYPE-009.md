# Pokémon Psyduck Yellow — intro prototype 009

Oak now releases shiny Eevee instead of Marill in the new-game introduction. The graphics and shiny palette come from HeartGold’s native Eevee resources. The release plays Eevee’s cry and HeartGold’s shiny sound, SEQ_SE_DP_REAPOKE (1808). The original ball release and intro music remain intact. HeartGold’s native shiny particle texture is converted to a 40-frame 2D sparkle sequence for the intro; its battle particle runtime cannot run directly in this screen. Eevee is positioned beside Oak rather than covering his face.

The rival prompt and confirmation display the complete 64×64 early FireRed Blue battle portrait extracted from the supplied USA/Europe Rev 1 ROM. The naming keyboard displays a 32×32 version of that complete portrait to fit its original icon area without covering the input or controls. Original Ethan/Lyra graphics, player naming and the final player shrink animation remain intact. Rival confirmation hides the unrelated player portrait. Cancellation and renaming retain the native naming-overlay lifecycle.

Only overlay 53 and the intro/naming graphics archives change from prototype 008, plus the prototype banner. Starter probabilities, parties, PC supplies, parcel progression, HeartGold’s shop progression, Johto content and starter selection are unchanged. Route 2 and Viridian Forest remain closed.

## Playtest

Use the patch-only browser download page with the original unmodified USA HeartGold NDS. It creates the full playable NDS on your device without uploading or altering the original. FireRed is needed for development only, not to use the downloader.

Start a **new game** to see the intro. Check Eevee’s white/gray shiny appearance, release sparkles, Eevee cry and sparkle sound. Test both player genders, enter names, choose No at rival confirmation and rename him, then choose Yes and reach the bedroom. Check that the chosen player and rival names persist after a normal save.

Back up existing normal saves before importing them. This build does not change the save format, but cross-version Android save testing remains the owner’s check. Continuing an existing save does not replay the intro. Do not transfer emulator save states between builds.

## Build

Requires the exact prototype 008 output, original USA HeartGold and supplied FireRed Rev 1 image, all kept local. FireRed SHA-256: `729041b940afe031302d630fdbe57c0c145f3f7b6d9b8eca5e98678d0ca4d059`. Graphics are extracted directly; no standalone proprietary artwork is committed.

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/intro_polish.py yellow-heartgold/build/firered-source.gba
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-009 --version 009
python3 yellow-heartgold/tools/check_repo_safety.py
```

Build assertions preserve ARM9/ARM7 and unrelated filesystem payloads, retain the original ball graphics and emergence animation, validate the exact source revisions, and decode the xdelta patch back to the identical output. Automated ARM checks execute the cry/sound hook and rival prompt, cancellation, rename, confirmation and Oak restoration paths. Release evidence is recorded in `releases/prototype-009/validation.json`. Listening to audio and Android testing remain owner playtests; verified native API calls do not establish subjective sound quality.

## Verification

94 tests passed with no skips. Chromium rejected incorrect input and downloaded the exact final NDS. Fresh DeSmuME runs on the final ROM reached the Pallet bedroom with both genders; the male-player run also rejected the first rival-name confirmation and returned to naming. Frame captures show shiny Eevee and visible sparkle glints beside Oak. Original and generated ROMs, screenshots, states and saves remain local. External hosting availability is separate from local browser verification.
