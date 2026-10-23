# Pokémon Psyduck Yellow

Pokémon Yellow's Kanto campaign rebuilt inside HeartGold's engine. **Latest: prototype 0050 BETA** — a pre-release for testing only; not a complete game. Kanto up to the first Hall of Fame only; **Johto is not ready — do not go there.**

## Play it
1. Open the **[0050 patching page](https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/prototype-0050/index.html)** (or pick a release from the **[Releases page](https://github.com/ThatAnarchyDude/Psyduck-Yellow-Releases/releases)**).
2. Choose your **own, original, unmodified USA HeartGold `.nds`**.
3. Click *Create my playable NDS*, wait for the checks, then download **Psyduck Yellow Prototype 0050.nds** and load it in your DS emulator.
4. Start a **New Game**. Saves from older prototypes are not supported.

Nothing is uploaded: the patching runs in your browser and every stage is hash-checked. No ROMs or saves are distributed.

## What is in this folder
- **[source/](./source/)** — the source: Python build tools, tests, data, assembly and notes (its README says what is and is not included).
- **[DEVELOPMENT-LOG.md](./DEVELOPMENT-LOG.md)** — the plain-language, dated log of every published change.
- **`index.html` and `prototype-00xx/`** — hosted patching pages for earlier prototypes (the page here at the top level is prototype 0041). The current page lives in the [Releases repository](https://github.com/ThatAnarchyDude/Psyduck-Yellow-Releases) so it can be updated without touching the source.
- **`playtests/`** — recorded emulator test clips and pages from earlier prototypes.
- **`tools/pkhex-plugin/`** — an experimental PKHeX plugin build for editing saves.

The patch decoder is RomPatcher.js by Marc Robledo (MIT licence); see `LICENSE.txt`. Credits: [hg-engine](https://github.com/BluRosie/hg-engine) by BluRosie and contributors; Pokémon Yellow data and dialogue are referenced from the [pret/pokeyellow](https://github.com/pret/pokeyellow) disassembly. Unofficial fan project, not affiliated with Nintendo, Game Freak, Creatures or The Pokémon Company.
