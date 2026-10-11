# Prototype 0021 — Cerulean’s initial Yellow visit

Cumulative from 0020. This restores the first Cerulean visit; Route 24, Route 25/Bill and the returning robbed-house/Dig event follow in campaign order.

- Misty uses Yellow’s level-18 Staryu and level-21 Starmie. Gym trainers use level-19 Goldeen and level-16 Horsea/Shellder. Winning awards the Cascade Badge and reusable TM11 BubbleBeam, with a safe retry if the bag is full. The Cascade Badge also permits Cut at an eligible tree.
- Blue visibly approaches at the north bridge. His level-18 Spearow, level-15 Sandshrew/Rattata and level-17 persisted starter retain the agreed starter choice, gender and rare properties.
- Melanie gives one level-10 Bulbasaur when the current lead has at least 147 friendship and there is a party slot. This adapts Yellow’s Pikachu-happiness check to our three starters.
- Cerulean’s Bike Shop uses a separate copy of HeartGold’s bike-shop interior. Its unaffordable price and Bike Voucher exchange follow Yellow. The voucher will come from Vermilion’s fan club in its later checkpoint. Johto’s original shop stays intact.
- The Center retains native healing/link services and Player PC storage. The Mart retains HeartGold’s normal stock and badge unlocks. Badge explanations and Yellow’s city conversations are restored; the owner’s broader dialogue correction list remains future work.
- Pewter’s guide stands in the central road, automatically stops all six exit lanes before Brock, and escorts around solid scenery to the gym. Manual approaches from the other sides align safely into the same path.

The startup issue in unpublished development build 5 was caused by a final code helper leaving the autoload section two bytes short of word alignment. Padding that helper restores title/Continue and normal-save loading; the builder and regression checks now reject that layout.

Normal saves remain in the native format. Back up the ordinary save before switching versions. Emulator save states are tied to the exact ROM. All earlier Fly testing conveniences and progression remain cumulative. Original HeartGold events are archived for later relocation.

Reported gatehouse NPCs inside counters and intermittent transition sprites remain tracked; their exact locations or reproduction are not yet established. No fix is claimed for those observations.
