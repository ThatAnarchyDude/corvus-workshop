# Pallet opening test — prototype 002

This is a short opening test, not a complete Yellow campaign. Use a NEW game and a separate save from prototype 001. The original HeartGold title screen remains for now; a new title screen is planned.

Unzip `yellow-heartgold-prototype-002.nds.zip` and open the single `.nds` inside in your Android DS emulator. Alternatively apply the `.xdelta` from the patch ZIP to the original US HeartGold ROM, never to prototype 001.

The game now starts in the Pallet upstairs bedroom. Walk to the northeast stairs, go downstairs and leave the house. Visit Oak's lab south of the houses and speak to Oak. Choose Pikachu, Eevee or Togepi; the selected level-5 partner follows immediately, and the National Pokédex is granted at this point. Moving the Dex grant to Oak's parcel return is deferred. Bag, Trainer Card, Save and Options are available without the original Johto introduction. Speaking to Oak again heals the party.

HeartGold's original Kanto event records, scripts and dialogue are preserved in the ROM for future adaptation into the Johto postgame. The opening uses separate appended assets.

Stay within the Pallet opening for this test. The first Pallet rival battle, Route 1 encounter balance, Yellow's campaign, gym changes, all-species acquisition paths and the Johto postgame are unfinished. Existing content beyond this slice can still use HeartGold's postgame levels and story requirements.

Check each starter's selection and immediate follower, the National Dex, house/lab exits, talking to Oak again, normal in-game saving and restarting with Continue. Prototype 001 remains available separately. This version has not yet been tested on a physical Android phone.

Original HeartGold SHA-256: `65f02a56842b75aa92d775d56d657a56fe3fa993550b04dc20704ab82d760105`.

Output SHA-256: `4c4cac888ba52d4eb3ecce80e045cd7b3e6cc2060d8328bf0617f1bffe12b6ef`.

Emulator verification passed for all three starter receipts with immediate visible followers, the National Dex UI, repeat Oak interactions, menu unlocks, normal Togepi save/restart/Continue reload and lab traversal with the follower. Ten automated checks and exact patch application round-trip also passed; details are in `validation.json`.
