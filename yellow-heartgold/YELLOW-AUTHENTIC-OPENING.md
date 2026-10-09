# Pikachu Yellow: Yellow-authentic opening (work in progress)

**Purpose:** replace the Prototype 003 shortcuts with the original Yellow staging and in-world starter scene, using HeartGold's engine, audiovisual style, and following-Pokémon system.

**Branch status:** source and audio-cue staging only. No rebuilt ROM or gameplay validation has been completed for this branch. **Prototype 003 remains the known-good build.** Do not substitute this branch as an Android release.

## Original Yellow scene reference

Source: [pret/pokeyellow scripts/PalletTown.asm](https://github.com/pret/pokeyellow/blob/master/scripts/PalletTown.asm) and [scripts/OaksLab.asm](https://github.com/pret/pokeyellow/blob/master/scripts/OaksLab.asm).

1. Player attempts northward exit without a Pokémon.
2. Music switches to the Professor Oak encounter; Oak says "Hey! Wait!" and approaches the player on-screen.
3. Yellow has a scripted wild Pikachu capture by Oak. Three-starter adaptation of the captured Pikachu is a **design question**, not yet solved.
4. Oak warns the player, then leads them south through Pallet Town. Player follows on foot with visible, verified turns; no script warp directly from Route 1 edge to the lab.
5. Both cross the lab doorway with normal warp/door behavior. Oak and player continue walking *inside* to their positions; only then does the conversation begin.
6. Yellow places its Poké Ball on a table to the right. Our agreed branch gives **Pikachu, Eevee, or Togepi** as selectable starters in-world, each at level five; retain the opponent choices and immediate follower.
7. Rival interrupts the attempted departure, walks toward the player, and the lab battle begins with encounter music; winner and loser dialogue, rival departure, and sound reset must be staged rather than instant moves.

### Existing HeartGold asset inspection

- Pallet map 49 currently has a **new** Oak actor (script object 3, sprite 366, staged at 1038,354 in Prototype 003), created by the development scripts. Native HG Pallet object 0 at (1040,367) is an unrelated woman (sprite 325); do not overwrite her.
- Prototype 003 triggers Oak at north boundary and uses `SetObjectMovementType` to move him near the player, followed by a direct `RockClimb`-op-indexed? (see exact verified opcodes) map transition; this shortcut must be deleted from the **final** live script, not hidden behind animations.
- Native HeartGold Oak's lab map 505 includes three ball objects at (7,3), (8,3), (9,3), sprite 87. Reuse their visual style in the **appended** Kanto event bank, but make them independently interactable. Do not modify or delete the original archive.
- Current `tools/prototype.py` globally replaces Johto starter species in binary code with (25,133,175). The Yellow manual-selection implementation must eventually reverse that global patch and give Yellow starters through **Kanto-only script logic**, otherwise Johto would incorrectly offer Yellow starters.
- Oak's currently scripted selection uses the stock HeartGold `ChooseStarter` interface. Remove that call from the Kanto storyline **only after** the physical Poké Ball interactions and follower initialization pass testing.

## Script and sound references

From [pret/pokeheartgold script commands](https://github.com/pret/pokeheartgold/blob/9d8b7591f09b65804da2fb2dfd56f320633e0d36/src/data/fieldmap/script_cmd_table.h) and [sound constants](https://github.com/pret/pokeheartgold/blob/9d8b7591f09b65804da2fb2dfd56f320633e0d36/include/constants/sndseq.h):

| Event | Script command / available cue | Status |
| --- | --- | --- |
| Oak calls out | PlayBGM opcode 80, sequence 1067 (Oak theme) | Staged in source, untested |
| Escort starts | PlayBGM opcode 80, sequence 1086 (escort cue) | Staged in source, untested |
| Rival challenge | PlayBGM opcode 80, sequence 1088 (HG rival cue) | Staged in source; **not** verified as Yellow's intended melody |
| Rival leaves | ResetBGM opcode 82 | Staged, untested |
| Physical Poké Ball selection | PlaySE opcode 73, menu selection cue | Not implemented |
| Starter cry | PlayCry opcode 76, WaitCry opcode 77 | Not implemented |
| Received a Pokémon | PlayFanfare opcode 78, WaitFanfare opcode 79, sequence 1187 | Not implemented |

These numbers identify existing HGSS sounds, **not** yet a claim of faithful Yellow music reproduction. New arrangements or replacement audio require separate asset work, tests and appropriate permissions.

## Blue and Johto preservation

- Blue's Kanto overworld sprite is present (sprite 375). For battles, `TRAINERCLASS_RIVAL` 23 uses the stored custom rival name but shows the Johto rival portrait. `TRAINERCLASS_LEADER_BLUE` 110 shows Blue's image but can alter the trainer class/name. **Never swap class 23 to 110 indiscriminately.** Use Kanto-rival-specific portrait assignment that preserves the saved rival name and leaves every Johto trainer unaffected.
- Leave the original red-haired rival, normal Johto story, maps and starter presentation intact for later postgame access. The only Johto campaign change approved so far is the separately planned gym-leader scaling.
- The HG starter chooser should be retained for a **future Johto event**, with its original species 152/155/158. Do not wire the Johto gift or override its unlock without an approved transition design.

## Acceptance gates before releasing a replacement

- All valid north-exit columns and both player genders; no NPC sprite snapping or magically appearing near the player.
- Both Oak and player visibly reach the Pallet lab doorway; door warp occurs only at the entrance. Oak and player continue into the lab, no loading-screen teleport to their final standing positions.
- Oak's scene handles Pikachu capture, dialogue, BGM changes and scene persistence, including saving/reloading during appropriate intervals.
- Right-side table visibly has three Poke Balls; player walks to one, presses A, hears selection cue, sees specific starter preview/name/cry, can decline, and confirms the choice with no touchscreen Elm interface.
- Only one chosen starter is granted; the opponent chooses the documented partner, both are level five; immediate following and the National Dex timing remain as already agreed.
- Blue (not Silver) is drawn in all Kanto dialogue/battle contexts; chosen name appears correctly. Silver and his existing Johto events are unchanged.
- Rival approaches before the lab-exit battle and visibly departs afterward. Appropriate encounter and battle music transitions play, followed by lab music restoration.
- Fresh saves for all three starters; save/reload; follower swaps; regression against Proto003; PC + Android melonDS acceptance; valid patch roundtrip. Fail closed on any missing evidence.

## Existing staged source

`tools/yellow_opening_scene.py` provides sound constants and **candidate** geometry for a future walking scene; `tools/opening.py` has initial meeting/escort/rival music calls. Neither change eliminates the old scripted teleport yet. Do **not** call this a complete implementation.

Keep this branch separate from `pikachu-yellow-development` and the owner's known-good `android-prototype-003` build until all new scenes pass acceptance.
