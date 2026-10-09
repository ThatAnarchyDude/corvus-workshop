# Yellow adventure in HeartGold — implementation plan

Status: prototype 001 is the Android-tested reference build. Prototype 002 adds a separate Pallet opening validated in the emulator; see `releases/prototype-002/validation.json` for evidence and remaining checks. See [ANDROID-TESTING.md](ANDROID-TESTING.md) for scope, files and Android instructions, and [BUILDING.md](BUILDING.md) for the build foundation. Full Yellow campaign and Johto postgame remain to be implemented.

## Agreed scope

Recreate Pokémon Yellow's Kanto story and progression in the US HeartGold engine and graphical style. Use all 493 Generation I–IV species. Starter choices are Pikachu (25), Eevee (133), and Togepi (175). The National Pokédex is available when the player receives their first Pokédex, without a regional-Dex completion gate; entries still require seeing/catching Pokémon normally. Keep the current grant immediately after starter selection during the next development work. Moving that grant to Oak’s parcel-return event, matching Yellow’s original Pokédex timing, is a deferred change.

Johto is the full postgame region, mirroring Kanto’s role in HeartGold: unlock travel after the Kanto campaign and first Pokémon League victory. Include its towns, routes, dungeons, eight gyms, regional story events, and services, adapted for postgame progression and difficulty. Implement travel between both regions and verify that returning to Kanto preserves completed story state. Rework HeartGold’s original Johto-first flags, introductions, badge checks, and travel unlocks for this reversed order.

Keep HeartGold's Generation IV battle rules: physical/special split, abilities, held items, natures, breeding, evolution rules, moves, and types. There is no Fairy type in this scope. Togepi and its evolutions retain their Generation IV typing. No hg-engine expansion is needed.

## Confirmed following-Pokémon behavior

Immediately after the starter selection is confirmed and the chosen Pokémon is added to party slot 1, initialize and display that Pokémon following behind the player. Do not wait for a later story event, first rival battle, Pokédex receipt, or Johto unlock. This applies equally to Pikachu, Eevee, and Togepi.

The follower is the Pokémon currently occupying party slot 1, not a permanently assigned starter. Refresh the follower after party reordering, party additions/removals, evolution, map transitions and save/reload. Preserve the engine’s safe handling of temporary scripted scenes and maps where following is unsupported, then restore the current slot-1 follower when normal exploration resumes. Explicitly verify the Oak lab starter scene supports immediate following; enable its map support if needed. Audit normal exploration maps for unintended follower restrictions.

Acceptance checks: each starter appears behind the player before leaving the selection scene; movement and transitions work without duplicate sprites or blocked exits; swapping another species into slot 1 changes the follower; evolution and save/reload preserve the correct follower; a new game has no follower before starter selection. Validate edge cases such as an empty party or an egg in slot 1 before deciding whether they require a documented exception or custom engine behavior.

## Inspected inputs

| Input | Size | SHA-1 | Identification |
| --- | ---: | --- | --- |
| Yellow | 1,048,576 bytes | cc7d03262ebfaf2f06772c1a480c7d9d5f4a38e1 | POKEMON YELLOW, CGB-compatible cartridge |
| HeartGold | 134,217,728 bytes | 4fcded0e2713dc03929845de631d0932ea2b5a37 | POKEMON HG, IPKE, revision 0 |

Both hashes match the corresponding pret reference builds. This identifies the inputs; it does not establish that a modified game works. HeartGold contains 513 FAT entries, 384 named files and 308 detected NARC archives. The remaining FAT entries are not named in the FNT; they must be preserved too. The machine-readable inventory is in `rom-inventory.json`.

Run the read-only inspector from the repository root:

```sh
python3 yellow-heartgold/tools/inspect_roms.py \
  'Pokemon - Yellow Version (UE) [C][!].gbc' \
  'Pokemon - HeartGold Version (USA).nds'
```

## Implementation route and tools

Use an asset/script ROM hack of the supplied HeartGold, with reproducible scripted edits and a patch output. Yellow is the story/layout reference, not executable code to transplant: Game Boy and DS code and data formats differ.

- [DSPRE](https://github.com/AdAstra-LD/DS-Pokemon-Rom-Editor): inspect/edit maps, matrices, headers, events, scripts, text, encounters, trainers, personal data and evolutions. Its documentation explicitly includes HGSS support. GUI execution in this Linux environment remains unverified; assess its Windows runtime requirements before relying on it.
- Python `ndspy`: candidate for reading/writing DS ROMs and NARCs. Install a pinned version in a project-local virtual environment, then prove read/write preservation before any game edits. ndspy 4.2.0 is now installed and used by the payload-verified baseline builder; gameplay validation remains outstanding.
- [pret/pokeheartgold](https://github.com/pret/pokeheartgold): reference for script commands, flags, map tables, species IDs and engine functions. Its documented matching build requires proprietary Metrowerks/Nitro SDK tools; do not choose a full source rebuild as the default route or assume those tools are available.
- [pret/pokeyellow](https://github.com/pret/pokeyellow): reference for Yellow's maps, dialogue, story events, rival teams and encounters.
- `xdelta3`: candidate patch generation/application tool. Require input-hash checks and compare the patched output hash against the build output. Installed locally under `.tools/`; patch application is round-trip verified.
- melonDS or DeSmuME: required for gameplay acceptance and save/load tests. A DeSmuME libretro core is compiled locally under `.tools/`; `tools/emulator_smoke.py` exercises boot, starter selection, followers, Dex and save/reload using built-in firmware.
- [hg-engine](https://github.com/BluRosie/hg-engine): evaluated but unnecessary for the agreed 493-species scope. Its later-generation expansion and battle changes would add substantial risk and alter mechanics.

Prototype 001 has passed the recorded emulator checks and the user reports successful testing in an Android DS emulator. This validates the prototype’s tested features, not the unfinished Yellow campaign.

## Content and feature policy

Create a new title screen for the remake in a later milestone. The current test builds retain HeartGold’s title screen; the final title, artwork and presentation remain to be chosen. This does not block the Pallet opening work.

Use HeartGold's existing Kanto visuals and following-Pokémon assets. Its Kanto represents a later period and postgame difficulty, so maps and events must be rebuilt where Yellow differs; simply moving the spawn to Pallet Town is insufficient. Reuse assets where possible and create missing map layouts with the same visual style.

Preserve Yellow's eight-gym progression, Oak's opening, rival encounters, Team Rocket story, Jessie/James appearances, Silph Co., Pokémon Tower, Safari Zone, Seafoam Islands, Victory Road and League. Restore missing or changed locations, including the original Cinnabar Gym, as required. Use Yellow's Pikachu story beats adapted to whichever starter was chosen. Rival starter/team behavior and Oak's presentation must cover all three branches.

Preserve HeartGold's following Pokémon, touch UI, day/night cycle, time-based encounters, held-item systems, berries, breeding/daycare, happiness, evolution support, Pokégear functions, Apricorn crafting, move services, and other in-game features. Each relocated service needs a reachable NPC/location and a progression unlock. Johto is confirmed postgame content, unlocked after the first League victory. Retain Battle Frontier and Pokéathlon with revised access gates; their exact unlock points remain planning defaults. Pokéwalker and Nintendo online connectivity require separate compatibility testing and cannot be promised by a local ROM patch.

National Dex availability alone does not make all species obtainable. Maintain an explicit 493-species acquisition table covering wild encounters, gifts, fossils, breeding, evolution and legendary/mythical events. Default to making all 493 obtainable within one save without obsolete online distributions or a second game. Adapt trade evolutions and version-exclusive access through documented in-game alternatives, preserving the species and battle mechanics. Balance early routes rather than placing every species there.

## Confirmed gym balance requirements

Kanto leaders must use their original Pokémon Yellow roster, party sizes, and individual Pokémon levels. Preserve each leader’s original specialty: Brock/Rock, Misty/Water, Lt. Surge/Electric, Erika/Grass, Koga/Poison, Sabrina/Psychic, Blaine/Fire, and Giovanni/Ground. Restore Koga and Giovanni as the campaign leaders rather than retaining HeartGold’s later Kanto replacements. Verify the exact Yellow trainer data against the reference before implementing teams.

Match Yellow’s intended difficulty as well as its levels. HeartGold’s Generation IV abilities, physical/special split, moves, AI, items, and the three new starter options can change difficulty even with identical rosters. Evaluate these factors explicitly and tune leader movesets, held items and AI toward Yellow’s challenge without changing the required roster, levels or specialty. Do not promise mathematically identical difficulty across engines or starter choices; validate through representative playthroughs.

Johto leaders retain their original type specialties, but their teams scale by challenge order instead of using HeartGold’s fixed Kanto reference battles. Any of the eight Johto leaders can be challenged first or last. Count distinct Johto badges already earned, not battles attempted, so defeats and retries do not advance the tier; Kanto badges do not affect it.

The starting level B is the highest individual Pokémon level among the finalized Kanto League opponent teams, including every Champion rival variant. This interprets “highest level League challenger” as the strongest League opponent rather than the player’s party. Verify B from the implemented trainer data. For challenge position n from 1 through 8, the team level is B + floor((100 - B) × (n - 1) / 7). All party members use that tier’s level. If B is 65, the eight tiers are 65, 70, 75, 80, 85, 90, 95 and 100; this is an illustrative schedule until the League data is verified.

Prepare eight battle configurations for each leader, preserving Flying/Falkner, Bug/Bugsy, Normal/Whitney, Ghost/Morty, Fighting/Chuck, Steel/Jasmine, Ice/Pryce and Dragon/Clair. Give each leader a full six-Pokémon team at every tier, with coherent species, moves, abilities, held items and AI fitting their specialty and the tier’s difficulty. The eighth leader always fields six level-100 Pokémon, regardless of identity. Retain recognizable signature Pokémon where feasible. Type specialty allows thematic dual types and coverage moves.

Select the tier immediately before battle from saved Johto badge state, persist badge awards only on victory, and prevent duplicate badge awards. A rematch must not award another badge or count as another first challenge; its separate policy remains to be designed. Remove badge-dependent route/story gates that force a particular gym order, while preserving necessary story access. Ensure every Johto gym is reachable before earning a Johto badge so all orders are possible.

Validate all 16 gyms for roster/level accuracy, type identity, badge/story gates, and difficulty. For Johto, verify each of the 64 leader/tier configurations, all eight leaders as first and last challenges, tier changes after victories, stable tiers after defeats, and save/reload persistence. Check Kanto with all three starters and Johto with representative League-winning parties. Apply these requirements to milestone 3, milestone 4, and the Johto portion of milestone 5.

## Milestones and acceptance gates

1. **Reproducible tooling and untouched baseline.** Pin source/tool versions; retain originals; extract/rebuild without gameplay edits. Record complete file/archive inventory and verify no unexplained changes. Boot the baseline and round-trip output, enter gameplay, battle, save and reload. A byte-identical rebuild is ideal; if padding/container bytes differ, explain every difference and verify all executable/file payloads are preserved.
2. **First playable slice: Pallet Town to first rival battle.** New game spawns in Pallet Town with appropriate home/Oak setup. Implement starter choices at level 5: Pikachu, Eevee, Togepi. Give each a viable opening moveset. Initialize the slot-1 follower immediately upon confirmed starter receipt, before leaving the selection scene; set persistent starter/rival variables; remove dependencies on Johto introduction flags. Activate the National Dex on initial Pokédex receipt. Verify all three choices, decline/reselect behavior, rival teams, victory/defeat, map transitions, follower behavior and save/reload. Confirm selecting National mode does not mark all entries caught.
3. **Pallet through Brock.** Implement Route 1, Viridian, Oak's parcel, Route 2, Viridian Forest and Pewter. Reconcile progression flags, gates, shops, healing, captures, encounters and first badge. Verify that each starter can progress without an unintended softlock; tune teams/encounters rather than assuming Generation I balance still applies.
4. **Complete Yellow campaign.** Build and validate consecutive gym/story segments through the League. Track dependencies in an event/flag registry. Include Rocket encounters and special Yellow gifts. Check HM, badge, key-item, warp and story dependencies on every route and dungeon, including alternative ordering.
5. **All 493 species and retained features.** Complete acquisition/evolution coverage and NPC-service placements. Implement the confirmed Johto postgame: all eight gyms, regional events, inter-region travel, and appropriate postgame encounters and trainer levels. Track Kanto and Johto badges separately and audit every badge-dependent gate. Add facility access. Audit all entries for reachable acquisition paths and ensure new Pokémon do not break trainer parties, follower graphics, Dex pages, breeding or storage.
6. **Regression and release patch.** Fresh-save campaign playthroughs for all three starters; story sequence/return-trip checks, defeat recovery, save/reload, box operations, evolution, breeding, clock changes and long sessions. Validate patch application against the exact input hash and output checksum. Document mechanics, known limits and save compatibility. Produce a patch and documentation; do not automatically commit/push the uploaded ROM binaries.

Keep event flags, variables, script/file identifiers and edited archive members under version control as structured data. Do not hard-code offsets until confirmed for this exact ROM revision. Store generated working ROMs separately from original uploads. Build steps must reject a wrong input hash and never overwrite the originals.

## Immediate next work

Continue the separate Pallet opening implementation in `tools/pallet.py`, using the verified asset registry in `opening-assets.json`. Regenerate it with `yellow-heartgold/.venv/bin/python yellow-heartgold/tools/inspect_opening.py`. The inspector checks the original ROM hash, identifies the unique decompressed new-game location, and records script, initialization-script, message and event IDs and hashes for Pallet, the player’s house and Oak’s lab. It does not modify a ROM.

Preserve HeartGold’s original events that take place in Kanto, including their scripts and dependencies, for later adaptation and relocation into the new Johto postgame. Determine their destination maps, actors, sprites and progression requirements later; do not delete or overwrite those original event assets while implementing Yellow’s Kanto campaign. Implement the Pallet opening with separate script assets, including starter receipt and the first rival battle, and relocate home/blackout recovery. Validate house/lab warp links and follower behavior on fresh saves before releasing a replacement for prototype 001. Keep the existing early National Dex grant; the parcel-return timing change is deferred at the user’s request.

Prototype 001 remains the Android-tested reference build. Prototype 002 starts in the Pallet bedroom and uses appended opening assets for the house, town and Oak’s lab. Fresh-game house/lab traversal, all three starter choices with immediate visible followers, the National Dex UI, repeat Oak interactions and normal Togepi save/reload have passed emulator checks on the released build. The first Pallet rival battle, Route 1 encounter balance, story gates, all 493 acquisition paths and the full campaign remain unfinished. Do not treat this opening slice as a complete campaign.
