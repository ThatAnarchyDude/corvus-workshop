# Prototype 0021 — published

Cumulative from published 0020. Published October 11, 2026 at 10:30 AM EDT. Preserve the existing checkpoints.

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

Startup issue resolved in development build 6: padding the final Cut helper restored word alignment of the autoloaded code section. Native boot reaches the Psyduck title, Continue, and the carried normal save. A regression check fails on build 5 and passes on build 6. The Bike Shop now displays its no-voucher welcome instead of incorrectly assuming a Bicycle is owned. Fifteen focused checks pass, including original map/archive preservation, serialized Yellow teams, chained TM lookup, and native Cut prerequisites. Voucher exchange and remaining native city checks continue before release.

Next-build request: add a reusable or automatic maximum-friendship test item in the player’s PC storage, including existing saves. See PROTOTYPE-0022-PLAN.md. This is not part of 0021.

Release validation complete: startup fixed; 16 focused checks and browser/hash roundtrip pass. Native guide, voucher/save/reload, Bulbasaur gift, Misty battle/rewards, Blue battle/departure and Center healing/Player PC menus checked. Genuine Save followed by final-ROM fresh reload retained one BubbleBeam and its received flag. Test-only boosted party is private and absent from the released game.

Published patch: https://raw.githack.com/ThatAnarchyDude/corvus-workshop/876971401fd392cad83d2230842f086e236925bc/psyduck-yellow/prototype-0021/index.html
