# Pokémon Psyduck Yellow: bedroom-PC intermediate playtest (2026-10-09)

**Scope:** Known-good Prototype 003 rebuilt from owner's original US HeartGold, plus a targeted map 506 (Red's bedroom) PC-item withdrawal script. This is NOT the promised complete Yellow-authentic opening. Do not treat it as final Prototype 004.

## Reconstructed baseline and development ROM

- Prototype 003 baseline SHA-256: `1cd5dd980e9c9a542783fe261e5b4b9c59df7b1061e1be2d97f6fa2dd9e635db`. Matched the previously released patch, byte for byte.
- Bedroom-PC derivative SHA-256: `1a8aa0c4cba2bda3351e843b963b8876019a13dc86573eb79446b408b1b16a9a`. 126,657,736 bytes.
- Modified ROM is kept outside GitHub and delivered privately in the chat for the owner's use with their source ROM.
- Builder: `yellow-heartgold/tools/bedroom_pc.py` and `bedroom_pc_script.py`.
- Script/text member data appended; original asset members preserved; map 506 points at new script/text members; event map is unchanged.
- PC script has one Potion, 95 Rare Candies, cancellation and bag-full retry, plus save flags to prevent duplication. Other PCs unchanged.

## Checks performed

- Focused bytecode interpreter: eight PC-withdrawal tests passed (yes/no, retry, inventory full, flags, repeat).
- Thirteen starter rules and five candidate walking-geometry tests also passed, **but neither system is integrated into this ROM**.
- Binary reconstructed correctly and passed NDS format parsing and patch roundtrip verification.
- DeSmuME libretro smoke test ran 4,530 simulated frames from a clean boot, reached the GAME FREAK opening and then the HeartGold animated title screen. Confirmed title screen screenshot.
- Emulator advanced to the New Game information screens using controller buttons and captured screenshots. It has **not** reached bedroom PC and validated withdrawal live.
- **Owner device testing pending** in melonDS PC and Android. Please test fresh game, PC, gift withdrawal, save/reload, and reporting.

## Not implemented

- Full Oak escort and Psyduck catching animation.
- Three physical right-side Poké Balls (male Psyduck, Togepi, female Eevee).
- New starter gender, shiny, IV or Hidden Ability creation.
- Blue battle portraits, final soundtrack transitions, Johto-gated native starter selection.
- Title-screen graphics. Current title still says HeartGold.

## Next engineering actions

1. Verify bedroom PC interaction with gameplay state and melonDS on actual device.
2. Integrate original-Yellow-style Oak choreography and Psyduck capture, preserving NPC movements and door transitions.
3. Build physical 3-ball selection and targeted starter creation mechanics.
4. Update Kanto Blue portraits separately from Silver and preserve Johto.
5. Re-test against reference Prototype 003 across PC and Android before claiming complete replacement.

No proprietary playable ROM should be committed to public or private GitHub branches without appropriate rights.

## Owner playtest result: 2026-10-09

The supervisor reported **all tests passed** for the released bedroom-PC intermediate ROM, after testing the Potion/Rare Candy interaction and returning to direct development. This is owner-reported playtest evidence, not a newly executed independent emulator automation. Retain this exact build as the regression baseline. No claim is made that the later Oak movement and Psyduck starter overhaul are implemented in the tested ROM.
