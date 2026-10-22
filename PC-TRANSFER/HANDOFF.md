## Governing owner override — October 16, 2026
Read yellow-heartgold/CAMPAIGN-FIRST-PLAN.md before selecting work. Complete playable Yellow Kanto first: (1) progression bugs/softlocks, (2) required campaign maps/events/battles/HMs/badges, (3) polish, (4) deferred optional Yellow content. Preserve all completed work. The mandatory restoration checklist retains postponed features, including expanded PC storage/editor integration; these are no longer 0031 release blockers. Package after each minimally functional map and at least once per active 24-hour development period, with verified patch links and completed/unfinished/test notes. If no safe newer build or meaningful progress is possible, provide the stable build, explain attempts/obstacle/changed approach, and await owner instructions on the blocked task. Unchanged builds do not count as progress. Immediate order: deliver tested 0031 improvements after release checks, then Cut-to-Lt. Surge progression and onward campaign dependencies. Earlier ship polish and PC-hook next-step instructions are superseded.

# Corvus Workshop handoff

## Current project rules
> - Every released test version from prototype 0029 onward must have its own verified public browser patching page. Post its link in chat and a dated entry in the public GitHub plain-language log, and update the latest-patch link. Preserve earlier release pages. Delivery is incomplete until these links are available. Publish patch pages and documentation only; keep ROMs local and unfinished builds private.
These rules supersede conflicting historical notes below.
> - Recreate Yellow’s full Kanto campaign in HeartGold’s engine, preserving all approved Psyduck Yellow customizations. Complete Kanto before developing Johto’s postgame.
> - Unlock Johto only after completing the Kanto campaign, defeating the Elite Four for the first time and entering the Hall of Fame.
> - Preserve HeartGold’s Johto content. Modify only the specific HM or access requirements necessary to traverse the entire region using Kanto-earned unlocks, and only when an actual need arises. The Soul Badge permits Surf in both regions; the Fog Badge remains an alternative.
> - Preserve the supplied Oak introduction and naming screens exactly, native HeartGold interiors, and the approved shared Day Care functionality.
> - Connect outdoor areas where practical. Shorten Yellow layouts when necessary to fit connected HeartGold geography, provided their intended gameplay is preserved.
> - Show small location-name banners on every named-area entry. Show native full-screen previews only on first entry and first entry after a time-of-day change.
> - Keep Blue as the Kanto rival before the first Hall of Fame. Giovanni remains Rocket and Viridian Gym leader until then; Blue takes over afterward.
> - After completing and testing each localized area, release the next numbered prototype, update the patching page, and post its link and an audiovisual test recording in chat and the plain-language GitHub log.
> - Keep originals, saves and generated ROMs local and ignored. Keep Project Recovery read-only. Publish only explicitly authorized patch pages, recordings and documentation; never publicly push ROMs or unrelated project source.
> - Maintain a working live viewing stream whenever execution and connectivity permit. Restore failed connections and create a new streaming tunnel when necessary without waiting for another reminder or approval. Show live game video and audio throughout actual in-game testing so the owner can watch the tests as they happen. Between playtests, pause picture and sound while keeping the server and tunnel connected whenever possible. Keep all game controls private. Whenever the viewing URL changes, post the new link in this chat and update the current viewing link in the GitHub plain-language development log.
> - Follow the latest checkpoint plan, record verified results accurately, and continue independent work while deferring unclear departures from Yellow.

> - Kanto shop progression (owner, October 13): all ordinary Kanto Marts, including Lavender, share cumulative inventory based on distinct Kanto badge count. Keep native HeartGold interiors and both vendors: northern sells balls, southern sells general supplies. Start with Yellow Viridian stock; successive badges add missing items from Pewter, Cerulean, Vermilion, Lavender, Fuchsia, Saffron, Cinnabar and Viridian. Lavender supplies the fourth-badge additions instead of Celadon. Never remove unlocked items; rematches and Johto badges do not advance stock. Do not sell Master Balls or Cherish Balls. Johto shops, Celadon Department Store and Pokemon League-area shops remain present with unchanged HeartGold inventories and prices. Apply the shared system to Vermilion first, then other regular Kanto Marts as work progresses.

> - Officer Jenny's Squirtle gift requires a free party slot. If the party is full, say exactly: "Oops. You already have a full party with you. Please, come back when you have a free spot?" Keep the gift available and commit its completed flag only after successfully adding Squirtle to the party. Do not send this gift to PC Storage. This approved customization supersedes Yellow's Box fallback requirement.

## Historical Notes:
Approved exception (October 13): Soul Badge unlocks Surf in BOTH Kanto and Johto; Fog Badge remains an alternative. This supersedes the earlier region-specific Surf rule. Other Johto preservation requirements still apply.

The owner is moving development from cloud to Windows with Ubuntu WSL2.

This working copy combines published main files with missing build source
from prototype-0025-source. Published files were preserved.

Latest release: Psyduck Yellow prototype 0029.
Next: prototype 0030, Vermilion City campaign conversion; read the latest appended checkpoint.
Read psyduck-yellow/DEVELOPMENT-LOG.md and
yellow-heartgold/PROTOTYPE-0030-PLAN.md and the latest appended checkpoint for current details.

0025 fixes bridge trainer visibility, the bridge sign, Bill's visible PC,
and the Cerulean Rocket/Dig quest. The restored cloud source reproduced
the published checksum and passed 14 focused tests.

Owner clarification (October 13, 2026): recreate Yellow's Kanto layout,
events, characters, progression and story roadblocks in HeartGold's DS engine.
Retained HG Kanto geometry is no longer the final target; audit earlier areas
and rebuild maps where needed. Existing approved Psyduck Yellow customizations
carry forward. Unlock Johto after the first Elite Four victory and Hall of Fame,
preserving HG Johto gameplay as much as possible in the requested open-world
postgame. Audit regional story flags, badges, travel and shared services. ONLY to reflect these specifications.
Kanto comes first; Johto is planned as postgame. Preserve original
HeartGold assets, earlier checkpoints and the two requested Viridian Cut trees.
Dialogue revisions and Blue's Eevee-evolution teams await the owner's lists.
Publish a new version under the current "prototype" naming convention, and post a link to the patcher we've been using so the owner can update their own local versions with each prototype release. Do this every time you finsh work and testing on a new localized area within the game's world.
Android editor development is paused; the melonDS freeze report is parked.

PC setup remains incomplete: private inputs, checkpoint ROMs, Python
dependencies and native emulator tools still need local verification.
The missing chat transcript and user saves were unavailable in cloud.
Never treat a prepared test save as the owner's campaign progress.

Power Simulator is also retained under power-simulator/.

Local testing setup update (October 12, 2026): installed Linux x86_64
DeSmuME core from Libretro buildbot under ignored yellow-heartgold/.tools/emulator.
Shared-library dependencies resolve; native adapter ran 900 boot frames on 0025,
producing both DS screens and 4 MiB RAM. This is boot validation only, not yet
campaign Continue or save/reload validation. Core provenance: downloaded
https://buildbot.libretro.com/nightly/linux/x86_64/latest/desmume_libretro.so.zip;
pin the local checksum before future replacement. Original user RetroArch ROM
matches published 0025 SHA-256. User's latest supplied .dsv is copied under ignored
build/owner-save-0025-backup/campaign-original.dsv; originals remain untouched.
RetroArch has both Windows DeSmuME and DeSmuME 2015 DLLs. No live viewing link
has been established yet.

Live dashboard started locally on port 8080 with an isolated campaign save copy;
Windows localhost HTTP returned 200 and video was enabled. Live feed is silent.
Android forwarding could not be applied: Windows requires Administrator rights.
PC-TRANSFER/Enable-Android-Live.ps1 prepares local-subnet/Private-profile access;
requires user-run Administrator PowerShell. No Android reachability verified.
Current runner is loopback-only and has no token; do not enable forwarding until
an access token is configured for the runner. Stop the runner when not testing.

Owner explicitly approved Cloudflare remote viewing with audio. Tunnel connected;
remote dashboard and native stereo PCM delivery verified, missing token denied.
Live runner now supports browser Enable sound. Seven bridge tests pass. Exact A/V
sync and Android physical-device playback are not yet validated. Tokens and URLs
remain local/private. Do not use the earlier Android LAN-forward script: remote
viewing uses the tunnel and does not need that forwarding rule.

Owner decisions during October 12 PC session:
- Do not touch Johto maps/events/encounters/gameplay. Kanto Day Care may reuse
  the native shared Johto Day Care save store and interactions, explicitly approved.
- Blue remains Kanto rival (no Leader title) before first Elite Four/Hall of Fame.
  Giovanni leads Rocket and Viridian Gym until then; Blue takes over afterward.
- Continue autonomously until finished or owner asks to pause; defer unclear choices.
- Hourly continuation heartbeat created: continue-psyduck-yellow-development.
  Local execution depends on Codex/PC availability and usage; no bypass promised.
- Native Continue from owner's backup loaded Route 25 (map 29), party size 3,
  parcel state 2, National Dex true. Source save/ROM unchanged.
- Owner confirmed stream is MUCH better after replacing the Python pixel loop
  with Pillow native RGB555/RGB565 decoding and restoring continuous MJPEG.
  Current runner uses --fps 24; remote token/link stays private and local.

Discord project-update plugin prepared (October 12, 2026):
- Private plugin "Discord Project Updates" created, backend ID
  plugins_6accc78b0cd081918de3300a743fe0ac, release
  pluginrel_6accc78b827c8191bdbeccad7e4e8b1d.
- Source and ZIP are in the owner's Project Recovery folder, separate from
  game source; no public push. Skill reads current notes and latest checkpoint
  plan, distinguishes development from releases, and excludes private artifacts.
- Python webhook sender passed offline checks for content limits, destination
  validation, mention suppression, per-date deduplication and uncertain-send
  blocking. Mocked sends only; no actual Discord post or connection verified.
- Target channel, daily time and webhook setup await the owner. No daily
  reporting automation created; existing development heartbeat unchanged.

Discord reporting setup completed (October 12, 2026):
- Plugin renamed Our Pokemon ROMHax, v0.1.1, red/black icon with light detail.
  Private release: pluginrel_6accc93e9ffc819180b05613d828e652.
- Owner selected channel webhook (existing bot offered but not needed).
  Incoming webhook verified for channel 1559168884488274010 via read-only API.
  Credential stored in Windows current-user Environment; never copy it here.
- Active daily heartbeat: our-pokemon-romhax-daily-discord-update, noon
  America/Indianapolis (EST/EDT). Reads current project notes and latest plan.
  First scheduled message is a status baseline; no initial test post sent.
- Sender also reads stored Windows user environment if Codex lacks an inherited
  variable. Per-date ledger: LOCALAPPDATA/CorvusWorkshop/discord-update-state.json.
- No end-to-end Discord send claimed yet. Runs depend on local PC/Codex availability.

Current implementation progress (October 12 morning):
- Route 5 foundation source: tools/route5.py, data/route5.json,
  tools/build_prototype0026.py; build/0026-route5-foundation.nds preserved.
- Six Route 5 tests pass. Native Day Care greeting/deposit and separate withdrawal
  with 100 fee observed. Normal in-game save then fresh Continue in development
  ROM retains map 517, party size 2, parcel state 2 and National Dex. All 480 bytes
  of the Day Care block match before/after. Private evidence: build/0026-native-validation.json.
- Day Care location/terrain still HG Route 5 house, not finished Yellow placement.
- Saffron drink gate module added in tools/saffron_gates.py. Four compiled-script
  and binary-boundary checks pass. Flag 0xA9D and variable 0x414E reserved; all four
  Kanto gatehouses (389,390,391,493) share progress. Native gate checks pending.
  New build/0026-route5-gates-v1.nds; source 0025 and foundation preserved.
- Read-only source layout extractor tools/yellow_layout_reference.py creates
  private references only under build/. Yellow Route5: 20x36 walking tiles;
  HG currently has one 32x32 cell at world cell (40,5). Actual geometry unfinished.
- Live runner now uses 0026 foundation, build/live-0026-daycare-v1, clear prepared-
  save label, --fps 24. Same private Cloudflare tunnel. Native touch controls and
  labels added; eight live bridge tests pass. Originals and campaign backups untouched.
- Jessie/James candidates found in LucianoNeo/gen1recomp-mods; local ignored copies
  under build/jessie-james-candidates. OW artwork is black-uniform alternate art;
  battle portrait is small FRLG-style, credited to Ody-chan. Do not present these as
  confirmed HGSS-quality replacements or publish without checking original credits.
- Owner locked entire Oak new-game intro and both naming screens to supplied 0025.
- Owner requested area-name banners every named-area change, including repeat visits.
  Native routine 0x021EFAF8 in overlay 1: skips areaIcon=0 or interior map types.
  Routes/cities already have icons; repeat and seamless transitions still need native
  validation. No banner change implemented yet. Blue title/promotion still pending.
- Owner authorized GitHub documentation updates and recordings with completed
  prototype updates. Plan/log published via connector commits ce350ba and 009853c;
  local copies synchronized. No unfinished source or private artifacts published.
- User's laptop is always plugged in; sleep/hibernate Never, lid Do Nothing on AC.
  Codex app must remain running; selected chat and separate setup PowerShell not needed.

Latest corrections and owner requests:
- Gate state 0x414E was discovered in original Ice Path scripts. DO NOT USE
  build/0026-route5-gates-v1.nds or its gate fixtures for release validation.
  Source corrected to GATES_OPEN=0x4154, absent from original script/C/asm refs
  and other project modules. DRINK_GIVEN=0xA9D has no native uses beyond definition.
  Corrected build: build/0026-route5-gates-v2.nds. Four gate tests pass after correction.
  No native Johto resource was edited, and all temporary state changes were confined
  to ignored private save copies. The foundation/live Day Care build has no gate code.
- Horizontal live dashboard now displays top screen left, touch screen right on
  wide displays (wraps on narrow devices), using one MJPEG input and two canvases.
  Native touch maps to bottom screen only. Eight bridge tests pass. Reload the same
  private Cloudflare link and Enable sound after the runner restart; video enabled.
- Owner asked whether live link was posted publicly. It was not: public log mentions
  the private stream and links recordings. Do not publish the current control-token
  link. A separate view-only link would need implementing if explicitly requested.
- Owner requests every named-area transition banner, including repeat visits.
  Native 0x021EFAF8 calls 0x0203B388 (areaIcon) and 0x0203B58C (IsInBuilding),
  then FieldDrawMapName draw at 0x021EFA3C. It has no visit-history test itself.
  Kanto routes already icon=3, cities/towns 1/2, Forest 5; interior maps suppressed.
  Need verify seamless boundary call sites/repeat transitions and named interiors;
  do not claim area-banner request implemented yet.
- Two normal Day Care deposit/reload tests preserved 480-byte save block exactly;
  separate native withdrawal observed fee deduction from 999999 to 999899.
  Compiled tests/transport screenshots are NOT campaign difficulty evidence.

October 12, 2026 — prototype 0026 local checkpoint delivered:
- Playable ROM: C:/RetroArch-Win64/downloads/Pokemon-Psyduck-Yellow-prototype-0026.nds.
  SHA256 c3085440e6f27d02898c6a9dd56ab0f64a4ede4f92c7dcd61dbbde4a6c1be9d4.
  Latest owner 0025 normal save copied to a new 0026 filename in DeSmuME 2015 saves;
  no overwrite or original-save modification. Do not substitute the prepared recording save.
- Scope: Route 5 Yellow-weighted encounters, Underground Path sign, outdoor NPC removal,
  native Kanto Day Care sharing existing Johto storage. Six focused checks pass.
  Intro/naming, approved customizations and all original archive members/overlays preserved.
  Yellow terrain and Day Care placement remain incomplete; this is an incremental checkpoint.
- Cumulative xdelta patch reconstructed the exact ROM from the pristine USA HeartGold base.
  Offline patch page prepared at yellow-heartgold/build/prototype-0026-web/index.html.
  No public ROM/save upload and no source push. Existing checkpoints preserved.
- Real 40-second native gameplay/audio recording:
  yellow-heartgold/build/0026-release-recording-v1/daycare-continue-audio.mp4.
  Observed normal Continue into map 517 and attendant dialogue on a copied prepared save.
  Nonzero 44.1kHz stereo audio, encoded AV duration difference 0.014312 seconds.
  Earlier deposit/withdrawal/100-fee and normal-save reload checks remain separate evidence.
  This recording does not prove campaign difficulty, egg handling or a full deposit cycle.
- IMPORTANT correction: 0x4154/0x4155 overlap dynamically allocated bedroom PC slots
  (0x4152..0x4165). Gate development v1, v2 AND v3 are unsuitable for validation/release.
  The earlier claim that 0x4154 was unused was wrong. Current gate source uses only flag
  0xA9D, with literal-zero coordinate triggers; four compiled checks pass, native pending.
  No gate code is included in the delivered 0026 ROM. Test transport uses 0x4000 only
  in private fixtures. Do not modify Johto or owner originals to test the gate work.
- Live server restored on existing tunnel, session 86280, video/audio feed OFF while editing.
  Top screen left, bottom right. Access unchanged. Owner posted the control-bearing link
  publicly; auto-review rejected viewer/control permission split and credential rotation.
  Specific approval question is pending; do not bypass rejection or treat emoji as approval.
- Next checkpoint 0027: native Saffron guard tests and true Yellow Route 5 geometry,
  followed by requested repeated area banners and phase-aware Blue rival title.
  Preserve the owner's entire Oak intro/naming screens exactly as supplied 0025.

October 12, 2026 — 0027 guard development and terrain reference:
- Candidate build/0027-gates-development-v1.nds SHA a848bd038f2aea75ea10bae692d24679da42f5f4cd1c54ef1ed442e340b6abe5. NOT a release; supplied 0026 is unchanged.
- Native north guard: no-drink dialogue and forced return to route-side y=5 observed.
  Fresh Water fixture starts with exactly 2, consumes 1, sets flag 0xA9D, no further
  drink consumed on repeat crossings. Saved normally, fresh Continue on candidate
  WITHOUT test transport retains open flag, one Fresh Water and original PC slot bytes.
- Saved open flag tested with private transports at all other Kanto gates 389/493/390.
  Player traversed beyond each trigger; Route 6 test reached Saffron map59.
  Drinks stay at one Fresh Water. Bedroom PC slots match byte-for-byte across all runs.
- Four compiled gate checks pass, now assert trigger condition literal (0,0).
  Native Soda/Lemon acceptance and closed refusal at other three approaches still pending.
  Evidence: validation-prototype-0027-development.json; raw RAM/screens stay ignored.
- The earlier fixture seemed stuck because its copied owner bag contained 995 of EACH
  drink and the removal loop had not finished, not an opcode fault. Replaced with
  explicit --clear-drinks 995 bulk fixture preparation and native post-checks. No
  live owner save/inventory changed. Private transports now refuse non-Kanto source maps.
- New read-only source tool tools/yellow_walk_topology.py derives real Yellow walking
  topology from bottom-left quadrant collision tiles, passable table and ledge rules.
  Route5 private reference: build/0027-route5-walking-reference-v1/topology.json and
  walking-grid.png. 20x36 tiles, 490 passable tiles, 449 reachable from north, 40 directed
  ledge edges; four north-side warp tiles reachable. South gate exit tile (10,33) is
  correctly disconnected before using the gate. This is NOT yet DS collision/geometry.
- Next: inspect/generated HG-style terrain models and choose a Kanto-only two-cell
  layout strategy; original Route5 matrix cell is 32x32, insufficient for Yellow 20x36.
  Avoid resizing Yellow down to fit or modifying Johto cells. All intro/naming stays locked.
- No public push or new artifact publication during this heartbeat. Prototype0026 local
  download and audio recording remain available. Stream remains existing credential,
  paused feed while editing; specific viewer/control-split approval remains pending.

Latest working checkpoint plan: yellow-heartgold/PROTOTYPE-0027-PLAN.md.

October 12 — owner requested phone patch page and explicitly approved stream split:
- Published 0026 patch page/manifest/license through GitHub connector, commits cc28983,
  42948c3 and a525667. Public URL:
  https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0026/index.html
  HTTPS fetch matched the verified local page EXACTLY, including embedded patch.
  Explicit owner publication request supersedes earlier pending-publication/no-push
  scope for THESE artifacts and accompanying notes only; do not push dirty source.
- Published the native 40-second audio recording page, commit e1f1ea4:
  https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/prototype-0026.html
  Exact remote/local page match verified. Browser page embeds the MP4 for playback.
  Public log/latest patch link updated in 615a4a3; playtest index links the new clip.
  No ROM/save or new private control token published.
- Owner specifically answered YES to public viewing/private controls. Approved split
  implemented in cloud_test_suite.py: original live-token is now viewing only;
  newly generated live-control-token is chmod600 in ignored owner-save backup folder.
  Use LIVE_TEST_TOKEN from live-control-token and LIVE_TEST_VIEW_TOKEN from live-token.
  Do NOT use the old live-token for agent control commands anymore. No rotation of
  viewing URL needed. Do not expose the private control credential in logs/GitHub.
- Ten bridge tests pass. ACTUAL public tunnel: viewing/status/audio allowed with original
  token; public and anonymous POST controls403; private POST controls200. Viewer UI
  hides game/touch/video controls. Same tunnel process/URL; stream runner session26023,
  source0026 foundation SHA equals released0026, same copied prepared save folder.
  Feed OFF/activity Editing Route5. Original campaign and Johto remain unchanged.
- Previous credential-split auto-review blocker is RESOLVED by explicit owner approval.
  Windows-local ROM link is unsuitable for phone delivery; use verified patch URL above.

October 12 later heartbeat — native guard checks completed; first terrain probe:
- Five additional native cases passed on copied prepared saves: Soda Pop and Lemonade
  each consume exactly one of two; no-drink refusal at gates389/493/390 returns player
  to route side. Original save SHA and bedroom PC slot bytes checked unchanged.
  Results ignored: build/0027-native-validation-v2/results.json.
  Combined with earlier north refusal, Fresh Water, normal-save reload and shared
  passage checks, all guard acceptance/refusal branches now have native coverage.
- Updated validation-prototype-0027-development.json and latest 0027 plan. No public push.
- Created private Route5 two-cell matrix296 with appended land691/692, using the native
  Day Care land212 flat 66-byte BDHC template. Matrix0 and all original archive members
  preserved; only Kanto map13 header and new resources change, plus private map29 transport.
- Probe v1: build/0027-route5-terrain-probe-v1; diagnostic color geometry and translated
  walking permissions; native load map13,x16,z1,height0 verified. Not final HG visuals.
- Probe v2: build/0027-route5-terrain-probe-v2; 40 one-way ledge cells encoded0x803B,
  matching original native land encodings. Loaded successfully. At row2, normal held
  DOWN moves to row4 via native hop; UP leaves row4 unchanged. One-frame hop assertion
  initially failed due inadequate input duration; held-input results verified.
  Evidence: native/held-input-ledge-results.json and screenshots. Native isolated
  snapshot GetMetatileBehavior queried0x3B at(16,3); GetLedgeDirection returned1.
- Colored model writer adapted from tools/title_models.py, scale128 and corrected
  full-cell bbox. Temporary colors/no doors/no grass behavior/no region connections.
  Do not release this probe. Need HG textures/props, native grass, doors/interior
  returns, north/south connection integration, lower-cell tests and save migration.
- Separate Route5 matrix avoids modifying shared matrix0/Johto, but entering from
  original seamless world requires explicit Kanto transition integration. Inspect
  matrix/main-map assumptions, Fly/follower behavior and safe saved coordinates before
  choosing production architecture. Do not shrink Yellow36rows to HG32rows.
- Prototype0026 remains latest published playable checkpoint. Owner original saves,
  Johto and locked Oak intro/naming unchanged. Live feed stays paused during editing;
  approved view-only URL and private control split remain operational.

October 12 11:50 EDT — lower cell, grass, compiler and actual LIVE terrain test:
- New private terrain probe v3: build/0027-route5-terrain-probe-v3. Source grass tile
  $52 verified from read-only Yellow data/tilesets/tileset_headers.asm, then translated
  to native behavior2 at all48 grass cells. Real grass walking triggered PidgeottoLv17,
  matching Yellow Route5's encounter table; screenshot in route5-terrain-grass/grass-walking.png.
  Prepared owner UmbreonLv100 is NOT normal-campaign difficulty evidence.
- Private lower-cell transport loaded map13,x16,z34,height0. Native walk reaches row35;
  attempt to enter blocked padding row36 leaves row35 unchanged. Normal in-game Save,
  fresh Continue on NON-TRANSPORT probe ROM retains map13,x16,z35,height0, party3,
  parcel2, NationalDex. Normal save and screenshots in probe-v3/normal-continue.
  This validates same-layout persistence, NOT migration from existing HG world coordinates.
- Reusable tools/route5_terrain.py now preserves the proven private compiler. Requires
  explicit diagnostic=True and a complete unique20x36 source grid. Four meaningful
  tests in tests/test_route5_terrain.py pass: exact native-tested ROM reproduction,
  only Kanto13 header/compression metadata change, every original archive member and
  matrix0 retained, original executable overlays/ITCM/ARM7 unchanged,48 grass/40 ledges,
  native permissions at known points and all padded tiles blocked. Final art/doors/
  neighboring region integration remain absent; do NOT release this diagnostic terrain.
- Actual LIVE run completed through the same Cloudflare URL, with viewing/audio only
  for public link. Live runner session69429 now uses private grass fixture, NEW copied
  save folder build/0027-live-terrain-v3. Label explicitly says diagnostic colors/not
  released. Buttons were separated after a bootstrap nullable-RAM/rapid-press issue.
  Gameplay feed ON for actual walking, native audio enabled, captured AbraLv7 encounter
  in live-test-frame.jpg; then video/audio OFF via control finally block while editing.
  Session remains running in private battle; no title-loop feed. Activity states finished
  playtest/editing. Source private fixture is NOT published playable prototype0026.
  Do not run another emulator against this live save folder while it is locked.
- Existing private control credential remains live-control-token; view token live-token.
  No URL/credential changes and no public push. Prototype0026 remains latest public patch.
- Next: native HG texture/prop discovery, correct DayCare/Underground/Gate models and
  paired door warps, source north/south links and saved-world-coordinate migration.
  Assess standalone matrix assumptions (Fly/Teleport and seamless transitions) before
  production choice. Preserve Johto and exact supplied Oak intro/naming throughout.

October 12 noon Eastern: first daily Discord status baseline confirmed sent (message 1559234251973726269), including the GitHub plain-language DEVELOPMENT-LOG link. Local posting ledger records this date; temporary draft removed. No game source/artifact publication performed.

October 12 afternoon — Route5 private door plumbing and native asset identification:
- New tools/route5_doors.py requires explicit diagnostic=True and existing1x2 terrain.
  Exterior warp anchors at Yellow's coordinates plus6x: (16,29),(15,29) north gate,
  (16,33) south gate, (23,27) Underground house469, (16,21) DayCare517. Gate391 returns
  to Route5 on BOTH ends now; south no longer jumps straight to HG Saffron. Connections
  beyond Route5 remain absent. Original interior actors/scripts/text/other exits preserved.
- Every original input NARC member preserved by cloning lands693/694 and matrix297;
  appended exterior/interior event banks only. Only Kanto headers13/391/469/517 change
  plus verified ARM9 compression metadata. Johto/matrix0/original executable overlays
  and ITCM untouched. Five meaningful tests in tests/test_route5_doors.py pass.
  Test compiler reproduces the exact native-tested door probe. NOT a released build.
- Native round trips on build/0027-route5-door-probe-v1 verified: DayCare→517→13(16,21),
  Underground→469→13(23,28), north gate→391→13(16,29), south gate→391→13(16,34),
  second north doorway→391→13(16,29). Party3/parcel2/Dex state retained in all metrics.
  North6F entrance needs continuous movement; initial8-frame step stopped on portal,
  so it was NOT counted as entry. Held24-frame input entered391; assertion helper now
  requires the intended interior before any success claim. Initial failed snapshot kept.
- A-button sign at(23,29) observed UNDERGROUND PATH text natively. Sign's graphical prop
  is not yet placed. Door props absent in diagnostic color terrain, yet native house
  0x8069 and north/south6F/6E warp behaviors work. Gate interior still original HG13x13
  corridor; Yellow small/two-portal interior geometry still pending. No final-art claim.
- Native Route5 asset discovery: a/0/4/0 has340 building/prop BMDs; a/0/4/2 area descriptor
  bank13 is8bytes 0c000d0000000101 (links model-list12 and texture-set13; other fields
  need source validation before editing). a/0/4/3 is prop model lists; a/0/4/4 is106
  texture sets. Original Route5 model map40_05c uses24 texture bindings, fully matched
  in sets7/13/18. Default Route5 points to area bank13; texture-set13 is the likely native
  exact source. Private index: build/0027-native-terrain-assets-v1/index.json, props.json.
- Native land153 props: model276 ha_h01a house,286 ha_dr01 door,31 board_c sign,290
  kn_chika Underground building.48bytes/prop:12 signed words (modelID,x,y,z,3rotation,
  3scale,2other). FX32 scale4096=1.0, position units16 per tile. Bounding widths/depths:
  house276 about4.122×3.25tiles; UG290 about4.25×2.875; NSgate246 kn_gate_a6.25×7.755;
  other gate247 kn_gate_b7.5×6. Models listed in list12 already loaded by area13.
  Source Yellow DayCare door right of building center; native276 door left of center.
  Evaluate native mirrored/scaled placement or model277 variant before final alignment;
  don't simply shift a door marker independently of the visible house opening.
- Next: native HG materials/texture binding or prop placement in new clone-only lands,
  precise building footprint/door alignment, Yellow gate interior, north/south links and
  legacy saved-coordinate migration. Keep final diagnostic=True safeguards until all
  release prerequisites tested. Prototype0026 remains latest public patch; no public push.
- Live stream remains previous private grass fixture, paused after actual prior test,
  with same approved view-only URL/private control credential. Do not run another core
  against build/0027-live-terrain-v3 while its session69429 owns that save folder.

October 12 afternoon — native materials and first visible Route5 props:
- tools/route5_materials.py clones two lands and one matrix, reusing the complete original
  Route5 material section and external texture bindings. Native grass01gs/egrass/cliff01gs
  render on the private two-cell map. Base floor is a single repeated-texture quad;
  grass/ledge overlays retain all source permissions. Flat cliff strips are diagnostic,
  not final visible ledge geometry. Four focused binding/preservation tests pass.
- Private build/0027-route5-native-materials-v1: lands695/696,matrix298; native screenshot
  native-material-grass/native-materials.png and map13(16,12) metrics. Original resources,
  executable overlays/ITCM/ARM7, doors, heights and Johto unchanged.
- tools/route5_props.py translates native land153 prop offsets: UG290 warp26,25 versus
  pivot27,24.5 becomes door23,27/pivot24,26.5; sign31 event28,26 versus pivot28.5,26.5
  becomes event23,29/pivot23.5,29.5. Native scale/rotation retained, flat terrain height0.
  New lands697/698,matrix299, no existing member replaced. Four prop checks pass.
- Private build/0027-route5-native-props-v1: native-props.png/native-sign.png show the
  building/sign and UNDERGROUND PATH text. native-building-roundtrip validates469entry,
  return13(23,28),party3/parcel2/Dex unchanged. Full Route5 suite23 checks pass.
- Actual LIVE test switched oldrunner69429 to newrunner52932; no tunnel restart or URL
  change. New separate save folder build/0027-live-native-props-v1. Private label states
  copied prepared save/unfinished scenery/not released. Native audiovisual feed ON for
  building entry/return, then OFF in finally; server continues paused during editing.
  First return check saw map13 before avatar settled and failed; status later confirmed
  23,28. Updated helper requires both expected map AND position; repeated live round trip
  passes. Evidence live-door-roundtrip.json/live-native-building.jpg. Failure snapshot
  retained as after-failed-coordinate-check.json; don't report the first run as success.
- No release/public push.0026 remains latest public playable patch. Owner saves and
  Project Recovery untouched. New tools require diagnostic=True; preserve these safeguards.
- Next: DayCare native variant/door alignment (Yellow door right of center, native276
  left), NSgate prop calibration and Yellow smaller gate interior, trees/source visible
  ledge geometry, north/south city connections, saved-coordinate migration/Fly/followers.
  Separate guard candidate still must be merged only after layout integration proven.

October12 afternoon — mirrored DayCare/gate scenery and native companion resources:
- route5_props.patch_probe_props now offers scenery=True (defaultFalse remains exact
  previous probe). Native276 house/286door mirrored at scales(-1,1,1.25); door leaf
  center16.5,21.5 matches warp tile16,21. Gate246 mirrored/scaled(-1.28,1,.5), native
  approach offsets map to rows29/33. Source originals untouched. New alignment check.
- Negative scale alone produced missing faces in private scenery-v1. New
  tools/route5_mirror_materials.py clones material culling to both faces, models
  276→340,286→341,246→342. Native loader dependencies discovered read-only from pret
  asm/overlay_01_021FB878.s and overlay_01_021EA6C4.s: metadata a/1/0/7 indexed by
  modelID; global bm_field_matshp.dat has u16modelCount/u16shapeCount,4bytes per
  model lookup then4bytes per shape. Extend count340→343 with copied three records;
  all original lookup records and shape payload unchanged. Capacity native0x226.
- Area13 descriptor's FIRST u16 selects BOTH prop list a/0/4/3 AND prop textures
  a/0/7/0; SECOND u16 selects terrain textures a/0/4/4. Clone list12/proptex12 to104,
  descriptor13→106 preserving other six bytes; only Kanto13 header area/matrix updated.
  Models/metadata/list/texture/area/land/matrix archive prefixes unchanged. Original
  executable overlays/ITCM/ARM7 and all Johto headers/files stay intact.
- Intermediate scenery-v2 lacked metadata and loaded black;v3 lacked shape lookup
  (black/serialization failure);v4 lacked aligned proptex (bad colors), though door
  entry passed. ONLY scenery-v5 passes full visual validation plus DayCare517entry,
  return13(16,22) and bothgate391entries. Do not count failed probes as successful.
  All remain ignored/private. Scenery-v5 uses lands699/700,matrix300,area106.
- Native v5 gate pictures show restored textured gate from north/south. Trees, flat
  diagnostic cliff strips, source-small gate interior, cloned door animation and city
  links/save migration remain unfinished; no final graphics claim.
- Full crossing first stopped on thirsty guard at391(5,7). Audit corrected earlier
  assumption: terraincompiler starts0027-gates-development-v1, so shared-drink guards
  already existed throughout terrain chain. Not a legacy guard replacement. New
  integrated probe re-applies verifiedguard patch after door returns, preserving both
  returns toRoute5. Native preparedwater2→1/openflagtrue/southpass and repeatednorth
  pass retain1water and allbedroomPCslots. Emptybag refusal returns391y5,flagfalse.
  Repeat heldinput expired during field transition; second input completes crossing.
  Evidence build/0027-integrated-route5-guards-v1/native-integration.json and screenshots.
- All33 focused Route5 checks pass (including six mirror dependency/preservation and
  three guard/scenery integration checks). tools/build_prototype0027_private.py now
  reproduces integratedprivate ROM from checked gate baseline with exactterrain,
  doors/materials/props/clonedresources/reappliedguards. Requires --diagnostic, ignored
  build destination, refuses existing ROM/report. Output98e49ed93e9f1dce11596b1dfb26fa8250692d6ea18ba0e10c9ee7db461431b9.
- Native24-second stereo recording: build/0027-scenery-recording-v1/daycare-scenery-audio.mp4,
  labelPRIVATE0027/preparedsave; maps13/517 observed. NativePCM44100Hz nonzero,
  duration23.986187video/23.999002audio,pitchpreserved,tempo1.0040378. No public upload.
- Actual LIVE DayCare test succeeded, sameCloudflare viewingURL/privatecontrols.
  Oldrunner52932 stopped; newrunner29241, separatecopiedsavefolder
  build/0027-live-native-scenery-v5, explicitprivateartprobe label. Feedvideo/audioON
  onlyactualgameplay, OFF afterward. Evidence live-daycare-roundtrip.json and
  live-native-building.jpg. Never run another core against its locked save directory.
- Owner saves/ProjectRecovery notmodified; no release/publicpush,0026 latestpublic.
  Next prioritize production matrix integration/north-south cities/saved-world-coordinate
  migration; remainingtrees/ledges/source-smallgateinterior/dooranimation/Fly/follower
  checks. Blue/Giovanni/HOFswitch and repeat-area banners remain future requirements.

October12 evening heartbeat — private Route5 city links:
- Read handoff/plainlog/latestplan first. Implemented tools/route5_connections.py,
  diagnostic=True only. Appends script/event banks only to Kanto13/52/59. Existing
  story scripts/actors/warps/coords retained; script_bank adds alignment padding only
  (test compares instructions after trailing zero padding). No persistent vars used.
  Original archives prefix intact; main matrix0/lands/props/code/Johto unchanged.
- Interim HG city links:52left(1291..1293,157)→13(9,1);52right(1306..1308,157)→13(24,1);
  59(1300..1301,199)→13(16,34).13north row0 x6..20→52(1292,156),x21..25→52(1307,156);
  13southrow35 x6..25→59(1300,200). Arrival rows differ from triggers, avoiding bounce.
  Central/outer north exits map to native city roads provisionally. This does NOT
  establish final Yellow city layout or production seamless integration. Defer final
  city layout choices to source-derived reconstruction; do not call this final design.
- Failed city-links-v1:1296,158 was native raised tree terrain (height6), avatar hidden,
  short/held inputs both blocked. Never count v1 success. Corrected v2 uses visible
  roads1292/1307,row156; native screenshots show avatar on road, tested triggers157.
- All six native directions pass:13(9,1)/13(24,1)/13(16,34); return52(1292,156),
  52(1307,156),59(1300,200). Party3/parcel2/Dex retained. Same-core repeated roundtrips
  at all three approaches preserve PC slots, drinks and shared guard state. Evidence
  build/0027-route5-city-links-v2/native-city-links.json (five cases plus separate left
  entry-metrics), native-repeated-links.json (three roundtrips), screenshots/metrics.
- Three focused tests in tests/test_route5_connections.py pass. Full Route5 suite36
  checks pass. Native v2 SHA f9e1879eb67ebd04edc820989f21e336b40aeb3e67bd2192d8cb79f485bfb6b5.
  tools/build_prototype0027_private.py --diagnostic --city-links reproduces exactly in
  build/0027-reproducible-city-links-v1. Default no-city-links builder preserved.
- Previous live runner/tunnel no longer running at heartbeat start (localhost refused,
  ps no cloudflared). start_0027_live_city_links.py now only tolerates a proven
  ConnectionRefusedError; auth errors still fail. New runner69278, separate copied-save
  build/0027-live-city-links-v2. Actual live native city roundtrip passes (local first,
  remote after tunnel recovery); feed/audio OFF afterward. Lock this save folder.
- Authorized Cloudflare recovery via detached subprocess, PID1316, logs and origin in
  build/0027-tunnel-recovery-v1. New origin https://remedies-regression-lawyer-ins.trycloudflare.com.
  View token unchangedlive-token; control unchangedlive-control-token PRIVATE. Remote
  test JPEG11787bytes/PCM44100nonzero, can_controlFalse and POSTviewer403 verified at
  live-city-links-v2/public-view-verification.json. Don't print/publish control token.
  Same fragment viewing token as local log. Old GitHub viewing link is now expired;
  local DEVELOPMENT-LOG updated only. Heartbeat says neverpublicpush, so no GitHub edit.
- Originals, owner saves and Project Recovery untouched. New ROMs/saves/tests private
  and ignored; no release/publicpush, latestpublished0026. Keep setup/publication scope
  distinct. Release blockers: old-world-coordinate saves on map13 before matrix loading,
  final Yellow city geometry/main matrix architecture, trees/ledges/smallgateinterior/
  cloneddooranimation/Fly/followers/camera. Next inspect saved-location initialization
  before map load for narrowly scoped Kanto13 migration; do not alter Johto or originals.

October12 — explicit owner stream restoration/log publication request:
- Owner now explicitly requested reestablishing testing stream and updating the
  GitHub plain-language log link. This authorizes the narrow link/documentation write
  despite the earlier heartbeat's no-public-push constraint; no broader publication.
- Existing local runner69278 and CloudflarePID1316 were healthy. Actual native city
  roundtrip re-run, remote video/audio verified and viewer controls403 confirmed.
  Existing origin remedies-regression-lawyer-ins.trycloudflare.com unchanged; viewing
  token unchanged, private control token never exposed. Feed paused after playtest,
  per owner preference of showing gameplay only while actually testing.
- GitHub DEVELOPMENT-LOG stream block updated via contents API, commit
  8f0cfd8633ad57b35c2bd2fc2cfff7131ce924d4, blob3eb8658df68add2ef54b532414f23c84921e230d.
  Re-fetch exactly matched prepared content. Added Enable sound, screen orientation,
  view-only/pause and temporary availability instructions. All other published content
  preserved. No ROM/source/private notes/saves/control credential published.
- Local log stream block synchronized; earlier stale-link/no-push paragraphs are
  historical. Public log now has current stream link. All previous release status
  remains unchanged:0026 latest playable patch;0027 private and unfinished.

Standing live-stream rule — owner clarification:
Keep the audiovisual server and remote viewing tunnel running and connected between
playtests. Hide/pause video and audio while editing or otherwise not actually
playtesting; enable both for real gameplay tests. A paused display does not authorize
stopping the server/tunnel. Keep existing viewing URL when the tunnel is healthy.
Recover failed services when possible, and update the viewing link when it changes
under the owner's explicit link-maintenance authorization. Never expose controls.

October12 owner clarification — COMPACT CONNECTED OVERWORLD is now active:
- Owner explicitly permits shortening areas to fit HG's connected overworld, including
  future similar cases without another question PROVIDED Yellow's vision/gameplay is
  preserved. Outdoor travel should be seamless with no loading-screen transitions;
  indoor/outdoor and building/cave floor transitions remain allowed. This supersedes
  old strict36-row separate-matrix architecture and temporary city-fade probes.
- tools/route5_compact_layout.py removes source spacing rows2/14/16/34. Earlier idea
  to remove15 was rejected because it contains ledges; nofeature-loss implementation
  occurred. Final20x32 reference retains48grass,40ledges,allfivewarps/sign and every
  building row. Source cellar counts424walkable/401north-reachable; southGateDoor still
  unreachable fromnorth withoutgatecrossing. Four protection tests pass. Reference
  build/0027-route5-compact-reference-v1/topology.json. Source36-rowreference immutable.
- New active tools/route5_connected.py starts0027-gates-development-v1. Keeps main
  matrix0,worldorigin1280/160, xoffset10 (matchesHGside roads/Saffroncenter). Only
  cells(40,5)Route5/(40,6)Saffron land IDs change. Original terrains/Johtocells remain
  stored/unchanged; new lands692/694. BGsign1307,186,height2. Doors1300,186;1299,186;
  1300,190;1307,184;1300,178. Gate391 returns both ends toRoute5 anchors2/0.
- Route5flatcollider cloned fromnativeSaffron133:66bytes,planeconstant-131072 gives
  worldY32/avatarheight4. Renderer root translation32 (textured_model ground_y optional,
  default0 preserves olderexactROMs); tilepermissions preserve native0x400level bits,
  lowgrass2/ledge3B/doorbehaviors. OriginalBDHC133 untouched. Saffronclone removes
  onlyobsoletegate246prop(pivotX327680),opens x20/21 rows0..7 with0x400normalfloor.
  OldSaffronwarp4/5 records preserved butnormalfloor disables their oldgate behavior.
- KantoArea13/propList12 users exactlymaps12/13/17/18/28/29/52, allKanto. Preserve bank13
  for nativeoutdoor area sharing; originallist12's23IDs retained plus340..342clones.
  This keeps native neighboringcity props available. Matrix0/list12 intentionally
  change Kanto-only tables; allother originalarchive members and oldshape records/
  payload remain intact. No Johto headers,code,overlays,ITCM orintro/naming changes.
- Native5outdoor crossings pass:bothCeruleanroads→13world1292/1307,z166;13north→52z157;
  Saffron59world1301,193→13z191;13world1301,191→59z194. Screen samples EVERY4frames
  showed no blackscreen; do not overclaim sampling as per-frame exhaustive verification.
  Evidence build/0027-connected-route5-v1/native-connected-boundaries.json andimages.
- NativeDayCare517,UG469,bothGate391 entrances/returns pass. Returns13world1300,179;
  1307,185;1300,186;1300,191,height4. Gateinterior standardfade remainsallowed. All
  party3/parcel2/Dex preserved. Sign/grasswalking oncompactgeometry stillneeds nativecheck.
- Save compatibility research located earlyFieldSystem_Init overlay124 call0x02260C6E
  toSaveLocalFieldGet0x0203B9C4,identitygetter0x0203B958 at0x02260C72. Localfield save
  index5,savedobjects10. Savedplayer/follower mapID is1,notregion13; IDs255/253.
  ITCM32024bytes/744free. NO MIGRATION HOOK INSTALLED; compactmain-world approach
  avoids out-of-rangeglobalcoords. Normal old0026Route5save at1292,172,h4 created via
  nativeSave oncopy (build/0027-legacy-route5-save-v1). Continue on PUREconnectedROM
  retains sameposition and EXACT blocks2/3/4/6/7/10 (party/bag/varsflags/Dex/DayCare/
  savedactors),zero diffs. Evidence legacy-continue/preserved-save-blocks.json. This
  coversoneoldroadlocation; otheroldpositions/heights/blockedtiles stillneedchecks.
- FullRoute5suite45checks passed; then addedoriginalresource-preservation check,
  connected subset6passes:46focusedcheckscurrently passing. Newactive reproducible
  builder tools/build_prototype0027_connected_private.py --diagnostic --output build/...
  exactSHA f2ae7cd2fecfd8316334d1431598d60d8f729c1c03646f4c93cacb8d17540cc0.
  Original standalone/city-fade builders andprobes historical; don'tcontinue them.
- Localnative24sec recording build/0027-connected-recording-v1/connected-boundary-audio.mp4,
  actualmaps13/52/44100Hzstereo nonzeroPCM;video23.986187/audio23.995011 sec,
  pitchpreserved tempo1.0038345668. Notpublished/notrelease/difficultyproof.
- ActualLIVEconnectedroundtrip passes withremote JPEG/audio/viewer403checks. Tunnel
  PID1316/URLremedies-regression-lawyer-ins unchanged. Backend brieflyrestarted ONLY
  toloadnewtestROM; currentrunner77973,savefolderbuild/0027-live-connected-route5-v1.
  Feed/audiopaused afteractualplaytest; server/tunnelstayrunningbetweenwork. Do not
  run anothercoreagainst its lockedsavefolder. Privatecontrol token unchanged/secret.
- Updatedlocalplan top makescompactconnectedarchitecture authoritative. Originals/
  ProjectRecovery/ownersaves untouched;generatedROMs/saves/mediaignored. No publicpush,
  latestrelease0026. Nextfinalnativeprops trees/fences/visibleledges,smallYellowgateinterior,
  cloneddooranimation,sign/grassnativecheck,morelegacypositions/Fly/followers/camera,
  cumulativepatch/releaseAV. Blue/Giovanni/HOFswitch andevery-area banners remainpending.

## October 12 — compact Route 5 interaction checks

The Underground Path sign opens with A on the connected map. The player can walk
from (1296,163) to (1297,163) through tall grass at height 4. A native eight-frame
Down press hops the ledge from (1296,161) to (1296,163); Up cannot climb back.
Party count, parcel progression and National Dex status remain unchanged. A
one-frame input missed the hop; the longer native input confirms the behavior.
These fixtures use copied saves and a clearly labeled private test transport.

All 46 focused Route 5 tests passed together. Evidence is local and ignored under
build/0027-connected-interactions-v1, including sign/grass screenshots, RAM metrics
and compact-ledge/one-way.json. This checks one grass step and one ledge; it does
not prove encounter frequency or every ledge. No new prototype has been released.

The existing live server and tunnel remain connected. Actual road approach and
movement were displayed, then video/audio paused. The western path's tree barrier
prevented that approach from reaching grass; do not label that live segment as a
successful grass encounter test. The isolated native fixture supplies the grass
walking evidence. Live emulator is now map13 at (1294,167), height4, feed paused.

Native Route5 original terrain shape/material mapping and mesh bounds inspected
locally: tree01 material26/shape0, tree01_re27/shape1, tree01_un28/shape9;
cliff01 material10/shape4. Original tree canopy mesh uses slanted textured quads,
not a generic vertical wall. Geometry report build/0027-native-geometry-analysis-v1.
Standalone texture preview still needs correct shared native palette extent;
failed decoder attempts are not successful art validation. No geometry installed.
Next: finish native trees/fences/visible ledges and cloned door animations, check
compact gate progression and more legacy save positions, then release testing.
Johto, originals, Oak intro/naming and released0026 remain untouched. No public push.

## October 12/13 — native trees and visible ledges checkpoint

Optional native tree and ledge geometry implemented in route5_materials.py and
route5_connected.py. Default options retain the previous exact connected ROM;
active safeguarded builder now supports --native-trees --visible-ledges with
--diagnostic and a new ignored output path. All49 source tree cells (collision0x50)
use original tree01gs material26, one half of its64x64 texture, slanted canopy
quad scaled to one Yellow walking tile. No new texture or palette archive installed.
The native standalone decoder failed because of aliased palette offsets and its
packed-color interface; fixed private preview reads the original offset plus32bytes
and supplies packed16bit colors. Original ROM remains untouched.

New40 visible ledges use allpeakgs material8 and low8-world-unit slanted quads,
leaving the ground collider/one-way permissions unchanged. V1 UV16..32 repeated
corner transparency and left gaps; V2 UV8..24 uses the center strip, joining rows.
V1 retained as history. Current private terrain V2:
build/0027-native-trees-ledges-v2/private-terrain.nds
SHA056b55fc21edfc22dc6f1ae73bb9cfeb0a8db33d171d70b90ca3323e0ab972e2.
Tree-only V1 SHAba3510381b3ab6690036a7812150dc43a444ddcde167802eb0404046d7c39107,
reproduced by the safeguarded builder. Earlier default connected SHA unchanged.

All52 focused Route5 tests pass together, including6 new tree/ledge checks proving
allnon-land resources/code identical, original permission/prop/BDHC payloads identical,
49tree render positions, fourmodel meshes, and exact private probe reproduction.
Native V2 approach1296,161,height4 ->Down8 hop1296,163 ->Up8 stays163; party3,
parcel2 andNationalDex retained. Source tree-only native/live grass walk1296<->1297,
163 passed with nativeaudio. V2 screenshots visually inspected; rows join properly.
Evidence: build/0027-native-trees-ledges-v2/visible-ledges/native-ledges.json andPNG.

LIVE backend69540 now owns build/0027-live-native-terrain-v2 copiedsave directory.
Old tree backend14958 was stopped solely toload thisnewROM; tunnelPID1316 remains,
URLremedies-regression-lawyer-ins unchanged. FirstliveDown input missed while
transportfinished; corrected-ledge-check/native-walking.json proves actual161->163
hop andnorthrefusal at163. Currentliveposition1296,163,height4/map13, feedpaused,
server/tunnelrunning. Never run anothercoreagainst this lockedlive savefolder.

New24sec native recording withreal44100Hzstereo/nonzeroPCM/noRAMwrites:
build/0027-native-terrain-recording-v2/native-tree-grass-audio.mp4
video23.986187/audio23.995011; pitch-preserved tempo1.0037995882. ActualRAM samples
include161->162->163 southhop andlaternorthrefusal. This is labeledpreparedsave,
notcampaigndifficultyproof; nativeMP4 staysignored/local untilproperrelease package.

Owner's standing GitHub log-maintenance request used ONLY for text checkpoint:
public DEVELOPMENT-LOG.md append commitbb66aab1606bbd22bcec22bb198d3b309d207568,
blobade07a653a23b44e94defe0be8fb407d004e3b42. ExistingstreamURL preserved. NoROM,
privatecontrol,save,sourcecode ormedia publication. Previous no-public-push notes
are historical; this narrow text-log update is explicitly authorized.
0026 remainslatestrelease. Fences, northvisualseam, smallYellowgateinterior,
cloneddooranimation, widerlegacy/Fly/follower/camera/fullcompactguardchecks pending.
Johto/intro/customizations/originals untouched. Keepdefaultprobeoptionsstable;
use opt-inflags fornewterrain andnewbuildpaths. Resume fromV2 forsceneryfinishing.
Public current0027 plan additionally created understandingexplicitplan-maintenance
request: GitHubcommite5f91a13c34411ebba6ccf8ceb506a9a5f16e556. The publicplainlog
andplan were re-fetched toconfirmthe52-checkcheckpoint andremainingwork. Theseare
text-only updates; no private builds/media/source/saves/controls published.

## October 13 — integrated compact Route 5 guard checkpoint

Current pure terrain remainsV2 SHA056b55fc21edfc22dc6f1ae73bb9cfeb0a8db33d171d70b90ca3323e0ab972e2;
no production code/ROM changes thisrun. Native integrated prepared-copy tests now
cover outdoorRoute13(1300,185)->northgate391, offeringone of2FreshWaters, sharedflag
A9D true andremainingwater1, southgateexitRoute13(1300,191,height4), then seamless
Saffron59(1300,195,height4). Normal ingameSave andfreshContinue on PURE V2 ROM
(no transport/drinkgrant script) retainmap59, flagtrue, remainingwater1 andPCslots.
Pure-ROM repeat northcross returns13(1300,186,h4) withoutconsuminganotherdrink.
Firstrepeat assertion waspremature atindoorwarp391(5,12); separatefollowup movement
presses completecrossing. Do notinterpret movementclipped bywarp asgatefailure.

No-drink preparedcopy on SAMEcompactterrain enters391 then guardreturnsplayer
(5,5), flagfalse andnodrinks; sourcePCslots retained. Native party3/parcel2/
NationalDex retained throughout. Evidence build/0027-integrated-gate-v1:
integrated-native-gate.json, integrated-native-empty.json, pure-repeat-passage.json.

Raw save comparison AFTER12additionalwalkingsteps isnot byte-exact. Bagblock3 and
Dex6 exact; party2 differs128bytes, vars4 two bytes, DayCare7 onebyte. Investigated:
Pokemonchecksums/LCGdecryptvalidateall3slots; Umbreon/Gyarados unchanged; Clefairy
friendship157->158 is ONLY plaintextdifference, normal128-stepnativefriendshiptick.
VAR_FRIENDSHIP_STEPS0x404B (nativevars.h)116->0 matches12steps completing128.
DayCareegg_cyclecounter20->32 matches12walkingsteps; noDayCaremondatachanges.
Scratchvar4000 usedprivatefixture/nativeSave resets2->0 onContinue. Nounexpected
party/bag/Dex/DayCareloss. Evidence native-walking-differences-explained.json plus
normal-save-pure-repeat-blocks.json. Do NOT claimthese walkedblocks allbyteexact;
previouslegacy stationaryContinue byte-exact proof remainsindependent/unchanged.

LIVEpreparedintegratedpassage also reachedSaffron59/1300,195,h4 withnativeaudio.
Currentbackend21926 ownscopiedsave build/0027-live-integrated-gate-v1; old69540
stopped ONLYtoload testfixture. Tunnel/URL/privatecontrols unchanged. Feedpaused
afteractualplaytest; server/tunnelstayrunning. Evidence live-gate-passage.json.
Neverrunanothercoreagainstthatlockedlivefolder. Label explicitly2preparedFreshWaters.

New80sec native AV build/0027-integrated-gate-recording-v1/integrated-gate-audio.mp4
includes observedmaps13/391/59, real44100Hzstereo/nonzeroPCM/noRAMwrites, preparedcopy
labels. Video79.981814/audio79.991995,pitchpreservedtempo1.0038832536. GeneratedROMs,
saves/RAM/mediaremainignored/local; ProjectRecoveryonlyreadforstructdefinitions.
No publicpushonheartbeat.52focusedcodechecksremainlastpass; nativeintegrationadds
scenarioevidence, notnewunitcount.0026latestrelease; continuefences,northvisualseam,
smallYellowgateinterior/cloneddooranimation,broadersave/travelchecks,releasepatch/AV.

## October13 — live dashboard blank-page fix and requested viewing window

Owner requested5minutesviewing, then reportednothingdisplayed. Initialwindow backend
video/audio endpointsverifiedbutBROWSERfailed: ReferenceError cannotaccess'on'before
initialization in drawScreens. cloud_test_suite.py called drawScreens BEFORElet on=false;
scriptabortedbeforerefresh, leavingConnecting andblankcanvases. Movedoninitialization
above drawScreens. ActualIABreload nowshowsbothgamecanvases/VideoON/read-onlyHUD;
EnableSoundclick initializesMuteSound withoutnewconsoleerrors. Native remoteJPEG+
nonzero44100PCM verified;priorendpoint-only checks didnotprovebrowserstartup.
Newtest_live_testing.DashboardStartup executes ACTUALPAGE JavaScript inNodeVM and
checksstatuspoll,viewerhiddencontrols andbothcanvasdraws; wouldfailwitholdTDZorder.
All11livebridge/dashboardchecks pass. Terrain/source52checksunchangednotrerun.

Backend restarted ONLYtoloadfixedPAGE,currentrunner6482/copyfolder
build/0027-live-dashboard-fixed-v1; nativefixtureuses2preparedFreshWaters. Old21926
stopped; tunnelPID1316/URL/view-onlycredential/privatecontrols unchanged.
Originalblank-pagewindowtimer7022 cancelledafterverifiedownedcommandline.
NEWfive-minutewindow startsUTC00:19:43, ends2026-10-13T00:24:43Z, timerPID7465;
build/live-view-window-20261013-fixed-v2/window.json andtimer.log. Timer pausesonly
video/audio,doesnotstopserver. Don'tprematurelypauseitviaordinarytestfinallyblocks.
Ifresumingafterexpiry,verifytimer.log/status beforeclaimingautopauseoccurred.

DuringearlierwindowSaffron->open391->Route13 north186 worked; tryingstraightnorth
toDayCarestoppedcorrectlyat13world1300,181 dueone-wayledge180. Aroute-onlydirected
BFS fromsource10,21 toDayCareapproach10,19 foundnopathWITHINRoute5. Thismayrequire
loopingthroughCerulean; verifyactualconnectedCeruleancentralgrass/DayCareaccess
before release. Don'tclaimthisliveDayCarewalk passed orproveglobalunreachability;
isolatedDayCaredoor/nativeReturn testsremainvalid. No terraincollisionchange.

Owneraskedrefreshafterfixedbrowserproof; continuedactualguardplaytestingduring
newwindow WITHOUTfinallyforcingvideooff. NoROM/save/original/Johtochanges. No
newprototype;52terrain+11livefocusedchecks currentlypassing. Keepcheckpointnotes
accurateandcontinuefences/northseam/naturalcentralaccess/dooranimationpending.

## October13 — natural northern access alignment

Diagnosedactuallayoutfitproblem: nativeHG52 stairs connecttosourceRoute5 side roads
(2,0)/(17,0); unchangedYellowtree(5,0) andfence(14,0) blocklateralentryintoitscentral
northernapproach. Isolatedfixturesprovedcentraldoorsbutnotnaturallywalkingthere.
New opt-in north_access=True/CLI--north-access opensONLYfirstrowcells(5,0)/(14,0),
DSlocal(15,0)/(24,0), permissions0x400. Removedonevisualtreeatopenedleftgap (48rendered
vs49prior); all48grass,40ledges,5doors/sign/buildings/nativecitymaps/events intact.
ThisalignsHGstairswithYellowcentralentryunderowner'sconnected-layoutpermission;
sourceYellowreferenceimmutable. No other collision changes or outdoorfade/scripts.
Southgateexit remainsunreachablefromnorth withoutgatecrossing. Johto unchanged.

Currentprivateprobe build/0027-native-north-access-v1/private-terrain.nds SHA
 a8c91c21ef9256ecb8a6e4bfd93d30a1b4f51a4d23828b74506fab8e595c71be.
Use activebuilder --diagnostic --native-trees --visible-ledges --north-access with
NEWignoredoutput. Defaultskeepolderexactcheckpoints. Newtests/test_route5_north_access.py
3checks protecttwo-tilepermissions,southernroadblock/daycarereachability,props/BDHC/
allotherresources/code/Johto,andexactreproduction. Scopeassertion initiallymissed
retainedprivateintermediateland691; correctchangedmembers691/692/693, originalmembers
unchanged. All55focusedRoute5checks nowPASS together;11streamchecks previouspass.

Continuousnativewalking AFTERinitialpreparedcitystart provesbothnative52entrances
leadnaturallythroughthecentralgrass/one-wayledgesandaroundhouseinto517DayCare:
left1292,158->13via1292,160->23sourcegraphsteps->13world1300,179->517(4,8,h0);
right1307,158->13via1307,160->22steps->517. No intermediatewarps/testtransports/RAMwrites.
Evidence natural-daycare-left-v2/natural-access.json andnatural-daycare-right-v1/
natural-access.json undernewprobe; PNG/checkpointmetricsretainparty3/parcel2/Dex.
FirstcontinuoushelperusedrelativeemulatorsavedirectoryandfailedtofindcopiedDSV;
absolute paths fixedinNEWfolder. Do notcountthefailedbootasnativeevidence.

LIVEsamecontinuouspath completedinto517,party3/parcel2/NationalDexretained. Initial
helperassertedblockedat1297,160->161before1secondstatusrefresh, actualstepcompleted;
resumedSAMEgamepositionwith1.4swaits andcontinuedpath, noreset/transport. Evidence
build/0027-live-natural-access-v1/natural-access-live.json. Currentbackend19854 owns
thatcopied-savefolder, map517/4,8,h0; video/audio pausedafteractualtest,tunnel/URLremain.
Oldfixedbackend6482stopped ONLYtoloadnewROM. Five-minute repairedwindow'stimerlog
confirmedautomaticpausebeforethiswork. Native/Live doorsuseapprovedsharedDayCare;
no Johtofacility scripts/gameplay changed. Preserveallcurrentlockedlivefolderfiles.

Exactsuccessfulcontrolleractions capturedin natural-daycare-left-v3-recorded-actions/
native-actions.json forreproduciblenativeAVrecording; copiedsave only, optionalprivate
fixtureinitialtransportbeforeplayback. Recording build/0027-natural-access-recording-v1/
natural-daycare-audio.mp4 currentlygenerated; verifycompletion/reportbeforeclaiming
recordingpass. No newrelease. Finishfences/northvisualseam/gateinterior/dooranimation,
additionallegacy/traveltests, cumulativepristinepatch/AVpackage next.
Naturalaccess AV completion verified:49secondnativevideo/audioobservedmaps52/13/517,
44100Hzstereo/nonzeroPCM,noRAMwrites; video48.975280/audio48.989002, pitchpreserved
tempo1.0038712441. RecordingpreviouslypendingnowPASS. Keepmediaignoredlocaluntil
releasepackage. No additionalnativecodechangesafter55-checkpass.
Authorizedtext-onlypubliccheckpoint updates: plainlogcommitba4fb602a3c1589dd4adf64fe26ad12753492b4a,
plancommitb3b9dacf4f2825c589cd3db2d483cf219d5eeb32. No sourcecode/ROM/save/privatecontrol/
media published.55nativecodechecks andcompletednatural49secAV remaincurrentevidence.
Resumeactiveprivate--north-accessprobe; do notregresstonortherninaccessibility.

## October13 — native Route 5 fence scenery checkpoint

Addedoptional native_fences=True/CLI--native-fences toactiveconnectedbuilder. Scenery
usesoriginalfence_a texture/material15 at64sourceboundarycells (38code0x3Aposts+
26code0x55fencecells), respectingthetwoopenednorthgaps. No newtextures/palettes or
collision changes. Buildingwallcodes18/23 andledgecorner54 excluded. Slantednative
billboards use8/16worldwidth and11.3125rise/back. Addedfifthmesh/node; sharedNitro
writer nowassignsnode4+names withoutchangingexisting<=4nodeoutputs. Originaltitle/
introassetsneverrebuilt orchanged. Johto/cityresources/events/props/BDHC/code unchanged.

Currentprivateprobe build/0027-native-fences-v1/private-terrain.nds SHA
7dac1b0a1a6674346ac2b083f474307917bcf93232922483521d802599a8b529.
Build --diagnostic --native-trees --visible-ledges --north-access --native-fences
withnewignoredpath. Preservepriorprobes/defaults. 55existingRoute5checks pass together;
3newtests/test_route5_native_fences.py checksalsoPASS (58currentcheckscollectively,
NOTafull58-runclaim). Fencechecksverifyallnon-landresources/codeunchanged,allland
permission/prop/BDHCbytesunchanged,64fences/48trees,validfive-node/five-meshdictionary,
nativematerial15SBCbinding andexactROMreproduction.

Nativefourdoorroundtrips onfenceprobe pass:DayCare517->13(1300,179),UG469->13(1307,185),
north391->13(1300,186),south391->13(1300,191),outdoorheight4/party3/parcel2/NationalDex.
Evidence native-connected-doors.json andconnected-*PNG/metricsundernewprobe. Fence
placementvisuallyinspectedatDayCareapproach; originalsharednativepalette renders
picketsviolet/pink. CurrentnativecontinuousCerulean->centralRoute5->DayCare ALSOpasses
in natural-daycare-left-v3-diagnose. Firstgrasswalk stoppedat1297,163withblue/black
frame before164; causeunclassified, notreproduced. Do NOTclaimwildbattleprovedor
nativegraphicscrashdiagnosed. Followupwithlongerstallwaitpassedwithoutstall; separate
fence/no-grassdoorchecks pass. Broadwildbattletransitioncheckremainsbefore release.

24secondnative AVrecording build/0027-native-fence-recording-v1/connected-boundary-audio.mp4,
labelprivatepreparedsave,observedmaps13/517,44100Hzstereo/nonzeroPCM/noRAMwrites,
video23.986187/audio23.997007,pitch-preservedtempo1.0040387659. Keepignored/local.
LIVEfenceDayCareroundtrip alsoexecuted; verifyitsnative-walking.json beforeclaiming
success. Currentbackend55323 ownscopiedsavebuild/0027-live-native-fences-v1; old19854
stoppedONLYtoloadnewtestROM; tunnelPID1316/URL/viewcontrols unchanged. Feedpausesafter
actualtest; server/tunnelremainrunning. NoProjectRecoverywrites/publicpushonheartbeat.
0026stillreleased. Nextnorthvisualseam/gateinterior/cloneddooranimation,
broaderlegacy/travel/wildbattlechecks, pristinepatchandreleaseAVpackage.
LIVEfollowupV2 PASSconfirmed native-walking.json maps517then13world1300,179,h4,
real44100HznonzeroPCM. FirstV1liveUp missedduringpreparedtransport, subsequentDown
hoppedbelowledge; notarendering/doorproof. ResetONLYprivatefixturecopytoV2 andused
longerwarmup/verify-each-transition loop; actualentry/returnnowpass. Helpernewline
encodingerrorcorrectedbeforeexecution. Currentbackend38202 owns
build/0027-live-native-fences-v2;55323stoppedforprivatecopyswitch; currentmap13/1300,179,h4,
feedpaused/server+tunnelrunning. Latestprivatebuilderreport accuratelylistsenabled
options andremainingnorthseam/gateinterior/dooranimation/wildbattle/travel/releasechecks;
report-onlychange,ROMbytesunchanged. All editedsourcespy_compilePASS/diffclean.
No publicpushornewreleaseonthisheartbeat. Resumeprivatefenceprobeallfiveflags.

## October13 — natural wild battle/return and door verification

ProductionprivatefenceROMunchanged SHA7dac1b0a1a6674346ac2b083f474307917bcf93232922483521d802599a8b529.
Nativeordinarygrasswalking atRoute13world1297/1298,163 yieldednaturalAbraLv7battle.
Aftermovementstopped,1200idleframes finishedload andshowedactualbattleGUI/Umbreon
vsAbra (transition-ready.png visuallyinspected). NativeRun touchscreen95,347 onCOPY
of SAME-ROMstate succeeded: returnedRoute13world1298,163,h4 withnormalgrass/mapmenu,
party3/parcel2/NationalDex retained. Evidence build/0027-wild-transition-v1/wild-grass
progress/RAM/state andflee/returned-after-run.png +return-metrics.json. Originalstate
retained; noinputROM/save/Johto changes. Thisresolvesgeneralgrass->battle->field concern;
priorparticularblueframewasnotretrospectivelyproved, butconsistentwithnormalbattle
load/lockedfieldinput. Don'tcallitconfirmedenginecrash orallencounters/difficultyproof.
SourcepreparedownerUmbreonLv100 intentionalcopieddata, notgrant/changebytest; noEXPbattle.

ActualLIVEordinarygrasswalk ALSO producedAbraLv7 (male,independentnativeRNG), battleGUI
visuallyinspected. NativeRun touchreturnedRoute13world1297,163,h4 andmapMENU; nativeaudio
44100Hznonzero verified. Evidence build/0027-live-wild-transition-v1/natural-transition-ready.jpg,
after-run.jpg,movement.json,flee-status.json. Currentbackend72507 owns THATcopiedsave
folder; old38202 stoppedONLYtoloadnewtestfixture. Feedpausedafteractualtest; tunnelPID1316/
URL/credentials unchanged,servicesremainrunning. No publicpushonheartbeat.

ClonedDayCaredoor341 verifiedwithnativeframeobservations: itopensvisiblybyframe40 after
Up (firstframesclosed), avatarwalksinby56, permittedinteriorfadeby72. Returnendsnormally
outsidewithdoorclosed. Noanimationfixneeded; existingcopied24-byte a/1/0/7 metadata matches
original286 andnativeindexedloader usesNARC107/40, supportingappendedbuildingIDs.
Fieldnamedbm_field.narc retains340originalmodels; itisnot theNARC40staticpropbank,
andmustNOT blindlycloneintoitbasedonmatchingnames. MetadataAreaDataManager_Alloc
native021FB888 opensNARC6B/28 foroutdoorarea. MmModelconstants referNPCsprites, notthese
buildingIDs; avoidusingtheirnumberedlabels toinferhouseanimlookup.
Evidence build/0027-door-animation-observation-v1/door-animation-frames.png andreturn/
return-animation-frames.png;entryopeningvisualverified,returnclosedstateverified (not
everyclosingframecaptured). UseSAMEROMcopiesforstates; nevercrossprototype savestates.

OnlyprivatebuilderPENDINGmetadataupdatedto remove alreadyverifiedcloneddooranimation and
narrowwilditemtobroaderencounterchecks; no ROMbytes/gameplay change. py_compilePASS.
58currentRoute5checkscollectivelystilllastpass (55full+3fences),11livechecks previouspass;
no unnecessaryrerunfortest-only/read-onlywork. Currentremainingnorthvisualseam,small
Yellowgateinterior,broaderlegacy/Fly/follower/camera/encounterchecks,pristinecumulative
patchandreleaseAV.0026 stillrelease; currentfencebuilderallfiveopt-inflags active.

## October13 — northern visual seam repaired

Activeprivatecliffprobe build/0027-north-cliff-v2/private-terrain.nds SHA
1739e30e16f3aeb91844ab66699b4ba2004b210188b0d45c7bc36773c92d6a57.
BuildallpreviousflagsPLUS--north-wall. DefaultFalsepreservespriorbyte-exactprobes.
Added26verticalnativecliffquads intoexistingthirdmesh, y0..16worldrelativeground32,
localz0/northernboundary, skippingx11/12/13 and26/27/28 native stairopenings. Existing
allpeakgs material8, UVu8..24/v22..31 opaquestrip; NO newtexture/resource/collision/
prop/BDHC/code/event/city/Johtochanges. No newmesh/nodecount. Wholefloorheightunchanged.
V1UVv16..32 includedtransparentrows16..20/31 andstillleftpartofblackgap; retained
history. CorrectopaquesubstripV2fillsvisiblegap,nativePNGvisuallyinspected.

Citymainmatrixcell40,4 land143 permissionsrowsdidnotnaivelymatchpreparedglobal
stairscoordinates; donotderivephysical/permissionchangesfromthatreadwithout
validatingnativecoordinateconversion. Thisfixisstrictlyvisual; collider/data
preservedandactualstaircrossingsproved. Stairholelocationsbasedverifiedrender/
walkingpositions,notanunvalidatedchangeofCityterrain.

All61focusedRoute5checksPASStogether (113.473s). Added3northerncliffchecks decodeactual
GXdisplaylist toprove26wallquadsheight16atboundaryand6staircellsuncovered; allnative
permissions/props/BDHC/code/otherresourcesbyteexactvsfenceV1, exactprobe reproduced.
NativeFIVEstair/outdoorcrossingsPASS: bothCeruleansideentry->13, northreturn->52,
Saffronentry->13 andsouthreturn->59. Noall-blacktop-screen samplesEVERY4frames;
notper-frameexhaustiveproof. Party3/parcel2/NationalDexretained. Evidence
build/0027-north-cliff-v2/native-connected-boundaries.json andconnected-*PNG.
Preparedvisualview13/1297,161 showsnativecitycliff,notblackvoidband.

LIVEcorrectedboundaryroundtrippassedwithremoteJPEG/audio/viewerPOST403 verification.
Backend30818 ownsbuild/0027-live-north-cliff-v2; old72507stoppedONLYtoloadnewtestROM;
tunnelPID1316/URL/viewcredential/privatecontrolsunchanged. Feedpausedaftertest,
current52/1292,y<160,server/tunnelremainrunning. Never useitslockedsavefolderelsewhere.
Evidence live-city-roundtrip.json/public-view-verification.json inlivefolder.

New24secnative AV build/0027-north-cliff-recording-v2/connected-boundary-audio.mp4,
preparedsavelabel, observed13/52,44100Hzstereo/nonzeroPCM/noRAMwrites,
video23.986187/audio23.993991,pitchpreservedtempo1.0038288946. Ignored/local.
PrivatebuilderPENDINGreportnowomitnorthernseamwhenwallenabled;metadata-onlychange,
ROMbytesunchanged/py_compilePASS. No publicpushonheartbeat;0026remainsrelease.
NextsmallYellowgateinterior,broaderlegacy/Fly/follower/camera/encounterchecks,
pristinecumulativepatchandreleaseAVpackage. Currentartfeatures opt-inverified.

## October 13 04:10 UTC heartbeat — small gate reference and private geometry probe

Read current handoff/log/0027 plan first. No public push or new release.
Extended yellow_layout_reference.py to resolve the map header's actual tileset,
including digit-to-word names (Route5Gate -> ROUTE_5_GATE). Extended
 yellow_walk_topology.py to use that tileset's collision label and reject
unhandled pair-collision exceptions; ledge rules apply only to OVERWORLD.
Five source-reference tests PASS; prior Route5 layout AND topology equal their
preserved JSON references exactly. Project Recovery was read only.

Yellow gate: 8x6 walking cells, 22 passable, 16 north-reachable, four exits
(3/4,0 and 3/4,5), guard1,3 facingright. Trigger3/4,3 cuts ALL north/south
paths while closed (BFS proof); no overworld ledges. Ignored local references:
 build/0027-yellow-gate-reference-v1/{layout.json,yellow-layout.png,native-gate.json}
 build/0027-yellow-gate-topology-v1/{topology.json,walking-grid.png}.
Native391 uses matrix69/land242, groundworldY16/avatarheight2, original exits
5,2/5,12, guard1,8, triggerwhole13wide row7. Native materials gate_f1,
gate_counter,gate_w1; original model eleven materials/shapes. Originalflat
BDHC is66bytes; nativeprop114 four plants. This is NOT the floorheight4 outdoor.

New opt-in module tools/route5_gate_interior.py, diagnostic=True required,
patch_small_gate(rom,topology,two_sided=False). Separate ignored builds:
 V1 build/0027-small-gate-v1/private-small-gate.nds
 SHA93f57bb7f83ebbde30bee298b0e783fc021adbe84f558b712425065d32c7a528
 V2 build/0027-small-gate-v2/private-small-gate.nds (two_sided=True)
 SHA29e7f33553a46d192857a91ee4d6ae84bbb0b84e9b0381d913d2b4a75a09263d.
Both derive north-cliffV2 SHA1739..., NOT added to active connected builder.
Append land695/matrix298/event647, only391 header matrix/event refs change.
Native floor, billboard wall/counter probe, source permissions/guardpos,
trigger(3,3,2,1), four warps ordered south3,5/north3,0/south4,5/north4,0
with Route13 anchors2/0/2/0 (preserves outdoor anchor0/1 meaning).
Shared native drink scripts/text/state untouched. Original archive members,
other maps and Johto preserved. Five new scope/reproduction tests PASS,
including V2 only changes appended BMD vsV1. Existing61 Route5 checks lastpass;
not rerun this turn because unrelated code/resources unchanged and Route5
reference equality verified. Ten new checks passed (5 reference +5 gate).

Native V1 precise copied-fixture checks PASS, evidence native-guard-checks.json:
 no-drink trigger rejects and returns3,1, flagfalse/drinksnone;
 two Fresh Waters consume ONE, sharedflagtrue/one remaining, Down exits13;
 party3/parcel2/Dex retained, PC-slot vars unchanged.
FIRST native-empty attempt did not clear995 owner drinks and said 'Gee,thanks':
NOT no-drink evidence. Correct tests use clear_drinks=995 then assert actual
native bag before movement; gate-water grants2 only in labeled privatefixture.
V1 native-gate-empty-v2/native-gate-water-v2 contain verified.json/screens.

ART IS UNFINISHED: native floor renders, walls/counters invisible/black.
V2 doublesided native materials produced same missing surfaces; culling alone
ruled out. Native V2 compact-arrival.png visually inspected; do not release or
claim finished Yellow gate. Next inspect native gate material lighting/UV/
texture binding and original floor/wall GX commands, then correct privateprobe,
verify both exterior entrance/return pairs, guard/no-drink/repeat/Continue,
legacy interior-position handling before integration/release. Original gate
saves at native5,6 etc may lie outside new room: explicit pending migration.
No cross-ROM savestates; all fixtures independently booted copied owner save.

Existing live north-cliff backend/tunnel left connected, status verified:
video false, map52 world1292,159,height5; activity city-boundary-testfinished.
No URL/credentials changed. No new release recording or public files this turn.
0026 remains latest released patch page. Active connected builder remains
north-cliffV2, NOT these unfinished small-gate probes.

## October 13 — independent 0026 Linux/Xvfb report and reproducible test kit

Tester uses standaloneDeSmuME0.9.13-4/Linux/Xvfb, reports unreliable movement
and blackscreen; no exact failure steps or original bedroom save supplied yet.
Root cause unconfirmed; do not label resolved emulator bug or game bug.
Clean exact0026 SHA c3085440... no-save NewGame completed unchangedOak/player/
rival naming (RED/BLUE); ordinaryDown6,6->6,7,Right3 andUp4->9,3; stairs
requireRight input, thenmap503/9,3,h0. OrdinaryDown->9,4. NativeSave completed
there; freshContinue(no savestate) verifies503/9,4/h0,party0/parcel0/Dexfalse.
Evidence build/0026-opening-report-20261013-v1 screenshots/RAM/actions state;
first-floorContinue build/0026-first-floor-continue-20261013-v1/continue-verified.json.
This is a FRESH test campaign, no starter/ownerdata/no grants/transport/RAMwrites.
Original0026 ROM and all prior campaign checkpoints remain untouched.

Localtools/live_core.py field_metrics had excluded valid partycount0; accept0..6
with all pointer/capacity/Dex checksretained. TwoactualopeningRAM/invalidcount
regressiontestsPASS; all11livebridgechecksPASS. NoROMchange bythisdiagnosticfix.

Sharedkit build/Psyduck-Yellow-0026-Linux-Test-Kit.zip,20509bytes, SHA
135e61c46aa0ae41463ab25081b84b1d67a8d8fb31c3749373f250731269f20f.
ContentsREADME/run_test.py/fetch_core.py/requirements/tools.live_core/fresh
Pokemon-Psyduck-Yellow-prototype-0026.dsv/manifest/first-floorPNG. NoROM/corebinary/
rawRAM/emulatorsavestate/ownercampaign. Ignored/localonly. Corefetchusesofficial
https://buildbot.libretro.com/nightly/linux/x86_64/latest/desmume_libretro.so.zip
which was downloaded/read/hashverifiedTHISturn to match our installedcore SHA
9d6fce21af1835f5fe9f577ef8904bb491577deb21aa2f9243086b4d335084bd.
Core0.9.12 x64JIT/software/native256x192/externalBIOSdisabled; UbuntuWSL2.
Runnerdirectlibretro input requiresNO Xvfb/GUI/windowfocus, copies suppliedsave
intoNEWoutputdir, no states, preservesoriginalhash. DefaultContinue+Down8/release100
verified503/9,4->9,5,h0 inbuild/0026-linux-kit-self-test-v2; real44100HzstereoWAV.
FirstselftestV1 caughtwrongEmulator.run(frames)API;fixedperframe andV2passed.
ZIPcontainscorrecttestedrunner; privatepackagegenerator needsperframeAPI correction
before futurekit generation (currentZIPalreadycorrect).

Manualauthorized scopedGitHub plainlog update commit
73c7e116556e2cee9a509e0d130f002a1a98a279, publicplanupdated also viaContentsAPI.
NoROM/save/privatekit uploaded; no publicsource/gitpush. Existing0026 remainsrelease.
Keep testerblack-screen report open pendingcomparison/reproduction. Currentlive
northcliff backend/tunnel unchanged; no newstreamtest thisturn.

## October 13 — complete offline Linux tester bundle

User explicitly requested runner, matching core, configuration and dependencies.
New preserved ignored artifact build/Psyduck-Yellow-0026-Linux-Complete-Kit.zip,
106812048 bytes/SHA8986c5f91bdfb668678170857ea2a5ce18de67b542795bafe1c2f39c441a608b.
Old smallkit remains unchanged. Sourcefolder0026-linux-complete-kit-20261013-v1.
Includes exact core9d6fce21..., Pythonrunner/adapter, consumedconfiguration.json,
portable CPython3.12.15 officialpython-build-standalone release20261009 with
assetdigestverified, pinnedPillow11.3.0 wheels cp310/311/312/313/314, offline
setup.py/run.sh, checksums, source/license notices, separatefreshfirst-floorDSV.
NoROM, originalcampaignsave, credentials, rawRAM or cross-ROMstate included.
Corebinary buildbotreportsgit#0; included upstreamsource snapshot provenance
explicitlydoesnotclaim exactbuildcommitknown. Sourcearchive/GPL licenseincluded.

ExtractedZIPnewfolder build/0026-linux-complete-extracted-test-v1; ran sh run.sh
usingONLYbundledportablePython/wheel, NO pip/venv/network/Xvfb, verifieschecksums
andLinuxlibs. ActualtestPASS: Continue503/9,4/h0 ->Down503/9,5/h0,party0/Dexfalse;
inputDSVhashpreserved, real44100HzstereononzeroWAV/screens/runtime.json.
Evidencebuild/0026-linux-complete-offline-results-v1. BaseOSlibraries(GL/C++/C)
notredistributed; startupctypesloaderdetectsmissing andgivesDebianUbuntuinstall
instructions. Linuxx86_64/glibc>=2.27 required, ARM/muslunsupported. Existing
Pythoninstallationunmodified. 4554packagedfiles. NoROM/sourcegamechanges.
Standalone0.9.13-4/Xvfb blackscreenreport remainsunresolvedpendingcomparison.
Package is107MB: downloadonlaptopbeforeforwarding, avoidearliermobilelocalfiletimeout.

## October 13 — prototype 0027 delivered locally (current checkpoint)

Current local ROM C:/RetroArch-Win64/downloads/Pokemon-Psyduck-Yellow-prototype-0027.nds
SHA1a81de601e1dfde131136763d7f358018fee62e593fed6b949f901bd280238c2.
Separate owner save COPY C:/RetroArch-Win64/saves/DeSmuME 2015/
Pokemon-Psyduck-Yellow-prototype-0027.dsv SHAed26932f27d1bc4fa0df44a160a3fdd1dcf488450de8fdb909dfb87f0e0763d1.
No existing checkpoint overwritten. Root build/0027-release-candidate-v1 contains
matchingROM/candidate-report.json/candidate-native-checks.json/cumulative.xdelta
(actual patch filename Pokemon-Psyduck-Yellow-prototype-0027.xdelta),959179bytes.
PristineHG65f02a...encode/decode ROUNDTRIP EXACT; original unchanged. Samepatch
copied toRetroArchdownloads. Only DSfilemenu banner updated to0027; fullOakintro
and naming overlay53 comparedexact to0025. Whole remake not complete.
PUBLIC patchpage remains0026; new activegoal explicitly no publicpush. Do NOT
publish ROM/save/source/patch merely because local0027 is delivered. Publiclog
streamURL was specificallyupdated on owner's directquestion, commit4338dd37...
No subsequent publicpublication authorized/performed aftergoal update.

Implemented compactconnectedR5 finalflags alltrue, native trees/fences/visible
ledges/northerncliff. SmallYellowgate8x6/22walkingcells, guard1,3, trigger3/4,3.
Nativewall/counterblackness DIAGNOSED: generatedNORMAL commands changedvertex
colors; V3solid surfacedwhite, V4sharedmatrixdidn'tfix, V5unlit did, V6removing
NORMALalonefixed it whilepreservingnative materialattributes/texturebindings.
Canonicaluse patch_small_gate(...two_sided=True,flat_vertex_colors=True,
yellow_anchors=True), preserveolddefaults andoldprobes. V7SHA b4eb1a653961d39c2f89709a59e9e228471f83f6c61152a8386249057dc94966.
Both distinctnorthernanchors preserved: outsideleft1299->391anchor1/x3,
right1300->anchor3/x4; returnleft->Route13anchor1, right->anchor0. Southsame.
NativeALL3entry/returnpairs pass V7, no-drinkrefusal andconsumeONE pass.
Record50sec build/0027-small-gate-recording-v7 withnativePCM/localignored.

New tools/gate_save_compat.py patches391SCRIPT/INIT refs only, oldarchives and
oldguardbytecode preserved, noexec/Johtochanges. ON_RESUME3 is immediate: check
savedguardposition andplayerwalkingcell via106/105 into nativeTEMP4000/4001,
then scheduleON_FRAME1 scene whenneeded. NEVER asyncWarpinimmediateLoadscript.
Scene4 uses8004/8005 playercoords, clearsTEMP0/1, nativefade/warp same391 to3,2
(oldY<8/north) or3,4(oldY>=8/south), preserving flag/bag/progression. New room
actors reloadcorrectly. No newpersistent storyflag allocated. V8SHA43acd39239088b0cec8bec33c93303ad69f90662c76a8df48f36a3fe57bf42a0.
Evidence build/0027-gate-legacy-save-v2: normalOLD0026 gate north5,6 andsouth5,9
saves created/verifiedonPUREoldROM, thenfreshPUREV8Continue migratescorrectside.
Party/bag/ALLvarsflags/Dex/DayCare blocks2/3/4/6/7 BYTEEXACT inOPTIONS stableRAM.
Normal-new-room Save3,1 andfreshContinue3,1 proveNO migrationreplay; same5blocks
exact. Initialno-repeatmovementneededTWO Bpresses tocloseOptions thenMENU;
firstmissedUp selectedmenu, notgamewalking bug. Currentnormal-no-repeat evidence.

IMPORTANT RAM testing lesson: firstlegacytesthitparty-byte mismatch inthird
Clefairy. ARM frameboundary capturedPARTIAL nativeXOR operation (first33boxwords
plaintext, remainderencrypted; partytailmixedtoo). Everychangedwordmatches either
encrypted or SAME decrypted data. Rawchecksumassert canfailonmidfunction snapshot.
Options freezesfieldupdates; independentlyOLD/NEW allfiveblocks thenEXACT.
Do NOT reportpartycorruption or silentlynormalize arbitrarydifferences. Old
headless emulator reportCLOSED at owner's explicitreply: suppliedkitfixedtheir
problem/otheremulators. No moreemulatorinvestigation requested.

All71 Route5 focusedchecks PASStogether160.332s (includes7gate+3compat+61prior).
Finalversionedcandidate nativeContinue passes owner'snormalcampaignMap29,
oldR5saveMap13 WITHone-tilewalking, oldgateMap391migration. Nativefinal50secAV
build/0027-release-recording-v1/prototype-0027-gate-audio.mp4 with preparedsave/
drinkfixture label, observed391/13,44100Hzstereo nonzeroPCM/noRAMwrites,
video49.978187/audio49.986009, pitchpreservedtempo1.0038633467. Localignored.
Recording builtfromfinal0027+privatefixture; privategrants/transport NOTinROM.

Live recovery: oldcloudflarePID1316 was terminated04:48:28UTC, oldhostnameDNS
stoppedresolving. NewdetachedPID5726 log/origin build/0027-tunnel-recovery-v2.
CURRENT https://wit-banana-suddenly-virtue.trycloudflare.com
viewfragment remains samepublic SaBO... storedlive-token; privatecontrolssecret
unchanged, NEVERpublish it. GitHubcurrentURL specificallyupdated/readbackverified
onmanualquestion; streamnewhostname verifiedremoteJPEG/nonzeroaudio/viewerPOST403.
Current livebackend57747 owns build/0027-live-release-0027-v1, finalrelease-derived
fixture; prior96212/V7 stoppedonlytochangeROM. Latestrun_live_release_0027.py
verifiesactualgift/passage thenPAUSES video; preserveURL/tunnel/server. Check
live-passage.json/status; don'tshare/saveDir withanothercore.

NEXT: continuefullKantoYellow reconstruction underlatestno-publicpushgoal.
Route6/UndergroundPath/Saffron progression and smallerremaininggates are next
geometry/story section; requested every-area banners and Blue/Giovanni preHOF
roles stillpending. FullfirstE4/HOF->Johto postgame integration remainslater.
Keepapprovedcustomizations/wholeOakintro, Johtomaps/scripts/encounters/gameplay
untouched; sharednativeDayCarealreadyapproved. Deferunclear changes, continue
independentwork. Do notmarkentiregoalcomplete because0027 checkpoint delivered.

## CURRENT superseding checkpoint — owner requested native interiors / 0028

Owner saw 0027 video and rejected custom small gatehouse visuals. Native HG
interiors need no geometry rebuilding. Preserve native interiors going forward;
fit Yellow events/progression into them. Delivered 0028 local ROM/patch in
C:/RetroArch-Win64/downloads and separate owner-save copy in saves/DeSmuME 2015.
Output build/0028-native-interiors-v1, SHA
0de636af251081172fafcfcfee1017c3dd68c15a654ff97b76e7972a68270a52.
Builder build/build_0028_native_interiors.py starts immutable gates-development
base + all connected R5 options, deliberately omits small-gate geometry patch.
Gate matrix69/land242 model/collision exact vs pristine HG. Yellow shared drink
scripts retained; connected outside doors both north enter native anchor1 and
south anchor0. Native interior returns still route13 anchor0/2.
New tools/route5_native_gate.py only adds391 resume/scene for former small-room
saves: detects saved guard1,3 vs native1,8, schedules async native same-map warp
north5,6 or south5,9 based on old Y<3/GE3. Native normal saves do not migrate.
No new persistent flags. verify_0028_native.py: owner map29, legacy route5 map13
one-tile walking, old native gate stays5,6. verify_0028_native_room.py: small-room
normal save3,1 -> native5,6; stable Options blocks2/3/4/6/7 byte exact; Johto
headers unchanged vs development base. South small-room reverse return still
needs dedicated native save test; do not overclaim coverage.
Final native recording build/0028-native-recording-v2/prototype-0028-native-gate-audio.mp4
passes map391->13 exit, nonzero44100 stereo/noRAMwrites. v1 stopped at tile11
because walking32frames insufficient for restored larger room; v2 uses64.
Originals/0027 untouched; patch encode/decode exact; Oak overlay53 exact0025.
Current live backend session76230 folder0028-live-native-v1 uses0028 private
fixture; same Cloudflare origin/view URL, video OFF. start_live_0028_native.py.
No public push; local plain log and plan updated. Next continue Route6/UG/Saffron
Yellow event/exterior work retaining native interiors; pending banners/Blue roles.

## CURRENT development after 0028 — Route6/Underground foundation

Progress this goal turn: tools/route6_encounters.py + 3 tests PASS. Map14 only
wild header -> appended a/0/3/7 member152, source116. All archives/Johto/interiors
unchanged. Grass Yellow exact species/levels/probabilities across times; rates
walking15/Surf3. Surf prepared5slots Psyduck15 x3 / Golduck15 / Golduck20.
Native Surf/probability selection still pending; do not claim full verifiedSurf.
Fishing/rock-smash original bytes retained pending source audit; radio/swarm
substitutions prevent unrelated grass/Surf species. Table struct verified against
Recovery/include/wild_encounter.h. Yellow Route6 wild source equalsRoute5grass.
Privatebuild build/0029-route6-foundation-v1/private-route6-foundation.nds,
helper build_0029_route6_foundation.py; layout/topologyrefs Route6 20x36 from
read-only Recovery, native map14 mainmatrixcell40,8 land130, northgate389 at
1300/1301,261, UG470 at1309,265. Yellow6trainers source coordinates21/30/31 rows.
Native grass fixture build/0029-route6-wild-v1/wild-grass at14/1305,271 h4;
check_0029_route6_wild.py natural RattataLv14 observed transition-ready.png,
check_0029_route6_run.py native Run95,347 returns14 visibly verifiedrun-return.png.

Next module tools/underground_path_yellow.py + 2 tests PASS. Kanto470girl319 at
3,5 usingYellow text, native room shape/collision unchanged. Native532 corridor
visibleNPC removed (Yellow hasnoactors); original allwarps/backgrounditems/coord
triggers retained. Append-onlyscripts/text/events; only470/532headers changed.
Privatebuild build/0029-underground-foundation-v1/private-underground-foundation.nds
built atoproute6foundation. Girlfixture build/0029-underground-girl-v1, prepared
470/3,6; native girl-dialogue.png visually verified 'People often lose'.
Current0029 NOTreleased/versionbannerstill0028; no public push. NeedYellow6
trainers/exterior, nativeSurf/fishingaudit, Yellow northerngate Cubone/Machoke
trade, corridorhiddenitems audit and bothUGexit traversal; keepnativeinteriors.
Live remains corrected0028 backend76230/tunnel, defaultvideoOFF whileediting.

## Latest Route6/UG development evidence — October13 continuation

Previous goal turn progress revalidated; native532corridor traversal now proved
BOTH directions and doors all the way to outdoor maps. Originalcones are BMD
embedded (land368/371 propsize0), but nativepermissions have gaps atx5/7. DO NOT
remove nativegeometry/cones merely because first testx4 hitscone row9/51.
NativeRoommatrix252 1x2 name11bytes lands368,371 preserved. First failed400frame
walkx4 stoppedcone8; lane5 passes. Endpoint probes holding600frame onlyafter
confirmingactualx5. Nativeinput12frames generallyonecell; 8frames canjustturn or
beignoredafterstate resume;20framescanmove2cells. Do not infer gameinputbug.
Stairsrequire continuingLEFT afterreachingx4 warpeventtile;24framesleftfromx5
works. Same-ROMstatesonly/noRAMwrites. Evidence
build/0029-underground-traversal-v2/verified-traversal.json north469/8,4 h0,
south470/8,4 h0. verified-outside-exits.json north13/1307,185 h4, south14/
1309,266 h4, party3. Both outside-door.png screenshots available. Helpers
finish_0029_north_stair_v2.py and finish_0029_underground_outside.py passed.
Earlierfailedprobe files preserved as diagnostic history, not validproof.

New tools/route6_yellow_reference.py extracts SIX source trainer teams/moves/
messages/vision/facing/positions with sourceSHA256, onlyreadonlyRecovery.
Private manifest build/0029-route6-foundation-v1/trainer-reference.json.
Test test_route6_yellow_reference.py PASS (sixteams, sight0,0,4,3,3,3, exact
Weepinbell/Cubone/Butterfree moves anddialogue). Initialparser off-by-one object
fields corrected toopp6/party7/facing4/text5. Teams: JrM10 Weepinbell16;
JrF25 Cubone20; Bug10 Weedle/Caterpie/Weedle16; JrM5 Spearow/Raticate16;
JrF3 Pidgeyx3 16; Bug11 Butterfree20. Yellowdefaultenemy moves frombase stats
then nonduplicate levellearnset <=level; lastfour, remainingzeros.
NEXT installthose6trainerrecords/nativebattletexts/commonaliases and native
battlefixtures, then final connectedYellowRoute6geometry (20x36 source fits
native32high viaapprovedspacing-onlyshortening ifpossible; nofunctionalrowloss).
Do notclaim trainersalreadyinstalled. Fishing/Surf, northtrade/hiddenitems
stillpending. No publicpush ornewrelease thisturn. Latestdelivered0028.

## Latest 0029 trainer-record checkpoint (heartbeat October13 07:55UTC)

tools/route6_trainers.py builds 6 exact-source battle records803..808 from the
verified trainer-reference manifest. Native templates26Camper/27Picnicker/4Bug,
no personal names, original parties/trainer/name/dialogue entries unchanged.
Teamdata includes explicitYellow moves. Common3000/5000dispatch refs pointto
appendedexpandedaliasbank; tests prove everyoriginalalias resolves SAME bytecode
body (payloadexact), originalscriptbanks archivedunchanged. No map headers or
interior/Johto geometry/resources changed by thistrainer-record step. Newrecords
are NOT activated in campaign overworld yet (actors_installed=False); placement
willfollowfinalRoute6terrain. Do notclaimRoute6campaigntrainersfinished.

Privatebuild build/0029-route6-trainers-v1/private-trainer-records.nds, report.json;
builder build_0029_route6_trainers.py. THREE test_route6_trainers.py PASS: exact
teams/moves/flagcapacity, originalrecords/textprefix andallunrelatedfiles unchanged,
no mapheader changes, original commonaliases/payload same. Modulesforestexpanded
commoncount808 supporttid803script3802, newdefeatflags0x550+id<0xB60.

Nativeprivatefixture build/0029-route6-trainer-native-v1: ONE testactor345 at14/
1305,271, script3802, subtype1,vision0; allotheractorsremoved ONLYinfixture.
Transportowner-save COPY to14/1304,271. Nativefresh-battle/weepinbell-command.png
visuallyprovesWeepinbellLv16. First five repeatedA presses unexpectedlyfinished
wholebattle due owner'sUmbreon100; NOT a trainer failure. Subsequenttalk shows
exactYellowpostdefeat 'My love will leave me in disgust.' facing-challenge.png.
verify_0029_trainer_defeat_flag.py PASS freshflagclear thenvictoryflagset.
verified-native-trainer.json records evidence. No original save writes.
Other5records structurallytested butnativebattles/defeat/repeat unverified.

CURRENTlivebackend35486 owns build/0029-live-trainer-v1 usingisolatedsingletrainer
fixture, labelsDEVELOPMENT0029/preparedplacement, sameviewURL/controlseparation.
start_live_0029_trainer.py; run_live_0029_trainer.py actuallytested live native
video/audio44100nonzero, storedlive-trainer-battle.jpg/live-test.json, thenpaused
feed (server+tunnelremain). No publicpush/newrelease;0028latestdelivered.
NEXT finalconnectedRoute6terrain + installall6actors afterpositionsvalidated;
other5nativebattles, Surf/fishing, northernYellowtrade and hidden-itemsaudit pending.

## Route6 connected-layout reference (heartbeat October13 08:55UTC)

Readcheckpoint/plainlog first; prior goalturnprogress verified. New
 tools/route6_compact_layout.py + TWO tests PASS; source-only reference
build/0029-route6-foundation-v1/compact-topology.json fromreadonlyYellow20x36
fits20x32 usingowner-approved shortening repeated rows0,5,9,34. These preserve
allgrass,6trainers,4doors,28ledges andstart/landing distances, sign, same4gate
reachability booleans. Bothwaterregions retained:52/28 ->52/21 watercells,
secondpondshortenedone repeatedrow. Gatewallrow5 shortensrepeatedbuildingwall,
not an interior. NoROMgeometrychanged yet; don'tclaimconnectedRoute6built.
Compacttrainers relative10,18 /11,18 /0,12 /11,28 /11,27 /19,23;
doors9,0 /10,0 /10,5 /17,10; sign19,12. Sourceinputs remainunmodified.
Tests reject grass/nonrepeated removals, preservepair adjacency/actorwalkability,
waterregion count, structuralfeatures; BFSnorthreach recomputed. Helper
build/compact_0029_route6.py preservesnewoutputexistingrefs.

Terrain nextneedswater rendering/nativeMaterial parsing. NativeRoute6area11,
maincell40,8 land130. IMPORTANT land130 header magic0x201234 means additional
32bytes beforemodel vsR5land153plain0x1234. ps2048/os144/ms20256/bs198;
BMD0 at2244, not2212 (naive20+ps+os). Nativepermissions stillfromoffset20.
Do NOT reuseR5native_materials(land153) parserblindly for130 orreplaceitsnative
header withoutunderstanding32byteextension. inspect_0029_route6_materials.py
locatesverifiedBMD0 and listsnative bindings/materials: pond_on, pond_edge,
pond_line, pond_un, grass01gs,egrass,allpeakgs,fence_a,tree01gs etc. Modelmaterial
count26, pond_on index0. Existingtextured_model expectscliff01gs but visibleledges
replacebindingname withallpeakgs; R6hasallpeakgs notcliff01gs. Neednativewatermesh
plusshoreline. Newcompiler should preserveoldland/matrix andcloneKantoonly.

ConsiderXoffset12 (notR5's10): sourcebottomexit8/9->native20/21 forVermilion.
Validate againstactualnativeboundary beforeusing; sourceUG17+12=29matchesHG
warp1309,265, butcompactnewZ266. GatewholeinR6meansboth389returns toR6newanchors,
obsoleteSaffronsouthprop/doorcollision mustcloneKantocell40,7 ONLY. Do NOTguess
nativecity permissions withoutactualwalking/visualtests. R5model340..342 already
in0028 clones; Route6area11 model-list maynotcontain342; clonearea/list/proptexture
for14 instead ofmodifying any sharedJohto graphics bank. Gateexterior5tiledepth
compact vsR5tested4; diagnostic scaling/native-dooralignment required.
Currentlive35486 pausedafterearliernative803test; sameURL. No publicpush/newrelease.

## CURRENT connected Route6 ROM terrain (heartbeat October13 09:59UTC)

Concrete ROM progress thisturn: tools/route6_connected.py, private builders
build_0029_connected_route6{,_v2,_v3}.py. Latest
build/0029-route6-connected-v3/private-connected-route6.nds.
NativeRoute6 materials parsedat20+ps+os+(magic>>16), BMD0/declaredsizevalidated;
land130prefix32 is BEFORE BMD, permissionsstill20 (runtimeproof below). Native
26materials copiedexact, grass/fences/ledges/nativegate342/UG290/sign31. Optional
water_tiles parameter inroute5_materials.textured_model addspond_on nativewater
mesh; defaultempty preserves oldRoute5. FOUR test_route6_connected.py PASS,
including EXACT released0028 Route5 land reproduction andKantochangeboundaries.
RootR6land695, clonedarea107/list105/proptex105, sourceareas/sharedbanks untouched.
All6trainers803..808 NOW installed atcompactsourcepositions usingXoffset12.
Coordinatepairs: male1302,274 /female1303,274; Bug1292,268; male1303,284 /
female1303,283; Bug1311,279. Nativevision0/0/4/3/3/3, propercommonaliases.
Updated14signbank+emptyinit excludesHGpostgame init; YellowUGsign1311,268.
Native389/470interior graphics/collision unchanged; onlyreturnwarpanchors updated.
389south->14anchor2, north->14anchor1;470outside->14anchor3.

Native evidence: build/0029-route6-terrain-native-v1 centralfield14/1304,272 h4
visuallycorrectgrass/pond/pair NPCs. Water73cells in2regions, p410 nativeWaterRiver;
build/0029-route6-water-door-v1 native walkingUP from1300,281 blockedatshore,
notproofSurfavailable. UGdoor1309,266 enter470/5,9 h0, return14 h4 PASS.
build/0029-route6-gate-native-v1 southdoor1302,261 enter389/5,12 h2 andreturn
14/1302,262 h4; northdoor1302,256 enter389/5,3 h2 return14/1302,256 h4 PASS.
NativeGatefrontlooksHG; NORTHplayeroccludedbehindroof nearbackentrance. Need
furthernorthstreetwalking/visual check beforeclaimfullapproachappearancegood.

v2initialcityseamprobes BLOCKEDboth ends (recordednativefailuresnotreleaseproof).
Investigated actualGetMetatileBehavior source02054918. FS+60->callbacks,+4 points
nativepermissionread. Unicorn executes actualcallback againstCOPIEDnativeRAM,
nevermutatesactualgame/save. query_0029_native_seam_permissions.py and
trace_0029_native_city_permissions.py evidence in0029-route6-seam-native-v1.
City135Saffron(40,7) permissionsoffset20 PROVED: native1300,253 reads66f exactly
rawoffset20 vswrong52 gives8006; readaddress02317a34. City126Vermilion(40,9)
native1305,288 reads600 matchesoffset20; rawhighmagicextra168 elsewhere, doNOT
assumepermissionsshift. Upperpermissionbits are NOT a directgroundheight value!
NativeSaffron135BDHC66 planeWorld32; nativeVermilion126BDHC394 hasmultipleplanes.

v3native_city_links=True: appendSaffroncity135clone696, patchONLY7permissioncells:
x21/22 rows29..31 to600 plusoldwarp x20,row29 to600, preserveentireBMD/props/BDHC.
NO oldgate246prop in135; DO NOTremovecityprops. Original59events preserved,
supersededwarp tilesdeactivated byordinarypermission (samepatternasR5).
SouthSourceYellowexitx20/21 vsHGnativeVermilionroadx25/26: short6tilebend atR6
row31 x20..26 opensonefencegap (omitthatfencesprite), ponds/trainers unchanged.
NativeVermilionassets untouched. FOUR focusedtests prove only40,8 +40,7 matrix
referenceschanged, cityallbytesexceptspecified7permissions exact; Johtoheaders/
archives originalmembers untouched. Actualseamchecks
build/0029-route6-seam-native-v2/seam-probes.json PASS BOTHdirections: north14/
1302,256 h4 ->59/1302,255 h4 ->14; south14/1305,287 h4 ->54/1305,288 h2 ->14.
VermilionisMAP54 (53isLavender), verifiedRecovery/constants/maps.h. Nofade scripts;
needframe-sampled/recordedcrossings beforeclaimingno visibleloading/blackframes.

CURRENTlivebackend43161 ownsbuild/0029-live-connected-v1, sourcev3preparedsave
fixture build/0029-live-connected-fixture-v1, labelDEVELOPMENT0029/connectedRoute6.
start_live_0029_connected.py; run_live_0029_connected.py LIVEpond/Down24 native
trainer sight approach at1300,283 ->PidgeyLv16 observed live-terrain-trainer.jpg
(matches807female/source3Pidgeys). Nonzero44100audio verified; partialbattle/
6A inputs, doNOTclaimall3enemywins/defeat/repeat yet. Feed PAUSED afterward;
server+tunnel sameURL. Live-test.json storedbeforefinallyvideoOFF; readstatus
foractualcurrentstate. Originalsavefiles/prototype0028 untouched. No publicpush.

NEXT: native all6trainer victories/repeats/save, actualSurf/fishingaudit, shore/
wateranimation appearance, northroof/street visualchecks, fullnaturalcity->Route6
->UGwalking plusframesampledno-loadingproof; northernYellowtrade/hiddenitems
stillpending. Sourcecitylinks alignmentbend approvedconnected-HGintent; preserves
functionalYellowroutefeatures. Do NOT release0029 beforecheckpointchecks/recording.

## October 13 — requested 0028 download and prepared post-Misty save
0028 ROM ZIP verified at yellow-heartgold/build/0028-download-package-v1/Pokemon-Psyduck-Yellow-prototype-0028.zip (61,170,614 bytes); extracted ROM SHA matches released0028. Local links only, no hosted/public upload.
No exact archived post-Misty checkpoint was found. Owner latest0025 save is Route25 with Cascade; old0020 pre-Misty save was copied, transported using private fixture to native gym427, and Misty's actual Staryu18/Starmie21 battle replayed on0028. Gyarados30 used Twister then Avalanche; no Pokemon/items/badges granted by fixture. Native reward dialogue completed and in-game Save made.
Fresh core Continue using PURE released0028 verified map427 x10 z2 height10, party3, Cascade present and MISTY_TM0xA89 set. Evidence/build/0028-post-misty-download-v1/verified-save.json; screenshot reloaded-post-Misty.png. Separate deliverable Pokemon-Psyduck-Yellow-prototype-0028-post-Misty.dsv SHA ab683e5135eb9a56e9b23a694f2230f8b68f6749533268fd2eddf5b3c3ca685c. Label prepared from older campaign, NOT latest historical save. Existing owner0028 Route25 save untouched. Helpers prepare_0028_post_misty.py, continue_0028_misty.py, verify_0028_post_misty_download.py. No public push. Resume0029 checkpoint plan above after user deliverables.

## October 13 — Route 6 trainer checkpoint
Native victories verified for all six trainers803..808; initially-clear defeat flags set and repeat dialogue checked. Evidence build/0029-all-trainers-native-v1/native-trainer-checks.json. Earlier805 automation stall was a switch-to-active-Pokemon input issue; touch selection of Gyarados and Keep Battling recovered it. New helper check_0029_trainers_touch.py completed806..808 without ROM edits.
Native Save after808 followed by fresh Continue on pure candidate0029v3 preserves map14 and808 defeat flag: build/0029-trainer-save-reload-v1/verified.json. Separate trainer save copies; not all6flags in one campaign. Original saves and0028 untouched. No public push/release. NEXT Surf/fishing badge audit, water appearance, north roof visual checks, frame-sampled city crossings, audio recording and northern Underground content. Live URL unchanged, viewing paused.0028 remainslatest.

## October 13 — native Surf and city-crossing evidence
Created ignored private Surf fixture from0029v3 and copied owner save. Diagnostic native script grants Psyduck30 with Surf57 in party slot3 and FogBadge3; explicitly labeled private grants in fixture.json, NO grants in candidate/releasedROM, no original save edits. Native interaction prompt -> Psyduck used Surf -> avatarstate2, walking on pond from1300,281 to1300,277; Down32 disembarks >=281, state0. Evidence build/0029-native-surf-private-v1/verified-surf-roundtrip.json and surf-actual-moved.png. Actual water behavior works; Kanto SoulBadge eligibility remains pending because native field_move.c requires JohtoFog3. Need Kanto-only hook including BOTH menu and shoreline interaction, preserving all Johto behavior. Do not claim SoulBadge unlock implemented.
City crossings frame-sampled from same-ROM copied native states (transport already completed before recording). 100 consecutive frames each: Route6->Saffron59 at1302,255 and Route6->Vermilion54 at1305,288. No fullblack/fade: minimum visible top fraction99.99/99.64percent respectively. Evidence build/0029-city-crossing-frames-v1/verified-crossings.json + frame-visibility.json. Actual nonzero native stereo44100audio captured; two short MP4 clips encoded top-left/bottom-right, paths north/city-crossing-native-audio.mp4 and south/same. helpers check_0029_crossing_frames.py, emulator_crossing_audio.py, encode_0029_crossing_recordings.py. These are ~1.67s crossing proofs, NOT release recordings or full campaign traversal.
Northern screenshot shows native gate roof occluding player just beyond boundary; still need furthernorth streetwalk visibility check. Surface look is native river texture (static mesh material); animation/shore polish remains pending. Fishing weights/source audit not completed. No public push, no release,0028 stilllatest. Livebackend unchanged/paused; these diagnostics used isolated smoke core, not live feed.
NEXT Kanto-only HM Surf badge handling meaningfulJohto regression, fishing source audit, north gate approach visibility, full natural traversal and releaseaudio recording, northernUGcontent.

## October 13 — Kanto-only Surf badge implementation validated
New tools/kanto_surf_badge.py patches ONLY menu native badge call020680FA and shoreline overlay1 call021E7534. Menu hook uses r4 FieldMoveCheckData mapId; shoreline uses r5 FieldSystem->location(+0x20)->mapId. Both read native map header Kanto bit atTABLE+map*24+20, select Soul12 forKanto and originalFog3 forJohto. All later native restrictions unchanged. Original non-overlay1 files exact; overlay1 differs only4bytes atbadgecall; originalmain code differs only4bytecall + append/layoutmetadata. No Johto map/script/encounter edits or releasedcheckpoint edits.
Private latest candidate build/0029-kanto-surf-badge-v3/private-connected-route6.nds, source immutable route6-connected-v3 SHA bbe7cd0d9140e139ff40362053b38cff2ca8aada11c95df54103bfd864ba7b67. Use THIS asnextbuildbase whenincorporatingSurf; livebackendstillolderconnectedv3.
Failed intermediates v1/v2 preserved, NOTrelease: v1 Keystone unaligned literal produced unsupportedLDR.W and directBLtarget+2; replaced with aligned .balign4 literal + nativefunctionBLX. v2 menu-only exact2160cases butactualshoreinteraction deniedSoul-only; found separateoverlay1 badgecall via binaryaudit. v3fixesboth. tests/test_kanto_surf_badge.py THREE testsPASS including all540maps x4Fog/Soulstates x2hooks (4320nativeexecution results), preservedr4/r5/SP, DS-compatible16bit hookinstructions, onlyallowedcode/memberdifferences and nativeautoloaderoffsetsdelta80. Test failure onautoLoaderpointers fixed byasserting exactexpectedrelocation; no gameplaycodemasking.
Native Soul-only fixture (Psyduck30/Surf57 plusSoul12 testgrant, noFog3) build/0029-native-surf-soul-private-v2: shorelineprompt, nativeSurf move, avatar2 at1300,277, disembark>=281 state0. verified-soul-roundtrip.json. noSoul/noFog fixture build/0029-native-surf-no-badge-private-v1: promptabsent, walkingblocked1300,281, avatar0; verified-denial.json. Alloriginalsave/ROM untouched. Fixturesprivategrants excludedcandidate. Menuhook logicexecutedexhaustively butactualparty-menu UI use notyetplayed; final native menu UI check pending. No publicpush/release.
NEXT actualparty-menuSurf UI; fishing weights/sourceaudit; furthernorthroof/streetvisualcheck; fullnativewalking/UGtraversal and releaseaudio recording; northernUGtrade/hiddenitems pending.0028 remainslatestdelivered. LiveURL unchanged/paused.

## October 13 — party-menu Surf, northern street and fishing odds audit
Completed actual party-menu Surf use on latest candidate fixture build/0029-native-surf-soul-private-v2: selected Psyduck card at180,267 (after closing Clefairy submenu), touched Surf60,223, native 'PSYDUCK used Surf!' then confirmedavatar2 at1300,277. Soulonly/noFog badges retained. Evidence verified-party-menu-surf.json, psyduck-menu.png, menu-surf-result.png, party-menu-surf-moved.png; helper step_private_fixture.py / check_0029_menu_surf_north.py. Party-menu native check now done.
Northern street walking from copied same-ROM seam proof state in NEW build/0029-north-street-visibility-v1: north72frames reachesSaffron59 at1302,246 h4. Avatar visible afterfirst24framewalk; screenshots north-street-1..3.png. Native gate roof occlusion is limited to immediatebackdoor edge. White rectangular road patch visible near1301/250; nativeSaffronBMD untouched, compare pure0028 baseline before anygeometryedit. Treat appearance issue separately; not a loading screen.
Fishing engine absent from supplied incomplete Cdecomp; reversed actualoverlay2. FieldSystem_PerformFishEncounterCheck at02246F70, fishingtable offsets80/94/A8, selectorcall02247CCC->02247764. Executednative selector on copied ROM memory with ONLY RNGstub fixedroll0..99 (nativeARM division still executes), exact nativecounts[40,30,15,10,5]. Evidence build/0029-fishing-source-audit-v1/audit.json + native-selector-rolls.json; helper audit_0029_fishing_rolls.py. Exact YellowGoodRod50/50 achievable slots[Goldeen,Poliwag,Poliwag,Goldeen,Poliwag], level10. OldRodallMagikarp5. YellowRoute6SuperRodGoldeen5/10/15/20 equiprobable needs scoped slot selector; do NOT approximate with HG40percentfirstslot.
Night substitution native02246AD4 replaces Goodslot3 and Superslot1 withtableC0nightFish. Swarm replacement native02246BD8 still needs full audit. Abilities native MagnetPull/Static optionalslotbias beforedefaultselector; preserveHG systems unlessKantoYellowrequiresoverride (donotquietlychangeJohto). Fishingtables STILL UNMODIFIED, auditonly. Latestnextbase still0029-kanto-surf-badge-v3/private-connected-route6.nds. Originals/checkpoints untouched, no publicpush.
NEXT baselinecheckwhiteSaffronstreetpatch; fishingtable/selector scopedmap14 implementation with day/night/swarm checks; northernUGtrade/hiddenitems; fullnativewalking plus releaseaudio recording. LiveURL unchanged, diagnosticsnotlivecore; viewing remains paused.0028 latestreleased.

## October 13 — owner-approved cross-region Surf exception implemented
Owner explicitly requires SoulBadge to enable Surf in bothregions, overriding prior preservation constraint for thisonefeature. FogBadge retained asalternative. Changed tools/kanto_surf_badge.py to shared32byte nativehook checksSoul12 thenFog3; both native menu020680FA and shorelineoverlay1/021E7534 callit. No region restriction; allothernativeSurf checks unchanged. Johto map/script/encounter assets untouched.
NEW latestcandidate build/0029-global-surf-badge-v1/private-connected-route6.nds fromimmutableconnected-v3; doNOTcontinuefrompriorregion-onlycandidate. Released0028 untouched. THREE focused testsPASS, nativecode execution all540mapcontexts x4badgecombos x2entrypoints (4320results), expectedSoulORFog, DSinstructionwidth and exactchangeboundaries/callee-savedregisters/SP verified.
Native actualJohto test on NewBark60 coast700,401 East withSoulonly/noFog; native prompt -> Surf at702,401 avatar2. Returnedtoland thenselectedPsyduck fromparty andSurf: actualparty-menu use alsoSurf2 at702,401. Evidence build/0029-global-surf-johto-private-v2/verified-johto-soul.json, johto-soul-surf.png, johto-party-surf-menu.png, johto-menu-surf-used.png. Fixture grantsPsyduck30/Surf57/Soul12 ONLYtestcopiedsave; transport script modifies ONLYsourceKanto29, noJohto map/script edit. SourceoriginalROM/save preserved.
Johto initialshorefixturev1 at680,401 waswrongcoordinate due rawland0permission lookup; preservedfailedfixture. Queried actualnativepermissioncallback in copiedRAM, correctshore700/401->water701/401. No actualgameRAM edits.
Latest checkpointplan now PROTOTYPE-0029-PLAN.md; handofftop stale0025/0026 references corrected. No publicpush/release. NEXT fishingYellowtables/exactSuperRodselector scopedRoute6, Saffronwhitepatchbaselinecompare, northernUGcontent and fullreleaseaudio recording.0028 latestreleased. LiveURL unchanged/paused.

## October 13 — owner clarification: limited Johto traversal changes
Kanto campaign completion is the top priority. Johto opens as postgame only after completing the full Kanto campaign, the first Elite Four challenge and the first Hall of Fame entry.
Johto edits are authorized ONLY when an actual need arises to make the entire region traversable with the necessary HMs, including compatibility with Kanto-earned unlocks such as Soul Badge Surf. Do not proactively redesign Johto or alter unrelated maps, encounters, characters, story or gameplay. Preserve HeartGold Johto as much as possible; apply only the changes required for traversal/HM access. This supersedes the previous blanket prohibition on Johto edits within this limited scope.

## October 13 — fishing implementation, graphics comparison and preview/banner rules
Latest private candidate now build/0029-route6-fishing-v1/private-route6-fishing.nds, derived fromglobalSurf candidate; globalSoulORFog Surf retained. tools/route6_fishing.py appendswild153 onlymap14, OldallMagikarp5, Good[Goldeen/Poliwag/Poliwag/Goldeen/Poliwag] all10 (nativeweights40/30/15/10/5 =>50/50). SuperfourGoldeenlevels5/10/15/20 equalnativeRNG low2bits. Threeoverlay2 callsitehooks: fishhelper224708A tags copiedstackRod2->3 ONLYmap14, selector2247CCC handles3 elsedelegatesnative2247764, fishswarm2247070 bypassesONLYmap14. Nativeothermaps/Johto behavior delegated, nooriginalarchive member changed. New table C0nightFishGoldeen preserves Goodslot3/Superslot1. Bite rates preserved.
tests/test_route6_fishing.py FOUR focusedtestsPASS inclall540maps x3rods markerABI, defaultnative distributions, exactSupertagdistribution, allarchive/code boundaries/swarm scope. Addedfifthnative nightreplacement test; rannewtestPASS (nativeTime0/3/4, Good+Super unchanged species/levels). ActualprivateBag->SuperRod -> landedPokemon ->nativebattleGoldeenLv5 observed build/0029-fishing-gameplay-private-v1/super-rod-battle-confirmed.png /native-battle-observation.json. PrivateSuperRod447 grant onlytestsave. Old/Good actualUI catches stillpending.
Saffron graphics compare root0029-saffron-graphics-baseline-v1: originalHG,0028,globalSurf0029 sameposition59/1302/249 all0 nearlywhite top pixels; earliernaturalwalkimage has439whitepixels. White rectangle occurs duringnaturalcitytransition, disappears ondirectcityload. Staticnativecitymodel unchanged; investigate transition/rendercache, doNOTeditnativecityart blindly. Fulltransitionvisualfixpending.
Owner presentationrule: retainnativefull-screen area/entrance previews and native morning/day/evening/night art. Showonfirstvisit andfirstentryAFTEReach time-of-day periodchange; suppressrepeatentries withinperiod. Showagain nextcycle (not onceeverperfourartvariants). No automaticpreview whileplayerjuststandsinsidearea; onentryonly. Fourartphases: nativeNite+Late bothnight. Existingseenhistory mustpersist throughSave/Continue without corrupting old saves; safe allocation notchosen yet. This is explicitlyrequestedpresentation behavior including shownJohto examples, separatefromtraversal-only gameplay changes.
Nativepreview audit: map_preview_graphic.c GetIndex/BeginShowImage retainfourvariants, assetbank a/1/5/0; nativewarp unk_02055BF0.c case7 calls GetIndex andshowImage everyeligibleentry, no visit-history guardthere. NewfrequencyruleNOTyetimplemented; addsafe persistence beforeclaimingdone. Full-screenpreviews exception toconnectedoverworld rule; ordinarysmallnamebanner stillEVERYareaentry.
Actuallyverified smallbanner naturalRoute6<->Vermilion repeatedentries ANDrapidrecrossings in build/0029-banner-repeat-native-v1: route6-first.png, vermilion-return.png, route6-repeat.png, quick-vermilion.png, quick-route6.png. Bothcorrectnamesobserved; no codechange neededfor theseentries. Allotherareas stillneedper-checkpointchecks, doNOTclaimall540areasverified.
No publicpush/release;0028 remainslatest. NEXT Old/Good nativefishing checks, transitionwhitequadcache investigation, northernUGtrade/hiddenitems, previewfrequency savedata design, otherbannerchecks and fullreleaseaudio recording. LiveURL unchanged/paused; smoke tests notlivebackend.

## October 13 — all three rods checked in native gameplay
Old Rod native Bag->use->bite->encounter: MagikarpLv5 observed build/0029-fishing-old-private-v1/native-rod-battle.png. Good Rod samepath: PoliwagLv10 in0029-fishing-good-private-v1/native-rod-battle.png. Super Rod priorGoldeenLv5 remainsverified. Thus all3rod nativeUI encounter checks pass; exactspecies/leveldistributions, nighttime andscope alreadychecked bynativecode tests. Pokemon were landed andbattlesstarted, notcaptured; doNOTclaimnewcampaigncaptures.
Eachprivatefixture copiesownerSave; nativeGiveItem445/446 grants ONLYthetestrod beforeKanto29->14 transport. Originals andcandidate unchanged. Helpers prepare_0029_fishing_old/good.py, check_0029_old_good_native.py, record_0029_old_good_checks.py. emulator_fishing_react.py readsnativeTask_OverworldFish env/SysTask stage and sendsA whenbitephase5 /messagephase8/13; writes noRAM andnogamepatch. NativeTask source verified againstreadonlyHG sys_task.h /overlay_01_021FC66C.s. Evidence native-battle-observation.json ineachfixture.
Currentcandidate remains build/0029-route6-fishing-v1/private-route6-fishing.nds; NOTreleased. All3rod gameplay checks removedfrompending. NEXT Saffrontransitionwhitequad artifact, northernUndergroundtrade/hiddenitems, safe savedpreviewhistory rule, allarea banners andnaturalroute releaseaudio recording. Johto limitedtraversal exception/SoulSurf maintained perlatesthumanclarification; no unrelatedJohto edits. No publicpush;0028 latestreleased. Livebackendunchanged/paused, isolatedsmokechecks notstreamed.

October 13 noon Eastern: daily Discord update confirmed sent (message 1559596643697828011), including GitHub DEVELOPMENT-LOG link. Reported released0028 versus private0029, connected Route6 trainer/Surf/fishing checks and remaining work. Existing Windows user posting ledger updated; temporary draft removed. No public Git push.

## October 13 — Underground hidden rewards verified; north trade audited
Read-only source audit tools/underground_yellow_reference.py, evidence build/0029-underground-source-audit-v2/audit.json with sourceSHA hashes. Yellow north/south corridor contains FullRestore23 andXSpecial61. ExistingnativeHG532 rewards8057 at5,14 and8058 at7,30 ALREADY contain exactly23/61. KeepnativeHG positions/interior perownerpreference; no itempatch required.
Initially prepared experimentalbuild/0029-underground-items-v1 relocatingpositions5,7 /5,50 beforediscoveringexactnativeitems. REJECTED, neverreleased/used aslatest; helper underground_yellow_items.py deleted; builderignored nowobsolete. DoNOTuseexperimentalROM. Lateststill0029-route6-fishing-v1/private-route6-fishing.nds.
Actualnative pickups verified build/0029-underground-pickups-native-v2/verified-pickups.json: spawnFullRestoreadjacent5,15 faceUp andXSpecial6,30 faceRight, pressA->rewardmessage, flags0x359/0x35A clear->set, repeat flagsretain. Screenshots item-pickup.png,repeat-pickup.png forboth. No item/badge/Pokemon grants, onlyKanto29 transport inprivatecopy. v1 testfailed becauseit stoodON rewardtile; HG A checksfacingtile. Correctedv2 casesPASS; noROMcodefixneeded. Originalsavefiles/candidate untouched.
North469 trade source scripts/UndergroundPathRoute5.asm + data/events/trades.asm: giveCubone104 -> receiveMachoke67 nicknameRICKY. CRITICAL engine/events/in_game_trades.asm explicitlytestsMACHOKE andcallsTryEvolvingMon: nativeYellow evolves it toMachamp68. DoNOTdisabletradeevolution basedonobsoletecommentaboutJPBlue/EnglishYellowdialogue. OTsource '<TRAINER>'. Trade stillNOTimplemented.
Potentialsafe reuse: archivedKantoPewterPokecenter Haunter/Xatu record9; tools/pewter_interiors.py removedtradeNPC4 andarchivedformerbank. RawLoadNPCTrade470+byte9 scanALL540currentheader banks yieldsNOreferences: native-trade9-references.json. Reusing9 canavoidglobalNPC_TRADE_MAX13 andnickname/OToffset13 expansions; verify anyotheractivecommon-scriptrefs beforemutatingrecord9. NativeNPCTrade record21ints/0x54, archivea/1/1/2; messagesbank200 nick9/OT22. Preserve allothernativeNPCtrades includingJohto, shinyrerollhook andsharedtradeengine. Noimplementationyet.
NEXT northRICKYtrade nativeanimation/evolution/save/repeat tests; Saffrontransitionwhitequad graphicscache, safepreviewhistory allocation and releaseaudio recording. Allotherlatestowner rules remain. No publicpush/release. LiveURLunchanged/paused.
Additional inventory proof: check_0029_ug_bag_deltas.py compares copied-owner baseline Bag block3 against pickup+repeat RAM. FullRestore994->995, XSpecial995->996, exactly one item each after repeat. Evidence verified-bag-deltas.json. Final pickup screenshots are after dialogue closes; only v1 facing-item.png captures FullRestore message.

## October 13 — stream tunnel refreshed at owner's request
New public viewing origin: https://attributes-set-inbox-educational.trycloudflare.com
Tunnel PID47005; logs/evidence build/0029-tunnel-refresh-v1. Previous tunnel5726 was verified and stopped. Existing backend remains connected, video/audio paused between playtests. Remote page/status passed; viewer can_control=false and control POST rejected403. Public GitHub DEVELOPMENT-LOG.md stream link alone updated and fetched for verification; commit132c45de3b95e1a90a5e48bff9aed1864d96f9ac. No code, ROM, save, or private control credential published.

Interrupted development checkpoint: northern Underground RICKY trade candidate build/0029-underground-ricky-v3/private-ricky-trade.nds is UNVALIDATED. Native trade receives Machoke30 named RICKY with OT TRAINER, but native HG NPC trade does not evolve it. Yellow source explicitly requires Machamp; implement scoped native post-trade evolution before claiming complete. Native copied-save fixture build/0029-ricky-gameplay-private-v2 is in RICKY Summary; no original saves touched. Latest validated base remains build/0029-route6-fishing-v1/private-route6-fishing.nds; 0028 latest release.
## October 13 — RICKY native trade/evolution checkpoint validated
Latest PRIVATE candidate now build/0029-underground-ricky-v5/private-ricky-trade.nds, derived from validated Route6 fishing base. Native map469 geometry/warps unchanged; trade9 reuses removed Kanto Pewter clinic trade. Native trade script copied from original bank753, flag0x133. Cubone104 -> Machoke67, nicknameRICKY/OTTRAINER, then native trade evolution toMachamp68.
tools/ricky_trade_evolution.py redirects native Task_NPCTrade pointer02067A5C to232byte ITCM wrapper. Scope map469+trade9+state4+species67+nativeGetMonEvolution result68. Runs native evolution app flags4/heap26, waits state7 then frees/destroys heap and resumes original state4 overworld restore. Temporary evolution pointer reuses finished animation data offset0xC; no saved-variable allocation. Native cleanup address0201A9C4 verified from wireless trade disassembly. v4 contained incorrect guessed cleanup address and MUST NOT BE USED; v5 corrects it before native animation test. Remaining ITCM space ~380bytes; account for this before future hooks.
THREE evolution tests pass: all539 othermaps/all12othertrade IDs and otherstates fall through native task, ABI and lifecycle checked, ROM member/overlay preservation. THREE resource tests pass: other540header assets/records/names preserved, native interior/warps retained. Tests test_ricky_trade_evolution.py and test_ricky_trade_resources.py.
Actual private fixture build/0029-ricky-gameplay-private-v4 (v5 ROM plus copied-save Cubone30 testgrant/transport) performed native Cubone send, RICKY Machoke arrival and native Machamp evolution (trade-evolution-start.png shows congratulations). Returned to room and repeat text verified. Native Save completed; fresh purecandidate Continue in build/0029-ricky-save-reload-v1 verified map469/party4/tradeflag0x133 and Summary Dex068 MACHAMP/RICKY/OTTRAINER/level30. Repeat-after-continue-confirmed.png shows one-time completed trade dialogue. No repeated trade offer after Continue.
Separate no-grant copied-save fixture build/0029-ricky-decline-private-v1 rejects Umbreon wrongspecies, retains party3 and clear tradeflag; decline/cancel UI still untested. No original saves modified. No publicpush or release. 0028 remains latest released.
NEXT explicit decline/cancel check, Saffron transition whitequad artifact investigation, safe saved-preview-history design, full natural candidate traversal and real audio release recording. Existing live backend still older connected terrain fixture, viewing paused; new trade native checks ran isolated smoke core, not livestream.
Additional native NO refusal verified in build/0029-ricky-decline-private-v2: declined-trade.png says That's too bad; verified-decline.json confirms party3 unchanged and flag0x133 clear. No grants in this fixture. Party-selector Cancel remains untested; explicit offer refusal now complete.
## October 13 — trade Cancel and seamless native terrain textures validated
Party-selector Cancel verified build/0029-ricky-cancel-private-v1/cancelled-trade.png and verified-cancel.json: native That's too bad dialogue, party3 unchanged, tradeflag0x133 clear. All requested RICKY trade paths now checked.
Saffron rectangles diagnosed as absent native terrain textures wall01_h/ymb_hole/ymb_shouka in Route6 bank11; Saffron bank12 supplies them. Native area manager loads terrain bank for the field session, so seamless crossing exposes missing entries previously hidden behind native gate warps. Model-list-only probe did NOT fix it and is not a candidate.
tools/route6_seam_textures.py appends union bank and cloned area records ONLY for Kanto maps14/59/54. All original texture/area members, geometry, collision, props, scripts, encounters, executable instructions and Johto headers remain unchanged. Shared graphics payloads identical except native Patricia dictionary-node metadata. tools/nitro_dictionary.py rebuilds dictionary nodes when membership changes.
Important failed probes: unionv1/v2 removed rectangles but broke compressed tree palettes because ndspy reorders palette data; v3 failed explicit offset assertion before writing ROM. REJECT v1-v3. v4 preserves the entire original bank11 palette buffer/offsets literally and relocates appended bank12 compressed4x4 palette references. Native trees, pavement and manhole/details now correct. Do NOT use earlier texture probes.
Latest VALIDATED PRIVATE candidate: build/0029-seam-texture-union-v4/private-seam-textures.nds, derived from RICKYv5. Three test_route6_seam_textures.py checks PASS: unchanged other files/headers/ITCM, original graphics payloads and new names, serialized Patricia lookup of every texture/palette. Initial preservation test flagged compressedStaticEnd metadata bytes; test now verifies exact ARM9 compressed end=02000000+len(rom.arm9), permitting only its4metadata bytes besides3area-header bytes.
Native Route6->Saffron walk at1302,249 renders correct pavement/trees. Fresh Saffron entry similarly correct. Saffron southbound enters native gate389 as intended; initial return test wrongly expected immediate map14, corrected target389. Fresh Vermilion->Route6 walking confirmed14/1305,286 with correct terrain. Evidence build/0029-seam-texture-return-checks-v2/verified.json and before/after screenshots. No claim of entire-route final traversal yet.
Actual live backend switched gracefully to current candidate NORTH private transport fixture, copied owner save, no Pokemon/item/badge grants. Session29515, output build/0029-live-seam-textures-v1. Live native Route6->Saffron and brief return exercised with actual nonzero44100stereo audio; verified-live.json. Feed PAUSED afterward. Tunnel PID47005 and public URL unchanged, remotely reverified page200/view control403/can_control=false. Already-posted GitHub link remains valid; no public push this turn.
NEXT safe saved-preview-history implementation, broader area-banner checks, full final native route/gate/Underground traversal and real audiovisual release recording, package0029/checks in fresh paths. Preview frequency still UNIMPLEMENTED; preserve native art and save compatibility. Native interiors remain unchanged. Released0028 and all originals untouched.
## October 13 17:23 UTC heartbeat — preview storage audit
Read latest handoff/log/0029 plan; current validated candidate remains seam-texture-union-v4. Source audit found25 native full-screen preview destinations (fits32-bit visit mask). SAVE_MISC block9 defines unused filler_0288[16]; native initialization zeroes it, no named filler references in native C/project Python, and three copied-save RAM samples show all16 bytes zero. Evidence build/0029-preview-storage-audit-v1/audit.json includes source SHA hashes and sampled block sizes/padding.
This is promising allocation evidence, NOT an exhaustive native-code access proof. No save fields or ROMs changed. SaveVarsFlags offset0x288 used by existing recovery is a DIFFERENT block4 variable, not Misc padding; do not confuse these addresses.
Proposed compatible history layout inside16bytes: magic/version, packed date+morning/day/evening/night stamp, 32-bit seen mask, reserved word. Reset mask when full date/period stamp changes; this allows a preview again next day even if intervening phases were not visited. Late and Nite share native night art. Mark only an actual preview entry, not simply standing in a map. Keep ordinary name banners every time.
NEXT prove Misc padding's native access boundaries, implement scoped warp preview eligibility hook with native RTC date/time, test sameperiod repeats/newperiod/newday/SaveContinue/legacy saves and untouched adjacent bytes/art. ITCM remaining ~380bytes; check hook budget. Preview frequency remains UNIMPLEMENTED; no release/publicpush.
## October 13 18:22 UTC continuation — native preview history implemented and tested
Private candidate build/0029-preview-history-v1/private-preview-history.nds derives from seam-texture-union-v4. tools/preview_visit_history.py redirects ONLY native warp GetIndex call02055F42; native index lookup0206A360 still executes. 120byte Thumb hook uses SaveArray_Get block9, SAVE_MISC unused padding0288..0293: magic31565050, packed native RTC year/month/day/4phase stamp, 32bit seen mask. Neighbor reserved0294..0297 untouched. Same date+period repeats return255, native warp still calls small-banner animation; newdate/period resetsmask. Native RTC getters02014780 CopyDate and0201481C GetTimeOfDay verified by actual native callers. Nite/Late sharephase3.
THREE test_preview_visit_history.py checks PASS: all25 real native preview IDs acrossfour phases/repeats/nightLate/newdate, all nonpreviewmaps noSaveaccess, persistedhistory model/clockback/change, ABI/SP/adjacentcanaries, unchanged ROMmembers/overlays/art/intro and exact restricted maincode edits.
Actual Forest entrance from native south gate419 verified build/0029-preview-forest-native-v1: first-entry7/9/12 show native evening full-screen art, then normalForest147. Only copied-save Kanto transport, NO grants. LeftForest naturally, nativeSave inside gate419 completed. Fresh PURE candidate Continue in build/0029-preview-save-reload-v1 preserves history and gate419; reentry repeat-entry7/9 show ordinary overworld plus small ViridianForest banner, no full-screenart.
Controlled-hour private fixture build/0029-preview-time-change-private-v1: getter fixture alone routes hour10 through original native hourly mapper02014844; art and eligibility both see nativephaseDAY. On entry from copied evening-history save, correct daytime full-screenart reappears, newstamp observed. Timeoverride EXCLUDEDcandidate; realclocknotchanged andoriginal saves untouched.
Live backend session55566 now this candidate's Forest entry private-transport fixture, folder0029-live-preview-history-v1. First live navigation sentUp before transport settled and failedarrivalassert; feedpaused viafinally, no emulatorfault. Retried aftersettle in build/0029-live-preview-retry-v1: first-native-preview.jpg shows native eveningart, repeat-small-banner.jpg shows overworld+namebanner; nonzero44100stereo audio verified. Feed PAUSED aftertest, tunnel URL unchanged.
Before accepting final semantics, audit duplicate preview variants: native table has25 entries including Ruins/Sinjohevent and VictoryRoad1F/3F. Identical art variants should share history; distinct DarkCave entrance artwork may retain separate first-view tracking matching owner's table. Do not claim all25 areas were gameplay-tested; native code scope testedall, actualForest only. No release/publicpush. Current preview candidate is development pending variant audit/final route checks; latestreleased0028.
## October 13 20:52 UTC — preview variants/night-cycle checkpoint complete
Latest VALIDATED PRIVATE candidate now build/0029-preview-history-v3/private-preview-history.nds, from seam-texture-union-v4. Final preview hook228bytes at01FFFE84, approx152bytes ITCM remain; avoid exhausting native32KiB ITCM.
Source artwork-ID audit build/0029-preview-variant-audit-v1/groups.json: Ruins normal/Sinjohevent indices3/4 have identical four-phase artwork; VictoryRoad1F/3F16/17 identical. They now share history keys3/16. Distinct DarkCave entrance graphics retain separate keys0/1 matching owner's separate preview rows. All native artwork/index selection remains unchanged. Initial table LDR mistakenly read bytes as pointer and failed Unicorn before ROM build; corrected to Thumb ADR.
Fixed midnight continuity before accepting final rule: nativeLATE4 is continuation of previous calendar date's NIGHT3. Subtract one date for LATE, accounting for month/year boundaries and leap years in DS RTC2000..2099; do not repeat unchanged night art at midnight. Source night v1/v2 are superseded; usev3.
FIVE focused tests PASS: every real native preview map/identical variant grouped correctly, four periods/repeats/newdate/Latecontinuity, month/year/leap transitions, allnonpreviewmaps untouched, persisted history, adjacent Misc canaries, ABI/SP and DS-supported instruction stream, unchanged original ROMmembers/overlays/art/intro. No Thumb2 wide instructions in execution path.
Native v2 first entry showed nightart at real currentclock. Fresh purev2 loading prior saved evening history showed correct nightart again after actual timeperiod change (preview-save-reload-v2/repeat-entry9). Made a normal nighttimeSave in nativegate419 onv2, then fresh purev3 Continue with that copiedSave: history retained, repeat entry omitsfullscreenart and shows smallForestbanner (build/0029-preview-save-reload-v4/repeat-entry9.png). Fresh legacy-owner fixture onv3 also shows correct first nightart (preview-forest-native-v3/first-entry9.png). No grants in these fixtures, only initial Kanto transport; originals untouched.
Live backend remains session55566/0029-live-preview-history-v1, earlier basic history candidate; paused betweenplaytests. URL unchanged. Before livefinalrecording switch gracefully tofinalv3 candidate/testcopy, not cross-ROM emulatorstate.
NEXT full final Route6/gate/Underground traversal, broader small-banner checks, true audiovisual release recording, cumulative patch/ROM verification and local delivery of0029 in fresh paths. Preview-frequency work now complete for checkpoint; do not claim all25 destinations were gameplay-tested (all25 testednativecode, actualForest field). No publicpush/release;0028 latest released. Latest human Johto traversal/HM exception continues to override stale heartbeat prohibition.
## October 13 — final-candidate preservation and continuous traversal in progress
Final preservation audit build/0029-final-preservation-v2/verified.json compares released0028 to preview-history-v3: all340 Johto map headers and active script/init/text/event resources identical; original land members identical. Shared mainmatrix0 differs ONLY at Kanto cells40,7/40,8; all other existing matrix members unchanged. Changed Kanto headers14/54/59/389/469/470/532. Candidate SHA e10c99766c73e7c458632bd7d9a17ee97bfe10231b33a727294c62eafaf08d76. Initial blanket matrix-prefix assertion was too broad for intended Kanto connections; corrected precise cell check, not masked gameplay changes.
Continuous native walk on FINAL candidate in build/0029-final-traversal-v1: copied ownerSave, initial private transport ONLY to northUG469,7,4. No Pokemon/item/badge/defeat grants. Then ordinary inputs reached532 corridor,470 south entrance,14 Route6 at1309,267. Corridor cones require alternating lanes6 then5; older claim of entire lane5 passability was imprecise. Native interior unchanged. Warps trigger stepping past the edge; single8frame Right stoppedonstair, additionalordinaryRight enteredcorridor.
FromRoute6 entry walked northgrass, east ofpond, encountered wildPidgeotto17, escaped nativeRun menu, and continued through southern approach. Required trainer807 approached at1300,283; native battle against threePidgey16 used owner's existing Umbreon100 FaintAttack. This is a functional prepared-save check, not campaign difficulty evidence. Separate trainer807-observation.json records actual defeat flag.
Current state atRoute6 1300,283; checkfield/battle completion from currentRAM/screens before nextDown movement. Finish second southern trainer if needed, ledge and road toVermilion, then final native Save/Continue, recording and packaging. Traversal stillINCOMPLETE, no0029 releaseyet.
Walk-progress.json logs all executed inputs/checkpoints. Same-ROM recording-start state+ROM/core SHA metadata saved before Route6 walk under record-start; no cross-ROM states permitted. Actual recording notmade yet. Input ledger now retains touches. Last hoststdout interruption was checked: no live emulator process and missing exit screenshot, then pendingstep rerun; reached14 naturally.
Owner asked where handoff lives; provided local Windows/WSL path and queued opening in currentCodex panel. No publicpush. Goal remains full YellowKanto remake, not just checkpoint0029.
## October 13 — final Underground-to-Vermilion traversal and save verified
Completed continuous ordinary-input traversal on final preview-history-v3 candidate: north Underground entrance469 -> corridor532 -> south entrance470 -> Route6 -> Vermilion54. Initial copied-save transport to469 only; no Pokemon/item/badge/defeat grants. Native wildPidgeotto17 encounter escaped; southern trainers807 (threePidgey16) and806 (Spearow16/Raticate16) defeated using existing owner party. Functional prepared-save test, not campaign difficulty evidence.
A transient black screenshot after806 did not establish a hang: post-victory-settled.png shows restored native field, and subsequent ordinary Down crossed the ledge to1300,287; Right/Down reachedVermilion1305,288. No ROM change required. Do not report this as confirmed recurring black-screen failure.
Native Save completed in private fixture; fresh pure candidate Continue without emulator state restore retained map54,1305,288,party3 and both actual trainer defeat flags. Evidence build/0029-final-traversal-reload-v1/verified.json and pure-continue-vermilion.png. Original owner save untouched. Ledger includes actual inputs; failed input-name9 lookup happened before core invocation and did not write ledger, then corrected mapping and reran.
Next: final native audiovisual recording, verify recording endpoint/real audio, package cumulative0029 patch/ROM locally and publish no ROM/source. 0029 remains PRIVATE,0028 latest release. FullKanto objective incomplete. Stream URL unchanged, prior live preview fixture remains paused between tests; this traversal ran isolated smoke core.

## October 13 — final recording/package prepared and live tunnel restored
Native50second audiovisual recording build/0029-release-recording-v1/prototype-0029-boundary-audio.mp4 runs fresh purecandidate Continue from copied native traversal save, then crosses54->14->54->14->54 with ordinary inputs. RAM timeline confirms crossings; native44100stereoPCM nonzero, pitch-preserving0.385% clock correction, encoded AV durations49.978187/49.980998seconds. Horizontal topLEFT/bottomRIGHT option added to tools/record_emulator_test.py, actualthumbnail inspected. This is prepared-save functional evidence, not campaign difficulty. No RAMwrites or emulatorstate restore.
Private package build/0029-release-package-v1 contains named0029ROM, cumulative xdelta, ZIP and manifest. PristinebaseSHA checked, xdelta roundtrip reconstructs exact candidateSHA e10c99766c73e7c458632bd7d9a17ee97bfe10231b33a727294c62eafaf08d76, ZIP memberSHA matches. PatchSHA dc3202131079aecfe735b05e80145319001c925a037a3a5de75b7a8ad0369686. Patching page/browser validation/publication remains pending; do not call0029published yet.
Previous live backend absent (localhostconnectionrefused); previous cloudflared process absent and oldURLDNS failed. Started finalPUREcandidate copiedsave backend session84194 /build/0029-live-final-release-v1, port8080. Actual live54->14->54 ordinary walk/stereoaudio verified build/0029-live-final-crossings-v1/verified.json; paused viafinally. That local test happened before remote tunnel recovery, so don'tclaimownerremoteviewing duringit.
Restored tunnel PID3881 /build/0029-tunnel-refresh-v2. Newpublicorigin https://standings-scholarship-arnold-winners.trycloudflare.com . Remote page200, can_control=false, publiccontrolPOST403. Newviewlinkpostedchat and GitHubplainlog link-onlycommit1339d357278a3b4b230858b947cf0bd2f5d95c93; fetchedverification. Privatecontrolcredential neverpublished. Backend/tunnel remainconnected, feedpaused. Next actual playtest mustdisplayviaworkingremoteURL perupdatedowner rule.
Currenthandoffrules revised byowner and clarifiedstreamwording withauthorization. PreservelatesthumanJohtoHMexception, nativeinteriors, introduction/naming, Kanto-first/fullgoal. 0028 stilllatestrelease;fullcampaignincomplete.

## October 13 — prototype0029 patch page and recording published
Published ONLY authorized patchpage, license, manifest, audiovisualrecordingpage and plain-language release announcement. Commits pagecf7eae6cab46e614859ab6467edc5002811543ee/licensed9807f76edfe49f48430c682e56080283b532d73/manifestb4d07dbe83b51fdc0a0f00f272f1175a0a05e2d7/recordingba8823af10489b22d0965820a6d709fe47cb7077. NoROM/save/sourcepush.
Patch URL https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0029/index.html
Recording URL https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/prototype-0029.html
build/0029-release-package-v1/browser-decoder-verified.json executes ACTUAL embedded pageworker inNode VM withWebCrypto: incorrectsize/checksumreject; pristinebaseoutputs exactSHA e10c99766c73e7c458632bd7d9a17ee97bfe10231b33a727294c62eafaf08d76. This is JavaScriptdecodervalidation, not UIfilechoosercoverage. Published rawGitHub page/license/manifest/recording exactmatch local ignoringterminalnewline, publication-verified.json.
Actual in-appbrowser openedgithackexternalcontentnotice thenpatchpage, shows0029title/input/disabledcreatebutton/correctscope/link; recordingDOMvideo readyState4,duration49.980998,1024x768,noerror. NoROMprovidedthroughbrowserchooser. Toolread chunksfirstattemptfailedbecausebytesvscharacters; noexternalwriteoccurredonfailedread, correctedcharacterbounds andexactchunklengthvalidated.
Next checkpoint0030: audit nativeVermilion Yellow events/interiors/encounters/progression and planconversion; fullKantoobjective remainsincomplete. Preserve0029outputs; newbuildpaths only. Ownerstream rule applies throughoutactualplaytests, controlsprivate, pausebetween. CurrentstreamURLunchangedfromlatestrestoration.

## October 13 — Vermilion audit and native Bike Voucher reward progress
Read currenthandoff/log; previousgoalturn wasprogress (0029patch/recordingpublished). Latest0030plan yellow-heartgold/PROTOTYPE-0030-PLAN.md. NativeROMaudit build/0030-vermilion-audit-v1/native-inventory.json inventories54/358..365 actors/warps/scriptbanks. Yellowread-onlysources confirmchairman BikeVoucher120, cityOfficerJenny/Squirtle, OldRod house, trade/Pidgey houses, S.S.Anne ticket/departure and Cut/gym dependencies. Do notsubstituteHG S.S.Aqua/postgamegating forYellowcampaign.
Newmodule tools/vermilion_fan_club.py changes ONLYchairmanscript0 and appendsYellowmessages inmap362. Originalroommatrix/events/actors/warps/init andotheroriginalscriptcode retained. Originalscriptbank clonedwithfirstentryredirectedtoappendedcode, soallnativeinternalrelativebranches retainoffsets. v1repackedbankchangedalignmentpadding; preservationtestcaughtit. REJECTv1; v2correctsstrategy ratherthanweakeningtest.
Privatecandidate build/0030-fan-club-voucher-v2/private-fan-club.nds SHA57b9a890cb63fda584fb8b30913a2c62c1514707771cdd02168f683d5d1f47b1, basedreleased0029. Newpersistentrewardflag0xA9E, belowdaily0xAA0. Read-onlynativeC/s/h/inc search foundonlydefinitionFLAG_UNK_A9E; priorprojecttools/testsnoallocation. No savedvariableallocation. Awarditem first, setflag onlysuccess, no/BagFullretry, repeatnogrant. No customtextlist assumed; suppliedYellowstoryused, repeatgenerictrainer avoidsuninitializedPlayerbuffer. Pokemonphoto/Printer andPikachu/Seel customstarter behavior deferred; otherFanClubNPCs stillnativependingconversion.
THREE meaningful tests PASS test_vermilion_fan_club.py: actualcompiledvoucher->CeruleanBicycleexchange/repeat,decline/fullbagretry, allothermapheaders/ROMfiles/originalarchiveprefixes/nativecode/textpreserved. These arecompiledscriptmodelchecks, notnativeSaveContinue/exchangeproof.
Actualnative reward successfully exercised LIVE onworkingremotetunnel: initialmap362,14,6 onlytransportfromcopiedRoute25ownerSave, no grants. Fixture build/0030-fan-club-native-fixture-v1. Livebackend session82988 /build/0030-live-fan-club-v1. Readsourcechairmanstory, choseYes, receivedBIKEVOUCHER (native-bike-voucher-received.jpg), explanationandactualrepeatHello trainer (after-voucher-8.jpg). NativeSave/Continue, Bagquantity, nativeCeruleanexchange anddecline/fullbag remainpending; originalsaveuntouched. No0030release.
BeforetestremoteviewURLverifiedpage200/control403/can_controlfalse. FeedONthroughactualnativeinputs andpausedaftertest, backend/tunnelretainedcurrentURL. Newrulefollowed; noURLchange. Usecurrentprivatecontrolfile only. Fieldcurrentlyinrepeatdialogue. NextnativeSaveContinue andvoucherexchange, thenremainingVermilioncampaignwork. NoROM/sourcepublication.

## October 13 — native Voucher persistence and Bicycle exchange verified
ActualnativeFanClubreward Save/Continue nowPASS: livefixturev3 had earnedVoucher, normalSavecompletedwithscreenclosed (save-completed-final.jpg), enginegracefullyclosedandcopiedDSV SHAa1e22f0cd1ddfcedc541019c7968b40121c1dfa440aec4966a2d23028647a335. Purecandidate freshContinue inbuild/0030-live-pure-continue-v3 loaded362,14,6/party3 andchairmanrepeatHello trainer, demonstrating savedone-timereward. Noemulatorstatetransfer. Originalownerfilesunchanged.
Importanttestcorrections: livev1 didn'tacceptoverwriteconfirmation; pureContinuev1 loadedold29. livev2wasstoppedwhileSavingstilldisplayed; pureContinuev2 loadedold29. Bothhelpers timedoutverifiedterminal, notROMfaults. livev3 also initiallypausedatvisibleoverwritequestion becausebuttonsequencetiming; selectedactualvisibleYes viaTouch231,288, waited30s andinspectedfieldreturn beforeSTOP. DoNOTreusefailedSavecopies orclaimearlierSaving screenshotwasfinished. NoROMfixrequired.
Prepared exchangefixture build/0030-exchange-native-fixture-v1 fromactualearnedVoucherDSV, initialtransportONLY362->432,8,7. Helperprepare_0030_exchange.py expandsoriginalscriptheader andpreservesallnativebodybytes/relativeoffsets (genericoldsplit_bank/repack unsafe forout-of-orderentry redirect). Noitem/Pokemon/badge/defeatgrants; fixtureexcludedcandidate.
ActualnativeBikeShopclerkrecognizesVoucher, awardsBicycle, removesVoucher, setsnormalexchangeprogress: native-exchanged-bicycle.jpg saysGOLDexchangedBIKEVOUCHERforaBICYCLE. ThisusesexistingCeruleanclerkmodule, notnewscriptmodelonly. Separate quantityRAMcheck andexchangeSaveContinue remainpending, so don'tclaimthose. verified-chain.json recordsUIevidence/provenance/map432/party3/nonzero44100audio. Allactualtestinputs displayedlive; pausevideo/audioafterchecks, serverandtunnelstillconnectedcurrentURL.
Currentlivebackend session66834, sourceexchangeprivatefixture/folder0030-live-exchange-v1, inBikeShoprewarddialogue. No0030release; privatecandidateunchangedvoucher-v2 SHA57b9a890cb63fda584fb8b30913a2c62c1514707771cdd02168f683d5d1f47b1. Latestrelease0029.
Additionalread-onlyaudit: HGOldRodhouse361 scripts781 onlysimpleNPCmessages, nogift. YellowexplicitlyoffersOldRodwithyes/refusal/fullbag/repeat. Nativeitem445 andsharedOldRodflag0x75; auditcompatiblegiftbeforeinstalling. Next remainingVermilionnativeinteriors/NPCs/OldRod/trade/Squirtle/ship/gym plan inPROTOTYPE-0030-PLAN.md; fullKantoobjectiveincomplete.

Audioverification initially sampled silence while item-receipt/jingle dialogue was still open andasserted; noverified-chain file written then. Closednativeexchange dialogue withordinaryBinputs, repeatedcheckPASS withnonzero44100PCM, verified-chain.json nowexists andfeedpaused. Noaudio/ROMcodechange required. Publicplainlog appendedaccurate0030rewardprogress viaGitHubconnector; noROM/sourcepublished.

## October 13 — Old Rod gift implemented and native refusal/acceptance/repeat checked
Newmodule tools/vermilion_old_rod.py patchesmap361 ONLYfishingguru entry0/textappend. Nativeinterior/events/actors/warps/init554 unchanged, alloriginalscriptcodebody preserved atsameoffsets; clonedbankfirstentryredirectsappendedcode. Item445OLDROD, Kanto rewardflag0xA9F. NativeC/s/h/inc andprojectsearchfoundonlynativeFLAG_UNK_A9Fdefinition, noprioruses. Thisislastunusedpersistentflagbelowdaily0xAA0; DO NOTallocatefutureprogressiondailyflags. JohtoFLAG_GOT_OLD_ROD0x75/script233 remainunchanged. ExistinginventoryOLDROD skipsduplicatewithoutrewritingJohtoflags; awardsetsKantoflagonlyonsuccess.
Nativeplayernamebuffer190/u8slot0 usedbeforeYellowmessages, so receipt/repeat correctlysayGOLD. SourceYellowVermilionOldRodHouse.asm SHA f5ebbeccc2159bb8479bcf9004dfca6b520a1635bbf64b58295ffa8bb16d1522. Privatecandidate build/0030-old-rod-v1/private-old-rod.nds SHA6da1de306d3157653fd3594ed42870d161ca7324e6a39edd50f5abb962fc97c9, derivedvalidatedFanClubvoucher-v2. Original0029/recovery/savespreserved. No0030release.
SIX focusedchecksPASS test_vermilion_old_rod.py +test_vermilion_fan_club.py: award/existingownership/repeat, No/fullbagretry, unrelatedflags includingJohto0x75 unchanged; allotherheaders/files/originalarchiveprefixes/nativebody preserved. Compiledfullbagcase only, notnativefullbagyet.
ActualLIVEfixture build/0030-old-rod-native-fixture-v1 initialtransportONLY362->361,5,6, usingcopiedearnedVoucherSave (sameSHAa1e22f0...). NoRod/item/badge/Pokemongrants. Safeheader-expansionhelperderivedprepare_0030_exchange retainsnativebodybytes evenout-of-orderchairmanentry. Backendsession75770 /build/0030-live-old-rod-v1. NativeNo refusal capturednative-rod-declined.jpg, same-save reoffer rod-reoffer.jpg, choseYes/receipt GOLDreceivedOLDROD rod-native-receipt.jpg, normalrepeat Hello there,GOLD rod-repeat-greeting.jpg. No countRAM/save/fishingclaimyet; nativeRodSaveContinue/fishing/fullbagremainpending.
Remotetunnelbeforetestverifiedpage200/can_controlfalse/POSTcontrol403, URLunchanged. FeedONthroughallactualinputs, thenclosedrepeatdialogueandpausedvideo/audio, backend/tunnelretained. Next nativeSave/Continue andOldRodfishingfromearneditem; ensureVermilionrodencountersmatchYellow (currentcustomRodhooksareRoute6map14only). OthercityNPCs/signs/terrain/houses/Squirtle/ship/gymremainunfinished. FullKantoobjectiveactive.

Clarification: A9F islastaddressbeforepersistent/dailyboundary, notproofthatallotherpersistentflagsareoccupied. Auditanyfutureallocation; neveruseAA0dailyflagsforcampaignprogress. PublicplainlogupdatedwithnativeOldRodprogress; noROM/sourcepublished.

## October 13 — earned Old Rod Save/Continue passes; Vermilion fishing audited
NormalSave onliveOldRodfixture: openedSave, inspectedactualoverwriteYes menu, selectedTouch231,288 andwaited30s. rod-save-finished.jpg showsfieldreturned, notSaving. Gracefulcoreclose, copiedsavedDSV tobuild/0030-live-rod-pure-continue-v1, bootedPUREoldrod-v1 candidate withouttransport/emulatorstate. NativeContinue loaded361,5,6/party3; actualrod-repeat-after-continue.jpg saysHello there,GOLD, retainingcompletedgift behavior. DirectBagquantity andactualfishingwiththisRod remainpending; repeatbranchchecksflagORinventory so thisisbehavioralpersistenceproof, notseparateRAMflagproof. OriginalownerSaveuntouched. Backendsession51300, purecandidateSavefolderabove. Actualinputsdisplayedlive, dialogueclosedthenpicture/soundpaused, URLunchanged/tunnelretained.
Vermilionfishing sourceaudit build/0030-vermilion-fishing-audit-v1/audit.json: nativewildmember98/196bytes. YellowSuperRod fourequiprobableslots Tentacool15/20/10,Horsea5; OldMagikarp5; GoodGoldeen10/Poliwag10 equally. SourceSuperRodSHA82e43c053995080f23f70a72150c6a4f9d7e03183ec87898129567b996240c65. NoROMfishingchangesyet.
Nativeoverlay2nighthelper02246AD4 callsRTC andunconditionallyreplacesGoodslot3/Superslot1 withsharedspeciesfield0xC0 atnight. A singlefieldcannotbothretainGoodGoldeen andSuperTentacool. Actualcallsite02247064 unique. ExistingRoute6Supermarkerhook01FFFD38 at0224708A, swarmhook01FFFD80 at02247070; slotselectoralreadyhandlesprivateSupertag3 withfourequalchoices. RemainingITCM152bytes (32616used). DoNOTblindlysetnightfield0 orreuseRoute6tableforVermilion.
Potentialscopeddesign: appendonlymap54wildrecord, wrapexistingSupermarker/swarm toadd54 whilefallingthroughoriginalRoute6hooks, reuseequalSuperselector. Nighthelperneedsstablemap54identification; noexisting196byteARCtablehas0xFFFF atC0, so uniqueprivate-sentinel innew54table plusnative-helperwrapper iscandidate approach. Validateallothermaps/nighttables/ABI/codebudget/DSinstructionset andsourcebounds beforeaccepting. Noimplementationclaimed. ActualRodfishing remainsnextindependentcheck aftercorrecttable. FullKantoobjectiveactive; latestrelease0029, latestprivatecandidateunchangedoldrod-v1 SHA6da1de306d3157653fd3594ed42870d161ca7324e6a39edd50f5abb962fc97c9.

## October 13 — Vermilion fishing candidate and reported gatehouse visibility regression
Current private 0030 candidate: build/0030-gate-visibility-v1/private-gate-visibility.nds SHA256 936d9feb5b5bae6741f70d6509069b005735120e0f5db313b372a4280da044e9. Includes Fan Club, Old Rod and private Vermilion fishing work. Latest release remains 0029; no 0030 release yet.
Fishing module tools/vermilion_fishing.py appends map54 encounter record154, wraps existing Route6 Super Rod/swarm hooks, and bypasses native night substitution only for the new table's unique 0xFFFF sentinel. Old Magikarp5, Good Goldeen10/Poliwag10 equally, Super four equal Tentacool15/20/10,Horsea5. Five meaningful native Unicorn/preservation tests PASS (18.32s), covering all map/rod markers, original night tables, RNG odds, ABI and scope. Native live fishing with actually earned Rod showed Not even a nibble and The Pokemon got away; no wild fishing encounter or catch verified yet. Do not claim gameplay fishing complete. Bag shows earned Old Rod after normal Save/Continue. First long test run deliberately stopped after identifying redundant repeated ROM parsing; cached baseline and reran unchanged coverage successfully.
Owner reported released0029 gatehouse north of Vermilion invisible while doorway still active; requested fix in next prototype. Audit found Route6 model list105 includes gate model342; Vermilion list10 does not. Both prop texture payloads are byte-identical and list105 preserves every Vermilion model. New tools/vermilion_gate_visibility.py clones ONLY Vermilion area record to use compatible list105. All original archives, interiors, events, warps, scripts, terrain, other headers and other files preserved; build/0030-gate-visibility-v1/report.json records passing preservation checks. Do not overwrite released0029.
Native live close-up test using copied earned-Rod save and initial transport ONLY to map54 coordinates1302,263: gate exterior rendered, ordinary Up entered native gatehouse389 (5,12), ordinary Down returned to Route6 and exterior remained visible. Screenshots build/0030-live-gate-visibility-v2/gate-visible-exterior.jpg, gate-native-interior.jpg, gate-visible-after-exit.jpg. This specifically tests Vermilion's loaded model list plus actual doorway/exit; complete continuous city-to-gate path still needs final traversal in release checks. Earlier city-start attempt at1305,288 reached Route6 banner but stopped against path/fence; not a completed gate walk. No emulator state or item grants. Native HG interior retained.
Current backend session13160, build/0030-live-gate-visibility-v2, private gate fixture. Stream picture/audio paused after actual live checks; server and existing standings-scholarship-arnold-winners tunnel kept connected. No changed viewing URL. Next: complete Vermilion work, remaining fishing gameplay and complete city-to-gate traversal, then release checks and recording. Full Kanto campaign remains incomplete.

## October 13 — Yellow Vermilion house speakers implemented, native checks pending
Read-only Yellow source audit: VermilionTradeHouse has NO trade in Yellow; its gentleman gives TeachingHMsText. Do not invent a Farfetch'd trade based on Red/Blue. VermilionPidgeyHouse contains youngster, Pidgey with cry and letter addressed to PIPPI describing Saffron Rocket trouble. Map363 native HG has two speakers; mapped to youngster sprite315 and native Pidgey444, keeping actor IDs, positions, movement and all other fields. Map364 native speaker receives Yellow HM advice. Letter interaction still pending; do not call house complete.
New tools/vermilion_houses.py appends source-backed messages and replaces only the existing entry pointers with appended scripts. Existing script bytes after header unchanged; message prefixes unchanged; original archives retained. Native room geometry, matrix, warps, init scripts and all other maps/resources unchanged. Pidgey script uses native PlayCry76 species16/argument0 followed by WaitCry77. No progression flags or save allocations.
Candidate build/0030-houses-v2/private-houses.nds SHA256 e365186c393d50c79c9e1ed3b98b5cd4a957bd38bb3a65b0f22925ffa805d39b. Removed Game Boy wrap artifact care- fully -> carefully. v1 preserved locally but superseded. Build assertions check all unrelated files/headers/ITCM/overlays, original archive prefixes, native script bodies, retained text and actor/warp scope. Native speaker/cry/letter tests pending. New source audit/build provenance in v2/report.json. Current live backend unchanged13160, gate fixture; video/audio remain paused and tunnel retained. Owner requested gate-exit screenshot; shown directly in chat from gate-visible-after-exit.jpg.

## October 13 — Pidgey-house dialogue exercised live
Native copied-save fixture build/0030-house-native-fixture-v1 derives houses-v2 candidate and initial-transports only from361 to363 (2,5). Current backend98431, folder0030-live-houses-v1. Actual youngster text observed (youngster-text.jpg and youngster-text-end.jpg), then ordinary movement and A interacted with Pidgey and displayed PIDGEY: Kurukkoo! (pidgey-text.jpg). Native cry opcodes are present and preservation assertions pass, but isolated audible cry confirmation remains pending. No grants/save-state transfer. Original room geometry retained. Letter and native HM-advice interaction still pending. Feed paused after checks; server/tunnel retained. User reported Markdown gate screenshot did not display; re-emitted actual image using view_image/image tool directly, not only UNC Markdown.
Native table audit: map363 matrix95, land213, model94 at6.5,5.5; solid tabletop cells6/7,5/6. Other prop models/positions in audit_0030_house_table.py output. No table/letter changes made yet. Preserve existing room, props and collision; add source-backed letter interaction with visible paper only after rendering and placement verified.

## October 13 — PIPPI letter and HM advice verified in native game
New tools/vermilion_letter.py appends Yellow's original three-paragraph letter to map363, adds A-button background events to the existing table's four solid tiles (6/7,5/6), and adds ONLY a small untextured paper/ink mesh to a cloned room land. Existing room model dictionaries, original display-list commands, props, collision, furniture and doors retained; no room redesign. Mesh uses existing append_mesh helper, paper height20.1 rendered correctly on native table. Original archive members retained. Script header expanded by4bytes for third entry; all original script body bytes and relative branches retained, first two entry pointers shifted correctly. No new flags/save variables/rewards.
Current private candidate build/0030-letter-v1/private-letter.nds SHA2565052d5c107d40a7de0c3a2d362b60482fcb70ce112cb680ad17198a3b6bad887 includes gifts, Vermilion fishing tables, gate visibility and both house speakers. Latest release remains0029. Build report/source SHA and meaningful preservation assertions in build/0030-letter-v1/report.json and build/build_0030_letter.py. All unrelated files/maps/ITCM, original archive prefixes, room props/collision/tail, native actors and warps unchanged. New mesh modifies cloned model only; do not claim the entire room model byte-identical.
Actual native letter check LIVE using copied earned-Rod save and initial transport ONLY361->363(6,4,Down): build/0030-letter-native-fixture-v1, livefolder0030-live-letter-v1. letter-room.jpg shows visible paper on native table. letter-page1.jpg DearPIPPI, letter-page2.jpg SaffronTEAMROCKET, letter-page3.jpg Vermilionsafe. Normal closure captured letter-closed.jpg. No emulator states or item grants. Existing youngster/Pidgey interaction already tested on houses-v2; isolated cry audio confirmation still pending, do not claim confirmed sound from compiled opcodes alone.
Native southern-house HM advice check LIVE on copy fixture0030-hm-advice-fixture-v1, transportONLY361->364(5,6,Up), same currentcandidate. Actual all text pages captured in0030-live-hm-advice-v1/hm-advice-page1.jpg, page1-end.jpg, page2.jpg; normal closure hm-advice-closed.jpg. Native furniture/room preserved. No in-game trade in Yellow's house; its original source gives HM advice.
Current backend session82369, folder0030-live-hm-advice-v1, inhouse364 withdialogueclosed. Video/audio paused between tests; serverandtunnel retained. Remote unchanged viewing URL verified page200/can_controlfalse/publicPOST403 via verify_0029_tunnel_v2.py. No source/ROM publication. Remaining city outdoorNPC/sign/layout/services/Squirtle/S.S.Anne/gym progression plus fishing gameplay, fullcity-to-gatewalk and final release checks still required. Full Kanto campaign incomplete.

## October 13 — Vermilion Mart dialogue candidate and service audit
Read-only Yellow Mart source confirms exact inventory PokeBall, SuperPotion, IceHeal, Awakening, ParlyzHeal, Repel. Native Mart script777 entry0 uses standard badge-dependent stock; entry1 uses special catalog14 (AirMail/NestBall/DuskBall/QuickBall). Neither is Yellow stock. Inventory conversion remains mandatory/pending, do not call shop finished. Native source scrcmd_mart.c has30special catalog pointers at0210FA3C, native SpecialMartBuy indexes directly; do not overwrite a shared Johto catalog. Remaining ITCM56bytes imposes code/data budget; audit scoped native callsite before adding catalog/hook.
New tools/vermilion_mart_dialogue.py replaces ONLY map360 entries2/3 with Yellow's original customer conversations, appending messages/native scripts. Both clerk entry pointers, original native body/code offsets, store interior/events/init/warps and all other files/headers preserved. Candidate build/0030-mart-dialogue-v1/private-mart-dialogue.nds SHA2569af9078de259582aeb1432833f112b9c0d30763f6577a6585a32218f05e2729b. Source SHA4750c92584db9c2908c27434ff9db878d0e04cd6fd0bd7c43a2d610bb8d5e86d. Build meaningful preservation assertions PASS; report.json records exact content and pending inventory/native checks.
Actual native male customer conversation reached all three paragraph starts LIVE on copied-save fixture0030-mart-native-fixture-v1 (initialtransportONLY361->3609,5); roaming actor required ordinaryLeft/Up approach. Evidence0030-live-mart-v1/mart-male-text.jpg, mart-rocket-text.jpg, mart-abandon-text.jpg. Female customer native check still pending. No emulator states/grants. Current backend84771, privateMartfixture; feed paused after test while keepingserverandtunnel. Latest release0029.
Read-only PokemonCenter358 inventory: nurse0 at8,11 script1; native staff common9017/9003/9001 retained; local NPCs4/5/6 scripts2/3/4 at4,17 /5,13 /15,12. Yellow center source includes guru training advice, sailor saying poison caused fainting while walking and Chansey. The poison statement assumes Gen1 behavior; verify current engine behavior before copying a false statement or changing shared Johto mechanics. Center conversion and services still pending. Full Kanto campaign incomplete.

Inspected mart-text-closed.jpg after writing checkpoint: normal field/menu returned, so male dialogue closure is verified. Female dialogue still needs native testing. This supersedes pending male closure wording.

## October 13 — shop-plan baseline clarified; native catalog checkpoint
Owner wants both HG vendors retained: northern sells ball-category stock, southern sells general supplies; combined inventory matches each original Yellow town. This is a baseline for a new plan still being explained. Viridian baseline: north PokeBall; south Potion/Antidote/ParlyzHeal/BurnHeal. Vermilion baseline: north PokeBall; south SuperPotion/IceHeal/Awakening/ParlyzHeal/Repel. Do not invent extra ball tiers/badge progression. Current private stock candidate does NOT yet satisfy split: all six Vermilion items at primary clerk, native specialty second clerk still retained. Must revise before release.
Private candidate build/0030-mart-stock-v1/private-mart-stock.nds SHAfe2953255159a0759b60db94adc1cc9a4fbe6bafbf3f24b15d40fb6bfec4eb82. Newmodule vermilion_mart_stock.py private catalog30, native lookup hook02048180->01FFFFC8,44bytes,12ITCMbytes remain.124native lookup/register/SP/flag cases PASS; all30original catalogs unchanged. Loader metadata BA0/BA4 relocation exactly44bytes verified; original test scope omitted expected copy-table relocation, corrected with exact delta assertions. Unicorn initially lacked high RAM mapping, corrected to8MiB and reranPASS. No ROM/source publication.
Actual native Buy/Sell checks LIVE on copied save fixture0030-mart-stock-fixture-v1: six Yellow items and prices200/300/250/250/200/350 displayed. Purchased onePokeBall for200, money999999->999799, count995->996. Soldone for100, count996->995, native receipt observed. Existingcopiedsave money/items used, no grants/originalsave changes. Evidence0030-live-mart-stock-v1/yellow-stock-list.jpg, stock-money-after.jpg, sell-pokeball-count.jpg, sale-bag-after.jpg, sale-count-after.jpg. Transactions not saved; do not claimSaveContinue. WrongSellpocket initially choseTM11, nativeunsellablerefusal normal, correctedinput. Currentbackend15213, samefolder; feedpaused/serverandtunnelretained aftertests. Latestrelease0029; fullKantoincomplete.

## October 13 — owner confirms cumulative Kanto Mart rule
Latest owner clarification supersedes earlier town-specific stock and Lavender exclusion: all ordinary Kanto Marts, including Lavender, use the same cumulative stock. Start Yellow Viridian five-item baseline. Each newly earned distinct Kanto badge advances one stage by badge count regardless of acquisition order, adding only missing items from the standard badge-city sequence Pewter/Cerulean/Vermilion/Celadon/Fuchsia/Saffron/Cinnabar/Viridian. Keep existing unlocks; duplicates/rematches/Johto badges do not advance. Northern vendor balls, southern vendor supplies; native interiors/two vendors retained. Pokemon League-area shops excluded. Celadon Department Store explicitly untouched, inventory/prices retained. Which Celadon department catalogs feed stage4 is not specified; defer that choice rather than silently adding TMs, vitamins or unrelated catalogs. Prior private stock candidate is fixed Vermilion catalog, not this new cumulative implementation. Full Kanto goal remains active.

## October 13 — latest owner engineering and shop clarifications
Improve efficiency opportunistically while developing the campaign: reuse shared logic and data, remove demonstrated waste, and address measured bottlenecks encountered in current work. Measure ROM size and runtime behavior separately, compare before/after and run meaningful compatibility/preservation checks. Do not assume smaller ROM means faster gameplay, promise unmeasured gains, delete content based only on apparent nonuse, or expand into an unrelated global rewrite. Preserve native interiors, approved content, original inputs/checkpoints and Johto's protected gameplay/resources. Kanto campaign remains the top priority.
Shared automatic Kanto Mart system approved: participating shops select common cumulative stock from distinct Kanto badge count when opened, rather than separately updating each shop after each badge. Apply to Vermilion first and connect other regular Kanto Marts as work progresses; Lavender included. Keep northern ball vendor/southern general-supplies vendor. Every Johto shop/service retains HeartGold inventories and prices. Celadon Department Store and Pokemon League shops remain present with HeartGold inventories/prices; excluded only from this new progression system. Shop exclusion NEVER means removing those facilities.
Never offer Master Balls or Cherish Balls in any newly authored shop stock or cumulative tier. Their presence in copied test-save Bags is not shop availability. Keep native excluded shops unmodified; audit and report any actual conflicting stock rather than broad speculative changes. No new ball tiers beyond specified source inventories.

## October 13 — shared cumulative shop data and Kanto badge counter
New tools/kanto_mart_inventory.py and data/kanto-mart-inventory.json generate one source-backed cumulative inventory shared by participating Marts. Actual native badge numbering confirmed in HGconstants/badge.h: Kanto bits8..15; Johto bits0..7. Native standardMartBuy countsall16, so it cannot be used unchanged. badge_count_script emits nativeSetVar41/CheckBadge294/AddVar39 to countonly8Kantobits into temporary8004, using800Ctemporary; no persistent allocations. New5meaningfultestsPASS in0.290sec, including all65536profilemasks and compiledscript-model execution for eachmask. These aredata/script-model checks, NOT native in-game shared-system proof.
Initial cumulative vendor-split tables:0badgesViridian fiveitems;1addsEscapeRope/Awakening;2addsRepel;3addsSuperPotion/IceHeal. BallvendoronlyPokeBall throughtheseinitialtiers, generalvendorremainingstock. Monotonicstock/sourcefidelity/exclusions/MasterBall/CherishBall rejection covered. Later-tier test explicitly uses Celadon2Fgeneralcatalog as a TESTpolicy, not ownerapproval. Productiondata stopsafter3badges and rejectsunresolvedtier4+ rather than inventingstock. Ownerasked viaasyncwhichCeladoncatalogstoadd atfourthbadge: generalballs/supplies only vsallDepartmentStorestock. Questionpending; independentcitywork cancontinue. CeladonstoreitselfremainsHGunchanged.
Native runtime connection pending. Do not releasefixedstock0030candidateasnewsharedsystem. ARM9spaceaudit: primarysection02000000 length1120352, staticBSS02111860..021E5900; cannot blindlyappendprimarysectiondatawithoutoverlappingglobals. ITCM01FF8000 length32712 =>56bytes available BEFOREfixedshop44bytehook; oldfixedcandidate12bytes. DTCM027E0000 native96bytesdata/32bytesBSS; stack/reservedrange not yet audited, doNOTputcatalogs/codeinunknownRAM. Inlinecatalog/nativecommandadapter remainspossiblefutureapproach, not implemented. Preservepriorcandidates/newpaths. Source andROMprivate, no publicpush.
Currentlivebackendretained15213 fromshopstocktest; picture/soundpausedbetweentests, tunnelunchanged. No new nativegameplay performed thisturn. FullKantocampaign remainsactive; VermilionCityotherNPCs/services/layout/gift/ship/gym plus sharedstocknativeintegration andremainingreleasechecks stillpending.

## October 13 — Vermilion Center advice, native healing and stationary Chansey checked
Current private candidate build/0030-center-v3/private-center.nds SHA27b498bfa97f541ec43cbe5588ff1dc6bb24f7c1ff0bdff53120de4ce29bc380. Module tools/vermilion_center.py changesmap358guru entry1 andChanseyentry3/textappend, actor6sprite542/species113 andmovement0. Native nurseentry0, sailorentry2, alloriginalscriptbodyoffsets/otheractors/events/init/warps/room/ITCM/otherfiles retained. Originalarchivesprefixes unchanged; meaningfulbuildpreservationassertionsPASS. v1crywordhadsourcewrappingChaaan sey -> v2joinChaaansey; v2inheritedchildroaming -> v3stationaryChansey matchesYellowSTAY. No overwritingpreviouscandidates. Fixedshopcandidate retainedbutstillrequiresnewsharedprogressionbefore0030release.
Actualnativeguru allpages +nursecompletedhealingsequence observed LIVE in0030-live-center-v1 fromv2 fixture initialtransportONLY361->3584,18. Evidenceguru-page1.jpg/page1-end.jpg/page2.jpg andnurse-greeting.jpg/healed.jpg/restored.jpg ('restored...fullhealth'); finalfarewellclosedandordinarywalkingresumed. These prove UIcyclecompletion, notseparatepartyHP/PP RAMaudit. Originalsaveuntouched, no grants/emulatorstates. NewstationaryChansey nativegreeting/repeat andreturntofield verified onv3 in0030-live-center-v2/chansey-text.jpg, chansey-interaction-finished.jpg, chansey-repeat.jpg. Nativecry76/WaitCry77 codepresentandinteractionreturnsnormally; isolatedaudiblecrychecknotclaimed. Nursecodev3byteidenticalv2, onlyChanseyactor movementchanges.
NativeHGpoison source ApplyPoisonStep/SurvivePoisoning confirms walkingdamagefloorsat1HP thenhealsstatus; Yellow sailor sayswalkingpoisoncausedfaint. Keepthisunclearmechanic/dialoguechoicepending; don'tsilentlychangeglobalJohto behavior. Centerconversionnotcompleteyet. SharedshopstageCeladonselection/nativeconnectionpending, continueothercitycampaignwork.
Currentbackend97127, folder0030-live-center-v2, privatefixture. Feedpausedafteractualtests/serverandtunnelretained. OwneraskedwhetherCeladonhasseparateMart: read-onlyYellowheaders andHGmapconstants showonlymultifloorDepartmentStore, no separateordinaryMart. Generalshopcounterisinside2F. Priorcountcorrection9shoppinglocations excludesLeague/countsCeladononce; allordinaryparticipatingMartsincludeLavender, excludeCeladonstoreitself.

## October 13 — owner chooses Lavender fourth-badge stock
Owner asked whether Lavender has stock not in previous towns, then confirmed that was the intended direction after the explicit fourth-stage proposal. Lavender replaces Celadon at stage4. Shared data/order now Viridianbaseline -> Pewter/Cerulean/Vermilion/Lavender/Fuchsia/Saffron/Cinnabar/Viridian. All9stage definitions implemented; nativeconnectionstillpending. Fourthbadge addsGreatBall/Revive/SuperRepel; fifthaddsUltraBall/HyperPotion/FullHeal; sixthaddsMaxRepel. Seventh/eighthaddnothing because Cinnabar/Viridian stock alreadycontained; this follows exactcumulativeunion rather than inventingnewitems. Celadon, League andJohto shops unchanged. No remainingCeladonstockselectionblocker. New5checksPASS0.305s coveringevery65536badgemask/scriptmodel, exactallstage additions, vendorpartition, forbiddenitems, monotonicstock/sourceexclusions. Not native shop proof. Builddata9stages; no newROMthischange. LatestprivateROMstill0030-center-v3, release0029.
Independentgift sourceauditstarted: YellowOfficerJenny requiresThunderBadge, offersYes/No, givesSquirtle10, persistentcompletedgift/repeat onlysuccess. GivePokemon source checksAddedToParty aftersuccess, so don'tassumepartyfullmustblockgift; nativeHG GiveMon137 delegates GiveMon andreturnscapacityresult. InspectnativeGiveMon return/storage semantics beforeimplementing; preserveBoxfullretry. ProjectflagsA80..A9FallallocatedexceptcandidateA87; nativeC/s/h searchfoundonlyFLAG_UNK_A87definition, but candidateNARCscript/actorflag andgenericflagloop auditstillneeded beforeallocation. No Jenny flag allocated or gift claimed yet. Sourceobjects showJenny at19,15 inYellow; needfitfaithfulVermilionlayout rather thanrandomplacement.

## October 13 — staged Jenny event, storage fidelity still incomplete
FlagA87 allocation audited: no occurrence evenasrawhalfword in anycandidateNARCscriptmember; noactorflag inanyevenarchive; nativeC/s/h searchonlyFLAG_UNK_A87definition; projecttoolsnoallocation. BelowdailyAA0. Fullaudit/provenance build/0030-jenny-audit-v1/audit.json. Nativecity1305,312permission0600validated, accessible roadnearhouses/harbor; finalYellowexteriorlayoutstillpending.
Newmodule tools/vermilion_jenny.py appendsoneentry/texts/actor19 tocity54, flagA87 onlyonsuccess, ThunderBadgeindex10, Squirtle7level10. Allnativeentrypointersrelocated+4withoriginalbody/relativebranches intact usingappend_bank; allotheractors/events/warps/init/geometry/resources/ITCM unchanged; originalarchivesprefixespreserved. Candidatebuild/0030-jenny-v1/private-jenny.nds SHA7e2b9cd13f690d0ac2c1732439362d28527c207afff726b11efd3a5197bb913e. BuildpreservationassertionsPASS and3compiledscriptmodeltestsPASS: badgegate, species/level/one-time/unrelatedflags, decline/capacityretry. ModelusesnativeGiveMonpartycapacitysemantics, notPCcompletion.
IMPORTANT unfinished: Yellow_GivePokemon sendsfullpartygift tocurrentBox ifspace; HGScrCmd_GiveMon delegatesGiveMon thatONLYParty_AddMon. Currentprivateadapter leavesrewardunconsumedandasksforpartyspace onfailure; thisisTEMPORARY, NOTfinalYellowfidelity. Boxfallback andstoragefullretry requiredBEFORErelease. Jennyusesnativepoliceman34 asexplicitplaceholder; finalJennyartwork/placementrequirescompletion. DoNOTreleaseorcallgiftcomplete. Giftaccepted/persistentSaveContinue andfullcapacitynativechecks stillpending. No sharedstorage/Johto changesmade.
Actualnativepre-Thunderbranch checkedLIVE oncopyofearnedRodsave, initialtransportONLY361->541305,313. No badges/items/Pokemongrants. NativeJennytextaboutmischievousSquirtle observed; partyremained3, badgeoffer/giftnotavailable. Evidence0030-live-jenny-v1/jenny-before-badge.jpg/end.jpg. Currentbackend5216, folder0030-live-jenny-v1; video/audio pausedaftertest, serverandtunnelretained. Existingrelease0029unchanged. FullKantogoalactive. NextnativeBox-capablegiftadapter/finalJennyart, S.S.Annecampaignaccess, sharedshopruntimeandremainingVermilionwork.

## October 13 — owner-approved Jenny party-only gift verified
Owner explicitly replaces Yellow Box delivery with a free-party-slot requirement and exact warning: Oops. You already have a full party with you. Please, come back when you have a free spot? This supersedes ALL earlier Boxfallback/release-blocker notes. New jenny(first) checks nativePartyCount332 >=full6 beforeoffer andbeforeGiveMon; flagA87setONLYsuccessfulGiveMon137. NativeGiveMonfailure remainsretryable. PCstorage never accessed. FourcompiledscriptchecksPASS: exactThunder10/species7level10, one-time/unrelatedflags, No/full retry, fullparty skips offer. BuildpreservationPASS, originalarchiveprefixes/othermaps/nativebodyrelativebranches preserved.
Currentprivatecandidate0030-jenny-v2/private-jenny.nds SHA48a07b4e9f73fce33f7797880b3f7291df8d4b851559858946b5b9d8836726b7. No Box adapter needed anymore. FinalJennyartwork (currentnativepolice34placeholder), othercitylayout/events/sharedshopnativeconnection/ship/gym andreleasechecks stillpending. NativeNo remainscompiled-test-only, notyetactualNo dialoguecheck.
ActualLIVE fullpartyfixture0030-jenny-full-party-fixture-v1 usescopyofearnedOldRodsave plusCONTROLLEDtestThunderBadge and3Pidgey5 tofillparty. Thesegrantsarefixture-only, NOTcandidate oractualGymvictory. Nativeparty6/warning/repeatedwarningverified in0030-live-jenny-full-v1/jenny-full-party.jpg/end/repeat; no reward consumed. ActualLIVEfree-slotfixture0030-jenny-free-slot-fixture-v1 usescopyofsameoriginal3Pokemonparty, testThunderBadgeONLY. Acceptedgift naturallycreatedSquirtle; party3->4, native receipt jenny-squirtle-receipt.jpg, repeat HowisSQUIRTLEdoing?, party-squirtle-level-v2.jpg showsSquirtle10. Originalsuntouched, no emulatorstate transfer.
NormalnativeSave acceptedonisolatedfree-slotcopy, jenny-save-finished.jpg fieldreturnverifiedafter30sec. FreshPUREjenny-v2 candidate loadednormallysavedtestDSV in0030-live-jenny-continue-v1, nofixture scriptsactive. jenny-repeat-after-continue.jpg retainscompletedflagbehavior, nativeparty4; squirtle-after-continue.jpg confirmsSquirtleLv10. TestBadge remainsinthatsavedcopybydesign; notownerprogress. No separateflagRAMclaimrequired, actualrepeatbranchonlyflagA87 provespersistence.
Currentbackend63814, purecandidate, folder0030-live-jenny-continue-v1. Field/partyUIclosed, video/audiopausedafteractualtests/serverandtunnelretained. CurrentviewURLunchanged. Fullgoalactive, latestreleased0029. SourceRoom/Johtopreserved. Futurepurposefulgiftchecks usecorrectnativeTouchPokemon45,265 andSave125,265; earlier279hittransition/cursorwrongly and235enteredPokedex, thosewereinputerrorsnotROMfaults.

## October 13 — restored prototype 0028 patch link and download location
The missing 0028 browser patch page is now published at https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0028/index.html. The actual browser worker reproduces the preserved release SHA256 0de636af251081172fafcfcfee1017c3dd68c15a654ff97b76e7972a68270a52 and rejects wrong-size and wrong-checksum input. Original compressed xdelta was unsuitable for the browser decoder; a new patch without secondary compression was generated in a separate private build directory. Existing releases remain untouched. GitHub plain-language log updated (commit d310724301b5ed3a86513834141333daa9274d39). 0029 remains the newer published checkpoint.
A byte-for-byte ZIP copy now resides at psyduck-yellow/downloads/prototype-0028/Pokemon-Psyduck-Yellow-prototype-0028.zip. The new downloads folder is explicitly ignored; no ROM archive was published. yellow-heartgold retains tools and ignored private build outputs to preserve existing dependencies; psyduck-yellow contains public project pages, notes, and the ignored user-facing local downloads.

## October 13 — Jenny decline and reoffer checked natively
Actual native No path now passes on a fresh copy of the earned Old Rod save with the previously prepared controlled Thunder Badge-only fixture. Live video and audio were enabled throughout ordinary Continue and NPC interaction. Declining showed "Oh... What am I to do now?", returned to the field, and retained party count 3. Speaking to Jenny again reached the gift offer and native Yes/No menu, proving the gift remained available. A second cancellation returned to the field. No gift grants, RAM writes or emulator save-state transfer were used during this test; the eligibility badge is a fixture-only grant, not an actual gym victory or owner progress.
Evidence: yellow-heartgold/build/0030-live-jenny-decline-v1/declined.jpg, decline-field-return.jpg, retry-offer.jpg, retry-yes-no.jpg and retry-decline-field.jpg. This supersedes the earlier native-No-pending statement. Final Jenny artwork/placement and the remaining Vermilion/shared-shop/ship/gym/release work remain pending. Latest release remains 0029; pure private candidate remains 0030-jenny-v2/private-jenny.nds.
Current live backend session 99073 uses the controlled decline fixture in 0030-live-jenny-decline-v1, not the pure candidate. Feed paused between playtests; server and existing tunnel retained. Previous session63814 stopped normally. Uppercase button input was rejected by the control API before delivery, then corrected to lowercase; no ROM change required.

## October 13 — compact shared Mart adapter proven, integration pending
New tools/kanto_mart_inline.py assembles a 40-byte ARMv5 Thumb adapter for SpecialMartBuy at 02048176, resuming at 02048184. It fits inside the existing 44-byte private fixed-stock hook footprint (01FFFFC8); no extra ITCM or unverified global memory required. Authored catalog ID30 reads a u16 byte length plus terminated u16 items inline from native ScriptContext.scriptPtr at +8, advances the pointer, and passes the list to native Mart_Init. Existing IDs0..29 keep native table0210FA3C behavior. Invalid/duplicate/Master/Cherish catalogs are rejected by the builder.
Unicorn native-instruction checks PASS: 240 original lookup register/stack/flag comparisons and 144 custom cases across all9 stages/both vendor lists, with callee-saved/stack and exact script-pointer advance checks. Evidence build/0030-inline-shop-adapter-audit-v1/report.json and adapter.bin. These are native-instruction tests, NOT in-game shop or release proof. Adapter is NOT installed into any ROM yet; latest pure candidate remains0030-jenny-v2.
Native field overlay3 Mart_Init02256D34 invokes stock setup02256CB4 then02256C2C, allocating shop list storage; item-copy/filter loop still needs exact audit before lifetime claims. Other overlays reuse that address and must NOT be interpreted as Mart_Init (initial audit listed those overlaps; follow-up uses ONLYoverlay3).
Important script integration finding: both existing Vermilion vendor scripts call standard2011 for greeting, then set8004 and call standard2052 for buy/sell/cancel menu. Standard2052 lives in commonbank3 and calls SpecialMartBuy from commonentry53. Therefore the inline catalog cannot simply be appended to the map vendor script while retaining the common2052 call: the executing context points into the commonbank, not the map bank. Next implement a LOCAL equivalent native buy/sell/cancel interaction for participating vendors, with inline stock in the actual SpecialMartBuy script context. Preserve global commonbank and excluded shop flows. Do not bypass or remove selling functionality, mutate commonbank3, or claim native integration finished.
No game inputs or save changes this turn. Live backend99073 retains the controlled Jenny decline fixture, feed paused/server+tunnel retained. Released0029 unchanged; originals and Project Recovery untouched. Full Vermilion/shared-stock/ship/gym and campaign remain incomplete.

## October 13 — shared Kanto stock connected to Vermilion and checked natively
New tools/kanto_mart_shared.py connects BOTH native Vermilion vendors to the common nine-stage cumulative source stock. Actor1/entry1 at y4 is the NORTHERN ball vendor; actor0/entry0 at y6 is SOUTHERN general supplies. Local script reproduces native greeting and Buy/Sell/Cancel menu, native MartSell and return/farewell messages. Common bank3/standard2052 unchanged: inline catalogs are in the executing local script, not appended behind an unrelated common call. Each Buy counts only Kanto badge bits8..15, preserving unrelated flags and using temporary8004/8005/800C.
Candidate build/0030-shared-mart-v1/private-shared-mart.nds SHA f21dbfb5dd59781355725b4c766e3ed7dae3ca15078a99414e3897358580d4b8. 40-byte adapter replaces ONLY existing44-byte hook reservation, leaving ITCM size unchanged and12bytes spare. Native14-byte lookup region02048176..02048184 is redirected. Preservation checks PASS: only that ARM9region and map360scriptpointer changed; existing script archive members, commonbank3, other archives/mapheaders, geometry/events/text/native interiors and nonhook executable sections preserved. New appended script1146 redirects entries0/1 and preserves oldbank bytes8..end/otherNPCentries. No released ROM changed.
Two compiled-script checks PASS3.281s: EVERY65536nativebadge mask for BOTHvendor scripts (131072catalog routing cases), exact source stages, and Sell/Cancel paths independent of badges/catalog reads. Earlier adapter instruction cases240native+144custom remainvalid; these model/instruction checks are distinct from actual in-game proof.
ActualLIVE native two-badge copied earnedOldRodsave, initialtransportONLY to360,4,4: northern stockPokeBall200only; purchasemoney999999->999799, Bag995->996; nativeSell onePokeBall offers100, returns995 andmoney999899; Buy andSell return tovendor menu; SeeYa/farewell returnsfield. Southern stockPotion/Antidote/ParlyzHeal/BurnHeal/EscapeRope/Awakening/Repel matches2badge cumulative union. Evidence0030-live-shared-mart-v1/north-stock.jpg,north-quantity.jpg,north-confirm.jpg,sell-balls.jpg,sell-ball-price.jpg,sold-ball.jpg,native-buy-return.jpg,sell-return-menu.jpg,north-field-return.jpg,south-stock-page1.jpg,south-stock-repel.jpg,south-field-return.jpg. ExistingMaster/otherballs inBag are source-save contents, never offered bynewstock.
SeparateCONTROLLEDfixture0030-shared-mart-stage4-fixture-v1 givesKantoBlaine/Giovanni14/15 outoforder to original2Kantobadges andALL8Johtobadges usingnativeGiveBadge295. No item/Pokemon/RAM grants. NativeContinueSaveprofile shows12totalbadges; BOTHshops correctlyselectONLYstage4: ballsPoke/Great(noUltra); suppliesincludeSuperPotion/IceHeal/Revive/SuperRepel whileHyperPotion/FullHeal/MaxRepel remainlocked. Evidence0030-live-shared-mart-stage4-v1/north-stage4.jpg,south-stage4-page1/2.jpg,save-prompt.jpg. This proves Johto badges don'tadvance andorderdoesn'tsubstitutehigherstage. Controlledbadges NOT actualgymvictories/ownerprogress.
NormalSave completedandfieldreturnconfirmedafter30sec(save-finished.jpg). Purecandidate withoutfixture script loadedfreshcopiednormalDSV in0030-live-shared-mart-continue-v2, nativeContinue retainedstage4supplies/fieldreturn(continue-profile.jpg,continued-field.jpg,continued-stage4.jpg,continue-field-return.jpg). No emulatorstate transfer. FirstContinuehelperlookedforjenny-private-fixture.dsv instead ofstock-private-fixture.dsv; stoppedbeforeboot, correctedandusednewv2folder. NoROM/savecompatibilityfailure.
Remaining: native0/5/6/8badge visualchecks, connectotherordinaryKantoMarts asareasprogress, fullVermilionexterior/Jennyart/fishing/ship/gym/gatewalk/release regression. DoNOT release city yet. Currentpurecandidate nowshared-mart-v1. Currentlivebackend33839 usesPUREcandidate withCONTROLLEDmixed-badge copiedDSV (notownerprogress), folder0030-live-shared-mart-continue-v2. Video/audio pausedbetweenplaytests; server/tunnel retained. Earlier backend89683/73262 stoppednormally. CurrentviewURLunchanged.

## October 13 — read-only S.S. Anne map-slot audit
Continued next ship dependency audit on pure0030-shared-mart-v1, without modifying any map/resource/save. Evidence build/0030-ship-map-slots-audit-v1/audit.json inventories eleven unused Sinnoh-labelled slots254..264 and nativeAqua donor maps307/308/309/310/311/328/329/330/386/387. AcrossALL540nativecandidateheaders/eventwarps: zero inboundwarps to254..264. AcrossALLmapmatrices: zero header-cell references. AcrossALLcandidate scriptbankmembers: zero rawWarp176+targetID matches. Available nativeC/H/scriptS sources: zero references to their MAP_FIGHT_AREA_UNUSED_*/MAP_BATTLE_PARK_UNUSED_* symbols. All11slots havezeroactors,matrix0,regionbit0. That bit alone labels them Johto in engine metadata, so doNOTassume it establishes actual Johto playable content; their Sinnohplaceholder provenance/defaultresources and unreachability require explicit preservation reasoning before any reuse. OriginalAqua/Johtomaps/resources muststayunchanged.
This is feasibility evidence ONLY, not installedship content or approval to rewrite protected maps. Available native Recovery snapshot lacks map_headers.h data source; ROMheaders and other available source were audited instead. No newROM produced. Next scope-isolated S.S.Anne clone design/resourceownership audit, including topology, boardingTicket/Cut/departure, Blue/rival/trainers and firstHOFregional gating. Never substitute nativeAqua/postgame progression forYellow. Keep unusedslot uncertainty deferred while independent work continues.
Currentpurecandidate remains0030-shared-mart-v1/private-shared-mart.nds; latestrelease0029. Backend33839 remainspaused betweenplaytests withserver/tunnelretained; no gameplay executed this heartbeat. Fullcity/ship/gym andKantocampaign incomplete.

## October 13 — maximum cumulative Mart stock checked in-game
Actual native maximum-stock playtest PASS on a fresh controlled eight-Kanto-badge fixture from a copy of the original two-Kanto-badge earned Old Rod save. Fixture adds only nativeGiveBadge295 IDs10..15 plus initial transport to360,4,4; it is not owner progress or actual gym victories. No items/Pokemon/RAM grants or emulator state transfer. Pure candidate remains unchanged0030-shared-mart-v1 SHAf21dbfb5dd59781355725b4c766e3ed7dae3ca15078a99414e3897358580d4b8.
Northern vendor displays ONLYPokeBall/GreatBall/UltraBall. Southern threepages display all14cumulative supplies: Potion/Antidote/ParlyzHeal/BurnHeal/EscapeRope/Awakening; Repel/SuperPotion/IceHeal/Revive/SuperRepel/HyperPotion; FullHeal/MaxRepel. NoMaster/CherishBalls or additionalLeague-onlystock. NativeSell/Cancel menu retained; fieldreturnverifiedafterclosing. Evidence0030-live-shared-mart-stage8-v1/north-stage8.jpg,south-stage8-page1/2/3.jpg,stage8-field-return.jpg. Sourcefixturemetadata explicitly recordscontrolled badges in0030-shared-mart-stage8-fixture-v1/fixture.json.
Duringplaytest existingpublictunnel remotelyverifiedHTTP200; publicviewtoken /control403 andcan_controlfalse. URLunchanged. Video/audioONthroughnativeinputs, pausedafterfieldreturn; server/tunnelretained. Currentbackend22232 usesSTAGE8TESTFIXTURE, NOTpurecandidate; previouspurebackend33839 stoppednormally. Livefolder0030-live-shared-mart-stage8-v1. No new release or publicartifact. Latestrelease0029; candidate0030sharedsystemstillrequiresothercity/ship/gym/gatewalk/releasework. Native0/5/6specificvisualprofilesremainunrun; exhaustivecompiledallmaskchecks andnative2/4/8checks nowcompleted. Broaderrepeatedshoptestingnotrequiredwithoutnewfailure/change; continueindependentcampaignwork.

## October 13 — isolated S.S. Anne room copies and captain Cut reward
Proven-unused Sinnoh placeholders254/255 are now used ONLY in an isolated experimental build. Read-only audit showednoinboundwarps/matrixreferences/rawWarp176+IDmatches/source-symboluses, emptyactors/events andunusedSinnoh symbols. Their defaultregion0bit is not playableJohtocontent. NewcloneheaderssetKanto1; every OTHER540-mapheader, including ALL originalAqua/Johtoplayablemaps, remainsbyte-identical. Originalscript/events/matrixarchiveprefixes/resources unchanged; newdata appended. Sharednativegeom/texturesmodels referencedread-only. No originalS.S.Aqua actor/story/event modified. This resolvespriorreuseuncertainty specificallyfortheseemptySinnohplaceholder slots, notgeneralpermissiontoeditJohto.
Moduletools/ss_anne_room_probe.py clones native307hall/308captain geometry into254/255 withONLYpairedwarps49,15<->9,11; removesallnativeactors/backgroundevents/triggers fromnewcopies, usesemptyprivatescripts/init. Candidatebuild/0030-ship-room-probe-v1/private-ship-room-probe.nds SHAe85c53fbbb60445536bda9fd4ac2fd4cdfd43cbe9692f7a76c0521d7224ff870. Preservation PASS: changedheaders254/255ONLY; byteoffsetBB4change is nativecompressionStaticEnd, explicitlyverified==02000000+len(compressedARM9), notunexpectedgameplaychange. Firstscopeassertomittedthatmetadata/rejectedbuild; correctedspecificmetadataassertbeforeaccepting. AllotherARM9/nativeITCM/DTMC/archivepayloads preserved.
ActualLIVE room-copy rendering and two-wayordinarywalking PASS fromcopiedearnedRodsave+initialtransportONLY. Hall25449,14->Down->captain2559,12; Upwalkedinside9,10; Downreturnedhall25449,16. Evidence0030-live-ship-room-probe-v1/copied-hallway.jpg,doorway-test.jpg,inside-copied-cabin.jpg,returned-copied-hallway.jpg. No story/item/badge/RAMgrants. NativeAqua names/mapsec226TEMPORARY; theseareasNOTconnectedtocampaign andMUSTNOTbe released withAqua branding/sharedpreviewtracking. NeeduniqueS.S.Anne location-name/preview/persistenceaudit beforeboardingintegration; native mapsectiondefinitions end234, potentialnew235requiresbound/name/previewaudit.
FlagA7F audit build/0030-captain-flag-audit-v1/audit.json: candidateALLscriptbankrawhalfwordsnoA7F, noactorflags, projecttoolsnoallocation; nativeC/H/S onlyFLAG_UNK_A7Fdefinition. NativeClearDailyFlags startsAA0;A7Fbelowdailybase/non-temp/persistent. Now RESERVE A7F ONLYforKantoCaptainCutGiven. NativeSaveVarsFlagsSet/Clearaddresses/regularSavepreserve semantics reviewed. NoA7Eflagallocated.
Newtools/ss_anne_captain.py authorednativecaptain236at9,4 innew255cabin. Yellowseasick/rubback/thankyou/Cut/repeat/fullbagdialogue adapted; HM01item420quantity1. FlagA7FcommitsONLYnativeAddItem125success; fullbag keepsretryable; repeatawardsnothing. Facingawaywhileinitiallysick, FacePlayer104onlyaftergift. Rubbinganimation/healingmusic NOTimplemented yet; receiptjingle1185native only. SourceRecoveryreadonly. New privatebuild0030-captain-reward-v1/private-captain.nds SHAaee032fb6f50c3a39bb39227f70ea59e9fbad13270c6089204f07c055f8c8e7f. Preservation PASS: new255script/text/event pointers andcompressionmetadataONLY; archivesappend-only; allgeometry/warps/nativeAqua/Johto/shopcode preserved. Two compiled-script-model testsPASS: one-time/exactHM/unrelatedflags andfullbagretry. Nativefullbagnotyetchecked.
ActualLIVE isolatedcaptainreward onfreshcopiedOldRodsave+initialtransportONLYto2559,6. Deskblocksfrontandtrashblocksleft; nointeractionfrominitialposition. OrdinaryDown/left/upapproachreachednativegenerictrashmessage,closedit; walkedaroundrightside to10,4facingleft. Nativecaptainconversationallpages/receipt GOLDreceivedHM01(CUT)! observed(captain-offer-end.jpg), repeatWhew/NowNotSick observed(captain-repeat/end.jpg). NoNativeStorygrants/emulatorstate/RAMwrites. ReceiptcomesfromsuccessfulnativeAddItem; no independentBagquantityauditclaimed. Nativegenerictrashinteraction remainsoutsideauthoredYellowtrash/bookevents; those stillpending.
NormalSavefinishedafter30sec/fieldreturnconfirmed(captain-save-finished.jpg). FreshPUREcaptaincandidateContinue withactuallyearnedsavedcopy retainscompletedCaptainA7Fbehavior(captain-repeat-after-continue/end.jpg). No fixture scriptactiveafterrestart, no savestates. Useroriginalsandreleasedcheckpointsuntouched. Currentbackend96200 PUREexperimentalCaptaincandidate in0030-live-captain-continue-v1; picture/audio pausedafterdialogueclosure,server/tunnelretained. Prior68391/85609 stoppednormally. URLunchanged.
Stableprivatecitycandidate remains0030-shared-mart-v1; experimentalshipbranchnow0030-captain-reward-v1. NextuniqueAnne naming/mapsectionpreviewaudit, faithfulcopied-room topology/morecabins/kitchen/bow, Ticketboarding/Blue/trainers/departure, rubanimation andnativefullbag/Bagchecks. Citylayout/Jennyart/fishing/gatewalk/Gymremainincomplete. Latestrelease0029; doNOTclaim0030city/shipfinished orpublishROM/source.

## October 13 — separate S.S. Anne location name checked natively
Newread-onlyaudit build/0030-ship-name-audit-v1/audit.json proves namebank279 originallyhas235messages (IDs0..234), unusednextindex235isabsentfromALL540mapheaders; S.S.Aqua226existingname retained. NativeBufferLocationName uses messagecountbounds andreadsmsg279 forordinarymapsections; appendedentry235isvalid withoutpatchingthefunction. Newmodule tools/ss_anne_name.py appends S.S.Anne at235 andassignsONLYcloned254/255headers. Existing235decodednames/keyunchanged, allothertextbanks/archives/mapheaders/ITCM/DTMC/gamecodepreserved. Candidate0030-ship-name-v1/private-ship-name.nds SHA7bc9cda699d10739ec2898a922c3a33213f392d9145db6b5b02593c5bf12fbac. Scope/preservation PASS.
ActualnativeContinue withcopyofnormallysavedearnedCaptainCutreward, PUREnewnamecandidate (nofixture script), nativeSaveUI shows S.S.Anne. Screenshot0030-live-ship-name-v1/ss-anne-native-name.jpg. PromptcancelledwithB, no newsaveconfirmed; picture/soundpausedaftercheck. Name-UI proof ONLY; no smallbanner/pokegearworldpositionclaim yet.
IMPORTANT correction topriornotes: NativeMapPreviewGraphic_GetIndex is keyed byMAP_ID, NOTmapsection. NeitheroriginalAqua IDs norunusedclone254/255appearinnativepreviewtable; returnsFF/noart. Existingpreview-visit hook exitsforindex>=25 beforeSavehistoryaccess. Thus clone'spreviousmapsec226didNOTshareAqua fullscreen-previewtracking; earlier concern was an assumption now corrected. Preserveallnativepreviewart; no nativefullscreen ship artwork exists to show or copy. Smallnamebannerentrybehavior still needsdirectnativecheck separately.
WorldMapmetadata auditpending: cloneborrowednativeAqua worldword399F, whilecurrentcity54word000F. DoNOTblindlycopy0coords or assumeAqua positioncorrectinKanto. Need nativePokeGearlookup/bounds/coordinates inspection fornewsection235 beforecampaignconnection/release. Existingnative names/met-locationdefinitions0..234preserved; new235notusedbyexistingmaps.
Currentbackend13756 PUREship-namecandidate withcopiedearnedCutSave, folder0030-live-ship-name-v1; feedpaused/server+tunnelretained. Prior96200 stoppednormally. No newreleasedprototype; latest0029. Stablecitybranchshared-mart-v1; experimentalshipbranchnowship-name-v1. Futurebuilds mustcarrycaptainA7F andnewname235 forward; originals/Johto/Aqua/Recovery remainunchanged. Continue topology/boarding/story work andpendingnativebanner/worldmapchecks; noownerdecisionneeded.

## October 14 — full PKHeX support verification and publication underway
Game development and its recurring automation remain paused while completing the owner's separately authorized full PKHeX and ALM request. Full PKHeX retains its normal editors and games, with an opt-in built-in 0029 profile; no separate narrow editor or profile plugin is substituted. GameVersion.PY=254 is application metadata, Generation IV; Pokemon origin/save ROM codes remain native HG7. Custom starter legality, supported HAs/evolutions, seven custom TMs, charms, project shiny thresholds and Golduck Water/Psychic are scoped to this profile. A type-ID regression found DS type IDs differ from PKHeX's normalized IDs; corrected to MoveType.Psychic/Water before publication. Core positive/negative regressions and full native Windows editor tests pass. Final exported copied DSV loaded through released0029 normal Continue to field; exact bytes matched the active emulator test copy. No RAM/state transfer or owner save modification. Wild/campaign custom encounter catalog remains incomplete; documented explicitly.
Editor source commit28ab2be09f5121504858e9eea420e7b42030b61b published to ThatAnarchyDude/PKHeX-Psyduck-Yellow branch codex/psyduck-yellow-0029-support. Windows release workflow38520080758 running; do not claim binary release delivered until verified. User expressly requires PKHeX publication BEFORE starting ALM implementation; ALM source inspection only, no ALM edits yet. Maintained ALM baseline santacrab2/PKHeX-Plugins90410f2681a0a72680d12280a1e0f14715e67dff matches .NET10/Core26.8.26.
Disk recovery: user manual deletion enabled Ubuntu recovery; 149 approved old local prototype0002..0027 ROMs were subsequently deleted and existence-verified, 19006968424bytes, all301 inventoried saves preserved. fstrim/Ubuntu VHD compaction returned Windows free space to approximately26GB. Recovery/originals/released0028+ and public artifacts preserved. Audit private/cleanup-20261014-v1/verified-report.json.
Stream restored on released0029 with copied editor-validation save in build/0029-pkhex-native-v1. Current backend15064/tunnel46474, video/audio paused after native Continue test, server+tunnel retained. Token-free viewer https://enrolled-ira-opening-five.trycloudflare.com/ published to public log commit48d0074740b2610b54e991ff605833c28fa0fe4d; complete owner viewing link posted in chat. Automatic approval review rejected placing the access token in public GitHub; do not bypass. Control credentials remain private; viewing controls403 verified.
## October 14 — PKHeX published before ALM; compatible full ALM built
Full PKHeX published and independently verified FIRST: https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v1 . Windows workflow38520080758 success; actual public ZIP downloaded/hash-verified93ef09a082794bc35b4415124056b3fa6ec72b79274fe35e23f45f292e636911, no ROMs/saves. ALM modifications began only afterward. Maintained full ALM custom fork now references this custom Core, excludes Core from Costura embedding, retains normal version checks and all12 plugin tools. Custom generation attaches active profile, recognizes starter families and validates every generated result with real host legality. 50 positive traits/species cases,5 negatives,async andordinaryHG Pikachu generation PASS. Exact packaged plugin loaded through REAL PluginLoader using five assemblies extracted from the ACTUAL public PKHeX executable; all12 tools initialized, generated shinyHA Psyduck passed normal editing, oneCoreonly. Upstream lowercase resource path corrected for WSL casing; upstream3 nullable warnings remain. Custom starter generator does not support advanced batch/egg/alpha requests; returnsfailure explicitly. Full custom wild/campaign encounter catalog stillincomplete; no blanketlegal bypass.
Local delivery psyduck-yellow/downloads/ALM-Psyduck-Yellow-0029-v1/ALM-Psyduck-Yellow-0029-v1.zip plus corresponding sourceZIP. No ALM public publication claimed. User's ROM-open error screenshot was diagnosed correctly: PKHeX reads battery saves, not .nds game files. No game development resumed; recurringgameautomation stillpaused. Stream remainsconnected/paused betweenplaytests.
Final delivery verification: ALM plugin ZIP SHA25619801245794bdf77dd1b7c62c5d67c72270329a552f24896de2a19c692b7c908; corresponding full source ZIP37bc887e085ebb8f47383a9cc54feabeb180369c98b26d6d90235f581c113ed0. Exact packaged DLL85522d90e648f03b1d75c4f9d5a7c819f5e4a7d0d93b414dbd05e8d50dc5e032 matched verified ZIP contents. Source contains new project hook and tests; ROM/save/credential exclusion verified. Windows-accessible copies placed in C:/Users/thata/.codex/visualizations/2026/10/12/01a12fa4-99b9-7270-a2f8-828af71c8984/ALM-Psyduck-Yellow-0029-v1/. Public game plain-language log links PKHeX release and explains save-vs-ROM inputs, commit2e3baff4d9183023221e81bc149f672510a01eaa. No public ALM artifact publication claimed. PKHeX-before-ALM ordering complete.
## Approved player-PC storage expansion — October 14
The next game prototype must start the player's item PC at20 usable distinct-item slots, unlocking5 per distinct Kanto badge, maximum60 after8. Johto badges/rematches do not increase capacity. PKHeX imposes NO badge restriction: expose every physical slot supported by the detected game/save layout, including locked in-game rows in the new layout. Preserve0029's existing ten slots and support both save layouts without converting legacy saves silently. The 0029 editor PC tab maps exact saved script variables4152..4165, quantity999, independently from Bag. Do not expand consecutively into4166..416F: initialization and story state occupy those variables. Audit private/pc-layout-candidates.json identifies only45 conservatively unreferenced variables, insufficient for100additional u16 fields; a separate expanded storage layout/native access/migration needs engineering and tests before release. No speculative save offset/flag allocation or expanded-layout support is claimed yet. Build format/version detection only after the game layout is implemented; coordinate PKHeX update and ALM compatibility. Current game campaign automation remainspaused; this approved expansion is mandatory in the next prototype plan.
## October 14 — PC inventory editor update verified, publication pending
PC inventory pouch and ninth Items tab added for0029 saves only. Reads/writes exact legacy variables4152..4165, up to999 items perstack. All10 physical slots exposed regardless of badges. Saving edited nonempty storage sets existing initialization4166 to1 so firstPC login cannot discard edits; evolution/story variables4167..416F preserved. NormalHG/SS bags have noextraPCtab. Core tests verify exactvarmapping, highestslot, fullquantity, bytepreservation outside40PCbytes+2initbytes, badge-independentrows, retailisolation. NativefullWindows form test verifiesPCgrid10rows, previousHA/inventorychecks; copiedrealDSVroundtrip checks pass.
Published source commit568b06d4a16d2a6086e51295c8ac3b14bb8c1cba, workflow38526249274 running, targetpkhex-py0029-v2. Earlier v1 preserved. Do not claimv2binaryreleased untilverified. Expanded60slotnewgame-layout implementation pending nextprototype, not partof0029 physicalsave. Owner clarifiededitorno badgegating andapprovedcoordinatingnextgameprototype/bothlayouts. ExistingALM compatibilitytestrunning againstupdatedhost; noALMAPIchange intended.
## October 14 — PKHeX v2 PC tab delivered
Published https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v2 . Independent Windows workflow38526249274 passed core and full UI tests; public ZIP downloaded and SHA256 verified5bfca01dd0a7f8759b39a92c2e30ade7dbd6fb105fc4c8708853a4d9477e5efc. Actual v2 assemblies extracted privately; existing ALM-v1 single-DLL package loaded all12 tools, generated legalshinyHA Psyduck and retainedresult throughnormalediting, oneCoreonly. No new ALM downloadrequired. Public plain-language log updated commit12199770b86f10fa8108c4976aa45f4f5ba34572. OldPKHeXv1/releasedgame0029 preserved.
Editor PCtab complete for all10currently supported0029slots, badgeindependent. NEXTGAME expanded20+5perKantobadge(max60) remainsmandatorypendingstorageformat/access/migration/nativevalidation; doNOTclaimthatcapacityimplementedor0029has60physicalslots. User approvedcoordinatingnextprototype andsupportbothlayouts. Game automationstillpaused; releasedgameunchanged.
## October 14 — resizable full PKHeX window checked, v3 release pending
Owner requests mainwindow resize/stretch-onmaximize without coveringTaskbar. EnabledstandardSizable border/nativeMaximize button. ExistingDock/anchor/tablelayout panes expand; uppermenusplitPanel1 staysfixedheight. Originalusableouter size setasminimum andsavepanelminimumwidth retained. Nofullscreen, manualScreen.Bounds sizing or taskbaroverlay introduced; nativeWindowsmaximizeworkingareabehavior retained. ActualWindowsform resize/maximize/restore testPASS: expandededitorheight/fillwidth, fixedmenuheight, maxclientrectanglecontainedinScreen.WorkingArea, restoredoriginalclientsize. ExistingHA/PCinventory/retailtestsPASS. Source andworkflow queuedforpkhex-py0029-v3; doNOTclaimreleaseuntilCIandpublicZIPverified. Existinggame0029, PKHeXv1/v2, ALMpackage andownerinputs preserved; gameautomation stillpaused.
## October 14 — resizable PKHeX v3 delivered
Published https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v3 . Source commit91edd91d8e217795aeddb4b820c4efbc10046388. Independent Windows workflow38528890231 passed ALLsteps includingactualmaximizeworkingarea/restore andpreviousstarter/PCtabregressions. PublicZIP downloaded/executable/private-material-exclusion/hash verifiedf933b573737dd3f0fc11ba7818c03b677325d4997427833a37bad7bd8cccf314. Originalv1/v2 retained. No saveformat/CoreAPI/ALM changes; game0029 unchanged andgameautomationpaused. Mainwindowresizable/maximizeenabled, menuheightfixed, originalminimumusablewindow, responsiveexistingpanes. UsesstandardnativeWindowsworkingarea, notfullscreen/Screen.Bounds. Publicplainlanguagelogupdatedwithv3link.
## October 14 — PKHeX v4 whole-interface scaling tested, publication pending
Owner clarifiedv3pane resizingisnot sufficient: fonts, controls, spacing, menus/images mustscaleproportionally. Manualresizingexplicitlyincluded. NewMain.WindowScaling wraps livecontentincenteredviewport, usesuniformmin(width/defaultWidth,height/defaultHeight), scalesfromoriginalcontrol/font/geometry/style snapshots, andretainsnativeWindowsworkingarea. No screenshot-basededitorreplacement. Mainwindowminimumoriginalusablesize retained; restoringoriginalclientsize returns100percent. Nestedmenuicons/padding,backgrounds/PictureBoxzoom, tabdimensions/absolutetablecolumns andsplitpanels scale. Save reload/displaylanguage restorebasebefore rebinding/rezoom; refreshedPokemonpreviewsize usescurrentfactor. Oldfontcacheentriesdisposedafterreplacement toavoidmanualresizeGDIgrowth.
ActualWindowstestsPASSmanualenlargement, exact150percentfont/imageexample, maximizefont/image/menugrowth, taskbarworkingarea, originalsize/font/imagerestore, save reloadwhilemaximized, all12supportedHAediting/PID/shinypreservationwhileenlarged, PCtab/retailisolation. Firstextendedsaverebindtestappearedslowbutfinishedsuccessfully; no reproducedloadfailure. Userreportedv3saveloadingworksgreat. ScreenshotC:/Users/thata/.codex/visualizations/2026/10/12/01a12fa4-99b9-7270-a2f8-828af71c8984/pkhex-v4-maximized.png inspected: populatedliveeditorwithenlargedtext/fields/tabs/boxgraphics. This istesttrainer/controlledPokemon, notownerprogress.
Sourcequeuedforseparatepkhex-py0029-v4release; doNOTclaimpublicationuntilpublicbuild/ZIPverified. Game0029/oldeditorreleases/ALM/API/saveformatsuntouched. Expandednext-gamePCstoragestillpending; gameautomationremainspaused.
## October 14 — PKHeX v4 delivered
Published https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v4 . Sourceb75c4ef07cb58ec161eb17d8d5ef41a378eb525e. Independent Windowsrun38536305224 passedcore/nativeUI/scalingtests andreleasepublication; publicZIPdownload/hash verified398652ceca3d3847894754a6897704e96aeb0a974c9f0dce55c2d0cbd6e73c37. Usermanualresizeclarificationimplemented; v3ownerloadingfeedbackretained. Originalclientminimum retained, uniformfitfactorcenteredforchangedaspectratios, nofullscreen/taskbaroverlay. Full liveediting/150percent/manualresize/SaveLoadWhileEnlarged/restoretests pass. v1/v2/v3 andgame0029 preserved. Publicplain-language loghasv4link. Gameautomationremainspaused; futuregamePCcapacity20to60notimplementedbyeditor.
## October 14 — game resumed; S.S. Anne Kanto map position verified
Owner explicitly resumed game development after the PKHeX work. Existing heartbeat continue-psyduck-yellow-development is ACTIVE again, with approved PC20+5/distinctKantoBadge(max60) and shared ordinary-Kanto-Mart rules retained. No duplicate automation created. Kanto campaign remains priority; latest released game remains0029.
Pinned native source audit pret/pokeheartgold@9d8b7591f09b65804da2fb2dfd56f320633e0d36 confirms interior Pokegear positioning uses explicit header worldMapX/Y, then main-matrix lookup; zero/zero instead falls back to last outdoor spawn. Copied Aqua rooms incorrectly retained25,14. Native Vermilion Center358 uses40,9, and actual candidate main matrix at40,9 is city54. New tools/ss_anne_world_map.py gives ONLY isolatedKanto254/255 this40,9 anchor, preserving move-model bits, uniqueAnne section235 and all other header fields. No Pokegear code or existingJohto/Aqua resources altered.
New private candidate build/0030-ship-world-map-v1/private-ship-world-map.nds SHA25666b8ffb965b4dc62f4a0f2af4c7337d2b88360d7ed5106ab9bc119c502beb905. Build preservation proves other538headers, allNARCs/files/overlays/arm7 andotherARM9sections identical. Three regression checks pass: exactcoordinate/assetpreservation; changedreference rejected; mismatchedmainmatrixlocation rejected. No PC expansion/layout implemented in this checkpoint; that remains mandatory before0030release.
ActualLIVE native Continue with new copied previously earnedCaptainCutDSV in0030-live-ship-world-map-v1 (noinitialtransport/fixture scripts/RAMwrites/savestates this run). Cabin255 Pokegear showsKanto/Vermilion andcorrectplayerposition (kanto-vermilion-position.jpg). Ordinarymovement aroundcaptain desk, throughpairedexit tohall254 passed (hall-field.jpg); hallPokegear alsoKanto/Vermilion (hall-map.jpg). This proves bothnativeworldpositions anddoorway transition; it doesNOTprovefirstentrybanner orfullshipcampaign. No newnormalSaveconfirmed, noowneroriginaledited. Existingcopiedsavecomesfrom prior isolatedearnedCutcheck, notnormalKantocampaigncompletion.
Currentbackend44979 usesPUREship-world-mapcandidate/copiedsave. Prior0029editorvalidationbackend stoppednormally. Existingtunnel46474 stillworks at enrolled-ira-opening-five.trycloudflare.com; authorizedviewing/pausedstate andview-token control403 rechecked. No changedURL, nopublicaccess-token publication. Video/audio enabledthrough actualplaytest, pausedafterUIclosure; server/tunnelretained.
Stablecitybranch remains0030-shared-mart-v1; experimentalshipbranch now0030-ship-world-map-v1. Carry captainA7F, Anne235 andworld40,9 forward. Remaining native smallbanner test, faithfulroomtopology/additionalcabins/kitchen/bow, ticketboarding/Blue/trainers/departure/rubanimation/fullbag checks, citylayout/Jennyfinalart/fishing/gatecontinuouswalk/gym andexpandedPCstorage/savecompatibility remainpending. Do not releaseincomplete0030 orclaimfullcampaign/60slotimplementation.

## October 14 — native S.S. Anne entry banners verified
Current experimental ship candidate build/0030-ship-banner-v1/private-ship-banner.nds SHA25673e98b63a4393357bf0fd3ecd5dcca8747eee1675b7d2d0f04a7daaf126a452c, derived from ship-world-map-v1. New tools/ss_anne_banner.py rewrites only native overlay1 FieldSystem_DrawMapNameAnimation64-byte routine at021EFAF8..021EFB37. Native building suppression is bypassed ONLY for isolated Kanto254/255. Existing icon9/name235 used; ALL map headers, ARM9/ITCM/ARM7, otheroverlays andNARC resources unchanged. Othermaps retain native icon/building gate andsame DrawMapName arguments. GetAreaIcon is a pure header getter; caching its result avoids duplicated lookup and fits64bytes, using zeroadditionalITCM.
Correction to preliminary commentary: native ship icon alreadyexists (9); no icon/header change was needed. Initial candidate assembly append rejected by32KiBITCM guard BEFOREoutput; that approach discarded, no ROM delivered. In-place64byte implementation preserves existingmemory allocation. ABI tests check callee-saved registers/stack; r3 is caller-saved scratch, not required preserved. Tests/test_ss_anne_banner.py: all540actualmapheaders plus48icon/building/boundarycases,1176native-instruction executions, PASS. Build checks prove soleoverlayroutine change withmetadata recomputed; nootherresource/ARM9 change.
ActualLIVE Continue from freshcopied priornormallyearnedCutDSV, nofixture script/RAMwrites/savestate/initialtransport. NativeS.S.Anne banner visibleonContinue (0030-live-ship-banner-v1/field.jpg). Ordinarymovement aroundcaptain desk andexit tohall; first capturehittransitionfade, so shorttimedframecapture usedsubsequently. Repeat hall->captain entry banner visible captain-repeat-entry-14.jpg; repeat captain->hall banner visible hall-repeat-entry-12.jpg. Bothrooms sharesection235 butdoorwayentry stilldisplaysbanner eachtime. No full-screen ship preview art exists; no suchartinvented orclaimed. Nativecaption/fieldreturn pass; broadernamedarea/globalbannercoverage stillrequiresaudit.
Currentbackend67591 PUREship-bannercandidate/copiedsave, previous44979stoppednormally. Existingtunnel46474/URLretainedandremotelychecked; viewtokencontrol403, noerrors, pausedpicture/soundafteractualtests. Originalssaves/Johto/Aqua/Recovery/released0029 untouched. No newnativeSaveconfirmedthisrun. Stablecitycandidate shared-mart-v1 remains; experimentalship nowship-banner-v1. CarrycaptainA7F/name235/world40,9/bannerexceptionforward. Boarding/topology/trainers/Blue/departure/rubanimation, remainingVermilion/gym/fishing/gatecontinuouswalk andexpandedPCstorage/savecompatibility stillpending; doNOTrelease0030 orclaimcampaigncomplete.

## October 14 — Yellow captain-room scenery checked natively
Current experimental ship candidate build/0030-cabin-scenery-v1/private-cabin-scenery.nds SHA256f0ecc51fe51c0ebed0ce98ee23701f7ae706883fde19144f6e411f997a1b318b, derived fromship-banner-v1. Newtools/ss_anne_cabin_scenery.py appends Yellowtrash/seasickness-book text andtwo localread-onlyscripts toclonedcabin255. Nativebin8,4 anddesk9,5/10,5 serveinteractionpoints, all-directionbackgroundevents. Read-onlyYellow sourceRecovery scripts/text/objectsSSAnneCaptainsRoom inspected; originalsneveredited. Exacttrashtext Yuck! Shouldn't have looked! andbook How to Conquer Seasickness... / The CAPTAIN's reading this! preserved.
Buildscopechecks PASS: originalcaptainentry relocated+8withALL originalbody/relativebranches identical; oldmessagekey+fivewords preserved; allpriorarchive members identical; sameactor/warps/coordevents; onlycloned255script/text/event pointerschange; other539headers/geometry/matrices/overlaybanner/ARM7/ITCM/DTCM unchanged. No flags/items/storage writes added, noextracodeallocation. Initialappend_banktuple misuse raisedbefore output andcorrected tobank,count; no invalidROMdelivered.
ActualLIVE freshcopiedpreviousnormallyearnedCutDSV normalContinue, nofixture scripts/transport/RAM/statewrites. Bookfromdeskrightside11,5facingleft: desk-book.jpg andbook-second-page.jpg showbothtextpages, thenordinaryfieldmovementpasses. Binaccessneedsleftapproach7,4facingright becausecaptain/tableblockdirectsouthapproach; earlierdown/uprequests hittablecollision, noteventfailure. Trashtextvisibletrash-yellow.jpg, normalclosuretrash-closed.jpg andsame repeattrash-repeat.jpg PASS. Video/audioenabledforentireplaytest. No newnativeSaveconfirmedthisrun; nooriginalownerprogresschanged.
Currentbackend33191 PUREcabin-scenerycandidate/copiedsave in0030-live-cabin-scenery-v1, previous67591stoppednormally. Existingtunnel46474/URLstillverifiedpaused/noerror/viewtokencontrol403. Feedpausedafterdialogueclosure, connectionretained; no newURLpublicationneeded. Stablecitybranchshared-mart-v1; experimentalship nowcabin-scenery-v1. CarrycaptainA7F/Anne235/world40,9/banners/sceneryforward. Topology/boarding/Blue/trainers/departure/rubmusicanimation/fullbagchecks andVermilion/Gym/PCexpandedlayout remainpending; latestreleased0029 unchanged, doNOTreleaseunfinished0030.

## October 14 — captain recovery sequence completed and checked
Latest private ship candidate: `build/0030-captain-recovery-v1/private-captain-recovery.nds`, SHA256 `fdad314cd9846180bf2cf1cc7bd6218b49f8ab7f76d8919e2e9947021bc9a34b`. It carries forward the ship location, banners, scenery and captain reward. `tools/ss_anne_recovery.py` appends the revised captain script and redirects only entry 0 in cloned cabin255. Scenery entries and their bytecode remain unchanged, as do every earlier archive member, all room geometry/events/text, other map headers, overlays, ARM7 and added ARM9 code sections. Preservation assertions passed. No additional ITCM space used.
Yellow's original captain script plays Music_PkmnHealed after the rubbing text, waits, then permits the captain to face the player. It does not contain a separate player rubbing movement animation; previous generic rub-animation-pending notes were too broad. The revised event plays native HeartGold healing fanfare1183 (SEQ_ME_ASA), waits using WaitFanfare, then FacePlayer and the thanks dialogue. Native healing machinery references this same fanfare in overlay02_02248728. No party healing command or new persistent flag was added. Yellow's separate rubbed-back flag remains a departure-design consideration, not allocated here; departure is still unimplemented.
Three compiled-script regressions pass: one-time reward and unrelated-flag preservation, failed-add retry, and recovery tune/wait/facing order with no repeat tune. Native gameplay used a fresh copied earned Old Rod save and a separate transport-only fixture (`0030-captain-recovery-fixture-v1`), with no item/Pokemon/badge/completion-flag grants or RAM/save-state writes. Initial movement before transport settled was corrected by waiting and walking around the desk; not a ROM failure.
Live evidence in `0030-live-captain-recovery-v1`: rub-rub.jpg; recovery-04.jpg during fanfare; recovery-20.jpg and recovery-39.jpg show the captain facing the player and thanking them; hm-cut-receipt.jpg shows successful HM01 receipt; repeat.jpg and repeat-finished.jpg show the completed-reward branch. Captured 9.68 seconds of nonzero 44.1kHz stereo audio in captain-recovery-live.wav. This proves the normal native sequence and audio output, not an independent acoustic classification of the melody. No new normal Save was confirmed this run; prior reward Save/Continue evidence remains separate. Native full-Bag test is still pending.
Current backend74043 uses the transport-only test fixture, NOT the pure candidate. Previous33191 stopped normally. Existing tunnel46474 and viewing URL retained; remote paused/no-error status and view-token control403 verified. Picture and sound paused after the interaction, connection retained. Originals and released0029 unchanged. Next: remaining ship topology/boarding/Blue/trainers/departure, full-Bag check, outstanding Vermilion/Gym checks and mandatory expanded PC layout. Do not release unfinished0030.

## October 14 — ship doorway requirements audited
Added tools/ss_anne_topology.py and tests/test_ss_anne_topology.py. Read-only extraction from Recovery Yellow object sources records hashes and all ten ship maps in build/0030-ship-topology-v1/topology.json. Seventeen passenger cabins are separate logical nodes even though Yellow groups them into three map files; with seven common areas, the graph has24 nodes. Internal destination anchors, reciprocal map destinations and cabin return identity pass. Adjacent double-door exits correctly share one cabin. All24 nodes are reachable at the source-doorway level. This is NOT native geometry/collision proof: hall connectivity is assumed from original Yellow. Three tests passed, including invalid-anchor and wrong-cabin-return mutations on temporary copies. Recovery untouched; no ROM changed and no playtest performed this checkpoint.
Latest pure candidate remains0030-captain-recovery-v1 (fdad314cd9846180bf2cf1cc7bd6218b49f8ab7f76d8919e2e9947021bc9a34b); latest released0029. Next: map these requirements onto copied native HG interiors, audit available unused non-Johto map slots against current candidate, then verify real doorway arrivals and collision before boarding/story integration. Do not treat grouped cabin map IDs as physically connected. Remaining campaign, PC expansion and release requirements unchanged. Existing feed was not restarted or reverified this checkpoint.

## October 15 — colored Jessie/James assets integrated and seen in native battle
Owner supplied a corrected0029 ROM SHA2561879f2f617427698a467793b5aedf7b59f45827658dcbe28369352af33b3aa4f and reusable sprite ZIP SHA256755d10968b5fd0a8b529703d8422c51d49dc57a53c0e155a036433d600e9c07a. Private copies/extraction: private/uploads/jessie-james-colored-2026-10-15. Bundled instructions/scripts treated as data and not executed. Direct comparison against preserved released0029 proves only NARC a/0/5/8 (file187), members645(animation),646(palette),649(static) changed; allother files/executables unchanged. Five packaged assets exactly match supplied ROM, with647/648 unchanged. Initial filename Folder object identity assertion corrected to serialized FNT equality, no file corruption.
New tools/colored_rockets.py strictly checks original-or-colored wholebundle hashes and applies ownerart. Candidate build/0030-colored-rockets-v1/private-colored-rockets.nds SHA256aad1cdeb56f69bb59d97716d3befe68951a353aa4ea7e71f1dc564b622693395 carries allcurrentprivatechanges, including experimental0030-ship-floors-v1 (84cd520e7569d89a240011af9a80adb145cccef67776efa4d08631304a8db223). Preservation assertions passed: onlythree graphicsmemberschanged, allotherROMfiles/ARM9/ARM7/overlays identical. KEEP these colors in allsubsequentbuilds.
Native isolated battle777 fixture on a fresh copied earnedOldRodsave shows correctcoloredportrait and normal trainerintroduction in0030-live-colored-battle-v2/intro-119.jpg.120timedframes plus30.59s capture/4,923,948bytesnonzero44.1kHzstereoaudio recorded. This is an explicitforcedbattlefixture, NOTordinaryMtMooncampaigntrigger/reward/replay validation; noitem/Pokemon/badge/completionflag grants or RAM/savestates. Initialv1 capturemissedbriefportraitbutloadednormalbattle; repeatedv2capturedportrait. Source save/releasedROMs untouched. No normalSave claimed.
Old WSLserver/tunnel had stopped; oldhostname no longerresolves. Newserver83871 uses battlefixture, tunnel63284 serves https://louisville-voted-worship-examining.trycloudflare.com/ . OwneraccessbearingURL private/current-viewing-url.txt andpostedownerchatonly. Remoteauthenticatedstatus/JPEG verified, viewercontrol403. Publiclog currenttokenfreeURLupdated+datedentry viaGitHub commitb14a3938b8120769a20fcc570f92490d13309125. Userreportednopicwhilefeedpaused; enabledlivevideo/audioandremoteJPEGchecked, userconfirmedAllgood. Feedpausedafterplaytest/server+tunnelretained.
Interruptedpriorfloorwork: tools/ss_anne_floors.py built17cabins/threehalls but is NOTfullywalkableverified. Native307 hasmainhall andisolatedcaptain-sidecomponent connectedvianative329; currentv1 omits thosebridges andmustbefixed. Preliminarygeometryagent-v1 secondcellcollisionwrong: native normal landloader reads extra-header length high16ofwordat16; terrainoffset20+extra (land64432extra,65148extra). Agent-v2 auditcorrectedandparentfinishedhall-components.json:307twointeriorcomponents, all8cabindoorsinmain;329oneconnectedinterior. DO NOTusev1incorrecthallrecommendations. All originalsread-only. Next restorecopiedbridgeconnections, testactualcabins/floors, thenboarding/story/Gym/PCexpansion. Placeholder258auditedin0030-ship-bridge-slot-v1: dummy/unreachableSinnohslot, noinbound/matrix/rawWarp/sourceuses. Latestrelease0029;0030NOTready/published.
PCagent investigationunfinishedbutcandidateidea: extend general SaveSlotSpec fromF628 toF700withoutmovingstorageF700/pagecounts16+19. OldfooterF618movesF6F0; proposed216byte extensionregionF618..F6EF fits16byteformatheader+50new4bytestacks. Preserve42nativearrayheaders/substructures/CRCs. This is a PROPOSAL, NOTimplementedorsafeproven: native dual-footer validation/counterselection/migration/CRC/hooks stillrequired. Evidenceprivate/pc-storage-layout-agent-v1/native-layout.json. Never treatpadbytes as already safeorclaim60slotsimplemented.

## October 15 — ship routes, correct door faces and native Save/Continue verified
LATEST PURE candidate: yellow-heartgold/build/0030-ship-door-faces-v1/private-ship-door-faces.nds SHA2565d4a077d22291fa0f4350d1acf70528e958bacc89f0457507192ad8e9f109f0b. Carries OWNER COLORED JESSIE/JAMES bundle (tools/colored_rockets.py) and all prior Vermilion changes. Parent chain colored-rockets-v1(aad1...) -> ship-passages-v1(985a5045ffa9a5bdd4028ef7bb0713fe5fb7cc6dca004d0a9aa39cfc64c76f68) -> ship-door-faces-v1. All original archive prefixes, all land/model/collision assets, originalAqua/Johto/maps, unlistedmapheaders/executables, ARM7/ITCM, battlecolors preserved by assertions. No extra executable memory used.
New tools/ss_anne_passages.py copies native329 two-cell passage THREE times in appended6x1 matrix under auditedunusedSinnoh258. Branch0 joins256's main/captainside components; offset64 joins254; offset128 joins257. Nativeleftstairs24,3/return and rightladder42,9+42,8 copied exactly with worldoffsets. Floors256(1F)/254(2F)/257(B1F) are copied307; grouped passenger maps259/260/261 have6/6/5 functionalcabins. Firstfloor retains3cells648,648,646; secondfloornow4cells648,648,646,646; basement3cells648,648,646. Extra unwirednativepaired-room components remain inaccessible. Nativecaptain255unchanged. Two otherwiseunusedvisiblehallroomdoors in1F servefloorconnectors; this is an explicitlayoutadaptation/WIP, not exactGBgeometry. Kitchen/bow/3F, boarding/story/actors/trainer contentstillpending.
Testingcaught actualarrivaldirectionbug inpassages-v1: south-facing1Fdoor to south-facinghallentrance spawnedplayerjustoutsideboundary24,20. Correctedvia tools/ss_anne_door_faces.py:2F/B1Freturnconnectors use nativeNORTHhall door36,8, withcabinportsrearranged. Nativeentrynow36,9, return1F30,14 or36,14. Modelchecks nowincludeoppositedoor65/69 faces; predecessorhas4violations, latestzero. Correctedterraincomponentaudit shows27/27activecomponentsreachable, seventeen distinctcabins. Tests/test_ss_anne_walkability.py FOURtestsPASS:allcabins/reachability/faces, olddisconnectedcandidate detected, oldbadfaces detected, variable-lengthnormal-landheaderparsing. tests/test_ss_anne_floor_banner.py TWOtestsPASS540headersplusboundaries/ABI; onlyAnne235bypassesnativeinteriorsuppression. Nativeheight/staticobjecttesting remains separate from thismodel; doNOTclaimall17cabinsnativelywalked.
ActualLIVE evidence0030-live-ship-walk-v1:allSIX1Fcabins entry/move/returnPASS across3landcells, oppositefacesincluded. Initial fixturetransportONLYto25624,12, copiedearnedOldRodsave; noitem/Pokemon/badge/completionflaggrants/RAMwrites/savestate. New0030-live-ship-doors-v1 uses latestcandidatewith initialtransportONLYto25630,13. Both1F<->2F and1F<->B1Fordinaryconnectingdoorways PASS withcorrectcoordinates. Farthest2Fcabin260105,3/4render/move/returnPASS innewfourthcell. Continuouswalk from1F via2F nativeleftstairs, copiedmiddlepassage, rightladderandcaptain-sidehall reached2559,11: captain-cabin-arrival.jpg. Nativefull-screenpreviewartnotinvented, smallbannerseen.
NormalSave insidecaptain cabin completed afterBOTHYes/overwriteconfirmations. saved-field.jpg was OVERWRITEPROMPT, despite its prematurefilename; save-state-now.jpg is actualreturntofield. Oldrunner16411stoppednormally; newPUREcandidate runner84256 loaded freshcopy of that normallysavedDSV in0030-live-ship-continue-v1, WITHOUTanyfixture/transportcode. OrdinaryContinue retains2559,11; continued.jpg. Nativecaptainexit,reverse ladder/passagestairs andordinaryreturnto1F30,13PASS onpurecandidate: continued-first-floor-field.jpg pluswalk-actions.jsonl. SourceOldRodsave/originalownerprogress/releasesunchanged. Nativeinputtimingcalibration led severalassertions beforeadjustments; these areloggedharness/inputerrors, separatefromactualfixeddoorfacebug. Ladderarrivalhasautostep/height6->2; allowsettle andavoidassumingimmediatecoordinates. HelpernowwaitsfornonnullRAM/mapduringtransition; noRAMmutations.
Currentlive84256 PURElatestcandidate, currentUNSAVEDposition25630,13, lastnormalSaveposition2559,11. Video/audio pausedaftertests; serverretained. Tunnel63284failedCloudflare1033whileprocessalive; terminatedonlyowned2533andcreatedtunnel97022(newprocess) at https://enclosed-mesa-cal-assumed.trycloudflare.com/ . OwneraccessURLprivate/current-viewing-url.txt, ownerchatposted. Remoteviewer/status/JPEG/control403 verified; latestpaused/noerror. PublictokenfreeURL+datedentryupdatedcommit aaade5ba029d78c53afd96c1cbfb36120556ceea; publiccoloredart/shipprogresscommit146b619a6d3cad734532762f8fd016b313c70ca7. NoROM/source/credentialspublished. Firstreplacementlouisville...obsolete; doNOTreuseoldurl.
Next checkpoint: campaignboarding(ticket/nativeportcopies; preserveAqua) andshipstory(actor/trainers/Blue/Cut/departure), missingkitchen/bow/3F design; remainingVermilion/Jennyart/Gym/fishing/gatecontinuouscoverage; mandatoryPC20+5perdistinctKantobadge60/layoutmigration+PKHeXcoordination. PCtailproposalstillNOTimplemented/proven. Latestreleased0029; DO NOTreleaseunfinished0030. Owner's post0029feedbackremainsdeferreduntil0030published asrequested.

## October 15 — native S.S. Anne boarding and postgame port routing verified
Latest pure private candidate: yellow-heartgold/build/0030-boarding-dispatch-v1/private-boarding-dispatch.nds, SHA256 53d9c36ffda9fe7ba0f9378083442914bc3ead205ebd761360cd538bc9044e3a. Parent boarding-v1 SHA256 ec5c90d8c77c64e976d2324311f05ccb7f9211628907064d408d0641bf4aae91, derived from ship-door-faces-v1. Owner-colored Jessie/James artwork and prior changes carried forward. Native ports386/387, Aqua307, Johto resources and all donor geometry remain unchanged. Audited unused Sinnoh placeholders263/264 receive native port copies. City54 warp7 routes to263; copied dock264 connects reciprocally to ship256 warp10. Archive prefixes and unrelated files/headers/executable sections preserved by build assertions. No extra executable memory used.
Ticket gate at263(7,9) checks native S.S. Ticket456 without consuming it; no-ticket refusal moves player one step north, remains retryable. Northbound return bypasses ticket dialogue. Bounded terrain routing audit proves the gate's only walkable chokepoint, independently of native checks. Three ticket-script and three dispatch-script tests pass; all23 test_ss_anne*.py regressions pass together.
ACTUAL native no-ticket test in0030-live-boarding-v1 uses copied earned Old Rod save plus initial transport ONLY: no ticket present, required-ticket message and pushback to7,8 observed. Misleading anticipated filenames ticket-flashed.jpg/ticket-admitted.jpg in that NO-TICKET folder actually show refusal/Sorry; do not use them as admission proof.
ACTUAL native admission test0030-live-boarding-ticket-v1 uses separately copied save, ONE clearly labeled fixture-only ticket grant and initial city transport, no badge/Pokemon/completion-flag grants. Correct flashed-ticket and welcome dialogue observed, then continuous ordinary city54 -> port263 -> dock264 -> ship256 travel passed. Return from ship25624,18 through dock264 and northbound port263 gate to city541309,340 passed; walk-actions.jsonl and labeled screenshots retained. This does NOT demonstrate Bill's story ticket acquisition, ticket persistence through a new save, or completed ship campaign. No normal Save performed this checkpoint.
New tools/ss_anne_port_dispatch.py uses native GAME_CLEAR flag0x964 to restore untouched port386 after Hall of Fame. Only native map-temporary4000 is written; native map transition clears4000..401F. Type2 callback resets it, asynchronous type1 dispatch handles native warp; no yielding warp in synchronous callback. Original gate/sailor scripts remain unchanged in appended script bank.
ACTUAL native checks on latest dispatch candidate:0030-live-dispatch-pre-v1 enters2637,3 before Hall of Fame.0030-live-dispatch-post-v1 enters untouched3867,3 with an explicitly artificial GAME_CLEAR flag in a separate controlled fixture, then ordinary Up exits tocity541309,340 with control restored. Post fixture also grants one test ticket and initial transport; not real campaign/Hall-of-Fame completion. Original saves untouched. Dispatch report originally says native_tests_pending=true; this dated checkpoint supersedes that field once native-verification.json is written.
Current backend79447 is POST-HOF CONTROLLED FIXTURE, city541309,340, not a release candidate for owner play and not saved progress. Previous boarding runner3633 and pre-HOF32961 stopped normally. Existing tunnel97022/enclosed-mesa-cal-assumed.trycloudflare.com retained; no changed viewing URL. Pause video/audio between actual tests and verify connection before leaving idle. Latest released game remains0029. Ship story/actors/trainers/Blue/departure, kitchen/bow/3F, remaining Vermilion/Gym/fishing and mandatory PC20+5 per distinct Kanto badge up to60 with legacy migration/PKHeX coordination remain pending. Next: save/reentry checks on pure boarding candidate, then ship campaign events; do not release incomplete0030.
Checkpoint closure: native-verification.json written in0030-boarding-dispatch-v1. Current remote viewer authenticated, video/audio paused, noerror; viewing credential rejected forcontrol403. Public plain-language log updated commit777c358b475b872d68029e517ad11aa30f46d67d; local development log appended. No changedURL, no patch release/source/ROM publication.

## October 15 — owner-authorized as-is prototype0030 release
Owner explicitly instructed release now and move unfinished scope to0031. This supersedes prior notes blocking0030publication on those features. Released PURE0030-boarding-dispatch-v1 candidate SHA25653d9c36ffda9fe7ba0f9378083442914bc3ead205ebd761360cd538bc9044e3a, copied to build/0030-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0030.nds; ROM/ROMZIP remain ignored/local. Patch SHA256c533e14a6e1bf13717c1be81e5dfbde7792a2fa76a32752bbfb52c9e54624d30. xdelta roundtrip, ZIPhash and actual embedded page worker execution PASS; wrongsize/checksum inputs rejected. PURE release excludes test fixture ticket/transport/HOF grants.
Public browser patch page https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0030/index.html published commit5f4adc6b2f68f409c310f446f0978c45f1438905, license d3c4c36cf1a7c9365172f12146259f4211c55d71, manifest e78ef6d66b1106c53b964de138759635f69f7627. Raw GitHub bytes match local files. Raw.githack initial403 is its normal External Content Notice; browser Open the page succeeds and shows correct0030 UI/limitations. Public log/latest link updated; historical releases preserved. No unrelated source/ROM published. No new0030 recording claimed.
NEXT PLAN: yellow-heartgold/PROTOTYPE-0031-PLAN.md. Ship story/missing areas, city/Gym/fishing and mandatory PC20..60 migration/editor work now0031.0030has10PCstacks. Existing live backend79447 remains paused CONTROLLEDPOSTHOF fixture, not released ROM; no new owner progress saved. Owner0029 feedback may now be acknowledged: no major issues, Fly toVermilion and PKHeXplugin working as tested byowner. Continue project under0031 plan after delivering0030link.

## October 15 — 0031 resumed from published0030
Verified released0030SHA25653d9c36ffda9fe7ba0f9378083442914bc3ead205ebd761360cd538bc9044e3a and copied it to new ignored build/0031-source-audit-v1/baseline-0031.nds. No gameplay changes yet. Release0030 remains untouched.
Read original Yellow VermilionDock.asm and VermilionCity.asm from Recovery READ-ONLY. Departure starts after obtaining HM01 when arriving at dock from ship warp1; receivingCut alone or entering dock from city must not markshipdeparted. Source setsEVENT_SS_ANNE_LEFT, plays shiphorn/surfmusic, scrolls/erases ship then forcesnorthwardexit; subsequent guardchecks preventboarding. Need faithful DS adaptation, not a bareflag/reward-trigger shortcut.
Flag candidateA7E REJECTED conservatively: raw byte matches in13 existing script members. CandidateA7D has zero rawscript/actormatches and exactlyone source reference: unusedFLAG_UNK_A7D definition. Projecttools/privatePython/JSON search finds onlynewauditselfreferences. Candidate is NOTallocated/written yet. Audit report build/0031-source-audit-v1/audit.json. No departure gameplay code, animation, native test or newrelease claimed.
Existing heartbeat continue-psyduck-yellow-development updated to0031plan, preservingACTIVE existing180minschedule and allrules. Unidentified Mega Evolution expansion NOTintegrated; currentbaseUSAretailHG. Continue ship departure arrival detection/animation/state before native Save/Continue/reentry checks; other0031scope unchanged. Prior paused controlled livefixture remains separate fromreleasebaseline.

## October15 — 0031 departure state/native persistence checkpoint
New tools/ss_anne_departure.py and tests/test_ss_anne_departure.py. Latest PURE private build0031-departure-v2/private-departure.nds SHA256fe3f2ebf817bf22ae5f501596df8cb869b2f30a152f450e0e1e46b94ec61955a. Build asserts changes only263/264 script/text/event pointers, appendedarchives andcompressionmetadata; donorAqua/Johto/geometry/coloredassets/ITCM/ARM7/otheroverlays retained. FlagA7D nowallocated fordeparted; captainA7Funchanged.
Async dock arrival callback checksnotdeparted+CUTgiven+nativePlayerAvatar coordinates23,18. Native GetPlayerCoords opcode105, not106. Firstv1used23,17 anddidnottrigger; v2corrected basedactualarrival. Telemetrycanreport23,17whileScriptGetPlayerCoords already18; donotuseRAMtelemetryasidenticalavatarpositionduringtransition. Sixcompiled-script tests verifynegativepositions/preCut/noearlyclosure, one-timedeparture, path, controlrelease, ticketindependentclosureandnorthboundexit; full29shiptestsPASS.
Scene currentlyplaysnativeSE1752, displaysdepartingmessage, automaticallywalksS2/W11/N7thenfade/warp2637,11 andsetsdepartedflag. Guardtalkandgateafterdeparture sayS.S.Annehas set sail, southernreboardingpushesnorth; northexitremainsfree. MOVINGSHIPVISUAL/HORNAUDIBILITYCAPTURE/faithfulcamerascene stillpending: thisisfunctionalstate/exitcheckpoint, notcompletedYellowanimation. Nativegeometrypreserved; shipmodelnotactuallyremovedfromcopy. No claimofshipvisuallysailingaway.
Actualnative0031-live-departure-v2 controlledfixture oncopiedOldRodsave grantsartificialcaptainA7F+oneTicketandinitialtransportto25624,18, noPokemon/badge/HOFgrants. Ordinaryexitshiptriggersmessage, automaticwalkreturn2637,11, northwardexitandticketheldreboardingrefusalPASS. Screenshotdeparture-arrival.jpg,departure-after-walk.jpg,reboard-after-departure-refusal.jpg. NormalSavecompletedafterYes/overwriteconfirmation,fieldmenureturnednormal-save-result.jpg. Touchattemptsusedwrongmenu coords; usedX/right/down/AtoSaveinstead. Noowneroriginalmodified.
Restarted PUREcandidatewithoutfixturetransport in0031-live-departure-continue-v1; Continued2637,8, saveddeparturegateblocksagain(saved-departed-gate-refusal.jpg), closesandpushesnorth, ordinaryexitcity541309,340PASS(saved-departure-city-field.jpg). First48Upframesmoved3tileswalkingafterContinue; increased64finish, inputtimingnotROMfailure. Currentpurebackend44602, UNSAVEDcityposition54; lastnormalSave2637,8. SourcecopiedsavehasartificialCut/testticketprovenance; notearnedBill/captaincampaign. Feedpausedaftertests.
Owneridentified Recovery/hg-engine-main.zip. ReadZIPREADONLYSHA2560cab9a9f4225a2d75de3507e30cee341577547d667755725c9e2e29833a16359. READMEidentifiesBluRosiehg-engineEnglishHGoverhaulwithMegas/Primals/Fairy/expansions/30boxes. include/config.h ALLOW_SAVE_CHANGES enabled andexplicitPKHeXincompatibilitywarning. Noarchivecodeexecuted/extracted/built/integrated. Assesshook/save/layoutcollisionsbeforeintegration; preservecurrentgame/editor/saves. Existingviewhostnameceasedresolving; replacementtunnelbeingrestored; donotclaimoldstreamhealthy.
Viewing restored: new tunnel21475 at minimal-charlotte-reader-survivor.trycloudflare.com; authenticatedremote statuscheckedpaused/noerror/viewcontrol403. Owneraccesslinkprivate/current-viewing-url.txt andchat. Currentpurebackend44602retainedpaused. PubliclognewURL+departurecheckpointupdated. Moving-shipvisualstillpending; no0031release.


## October15 scheduled engine assessment
Read-only ZIP audit recorded in build/0031-hg-engine-audit-v1/audit.json. Screened93 literal ARM9 org locations in16byte windows; one potential overlap at02000BB4 in patchoutarm9compression.s, not a confirmed conflict. Overlay/conditional/memory/NARC/save compatibility still pending. Config enables save changes, Mega Evolutions, item pocket expansion and30 Pokemon boxes. Pokemon boxes are separate from planned20..60 PC item slots. No engine build/integration/gameplay change; current0031 departure-v2 and released0030 preserved. No owner decision needed.

October 15 noon Eastern: daily Discord update confirmed sent (message 1560321442233450496). Reporting window since last confirmed October13 post; covered published0030, PKHeXv4, private0031 departure state and remaining work. Included public0030 patch and GitHub DEVELOPMENT-LOG links. Posting ledger updated, temporary draft removed; no public Git push.


## October15 afternoon — animated departure verified; Blue encounter native checks active
Owner explicitly requests CONTINUE UNTIL USAGE RUNS OUT; do not stop at ordinary checkpoints. No authorized reset/credit redemption. Continue0031 under latest rules; do not publish privateWIP.
PURE animateddeparture0031-departure-v3/private-departure.nds SHA256ee2d86a946d1666c9a98a22209cc0a741e0249c6361a0a0399b689ae2ff2d572. Uses native opcode723, byteargs1,0 then destination263,7,11. Source native723->sub020979A8->overlay105 animates departing ship, then restores destinationfield; noJohtoscripts/geometry/flagsmodified. FlagA7DcommitsAFTERcinematic returns. Otherstate/gatechecks retained. Buildpreservation passes. Actualnativecapturedmovingboat in0031-live-cinematic-repeat-v1/departure-048.jpg,055,060;120timedframes~30.37secwithnonzerostereo44.1kHzaudio5247716bytes. SourcecontrolledfixtureartificialCutA7F+ticket+initialtransportONLY; noearnedcaptaincampaignclaim. Firstrecordinghadmessageopen; secondmissedbriefanimation; repeatcapturewithtwoAacknowledgements successfullyrecorded. Nativeapp returns2637,11, reboardrefusalwithticketPASS. NativeSavecompletednormal-save-result.jpg. FreshPUREv3Continue0031-live-cinematic-continue-v1 retains2637,8; savedgateblocksandordinaryexitcity541309,340PASS. Lastpurebackend12149 pausedbetweenactualtests; connectionretained. CurrentbackendmaynowBluefixture below. Userwasgivenexistingminimal-charlotte-reader-survivor ownerlink; remotevideo/audioandviewcontrol403confirmed. NoURLchange.
NewBluewrapperaudit foundITCM32756bytes(12spare), nativehook02073440->01FFF29C->older01FFCCF8. Verifiedoldwrapperexact368bytesfromsource;latestidenticallogicfordifferenttrainerIDs. New tools/blue_properties_shared.py reuses52bytesofoldwrapperaseligibilityhelper, delegatespartycreationonce directlyto02073604 fromlatestwrapper andpatches16byteeligibilityguard. NoITCMgrowth. Oldwrapper externalcallaudit acrossallARM9sections/overlays findsONLYlatestcall; noexternalpointerreferences. Eligible741..750,782..785,new809..812. Reclaimedoldbody316bytes availableafterhelper; later56bytesusedtitlehook,260stillunusedbutmustrespectregistry. ARMnativeAPIstubs/tests/test_blue_properties_shared.py SIXtestsPASS: old/newexistingtrainerPokemonfieldresults, savedshiny/perfectindependence/freshseed, allfournewrecords matchpriorstarterproperties, unrelatedtrainersunchanged, helperall0..999IDs, ABI/stack/resourcepreservation. TestharnessinitiallymistookUnicornstop-before-sentinel asfailure; correctedPCsentinelcheck, notROMbug. Candidate0031-blue-properties-shared-v1/private-shared-properties.nds.
NativeBlueclass110providesBlueartwork;23wouldshowSilver. Shipclassassert23 initiallyrejectedBEFOREoutput, correctedto110. Existingnamehookalreadyusesowner'ssavedrivalnameforclass110IDs>=741. New tools/blue_rival_title.py uses56bytes ofreclaimedoldwrapper at01FFCD2C. Patches nativeReadMsg calls0200C2F0,0200C328,0200C360; onlyclass110 beforeGAME_CLEAR0x964 gets TEXT-ONLYlabel130 (copyofRivalclass23) appendedbanks730/731. StoredclassID/art/gender/payoutremain110. HOFflagreadthroughglobalSavePointer021D2228->020503D0SaveVarsFlags->offset040Cbit10; nopersistentwrites. AfterHOFnativeLeaderlabel110restored. Otherclasses/nullsavenativebehaviorunchanged. TwoUnicorntestsPASSallclasses0..139bothHOFstates/null, args/stack/callee-saved/read-onlyflag preservation. Candidate0031-blue-title-v1 SHAa58fcd6b2c5d57ffa4f066116e91f7cd0995df0c0755c8653fb25a9698fcbeb9.
LATESTprivatecandidate0031-ship-rival-v1/private-ship-rival.nds SHA2560565001a504948b183d26dca2a3e629a8a2084c69c068a9a0484b7bdb37d9fef. tools/ss_anne_rival.py appends4trainers809..812; nativeYellowSSAnne teamSpearow19,Rattata16,Sandshrew18,starter20. RetainsapprovedsavedPsyduck/Eevee/genderchoice, nativeBlueclass110art withnewRivaltitle. SpearowmovesPeck/Growl/Leer/FuryAttack;RattataTackle/TailWhip/QuickAttack/HyperFang;SandshrewScratch/SandAttack/Slash;starterapprovedpreviousmovesretained. Existingtrainerrecords/parties/names/textstablepreserved; onlyoldtextbanks728/729appendentries. Allunrelatedresources/headers/ARM7/ITCM/overlayspreservedrelativetitlecandidate.
Map254 actor0sprite375 at48,16facesEast, initiallyhiddenviaA79. Mandatorysinglefronttile49,16 coordtriggersscene;Captainwarp49,15nativewall-door,adjacentapproachesotherwiseblocked. NewDONEA7B,HIDEA79auditrawscripts/actorszeroandnativeC/HonlyUNUSEDdefinitions; A7Crejectedrawmatch. Maptype2initSetHIDEonentry. Scene skipsDONEorlegacyCUTgiven;otherwiseLock,clearHIDE,ShowPerson,playerfaceWest,YellowBonjourdialogue, selectedBattle4branches, checkresult220. LOSSdialogue+nativeBlackout219 noDONE so retry;WINdialogue/Cutmastermessage,BluewalkW6/N6alongnativecorridor,SetDONE/HIDE,HidePerson,restoreBGM/release. Nofakelegacywins. FIVEcompiled-scene testsPASSallstarterbranches/lossretry/no-repeat/legacyCutskip/exitpath. Nativeheight/scene/battleoutcome checks PENDING.
CurrentBluefixture0031-ship-rival-fixture-v1 has initialtransportONLY361->25449,17 usingfreshcopiedOldRodsave; NOitems/Pokemon/badge/completionflaggrants. Currentlive63310 folder0031-live-ship-rival-v1. Continuehelperprivate/continue-0031-blue.py started, maystillrunning session48878; inspectstatusbeforemovement. NeedUp8/16to49,16trigger; advanceBonjourpages, verifyRivalGOLD/Blueportrait/team/nativewinloss,SaveContinue/retry. Sourcepartystrengthunknownuntilbattle; doNOTgrantanythingunlessclearlylabeledisolatedfixture. Currentowneroriginals/releasesuntouched.
Controlhelper stored inallowedWindowsvisualizations path /mnt/c/Users/thata/.codex/visualizations/2026/10/12/01a12fa4-99b9-7270-a2f8-828af71c8984/native-control.py acceptsfolder mode(status/frame filename/buttons a:8,up:8/pause). Allnewprojectwritescurrentlyrequireexplicittool require_escalated becauseworkspacepermissionschanged; automaticreviewhasapprovedauthorizedwork. PreferexistingWSLvenv; noRecoverywrites. Newmodules/tests copiedviaallowedvisualizations scripts+WSL. No publicsourcepush. Logsrequireupdatewithverifiedcinematiccheckpoint, notyetpublicthisturn.

## October15 — native Blue victory and pure Save/Continue verified
Latest0031-ship-rival-v1 remains private, SHA0565001a504948b183d26dca2a3e629a8a2084c69c068a9a0484b7bdb37d9fef. Native controlled initial-transport-only fixture used copied OldRod save, existing level100Umbreon (not granted). Correct Blue portrait and Rival BLUE title captured blue-140.jpg; actual team Spearow19/Rattata16/Sandshrew18/Psyduck20 defeated through ordinary inputs. This is encounter functionality, not campaign balance proof. Native outro100frames/stereoWAV complete in0031-live-ship-rival-v1, final blue-outro-099.jpg shows Blue absent, control restored. Normal save completed blue-saved-field.jpg. New PURE candidate backend38012, folder0031-live-blue-continue-v1 loads copied normal victory save without fixture transport. Down/up across49,16 no repeat, captain2559,11 reachable; saved-blue-no-repeat.jpg and saved-blue-captain-entry.jpg. Captain dialogue active at10,4; ordinary reward continuation underway. Native loss/retry and continuous post-Cut departure still pending. All34 test_ss_anne*.py tests PASS in57.925s. Originals/releases unchanged. Keep working per owner until usage unavailable.

## October15 — Blue-to-captain-to-departure sequence checked
PURE0031-ship-rival-v1 continued from normally saved native Blue victory. Trigger49,16 did not repeat; captain255 entered normally. Captain dialogue/reward completed through ordinary inputs (captain-after-blue.jpg, captain-reward-now.jpg). Return around desk requires x11, not blockedx10south; first route assertion correctly stopped at desk, no gameplay bug. Ordinary reverse path through254/258/256 all map/position checks passed. Exit25624,18->264 triggered departure without an artificial Cut flag or ticket grant in this run. Captured120timedframes30.34s and5280284bytesnonzero stereo audio in0031-live-blue-continue-v1/earned-capture.json, earned-ship-departure-live.wav; earned-departure-035.jpg visibly shows moving boat. Returned2637,11 with control. This extends the initial-transport-only copied-save Blue test, not Bill ticket/campaign-balance proof. Eight Blue property/title tests additionally PASS. Normal Save of postdeparture sequence underway; verify completion before switching runners.
Prepared separate HP-only loss fixture in allowedWindowsvisualizations weak-party-tool-v1: leadexistingUmbreonHP1, existingGyarados/Clefairyfainted; species/levels/items/badges/storyunchanged, checksum/decodedbytepreservationassertionsPASS. SourcefileSHA20290CCB22FCA28C1418D5B5268589705D5E34A37996F4CE14BB51144BC8A27C unchanged;output48E1D8CF659DB9935094143241B27B8C6E1217B92295CBB1B53B745320D39627. Originalprovenance mistakenlyhashedmutatedinmemorysourcebufferafterexport; correctedindependentfilehashinblue-loss-hp-only.corrected.json andfixedProgram.csforfuturebuilds. FixtureNOTnative-tested yet; no originalsavewrite.
Postdeparture normal Save confirmed earned-departure-save-result.jpg. Live runner now22775 HP-only copied lossfixture folder0031-live-blue-loss-v1; no owner save edits. Public plain-language checkpoint published commit1fb526583304cbe88c1f3776c8bbc6a52150fbe8 contentSHA2038c881e56a5d8fe72ca24161bf095a710782d8; latestpublicpatch0030 unchanged.

## October15 native loss regression found and corrected; retest active
0031-ship-rival-v1 HP-only native loss test exposed white-screen stall after party fainted. Source Task_StartEncounter returns on normal loss WITHOUT restoring overworld; previous scene attempted field msg2 before WhiteOut, which cannot render. New tools/ss_anne_rival.py lost branch calls219 directly before any field dialogue; no allow-loss/healing shortcut added. test_ss_anne_rival.py now models field unloaded after normal loss and rejects field dialogue untilWhiteOut;5testsPASS. New0031-ship-rival-v2/private-ship-rival.nds SHAeb353a34c0e73e7a08a5ea80123b185a1549e51708dac0da6f3a72b67ba35476. Parenttitle-v1 reused;unlistedfiles/ARM7/overlays/ITCMpreservationassertionsPASS. Priorv1build/evidencepreserved. LatestnativeLOSSretestactivebackend59473 folder0031-live-blue-loss-v2, correctedtransportonlyfixturev2, freshsameHP-onlysave. Continuehelperrunning; verify result before claimingfixnativePASS. No0031release.

## OWNER OVERRIDE October15 — ship rival victory is OPTIONAL
Owner explicitly replaces blackout/retry design: after losing this ship battle, automatically heal ENTIRE party, let Blue finish scene dialogue and leave, then allow captain access. Winning NOTrequired. Priorv2directWhiteOut fix superseded before native retest; DO NOTrestoreblackoutrequirement.
Latest0031-ship-rival-v3/private-ship-rival.nds SHA237b9d24e8a8bb9ed9e4f0b9842bee67609db0afb324c2c590ea103231411426. selected_battle uses native allow_loss1/BATTLE_TYPE_11: native Task_StartEncounter heals party on loss and restores field before scene resumes. Result220 still actualwin/loss; winningmsg1 or losingmsg2 thensharedmsg3, BlueW6/N6exit, DONEA7B/HIDEA79setandhide/release. DONEmeansscenecompleted, notfakebattlewin. NoBlackout219innewscene. All5compiled-scene testsPASS includinglossheal/commonexit/norepeat/captainpath. Unrelatedfiles/ARM7/overlays/ITCMpreserved. Newtransportfixturev3; currentrunner54622 folder0031-live-blue-optional-v1 using HP-only copiedsave. Nativeoptional-loss verification INPROGRESS; doNOTclaimyet. Continuehelperstarted. No0031release. Keepworkinguntilusageunavailable.

## OWNER GLOBAL RULE October15 — every pre-Champion Blue rival battle is optional
Owner explicitly extends optional wins to ALL rival battles against BLUE before facing him as first Pokemon League Champion at Kanto's end, unless later overridden. Loss automatically heals ENTIRE party, Blue completes scene dialogue and leaves, story continues. FirstChampionBlue victory remains REQUIRED. This is approved departurefromYellow, doNOTdefer. Apply existingRoute22/Ceruleanscenes aswell asship; labalreadyallowsloss. Preserveactualwin/lossresult; completionflagsmeanscenecomplete. DoNOTapplytoGiovanni,othertrainers,EliteFour,postgamegymBlueorJohtocontent. Currentshipv3implementsrule; Route22andCerulean changes STILLPENDING. Nativecurrentoptionalshiptest54622/0031-live-blue-optional-v1 underway; nextinspectcapturedoutcome, verifyfullpartyhealedandcaptainaccess, thenpatch/auditexistingotherBlueencounters.
TEST LAUNCHER CORRECTION: v2loss/optional-v1 wrappers only replaced text in an outer wrapper, which did not contain the actual runtime-loaded ROM path. They still launched fixture-v1. Their white screens reproduce OLDv1lossbug, NOTv3optional failure. Corrected full launcher start-blue-optional-verified.py explicitly uses0031-ship-rival-fixture-v3. Currentnativebackend51637 folder0031-live-blue-optional-v2; this is first VALIDv3optionalnativecheck. Olderchecks preserved/labeledinvalidforv3. Route22/Cerulean generators nowoptionaldefaultTrue withlegacyFalse exactmatcher, but candidateROMpatchstillPENDING.
LATESTCANDIDATE0031-blue-optional-all-v1/private-blue-optional.nds SHAc10a3bc52e1c85d371ec705790fafe89903e5828d25bb302aa824d2b6baa0c72 appliesnewglobalruletoRoute22map27trainers747..750andCeruleanmap52trainers782..785; labalreadyoptional, shipv3included. Newtools/blue_optional_battles.py exactoldcompiledscenematches beforeappendnewbank andheaderpointer. Preservesallotherbanks/files/ARM7/ITCM/overlaysandChampion. NativeearlierencounterchecksPENDING; compiledmodeltestsnext. Currentliveverifiedshipv3testnotyetallcandidate, backend51637folderoptional-v2.

## October15 — VALID optional Blue loss native check PASS
Correctlauncher51637 actuallyusesfixture-v3;0031-live-blue-optional-v2. Native battle lost afterexistingUmbreonHP1 andother2fainted; outcome180frames36.51s+6368644bytesnonzerostereoaudio. Restoredfield25449,16, Bluefinishedlosingdialogue/sharedoutro/walkedaway (verified-loss-current.jpg). NativepartyUI verified ALLthreeFULLHP:Umbreon331/331,Gyarados331/331,Clefairy39/39 inverified-full-party-healed.jpg. OrdinaryUpcaptainentryPASS captain-access-after-loss.jpg showscaptaincabin2559,11; telemetryinitiallylagged25449,15whiletransition, allowsettle. This is VALIDv3nativeoptionalPASS;prioroptional-v1wasstalev1ROMinvalidforthisclaim. CurrentliveinCaptainroom; no postlossSaveyet. All34shiptestsPASS41.213s. GlobalRoute22/Ceruleanmodeltest144casesPASS; latestallcandidatec10a3bc... nativeearlierchecksSTILLpending. No0031release. UserglobaloptionalpreChampionrulemustpersistinrecurringplans;Championfirstvictoryrequired.

## October15 20:16UTC — optional ship loss persistence checked
Normal postlossSave completed in0031-live-blue-optional-v2/post-loss-save-final.jpg. NewPURE latestglobalcandidatec10a3bc... backend53168 folder0031-live-blue-loss-continue-v1 loaded a copyofthatnormalSave, NOfixturetransport. Continue retainedcaptain2559,11; ordinaryexit returned25449,16 withBlueabsent/noRepeat (pure-postloss-landing.jpg), normalcaptainreentryalsoobserved. Firstbatchsnapshotblackwastransitional; pure-loss-settled.jpg latercorrectfield. SaveprompthelperinitiallyopenedOptionsbecausecursorretainedPokemon; canceledwithoutsettingchanges, thenactualsavepromptverified. Nooriginalsmodified.
Existingrecurringheartbeatupdatedthroughautomationtool toincludeGLOBALoptionalBluepreChampionrule, Championvictoryrequired; existingACTIVE135minuteschedulepreserved. CurrentnextnativeRoute22test16923/0031-live-route22-optional-v1 useslatestallcandidateviaexplicitfixturepath. FixtureclearsR22DONEB44/HIDEB43 andBOUNDARY416B=0 theninitialtransport27(981,266); HP-onlycopiedsave, noitem/species/level/badgegrants. This iscontrolledscene reset, NOTearnedcampaignprogress. Continuehelperrunning. NativeRoute22/Cerulean checksNOTyetclaimed. No0031release.
Publicoptionalrule+PUREsavedlosscheckpointpublishedcommitf892f3e6759cfda849bc712fcf0b3c1c5944fc52 contentSHAe35854af57e38072149cd4d197511b238843e2a3. Route22nativev1actuallyWON (autoAselectedFaintAttackagainstboth);correctBlueintro,Spearow9/Psyduck8, dialogue+exitPASS route22-native-win-exit.jpg. DoNOTclaimnativeLOSSfromv1despitefixturelabel. Freshv2folder0031-live-route22-optional-v2 runner5317 ready; capturecontrolledintro stopautoAafter18stoavoidselectingattack. NeedchooseHelpingHandonFIRSTFightmenu, allowSpearowtohitHP1. NoSaveinv1. ShipPUREpostlossContinuePASS remainsvalid. Compiled144executions=72outcome/starter/lanecombinationsplus72norepeatchecks.

## October15 20:23UTC — Route22 optional native LOSS/WIN PASS
Latestglobalcandidatec10a3bc... testedthroughfixture0031-route22-optional-fixture-v1 (explicitclearDONE/HIDE+BOUNDARY0; noitems/Pokemon/badgesgranted). Nativev1autoAactuallyWON; correctSpearow9/Psyduck8, dialogue/BlueexitPASS route22-native-win-exit.jpg. Separatefreshv2HP-onlycopy selectedHelpingHandFIRSTturn, SpearowdefeatedUmbreon(outcome-040.jpg), fieldlosingdialogue/sharedoutro(outcome-095.jpg) thenBlueexit/controlPASS. Entirepartyfullyhealed331/331,331/331,39/39 route22-party-healed.jpg. Left/rightacrosstriggeragainnoRepeat route22-loss-no-repeat.jpg.180timedframes36.486s/nonzero6362152bytesstereoaudio. NoSaveclaimedforRoute22;sourceoriginals/releaseunchanged.
NextCeruleannativefixture0031-cerulean-optional-fixture-v1 useslatestallcandidate, clearsA81/A82and4144=0,initialtransport52(1327,101), copiedHP-onlysave. Currentrunner65076folder0031-live-cerulean-optional-v1. Continuehelperrunning. TriggerUP8to1327,100; capturenativeintroSTOPautoAbeforeFightmove thenHelpingHand tolose. CeruleanNATIVEPENDING; no0031release. Fixturepreparescriptsinheritobsoleteconsoletextship-floor; relyexactfixtureJSON/actualROMpathandlabel, notconsolecaption.

## October15 20:28UTC — Cerulean optional native LOSS PASS
Latestallcandidatec10a3bc... through0031-cerulean-optional-fixture-v1 withclearedA81/A82,4144=0andinitialtransport52(1327,101), existingHP-onlycopiedsave. NormalUPtriggerBlueapproach/RivalintroductionPASS; nativefirstopponentSpearow18. ExplicitHelpingHandused;partydefeated(outcome-090.jpg: GOLD is out of usable Pokemon). Restoredsamecity52(1327,100), lossdialogue/sharedBilloutrofinished,Bluewalkedaway/controlrestored(cerulean-loss-exit.jpg). Fullpartyhealed331/331,331/331,39/39(cerulean-party-healed.jpg). Down/uprecrosstriggerNOrepeat(cerulean-loss-no-repeat.jpg).180frames36.494s+6360416bytesnonzero44.1kHzstereoaudio. Nativeallstartergenders/lanevariationsnotallreplayed;compiled72outcomecombinations+72norepeatcheckscoverthose. NoCeruleannormalSaveyet; shipoptionalLOSSnormalSave+PUREContinuealreadyPASS earlierthisrun. Champion/unrelatedresourcespreservedbypatchassertions;ChampionbattleNOTnative-testedthischeckpoint.
Currentlive65076folder0031-live-cerulean-optional-v1 remainscontrolledfixture, nooriginalsmodified. Existingremoteviewerstatus/JPEG200verified, URLunchanged. Pausevideo/audioaftertestsandkeepconnection. LatestPUREcandidate0031-blue-optional-all-v1/private-blue-optional.nds SHAc10a3bc52e1c85d371ec705790fafe89903e5828d25bb302aa824d2b6baa0c72. Nextreturnto0031campaignscope: remainingAnneareas/actors/trainers, VermilionGym/fishing/gatecoverage, mandatoryPC20..60legacy/editorwork. DoNOTrepeatcompletedBluecheckswithoutnewchange. No0031release.

## October15 22:28UTC — PC extension offline migration model checkpoint
Readlatesthandoff/developmentlogfirst; resumedmandatoryPC20..60work, notBluechecks. Newtools/pc_storage_layout.py is OFFLINE COPY-ONLY CONTRACT, NOTROMhook/PKHeXintegration. ConstantslegacygeneralF628/footerF618, expandedgeneralF700/footerF6F0, originalPokemonstorageoffsetF700unchanged. Proposed16bytePYPCv1header+50extra4bytestacks fills216bytes; originaltenvarstacks/nativeprefixbeforeF618remainbyteidentical. normalize_general acceptsfullbufferthroughF700, validatesnativefooter/magic/slot/CRC, copieslegacycountertoexpandedfooter, zero-initializesextra50, preservesallbytesfromF700on. Expandedinputidempotent;unsupportedheader/reservedvalues/malformedquantities/corruptCRCfailclosed. NOdual-copyselectioninvented; nativegeneral/storagecountercoordinationandatomicwritefallbackSTILLREQUIRED. capacity() requires8bitKantobadgemask20+5popcount, all256maskschecked. Physicalextra50preservedevenifbadgecaplower (noitemloss). FormatPROPOSEDuntilnativeintegrationverified; donotclaimPCcapacityexpandedingame.
Newtests/test_pc_storage_layout.py FIVEtestsPASS (nativeprefix/storage/inputimmutability;count0/1/FFFFFFFE/FFFFFFFF;idempotence/finalslot999retention;legacy/newcorruption;validCRCunknownschema/malformedstackrejection;allbadgemasks). ActualcopiedOldRodDSVbothlegacybanksvalidatednativelyCRC; INMEMORYONLY normalizedcopiescount42/41 preservednativeprefixandallPokemonstorage/tail, remainedidempotent; sourceSHA20290ccb22fca28c1418d5b5268589705d5e34a37996f4ce14bb51144bc8a27c unchanged. Reportbuild/0031-pc-layout-model-v1/report.json explicitlyOFFLINE_MODEL_ONLY_NOT_NATIVE_IMPLEMENTED;NOsavefileswritten,NOcandidateROMchanged. LatestPUREremains0031-blue-optional-all-v1c10a3bc...; released0030unchanged. Nextauditexactnativevalidation/slot-sizehooks,cachedfooterpointer/dualcopyselection,memorybudgetbeforeARMpatch; thenfresh/legacy/corrupt/mixedsavecasesandPKHeXdual-layoutsupport. KeepRecoveryreadonly. Existingviewerpausedbetweenactualtests; nofeedrestartneededforofflinework.

## October16 00:46UTC — PC dual-copy recovery reference tested offline
ReadHANDOFF/DEVELOPMENTLOGfirst. ContinuedPCsavecompatibilitywithoutROM/savewrites. Auditednative save.c ValidateSaveSectorFooter, SaveSlotCheck_InitFromSavedat, Save_GetSaveFilesStatus and InitSlotSpecs. Important: nativecountercompareONLYspecialcasesFFFFFFFF->0; doNOTreplacewithgenericserialarithmetic. NativechoosesCOHERENTgeneral+PokemonstoragepairatSAMEcopyindex, notindependentnewestblocks. Solevalidpairwithmismatchedcountershitsnativeassertion; offlineportfailsclosed. Cachednewfooterpointerstillrequiresmigrationbeforecountread. InitSlotSpecscomputesgeneral/storageoffsetsafterroundingto100; generalF700keepsstorageF700and16+19pages.
Extendedtools/pc_storage_layout.py withSOURCE-FAITHFUL OFFLINEcounter/ranking/pair-selectionreference, notnativehook. native_validnowacceptsexpected_slotforstoragevalidation. Newtests/test_pc_storage_recovery.py FIVEtestsPASS:counterwrap/equalpreference,allfourlegacy/expandedmixeswithsamecounters,interruptedwritecoherentfallback,rejectsplitvalidcopies/solemismatch,all16validitymasks. Combinedtest_pc_storage*.py TENtestsPASS0.077s. RealcopiedOldRodDSVbothgeneralANDstorageCRCvalid (slot0/1respectively),counters42/41forboth;referencechoosescopy0GOOD. SourceSHA20290ccb22fca28c1418d5b5268589705d5e34a37996f4ce14bb51144bc8a27c unchanged. Newreportbuild/0031-pc-recovery-model-v1/report.json explicitlyOFFLINE_REFERENCE_ONLY_NO_NATIVE_HOOK. NoROM/savecreatedormodified;currentgameSTILLTENPCstacks. NoPKHeXexpansionclaimed.
ExactbinaryhookaddressauditstillPENDING. Recoveryasm/save.sdoesnotexist(decompiledCsource); no guessedaddresspatchattempted. Needidentifyfunctionsfromverifiedbinary/disassembly/symbols, establishexecutablebudgetandfresh-saveinitbeforeactualnativeintegration. LastBluecheckpointnotrepeated. Released0030/latestpure0031c10a3bc...unchanged;existingviewerpausedbetweenactualplaytests. Noownerdecisionneeded.

## October16 02:58UTC — exact native save routines identified and executed
ReadHANDOFF/DEVELOPMENTLOGfirst. Read-onlyThumbdisassemblymatchednativefunctionsagainstsave.c. Exactsites: GetSaveSectorFooterPtr020275F4(40bytes),ValidateSaveSectorFooter0202761C(112),SaveSlotCheck_InitFromSavedat0202768C(52),SaveSlot_BuildFooter020276C0(76),SaveData_InitSlotSpecs02027EFC(172). AllfivewholecodewindowsbyteidenticalpristineHGviaBASEcomparison;hashesrecordedbuild/0031-pc-native-hook-audit-v1/report.json. No guessedaddresspatches. Initialslotdisasmstartedonliteral/invalidhalfwordandreturnedempty; correctedRAM-baseoffset+skipdataidentifiedproperfunctionentry, notROMissue.
Newtests/test_pc_native_save_functions.py FIVEtestsPASS0.605s executing ACTUAL unmodifiedThumb underUnicorn: nativefooterpointertrackslegacy/newsize;matchingnativeCRC/layoutacceptsandcrosslayoutsreject;corruptionrejects;cachedcountreadreadsnewfooterFFFFFFFFcorrectly;actualnative42headerInitSlotSpecsproducesF628/F700storageoffsetand16/19pages. CRCservice0201FF98stubbedwithindependentlycheckedCCITTreference; thisisnativecontrolflow/ABIvalidation, NOTfullDSflash/runtimeintegration. Callee-savedregisters/SP/returnasserted. FirstharnessmappedunneededDTCMsectionwithoutRAMmapandfailed; restrictedtoloadingrequiredmainsection,thenall5PASS. NOsave/ROMchanged. Existing10offlinePCtestsremainpreviouslyPASS, notunnecessarilyrerun.
Nextinstallcarefullytestednativevalidator-calladaptersandgeneral-spec-sizechangeafterexecutablebudgetaudit. Cachedfooterpointer020276A0 iscomputedBEFOREvalidation020276A8; migratednewfooterMUSTexistbeforevalidatorreturn. Needfresh-saveheaderinitializationonnewfooterbuildandvariableaddressremapping,strictformatguards,actualmixed/corrupt/legacyContinue+normalSavebeforePKHeXdual-layoutrelease. NativehookimplementationstillPENDING;physicalgamecapacityremains10. Latestpurec10a3bc...andpublished0030unchanged. Viewerpausedbetweenactualplaytests; noownerdecisionneeded.

## October16 05:12UTC — isolated native migration adapter passes instruction tests
ReadHANDOFF/DEVELOPMENTLOGfirst. Newasm/pc-general-validate.s is an ISOLATEDPROTOTYPE, NOTinstalledinROM. Thumbadapterassembledatproposedreclaimed01FFCD64,200bytesof260auditedfreebytes(60remain),SHA7dd3f4b2bde58fb415526f41e6af65abfc7d8533725eda6e954c522387f090e1. UsesunmodifiednativeValidate0202761C;non-generalandlegacy-specdelegateunchanged. ForF700general:validnewfooterrequiresPYPCv1/count50/reserved0header;otherwisevalidateslegacywithTEMPORARYF628spec,restoresF700evenonfailure,thenmigratesincopiedRAM,zeroes216bytestail,writesheaderandnewfootercounter/size/magic/slot/CRC. Sourcelegacycounterpreservedbeforetailzero. NativeCRCserviceusedfornewbody. Callerregisters/stackpreserved. Report+binarybuild/0031-pc-validator-prototype-v1 explicitlyISOLATED_UNICORN_ONLY_NOT_INSTALLED; noROMorowner-savewrite.
Newtests/test_pc_validator_adapter.py SIXuniqueadaptertests+FIVEnativeregressions=11PASS0.781s:fitsbudget,legacycount0/42/FFFFFFFFmigrationbyteidenticalreference,expandedidempotence/unknownversionreject,invalidlegacyread-only+specrestored,legacy-specpass-through,actualPokemonstorageslot1unchanged,ACTUALnativecached-footerflow redirectedAT020276A8inUnicornreadsNEWmigratedcount42correctly. CRCstubsameindependentlyverifiedCCITT. Firstdiscoveryimportexposedbaseclassandrepeated5tests; correctedmoduleimporttoavoidduplicatebasecollection. NotDSflash/runtimeproof.
StillPENDINGbeforeinstallation: rejectCRC-validmalformedextra-stackpairsinadapter(currentheaderguardsONLY),slot-sizehook,fresh-saveheaderinit,allvalidatorcallsitesaudit,virtualvarmapping,60slotPCUI+badgecapacity,fulllegacy/fresh/corrupt/mixednativeContinue+normalSave,PKHeXdual-layout. Only60bytesremaininthisreclaimedblockafterprototype; doNOTassumeotherhooksfitwithoutbudgetaudit/additionalverifiedreclaim. LatestPUREc10a3bc.../published0030unchanged;gameSTILL10PCstacks. Continuefromadaptertestsnext,donotrepeatpriorBlueplaytests. Existingviewerpausedbetweenactualtests; noownerdecisionneeded.


## October 16 — prototype 0031 released under campaign-first rules
Delivered candidate c10a3bc52e1c85d371ec705790fafe89903e5828d25bb302aa824d2b6baa0c72 unchanged as yellow-heartgold/build/0031-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0031.nds. ZIP verified; cumulative xdelta roundtrip and actual page-worker decoder PASS, including wrong-size and wrong-checksum rejection. Native Blue/ship evidence remains as documented; no repeated playthrough or new full-campaign claim. Public page https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0031/index.html rendered successfully in browser. Patch page commit 8b9375b4d6a2db3b7dc829d4ea2c07bd8a0f17ce; public log/latest-patch updated commit e6b1d99fcc616e38a564341ac977ccc8a2ffb634. Only patch page/license/manifest and public documentation published; ROM/ZIP/saves remain local. Earlier releases preserved. PC storage still ten stacks; migration adapter not installed. Next required task is Cut-to-Lt. Surge/Thunder Badge and onward campaign travel. Use 0031 as released baseline and new 0032 build paths for next changes. No ship polish/PC expansion release blockers. Publication checkpoint October 16; next active 24-hour checkpoint must yield playable progress or explicit blocker report per owner rule.
Public HTTP download additionally verified byte-identical to tested local page: SHA256 1040433b2876af760359620d70e65db5915cf13b649878f55172e10d6694ae72. Recurring reminder updated to preserve released0031 and advance campaign changes under0032.

Owner clarification October 16: A release is a checkpoint, never a reason to stop. Continue immediately with the next campaign-critical task while usage and execution are available. Stop only for an issue that genuinely requires owner advice or unavailable usage/execution, or an explicit owner pause. After a usage interruption, resume on the first recurring reminder when usage/execution is available. Do not claim background execution between turns. Preserve the campaign-first priorities and regular playable release cadence.

## October 16 — private0032 Gym checkpoint
Campaign-first work continued after0031 release. New tools/vermilion_gym.py retains native Gym puzzle/badge/loss/full-Bag-retry script; clones778->1164 with only reward operand909 changed TM34(361)->TM24Thunderbolt(351), text485->925 corrected. Yellow sourceparties/specialmoves read-only: trainer232 Magnemite24;337 Voltorb22/Magnemite22;396 threeVoltorb20;255 Raichu28 withThunderbolt/MegaPunch/MegaKick/Growl. Other records/resources/maps preserved. Juniorclass/name and otherdialogue polish deferred. Native source search found these trainer constants only in VermilionGym script.
Candidatebuild/0032-vermilion-gym-v1/private-vermilion-gym.nds SHA33ece532c5f1b11453b16fd807bf0bdfe6b46e91695500dab8c94fabaab9ab77. Four focusedtest_vermilion_gym.py checksPASS. Initialpreservationtest caught documentedcompressedStaticEnd metadata difference atcodeSettings+20; exactdiff onlymetadata+intendedheaderpointers, testcorrectedexplicitly.
NativePURE0032-live-gym-pure-v1 loaded copied earnedCut/shipdeparturesave and normalwalk263->264->263->city54->Gym365passed. Existinghighlevelparty: threeVoltorb20trainer defeated, fieldrestored, firstswitchfound. Othertrainertriggered9,14;08:04UTCusage rejection prevented nextinput, NOTexecuted. No normalSaveclaimed. ExteriorCutdependency NOTverified: no actualCutuse demonstrated oncitywalk; investigatenotassume.
Afterusageresetoldrunnerrefusedconnection. New0032-gym-transport-fixture-v1 onlyinitialtransport263->3656,18; noitems/Pokemon/badges/storyflags granted. Continuetemp4000retained1; ordinarydockreturncleareditthenfixturetransportPASS. Currentrunner86756folder0032-live-gym-transport-v1; copiedsameearnedCutsave. Nativepuzzle/Surge/reward/SaveContinue stillpending. Controlledfixturesarenotnaturalcampaign/balanceproof. No0032release.
Viewingrestoredsession91601, remote200: https://semiconductor-occasionally-filters-howard.trycloudflare.com/ . FullaccessURLprivate/current-viewing-url.txt/ownerchatonly; publiclogcommit9378953793b6f6c2d49111bd4929e0e4f4eabc5c tokenfree. PauseA/Vbetweenactualtests. Nextfinishpuzzle/Surge/Thunderbolt+normalSave/PUREContinue, checkCutaccess, package0032, moveon. PCexpansion/shippolishdeferred.

## October 16 13:36UTC — prototype0032 released; continue campaign
Native controlled initial-transport-only Gym sequence passed: trainerHorton threeVoltorb20 andGregoryVoltorb22/Magnemite22, firstswitchcan5 thenadjacentcan0 second, bothnativegateanimations andclearpathmessage. Surge6,4 battledRaichu28 andlostnormally. ThirdbadgeSaveUI observed, TM24receipt andTHUNDERBOLT explanation captured. LeadUmbreonFaintAttackPP0 inexistingcopyrequirednormalbattlepartyshifttoexistingGyarados; nativeparalysiscausedsomefull-paralysis turns beforeIcyWindKO. No party/PP RAMedits or grants. Highleveltestnotbalanceproof. ThirdjuniorMagnemite24 rawdataonly; Surge disablesremainingjuniorsasnative/Yellow.
NormalSavecompletedgym-save-finished.jpg. NewPUREcandidate runner46152 folder0032-live-gym-continue-v1 loadedcopyofearnedGymSave, nofixturetransport. Continue3656,5, Surgepostvictoryadvice(noBattle/noTMretry)passed. Ordinaryexitthroughbothopengatesandwestaislethenbottomdoorreturnedcity54(1295,319);gym-exit-settled.jpg. Video/audio pausedaftertest; server/tunnelretained. No postContinueSaveclaimed.
RELEASE0032: build/0032-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0032.nds SHA33ece532c5f1b11453b16fd807bf0bdfe6b46e91695500dab8c94fabaab9ab77. ZIP/cumulativexdeltaroundtrip/actualpageworkerdecoder+wrongsize/checksumrejectionPASS. Publichttps://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0032/index.html . PublicHTTPbyteidenticaltestedlocalpageSHA50ecf04d4a5bfe71831b6f601e284b25fbb8940938b5a708933c3d93339cb494. CUAtoolfailedkernelassetsinitialization; browserUIrendercheckUNAVAILABLE, doNOTclaimrendered. Publicpagecommit8f4a4e220cf3684c693b4515164566fa9f2c5c58; publiclog/latestpatch821da6deee79bd7f7394d7b62bf58712059b74f1. Patch/license/manifest/docsONLYpublished. NoROM/save/sourcepush. Newrecordingnotbundled.
Continueimmediatelyfromreleased0032usingnew0033paths. Priorityrequireddependencies: investigateexteriorCutaccessoncleanpreCutstate(withoutguessingfromoldcopies), thenRoute9/10/RockTunnelpath/trainers/events/HMdependencies. PreservenativeworkingGym/puzzle; cosmeticjuniorclass/name/dialogueandPCexpansiondeferred. DoNOTholdnextreleaseforpolish. Keepnewcampaigncontentminimalfunctional/Yellowfaithful.

## October16 13:57UTC — 0033 Cut progression fix RELEASED
Causeconfirmed: historicalforest_progression.remove_kanto_terrain_gates removed nativeVermilion54object11sprite86 at1300,319 (flag0x16, std10000). Restoredexactnativeactorinappendedcityevent681, retainingallotherrows/warps/triggers. tools/kanto_cut_obstacles.py clonesnativebank146->1165, appendbadgehelper19, replacesONLYfirstCutCheckBadge6bytes withsame-sizeCall26 tohelper. Hive1preserved;Cascade9accepted, matchingalreadyapprovedmenubadgehook. Original19bodies preservedexcepttargetcall; onlystd10000dispatchscriptpointerchanged atmainoffset1025242. Allotherfieldmovesretainnativecode; noJohtomap/event/encounterresourceedits. This issharedCutpermissionconsistencyneededforKanto, notanengineexpansion.
Fourtest_kanto_cut_obstacles.pychecksPASS:all65536badgemasksacceptONLYHive/Cascade, exactactor+othercityrowsunchanged,originalbankarchive/relativebodycalls,preservationallunrelatedfiles/maps/executables. Candidate/releaseSHA304d391a6e37956f9e4ef4f8bad49e5f991293bdd6354b2c0840480fd0692e7c.
NativePURE0033-live-cut-pure-v1 copiednormallyearned0032Gymsave. Gymexitloadscitytree; movementblockedat1300,320 andwithoutCutpartyonlylookscuttablemessage. NativepersonalcompatibilityreadconfirmedexistingUmbreon197learnsCut. EarnedHM01taughtNORMALLYthroughBag, replacedHelpingHand(copiedsaveonly). NativeCutofferwithCascade (Kantobadges8/9/10, noHivegrant), nativeanimation/treehide andpathcrossingto1300,317PASS. Normalfanclub363entry/exitregrewtree; treeblockedfromoutside1300,318/offeredCutagain. CanceledCutthenNORMALSAVEcompletedcut-save-complete.jpg.
FreshPUREContinuefolder0033-live-cut-continue-v1 runner1896 copiedthatnormalSave. Continuedcity1300,318, nativeCutofferandactualCutanimationPASS. OrdinarywalkthroughclearedtileintoGym3656,22 confirmedcut-gym-entry-settled.jpg. No fixturetransport/RAMwrites/partygrantsin0033tests. ExistinghighlevelcopiedpartymeansNOTcampaignbalanceproof. Picture/audiopausedaftertests;server/tunnelsession91601retained.
RELEASE0033 folderbuild/0033-release-package-v1, ROM/ZIP localignored. Cumulativexdeltaroundtrip,ZIP,actualpageworker+wrongsize/hashrejectionPASS. Publicpage https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0033/index.html byteidenticaltestedlocalSHA5aca24840af893bff5cb988f8e862a6c013a85a21b84adee0706fa4c404088a3. Pagecommita7f1b0f490c7d5b82c704f134269b3a04b9adf48;log/latestpatch9e2648996d8c95b4deadf6a067fee6a6ba3693a4. BrowserUItoolstillunavailable; doNOTclaimUIrendercheck. Patch/license/manifest/docsONLYpublished;noROM/source/savepush. No newrecordingbundled.
LegacycityContinues mayretainoldactorlistwithoutnewtreeuntilbuildingvisit/reentry;thisisdocumentedonpatchpage. Newcityloadsusenativetree. No completedcustomizationsreverted. Preserve0033 andcontinueimmediatelyusing0034paths forrequiredRoute9/10/RockTunnel/HMdependencies. AuditnativeobstacleremovalhistoricalimpactwhereYellowrequiresCut;donotreinsertunrelatedHGgateobjectsblindly. NoPCexpansion/shippolish.

## October16 — 0034 Route9 private candidate; not released
Read-only HG/Yellow route audit started after0033 delivery. CurrentRoute9 map17 keepsnativeHGterrain/connections, sixHGtrainerpositions andnativeoptionalpickups; Yellow has nine trainers. Newroute9_yellow_reference.py extracts allnine exactteams/moves/three-dialogue-states plus10grassslots fromreadonlyRecovery. Ninthtrainertext is intext/Route9_2.asm; initialextractfailedclosedbeforeoutput, thenincludedsecondbank/hash andsucceeded. GenericnationalIDsreadDEXconstants (notGen1internalIDs). Sourcechecksumreference build/0034-route-audit-v1/yellow-route9-reference.json.
Existingroute6_trainers.patch generalizedwithoptional map_name/expected_count/templates arguments, defaultRoute6unchanged; all3Route6regressionchecksPASS. Newroute9_progression.py installsnineappendedtrainers813..821, aliasescommon1166, Yellow18..24teams andspecificmoves, Gen1grassrate15/species/levelsalltimes, inactivewater/fishingrates. Alloldrecords/resourceskept. NewRoute9event682 andwild155; no terrain/matrix edits. NativeHGsixlocations retained;3extras chosenfreefloorlocationsnearprojectedYellowpositions, subjectnativevalidation. TwoCuttreesat1347/1348,143 gateexistingtwo-widewesternapproach; onlyoneCutopenslane. OriginalHGsideCutobjectsNOTblindlyrestored. SharedCascade/HiveCutfixfrom0033retained.
Candidatebuild/0034-route9-v1/private-route9.nds SHAbb0b1aeb41a6e9586eb1b57030a955ee46bd5832f90f39ac8d18e1879800dcea. Fourtest_route9_progression.pychecksPASS: nineexplicitYellowteams/moves,actordispatch/vision+transitions,alltimewildtables,unrelatedfiles/maps/prefixarchivespreserved. NativeplaytestingPENDING. Notrelease.
IMPORTANT terrainreferenceLIMIT: collision-onlyBFSexcludingSurfabletilesstopsbeforeeastRoute9; someORIGINALHGtrainerpositions1410,153and1412,144haveseawaterbehavior0x15 (bridges/elevationnotmodeled). Comparisonprovesmatrixcells/permissionsbyteidenticalnative, notnewterraincorruption. DoNOTblindlyeditnativebridge/terrainbecausecoarseBFSfails. ItproveswesternCutchokeonly;fullrouteconnectionrequiresactualnativewalk.
Currenttestfixture0034-route9-transport-fixture-v1 initialtransportONLYcity54->Route917(1347,142), facingSouth, copied0033normallysavedCutparty. Noitems/Pokemon/badges/defeatflagsgranted. Currentrunner2219folder0034-live-route9-v1; Continuehelperunderway. VerifyactualROMpathandfixtureJSON. NextnativeCutentrance,trainerbattleandcontinuouspaththroughRoute9toRoute10/Center/RockTunnelentrance,normalSave/PUREContinue,thenpackagepromptly. OptionalTMTeleportconversion/exactterrainvisualalignmentdeferred; preserveworkingHGpath/props. No0034releaseyet.

## October16 18:25UTC — 0034 Route9 RELEASED
ROM build/0034-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0034.nds SHA256 bb0b1aeb41a6e9586eb1b57030a955ee46bd5832f90f39ac8d18e1879800dcea. Public patch https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0034/index.html pagecommit81d49927d0a4df7b445bdfc6347ff8a6c9af1f9b; publicpageSHAf63f1b143baeb992cc2977818ab7892caa32b79ea2ad8b2b0dc48fc65dd5dc8b matcheslocaltestedcontent after trailingnewline normalization. Cumulative xdelta roundtrip, ZIPcontent/CRC, actualpageworker and wrongsize/hash rejection PASS. Publiclogcommitd88af8cfa72ebb97b1e8be3b6fbfec164cd50de2 blob2897e9e88140b316055920510b068c543619d5cf latest0034. BrowserUItoolunavailable, noUIclaim. Ownernotifiedchat. Preserve0033/0034.
Native0034fixture2219 initialtransportONLYwestRoute9; noitem/Pokemon/badgegrants. Cutlefttree, Sandshrew24 battle/postbattle-norepeat, Meowth23 battle, continuousnormalwalking reached Route1018(1431,161), Center466entry/exit andRockTunnel108(46,10). Bridge/elevation traversable natively, coarseBFSlimitationconfirmed. Movementassertsegment6stoppedone-tile-short1396,151; screenshotshowednormalfield, extraRight8thenrestproceeded. NoROMbug. EnteringCenter/tunnel transitionsneedsettling; firstblackcaptures transient, notstall. NativeSavecompletedsave-complete.jpg. FreshPURErunner1908 folder0034-live-route9-continue-v1 loadednormallysavedfixturecopy into pure0034withouttransport, retained10846,10 andordinaryexitto181419,163 PASS pure-outside-settled.jpg. LiveAVpausedretainingserver/tunnelbetweenofflinework. SevenfocusedchecksPASSpreviously; nofullcampaignorbalanceclaim. CurrentnormalSaveinsideRockTunnel, actualunsavedpositionoutside. Next0035 paths forRoute10/RockTunnel requiredYellowprogression. DoNOTrepackage0034asnewprogress.

## October16 — private0035 Route10 candidate
Published0034 baseline preserved; nextcandidate0035-route10-v1/private-route10.nds SHAca5580ad4bfc2b1e46fb3f966045250201577a3cc74a49c0df38991062ffcaec. Newyellow_route_reference.py genericread-onlyYellowextractor verifiedRoute10six,RockTunnel1Fseven,B1Feightteams/moves/dialogue/grass; references0035-route10-audit-v1. route10_progression.py appendsRoute10sixtrainers822..827 via common1167, northmap18event683/south388event684, grass156alltimes. Originalterrain/warps/triggers/nontrainerNPCspreserved. Four focused testsPASSexactteams/moves/northsouthdispatch/wildtables/unrelatedresources. Nativepending. NativepowerplantNPCsretained; no optionalquestrewrite. Placement0powerplant1430,186;3north1429,167;1/2/4/5south1416,201;1430,205;1415,210;1425,215. InitialnativePURErunner83028 folder0035-live-route10-pure-v1 uses copiednormal0034RockTunnelsave; nofixturetransport/grants. Continuehelperunderway. Nextordinaryexitnorth,testJrF20Jigglypuff/Clefairy,northCenter; thenrequiredRockTunneltraversal/Flashdependencies andsouthtrainers. No0035releaseyet. Automationlatestbaselineupdated0034 and0035next; preservedACTIVE30minutescheduleasfound, notolder135minuteassumption.

0035nativeupdate18:41UTC: northJrFapproach/battleJigglypuff20+Clefairy20/victory/postbattletextPASS; nativeCenterhealingusedandreturnedtotunnel. Noartificialgrants. Existingcopiedsavecontains995itemstacks; oneexistingMaxRepelusedviaBagafterwildCubone13encounter, flednormally. Thisiscontrolledhighlevelcopysavefunctionality, notbalance. Tunnelcollision-onlyBFS211tilesnativewalkunderway; inputassertionsverifiedfirsttwofloorlegs. NativefirstB1Fladderarrivalsettles37,19notwarp37,18; detoured36,19northaroundladdernormalwalk. B1F8,7needsadditionalUp8ontophysical8,6warpthen1F8,7. Theseareguidecoordinatecorrections, notterrainbugs. Rawwarpeventcoordinate!=settledarrival. Current0035runner83028, PUREgame, 1F8,7transition. FourRoute10testsPASS; no0035release. RockTunnelYellowtrainers/FlashaiderewardNOTyetimplemented; identifiednativeDexOwnedopcode245, FlashTM70item397, Route2gate418actor0at6,7script1. KeeprequiredFlashdependencytask, noJohtochanges.

## October16 18:52UTC — 0035 Route10 RELEASED
ROMbuild/0035-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0035.nds SHAca5580ad4bfc2b1e46fb3f966045250201577a3cc74a49c0df38991062ffcaec. Public https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0035/index.html pagecommitac42a041907f737c08f2f90829ade409c6c551ee; publicpageSHA2c0eb5291da0ada62d36d036870793b59312e6268fa887cd405a314d05d428ea matcheslocalaftertrailingnewlinenormalization. Cumulative xdelta/ZIPactualdecoder/wronginputchecksPASS. Publiclogcommit3a44d0208c130ded170311834f60f6c046b70547 content71222e892ae696ec63d7518c9e9c2002cecf100d latest0035; ownernotifiedchat. FourRoute10testsPASS. BrowserUIunavailable; nofullnewgame/balanceclaim.
NativePURE0035 northJrF20Jigglypuff/Clefairy, southHiker21Geodude/Onix and19Onix/Graveler defeated. OrdinarycontinuouswalkthroughnativeRockTunnel108/452fourfloorchanges reached388southernRoute10, thenLavender53(1424,225). Southernguideassert5stoppedbecauseexpected388butactual53, legitimateboundarysuccesssouth-stop-05.jpg, notROMbug. MaxRepelexistingcopiedsave995stock, usedoneviaBag; noaddedgrants. NativeCenterhealingrestoredpartyPP. Darknesswalkwithguide doesNOTmeanYellowRockTunnelconversioncomplete.
NormalSaveLavendercompletedlavender-saved-settled.jpg. FreshPUREContinue51104folder0035-live-route10-continue-v1 retained531424,225. LiveAVpausedretainingserver/tunnel. Sourcecopiednormallysaved0034,taughtCutandtrainerworkcarried; nofixturein0035. ThreeotherRoute10traineroutcomes/powerplantaccessstillnativepending, disclosed. Allsixteams/source/moves/preservationcheckedoffline.
NEXT0036paths fromreleased0035: requiredRockTunnelYellowtrainers7+8,encounters, Route2Flashaidereward10owned (HG397TM70reusable; nativeCountNationalDexOwned245; map418actor0at6,7entry0), and onwardLavender/Tower/SilphScopestory. References0035-route10-audit-v1/RockTunnel1F.json/B1F.json andgrids/path alreadyread-onlyaudited. Nativecontinuouspathguide211tilesbutarrivalsdifferrawwarps; first45237,19, 1088,6,45210,20,1088,33. PhysicalB1F8,7needsUp8to8,6;8,33needsDown8to8,34. No terrainchangesneeded. Preserve0035and0034. PC10,optionalexpansiondeferred.

## October16 — private0036 Flash dependency
Currentbuild0036-flash-v1/private-flash.nds SHAaf843ce76da00552d67b842082236f36324d2985ec8e0f59d8b01e9745d7606f clonesRoute2southeastgate418aideentry0. NativeCountNationalDexOwned245 requires10, rewardsTM70Flash397reusablethrough existingTMengine; bagfullretry,one-timeflagA60,explanation. Alloriginalscripts/textpreservedappendclone;otherentry/actors/interiorunchanged. FlagA60auditedno30/31/32scriptuses/noactorflaguses,currentnativeCsourceonlyunrelatedHPbarliteral,flagdeclUNUSED. ThreefocusedtestsPASS494counts,bothcapacity/retry/one-timecases,originalscriptbodies/otherentry/unrelatedROMpreservation. NoJohtochanges.
Native91672folder0036-live-flash-v1 usesinitialtransportONLYLavender53->4186,8fixture, copiednormal0035save4ownedspecies, nogrants. Continuehelperunderway; ifsourceLavenderContinuedoesnottrigger, normalbuildingvisitrefreshrequiredlikepriorfixture. Nativeeligible/reward/fullbag/teaching/fieldFlashpending, no0036release. Current0035delivered, nextRockTunneltrainers7+8/encounters remainsrequiredafterFlashdependency. Do notcancel/deferessentialFlashasoptionalcosmetic.

0036nativepreflightcaughtBUG: initialv1gaveFlashbecauseopcode245countsSEEN, notCAUGHT. EarlierregexindexedonlyScrCmd_namesandmissedUnsetPhoneCallTriggerentryinfulltable. Correctedmoduleto246CountNationalDexOwned, regeneratedPRIVATEv2 SHAade12749956eeb0f33cf65244a01ce3c5c142e0b438a8b4cbbb7a9e04c52e152; v1NEVERreleasedorSaved. TestsnowincludeFULLnativetableallfunctionnamesandassert245seen/246owned. FourtestsPASS. Freshv2nativewithoriginal4-ownedcopyREFUSALPASS aide-correct-refusal.jpg. Noownerdatachanged. DO NOTclaimv1validrewardtest.
Eligiblefixture0036-dex-only-fixture-v1 changesONLYcaught/seenflagsandnativeCRCs inbothvalidgeneralsavecopiesfrom4owned[35,129,133,197] to10adds[1..6]. Magic/CRC/unrelatedbytepreservation/sourceunchangedassertionsPASS; party/items/badges/storyflags untouched inclA60initialfalse. ClearlylabeledfixtureNOTnaturalcatchprogress. Currentrunner91477 folder0036-live-flash-eligible-v1 usesv2transportfixturewiththisDexcopy; Continuehelpernext. Neednative397rewardonce/SaveContinue andteachFlash/actualcavefieldtest; no0036releaseyet. SDKnotcurrentlyonPATH, usedexistingverifiedPythonCRCmodel, noinstallationneeded.

0036v2eligibleNATIVEPASS: labeledDex-only10ownedfixtureactualaidegrantsTM70, BagFlash95->96visibleflash-tm-page12.jpg (not995; TMsstart95whileotheritems995). NativeFlashteachingtoexistingUmbreon succeeded,replacedConfuseRaythroughnormalfourmovesUI,flash-learned.jpg; Cutpreserved. SavepromptdisplaysDex10consistentfixture. NormalSaveinprogress,current91477eligible-v1. NextverifycompletebeforestartPURE0036-v2 via start-0036-flash-continue.py/continue-0036-flash-pure.py; sourcefolderexpectedflash-transport-private-fixture.dsv. VerifyrepeatdoesnotaddanotherFlashandmove/flagpersists. ActualfieldFlashdarkcavestillpending; canuseinitialtransportONLYtestfixturefromnormalSave toRockTunnel, nofield-flashflaggrants. No0036release.

0036v2 normalSavecompletedflash-save-complete.jpg. PUREContinue93241loaded4186,8andAideonlyexplanation/norewardnativePASS pure-aide-repeat.jpg. LearnedFlashpersistednormalSave; TM70count96visibleaftergift/teachingnotconsumed. Newfieldfixturefirstv1failedBEFORElaunchbecauseglobalrenamerewrotesourceDSVname; outputprivateROMpreservedbutnoclaimtest. Correctednewfieldfixture-v2 sourceeligible-v1/flash-transport-private-fixture.dsv, targetRockTunnel10846,10 initialtransportONLY; current19752folder0036-live-flash-field-v1. Normalearnedreward/taughtFlashprovenancewithDex-onlycountfixturecarried, noFlashfieldflaggrants. NativeactualFlashstillpending; no0036release.

## October16 19:09UTC — 0036 Flash RELEASED
ROMbuild/0036-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0036.nds SHAade12749956eeb0f33cf65244a01ce3c5c142e0b438a8b4cbbb7a9e04c52e152 (v2correctowned246,NOTv1seen245). Public https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0036/index.html pagecommitb04d21b0228cd533a8295d92a350a94747804a2a; publicpageSHA71f94e418674537028f0e0a57ea774544f6a33bd006e7b9bf7074ac022b53540 matcheslocaltestedcontentaftertrailingnewlinenormalization. Publiclogcommitd7d5c30226bc397384e180d1416eced1bf07e831 contentf33548ac01aad7ce3b5062f94374c06020ed883a latest0036. Ownernotifiedchat. Cumulativepatchroundtrip/ZIP/actualpageworker/wronginputrejectionPASS; browserUIunavailable. FourfocusedtestsPASS inclfullnativeopcodetable. Originals/privatefixtures/ROMsnotpublished.
Native4ownedrefusal; Dex-only10ownedeligiblefixture397receipt95->96; teachingFlashnormallytoUmbreonreplacedConfuseRay,Cutpreserved,reusableTMkept; normalSave/PUREContinueaideonlyexplanationPASS. Fieldfixture-v2 initialtransportONLY418->108 usednormallearnedsave, noFlashflaggrants. ActualpartyFlashmenu/nativesceneexpandedRockTunnelvisibilityfield-flash-settled.jpg PASS. Current19752folder0036-live-flash-field-v1 pausedAVretainingserver/tunnel. Noafter-FlashSaveclaimed. Thisiscontrolledcopiedhighlevel/Dexfixturefunctionaltest, notnaturallycaughtten/newgame/balanceproof.
NEXTnew0037pathsfromreleased0036: YellowRockTunnel1F7+B1F8trainers/encounters, requiredladdertraversal, thenLavender/Tower/SilphScope. Nativefulltunnelroute/fourfloorchanges alreadywalked0035withoutterrainchanges, sourceRefs/grids/path0035-route10-audit-v1. Flashdependencyresolved; doNOTreopenasunfinished. Keepfullcampaignnewgameproofpending. Preserve0036andallolderreleases. PC10unchanged.

## October16 19:12UTC — private0037 RockTunnel candidate
Newrock_tunnel_progression.py appends15Yellowtrainers(828..842), exactsourceexplicitmoves/dialogue/wilds alltimes for1081F/452B1F. Existingterrain/ladders/warps/triggers/pickups/Johto preserved; originalarcfileskept. v1preflightunreachablevoidpositionsrejectedbeforetests/native; correctedv2candidate39bf40df007bd8a0e070479f1b685f5e40646d7a427817042ade51cc1beea577 in0037-rock-tunnel-v2/private-rock-tunnel.nds. Placementnowrequiresreachablefromnativewarpcomponents AND preservesallwarpcomponentconnectionswithactorsblocked; nevereditsterrain. FourfocusedtestsPASS15hardcodedteams/moves,reachableactors/connectivity,grass+specialtables,unrelatedfiles/headers/prefixpreservation. 1Fpositions12,8;8,19;22,18;28,11;40,29;27,25;36,27. B1F16,13;11,13;6,8;25,24;35,13;19,27;38,8;29,27. No0037releaseyet.
Currentnative53434folder0037-live-tunnel-v1, initialtransportONLY418->10846,10 using0037candidate andnormal0036Flashlearned/rewardsave(withexplicitDex-only10speciesprovenance, highlevelparty/testingBag). Continuehelperprivate/continue-0037-tunnel.py NEXT. NeednativeFlash, representative1F/B1Ftrainerbattles,fullordinarynorth-to-southwalkwithnewactors,normalSave/PUREContinue,thenpublishmapcheckpoint. Nativepathguidesfrom0035stillvalidterrain,buttrainersinterruptandarrivaltilesoffsetfromrawwarps; dosettledstatusassertions. Previous0035tunnelwalk/Cubone wasHGencounters, not0037proof. Source0036releasedpreserved. Feednewtunnelunchanged, pausedwhileoffline;activateactualtest.

0037native19:17UTC: Flashworksagaininnewcandidate, enteredB1Fthroughfirstladder, manualHiker38,8battleMachop20observed. ExistingRepelhad20stepsleft; firstreapplycorrectlyrefusedwhileactive, thenwearoffmessageblockedmovement. ClosedmessageandusedanotherpreexistingMaxRepel994->993 natively; noitemgrants. CurrentB1Fplayer39,8battleHikerMachop20/Onix20 underway. IMPORTANT correctiontoearlier0036notes: latestactualbattleUIshowsFlash/Moonlight/Cut/ConfuseRay. TeachingthereforereplacedFAINTATTACK, notConfuseRay asintended; thiswasprivatecopiedpartyonly, owneroriginalunmodified. Flash/Cutpersistingstillvalid; doNOTrepeatincorrectmove-replacementclaim. NativecopyhasnoFaintAttacknow,useCutbottomleft62,310forbattles. AutoAselectedFlashfirstturn,MachopLowKickhit6HP, notparty/battlebug. Sourcepublishedgameunchanged.

0037native19:20UTC: actualFlashmenu/useexpandedvisibility; B1FHiker38,8 Machop20/Onix20 defeatedwithnormallyknownCut, repeatdialoguewithoutbattlePASS b1-hiker-repeat.jpg. Newtrainerart/team/scriptworks. FirstRepelreapplywasrefusedbecauseprevious250stepeffectstillactive; afterwearoffusedexistingMaxRepel994->993viaBag, no grants. Continuouscontrollerwalkfromnorth1FthroughB1Feast/top/westcorridor reachedB1F8,7; extraUp8triggered1Fladder, nextsettle8,6. Current53434folder0037-live-tunnel-v1. Needright56/up8to15,5 thenoldguide25..28arrives26,17; optionalmanualPokemaniac28,11testrequiresUp48from26,17, lineLEFTvision3 at26,11, thenactualbattleCubone23/Slowpoke23. AfterfinishDown48back26,17, oldguide29..30firstfloor/B1F thennormalarrival10,20. NewB1Ftrainer25,24blocksoldguide35; detour26,23down26,25maytriggerRIGHTvisiontrainerCharmander22/Cubone22. Completeordinarysouthpath,normalSave/PUREContinueandrelease0037. FourofflinechecksPASSbutnativefullnewactorpathnotyetcomplete. NativeDarkcavetraversal0035oldtrainersdoesnotreplace0037validation.

## October16 23:22UTC — execution resumed after usage interruption
At19:21UTC automatic approval review rejected Cubone battle inputs because usage limit was reached; those inputs DID NOT execute. No development claimed during interruption. At23:21reminder escalation succeeded; native runner53434stillat10826,11 inCubone23trainerbattle, priorprogressintact. Sent actualFight/Cutinputsnow; nativeoutcomeverificationnext. 0036latestreleased,0037v2privateunchanged. NeedfinishcurrentCubone23/Slowpoke23battle thencontinuoussouthpath,newactorchecks,normalSave/PUREContinueandrelease. Streamserverretained; priorliveAVwasnotpausedbecauseusageblockedcontrol, do notclaimotherwise. Currentnativeactiveactualplaytest.

0037native23:23UTC resumedCubone23/Slowpoke23PokemaniacbattledefeatedPASS f1-maniac-victory.jpg. Trainerapproachtriggerednaturallyat1F26,11whilewalkingnativeguide, noaddedbattlefixture. Ordinarycontinuedown26,17/leftladder10,18reachedB1F10,19transition; settledarrival10,20expected. Remoteviewstatus200checkedafterresume; currenttunnel/serverhealthy, noURLchange. Fullnewactorpathstillfinishing; no0037releaseyet.

October17 daily Discord post confirmed after delayed execution, message1561132266506297405. Covered latestreleased0036 and private0037, since lastconfirmedOct15; included0036 patch and GitHub plain-language log links. Persistent ledger updated and temporary draft removed. No Oct16 post or new game development claimed; no public Git push.

October19 delayed daily Discord update confirmed, message1561883774147493919. Explicitly reported no new documented gameplay progress since lastconfirmedOct17 post;0036 released/0037 private. Included GitHub plain-language log and0036 patch links. Persistent ledger updated, temporary draft removed. No new development/tests/public Git push claimed.

## October19 OWNER OVERRIDE — isolated 0037 engine expansion
Owner explicitly requests copying unfinished0037 and integrating suppliedhg-engineintoDUPLICATEasfinishedprototype, preservingoriginal0037. Gameplaytesting/bugfixand0038workWAITforownergoahead. DoNOTcontinueoldRockTunnelplaytestunderrecurringreminderwhilethisrequestactive. Currentsource0037-rock-tunnel-v2/private-rock-tunnel.nds SHA39bf40df007bd8a0e070479f1b685f5e40646d7a427817042ade51cc1beea577 copiedto0037-expanded-engine-v1/0037-preserved-input.nds, hashverified. EnginearchiveRecoveryreadonlySHA0cab9a9f4225a2d75de3507e30cee341577547d667755725c9e2e29833a16359 extractedprivate/hg-engine-0037-v1/hg-engine-main; bothignored. Provenance0037-expanded-engine-v1/provenance.json integrationPENDING. DoNOTcallfinisheduntilactualbuild/packaging; labeluntestedexperimental. Userauthorizesexpansionnow, oldnointegrationinstructionssupersededforcopyonly. No0038authorizationyet.
WSLhadnocompilers/make/cmake/cargo. AuthorizeddependencyinstallviaescalatedWSLrootaptunderwaysession53207(build-essential,arm-none-eabi,newlib,libpng/zlib,cmake/autotools,cargo/pythonvenv). ExistingRecovery/releases/owner savesuntouched. Preservecustomcampaign/scripts/trainers/starter/evolution/abilitychangeswhileexpanding; assessandmergeenginegeneratedresources/hooks, notblindlyoverwrite. PKHeXexpanded-saveincompatibilityknown; futureeditorworknotcurrentlyrequested.

## October 19, 2026 — isolated 0037 hg-engine expansion packaged (untested)
Owner authorized copying unfinished0037 and integrating the supplied expansion, with gameplay tests/bugfixes deferred until explicit0038 authorization. Original yellow-heartgold/build/0037-rock-tunnel-v2/private-rock-tunnel.nds remains SHA25639bf40df007bd8a0e070479f1b685f5e40646d7a427817042ade51cc1beea577. Isolated engine source is private/hg-engine-0037-v1/hg-engine-main; source archive SHA2560cab9a9f4225a2d75de3507e30cee341577547d667755725c9e2e29833a16359, Recovery unchanged.
Built expanded candidate yellow-heartgold/build/0037-expanded-engine-v1/Pokemon-Psyduck-Yellow-prototype-0037-expanded-UNTESTED.nds SHA2563dd95a51f8a444d3ede11d3851d67f2c85bc65d09ef9c841b4c718c53dacff66,193145824bytes. ZIP, cumulative original-USA-HG xdelta and self-contained browser patcher prepared. Compile/structural checks, patch roundtrip, ZIP integrity and actual page worker wrong-size/wrong-hash/exact-output tests pass. NO boot, gameplay, Mega battle, Save/Continue, migration or PKHeX/ALM test. Engine changes save layout: legacy compatibility UNKNOWN; keep saves isolated. Mega retains engine flag2518/held-stone gating; no campaign unlock event added.1535personal records include forms/placeholders, not1535 complete distinct species.30Pokemon boxes differs from deferred item-PC expansion.
Merged843trainer records, custom encounters, Golduck Water/Psychic, approved item evolution exceptions, custom Togepi levels, seven custom NPC models relocated after expanded followers, custom113..123/246item metadata/icons and seven customTM move indices/compatibility. Original customITCM byte-identical; custom script/event/matrix/art checks pass. Engine's overlapping native hook replacements still require runtime verification; preservation of bytes is not behavioral proof. Engine includes level100RareCandy logic but approved behavior remains untested here.
Build-only repairs: decompression now checks the compression pointer instead of assuming stock compressed size; five encounter hook targets corrected from ARM9 to overlay2; original ARM9 loader footer preserved. Source generators rebuilt after imports. Logs/reports and reproducible scripts private/*0037*expansion* retained. Partial intermediate ROMs in isolated folder are NOT releases.
Public patch page committed4d05912175fd83a67541b14e6830a3f04020119f at psyduck-yellow/prototype-0037-expanded/index.html; remote delivery verification and dated public log update pending at this note. Do not treat interim hash8c9b/1be6 as final. Live server was not reachable; no tests or stream restoration attempted under the owner's testing deferral. STOP after delivery and wait for explicit0038 go-ahead; do not resume old0037 gameplay or automatically begin0038 from recurring reminders.

### October19 final delivery verification — supersedes publication-pending paragraph above
Experimental0037 expansion delivered. Public page https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0037-expanded/index.html downloaded byte-identically to tested page (SHA2568590cc1ed4762011ff50cdb18726a3194163141113c2270e2eda985cc36e3a31). Initial compressed download timed out; identity-encoding full download completed and matched. Public dated log/latest link committed5067af3f3f51e8cbd5da42ce31772704faf1a969; local log synced and Git blob matchesa5fde57f5e1256134afa870d4323849031fe2981. Local delivery ZIP is psyduck-yellow/build/0037-expanded-engine-v1/Pokemon-Psyduck-Yellow-prototype-0037-expanded-UNTESTED.zip, ignored via local .git/info/exclude. FinalROM remainsSHA2563dd95a51f8a444d3ede11d3851d67f2c85bc65d09ef9c841b4c718c53dacff66. Public artifacts are patchpage/credits/license/release notes/manifest/docs ONLY; noROM/save/source push. No gameplay tests. Await explicit owner0038go-ahead; recurring override already updated. Originalunfinished0037 hash rechecked unchanged.

## October20 OWNER AUTHORIZATION — begin0038 boot/save bugfixing
Owner reports expanded0037 rejects old save and black-screens with no audio after Oak/player/rival naming. Owner explicitly answered Yes—begin0038bugfixing. Previous wait restriction lifted. Preserve released0037SHA3dd95a51f8a444d3ede11d3851d67f2c85bc65d09ef9c841b4c718c53dacff66 and unfinishedoriginal0037SHA39bf40df007bd8a0e070479f1b685f5e40646d7a427817042ade51cc1beea577. New0038paths, isolated clean new-game reproduction first; old-save diagnosis/migration on copies afterward. No fix/runtime diagnosis proven yet. Static engine configuration enables ALLOW_SAVE_CHANGES and30PokemonBoxes; this changes save structures and provides no verified legacy migration. Do not call old save corrupt. Preserve all approved customizations. Automation prompt updated; existing weeklyMonday09:00 schedule preserved.


October20 clean-new-game reproduction CONFIRMED on unchanged released0037 SHA3dd95a51f8a444d3ede11d3851d67f2c85bc65d09ef9c841b4c718c53dacff66. No imported save, normal Oak intro/boy/playerA/rivalA/naming completed; persistent black screen when entering world. Evidence0038-boot-reproduction-v1/black-after-naming.jpg and clean-new-game-failure.json. PCM callback returned nonzero samples; do not claim audio was verified silent. User reports silence. First runner stopped, feed paused; accelerated unchanged0037 diagnostic replay prepared with local-only state/RAM capture on emulator owner thread, new0038-boot-diagnostics-v1folder. No game-code fix yet. Viewing tunnel restored token-free https://certificates-fully-literature-biographies.trycloudflare.com/ ; view credential ownerchat only, control private. Patcherfix already published2ec17cf44e1611f8de0db553a1b0a680b560ebe7: smallpage46KB fetches unchanged31MBxdelta on click; full localChromeUI successful. Public page and patch downloaded, patch hash matched05dae8773b3309562f66ba705e26d1d13a0482df6e109f991eda777116a6066f. Prior note update was blocked by approval-usage limit; this entry restores checkpoint accuracy.


## October20 RELEASE0038 — expanded engine startup repair and Mega bedroom controls
Delivered https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0038/index.html. ROM SHA256 e86da7667b8347043b61fb11a63a60ecca54c840ab0120d58689457e025c80d3, local yellow-heartgold/build/0038-release-v1/Pokemon-Psyduck-Yellow-prototype-0038-EXPERIMENTAL.nds. Preserve all releases, including both0037 baselines. Publiccommit474f84afb7b0ab987c9152d1425eadf55561c81d has seven patch/doc paths only, noROM/source/save. Publicpage/repairpatch/manifest/notes HTTP200 and byte-identical viaWindowsInvokeWebRequest. Full localChrome file-selection/Create/Download yields exact finalSHA. PublicChrome buttonlocator timedout: do not claim remotebrowserflow PASS. WSLfetch403 was environment-specific; Windowspublicfetch succeeded. WindowsGit lackedcredentials; canceledpush and usedGitHubconnector. Partial unpublishedGitcommitbc4190 is not a release. Browser uses two verified stages (existing public0037 patch and10,238-byte0037-to-0038.xdelta); originalUSAinput only. Localcumulativepatch alsoverified. ZIPintegrity PASS.
Rootcause: tools/narcpy.py extracts1171members with4-digitnames2_0003/2_0953 but narcs.mk creates3-digit2_003/2_953. Sortedpacking insertsnewmembers andshifts indices; repeatedbuildcompounds. Script149 thenexecuted wrongtext/UIcode beforefieldoverlayloaded, ARM/Thumb mismatchblack screen. Restored ALL1171originalcampaignfieldscriptbanks, notonlyappendedcustombanks. Preserve expandedenginecode/data. Guard allbankindices, notmerely965plus, beforefutureenginebuilds. TemporarytraceROMs/RAMwrappers are diagnostic only, never releaseinputs; stale before-world state replay gave misleading exception, usefreshboot.
Nativepass: cleannewgame through suppliedOak/player/rivalnaming tobedroom; movement/stairs; normalSave/freshPUREContinue intohouse; normalstairsbackbedroom. Nofullcampaign/balanceclaim. Currentreleased0038bedroom map506script1171/text927/event687 retainsfouroriginalscripts/PC/interior. Itemballobj20(4,5),CharizarditeX660,one-timeflag0xB20,full-pocketretryimplemented. Redstandingflagpanelobj21sprite400(8,5) togglesMega2518ON/OFF viaA; startsOFFunlessused. EngineCheckCanDrawMegaButton checksflagandmatchinghelditem/species/form, noMegaRingpossessioncheck. Nativebag660x1 andONRAMflagverified, OFFdialogueverified. NoPokemongift. Mega battle/reversion, full-pocketnativecase, post-pickupSave/Continue stillpending. Legacy save conversion andPKHeX/ALM compatibility NOTverified. Use separatefolder/newgame, preserveoldsave. Native server0038-mega-test-v1 currentlyvideoOFF; privatecontrolhelpers preserved, tunnel retained. Check serverstatus beforestartinganotherowner.
Next authorizedwork: verifybedroomstateSave/Continue; legacy-savecompatibility/migration oncopies; earlycampaignandbattle/Mega regression. Newprivatepaths0038-compatibility-v1; nooverwrite0038release. Optionalcampaign-firstdeferredchecklist remains. OwnerrequestedScheduledTaskupdatesatinput-readycheckpoints; currenttaskupdated preservingitsactual4-hourinterval.

## October20 governing owner instruction — PKHeX0038 first;0039 waits for owner confirmation
Current task: upgrade the existing full PKHeX build for0029 to safely edit0038 expanded-engine battery saves (.dsv/.sav), retaining0029/retail support, all30Pokemon boxes, expandedbag/Dex/species/items/ability encoding, nativechecksums andemulatorfooter. PKHeX edits saves, notROMfiles. No compatibleeditor released yet. Source private/PKHeX-Psyduck-Yellow; plugins private/PKHeX-Plugins-Psyduck-Yellow. WindowsSDK private/build-tools/dotnet-win-10.0.113 (10.0.113); systemdotnet hasruntimeonly. Existingprivate/pc-storage-layout-agent-v1/native-layout.json listsall42legacysizefunctions; expandedlayoutverified0038-boot-fix-v1/expanded-layout.json. Do not silently assume nativeoffsets.
After editor is delivered, wait for owner's explicit confirmation before resuming prototype0039 gameproduction. First0039bug: after defeatingLtSurge, video turnsblack whileaudio remains/controluncertain, especiallyFlytoCerulean and enteringPokemonCenters. Reproduce separately, preserve0038release, new0039paths. No0039gamecodework beforeconfirmation. This supersedes prior automaticcontinueinstruction forgamework whileeditorconfirmationpending.
Additional0038evidence completedafterrelease: yellow-heartgold/build/0038-mega-test-v1/persistence-report.json confirmsnormalSavecounter2, savedMega2518ON, freshContinuebedroom, CharizarditeX660quantity1 andpickupflagB20persistent. ExtraAafterContinue intentionallytoggledOFFagain; don'tmisdiagnoseRAMOFFassavefailure. OldsavecompatibilityresearchpausedforPKHeX. Lastlegacyrunnerprivate/start-0038-legacy.py (originalunfinished0037ROM/copied0025save) maybeactivevideoOFF; attemptedcontrolblockedbyapprovalreviewusagelimitandNOTexecuted. Defaultworkspace readtoolsavailable; WindowsSDKconfirmed. No publicsourcepush authorizedbycurrenttask; preserveGPL/sourceobligations ifeditorredistributed.

### October20 PKHeX0038 validation in progress (not delivered)
Source adds separate expanded-save detection/offsets, 30 boxes, ROM-derived species/move/item/ability/personal/form data, expanded bag physical capacities, ten existing PC slots, wide ability encoding, hidden/swap ability flags, mint and Hyper Training fields. Preserve originals/releases. Core probe passed copied0038 DSV/raw roundtrip, checksums/footer, box30/name/wallpaper, every pocket boundary, expanded encrypted Pokemon fields, event flags and legacy0029/retail layout checks. Current tests rerun after Hyper Training additions. GUI build passed earlier; isolated control harness had initialization failures, now replaced by full Main initialization; GUI acceptance still pending, do not claim editor ready. Native unchanged released0038 loaded minimal editor export through ordinary Continue into bedroom; trainer card visibly shows edited424242 money (native-continue/continued-field.jpg and trainer-money.jpg). No state/RAM writes. Video/audio paused after check; server retained8080. This is focused save-export validation, not campaign/Mega battle verification. Outputs yellow-heartgold/build/0038-pkhex-v1; probes there. Scheduled task updated with editor-first and WAIT for owner confirmation before0039; first0039 bug remains post-Surge FlyCerulean/Center blackvideo/audio present. No0039 work yet. Finish GUI roundtrip, expanded flag/form/boundary recovery and legacy tests, package full editor+matching source/license, then deliver and wait for confirmation. Previous usage-limit interruption prevented a Continue button input; subsequent resumed input succeeded. No background development claimed.
## October20 PKHeX0038 editor delivery checkpoint
Completed and packaged the full existing Windows PKHeX fork for released0038 expanded battery saves; older0029 and retail support retained. Application: yellow-heartgold/build/0038-pkhex-v1/release/PKHeX-Psyduck-Yellow-0038-v1.zip (23214313 bytes, SHA256655b84fc795414314cf2389d07d4bc55fbb48eaad8fefbae1804029030ae0616). Corresponding Windows source/GPL archive: samefolder/PKHeX-Psyduck-Yellow-0038-v1-source.zip (28630967 bytes, SHA2560328cafb735ed61ee6b87b1cd0e486d955f79cc6be82e5d8ed6376d0949b04d1). Unrelated Android APK downloads excluded. ZIP integrity/noROM/save/state checks pass; no public source or ROM push. Source private/PKHeX-Psyduck-Yellow with PSYDUCK-YELLOW-0038.md instructions. Source/probes/resources correspond to tested binary; wholeUI scaling retained.
39 core checks PASS: autodetection, native/checksum/footer/rawsave roundtrip,30boxes/box30metadata, physical bag pockets/PC10, engine IDs/data, wide abilities/EXP, hidden/swap ability, mint/HyperTraining bits, eventflags, Dex, newestCRC-valid partition and damaged-newest fallback. Existing0029 probe PASS including3starters, HA/shiny/legality/PC/retail isolation and real copied-save party/story/footer preservation. Nine full-Main Windows checks PASS: actual engine speciesname/ID, heldstone, expandedmoves/EXP, storedwideability/slot, CharizardMegaform, naturallywideability, Inventory and1535recordDex UI. Initial test-harness initialization errors resolved; no remaining reported GUI acceptance failure. A concurrent build caused a compiler output lock; reran sequential/no-project-reference probes successfully, no skipped required check. Native released0038 normalContinue loaded minimal editor export into bedroom and trainer card visiblyshowed424242 editedmoney, noRAM/statewrites; this is focused save validation, notcampaign/Megabattle testing. AVpaused/serverretained8080 aftertest.
LIMITS: editor does not migratelegacy0029campaign saves toexpanded0038. Expandedretail legality/AutoLegality unavailable; do notclaimofficiallegality or expandedALM compatibility. ActualphysicalPCstorage10; deferred20-to60 unchanged. Unknown engine form preview usesneutral sprite; actual ID preserved. Sources/saves/ROMs remain localignored. No0039gamechanges.
OWNER CONFIRMATION GATE: This editor delivery is complete. WAIT for explicit owner confirmation that this0038editor task is done before beginning0039. Recurring reminders must not bypassgate. First0039 task afterconfirmation: post-Lt.Surge blackvideo/audio retained, especiallyFlyCerulean andPokemonCenterentries, controlsuncertain; investigate oncopies/new0039paths, preserve released0038. Thencontinuecampaign-first/restorationchecklist. Scheduled task updated accordingly.
October20 editor delivery workaround: owner reported Could not download artifact for UNC chat links. Verified identical application/source ZIPs copied to C:/Users/thata/Downloads/PKHeX-Psyduck-Yellow-0038-v1.zip and matching -source.zip. Extracted app C:/Users/thata/Downloads/Psyduck-Yellow-0038-Editor/PKHeX-Psyduck-Yellow-0038/PKHeX.exe. No existing files overwritten; both ZIP SHA256 values matched original packages. Wait for owner editor confirmation before0039 remains in force.

## October20 OWNER CONFIRMS editor; narrow game-fix release then HALT
Owner confirms PKHeX worked. Authorization resumes ONLY to investigate/fix post-Lt.Surge blackvideo/audio-retained issue, prioritizing their observation that it did not occur with Mega Evolution feature flag OFF. Compare matched ON/OFF saves/transitions first, then verify fix. Owner now requests package/publish a new0038 testing revision after fix, NOT automatic0039 progression; preserve existing0038 release and publish distinct revision page/artifacts (e.g.prototype-0038-r2). After delivery HALT all development and await further owner instructions; recurring reminders must not start0039 or campaign work. Currentinvestigationpending. Existing released0038SHAe86da7667b8347043b61fb11a63a60ecca54c840ab0120d58689457e025c80d3 unchanged. Need first inspectMega2518(0x9D6) flags/battlecleanup/fieldtransition dependencies. Any prepared fixture use must be labeled, not presented as fullcampaignprogress.
### October20 0038-r2 diagnosis resumed after usage interruption
Latest task remains fix Mega-related post-Surge blackvideo, publish distinct0038revision then HALT. No fix/release yet. Staticaudit releaseROM: flag2518 appears only bedroom1171 scripts and no actor-visibility flags, no direct campaign-script collision proven. Matched prepared0038 fixtures: copied genuine0033 trainer/flags (badge7), test Charizard100 with held660/Fly; notcampaignplaythrough. NativeContinue Cerulean52 -> walk Center428 withMegaON displayed normally, exit/re-entry passed; flag alone not yetreproduction. Earlier preparedContinue directlyinsideGym restoredstale roomobjects/noSurge; invalidbattlefixture, doNOTclaimbattle result. V3 startsoutsideGym54 at1295,320 thenactualnativeentry loadsactors; copiedKantobadges reduced3/preSurge, trainerflag0x64F cleared, leaderhide2F0 cleared, solvedpuzzle/stopflags prepared. NativewalkviaoutsideaislestoSurge6,5 andrealintro dialogue underway, MegaON. Currentrunner folder0038-r2-mega-transition-v1/gym-v3-mega-on, port8080; metrics wrapper private/cloud_test_suite_0038_metrics.py. private/r2-controls.py boundedJSONactions; facingUP beforeA. Command to faceUP/talk originallyblocked automaticapprovalusagelimit DID NOTexecute; resumed successfully onownerResume. Need completeactualbattle/Mega andFly/Center transitions thenmatchedOFFcontrol, diagnosebeforepatch. Explicitquestion pending: didowneractuallyMegaEvolveduringSurgebattle oronlyswitchON? No replyyet.
Viewing tunnel restored/remotestatus200: token-free https://format-bios-millions-signed.trycloudflare.com/ ; authenticated ownerlink postedchatonly, controlprivate. Publiclog stream/diagnosis updatecommit4dcecb7789b9db6d5f45884d8a6c7b3e82e13320, noROM/source publication. AVcurrentlyONforactualtests; pausebetween. Diagnosticcapturebefore-surge inoldgym-mega-on notsuccessfulbattlefixture. Helper/provenancefilesinprivate/buildfolder; originalreleases/savespreserved. Note editor MapUnlockState property's raw offset0xBAE7 appears unmappedinexpandedprofile; separatefutureaudit, not establishedasthisgamebugcause.
## October21 owner scope — custom assets intake; per-Mega design approval required
Owner stopped development and then set the Surge/Fly/Center black-screen investigation aside; possible contribution from converted legacy save is UNVERIFIED. No fix or0038-r2 release delivered. Owner clarified Mega switch was ON but no actual Mega Evolution during their Surge battle. Preserve diagnostics; do not resume investigation automatically. Earlier diagnostic save-state replay black field is not reliable proof: fresh native Continue with actual Mega selection returned to the Gym visibly. Native Center-entry attempts ended the runner; cause not established. No cause or compatibility claim.
New authorized task: inspect supplied recovered custom Pokemon art archive and ask for desired implementation BEFORE adding each new Mega Pokemon/Stone. New Megas use existing engine form/Pokedex handling; NO separate Mega Pokedex entries unless owner later says otherwise. Do not infer stats/types/abilities/availability from artwork, package numbering or attached checklist instructions. No custom Pokemon, Stone, art or ROM integration performed. Existing released0038 remains unchanged. General scheduled development stays PAUSED; this narrow intake does not authorize0039 or other campaign work.
Archive read-only: C:/Users/thata/Desktop/The Lab/Psyduck_Yellow_Custom_Pokemon_Asset_Library_RECOVERED.zip SHA256ff82824efc3933806e2e0ac8bc249b92a019102ffb12c738081d6fe3f93fd7a2,148entries. All147manifest-listed entries match SHA256. Independently decoded28indexed battle PNGs: all80x80, indexed, transparent index0 and <=16distinct used colors. PLTE tables padded256entries; not256usedcolors. This is file/header/color-count validation, NOT importer or in-game/visual approval. Two-frame sheets documented duplicate frames, not animation.
Contents: basePsyduck; MegaPsyduck and shinyMegaPsyduck front/back; Psyduckite32/64RGBA; candidate menu icons; ten custom Eeveelution sets Brawleon/Ferreon/Zephyreon/Venomeon/Duneon/Chryseon/Strateon/Wraitheon/Wyrmeon/Novareon. Wraitheon has shiny artwork. No other custom Mega/Stone set found. Source masters retained in original ZIP; archive documents treated as asset information, not execution authorization. Source notes flag Chryseon/Wraitheon/Wyrmeon art differences for later owner review. Reports/private scripts: private/custom-assets-recovered-inventory-2026-10-21.json and private/inventory-recovered-custom-assets.ps1. Pending owner design for first MegaPsyduck/Psyduckite: eligibility, typing, six base stats, ability, stone acquisition; normal engine Mega/reversion rules assumed only after owner's design is agreed. No new approval granted by receiving assets alone.

## October21 — Eevee New Horizons visual guide received
Read15page C:/Users/thata/Desktop/The Lab/Eevee-New-Horizons.pdf SHA589a2dccde078ff433a95d95e03411712c188f10d96eada3c50e6ad39659b1a0. Local renders/text/design summary: private/custom-design-review-2026-10-21/DESIGN-REFERENCE.md. Reference outlines9ordinary newEeveelutions plusStellarNovareon, Eonite18single-type sharedMegaEevee variants returningtoexactsource species, separateNovareonite personalMegaNovareon. Stoneartfixed, held/reusable/deliberateactivation/oneMegaallowance, proposedKeyStonegating. Treat as designreference, NOTimportauthorization. Source's separateMegaDexentries conflictwithowner'slatestNOseparateMegaentries: ownerwins; noMegaDexentrieswillbeadded. Existing-speciesreplacementDextextlikewiseonlyreference. Stats/abilities/moves/evolution/acquisition/Stellarbattlerules unspecified; obtainagreementbeforeimplementation. ZIPhas10basespecies butnomatchingMegaEevee/MegaNovareon/Eonite/Novareonitespritefiles. PDFillustrationsarenotvalidatedDSsprites. NoROM/engine/artchange; schedulerremainspaused; pendingownerchoiceandperMega/Stonespecification.

## Owner-approved starter restrictions — October 21, 2026
- Only the original starter Psyduck may activate Psyduckite. Other Psyduck are ineligible.
- The starter Psyduck cannot evolve into Golduck. Preserve other Psyduck's approved evolution into Water/Psychic Golduck.
- Only the original starter Eevee may evolve into Novareon. Other Eevee are ineligible.
- Novareonite eligibility belongs exclusively to the Novareon evolved from that original starter Eevee, consistent with the reference's Novareon-to-Mega-Novareon activation. Do not grant ordinary Eevee a direct Mega Novareon transformation.
- These restrictions must follow the individual starter Pokemon through party/storage/evolution; do not identify eligibility by nickname, current party position or species alone. The persistent identification mechanism and existing-save handling still require design/verification; no implementation or compatibility claim.
- This approves eligibility restrictions only. Mega stats, ability, Psyduck Mega typing, evolution method, Stone acquisition and Stellar rules remain to be agreed before new Mega/Stone integration. No ROM changed. No separate Mega Pokedex entries. General scheduled development remains paused; black-screen investigation stays deferred.

## Owner clarification — October 21, 2026: internal starter variants and Eonite
- Owner proposes separate NEW internal species for starter Psyduck and starter Eevee to simplify exclusive behavior. This is a proposed implementation approach, not a completed change or evidence of easier total integration. Evaluate dedicated internal IDs versus marked forms before allocating IDs. Preserve existing approved starter properties and ordinary Psyduck/Eevee behavior; consider displayed species names, Dex aliasing, follower assets, evolutions and PKHeX support. Do not silently convert existing saves.
- Eonite is usable by ALL Eevee and all seventeen ordinary-type Eeveelutions (including the nine proposed ordinary-type custom evolutions), whether starter-derived or not. The starter Eevee itself is eligible. Starter Eevee's ordinary evolutions are eligible. Novareon is excluded from Eonite.
- The starter-only rules remain: Psyduckite only for starter Psyduck; starter Psyduck never evolves into Golduck. Only starter Eevee evolves into Novareon; that Novareon alone uses Novareonite. Novareonite does not transform unevolved Eevee directly.
- Pokedex correction: Novareon IS a genuinely new Eevee evolution and receives its own species entry. Mega Novareon belongs WITHIN that Novareon entry as its Mega form, like other Megas. NO separate Mega Novareon entry/number. An earlier assistant assertion about a dedicated separate Mega entry was explicitly corrected by owner and must not be followed.
- Current source audit confirms species-based Mega lookup (monindex + held-item + base/target form) and ordinary IDs in starter tooling; separate starter IDs could simplify eligibility checks but require mapping/preservation across other systems. No engine/ROM/asset integration done. Stats/abilities/evolution triggers/acquisition/Stellar battle rules remain pending owner specification. Scheduled general development remains paused; old black-screen investigation stays deferred.

## October21 — starter Eevee / Mega Eevee one-test checkpoint: HALTED
Owner authorized new starter Eevee plus its Mega form with inherited stats/ability and provisional art, one native transformation test, then HALT/report. Private experiment yellow-heartgold/build/0038-starter-eevee-mega-v1/Pokemon-Psyduck-Yellow-starter-Eevee-Mega-TEST.nds SHA256 c6891f2cb7a1c2f1cae93a5b91339c1bc17a722d48ec5682a473a3813689749d. Appended starter species1561, Mega data record1562 (species1561/form1), held Eonite3145. Copies native Eevee battle art/CharizarditeX item art as placeholders; no finalized Mega art. Build succeeded. Static checks preserve all original campaign script banks, original ITCM, regular Eevee records and original95Mega table entries; isolated engine checks pass new eligibility/form mapping and narrow starter gift wrapper. These checks do not establish absence of runtime conflicts.
Native test ATTEMPTED ONCE October21 11:23UTC: copied genuine expanded0038 battery save (NOT legacy migration), prepared level100 starter1561/held3145/Mega2518ON outside Surge Gym. Runner started, accepted video and three A-button Continue inputs, then exited (process exit1); status request failed connection-refused. Last metric frame2907, phase running, ram null, error null. No diagnostic traceback identifying cause; no completed field/battle screenshot, no Mega transformation or reversion evidence. Do NOT claim native success, a specific game crash cause, save compatibility or starter-gift acquisition verification. Capture/provenance/live-metrics preserved in native-once. Emulator stopped; no active picture/sound feed remains. No fixes/retests after this failed attempt; owner requested halt after one test. No new release/public patch produced; released0038 unchanged. Starter gift path, battle/form/reversion, bag acquisition/editor/follower behavior remain native-unverified. This scoped Eonite table row covers only new starter; eventual all-Eevee/all17ordinaryEeveelution support remains required future work, Novareon excluded. No other custom Pokemon integrated. General development/scheduled task remains PAUSED, old black-screen investigation deferred. Await explicit owner instructions before diagnosis/retest or further implementation.
## October21 — Eevee Continue failure diagnosed; private field fix verified
Owner authorized determining cause/necessary adjustments and reporting the proposed solution once found. This lifts the previous one-attempt halt ONLY for this diagnostic scope; general campaign/0039/old Surge investigation remains paused.
Controlled native Continue diagnosis in 0038-starter-eevee-mega-v1/diagnosis-v2: unchanged genuine native0038 save/released ROM loads; ordinary Eevee133 with existing item660 loads experimental ROM; ordinary Eevee133 with Eonite3145 also loads; appended starter1561 with existing item660 fails. Baseline ROM with unsupported1561 fixture also fails and is NOT evidence of a general emulator defect. Controls share the same prepared map54 location; no migration or campaign-completion claim. Corrected fixture provenance for diagnostic controls to actual species/item arguments (the initial builder report text had hardcoded1561/3145 while output bytes followed the supplied arguments).
Root cause: the initial hook aliased only follower asset/index lookup. A separate earlier get_mon_ow_tag path (0x023DA73C) still generated MON_OVERWORLD_TAG_START2500 + new species1561 =4061 (0xFDD), outside supported follower graphics. Interpreter diagnostic RAM shows follower object graphics0xFDD, callback+0xC4=0xE92D4000 (ARM instruction bytes, invalid callback). Native ARM9 dispatch at0x0205F478 BLX r1 jumps to invalid value; JIT host SIGSEGV traced at desmume_libretro.so+0x9A37B. This is not a Mega battle failure and does not establish any cause for the separately deferred owner Surge/Fly issue.
Applied narrow candidate fix to NEW output only: alias1561/1562 to Eevee133/form0 at get_mon_ow_tag BEFORE graphics/tag selection; ordinary inputs replay original prologue. Also append missing follower model-form records while preserving every original record. Existing starter species/form/battle IDs remain distinct; do not globally replace species with133. Candidate diagnosis-v2/Pokemon-Psyduck-Yellow-starter-Eevee-Mega-field-fix-WIP.nds SHA2562c2bd3659c609b6d90ec86a0c66195f43aff2203487f991e0c8319f9a0661600. Hook appended at0x023DE328. Same original1561/Eonite3145 native fixture now completes Continue and stays running through4500 frames, fieldmap54 party1; visible field screenshot field-fix-control/last.png. No native Mega battle/reversion, starter acquisition, full follower movement, bag/editor, or old-save migration claims. All original releases and v1 failure preserved. No public release. Proposed solution found/reported; HALT pending owner directions on next gameplay test. Automation remains PAUSED. Evidence field-fix-build.json, native-diagnosis-report.json, per-control CPU/RAM/status, copied native crash traces.
## October21 — prototype0039 published/delivered; HALT
Owner explicitly requested publishing the current fixed Eevee experiment as prototype0039 with normal public patch page, then awaiting instructions. Released byte-identical candidate SHA2562c2bd3659c609b6d90ec86a0c66195f43aff2203487f991e0c8319f9a0661600, preserved under yellow-heartgold/build/0039-release-v1/Pokemon-Psyduck-Yellow-prototype-0039-EXPERIMENTAL.nds and local ZIP. No additional gameplay changes. Public patch https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0039/index.html . Publication commit b485392518137183be23232f7411b47e5007a422 includes only six new0039 patch/page/manifest/notes/credits/license files and dated public development-log/latest-patch update. No ROM, save or unrelated source push. Earlier releases preserved.
Browser accepts originalUSAHeartGold, automatically applies existing0037 expansion, published0038 repair and new80627-byte0038-to0039 delta; each stage hashes its input/output. Native patch roundtrip and local ZIP pass. Full WindowsChrome local-served page selection/Create/Download PASS exact0039hash, no page errors. Public hosted six files all HTTP200 and byte-identical from Windows network; publicdatedlog/latestlink also matches. WSLurllib publicrequest returned403; publicChrome UI navigation could not locatebutton (timeout), so do NOT claim full remoteChrome Create test. Actual localChrome flow plus hosted-byte equivalence verified. Evidence browser-check.json, public-verification/report.json. No further native gameplay tests added during packaging.
Release limitations explicit on page/notes: inherited battle data/placeholderart; prepared nativeContinue intoVermilion verified, Mega transformation/reversion and new-game starter acquisition NOTverified; full follower movement/new-ID bag/editor/evolution/Dex behavior unverified; Eonite no normal pickup, scoped eligibility onlynewstarter1561 soallVeeVee expansionpending. Existing bedroomCharizarditeX/switch retained; no othernewcustomPokemon. Oldpreexpansionsavemigrationunsupported; previousSurge/FlyissueNOTclaimedfixed. Generalcampaignunfinished. All sources/privateuploads/saves/ROMsremainlocalignored. DevelopmentHALTED afterdelivery atownerrequest; scheduledtaskPAUSED. Do not resumefromreminders; awaitexplicitownerinstructions.
## October21 — authorized Mega Eevee artwork imported privately
Owner requested using supplied images (conversion allowed) for starter Eevee's Mega sprites only; base Eevee may remain unchanged. Supplied recoveredZIP contains no namedMegaEevee front/back pair. Inspected supplied Eevee-New-Horizons.pdf page7 reference and adapted its sandy-brown body, cream star ruff, single large tail, long ears/amber eyes into front/back pixel art with builtin image tool. Normal variant uses pearly-silver ruff gem, following guide's Normal accent. This is an AI-assisted adaptation of supplied illustration, not a pre-existing ZIP sprite. Generated original C:/Users/thata/.codex/generated_images/01a12fa4-99b9-7270-a2f8-828af71c8984/exec-87273287-6b17-4531-b71d-d66860ce5f82.png retained; project copy source-adaptation.png. No originals modified.
Private work folder yellow-heartgold/build/0040-mega-eevee-art-v1; NOT a published0040 release. New ROM Pokemon-Psyduck-Yellow-Mega-Eevee-art-WIP.nds SHA2561114ae2cc11777868150d95caa4ad5378d311b28ad76769c8dc1cad88fec71a3, built from released0039. Replaced ONLY six sprite/palette members9372..9377 for Mega datarecord1562 in a/0/0/4 (bothgender front/back, normal/shinypalette). Ordinary133 and starter1561 base graphics/palettes all byte-identical; all other sprite members preserved. No gameplay/stat/stone/script/othercontent change. Published0039 stays unchanged.
Conversion: transparent index0, at most15opaque colors, 80x80 perview, native160x80 two-frame sheets with identicalframes; isolated edge specks removed. Original nativeEeveelookup encryption keys copied locally, existingengine nitrogfx -scanfronttoback used, decode exact indexedpixel roundtrip PASS for front/back; native-decoded-preview.png visuallychecked. Shiny palette applies existing nativeEevee normal-to-shiny color shifts to newpalette; no separately suppliedshinyMegaart. Inherited animation deformation and native in-battle appearance NOTverified. No Mega activation/reversion test performed or claim. Source/adaptation/import scripts private/convert-mega-eevee-art.py and private/import-mega-eevee-art.py; evidence art-import-report.json. Art-onlytask complete; general scheduleddevelopment remains PAUSED. No publication or further battle/development work until owner's direction.
## October21 — prototype0039 SPRITE UPDATE published; wait for owner testing
Owner explicitly requested publishing the new Mega sprites as prototype0039 and supplying an updated patching page; this supersedes prior private-art-only state. Released ART revision ROM SHA2561114ae2cc11777868150d95caa4ad5378d311b28ad76769c8dc1cad88fec71a3,194488288bytes, localreleasefolder yellow-heartgold/build/0039-art-release-v1/Pokemon-Psyduck-Yellow-prototype-0039-SPRITE-UPDATE.nds and matchingZIP. Internal0040-artWIPfolder remains historical; this release is0039, not0040. No gamechanges beyond completed Mega art import.
UPDATED VERIFIED PUBLIC LINK: https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0039/index-art.html . Standardindex.html also updated inGitHub, but hostedCDN temporarilyreturnedolderHTML; use dedicated index-art link to avoidcache. Original0039page preserved as index-initial.html and originalROM/patch/manifest remain intact. Commit eb25ab5692aa1a24c1afe3d814b395459a6c17d4 includes only updatedstandardpage, newartpage, archivedoriginalpage,8418-byte delta, artmanifest/notes and datedpubliclog/latestlink. NoROM/save/sourcepush.
Four-stage browserpatch fromoriginalUSA input (0037expansion→0038repair→original0039→spriteupdate), eachstagehasheschecked. Source-dependent0039-to0039-art.xdelta SHA0c0a17f1400d5317054f0e74464b54c6b43144a20eb6aa6902d8ece347121689, magicD6C3C400. Patchroundtrip andZIPintegrityPASS; fullLOCALWindowsChrome file-selection/Create/Download PASS exactARTSHA, noerrors (browser-check.json). Five public hostedart/archivefiles HTTP200 byteidentical; rawcommittedstandardindex/publiclog match (public-verification/report.json). No fullremoteChromeCreate claim.
Publication was initially autoreview-rejected onopaque binary/ROMfilename concern; then usage-review failure prevented a diagnostic write, not executed. OnResume proved artifact is8418-byte VCDIFF withsourceCOPYwindows requiring194MBsourceROM, filename strings merelyapplicationmetadata; onlysixMegaartmemberschange. Samepatch retry approved; no approval bypass or ROMpublication. Proof patch-publication-proof.json retained.
BaseEevee133 andstarter1561 sprites unchanged; Mega1562 front/back/palettes updated. NativeformatpixelroundtripPASS, actualbattleappearance/animation/transformation/reversion NOTverified. No newgamestarteracquisition proof, Eonite stillno normalpickup; allbroader0039limits remain. Usercan test this publishedexperimentalrevision. Generaldevelopment HALTED awaitingfurtherinstructions, automation PAUSED; do notresumeoldSurge/campaign/otherwork automatically.