# Pokémon Psyduck Yellow — development log

A plain-language guide to what has changed, what you can play now, and what is
still being built. Share this page with anyone following the project.

**Last updated: October 15, 2026.**

[Watch LIVE testing with video and audio](https://enclosed-mesa-cal-assumed.trycloudflare.com/)

Tap **Enable sound** in the viewer for game audio. The upper DS screen is on the
left and the touch screen is on the right. The link grants viewing only; game
controls remain private. Video and audio pause between actual playtests.

*Stream link refreshed and remotely checked: October 15, 2026. This temporary link
requires the laptop and streaming processes to remain online.*

**Latest published patch: prototype 0029.** Connected Route 6 and native Underground Path services, with earlier checkpoints carried forward.

[Create the latest published playable prototype](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0029/index.html)

The download page contains a modification patch. Select your original,
unmodified USA HeartGold game file to build the playable DS file on your own
device. The original file is not uploaded. Each new checkpoint includes earlier
changes; use the original HeartGold file as input, rather than a previous
prototype. Published checkpoints are kept separately and are not overwritten.

For every newly released test prototype, publish and verify its own browser patching page, post the link in this chat and its dated GitHub update, and update the latest-patch link above. Preserve earlier patch pages. Private work-in-progress builds are not announced as released versions.

## Watch recorded playtests

[Watch the recorded playtests](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/index.html).

This public page will receive additional recordings during active development.
Two new 40-second prototype 0025 recordings show the bridge/sign and Bill’s visible computer, with real game music and stereo audio. Earlier recordings remain available.
The first sample remains a short, silent prototype 0022 controller/recording check,
showing both DS screens and a RAM HUD. It uses a prepared test save containing
a test-only level-50 Pikachu; it does not establish normal campaign difficulty.
Recordings preserve observed behavior, and unknown telemetry is marked clearly.
Please include the prototype number and video timestamp when reporting an issue.

## What we are making

Pokémon Yellow's Kanto adventure, rebuilt using HeartGold's DS graphics and
gameplay systems, with selected modern conveniences and personal touches.
HeartGold's battle mechanics and its support for all 493 Pokémon through
Generation IV are the foundation. Making every species obtainable is still
future work; engine support does not mean every encounter is already placed.

Kanto comes first. Johto is planned as the post-game region. Development is
moving through Kanto one area at a time, with separate patch checkpoints.

## Features carried forward from earlier checkpoints

### A new opening in Pallet Town

- Oak stops you before entering the grass without a Pokémon, walks into view,
  catches a wild Psyduck in an animated field scene, and walks you to his lab.
- The lab's starter table is moved one tile north. Its balls offer **Psyduck on
  the left, Togepi in the center, and Eevee on the right**, with previews, cries
  and confirmation prompts.
- Psyduck is male, Eevee is female, and Togepi uses its normal gender ratio.
- Your lead Pokémon starts following immediately. Changing party slot 1
  changes which Pokémon follows you.
- Blue chooses a starter and challenges you in the lab. Winning or losing lets
  the story continue. Winning gives exactly enough experience to reach level 6.
- Rival naming stays in Oak's opening introduction. Blue's full FireRed
  portrait appears in the touch-screen panel during his introduction and name
  confirmation; the naming keyboard keeps its normal appearance.
- Oak introduces a shiny Eevee instead of Marill, with aligned sparkles and a
  shiny sound. Music and sound commands accompany the opening events.
- The title screen reads **Pokémon Psyduck Yellow**, with an original 3D Psyduck
  paddling through water instead of Ho-Oh flying above clouds. The separate
  opening movie remains HeartGold's original movie.

### Route 1, Viridian and Oak's Parcel

- Route 1 uses Yellow's low-level Pidgey and Rattata encounters, dialogue and
  early item setup. The inherited high-level HeartGold trainers are removed
  from its active events.
- Mom gives the Running Shoes and unlocks running before you leave Pallet.
- A cashier greets you outside on entering Viridian, walks you into the Mart,
  and asks you to deliver Oak's Parcel.
- **Oak gives the National Pokédex only after parcel delivery.** He walks to
  collect the two visible Pokédexes from the back table; they then disappear.
  After Blue leaves, Oak gives five regular Poké Balls and explains catching.
- The remaining starter ball tells you to leave Oak's last starter there.
- Viridian's Pokémon Center entrance works before parcel delivery. Healing,
  Pokémon storage and the player's shared item storage are available.
- The extra escort cashier leaves after the parcel pickup and your departure.
  Only two cashiers remain behind the counter; the upper one runs the shop.
  Ball sales follow HeartGold's shop progression.
- Returning to the upper cashier after delivery awards the Pokégear and Town
  Map. In Kanto, the map opens on Kanto. The reward happens once.
- The old man blocks the northern center path before the required story events.
  Afterward he gives a catching demonstration and walks aside. His granddaughter
  also moves aside and begins wandering. Temporary invisible barriers clear.
- The two specifically requested side-path Cut trees remain until Cut is used,
  following HeartGold's normal tree reset behavior when re-entering the map.
- A western guard warns about strong Pokémon before parcel delivery, then
  leaves. The League reception guards prevent access to unimplemented later
  routes; the eastern guard names Johto and moves the player back to the right.
- Daisy describes Blue as a new trainer, not a gym leader. The Trainer House
  and gym NPCs no longer repeat the same gym-closed message.
- Long custom dialogue scrolls properly instead of appearing cut off.

### Blue, starters and rare Pokémon

- Choosing Eevee gives Blue Psyduck; choosing Psyduck gives him Eevee.
  For new Togepi games, he randomly chooses Psyduck or Eevee and gets the
  opposite gender to your Togepi. His choice is saved, not rerolled each battle.
- The early Route 22 encounter uses Yellow's levels: **Spearow 9 and Blue's
  chosen starter 8**. This team does not scale dynamically with badges.
- Newly generated Pokémon have a base shiny chance of **1 in 4,096**. Carrying
  the Shiny Charm raises it to **1 in 2,048**. One Charm is available in the
  bedroom PC for testing; its current icon is borrowed from Cleanse Tag.
- Player and Blue starters each have an independent **1 in 16,384** bonus
  chance for six perfect IVs. Other rolls use normal random IVs. Being both shiny
  and perfect is possible. The earlier starter-only shiny odds were superseded.
- Starters can receive selected Hidden Abilities already supported by the
  Generation IV engine. This is not a complete later-generation ability system
  or a Hidden Ability update for every species.
- Newly generated members of the 17 existing Yellow/HGSS Legendary encounter
  species receive six perfect IVs: Articuno, Zapdos, Moltres, Mewtwo, Raikou,
  Entei, Suicune, Lugia, Ho-Oh, Latias, Latios, Kyogre, Groudon, Rayquaza,
  Dialga, Palkia and Giratina. This adds no new Legendary encounters and does
  not rewrite Pokémon already stored in saves.
- Several native shiny restrictions are removed, including supported gift,
  trade and special-generation paths. Externally supplied fixed-personality
  event gifts are not rewritten. Deliberately guaranteed shiny scenes remain.

### PC supplies and evolution testing

- The bedroom PC offers the player's PC services, not Pokémon box storage.
  Shared item storage starts with **one Potion and 95 Rare Candies**.
- An upgrade adds 95 each of Thunder, Water, Fire, Dawn, Dusk and Leaf Stones,
  plus NeverMeltIce as the Ice Stone substitute. Stored items persist and the
  supplies are not repeatedly duplicated.
- Extra item evolution options let Eevee become all seven of its Generation IV
  evolutions, and let Togepi become Togetic with a Dawn Stone. NeverMeltIce
  keeps its held-item effect while gaining an evolution use.
- Starting with prototype 0016, Psyduck evolves only with a Moon Stone. The
  earlier level-up and Water Stone methods remain only in older downloads.
- **Golduck is Water/Psychic.** Psyduck stays Water. Golduck's moves have not
  been changed yet.

### Route 2, Viridian Forest and Pewter

- Route 2 and the Forest use Yellow's grass encounters and weighted chances
  throughout the day. Forest trainers have Yellow's teams, levels and dialogue.
  This includes Yellow's rare level-9 Pidgeotto encounter.
- Forest pickups, Route 2's Moon Stone and HP Up, gatehouse conversations and
  signs are adapted to HeartGold's existing locations.
- Inherited Cut trees, Rock Smash rocks and Strength boulders are removed from
  Kanto's active events, except the two specifically requested Viridian trees.
  Yellow's required story gates remain part of the plan. Johto terrain is kept.
- Pewter's outdoor conversations and walking guides are adapted. Brock's gym
  uses Yellow teams: the junior trainer has Diglett and Sandshrew at level 11;
  Brock has Geodude 12 and Onix 14 with Yellow's moves.
- Winning awards the Boulder Badge and a Bide TM34. HeartGold's original
  Shock Wave TM34 remains separately available. In prototype 0015, teaching
  Bide still consumes its TM; reusable TMs are available starting with 0016.
- Pewter's houses, Mart, Center and museum conversions are complete in 0016.
  Route 3 is now converted; Mt. Moon and Route 4 are next.

## Added in published prototype 0016

These changes first appeared in 0016 and carry forward into the latest
download above. Earlier downloads retain their original behavior.

- Yellow conversations for Pewter's houses, Mart and Pokémon Center, while
  keeping HeartGold's healing, shop and PC services.
- Museum admission for 50 Pokédollars, a one-time Old Amber gift, and a new
  second floor for Yellow's upstairs visitors and exhibit conversations, using
  HeartGold's existing displays. Custom exhibit models are deferred after they
  caused a black screen in testing. The revised floor now loads in the DS
  emulator, with working stairs in both directions.
- A correction to Brock's interaction sound command.
- Reusable TMs, including Bide, through the normal teaching system.
- Rare Candy use at level 100 can trigger the next eligible **level-up**
  evolution without raising the level. Friendship, time, location and other
  requirements still apply. B can cancel the normal evolution scene. No eligible
  evolution means no candy consumed.
- Psyduck evolves **only with a Moon Stone**. Its level-33 and Water Stone
  methods are removed. Rare Candies no longer evolve it.
- Stone evolutions remain usable at level 100, including Psyduck's Moon Stone
  and the existing Eevee/Togepi item options.
- Simpler fixes and Pewter event checks take priority before the more complex
  interfaces and campaign systems.
- 0016 did not include bulk Rare Candy selection. Prototype 0018 now includes
  the quantity picker, intermediate moves and one final evolution check.

The 0016 build passed 212 automated checks, including Moon Stone
evolution, removal of Psyduck's earlier methods, and existing stone evolution
at level 100. The revised museum also passed 17 focused Pewter checks; both stair transitions
worked in a DS emulator, and Old Amber was awarded exactly once with repeat
dialogue. The local downloader reproduced the verified ROM with its four-digit
filename.
These checks are not a complete playthrough of the full campaign.

## Release history

New checkpoints use four digits, beginning with **0016**. Earlier labels in the
chart also use four digits; their existing download URLs and files stay valid.

Each row describes what that version added; later versions include earlier
changes and sometimes correct or replace them. The sections above describe the
current rules, so older details should not be mistaken for today's behavior.

Dates and AM/PM times for 0001–0015 come from the recorded release commits,
converted to Eastern Time (America/New_York). They are the best available release
records; the exact GitHub push or hosting activation times were not recorded.
Prototype 0009 uses the intro release, following the withdrawn shop experiment.
Checkpoint 0016 and future checkpoints use the recorded successful publication
push date and time.

| Checkpoint | Made live (Eastern Time) | Main changes |
| --- | --- | --- |
| 0001 | Oct 8, 2026 · 8:41 PM EDT | First Android testing patch and instructions; early starter and Pallet-opening experiments. |
| 0002 | Oct 8, 2026 · 10:56 PM EDT | Pallet opening with protected HeartGold event assets, starter selection and follower tests. |
| 0003 | Oct 9, 2026 · 12:40 AM EDT | Bounded Yellow opening, intro rival naming and low-level Route 1 setup. |
| 0004 | Oct 9, 2026 · 6:50 AM EDT | Visible Oak escort/capture scene, three physical starter balls, immediate follower, Blue opening, starter properties and bedroom item storage. |
| 0005 | Oct 9, 2026 · 12:37 PM EDT | Psyduck swimming title screen and project logo. |
| 0006 | Oct 9, 2026 · 1:11 PM EDT | PC evolution supplies and additional item evolution choices. |
| 0007 | Oct 9, 2026 · 3:18 PM EDT | Mom's Running Shoes, Route 1 travel, cashier escort, Oak's Parcel, delayed National Pokédex and Viridian Center item storage. |
| 0008 | Oct 9, 2026 · 5:40 PM EDT | Center doorway fix, removal of the extra cashier after pickup, upper-cashier shopping and Poké Ball sales. |
| 0009 | Oct 9, 2026 · 7:42 PM EDT | Shiny Eevee introduction and Blue's full portrait on intro/confirmation screens. |
| 0010 | Oct 9, 2026 · 9:45 PM EDT | Old man's catching lesson, Oak collecting visible Pokédexes, corrected leftover starter-ball text. |
| 0011 | Oct 9, 2026 · 11:59 PM EDT | Old man's center-lane placement, Blue portrait moved to the touch-screen panel, aligned Eevee/sparkles. |
| 0012 | Oct 10, 2026 · 1:02 AM EDT | Persistent side Cut trees, granddaughter moving aside, cashier Pokégear/Map reward, western warning guard and temporary barrier removal. |
| 0013 | Oct 10, 2026 · 3:42 AM EDT | League guard fixes, early Route 22 Blue battle, exact level-6 lab reward, automatic Oak Poké Balls, dialogue repairs, fair rival starter rolls, global shiny odds, Shiny Charm and scoped Legendary IV rules. |
| 0014 | Oct 10, 2026 · 4:19 AM EDT | Route 2 and Viridian Forest encounters, trainers, items and conversations; removal of inherited Kanto HM terrain gates. |
| 0015 | Oct 10, 2026 · 5:36 AM EDT | Pewter outdoor events, Brock's gym/Boulder Badge/Bide TM, Water/Psychic Golduck. |
| 0016 | Oct 10, 2026 · 1:14 PM EDT | Pewter interiors, two-floor museum/Old Amber, reusable TMs, eligible level-100 Rare Candy evolution and Moon Stone Psyduck. |
| 0017 | Oct 10, 2026 · 4:29 PM EDT | Route 3: eight Yellow trainer teams, encounters, dialogue and post-Brock access. |
| 0018 | Oct 10, 2026 · 10:27 PM EDT | Mt. Moon: Yellow trainers/encounters, fossils, Jessie/James, rewards and Center services; bulk Rare Candy quantity picker. |
| 0019 | Oct 11, 2026 · 12:01 AM EDT | Route 4: Yellow encounters, optional Lass and reusable Whirlwind; working A-button signs, visible Forest boards, solid item balls and carried-save NPC refresh. |
| 0020 | Oct 11, 2026 · 12:55 AM EDT | Testing travel: two-way Route 4 return crossing and free HM02 Fly at Celadon’s third-floor TM counter; outdoor Fly needs no badge. |
| 0021 | Oct 11, 2026 · 10:30 AM EDT | Cerulean’s initial Yellow visit, Bike Voucher exchange and corrected Pewter guide escort; startup repair. Later save issues are corrected in 0022. |
| 0022 | Oct 11, 2026 · 1:46 PM EDT | Saved quest/reward repair, cleared stale Viridian NPCs, Kanto-first Trainer Card and PC Friendship Charm. |
| 0023 | Oct 11, 2026 · 10:47 PM EDT | Nugget Bridge, Charmander and reusable Thunder Wave; correct Blue bridge approach; Mt. Moon fossil rendering and mandatory guard/exit battles. |
| 0024 | Oct 12, 2026 · 02:18 AM EDT | Yellow’s Route 25, reusable Seismic Toss, hidden Ether/Elixir, Bill’s visible separation scene and automatic S.S. Ticket. |
| 0025 | Oct 12, 2026 · 03:53 AM EDT | Visible bridge trainers, a working Nugget Bridge board, Bill’s visible PC, and Cerulean’s rear-house/Rocket/Dig event. **Latest published patch.** |

[Detailed release notes and verification records](https://github.com/ThatAnarchyDude/corvus-workshop/tree/d40c17fb9e721305bedf0781e00f1a11ce5cfe7c/yellow-heartgold)

## Added in published prototype 0017

- Route 3 has Yellow's eight trainer teams at levels 9–14, explicit Yellow moves,
  and complete battle and post-battle dialogue. Trainers use native HeartGold
  approaches, battles, rewards and defeat flags, at existing route positions.
- Grass encounters are Spearow, Mankey, Sandshrew and Rattata at levels 8–12,
  preserving Yellow's slot probabilities across morning, day and night.
- The sign and resting traveler use Yellow conversations. The PC tip says
  **30 Pokémon per box**, matching HeartGold's capacity.
- Pewter's east exit opens after Brock's Boulder Badge. The pre-Brock escort
  remains. No additional terrain barriers are added.
- Original HeartGold route geometry and warps remain. Its original trainer and
  item events are archived; Yellow has no Route 3 item pickups.
- Existing Blue teams remain unchanged pending the owner's future team plan.

All **218 automated tests passed**. The browser downloader rejected incorrect
input and generated the verified ROM with its four-digit filename. DS emulator
checks loaded a normal save carried from 0016, crossed the post-Brock exit in
both directions, and won the shorts Youngster's battle against Rattata 11 and
Ekans 11. The defeat flag and post-battle dialogue were checked. Private native
commands prepared the battle test save; those grants are absent from the release.
Not all eight battles or the complete campaign have been playtested.

Normal saves are carried forward for focused new-area checks; opening changes
still receive fresh-game tests when needed. Mt. Moon is being converted and Route 4 remains unconverted:
their native exits remain available, but their events are outside this checkpoint.

## Added in published prototype 0018

Published October 10, 2026, 10:27 PM EDT. This cumulative patch includes every earlier checkpoint;
prototype 0017 and all older downloads remain unchanged.

**Bulk Rare Candies:** choose the amount with the quantity picker, apply the
candies, process moves from each intermediate level, then check evolution once
at the end. Normal four-move replacement choices still appear. Cancelling the
picker uses no candies, and only useful candies are consumed. Eligible level-100
level-up evolutions remain supported. Native testing raised Bulbasaur from
level 14 to 17, offered Take Down, then evolved it once into Ivysaur; cancelling
the final evolution also worked.

**Mt. Moon:** Yellow's low-level cave encounters, trainer teams and dialogue,
the Super Nerd's fossil battle, one exclusive Helix or Dome Fossil choice,
and Jessie and James's level-14 Ekans, Meowth and Koffing ambush. The fossil
props look different, Jessie and James have separate overworld sprites and
Yellow's paired battle portrait, and both visibly leave after defeat. Their
Rocket battle music, transition and prize money are preserved. HeartGold's
cave layout is retained without adding HM terrain obstacles.

**Rewards and services:** the nearby Pokémon Center heals Pokémon, supports
shared player PC storage, and sells one level-5 Magikarp for 500 Pokédollars.
Cave rewards include Potions, a Rare Candy, Escape Rope, Moon Stones, Ether,
HP Up and reusable Water Gun/Mega Punch TMs. Existing HeartGold TMs remain.

**Checks:** 263 regression tests passed before the final trainer-name/music
corrections, followed by five passing focused checks on the final code. Native
emulator checks cover both fossil choices, the Rocket battle/departure, rewards,
TM teaching, a deeper-cave encounter, Center services and the exit to Route 4.
Normal saves were carried forward, saved in-game and freshly reloaded. Water Gun
remains learned and its TM retained; the Helix/HP Up run reloads on Route 4 with
the Rocket quest complete. The browser produced exactly the verified DS file
and rejected an incorrect input file.

Not every optional battle or encounter slot has been individually playtested,
and audio playback has not been audited by ear. Route 4 remains unconverted.
Back up your ordinary save before switching versions; emulator save states
must stay with the exact ROM that created them.

[Prototype 0018 download page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/3a18894189a390ba86279a75a097f6b16252e331/psyduck-yellow/prototype-0018/index.html)

## Added in published prototype 0019

Published October 11, 2026, 12:01 AM EDT. This cumulative patch includes the earlier
checkpoints. Previous downloads remain available separately.

**Signs and items:** press A to read Kanto signs. Walking toward them no longer
opens their text automatically. Route 2 signs match their visible boards, and
Viridian Forest has six visible boards with Yellow’s tips. Ground item balls
block walking until collected; their empty tiles become walkable afterward.

**Route 4:** Yellow’s Spearow, Mankey, Sandshrew and Rattata encounters at levels
8–12, the route sign and Geodude conversation, and a reusable TM04 Whirlwind
pickup. The optional Lass has two Paras and one Parasect at level 31, as she
does in Yellow, and stands off the main eastbound path. HeartGold’s existing
terrain and warps remain; no new HM obstacles were added.

**Save carryover:** testing began with the last ordinary 0018 save, retaining
Golduck, the Helix Fossil choice, HP Up and completed Mt. Moon quest. A one-time
refresh prevents HeartGold’s old Route 4 trainers from returning through saved
NPC records. Whirlwind collection and the updated NPC state survived a normal
in-game save and fresh boot of the final release.

**Checks:** 275 regression tests passed before the last NPC-position correction,
then 12 focused tests passed on the final release. Emulator checks covered
A-button signs, solid/collected items, the route walk and TM pickup, the optional
Lass battle opening, the complete Geodude conversation and normal-save reloads.
The browser rejected incorrect input and produced exactly the verified DS file.
The full optional Lass battle and every encounter slot have not been individually
playtested. Audio has not been audited by ear. Cerulean City remains unconverted.

[Prototype 0019 download page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/732edbaea0dfbe33dc038db31747b173a21d1f27/psyduck-yellow/prototype-0019/index.html)

## Agreed plans that are not finished features

- Eventually vary Blue’s teams according to the evolution chosen for the
  player’s starter Eevee, including an unevolved Eevee. This waits for the
  owner’s complete team plan; current teams remain in place.

- Continue Yellow's Kanto campaign through Giovanni's eighth badge, then the
  remaining adventure. Route 24 and Route 25 follow Cerulean’s initial visit.
- Give every Generation IV species an obtainable path, and complete later
  gyms, towns, dungeons, Rocket events, gifts and services.
- When later battles require Blue's evolved Eevee: use Jolteon if the player
  originally chose Togepi, or Umbreon if the player chose Psyduck. These later
  battles have not been scripted yet.
- Add Johto as post-game. Preserve its existing maps/terrain and Silver's
  identity, use a default name for Silver, and retain HeartGold's Johto starter
  selection for a later Johto starter gift.
- Scale Johto gym battles by challenge order, starting above the strongest
  League challenger and ending with a full level-100 team, preserving gym types.
- Preserve HeartGold's original Kanto events for later adaptation into Johto;
  their final locations and story timing are undecided.
- Adjust Golduck's moves after Kanto is complete. Do not treat this as already
  implemented.

## How testing and updates work

Published patches are cumulative and kept separately. This page is the living
summary: its public URL stays the same as new progress is recorded. GitHub's
file history shows earlier versions of the log.

Checks include automated game-code/script tests, selected desktop DS emulator
scenes, normal saving/reloading, and verification that the browser builds the
expected playable file. The owner has also tested earlier prototypes. This
does not establish a complete campaign playthrough, coverage of every emulator,
or audible verification of every music/sound change. Specific limits are recorded
in each release's detailed notes.

Back up ordinary saves before moving between prototypes. Emulator save states
are different and should not be transferred between builds. The project is an
unofficial fan modification; the public downloads distribute patches, not full
commercial game ROMs. Work proceeds during active development sessions.

## Added in published prototype 0020

- Walk both ways through the westernmost tile of Route 4’s final ledge, immediately beside the trees, to return toward Mt. Moon from Cerulean. The existing ledge artwork remains.
- Buy HM02 Fly for zero Pokédollars at Celadon Department Store’s third-floor TM counter. Its other TMs stay available. Teach Fly to a compatible Pokémon normally.
- Fly outdoors without a badge during testing; destinations still need to have been visited. Other field moves and story restrictions retain their normal checks.
- Native emulator checks verified the return crossing, free purchase, teaching Fly, flying to Celadon’s Center, and normal save/reload with HM02 retained. Six focused tests and the browser download/hash checks passed.
- Prototype 0021 will resume Cerulean’s Yellow campaign conversion.

[Prototype 0020 download page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/28b5fd7b8dd7e5311d0c182b5d047f91ffca451b/psyduck-yellow/prototype-0020/index.html)

## Added in published prototype 0021

- Misty uses level-18 Staryu and level-21 Starmie. Her gym trainers match Yellow’s levels. Winning gives the Cascade Badge and reusable TM11 BubbleBeam; Cascade also permits Cut at a suitable tree.
- Blue approaches visibly at the north bridge and uses Spearow, Sandshrew, Rattata and his saved starter choice. He walks away after the battle.
- Melanie gives a level-10 Bulbasaur when your current lead has at least 147 friendship and there is room in your party. A Pikachu is not required.
- The Bike Shop offers Yellow’s unaffordable price and exchanges a Bike Voucher for one Bicycle. Vermilion’s fan club will provide the voucher in a later area checkpoint. Its interior is a separate copy of HeartGold’s bike-shop assets; Johto’s shop is unchanged.
- Cerulean’s Center includes normal healing and Player PC item storage. Its Mart keeps HeartGold’s sales rules.
- Pewter’s guide stands centrally, stops all six exit lanes before Brock and escorts around scenery to the gym. His manual interaction approaches are also corrected.
- An unpublished candidate’s startup problem was repaired. Sixteen focused checks pass, and browser output matches the verified release. Native checks include the guide, voucher/save/reload, Bulbasaur gift, Misty battle and rewards, Blue’s battle and departure, Center healing and Player PC storage menus. Later testing found that the save checks missed an invalid flag-storage boundary. Prototype 0022 corrects it; retained items alone had not proved that the reward flags were safe.
- Private battle test saves used temporary strong Pokémon to check reward events efficiently. Those grants are absent from the released game.

[Prototype 0021 download page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/876971401fd392cad83d2230842f086e236925bc/psyduck-yellow/prototype-0021/index.html)

The owner’s reports of gatehouse NPCs inside counters and occasional transition sprite glitches remain recorded for investigation. Their exact locations or causes have not been confirmed.

### Next: prototype 0023

Continue the southbound Route 5 campaign. The requested friendship-testing item is available in 0022.

### Future dialogue review

The owner will provide a Current Dialogue → Expected Dialogue list. Broader dialogue revisions are deferred until that list is available.

## Added in published prototype 0022

Published Oct 11, 2026 · 1:46 PM EDT.

- Fixed two save problems: older custom completion markers could be cleared each day, and new Cerulean markers extended past HeartGold’s saved flag storage. Earlier tests missed these cases.
- Recovery restores the parcel/Pokédex and Viridian event states when retained progress supports it. A fresh game keeps the original early quest requirements. Saved NPCs that should be hidden are removed on Continue.
- Brock recognizes retained Bide as already awarded; Misty’s BubbleBeam and the Bicycle receive the same recovery treatment. Existing items are kept.
- Kanto’s leaders and badges appear above Johto’s on the Trainer Card. Actual saved badge identities are unchanged.
- Withdraw the Friendship Charm from the bedroom PC to maximize friendship for every non-Egg party Pokémon. If PC storage is full, withdraw a stack, close it and reopen it. Other evolution requirements still apply.
- 44 focused checks passed. Native emulator checks covered a parcel-complete 0020 save transfer, recovery of reset symptoms, another normal save/reload, Brock giving advice without another Bide, maximum friendship persisting after reload, and the swapped badge display. Browser output matches the verified build. These are focused checks; the owner’s actual save and Android emulator were not part of this run.

Back up the normal save, use Continue, and save again after loading 0022. Recovery cannot reconstruct erased history that has no remaining evidence. All previous patch pages remain available unchanged.

[Prototype 0022 download page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/0a1887b1ef80c3980576b1ff0793191b736d1859/psyduck-yellow/prototype-0022/index.html)

### Planned save-editor compatibility

PKHeX Core 26.08.26 recognizes prototype 0022's HeartGold save format. Copied
prepared saves retained Pokédex access and parcel progress after exporting and
loading through Continue. Further tests preserved Hidden Abilities for all 12
supported species. Psyduck, Eevee and Togepi retained their Hidden Abilities and
project shiny status in-game; an edited PC item stack also survived Continue.

The experimental plugin now edits party slots directly because PKHeX's normal
Generation IV editor can replace a custom ability with a standard ability.
Apply project abilities after other Pokémon edits, then export. The plugin
shows our shiny status and player PC items, and supports PC stack edits.
It leaves official legality checks and stock item/species displays unchanged.

[Download experimental plugin 0.1.0 and read its instructions](tools/pkhex-plugin/0.1.0-experimental/README.md).
The download contains the DLL, plugin source, build instructions and GPL license;
it includes no ROMs or saves. Use PKHeX 26.08.26 and a backup copy of a save.

The actual PKHeX plugin loader and Windows interface checks passed on
[GitHub Actions](https://github.com/ThatAnarchyDude/corvus-workshop/actions/runs/38168315938).
A complete manual editing session still needs testing. The data tests used
prepared fixtures, not the owner's actual save or every possible game state.
The upstream license permits modification and distribution under GPL terms,
including source availability and preserving notices.

[Compatibility findings and source](https://github.com/ThatAnarchyDude/corvus-workshop/tree/7137a96a526306225def58c26095597f752e22b1/yellow-heartgold/pkhex).
The project now has separate public repositories for the tools:

- [PKHeX plugin source and instructions](https://github.com/ThatAnarchyDude/psyduck-yellow-pkhex-plugin)
- [Standalone experimental plugin release](https://github.com/ThatAnarchyDude/psyduck-yellow-pkhex-plugin/releases/tag/v0.1.0-experimental)
- [PKHeX upstream fork](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow)

The fork retains the upstream application and now includes a separate Android
save editor. Windows custom editing features live in the plugin. The plugin repository includes GPL source, build instructions
and automated Windows checks. Its fresh Windows build and loader/interface
tests passed before the first standalone experimental release was published.
Follow these repositories for further tool work.
This investigation takes place before campaign work on prototype 0023.


## Android save editor and bedroom-start testing save

Published: October 11, 2026 at 06:10 PM EDT.

The first experimental Android editor is available for Psyduck Yellow and
HeartGold normal saves. Open a `.dsv` or 512 KB `.sav`, edit party levels,
friendship, IVs and supported abilities, then export a separate copy. It uses
Android's file picker and works offline. Keep an original backup. This first
version does not yet include box editing, item editing, Pokemon creation or
all of the desktop application's tools.

[Download Android editor 0.1.0](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.0-experimental/Psyduck-Save-Editor-0.1.0.apk).
[ZIP alternative for downloads that stall on the APK](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.0-experimental/Psyduck-Save-Editor-0.1.0-Android.zip).
Extract the ZIP using My Files, then tap the APK inside. It contains the same
signed application; no existing release files were replaced.
[Source, license and instructions](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/tree/master/Android).

Save-data checks passed 54 assertions. An Android 16 emulator also passed
installation, opening a save, changing a level, exporting and checking the
exported save. The owner's physical phone has not yet been tested.
[Build and Android interface verification](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/actions/runs/38178129659).

A separate testing save skips the intro and starts at the first arrival in
the player's bedroom in prototype 0022. The player is a boy named GOLD and
the rival is BLUE. No starter, badges, Pokedex or parcel progress has been
obtained. It was saved through the normal in-game menu and verified by a
fresh boot through Continue. Both file formats also passed the Android
editor's import/export checksum checks.

- [Download bedroom-start .dsv](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.0-experimental/prototype-0022-bedroom-start.dsv)
- [Download equivalent .sav](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.0-experimental/prototype-0022-bedroom-start.sav)
- [Download ZIP with both formats and instructions](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.0-experimental/prototype-0022-bedroom-start.zip)

Back up the emulator's existing save before importing one of these files;
then select Continue. No ROM is included. These save downloads are release
attachments, not files in Git history, and do not replace any earlier patch.
Compatibility of this specific testing save with other prototypes is unverified.


### Android editor 0.1.1 compatibility update

Published: October 11, 2026 at 06:36 PM EDT.

The owner successfully downloaded 0.1.0 using the ZIP alternative, but the
app closed immediately on their Samsung Android 16 phone. The exact crash
cause is still unconfirmed because a device crash log is not available.

[Download the new 0.1.1 ZIP](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.1-experimental/Psyduck-Save-Editor-0.1.1-Android.zip).
Extract it, then tap the APK to update the existing app. The original release
files remain available. This update uses a more conservative runtime setup
and includes a Share startup diagnostics button. Reports contain device and
runtime information, not game saves; sharing is controlled by the user.

The build, APK signature, update certificate and 16 KB packaging checks
passed. [Android 16 automated checks also passed](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/actions/runs/38180556331), including five cold launches,
diagnostic sharing, opening a save, editing a level and validating the exported
copy. These emulator results do not establish a fix for the owner's phone;
physical-device confirmation is still needed.


### Android editor 0.1.2: party management and held items

Published: October 11, 2026 at 07:43 PM EDT.

The owner confirmed that 0.1.1 works on their Samsung phone. Version 0.1.2
keeps that startup configuration and adds customized Pokemon creation, proper
party size updates, party removal, held-item editing and four-move editing.
Choose among all 493 Generation IV species, then customize level, gender,
nature, shiny status, IVs, friendship, ability, moves and held item.

[Download Android editor 0.1.2 ZIP](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/download/android-v0.1.2-experimental/Psyduck-Save-Editor-0.1.2-Android.zip).
Extract the ZIP and tap the APK to update the existing app. Export an edited
copy and keep the original save backed up. Earlier releases remain available.

Party size follows the actual members, up to six; removal closes the gap and
cannot remove the last member. Removing a Pokemon does not move it to a PC
box. Held items are searchable by name or ID; None clears an item. Key items,
HMs and mail cannot be newly assigned as held items. Created Pokemon and
chosen moves are for customized play/testing, with no promise of official
encounter legality. Party changes preserve quests and Pokedex progress.

The save model passed 94 assertions. A zero-party bedroom save also exported
correctly with six members without changing quest or Pokedex state. A DS
emulator loaded a separate edited save through Continue and displayed all
three members, including the new female shiny Eevee holding Leftovers.
[Android 16 interface tests passed](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/actions/runs/38184727927): five cold launches, party addition/removal,
held-item assignment, move editing and validated save export. Signature,
update certificate and 16 KB packaging checks passed too. The new interface
still needs the owner's phone test.

### Prototype 0023: Nugget Bridge and Mt. Moon corrections

Published: October 11, 2026 at 10:47 PM EDT.

The bridge’s five contest trainers, optional grass trainer and Rocket recruiter
use Yellow’s teams, levels, moves and dialogue. Beat all five for one Nugget,
then the recruitment battle. Losing permits a retry without another Nugget.
Damian gives one level-10 Charmander; make room in your party first. The solid
item ball gives reusable TM45 Thunder Wave. Grass uses Yellow’s species and
levels during morning, day and night. Blue’s approach covers the bridge lanes
at the correct height and keeps his saved starter.

The extra figure near the fossils came from incorrect fossil rendering
settings. Both fossils now display as items. The guard automatically stops
you for his battle before fossil selection; an early exit attempt starts his
battle before any fossil reminder. Jessie and James wait to the left of the
southern opening, walk up for their ambush after a fossil is chosen, and walk
to the exit after defeat. Side approaches along the bottom wall are covered
too. The map terrain and warps remain unchanged.

Normal saves preserve the rewards, party and National Pokédex through Continue.
The automated checks passed 37 tests, and the browser patcher reproduced the
expected DS file. Native checks used private prepared saves, including staged
contest wins and a test Pikachu for TM teaching; these are focused checks, not
a complete campaign difficulty test. Private test grants and transports are
excluded from the prototype. Android game testing remains deferred.

A new [30-second recording with game audio](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/index.html) shows the fossil
rendering and automatic guard scene. Earlier recordings and patches remain.
[Route 24 details](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/ROUTE24.md),
[Mt. Moon corrections](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/MTMOON-CORRECTIONS.md),
and [verification](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/validation-prototype-0023.json)
are available for reviewers.

### Prototype 0024: Route 25 and Bill

Published: October 12, 2026 at 02:18 AM EDT.

Route 25 keeps HeartGold’s terrain and gains Yellow’s nine trainer teams, levels,
moves and conversations. Grass uses Yellow’s species and levels throughout the
day. A solid item ball above the Camper gives reusable TM19 Seismic Toss;
Thunder Wave remains TM45. Yellow’s hidden Ether and Elixir use the normal
A-button pickups and Dowsing behavior. The Sea Cottage sign requires A.

Bill begins combined with a Pokémon and walks into the left chamber after
asking for help. Use the PC on the left wall to start the separation machine,
with game sounds and a brief flash. He walks out of the right chamber and
automatically offers the S.S. Ticket. A full Key Item pocket permits a later
retry; receiving the ticket cannot be repeated. His PC later shows his favorite
Eevee family with portraits and cries. Bill’s completion opens the existing
Cerulean police gate; the Rocket/Dig follow-up is the next checkpoint.

Normal Save/Continue retained Bill’s completion, one S.S. Ticket, the party,
parcel progress and National Pokédex. All 29 focused/regression tests passed,
and the browser download reproduced the expected DS file. These checks used
private prepared saves and do not constitute a complete nine-trainer difficulty
playthrough. No private test transports or Pokémon grants are in the release.
Johto terrain and earlier releases remain unchanged. Later-generation Seismic
Toss compatibility uses HeartGold’s Brick Break eligibility; Generation I
compatibility follows Yellow.

[Watch the new 40-second recording with sound](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/index.html),
[read Route 25/Bill details](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/ROUTE25-BILL.md),
or [review the checks](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/validation-prototype-0024.json).

The owner reported a freeze in Android melonDS while crossing northern Route 2
and Cerulean in 0023. Their PC DeSmuME comparison did not freeze, and they asked
to park the report and continue. The cause remains unconfirmed; transferring
a save has not been established as the cause.


### Next: trainer visibility, then the returning Cerulean quest

The owner’s new screenshots show Nugget Bridge trainers appearing and
disappearing when the player is nearby. Similar behavior affects other added
trainers. Investigating and fixing that is the first priority for 0025, before
continuing the robbed-house/Rocket/Dig event. The released 0024 patch remains
unchanged; the visibility issue has not yet been fixed.

### Prototype 0025: visible bridge trainers and the stolen Dig TM

Published: October 12, 2026 at 03:53 AM EDT.

The first three Nugget Bridge trainers now appear before you cross from
Cerulean into Route 24. HeartGold’s neighboring-map actor system keeps them
visible during an approach and retreat, including after loading an older
normal save. Their ordinary trainer battles remain intact. This fixes the
confirmed boundary issue; focused checks of another added Route 25 trainer
also showed normal visibility and sight-based interaction. Other rendering
reports can still be investigated if they recur.

The board west of the southern bridge entrance now reads ROUTE 24, NUGGET
BRIDGE, and “Five trainers await your challenge!” with the A button. Bill’s
PC now has a visible HeartGold computer terminal at its existing interaction
spot. It still operates the separation machine and his later collection menu.

After helping Bill, enter Cerulean’s robbed house and use its new rear-wall
passage. The Rocket stops adjacent approaches and battles with Yellow’s
level-17 Machop and Drowzee. Winning returns one reusable TM28 Dig. He walks
away afterward; a full TM pocket permits a reward retry without another
battle. Losing does not finish the event. Its completion and reward survive
normal Save/Continue, and the rear entrance cannot skip Bill’s earlier gate.

All 31 focused/regression checks passed. Native DeSmuME checks confirmed
older-save loading, bridge approaches and boundary transitions, A-button sign
text, Bill’s visible PC and separation, the Rocket battle/reward/departure,
both rear-house transitions and saved completion. The browser patcher
reconstructed the expected playable file and rejected an earlier prototype
as its input. Prepared private saves were used; these checks do not establish
normal campaign difficulty or exhaustive emulator compatibility.

The two new recordings play with sound. Small recorder audio-clock drift is
aligned without changing pitch, and that adjustment is recorded in the clip
log. Original soundtracks, earlier patches and earlier recordings are retained.
Johto terrain and archived HeartGold events remain unchanged. Private ROMs,
saves, raw RAM and test transports are excluded from this publication.

[Watch the recordings with sound](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/index.html),
[read the checkpoint details](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/CERULEAN-DIG-VISIBILITY.md),
or [review the checks](https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/yellow-heartgold/validation-prototype-0025.json).

Route 5 is next. The owner’s broader dialogue list and Blue teams reacting to
the player’s Eevee evolution remain future work. Android editor development
is paused, and the earlier melonDS movement-freeze report remains parked
without a confirmed cause.


## PC development resumed — October 12, 2026

Prototype **0025 remains the latest published playable patch**. A new local 0026
build is in development; it is not yet a finished or downloadable checkpoint.

The target is now explicit: rebuild Yellow’s Kanto layout and adventure using
HeartGold’s DS graphics and systems, then open Johto after the first Elite Four
victory and Hall of Fame. Earlier areas will be checked where their maps still
follow HeartGold. Johto’s existing maps and gameplay will be preserved. The approved
starter choices, shiny odds, bedroom PC supplies, Water/Psychic Golduck and custom
evolution methods remain intentional. The complete Oak introduction and player/rival
naming screens are locked to the owner’s supplied 0025 version.

Blue remains the Kanto rival, without a Leader title, before the first Hall of Fame.
Giovanni remains Team Rocket’s leader and Viridian Gym’s leader during that campaign;
Blue’s gym takeover follows afterward. These later events are planned, not implemented.
Suitable color Jessie/James overworld and battle sprites are being researched.

Route 5’s first development build now has Yellow’s encounters throughout the day,
its Underground Path sign and no inherited outdoor NPC. The Kanto Day Care is being
connected to HeartGold’s native services. The owner has approved sharing its deposited
Pokémon and interactions with Johto’s existing Day Care, while leaving that facility
unchanged. A private test reached the Kanto house, selected a Pokémon and deposited it;
withdrawal, saving/reloading and egg handling still need checks. Yellow’s route layout,
correct Day Care placement and the Saffron guard’s drink roadblock are still unfinished.
Six focused automated checks pass; this is not a full campaign playthrough.

The local build tools and DS emulator are working. A copy of the owner’s latest save
loaded through Continue; the original was left untouched. A private live viewing link
now carries both DS screens and game audio. A slow video conversion was corrected,
and the owner reported much smoother playback. The private link is temporary and
requires the PC and streaming processes to stay online; it is not a public viewing page.

Each completed prototype update will include a labeled gameplay test recording
here, alongside its playable patch link. Prepared saves or test-only setup will be
identified, and earlier checkpoints and recordings will remain available. No new
0026 completion recording or playable patch is being claimed in this progress update.


## Prototype 0026 — local playable checkpoint, October 12, 2026

Prototype 0026 has been delivered to the owner’s RetroArch downloads, with a separate copy of the latest normal 0025 save. Originals remain untouched. This is an incremental Route 5 encounters and Day Care checkpoint; 0025 remains the latest public patch page until the new artifacts are published.

Route 5 now has Yellow’s weighted grass encounters throughout the day, its Underground Path sign and no inherited outdoor NPC. Its existing HeartGold house provides native Day Care interactions using the same deposited Pokémon as Johto. Separate native checks observed deposit, withdrawal with the 100-Pokédollar fee and a normal save/Continue reload preserving the entire Day Care save block. Egg handling is still untested. Johto resources, the supplied Oak introduction and naming screens, and approved customizations are preserved.

Six focused Route 5 checks pass. The cumulative patch was applied to a pristine USA HeartGold ROM and reconstructed the exact tested 0026 file. A new 40-second recording with real game music and stereo audio shows Continue into the Kanto Day Care and attendant dialogue. It uses a copied prepared save; it is not campaign difficulty evidence or a recording of the entire deposit/withdrawal cycle. The playable file and recording are linked in the owner’s desktop chat; public artifact publication remains pending.

Yellow’s Route 5 terrain and Day Care placement remain unfinished. Saffron’s drink roadblock is excluded from this checkpoint: a saved-variable collision with bedroom PC item slots was found during development. The gate source now uses a shared flag without that saved variable; native tests are still needed. Area-name banners on every transition and Blue’s phase-aware rival title also remain pending. Work continues toward the full Yellow campaign.

The live dashboard now places the upper DS screen on the left and the touch screen on the right. Video and audio pause while editing. The owner-posted viewing URL is unchanged; a proposed separation of public viewing from private controls awaits specific approval.


## Prototype 0026 — phone patching page published

[Create prototype 0026 on your phone or PC](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0026/index.html) by selecting your original, unmodified USA HeartGold ROM. The page applies the cumulative modification patch locally and verifies the finished file; your ROM is never uploaded. Use the original HeartGold file, rather than 0025, as patch input. Earlier patch pages remain unchanged. The owner’s Windows file link timed out on the phone, so this restores the browser-based download workflow.

[Watch the new 40-second test recording with real game audio](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/prototype-0026.html). It shows normal Continue into the Kanto Day Care and attendant dialogue using a copied prepared save; it does not show a full deposit/withdrawal cycle or establish campaign difficulty. Separate native deposit, withdrawal/100 fee and normal-save preservation checks are recorded in the checkpoint notes. Egg handling is untested. Yellow’s Route 5 geometry, precise Day Care placement and Saffron drink gates remain excluded or unfinished in 0026.

The owner specifically approved public viewing with private controls. The existing live URL is unchanged and now grants viewing/audio only; a new private control credential stays local. Ten bridge checks pass, and remote checks confirm that viewing/audio work while public and anonymous game controls are rejected. Video/audio remain paused while editing. No ROMs, saves or private control credential were published.

## October 12 — connected Route 5 scenery in progress (private 0027)

Route 5 now has a private test build with seamless outdoor connections, HeartGold tree graphics at all 49 Yellow tree positions, and visible, joined cliff ledges. Yellow's spacing was shortened with the owner's approval while preserving its grass, ledges, doors and gate-required progression. The Underground Path sign opens correctly. Native gameplay checks show grass walking, southward ledge hopping and refusal to climb back north; actual testing was also shown on the existing live audiovisual feed.

All 52 focused Route 5 checks pass. The new scenery changes rendered terrain only: collision, events, executable code and other resources remain unchanged compared with the connected baseline. Johto and the supplied Oak introduction/naming screens remain preserved. A labeled 24-second native gameplay recording with real stereo game audio is saved locally for this private checkpoint.

0026 remains the latest released prototype. 0027 still needs fence/scenery finishing, gate interior and door-animation work, broader old-save and travel checks, and release patch verification. The next step is to finish those items before posting a new patching page and its recording. The live server and viewing tunnel remain connected; picture and sound pause between actual tests. No ROMs, saves or private controls are published by this update.

## October 13 — live viewing page repaired

The stream server was sending video and audio, but a JavaScript initialization error left the viewing page blank before it could draw the game screens. That error is fixed. Both screens now visibly render in the browser, sound initializes, and all 11 stream/dashboard checks pass, including a new test that executes the actual page script. Refresh the stream page to load the repair. The existing viewing URL is unchanged; public viewing and private controls remain separated.

This repair does not change the ROM. The server and viewing tunnel remain connected, with ordinary video/audio pauses between tests. The owner's requested five-minute viewing window was restarted after the browser repair.

## October 13 — natural Cerulean-to-Day Care access verified (private 0027)

The northern entrance needed alignment: HeartGold's stairs reach the side roads, while Yellow's central approach sits between them. Two small gaps in the first-row tree/fence boundary now connect those stairs to the central path. All 48 grass tiles, 40 ledges, doors, buildings and the southern gate roadblock remain intact; Cerulean's original map and Johto remain unchanged.

Continuous native tests now walk from either existing Cerulean entrance through Route 5 into Day Care without intermediate test transports. The actual live walk also completed that route. All 55 focused Route 5 checks pass. A labeled 49-second native recording with real stereo audio verifies Cerulean, Route 5 and Day Care; it stays local with this private checkpoint until release packaging.

0026 remains the latest released prototype. Remaining work includes fences, the northern visual seam, gate interior and door animation, broader save/travel checks, and the cumulative release patch/recording. The viewing server and tunnel remain connected, with the feed paused between actual playtests.


## October 13 — prototype 0026 bedroom report checked

A tester reported unreliable movement and a recurring black screen using standalone DeSmuME 0.9.13-4 under Linux Xvfb. The cause is still unconfirmed.

A clean run of the exact released 0026 ROM with our DeSmuME libretro core completed the supplied Oak/player/rival introduction, walked normally in the bedroom, used the stairs, and made a normal first-floor save. A fresh Continue boot loaded that save, and a separate direct-input test moved the player another tile. This does not rule out the tester's reported failure in their environment.

A local Linux test kit and separate fresh first-floor .dsv were prepared for comparison. The kit needs no Xvfb, contains no ROM, preserves its input save, and captures screenshots and actual stereo game audio. Its official core downloader verifies the same core used by development. Saves and private test artifacts remain local. Two opening-metrics checks and all eleven stream/bridge checks pass. Prototype 0026 remains the latest release.


## October 13 — complete offline Linux tester bundle

The requested local bundle now includes the Python runner, exact DeSmuME libretro core, explicit configuration, portable Python, pinned Pillow packages, offline setup and the separate fresh first-floor save. It contains no ROM or owner campaign save. Base Linux runtime libraries are checked at startup.

An extracted-copy test using the bundled Python and packages passed Continue and one-tile movement, captured both screens and real stereo audio, and preserved the supplied save. No Xvfb, pip or network download was required for setup. The bundle remains local for transfer to the tester. Prototype 0026 remains the release, and the standalone DeSmuME/Xvfb black-screen report remains open pending comparison.


## Prototype 0029 — Route 6 and Underground Path, October 13, 2026

[Create prototype 0029 on your phone or PC](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0029/index.html). Select your original, unmodified USA HeartGold ROM; the cumulative patch is applied locally and your original is never uploaded. Back up normal saves and keep emulator save states with their exact ROM version. Earlier patch pages remain available.

Route 6 now connects to the native cities and has Yellow's six trainer teams, grass encounters and rod encounters. Native Underground rooms and hidden Full Restore/X Special rewards are retained. The northern entrance offers Cubone for RICKY, with the native trade followed by evolution into Machamp. Earlier Route 5 work and native interiors carry forward. Saffron's missing pavement textures are repaired.

The Soul Badge permits Surf in both Kanto and Johto, with Fog Badge retained as an alternative. Native full-screen location previews remember visits within each time period and return after a period change; repeated entries keep the small name banners. The supplied Oak introduction/naming screens, approved customizations and native interiors are preserved. Johto assets remain preserved; future changes are limited to necessary traversal/HM compatibility with Kanto-earned unlocks. The full Kanto campaign remains unfinished.

[Watch the 50-second recording with real game audio](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/prototype-0029.html). It shows repeated Vermilion/Route 6 crossings following a normal Continue on the final candidate. Both screens are side by side. Testing used a copied prepared traversal save and its existing party, without RAM writes or emulator state restoration; it does not establish campaign difficulty. Native audio-clock drift was aligned while preserving pitch.

Separate continuous gameplay checks walked through both Underground entrances and the corridor, encountered a wild Pokémon, defeated both southern trainers and reached Vermilion. Native Save followed by fresh pure-candidate Continue retained the position and both actual defeat flags. Trade/evolution, hidden pickups, all three rods, Surf, preview history and preservation checks have separate evidence; this is not a complete campaign playthrough or gameplay coverage of every preview destination.

The actual patch-page JavaScript decoder reconstructed the exact candidate and rejected incorrect size/checksum inputs. The cumulative xdelta and ROM archive also passed checks. Published patch and recording pages matched the tested local artifacts. No ROM, save or private control credential was published.


## October 13 — Vermilion Bike Voucher reward verified in development

The Fan Club chairman now gives Yellow's one-time Bike Voucher in the private 0030 candidate, keeping HeartGold's room intact. An actual native reward, normal save and fresh pure-candidate Continue retained the completed reward. A copy of that earned-Voucher save then completed the native Cerulean Voucher-for-Bicycle exchange. Tests used initial private transport only, without item grants or emulator save states; original saves remain untouched.

Three focused checks cover the exchange/repeat logic, refusal/full-bag retries and native-resource preservation. Gameplay checks ran on the connected live video/audio feed, with picture and sound paused afterward. Other Vermilion events, Old Rod gift, ship and gym progression remain unfinished. The exchange's own Save/Continue and native refusal/full-bag cases still need checks. Prototype 0029 remains the latest published release.


## October 13 — Old Rod gift in development

Vermilion's fishing guru now offers Yellow's Old Rod in the private 0030 candidate, retaining HeartGold's room. Actual live testing confirmed refusal and reoffering, acceptance and the named receipt, then the completed-gift greeting. Six focused Rod/Voucher checks pass, including existing ownership, refusal/full-bag retries and native-resource preservation. Johto's native fishing-guru flag and scripts remain unchanged.

Native Rod Save/Continue, fishing with the earned item and the full-bag case still need checks. Other Vermilion campaign work remains unfinished; prototype 0029 is the latest published release. Original saves are untouched, and the viewing connection remains available with picture and sound paused between tests.


## October 13 — reported invisible gatehouse repaired in private0030
The northbound gatehouse was missing from Vermilion's loaded building models even though its doorway remained active. The private next-prototype candidate now includes the compatible gate model. Live testing with a copied save showed its exterior, entry into the original HeartGold interior and normal exit with the exterior still visible. Complete city-to-gate traversal remains on the final release checklist.
Preservation checks passed: the fix changes only Vermilion's graphics reference, leaving interiors, events, doors, terrain and Johto unchanged.0029 remains the latest release. The existing stream connection stays available with picture and audio paused between tests; its URL has not changed.


## October 13 — Vermilion letter and house advice tested
Yellow's letter to PIPPI is now visible on the existing house table and readable through all three paragraphs. Live tests also verified the youngster and Pidgey dialogue, the southern house's HM advice and normal dialogue closure. The original HeartGold rooms, furniture, collision and doors are preserved; only a small letter object was added.
Preservation checks pass. The viewing link remains connected and remotely verified, with controls private and picture/sound paused between tests.0030 is still in development;0029 remains the latest release.


## October 13 — Vermilion Mart conversations in development
Added Yellow's two Mart customer conversations to the private candidate, preserving the native shop interior and clerks. The Rocket conversation and normal dialogue closure were exercised on the live feed. Preservation checks pass; the second customer's gameplay check and Yellow's exact shop inventory still need completion. Pokémon Center services and dialogue remain in progress.0029 remains the latest release.


## October 13 — shared Kanto shop progression foundation checked
The owner approved a common cumulative stock system for regular Kanto Marts, including Lavender: start with Yellow's Viridian stock and add missing items after each newly earned Kanto badge, following the standard badge-city order. Northern vendors sell balls and southern vendors sell general supplies. Johto shops, Celadon's Department Store and Pokémon League shops keep their HeartGold inventories and prices. Master Balls and Cherish Balls are excluded from new shop stock.
Prepared shared inventory data and a Kanto-only badge counter. Five checks pass, including every possible badge combination. Native integration and the fourth badge's Celadon-derived stock selection remain pending. The earlier fixed Vermilion catalog passed actual copied-save buy/sell checks; the new shared system is not yet playable.0029 remains the latest release.


## October 13 — Lavender supplies the fourth shop expansion
Confirmed Lavender's Yellow stock for the fourth-badge expansion: Great Balls, Revives and Super Repels. All cumulative stock stages are now defined and five checks pass, including every badge combination and the two-vendor split. Celadon Department Store, League-area shops and Johto shops remain unchanged. Native integration is still pending; this is not yet a playable shared shop system.0029 remains the latest release.

## October 13 — Vermilion Center interactions checked
Yellow's training advice and stationary Chansey are implemented in the private candidate. Live checks verified their dialogue and return to normal field control, plus the native nurse's completed healing sequence. Preservation checks pass; the original room, nurse and link-service scripts remain intact. A conflicting poison-dialogue detail and other Vermilion campaign work remain pending.


## October 13 — Jenny reward event staged
The private candidate now contains Jenny's Thunder Badge check and level-10 Squirtle event. Three compiled-script checks pass; live testing verified that the existing two-badge save cannot receive the gift yet. The event is not release-ready: Yellow's Box delivery when the party is full, final Jenny artwork and accepted-gift save checks remain unfinished. Originals are untouched;0029 stays the latest release.


## October 13 — approved Jenny gift behavior verified
Jenny now uses the requested full-party warning and keeps Squirtle available until the player has a free party slot. This approved customization replaces automatic Box delivery. Four script checks pass. Live testing verified full-party refusal/retry, successful level-10 Squirtle delivery, repeat dialogue and persistence through normal Save/Continue on the pure candidate.
Tests used isolated copied saves; eligibility and capacity fixtures were clearly labeled, and originals remain untouched. Jenny's final artwork and other Vermilion campaign work still need completion.0029 remains the latest release. The viewing connection remains available with picture and sound paused between tests.

## October 13 — restored prototype 0028 patch link

The missing [prototype 0028 browser patch page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0028/index.html) is now published. It restores native gatehouse interiors. Its browser decoder reproduces the preserved released ROM exactly and rejects incorrect original files. Use an unmodified USA HeartGold file; the page contains only a patch and performs patching locally. Prototype 0029 remains the newer published checkpoint.

Project pages and plain-language notes belong under `psyduck-yellow`. The existing `yellow-heartgold` folder holds development tools and ignored private build outputs. A local copy of the 0028 ZIP is now also available under `psyduck-yellow/downloads/prototype-0028`; that download folder is ignored and its ROM archive is not published. Existing release and tool paths remain preserved.


## October 13 — shared Vermilion Mart stock checked in-game

Both Vermilion vendors now use the new cumulative Kanto stock system in the private prototype 0030 candidate: the northern vendor sells balls and the southern vendor sells supplies. Native buying, selling and cancellation work. Tests on a copied two-badge save showed the expected early stock. A separate controlled fixture with four out-of-order Kanto badges and all eight Johto badges selected fourth-stage stock correctly, including Great Balls, Revive and Super Repel; later items remained locked. A normal save and fresh Continue on the pure candidate retained that stock. These fixture badges are test setup, not campaign victories.

Compiled-script checks cover every badge combination for both vendors. Preservation checks confirm the existing shared shop scripts and excluded shops remain unchanged. Other ordinary Kanto Marts still need connecting as their areas progress. Vermilion's remaining city, ship and gym work and release checks are unfinished; prototype 0029 remains the latest published release. Original saves and released builds remain untouched.


## October 13 — isolated ship rooms and captain reward checked

Separate copies of HeartGold's ship hall and captain cabin now render and support ordinary doorway travel in both directions. Existing S.S. Aqua and Johto maps, events and assets remain unchanged. These test rooms are disconnected from the campaign and still have temporary native ship labels.

The captain's Yellow dialogue and one-time HM01 Cut reward were checked in the native game on a copied save. A repeat conversation used the completed-reward greeting, and that behavior survived a normal Save and fresh Continue on the pure experimental candidate. Script checks also cover full-bag retry and unrelated quest flags; the full-bag case still needs an in-game check. The rubbing animation, final location names, boarding, rival, trainers and departure remain unfinished. Prototype 0029 remains the latest public release; this is private development progress, not a new playable release.


## October 14 — viewing stream reconnected

The viewing stream was restored after the desktop and Ubuntu recovery. [Open the refreshed live video/audio viewer](https://enrolled-ira-opening-five.trycloudflare.com/). Remote checks confirm authenticated viewing works and the viewing credential cannot use game controls. The access-bearing link is shared with the owner in chat; this public log stores only the viewer address. Picture and sound pause between actual playtests; the server and tunnel remain connected when possible. Prototype 0029 remains the latest published game release.


## October 14, 2026 — full PKHeX with built-in prototype 0029 support

[Download the full Windows PKHeX release](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v1). This keeps PKHeX's normal editors and adds an optional Psyduck Yellow 0029 profile. Open a copied battery save (.sav/.dsv or supported .srm), then enable Tools → Psyduck Yellow prototype 0029. The .nds game file and emulator save states are not editor inputs.

Custom starter legality, supported Hidden Abilities, evolution changes, project shiny classification, item names and Golduck's Water/Psychic typing are built in. Saves remain Generation IV/HeartGold-compatible. Windows editor regressions and an exported-save native Continue check passed; an independent public build also passed. The full altered wild/campaign encounter catalog remains incomplete, so other custom encounters may still produce retail warnings. ROMs and player saves are not included. The game release remains prototype 0029.


## October 14, 2026 — player PC items tab in PKHeX v2

[Download PKHeX with the new PC inventory tab](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v2). With the Psyduck Yellow profile enabled, SAV → Items now includes the player's PC item storage separately from the Bag. All ten physical slots in prototype 0029 are editable regardless of badges. Tests verify correct saved item/quantity mapping, preservation of Bag and story data, and no extra tab in ordinary HeartGold saves. The independent Windows release build passed; v1 remains available.

The approved next game prototype will start at 20 usable PC slots and unlock five for each distinct Kanto badge, up to 60. This restriction belongs in the game only; PKHeX will expose all physical slots supported by that new save layout. The expanded game layout is still pending and is not written into existing 0029 saves by this editor. The game release remains prototype 0029.


## October 14, 2026 — PKHeX v3 resizable window

[Download PKHeX v3](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v3). The main window now supports dragging its edges and the standard Windows maximize button. Editor panes expand to fit, the menu stays at its normal height, and maximizing uses the desktop working area so the visible taskbar remains accessible. Restore returns to the prior normal size. Native Windows resize/maximize/restore checks and the existing PC-item/starter editor regressions passed locally and in the independent public release build. Earlier editor releases remain available. Game prototype 0029 is unchanged.


## October 14, 2026 — PKHeX v4 proportional interface scaling

[Download PKHeX v4](https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow/releases/tag/pkhex-py0029-v4). Both manual resizing and maximizing now enlarge the live interface together: text, controls, spacing, menu icons and Pokemon images scale from their original dimensions. At 150% of the default client size, the display uses a 150% scale. A uniform factor fits differing window shapes without clipping or distortion; the taskbar remains available. Returning to the original size restores the original interface.

Local and independent Windows checks passed manual scaling, the exact 150% example, maximize/restore, loading a save while enlarged, editing supported starter families and the PC inventory tab. The game/save format remains unchanged and earlier editor releases are preserved.


## October 15 — viewing stream restored

[Open the current live video/audio viewer](https://louisville-voted-worship-examining.trycloudflare.com/). The previous temporary tunnel stopped; its replacement is remotely verified. Authenticated viewing works and the viewing credential cannot operate game controls. The access-bearing viewing link is shared only with the owner in chat. Picture and sound pause between actual playtests. Prototype 0030 remains private and unfinished; prototype 0029 remains the latest published game release.


## October 15 — replacement viewing connection

The earlier temporary tunnel returned Cloudflare error 1033. [The replacement live video/audio viewer](https://enclosed-mesa-cal-assumed.trycloudflare.com/) is remotely verified and controls remain private. The owner received the access-bearing link in chat. This public address contains no viewing credential. Prototype 0030 is still in development; prototype 0029 remains the latest released game.


## October 15 — colored battle artwork and ship navigation in development

The owner's colored Jessie and James battle artwork is now integrated into the private prototype 0030 candidate and was observed in the running game's trainer introduction with stereo audio. Comparison with the preserved 0029 release confirms the supplied artwork changes only the intended battle graphics. The test used a copied save and a clearly identified forced-battle fixture; it does not establish a complete Mt. Moon story replay.

Ship navigation work now accounts for all 17 passenger cabins. Live checks exercised all six first-floor cabins, both floor connections in both directions, and the farthest second-floor cabin. A doorway arrival-direction mismatch found during testing was corrected. A continuous native walk then reached the captain through the copied passage and ladder, with no intermediate test transport. Original HeartGold ship resources remain preserved. Boarding, remaining ship story events, Gym progression, expanded PC storage and final release checks are still unfinished. Prototype 0029 remains the latest published game; 0030 has not been released.


## October 15 — saved-game ship travel checked

A normal save in the captain's cabin loaded successfully through fresh Continue on the pure private candidate, with no test transport or battle fixture active. Ordinary movement then returned through the ladder and passage to the first-floor hall. This adds saved-game travel coverage to the earlier cabin and doorway checks. Originals remain preserved. Prototype 0030 is still unfinished and has not been released.


## October 15 — S.S. Anne boarding checked
The private 0030 candidate now connects Vermilion to the S.S. Anne through copied native port rooms. Native playtests confirmed refusal without a ticket, admission with a ticket, and a continuous return walk from the ship to Vermilion. The admission test used one explicitly granted test ticket on a copied save; this does not claim the full Bill-to-ship story is complete.
Separate controlled tests verified that the pre-Hall-of-Fame route reaches the Anne port, while the post-Hall-of-Fame route restores the unchanged native HeartGold port and allows a normal return to the city. All 23 ship regression tests passed. Existing Johto content, original saves and the supplied colored battle artwork were preserved.
Prototype 0030 remains private and unfinished. Ship story events and missing areas, remaining Vermilion/Gym work, and expanded PC item storage still need completion. Prototype 0029 remains the latest published patch.
