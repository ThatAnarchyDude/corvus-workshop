# CHECKPOINT (campaign-loop)

Newest ROM: /mnt/c/RetroArch-Win64/downloads/Pokemon-Psyduck-Yellow-0041-engine-map-extension.nds (engine only, no Tower).
Work ROM (not a release): yellow-heartgold/build/0041-lavender-tower-v1/tower-t4.nds, built by tools/campaign_build.py tower
  (args: tower <0041 engine ROM> <out.nds> <pret/pokeyellow clone dir>).
Done: map header extension (IDs 540+). Tower 1F-7F = Bell Tower clones (540-546), Yellow Channelers 3F-6F + wilds, Lavender Radio Tower door <-> Tower 1F until flag 0x964.
Fixed this session: land-data permission block starts at byte 16 (not 20); trainers/arrival now sit on passable tiles inside the rooms (3F floor map verified by dump).
Unconfirmed: 3F battle trigger by screenshot (fixture 542 at 13,11 facing down; inputs showed no visible battle, only trainer sprites shifting). Recheck with a longer run.
Gaps: 2F rival, 6F Marowak ghost gate, 7F Jessie/James + Mr. Fuji, Poke Flute (Fuji house = map 435), floor items/NPCs, Silph Scope.
Next: confirm battle trigger, build the scenes above, then copy a tested ROM as ...-0041-lavender-tower.nds.
