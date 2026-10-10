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
  encounters in its two side chambers, at all times of day. Yellow's B2F table
  is also recorded for the remaining story work.
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
picker a required part of 0018. Complete and test it before releasing this
checkpoint. See ITEM-QUALITY-OF-LIFE.md for native integration findings.

Finish the Super Nerd's mandatory fossil battle and exclusive fossil choice;
Jessie and James's ambush, artwork and departure; the remaining visible and
hidden pickups, including Yellow's TMs; and the Mt. Moon Center/Magikarp seller.
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
verified 0017 file, including the cave foundation and the implemented bulk Rare
Candy feature. Run `.venv/bin/python tools/build_prototype0018.py` from
`yellow-heartgold`. Generated files remain in ignored `build/`; this command
does not package or publish a checkpoint. Bulk Candy native checks and all
236 automated tests passed; see validation-prototype-0018-bulk-candy.json. The
remaining Mt. Moon story work listed above still prevents release.
