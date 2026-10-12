# Prototype 0024: Route 25 and Bill

Cumulative from published 0023. Earlier patch folders remain unchanged.
Route 25 retains HeartGold's terrain, models and warps. Its nine trainers use
Yellow's original teams, levels, level-appropriate moves and dialogue. Trainer
classes and overworld sprites match their roles. Morning, day and night grass
uses Yellow's ten species/level slots mapped onto HeartGold's twelve weights,
with encounter rate 15. Surf/fishing encounters are not converted here.

The solid ground ball above the Camper gives reusable TM19 Seismic Toss.
Spare item ID 123 and compatibility bit 106 preserve every existing TM.
Generation I compatibility follows Yellow; later species use HeartGold's
Brick Break compatibility as the adaptation rule. Thunder Wave still displays
TM45 and remains usable. The two hidden rewards are Yellow's Ether and Elixir,
with native A-button/Dowsing behavior and independent pickup flags. Positions
are adapted to accessible tiles in the retained map. The Sea Cottage sign
requires A instead of triggering on touch.

HeartGold's Sea Cottage already contains two chambers and a PC. Bill begins
as a Clefairy, explains the experiment and asks for help. He visibly enters
the left chamber; when approached from above, he walks around the player.
Interact with the PC on the left wall. Native sound effects, timed pauses
and a brief white flash accompany separation. Bill walks out of the right
chamber, thanks the player and immediately offers the S.S. Ticket. A full
Key Item pocket preserves the reward for a later conversation. Returning
after receiving it cannot grant another ticket or repeat the transformation.

Four chamber doorway permissions are opened for these walks. The room's
models, furniture and remaining permissions stay intact. Original HeartGold
story/script/event records remain archived; Johto's terrain and headers are
unchanged. Bill's completion state opens the already-scripted Cerulean police
gate. Restoring the Rocket/Dig follow-up is the next checkpoint.

Bill's PC subsequently offers Eevee, Flareon, Jolteon and Vaporeon portraits
and cries, with Cancel and B-button exit. This adapts Yellow's collection list
to HeartGold's field portrait interface; it does not grant Pokemon or mark
them as caught.

New quest flags A94–A9B and trainer flags 86A–872 sit below HeartGold's daily
reset range. Scene variables 414A–414C avoid bedroom PC storage and existing
story variables. The save format is unchanged. Back up a normal save and use
Continue. Emulator states belong to the exact ROM that created them.

See [the validation record](validation-prototype-0024.json) for executed checks
and their limits. Private transports, staged victories and test Pokemon are
excluded from releases. The reported melonDS/Android 0023 freeze remains
unresolved; the owner and cloud DeSmuME comparison did not reproduce it, and
the owner requested continuing development. Save transfer has not been
established as the cause.
