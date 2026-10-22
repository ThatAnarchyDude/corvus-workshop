# Pokémon Psyduck Yellow — progression corrections prototype 013

This build fixes the issues reported in the prototype 012 Android playtest and adds Yellow’s early Route 22 rival encounter.

The Pokémon League reception gate now intercepts the player in front of the eastern guard. He names the destination Johto and moves the player one tile east, toward Route 22. Separate guards also block the League and Mt. Silver corridors. These entrances remain closed during this opening prototype; future campaign work will supply their progression unlocks. Original HeartGold events and trainer records remain archived for later use.

After parcel delivery, Blue challenges the player near the eastern end of Route 22 with Yellow’s early levels: level 9 Spearow and his chosen level 8 starter. His introductory, defeated, victory and departure text follows Yellow. He walks up to the player and walks away after a victory. Losing uses normal blackout handling and leaves the encounter available. Yellow, Red and Blue use separate fixed early and late Route 22 encounters, rather than dynamically scaling this team to badges. The starter follows the saved lab choice even if the player has evolved or stored their own starter: Eevee players face Psyduck, while Psyduck players face Eevee. New Togepi players give Blue a 50/50 choice of Psyduck or Eevee, always with the opposite gender to that Togepi. Both are saved permanently. Imported older Togepi saves retain the Eevee that Blue already picked. Discuss Blue’s Eevee evolution with the owner before implementing its first evolved encounter; Psyduck and Togepi can evolve normally when later battles are implemented. The later pre-League encounter is future work.

Winning the first lab battle awards exactly the remaining experience to reach level 6: normally 91 for Psyduck or Eevee, and 72 for Togepi. The native battle experience animation, stats and move-learning logic still run. Other battles retain normal experience. A starter already at or above level 6 receives no additional experience from this one scripted battle.

Oak gives five regular Poké Balls and the existing catching/data explanation during the parcel and National Pokédex scene, immediately after Blue leaves. No extra conversation is needed. The gift remains one-time; an unexpectedly full Ball pocket can retry through Oak’s existing recovery dialogue.

Daisy describes Blue as another new trainer. The NPC outside the Trainer House is now a different character with a Trainer House message; the elder outside the actual gym retains the gym-closed message. The duplicate was a reused placeholder, not a second story gate.

Long custom messages now scroll correctly after the second line. This fixes the west guard’s warning and both cashier messages without shortening their requested wording. The issue was textbox cursor placement after scroll commands, rather than missing stored text.

## Shiny odds and Legendary IVs

The base shiny probability is 1 in 4,096. Carrying the passive Shiny Charm Key Item raises it to 1 in 2,048. One Charm is added to the bedroom player's PC for testing, once per save, including imported saves. It cannot be discarded. This prototype reuses HeartGold's Cleanse Tag icon; a custom Charm icon can come later.

The player and Blue retain independent 1-in-16,384 perfect-six-IV rolls, with ordinary random IVs otherwise. A shiny starter with perfect IVs remains possible. Withdrawing or depositing the Charm does not recolour existing Pokémon. The base threshold change can make existing Pokémon with shiny XOR values 8–15 shiny; this is a consequence of changing the engine's base probability. Eggs retain native breeding bonuses. Intentional guaranteed shiny story encounters and Oak's intro Eevee stay shiny.

Native non-shiny rejection is removed from the constructor, Ranger Manaphy hatch, random Mystery Gift and Pokéwalker paths. NPC trades receive the same base/Charm probability; their low personality bits preserve gender and ability, ordinary non-shiny trades keep their fixed personality, and Kenya/Shuckie identity checks accept the exact generated variants. Rare changed personalities can change nature. Fixed-PID distribution gifts supplied externally still carry their supplied personality; this build does not rewrite external gift payloads or emulate unavailable distribution services.

Guaranteed perfect IVs apply only to the 17 existing Yellow/HGSS Legendary encounter species: Articuno, Zapdos, Moltres, Mewtwo, Raikou, Entei, Suicune, Lugia, Ho-Oh, Latias, Latios, Kyogre, Groudon, Rayquaza, Dialga, Palkia and Giratina. The last three are already supported by HGSS's Sinjoh event. No new Legendary encounters are added, and other Legendary/Mythical species do not receive this guarantee. The guarantee applies to newly generated Pokémon and native IV assignments, rather than retroactively rewriting existing saves.

## Playtest

Back up normal saves and use the download page with the original unmodified USA HeartGold ROM. The page builds the full playable NDS locally. Avoid moving emulator save states between versions.

1. Start a new game and win the lab battle. Check that the starter finishes at level 6. Losing must still let the opening continue.
2. Deliver Oak’s Parcel from a pre-delivery save. Watch the Pokédex collection, Blue’s departure and automatic five-ball gift with catching advice.
3. Check Daisy, both building NPCs and the complete west guard/cashier messages.
4. After delivery, take Viridian’s west exit. Check Blue’s level 9 Spearow and level 8 lab starter battle. After winning, leave and return: the encounter should not repeat.
5. Withdraw the Shiny Charm from the bedroom PC. It should appear in Key Items without a Use action and remain after saving/reloading.
6. Continue toward the League gate. The Johto guard must stop you before passing him, describe Johto, and move you right. The other corridors must remain blocked.

## Build

```sh
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/progression_cleanup.py
yellow-heartgold/.venv/bin/python -m unittest discover -s yellow-heartgold/tests
yellow-heartgold/.venv/bin/python yellow-heartgold/tools/package_playtest.py yellow-heartgold/build/browser-download-013 --version 013
python3 yellow-heartgold/tools/check_repo_safety.py
```

Builds from the verified prototype 012 and original USA HeartGold. The native EXP hook applies only to lab trainer IDs 741–746 and party slot zero. Blue’s starter receives independent 1-in-4,096 shiny and 1-in-16,384 perfect-IV rolls, normal random IVs otherwise, and a persistent seed stored in unused saved flags. The independent starter property roll applies only to his starter in the appended lab/Route 22 records; other Pokémon use the global shiny rules above. The Route 22 trainer is a separate appended record. Original scripts/events/parties remain unchanged in their archive members; only approved map headers point to appended replacements. Johto story/maps, the approved intro, map graphics, Cut trees and Pokémon Center services remain intact. Global shiny/Legendary engine changes also apply in Johto.

Validation details and limitations are recorded in `releases/prototype-013/validation.json`. Route 2 and Viridian Forest are next. Owner Android testing is deferred until the complete game; development continues with desktop DS emulator checks.
