# Item quality of life

These changes are cumulative additions to the current development build.
Published checkpoints remain unchanged.

## Psyduck evolution

Psyduck now evolves into Golduck only when a Moon Stone is used. Its original
level-33 evolution and the earlier prototype's Water Stone shortcut are removed.
Rare Candies, including at level 100, do not evolve Psyduck. Golduck retains the
previously requested Water/Psychic typing. Other species' evolution methods are
unchanged. Earlier published prototypes keep their original behavior.

Stone evolutions remain usable at level 100. This includes Psyduck's Moon Stone,
Eevee's native and custom stone options, and Togepi's custom Dawn Stone option.
An unsuitable stone has its normal no-effect behavior.

## Reusable TMs

Successful teaching keeps the TM in the bag. Compatibility, move selection,
PP reset, friendship, HM behavior, selling, tossing and depositing retain their
native rules. The Bide TM also becomes reusable.

## Rare Candy at level 100

A level-100 Pokémon can use one Rare Candy to enter its next eligible level-up
evolution. The level and experience stay unchanged. Eligibility uses HeartGold's
existing evolution checks, including minimum level, friendship, time, location,
gender, held items and party requirements. An Everstone retains its normal effect.
Stone evolutions do not become level-up evolutions through this feature.

The usual evolution scene allows cancellation with B. Once an eligible evolution
starts, the candy is consumed even if the player cancels, as with normal Rare
Candy use. An ineligible Pokémon does not consume a candy. Each use triggers at
most one evolution: Bulbasaur can evolve into Ivysaur, and a second use can evolve
that Ivysaur into Venusaur. Their normal minimum levels are 16 and 32.

Implementation: `tools/rare_candy_evolution.py` redirects the party-menu item
dispatcher. It checks eligibility before taking the candy and requests the native
Rare Candy evolution scene. Other items, eggs and Pokémon below level 100 use
the original dispatcher. The patch neither grants experience nor repeats move
learning at level 100.

Validation: native Thumb code execution with service doubles covers eligible
and ineligible results, evolution scene selection, one-item consumption,
missing inventory, eggs and fallback for other levels/items. These tests check
the dispatcher. Additional tests execute the actual native evolution routine
against ROM evolution tables: Bulbasaur and Ivysaur level thresholds, Togepi's
220 friendship threshold, Eevee's day/night branches, Everstone and Pikachu's
stone-only evolution. These do not constitute an emulator playtest of every
evolution.

## Bulk Rare Candy use — required for prototype 0018

The owner confirmed on October 10, 2026 that this must be included in 0018.
It was absent from 0016 and 0017; those published patches remain unchanged.
Do not publish 0018 until the quantity interface and continuation are tested.

Add a shop-style quantity selector, clamped to available inventory and useful
level increases. Apply each candy separately so that moves, evolution prompts
and cancellation remain normal. Spend only the amount actually used. Preserve
the remaining request across evolution and move-learning screen transitions.
At level 100, allow an eligible evolution use without increasing the level.
The quantity selector and continuation logic are not implemented yet.

### Native integration findings

HeartGold's bag overlay 15 already supplies a quantity picker with touch
controls, single/ten/hundred-step adjustments, confirmation and cancellation.
Relevant native entry points are `ov15_021FBCAC` (initialize quantity),
`ov15_021FBD50` (quantity input), and `ov15_021FBF98` (confirmation). These
belong to the Toss path: reuse the controls, not its disposal callback or text.
Normal Use starts at `ov15_021FB680`. Other item actions must retain their
original behavior.

The party menu's `PartyMenu_ItemUseFunc_LevelUpLearnMovesLoop` completes move
learning before checking evolution and returning to the field application.
The field's `Task_StartMenu_WaitEvolution` then returns to the bag. A batch must
carry its remaining count and selected party member through both transitions,
including the separate move-forgetting summary screen. Applying several level
increases inside `UseItemOnMonInParty` would skip intermediate prompts and is
not an acceptable implementation.

Required checks: zero consumption on cancel; inventory and level-limit clamps;
three candies producing three levels and consuming three; intermediate move
learning; evolution and B cancellation with the remainder retained; an eligible
level-100 evolution and an ineligible level-100 no-effect result; correct
behavior with a single candy; and ordinary potion/Toss/Sell actions unchanged.
