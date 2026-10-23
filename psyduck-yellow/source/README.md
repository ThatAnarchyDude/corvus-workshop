# Psyduck Yellow — source

The build tools, tests, data and notes behind **Pokémon Psyduck Yellow** (latest: prototype 0050 BETA). Each prototype is produced by chaining small Python patch scripts, each starting from the previous build's ROM; the public downloads are `xdelta` patches of those ROMs (see the [Releases](https://github.com/ThatAnarchyDude/Psyduck-Yellow-Releases/releases)).

## Layout
- `tools/` — the patch and build scripts (one module per area or feature, e.g. `starter_eevee_line.py`, `novareon.py`, `stellar_stab.py`, `stellar_rainbow.py`, `new_images.py`, `starter_display_fix.py`, `build_release_00xx.py`) and small emulator-test helpers.
- `tests/` — offline tests that need no ROM; `data/` — Yellow-derived tables and event data as JSON; `asm/` — hand-written Thumb patches; `pkhex/` — PKHeX plugin source; `art/` — title artwork.
- `*-PLAN.md`, `CAMPAIGN-FIRST-PLAN.md` and other notes — design decisions, owner approvals and test records, newest last.

## What is NOT here (and why)
- **No ROMs, saves, emulator states or game files** — the original HeartGold ROM and every built game stay on the developer's machine. The scripts need your own legally obtained USA HeartGold to do anything.
- **Private dependencies are not included**: a working copy of hg-engine, the PKHeX forks and the developer's original sprite library live in a separate local folder. Scripts that reach for them (for example `tools/novareon.py`) will not run from a plain checkout.
- Build output, test fixtures and screenshots.

The scripts were written to run from a local project folder; some paths and notes mention the developer's own machine. They are published so the work can be read and audited, not as a one-command build.

## Prototype notes (newest first)
**Prototype 0050 BETA** — the starter Eevee line (all eight Eeveelutions plus the new Stellar-type Novareon via a Sandwich, each with its own Mega), the Stellar type with its rainbow tag, new Sandwich and Novareon icons, and fixes for the starters' evolution screen, summary sprites and shiny Mega colours. See the [development log](../DEVELOPMENT-LOG.md).

**Prototype 0042 BETA** — Silph Co., Victory Road, the second Route 22 rival battle, the Route 22 badge gate and the way to the League and Hall of Fame.

**Prototype 0041** — Pokémon Tower, the Celadon Gym, the Rocket Hideout, Routes 8 and 11–18, the Fuchsia, Saffron, Seafoam and Viridian gyms, the League, Mega Psyduck and the free Mega Stones.

---

Prototype 0024 adds Yellow’s Route 25 trainers, encounters, hidden Ether/Elixir and reusable Seismic Toss TM, plus Bill’s visible separation scene and automatic S.S. Ticket reward. See [ROUTE25-BILL.md](ROUTE25-BILL.md) and the [validation record](validation-prototype-0024.json). The returning Cerulean robbed-house/Dig event follows next.

Prototype 0023 continues through Route 24 and Nugget Bridge, including Yellow’s contest teams, Nugget/Rocket event, Charmander gift and reusable Thunder Wave TM. It also corrects Blue’s bridge approach lanes and height, the fossil rendering and mandatory Mt. Moon battles. See [ROUTE24.md](ROUTE24.md) and the [validation record](validation-prototype-0023.json).

Prototype 0022 repairs the normal-save and daily-reset regressions reported in 0021, recognizes retained one-time rewards, removes stale saved custom NPCs, shows Kanto’s badges above Johto’s and adds the temporary Friendship Charm to bedroom PC storage. See [SAVE-COMPATIBILITY.md](SAVE-COMPATIBILITY.md) and [the validation record](validation-prototype-0022.json). Back up the normal save and use Continue; recovery relies on retained evidence.

Prototype 0021 restores Cerulean’s initial Yellow visit, the Bike Voucher exchange and Pewter’s mandatory pre-Brock escort. Its startup issue was repaired, but later playtesting found save-flag bugs; use 0022 for those fixes. See [CERULEAN.md](CERULEAN.md). Route 24/25, Bill and the returning robbed-house event follow next.

Prototype 0020 adds the requested two-way Route 4 return crossing and free HM02 Fly at Celadon’s third-floor TM counter, with no badge required for outdoor Fly during testing. Normal saves remain compatible. Cerulean campaign work moves to 0021. See [TESTING-TRAVEL.md](TESTING-TRAVEL.md) and [the validation record](validation-prototype-0020.json).

Prototype 0019 adds Yellow’s Route 4 encounters, optional Lass and reusable Whirlwind TM. It also restores working signs, requires A to read Kanto signs and keeps ground item balls solid. This checkpoint carries normal 0018 saves forward; Cerulean City is next. See [ROUTE-4.md](ROUTE-4.md) and [the release validation record](validation-prototype-0019.json).

Prototype 0018 adds Mt. Moon, its fossil choice and Jessie/James ambush, cave rewards and Center services, plus bulk Rare Candy use with a quantity picker. It is cumulative from 0017; Route 4 remains unconverted. See [MT-MOON.md](MT-MOON.md) and [the release validation record](validation-prototype-0018-release.json).

Prototype 013 fixes League gate direction and progression, exact lab experience, mandatory Oak Poké Balls, Daisy/Trainer House messages and long dialogue; it adds Yellow’s early Route 22 Blue battle with his lab starter, a random Psyduck/Eevee choice of opposite gender for Togepi players, and matching 1-in-4,096 shiny and 1-in-16,384 perfect-IV odds. See [PROTOTYPE-013.md](PROTOTYPE-013.md). Global base shiny odds are 1/4,096, or 1/2,048 with the passive Shiny Charm supplied through the bedroom PC. Perfect Legendary IVs apply only to the 17 existing Yellow/HGSS encounter species listed in the release notes.

Prototype 012 completes the Viridian opening groundwork with Cut trees, removable lesson barriers, the granddaughter, a temporary west guard and the cashier’s Pokégear/Town Map reward. See [PROTOTYPE-012.md](PROTOTYPE-012.md).

Prototype 011 fixes the three-lane coffee gate, Blue’s touch-screen portrait and Eevee’s intro position. See [PROTOTYPE-011.md](PROTOTYPE-011.md). Route 2 and Viridian Forest follow after this correction playtest.

Prototype 010 adds Viridian’s old-man catching tutorial and Oak’s visible Pokédex pickup. See [PROTOTYPE-010.md](PROTOTYPE-010.md). Route 2 and Viridian Forest are next after this playtest.

Prototype 009 updates Oak’s introduction with shiny Eevee and FireRed Blue’s rival portrait. See [PROTOTYPE-009.md](PROTOTYPE-009.md) for playtest and build notes. HeartGold’s shop progression remains intact.

Prototype 008 fixes the Viridian Center doorway and retires the parcel escort cashier after leaving the Mart. See [PROTOTYPE-008.md](PROTOTYPE-008.md) for playtest and save notes.

# Pokémon Psyduck Yellow — implementation plan

Status: prototype 007 opens Route 1 and Viridian for Oak’s Parcel, adds Mom’s Running Shoes scene and a walking cashier escort, and grants the National Pokédex only after delivery; see [PROTOTYPE-007.md](PROTOTYPE-007.md). Prototype 006 added PC evolution supplies and the requested item evolution methods; its Android playtest passed according to the owner. Prototype 005 added the animated Psyduck/water title to prototype 004's Pallet opening. Prototype 001 is the earlier Android-tested reference build. Prototype 002 adds a separate Pallet opening. Prototype 003 adds Oak's exit stop, Blue's starter pickup and lab-exit battle, and a bounded Route 1 test with Yellow encounters and NPCs. See the matching release's `validation.json` and `ANDROID-TESTING.md` for evidence and remaining checks, and [BUILDING.md](BUILDING.md) for reproducible build commands. The full Yellow campaign and Johto postgame remain to be implemented.

## Agreed scope

Recreate Pokémon Yellow's Kanto story and progression in the US HeartGold engine and graphical style. Use all 493 Generation I–IV species. Starter choices are Psyduck (54, always male), Eevee (133, always female), and Togepi (175, normal gender ratio). The lab table order is Psyduck on the left, Togepi in the center, and Eevee on the right. The National Pokédex is available when the player receives their first Pokédex, without a regional-Dex completion gate; entries still require seeing/catching Pokémon normally. Prototype 007 grants the National Pokédex after returning Oak’s Parcel, matching Yellow’s story timing. Starter selection grants no Pokédex. Imported earlier saves retain their records while access stays hidden until delivery.

Johto is the full postgame region, mirroring Kanto’s role in HeartGold: unlock travel after the Kanto campaign and first Pokémon League victory. Include its towns, routes, dungeons, eight gyms, regional story events, and services, adapted for postgame progression and difficulty. Implement travel between both regions and verify that returning to Kanto preserves completed story state. Rework HeartGold’s original Johto-first flags, introductions, badge checks, and travel unlocks for this reversed order.

Name the Yellow/Kanto rival during Oak's pre-game introduction, before the bedroom scene. Use that chosen name in Kanto's dialogue and rival battles. Preserve HeartGold's rival content for later Johto adaptation; that separate rival will use the default name Silver, without another naming sequence. Keep those identities separate when activating the Johto scripts and trainer data later.

Keep HeartGold's Generation IV battle rules: physical/special split, abilities, held items, natures, breeding, evolution rules, moves, and types. There is no Fairy type in this scope. Togepi and its evolutions retain their Generation IV typing. No hg-engine expansion is needed.

## Confirmed following-Pokémon behavior

Immediately after the starter selection is confirmed and the chosen Pokémon is added to party slot 1, initialize and display that Pokémon following behind the player. Do not wait for a later story event, first rival battle, Pokédex receipt, or Johto unlock. This applies equally to Psyduck, Eevee, and Togepi.

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

Prototype 001 passed its recorded emulator checks. Prototype 003 also passed its documented DeSmuME checks, and the owner reports using melonDS DS on both PC and Android with the prototype working as intended so far. These observations cover the tested opening, not the unfinished Yellow campaign; see the Prototype 003 release validation file for separately documented and unrun checks.

## Content and feature policy

Prototype 005 added the Pokémon Psyduck Yellow title with an animated Psyduck swimming over water. Later prototypes preserve that title.

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
2. **First playable slice: Pallet Town to first rival battle.** New game spawns in Pallet Town with appropriate home/Oak setup. Implement starter choices at level 5: Psyduck, Eevee, Togepi. Give each a viable opening moveset. Initialize the slot-1 follower immediately upon confirmed starter receipt, before leaving the selection scene; set persistent starter/rival variables; remove dependencies on Johto introduction flags. Activate the National Dex on initial Pokédex receipt. Verify all three choices, decline/reselect behavior, rival teams, victory/defeat, map transitions, follower behavior and save/reload. Confirm selecting National mode does not mark all entries caught.
3. **Pallet through Brock.** Implement Route 1, Viridian, Oak's parcel, Route 2, Viridian Forest and Pewter. Reconcile progression flags, gates, shops, healing, captures, encounters and first badge. Verify that each starter can progress without an unintended softlock; tune teams/encounters rather than assuming Generation I balance still applies.
4. **Complete Yellow campaign.** Build and validate consecutive gym/story segments through the League. Track dependencies in an event/flag registry. Include Rocket encounters and special Yellow gifts. Check HM, badge, key-item, warp and story dependencies on every route and dungeon, including alternative ordering.
5. **All 493 species and retained features.** Complete acquisition/evolution coverage and NPC-service placements. Implement the confirmed Johto postgame: all eight gyms, regional events, inter-region travel, and appropriate postgame encounters and trainer levels. Track Kanto and Johto badges separately and audit every badge-dependent gate. Add facility access. Audit all entries for reachable acquisition paths and ensure new Pokémon do not break trainer parties, follower graphics, Dex pages, breeding or storage.
6. **Regression and release patch.** Fresh-save campaign playthroughs for all three starters; story sequence/return-trip checks, defeat recovery, save/reload, box operations, evolution, breeding, clock changes and long sessions. Validate patch application against the exact input hash and output checksum. Document mechanics, known limits and save compatibility. Produce a patch and documentation; do not automatically commit/push the uploaded ROM binaries.

Keep event flags, variables, script/file identifiers and edited archive members under version control as structured data. Do not hard-code offsets until confirmed for this exact ROM revision. Store generated working ROMs separately from original uploads. Build steps must reject a wrong input hash and never overwrite the originals.

## Repository safety and release practice

The current development branch is `android-prototype-013`; its starting point is the known-good prototype 003 branch, after removal of complete modified DS ROM ZIP archives from the branch contents. The project files are still in a **public** GitHub repository, so do not put original or rebuilt ROMs, proprietary SDKs or private assets into commits.

- The repository-root `.gitignore` excludes common ROM and save file extensions, plus local build outputs.
- `python3 yellow-heartgold/tools/check_repo_safety.py` examines tracked files and ZIP members for known ROM/save extensions. GitHub Actions runs it for future pushes and pull requests on this branch.
- Release **patch archives and source instructions**, not complete game ROM archives. Verify clean-base input and patched-output hashes before publishing.
- Removing ROM archives in new commits does **not** remove their blobs from historical commits or existing clones. A separate coordinated history rewrite and cache/retention review may be necessary; do not force-rewrite public release branches without a migration plan.
- Scripted builds must not overwrite the input ROM, and their output belongs only in ignored local build directories.

## Prototype 004 staging

Prototype 004 implements visible Oak choreography, an animated Psyduck field capture, the shifted three-ball table, Blue naming artwork, and the native starter property/follower hooks. See [PROTOTYPE-004.md](PROTOTYPE-004.md) for evidence and known limits. Prototype 003 remains the earlier user-tested reference.

**Current playable boundary:** prototype 007 extends Route 1 into Viridian for the parcel loop. Mom unlocks Running Shoes, the cashier escorts the player into the Mart, and Oak grants the National Pokédex after delivery. Route 2 and Route 22 remain blocked. Advance to Route 2 and Viridian Forest after this slice passes the owner’s playtest. Preserve HG’s original Kanto assets for later Johto-postgame adaptation.

**Regression gate:** fresh starts for Psyduck/Eevee/Togepi, intro/rival naming and battle, follower behavior, save/reload, Route 1 Potion one-time event, encounter distribution, map transitions and blackout recovery. Do not assume Android parity from PC-only automated tests. Record what actually ran and keep untested behavior clearly labeled.

## Immediate next work

Keep development limited to Pallet's opening and the first Route 1 grass path until the user has tested this slice and agrees to advance. Work one town and one route at a time. Use `tools/opening.py` for prototype 003, building on `tools/pallet.py` and the verified asset registry in `opening-assets.json`. Regenerate that registry with `yellow-heartgold/.venv/bin/python yellow-heartgold/tools/inspect_opening.py`. The inspector checks the original ROM hash, identifies the unique decompressed new-game location, and records script, initialization-script, message and event IDs and hashes for Pallet, the player’s house and Oak’s lab. It does not modify a ROM.

Preserve HeartGold’s original events that take place in Kanto, including their scripts and dependencies, for later adaptation and relocation into the new Johto postgame. Determine their destination maps, actors, sprites and progression requirements later; do not delete or overwrite those original event assets while implementing Yellow’s Kanto campaign. Implement the Pallet opening with separate script assets, including starter receipt and the first rival battle, and relocate home/blackout recovery. Validate house/lab warp links and follower behavior on fresh saves before releasing a replacement for prototype 001. The owner approved moving the National Dex grant to parcel delivery for prototype 007.

Prototype 001 remains the Android-tested reference build. Prototype 002 starts in the Pallet bedroom and uses appended opening assets for the house, town and Oak’s lab. Prototype 003 retains those assets and adds another set for the bounded opening. Original Route 1 trainers are retained in their original event bank, while the active copy has no trainer battles. Yellow's Pidgey/Rattata encounters preserve weighted species/level probabilities in HG's 12-slot format at all times of day. Blue's new parties are level 5 and branch from the selected starter. Northward travel is blocked for this test. A dedicated Oak capture battle screen, later Kanto progression, gym adaptations, all 493 acquisition paths, Johto postgame remain unfinished. Consult the release evidence before claiming a gameplay check passed.

## Planned dialogue review

The owner will provide a “Current Dialogue → Expected Dialogue” list. Review and apply those revisions later; broad dialogue rewrites are deferred while the area conversion continues.

## Live cloud testing

See [LIVE-TESTING.md](LIVE-TESTING.md) for the default-off DS frame stream, read-only RAM HUD, agent-controlled video switches, and optional Xvfb/noVNC setup. Remote viewing requires a workspace port-forward or tunnel; a local server alone does not create a ChatGPT preview panel.
