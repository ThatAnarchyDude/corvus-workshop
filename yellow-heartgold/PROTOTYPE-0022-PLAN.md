# Prototype 0022 — released save repair checkpoint

Cumulative from published 0021; retain all previous patch pages.

## Requested first

Repair normal-save compatibility before adding campaign content. Prototype 0021 allocated flags beyond HeartGold's persistent flag array; earlier custom flags also occupy the native daily-reset range. Relocate the new flags into a verified unused persistent range, protect the earlier quest/reward flags from daily clearing, and reject future out-of-range allocations. Test ordinary Continue saves across versions and across a daily rollover.

Recover completed parcel/Pokédex/Viridian events using independent saved evidence, without granting them to new games. Include Brock's one-time Bide reward in recovery and repeat-interaction tests; do not remove items already in the player's inventory.

Show Kanto's badge page first on the Trainer Card, keeping the saved badge identities intact.

Add a temporary friendship-testing item to the player's PC storage. It must grant maximum native HeartGold friendship (255) for happiness-based evolution tests. The owner permits a reusable item or an automatic Key Item, whichever is simpler to implement safely. Prefer a reusable selected-Pokémon action if it fits the native item system; otherwise use the permitted automatic Key Item. Make the supply available to existing saves as well as new games. Do not silently claim that maximum friendship overrides species, time, held-item or other evolution prerequisites.

## Campaign work afterward

Continue Yellow's progression through Route 24, Route 25/Bill and the returning Cerulean robbed-house/Dig event. Preserve Johto's original maps and HeartGold event archives. The wider Current Dialogue → Expected Dialogue review remains deferred until the owner's list.

The compatibility fixes take priority in 0022; campaign additions move to 0023.

Published October 11, 2026 at 1:46 PM EDT. Publication receipt and focused checks are recorded in `releases/prototype-0022/publication.json` and `validation-prototype-0022.json`.
