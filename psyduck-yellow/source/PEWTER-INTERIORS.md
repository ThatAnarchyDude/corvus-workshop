# Prototype 0016 — Pewter interiors and item improvements

This cumulative checkpoint starts from prototype 0015 (previously labeled 015).
Earlier downloads retain their existing names and URLs. New checkpoints use
at least four digits.

Pewter's houses, Mart and Pokémon Center have Yellow's conversations and NPC
roles. The Center retains HeartGold's nurse, upstairs receptionists, Pokémon PC
and player item storage; the Mart retains HeartGold's shop progression.
Jigglypuff uses its cry and the native lullaby. Brock's interaction uses the
proper menu selection sound command.

The museum charges 50 Pokédollars per visit. Refusing admission or lacking money
returns the player outside. Reloading a normal save inside does not charge
again. A scientist gives one Old Amber, with retry if the bag cannot accept it.
Fossil revival belongs to the later Cinnabar conversion; the original HeartGold
museum revival and named-character scripts remain archived.

A second museum floor contains Yellow's upstairs visitors and exhibit dialogue.
It uses a previously unused map header, cloned HeartGold museum geometry and
native stairs. Original area models, textures and animation metadata stay
unchanged. Custom space-exhibit miniatures were deferred after emulator loading
failures; existing HeartGold displays are used instead.

TMs now remain in the bag after successful teaching, including Bide. A Rare Candy
can trigger an eligible level-up evolution at level 100 without changing the
level or experience. Native prerequisites still apply and B can cancel the scene.
Psyduck now evolves only using a Moon Stone, including at level 100; its former
level-33 and Water Stone methods are removed. Golduck stays Water/Psychic.
See [item behavior details](ITEM-QUALITY-OF-LIFE.md).

The bulk Rare Candy quantity selector remains unfinished. This checkpoint
contains single-item use improvements only.

## Build and validation

From `yellow-heartgold`, run `.venv/bin/python tools/pewter_completion.py`, then
`.venv/bin/python tools/package_playtest.py ../psyduck-yellow/prototype-0016 --version 0016`.
The verified local base HeartGold ROM and prototype 015 build are required.
The output is `build/yellow-heartgold-prototype-0016.nds`; public distribution
uses the patch and a local browser downloader.

The full automated test results are recorded in `validation-prototype-0016.json`.
Focused tests preserve native services, original archives, other map headers and
Johto resources. Native Thumb execution checks reusable TM teaching, Rare Candy
fallback/consumption and the original evolution engine against ROM tables.

The final ROM loaded both museum floors in the DS emulator, returned downstairs,
and awarded one Old Amber. Repeating the conversation retained one copy and
showed the reminder. A Chromium test rejected incorrect input and generated a
ROM matching the manifest hash, with the four-digit filename and no page errors.
The xdelta round trip matched the ROM exactly. These checks do not constitute
a complete playthrough or an audible verification of every sound/evolution.
