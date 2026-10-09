# Build status and commands

The build foundation and experimental prototype 001 are implemented. Run `yellow-heartgold/.venv/bin/python yellow-heartgold/tools/prototype.py` from the repository root to build the prototype. See ANDROID-TESTING.md for its implemented changes and limitations.

From `/workspace/corvus-workshop`:

```sh
python3 -m venv yellow-heartgold/.venv
yellow-heartgold/.venv/bin/python -m pip install -r yellow-heartgold/requirements.txt
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/build_rom.py
```

Outputs are ignored under `yellow-heartgold/build/`: `heartgold-baseline.nds` and `baseline-report.json`. The builder verifies the exact original SHA-256, repacks through pinned ndspy 4.2.0, reloads the result, and compares all 513 file payloads, filenames, ARM9/ARM7 binaries, overlay tables, banner and RSA-signature bytes. It checks that the original remains unchanged. These comparisons establish payload preservation, not playable behavior or cryptographic signature validity.

Current output is 126,645,960 bytes versus the original 134,217,728 bytes. The repacker changes container layout/padding. Every checked payload is identical, but the output is not byte-identical and must pass boot, battle and save/reload checks before serving as a validated base. Prototype 001 emulator checks are recorded in `build/validation.json`; baseline-only gameplay checks are distinct from that prototype validation. Do not treat this output as the requested game.

## Located implementation points

Source reference: pret/pokeheartgold commit `9d8b7591f09b65804da2fb2dfd56f320633e0d36`, inspected in `/tmp/yellow-hg-reference`. This temporary checkout is not a permanent build dependency.

- `src/choose_starter.c`: constructs level-5 starter Pokémon and adds the selected one to the party. Original species table `[152,155,158]` occurs once in decompressed ARM9 at `0x108514` for this exact input. Planned replacement is `[25,133,175]`.
- `src/choose_starter_app.c`: selection screen has a second species table. Original table occurs once in decompressed overlay 61 at `0x1a98`. Presentation and actual receipt must change together. Confirm UI text, cries, graphics, rival scripts and persistent starter state before calling a table replacement complete.
- `src/choose_starter.c`: party receipt is in state 3; the field overlay reloads before fading back to gameplay. This is the integration point to inspect for immediate follower creation.
- `src/follow_mon.c`: original follower code uses `GetFirstNonEggInParty` and `GetFirstAliveMonInParty_CrashIfNone` in some paths. Therefore stock behavior does not always mean literal slot 1. Audit and adapt those paths to the requested slot-1 rule, including fainted leads and egg/empty-party handling. All-species graphical coverage is distinct from slot-selection correctness.

Offsets refer to decompressed component data, not offsets to write directly into the original ROM. Compression, ARM9 module parameters, overlay compressed-size metadata and runtime loading must be handled correctly before binary edits are made.

Prototype 001 now patches the coordinated starter tables/text, early Dex grant, follower selectors, Togepi opening moves and first rival teams. Six focused binary/script tests pass, and xdelta round-trip reproduction passes. Consult build/validation.json for completed emulator checks. All three starter receipt paths and Eevee normal save/reload have passed emulator checks. The user also reports successful Android testing. Follower reordering, fainted leads, eggs and all-species coverage remain unverified. Pallet relocation, story replacement and gym scaling remain to be implemented. The next opening build will retain the current early National Dex grant; relocating it to Oak’s parcel return is deferred.


## Prototype commands

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/prototype.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -v
```

The builder optionally generates and round-trip verifies the xdelta patch when `.tools/xdelta3` exists. The current ignored tools directory contains xdelta3 from Debian’s signed trixie package indexes, and a locally compiled DeSmuME libretro core (upstream commit `95b4d798731caa809125b6c3c11d17cc332ff6ef`). No proprietary BIOS/firmware was required for this emulator smoke test. The core uses built-in emulation.

`tools/emulator_smoke.py` is a local ctypes/libretro test harness. Run it with system `python3` (Pillow available), the ROM path, and a JSON list of actions containing `frames`, optional `buttons` (libretro joypad IDs), optional `touch` coordinates in the 256×384 stacked-screen layout, and optional `screenshot` output filenames. Add `--fresh` to start without loading the previous test state. Test states, screenshots and RAM dumps remain ignored under `build/emulator/`; they are development artifacts, not included in the Android patch package.

## Pallet development build

Prototype 002 is built separately from the exact tested prototype 001 output:

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/pallet.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -v
```

Outputs are `build/yellow-heartgold-prototype-002.nds`, its `.xdelta`, and `build/pallet-report.json`. The builder appends separate opening scripts, initialization scripts, text and event copies, and redirects four Pallet map headers to those additions. Original Kanto archive members remain available for the future Johto postgame. The only existing script changes remain the two Johto prototype-001 entries. The shared starter UI now names Oak. New-game and home-return positions and initial home recovery move to Pallet. The National Dex remains granted at starter receipt. Separate map-transition scripts unlock Bag, Trainer Card, Save and Options without requiring the Johto mother introduction. Oak’s gift uses the native follower release sequence and records the chosen starter for future rival branches.

Use `--output-dir yellow-heartgold/build/emulator-002` with the emulator harness to isolate prototype-002 save states and normal saves from prototype 001. Its first rival battle, route encounter balance and campaign progression are not yet implemented. Consult the build report and validation evidence before distributing it as a playable test.

## Bounded opening build

Prototype 003 builds from the exact released prototype 002 and keeps its previous assets intact:

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/opening.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -v
```

Outputs are `build/yellow-heartgold-prototype-003.nds`, its `.xdelta`, and `build/opening-report.json`. The builder requires the local xdelta3 tool and verifies patch application against the untouched original HeartGold ROM. New scripts, events and messages implement Oak's Pallet north-exit stop, starter pickup by Blue and a level-5 lab-exit battle. A separate pre-starter exit guard prevents leaving Oak's lab without a partner. Saved variables `0x416F` and `0x416E` track Oak and rival progression; the report records the reserved flags and variables.

Route 1 uses Yellow's Pidgey/Rattata levels and weighted encounter probabilities for all three time periods. Its four original HG trainers are removed from the active event copy and retained in the original archive member. Yellow's two non-battling NPCs replace the active route actors. A full-width coordinate guard limits the opening test to the first grass path. Do not unlock another town or route until its content has been adapted and verified.

Opening dialogue is transcribed from pret/pokeyellow at the revision recorded in `data/yellow-opening-dialogue.json`, then reflowed into HG's message format. Player and rival names remain dynamic. The three-starter choice requires adapted gift dialogue. Oak's escort currently uses a lab transition, without the full Yellow Pikachu capture scene, and the rival battle retains HG's rival portrait.

`tools/intro.py` restores the rival-name step in Oak's pre-game introduction after player naming and before the bedroom. It assembles the Thumb-1 wrapper in `asm/oak-rival-name.s` using pinned Keystone 0.9.2, verifies the original overlay-53 hash and hook, and extends that overlay within a checked size bound. HG's existing naming overlay, confirmation controls and final name-save routine are reused. Player-name arguments are left separate; the unused `OakSpeechData.unk_010` field tracks this new introduction phase. Two messages are appended to the existing intro bank without changing its original entries. Original Kanto event banks remain intact.

New rival parties use HG's rival trainer class, which reads the saved name instead of a fixed trainer label. Saved variable `0x416C` records the first lab battle's win/loss result for future Yellow story dependencies. Johto's later HG rival will have the separate default identity Silver; no second naming scene is planned.

Use a new game and `--output-dir yellow-heartgold/build/emulator-003-final` to keep prototype 003 saves separate. Final release evidence and explicitly unrun checks belong in `releases/prototype-003/validation.json`.

## Prototype 004

See [PROTOTYPE-004.md](PROTOTYPE-004.md) for the current builder, downloader and actual verification evidence. Older sections above describe earlier releases; their starter UI and portrait details are superseded for prototype 004.

## Prototype 005 title screen

See [PROTOTYPE-005.md](PROTOTYPE-005.md) for the title builder, generated-art inputs, normal-save compatibility and exact validation scope. `tools/title.py` requires the exact tested prototype-004 input; it changes only title resources and the banner.

Prototype 006 builds on the exact prototype-005 output. Run `yellow-heartgold/.venv/bin/python yellow-heartgold/tools/evolution_testing.py`, then package with `tools/package_playtest.py ... --version 006`. See [PROTOTYPE-006.md](PROTOTYPE-006.md) for commands, PC upgrade behavior and validation.

## Prototype 007 — Oak’s Parcel

Requires the exact prototype-006 output and supported pristine USA HeartGold ROM, both kept locally and ignored.

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/parcel_quest.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests -q
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-007 --version 007
python3 yellow-heartgold/tools/check_repo_safety.py
```

The builder appends quest script/text/event assets and a small ITCM Dex gate. It retains prototype-006 evolution and title data and every original script/event member. Quest variables use the existing save layout: shoes 0x4169, parcel 0x416A, cashier 0x416D; flag 0xB52 marks initialization and 0xB53 tracks Oak’s one-time Poké Balls. Type-3 map scripts also run the Dex gate when importing a normal save. Seen/caught records are preserved. Running Shoes use unused item ID 113 and native running functionality. Read the release’s playtest notes before interpreting scripted model checks as emulator evidence.

## Prototype 008 — Viridian fixes

See [PROTOTYPE-008.md](PROTOTYPE-008.md) for the incremental builder, required input and checks. It builds from the exact prototype-007 output and keeps that release reproducible.

## Prototype 009 — Yellow shop stock

See [PROTOTYPE-009.md](PROTOTYPE-009.md) for the incremental builder and fixed inventory dispatch. Requires the exact prototype-008 output.
