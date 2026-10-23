# Prototype 0017 — Route 3

This cumulative checkpoint builds on prototype 0016. Earlier downloads remain
unchanged. Public patches use the original USA HeartGold ROM as their input.

Route 3 has Yellow's eight trainers, species, levels, level-appropriate Yellow
moves and full pre-battle, defeat and post-battle conversations. Trainers are
stationary and use HeartGold's native vision, approach, battles, reward and defeat
flags. They retain suitable original HeartGold trainer positions; the original
route layout, permissions, model assets, music and warps are unchanged. Original
HeartGold trainers and events remain archived.

| Trainer | Team |
| --- | --- |
| Bug Catcher | Caterpie 10, Weedle 10, Caterpie 10 |
| Youngster (“shorts”) | Rattata 11, Ekans 11 |
| Lass | Pidgey 9, Pidgey 9 |
| Bug Catcher | Weedle 9, Kakuna 9, Caterpie 9, Metapod 9 |
| Lass | Rattata 10, Nidoran♂ 10 |
| Youngster | Spearow 14 |
| Bug Catcher | Caterpie 11, Metapod 11 |
| Lass | Jigglypuff 14 |

Grass encounters are Spearow, Mankey, Sandshrew and Rattata at levels 8–12.
The ten Yellow encounter slots are split across HeartGold's twelve slots to
preserve their exact species/level probabilities. Morning, day and night use the
same Yellow table. Inherited radio/swarm replacements cannot introduce
postgame species. Yellow's encounter rate is used; there are no active water,
fishing or Rock Smash tables on this route.

The eastern route sign and resting traveler use Yellow's text. The PC storage
tip says 30 Pokémon per box to match HeartGold. Yellow has no Route 3 item
pickups: the inherited HeartGold item and hidden-item events remain archived
rather than offering late-game supplies.

Pewter's pre-Brock escort remains. Returning to the city after earning the
Boulder Badge disables its former development boundary, opening Route 3.
The city still resets museum admission when leaving the museum. No additional
terrain barriers or test-boundary obstacles are added.

Mt. Moon and Route 4 remain unconverted; they are the next work area. Their
native warps remain available, but their battles/progression are not part of
this checkpoint. Earlier item, opening, shiny, rival and museum changes carry
forward. The bulk Rare Candy selector remains unfinished.

Blue teams that vary with the player's starter Eevee evolution are reserved
for the owner's future complete team plan. This checkpoint leaves existing
Blue teams unchanged.

## Building and validation

From `yellow-heartgold`, run `.venv/bin/python tools/route3.py`, then
`.venv/bin/python tools/package_playtest.py ../psyduck-yellow/prototype-0017 --version 0017`.
The pinned original HeartGold ROM and verified prototype 0016 local build are
required. The builder verifies the cumulative input and xdelta round trip.

Automated checks cover exact teams and moves, encounters and probabilities,
trainer dialogue indexing, NPC positions, original archives, all other map
headers, existing warps, Johto resources and earlier native item hooks. The
browser downloader rejects incorrect input and generates the verified ROM with
its four-digit filename. Detailed results are recorded in
`validation-prototype-0017.json`. All 218 tests passed. Native emulator checks
loaded a normal save carried from 0016, crossed Pewter’s post-Brock exit in both
directions, and completed the shorts Youngster’s battle with Rattata 11 and
Ekans 11. The defeat flag and post-battle dialogue were verified. The private
setup granted a test Pokémon and badge using native commands; it is absent
from the published ROM. These checks do not constitute all eight battle
playthroughs, audible sound checks, or a complete campaign test.
