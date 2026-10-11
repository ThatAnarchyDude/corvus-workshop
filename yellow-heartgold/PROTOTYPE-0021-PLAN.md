# Prototype 0021 — active work

Cumulative from published 0020. No 0021 patch is published yet. Preserve the existing checkpoints.

- Cerulean’s initial Yellow visit: native Center/Player PC services, HeartGold shop sales rules, Blue’s north-exit scene with his persisted starter, Misty’s Yellow teams and Cascade Badge, reusable BubbleBeam TM, and Melanie’s level-10 Bulbasaur gift. Adapt Yellow’s 147 happiness requirement to the current lead Pokémon’s HeartGold friendship because this game has three starters.
- Restore Cerulean’s Bike Shop using a separate clone of HeartGold’s existing bike-shop interior, retaining Johto’s original map. Implement Yellow’s unaffordable price and Bike Voucher exchange, retaining the voucher if the gift fails. The Vermilion fan club will provide the voucher in its area checkpoint.
- Correct Pewter’s guide placement, cover all six walkable exit rows, use a dedicated pre-Brock state, and escort around solid scenery to the gym.
- Preserve the normal 0020 testing save including HM02 and Pidgey’s Fly. Test the new content through native gameplay and save/reload.
- Record the owner’s 0020 notes: NPCs embedded in unidentified gatehouse counters; intermittent transition sprite glitches cleared by opening/closing the Bag. Reproduce before attributing them to the owner’s older emulator. A screenshot/location is not available yet.
- Future dialogue review: wait for the owner’s Current Dialogue → Expected Dialogue list before broad wording changes.

Route 24, Route 25/Bill, and the returning robbed-house/Dig sequence follow in their campaign order. The initial Cerulean visit must not activate HeartGold’s missing-Misty, power-plant or Suicune postgame scenes. Those original assets remain archived for later relocation.

## Development checks so far

- Ten focused script-decision and CPU-hook tests pass, covering all six Pewter exit lanes, manual guide interactions from all four sides, reward failure/retry decisions, and Blue’s persisted starter properties.
- A genuine pre-Brock normal save reaches the automatic guide stop on a previously bypassable lane and completes the escort to the gym in the native emulator. Escort and return coordinates were checked against map collision data.
- The initial native Bike Shop check exposed an incorrect inventory command (checking capacity instead of ownership). Corrected to HeartGold’s HasItem command; the revised build still needs its voucher and no-voucher native checks.
- This checkpoint remains unpublished. Complete remaining native service, battle, gift, and save/reload checks before preparing a public patch.

Latest native check: development build 5 repeatedly remained in the opening animation instead of reaching Continue. Do not publish it. Its final appended Cut helper left the ITCM autoload section two bytes short of word alignment; build 6 pads that helper to test this suspected startup cause. The inventory correction is source- and decision-tested but not yet validated in native play.
