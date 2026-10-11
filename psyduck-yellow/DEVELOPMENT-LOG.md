# Pokémon Psyduck Yellow — development log

A plain-language guide to what has changed, what you can play now, and what is
still being built. Share this page with anyone following the project.

**Last updated: October 11, 2026.**

**Latest published patch: prototype 0019.** The playable campaign now reaches
Route 4 after Mt. Moon. This checkpoint fixes sign interactions and ground-item
collision, adds Yellow’s Route 4 encounters and reusable Whirlwind TM, and
keeps its optional level-31 Lass off the main path. Cerulean City is next.

[Create the latest published playable prototype](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/732edbaea0dfbe33dc038db31747b173a21d1f27/psyduck-yellow/prototype-0019/index.html)

The download page contains a modification patch. Select your original,
unmodified USA HeartGold game file to build the playable DS file on your own
device. The original file is not uploaded. Each new checkpoint includes earlier
changes; use the original HeartGold file as input, rather than a previous
prototype. Published checkpoints are kept separately and are not overwritten.

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
| 0019 | Oct 11, 2026 · 12:01 AM EDT | Route 4: Yellow encounters, optional Lass and reusable Whirlwind; working A-button signs, visible Forest boards, solid item balls and carried-save NPC refresh. **Latest published patch.** |

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
  remaining adventure. Route 4 follows Mt. Moon's completion.
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
