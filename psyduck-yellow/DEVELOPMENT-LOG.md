# Pokémon Psyduck Yellow — development log

A plain-language guide to what has changed, what you can play now, and what is
still being built. Share this page with anyone following the project.

**Last updated: October 11, 2026 at 10:47 PM EDT.**

**Latest published patch: prototype 0023.** Route 24 now has Yellow’s Nugget Bridge contest, Nugget/Rocket event, Charmander gift, Thunder Wave TM and grass encounters. Blue correctly stops you on the bridge. Mt. Moon’s extra figure is removed, its fossil guard battle is automatic, and Jessie/James ambush every exit approach after fossil selection. Route 25 and Bill follow next.

[Create the latest published playable prototype](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0023/index.html)

The download page contains a modification patch. Select your original,
unmodified USA HeartGold game file to build the playable DS file on your own
device. The original file is not uploaded. Each new checkpoint includes earlier
changes; use the original HeartGold file as input, rather than a previous
prototype. Published checkpoints are kept separately and are not overwritten.

## Watch recorded playtests

[Watch the recorded playtests](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/playtests/index.html).

This public page will receive additional recordings during active development.
A new 30-second prototype 0022 sample includes real game music and stereo audio.
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
| 0023 | Oct 11, 2026 · 10:47 PM EDT | Nugget Bridge, Charmander and reusable Thunder Wave; correct Blue bridge approach; Mt. Moon fossil rendering and mandatory guard/exit battles. **Latest published patch.** |

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

Continue Route 25/Bill and the returning Cerulean robbed-house/Dig event. The requested friendship-testing item is available in 0022.

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
