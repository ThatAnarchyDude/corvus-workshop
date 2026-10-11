# Prototype 0020 — testing travel

Cumulative from prototype 0019. This checkpoint contains only the requested testing conveniences; Cerulean campaign conversion moves to prototype 0021.

- Route 4's final one-way crossing now permits walking in both directions, allowing a return from Cerulean toward Mt. Moon. The existing ledge artwork remains; walk through its westernmost tile, immediately beside the trees.
- Celadon Department Store's **third-floor TM counter** stocks **HM02 Fly for ₽0**, alongside its existing TMs. The native quantity picker allows one per purchase safely, even with no money.
- Teach Fly to a compatible Pokémon normally. Outdoor Fly no longer requires a badge. Its usual outdoor, visited-destination and temporary story restrictions remain. No badges are granted and other field moves are unchanged.
- Keep these conveniences during testing. Normal save layout and earlier campaign data are unchanged; continue your existing normal in-game save. Emulator save states depend on the exact ROM and are not portable between prototypes.

The patch page builds the complete playable file locally from your original, unmodified USA HeartGold ROM. ROMs and testing saves are not published.

## Validation

Six focused tests cover native Fly checks, the free-item shop quantity calculation, shop stock preservation, exact code/data changes, unchanged campaign assets and bidirectional terrain connectivity. Native emulator checks cover walking across the crossing, buying HM02 without spending money, teaching Fly, and a normal save/reload with HM02 retained. The browser rejects incorrect input and downloads a file matching the release hash; xdelta reconstruction matches the same hash.

Build: `.venv/bin/python tools/release_prototype0020.py`. Existing release artifacts are protected against overwriting.

Published October 11, 2026 at 12:55 AM EDT. [Prototype 0020 download page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/28b5fd7b8dd7e5311d0c182b5d047f91ffca451b/psyduck-yellow/prototype-0020/index.html). Prior patch exports remain unchanged.
