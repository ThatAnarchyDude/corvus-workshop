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

The native bag quantity controls select the requested amount before choosing a
Pokémon. Apply the useful candies first, then process every move available at
the intermediate levels, and check evolution once at the end. Pokémon with four
moves still need replacement choices. Only the current species' learnset is
processed during the batch; evolution happens afterwards. One batch triggers at
most one evolution, with the usual B cancellation.

The quantity picker is bounded by inventory. After selecting the Pokémon,
actual use is also bounded by the remaining levels to 100. Unused candies stay
in the bag. The existing eligible level-100 evolution behavior remains intact.
Runtime batch data lives in ITCM and does not change the save format.

Implementation: `tools/bulk_rare_candy.py` redirects only the Rare Candy Use
entry into the native overlay-15 quantity widgets. Confirmation returns to Use;
it never reaches Toss. The native level-up callback applies the batch using
HeartGold's item service. A scoped learnset hook scans the intermediate levels
without temporarily changing the Pokémon's actual level. Native move replacement
screens remain available. The original final evolution check remains unchanged.

Validation: twelve Thumb execution checks cover consumption, inventory and
level caps, one-candy use, the actual native intermediate learnset scan,
replacement cursors, quantity confirmation/cancellation, original label
restoration, Potion bypass and clearing batch data on exit while preserving it
for move replacement. In the DS emulator, selecting three candies raised
Bulbasaur from 14 to 17, offered its level-15 Take Down, returned from the normal
move replacement summary, evolved once into Ivysaur, and left two of five
candies. The final button label fits; cancelling the quantity picker leaves all
five candies. A normal save prepared with native game scripts loads in the
actual development ROM. B cancellation of the final evolution was also tested: Bulbasaur stayed at
level 16 after a two-candy batch. Saving and a fresh boot preserved that level
and the three remaining candies. All 236 automated tests passed. Audible sounds
were not tested.
Prototype 0018 remains unpublished until its remaining Mt. Moon content and
release checks are complete. See validation-prototype-0018-bulk-candy.json.
