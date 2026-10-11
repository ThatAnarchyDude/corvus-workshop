# Prototype 0018 — Mt. Moon work in progress

This checkpoint is **not published or ready for playtesting**. Prototype 0017
remains the latest downloadable patch. Never package the private test fixture.

The first implementation builds cumulatively from the verified 0017 ROM,
SHA-256 `71f86b48272129c0f3d8f6b876403bf831c454b5917add58caf9921560f1976d`.

## Implemented in the unpublished foundation

- Yellow's seven first-floor trainers and three ordinary Rocket grunts, with
  exact species, levels and explicit Yellow moves. These use native HeartGold
  trainer portraits and battle dispatch, with new persistent defeat flags.
- Yellow first-floor wild encounters in HeartGold's main cave, and Yellow B1F
  encounters in its two side chambers, at all times of day. The fossil corridor
  selects Yellow's B2F table using the player's live position.
- The Zubat warning sign and trainer conversations, with complete scrolling.
- Two Potions, a Moon Stone, a Rare Candy and an Escape Rope, each collected
  once and left available if the bag is full.
- Original native passages and geometry retained. Silver's endgame cave battle
  and the weekday warp changes are archived, rather than active in this draft.
  The separate square and its events remain unchanged for now.

The pinned source is pret/pokeyellow commit
`e89ead154b9968aa50eed9328ff2b38b6c194382`. `data/mtmoon.json` records dialogue,
teams, moves and encounters. `tools/mtmoon.py` has no publication entry point.

## Required before release

The owner's October 10 testing feedback makes the shop-style bulk Rare Candy
picker a required part of 0018. It is implemented and natively verified: apply
the batch, offer intermediate-level moves, then check evolution once. See
ITEM-QUALITY-OF-LIFE.md and validation-prototype-0018-bulk-candy.json.

Finish Jessie and James's artwork and the fossil prop graphics. Complete native
checks of the remaining rewards, deeper-cave encounters and final traversal.
Confirm the story can be completed on HeartGold's smaller cave layout without
adding terrain obstacles. Test the scenes and rewards natively, then package an
immutable cumulative 0018 patch and publish its link. Do not release this
foundation as though those scenes already work.

Preserve ordinary 0017 save backups. Use native-command private fixtures to
prepare cave progress; do not edit save bytes or reuse another ROM's save state.

## Owner playtest feedback

On October 10, 2026 the owner reported no issues in 0016 except the previously
deferred roadblocks, and began testing 0017. Keep those roadblocks deferred.
This does not authorize adding new HM obstacles to Kanto.

## Foundation verification

Six Mt. Moon checks and six Route 3 regression checks passed. The ordinary
0017 save loads in the draft with the Route 3 Youngster's defeat flag retained.
A private native-command warp prepared a cave-entry normal save, which was then
reloaded on the actual draft. The cave Youngster's Rattata 10, Rattata 10 and
Zubat 10 were defeated in the DS emulator; his defeat flag and post-battle
conversation were checked. Other cave battles, pickups and audio playback have
not been playtested yet. Details are in validation-prototype-0018-foundation.json.

## Updated development build

`tools/build_prototype0018.py` builds the cumulative unpublished ROM from the
verified 0017 file, including the cave foundation, story, Center, rewards, and
bulk Rare Candy feature. Run `.venv/bin/python tools/build_prototype0018.py` from
`yellow-heartgold`. Generated files remain in ignored `build/`; this command
does not package or publish a checkpoint. Bulk Candy native checks and all
236 automated tests passed in the earlier bulk feature build; see
validation-prototype-0018-bulk-candy.json. The remaining release checks and art
listed above still prevent publication.

## Added cave story and services

`mtmoon_story.py` adds the Super Nerd's Grimer, Voltorb and Koffing at level 12
with Yellow's moves. He visibly approaches the player, battles, returns, and
offers one fossil. Bag-full and declining branches award nothing and change no
quest state. After collection, he walks to collect the other fossil. Native DS
checks verified a Dome Fossil choice, both props disappearing, control returning,
and the choice persisting through a normal save and fresh boot. Both fossil
branches and battle-loss handling also have focused automated checks.

Saved quest variables are `0x4140` (0: boss pending, 1: choose a fossil,
2: fossil chosen, 3: Rockets beaten) and `0x4141` (1: Dome, 2: Helix). These were
unused by the native game. Both cave headers now use native cave battle scenery.

`mtmoon_center.py` keeps the native nurse, warps and communication staff and
copies the verified Center PC service with shared player item storage. The
$500 level-5 Magikarp sale charges only after successfully adding the Pokémon;
declining, insufficient funds, a full party or a failed gift cost nothing.
Native checks verified one sale, a second refusal, healing and the player PC
menu. Focused tests cover the failure branches and preservation of services.

`mtmoon_tms.py` adds reusable TM12 Water Gun (item 116, compatibility bit 101)
and TM01 Mega Punch (item 117, bit 102). HeartGold's original TMs remain intact,
including Taunt and Focus Punch. Gen I compatibility follows Yellow; later
species inherit Water Pulse and Focus Punch compatibility respectively. The
existing native pocket capacity and save layout are retained. Thumb execution
tests verify every existing item lookup, added moves, displayed numbers and
unchanged bag IDs/registers. `mtmoon_items.py` adds these pickups and HP Up,
plus a native hidden Moon Stone and Ether with Dowsing Machine support. Hidden
IDs 8195 and 8198 have no active uses elsewhere after cave conversion.

`mtmoon_rockets.py` adds Yellow's fossil ambush dialogue and the original level-14
Ekans, Meowth and Koffing team. The draft uses native Rocket placeholders pending
Jessie/James art. Both characters walk into position and leave via the exit after
victory. Battle loss keeps the encounter pending. The trigger is a saved story
condition, without new HM terrain obstacles or geometry changes. Native checks
verified the complete battle and departure; artwork and final traversal still
prevent release. The ordinary Bug Catcher now stands in the eastern pocket at
(24,16), keeping his line of sight clear of the scripted Rocket exit trigger.

Native checks verified learning Mega Punch on Golduck while retaining the TM,
then a confirmed normal save and fresh boot with the TM still present. The
hidden Moon Stone is awarded once and stays collected through a normal save and
fresh boot. The Rocket victory and hidden actor flags also persist after saving
and reloading. Remaining item checks are listed in the current validation record.

`mtmoon_encounters.py` selects Yellow's B2F table for map 107's fossil corridor
(live player z >= 20). It reads the active player's map object, never saved
coordinates, and falls back to the native table everywhere else. Thumb execution
checks cover all 540 map IDs, the boundary and missing transient pointers;
morning, day and night share Yellow's species and levels. Map archives,
terrain and save structures remain unchanged by this selector.

Developer builds can use `--output build/unique-name.nds`. Never overwrite the
ROM used by an active emulator state; carry ordinary saves into a fresh boot
instead. Private fixtures must use one native warp transition at a time and verify the
result through a normal menu save and fresh boot before continuing.

## Current regression checkpoint

All 259 automated tests passed after the live B2F table selector and Bug Catcher
position correction. Native checks on the new deeper-cave build loaded the
completed Rocket ordinary save with its flags preserved and encountered
Geodude at level 11 in the fossil corridor. The hidden Ether was awarded to the
Medicine pocket. See validation-prototype-0018-mtmoon.json for exact builds,
checks and remaining limitations. No 0018 patch has been published.
