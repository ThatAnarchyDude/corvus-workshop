# Pokémon Psyduck Yellow — development log

A plain-language guide to what has changed, what you can play now, and what is
still being built. Share this page with anyone following the project.

**Last updated: October 10, 2026.**

**Latest published patch: prototype 015.** The playable campaign currently
reaches Pewter City and Brock's gym. This is an unfinished game, not a complete
Yellow remake. Prototype 016 is in development and has not been released.

[Create the latest published playable prototype](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/532f79780c06314bbb0e8615e485da9aee55874f/psyduck-yellow/prototype-015/index.html)

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

## Changes you can play in prototype 015

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
- **In published prototype 015**, Psyduck can evolve normally by level and also
  by Water Stone. The Moon Stone replacement below is still unpublished.
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
  Shock Wave TM34 remains separately available. In prototype 015, teaching
  Bide still consumes its TM; reusable TMs are part of the unpublished update.
- Pewter's optional interior conversions are unfinished in the published patch.
  Route 3 is currently the next development boundary.

## Unpublished development work — prototype 016

These changes are in source or local builds. **They are not in the prototype
015 download above, and this section is not a release announcement.**

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
- The requested **bulk Rare Candy quantity selector is not implemented yet**.
  It must preserve each level-up's move learning, evolution and correct item use.

The development build passed 210 automated checks, including Moon Stone
evolution, removal of Psyduck's earlier methods, and existing stone evolution
at level 100. The revised museum also passed 17 focused Pewter checks; both stair transitions
worked in a DS emulator, and the local downloader reproduced the verified ROM.
These checks are not a complete playthrough of the unfinished update.

## Release history

Each row describes what that version added; later versions include earlier
changes and sometimes correct or replace them. The sections above describe the
current rules, so older details should not be mistaken for today's behavior.

Historical dates and AM/PM times below come from the recorded release commits,
converted to Eastern Time (America/New_York). They are the best available release
records; the exact GitHub push or hosting activation times were not recorded.
Prototype 009 uses the intro release, following the withdrawn shop experiment.
Future checkpoints will record their confirmed publication date and time.

| Checkpoint | Made live (Eastern Time) | Main changes |
| --- | --- | --- |
| 001 | Oct 8, 2026 · 8:41 PM EDT | First Android testing patch and instructions; early starter and Pallet-opening experiments. |
| 002 | Oct 8, 2026 · 10:56 PM EDT | Pallet opening with protected HeartGold event assets, starter selection and follower tests. |
| 003 | Oct 9, 2026 · 12:40 AM EDT | Bounded Yellow opening, intro rival naming and low-level Route 1 setup. |
| 004 | Oct 9, 2026 · 6:50 AM EDT | Visible Oak escort/capture scene, three physical starter balls, immediate follower, Blue opening, starter properties and bedroom item storage. |
| 005 | Oct 9, 2026 · 12:37 PM EDT | Psyduck swimming title screen and project logo. |
| 006 | Oct 9, 2026 · 1:11 PM EDT | PC evolution supplies and additional item evolution choices. |
| 007 | Oct 9, 2026 · 3:18 PM EDT | Mom's Running Shoes, Route 1 travel, cashier escort, Oak's Parcel, delayed National Pokédex and Viridian Center item storage. |
| 008 | Oct 9, 2026 · 5:40 PM EDT | Center doorway fix, removal of the extra cashier after pickup, upper-cashier shopping and Poké Ball sales. |
| 009 | Oct 9, 2026 · 7:42 PM EDT | Shiny Eevee introduction and Blue's full portrait on intro/confirmation screens. |
| 010 | Oct 9, 2026 · 9:45 PM EDT | Old man's catching lesson, Oak collecting visible Pokédexes, corrected leftover starter-ball text. |
| 011 | Oct 9, 2026 · 11:59 PM EDT | Old man's center-lane placement, Blue portrait moved to the touch-screen panel, aligned Eevee/sparkles. |
| 012 | Oct 10, 2026 · 1:02 AM EDT | Persistent side Cut trees, granddaughter moving aside, cashier Pokégear/Map reward, western warning guard and temporary barrier removal. |
| 013 | Oct 10, 2026 · 3:42 AM EDT | League guard fixes, early Route 22 Blue battle, exact level-6 lab reward, automatic Oak Poké Balls, dialogue repairs, fair rival starter rolls, global shiny odds, Shiny Charm and scoped Legendary IV rules. |
| 014 | Oct 10, 2026 · 4:19 AM EDT | Route 2 and Viridian Forest encounters, trainers, items and conversations; removal of inherited Kanto HM terrain gates. |
| 015 | Oct 10, 2026 · 5:36 AM EDT | Pewter outdoor events, Brock's gym/Boulder Badge/Bide TM, Water/Psychic Golduck. **Latest published patch.** |
| 016 | Not published yet | Pewter interiors/museum and item improvements described above. **Unpublished; still being checked.** |

[Detailed release notes and verification records](https://github.com/ThatAnarchyDude/corvus-workshop/tree/9282bba885b399df77f451f36dd07ea0b6aa5dc7/yellow-heartgold)

## Agreed plans that are not finished features

- Continue Yellow's Kanto campaign through Giovanni's eighth badge, then the
  remaining adventure. Route 3 and Mt. Moon follow Pewter's completion.
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
