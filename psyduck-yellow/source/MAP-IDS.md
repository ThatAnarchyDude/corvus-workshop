# MAP / DATA IDS (reference; keep appending, do not re-derive)
Verified = tested live or read straight from a builder's constants. Inferred = deduced from header order/mapsec and consistent with warp counts, not yet exercised.

## Extension maps (header ids >= 540, installed by map_header_extension.py; native maps are 0-539; 587 headers in ROM 0148)
| ids | what | status |
|---|---|---|
| 540-546 | Pokemon Tower 1F-7F (area 113-119, mapsec 70) | inferred (tower-handoff note) |
| 547-550 | old Rocket Hideout stand-in clones (script banks/texts still used by 560-563) | verified (hideout_yellow.py OLD) |
| 551-554 | old Silph stand-in clones (scripts still used by 564-574) | verified (silph_yellow.py CLONES) |
| 555 / 556 / 557 | Mt. Moon 1F / B1F / B2F | verified (live) |
| 558 / 559 | Rock Tunnel 1F / B1F | verified (live) |
| 560-563 | Rocket Hideout B1F-B4F | verified (floor_model_check.py regenerates each floor's stored model with the Hideout builder's constants; live warp tests) |
| 564-574 | Silph Co. 1F-11F | verified (floor_model_check.py + live warp tests) |
| 575-578 | Pokemon Mansion 1F, 2F, 3F, B1F | verified (mansion_yellow.py, floor_model_check.py, live warp tests) |
| 579 | Viridian Gym | verified |
| 580 / 581 / 582 | Victory Road 1F / 2F / 3F (floor f = 579 + f) | verified (live) |
| 583-586 | Safari Zone Center, East, North, West | verified (13 zone-to-zone warps walked live on ROM 0151; the south exit lands in Fuchsia) |
Cave floors are all `cave_floor.install` builds: OX,OZ = (8,12) for 20x18-block floors; Mt. Moon B1F is (4,4). Yellow step (x,y) = 2x2 tiles at (OX+2x, OZ+2y). Warp = 2x2 block, behaviour byte 110, one warp event per tile (cave_ladders.py).

## Native maps the project reuses
Route 3 = 11, Route 4 = 12, Route 10 north (Center side) = 18, Route 10 south (Lavender side) = 388, Cerulean City = 52, Route 23 gate = 299, Indigo Plateau = 58, Viridian Forest = 147 (gates 419 / 420), Route 2 north = 414, Fuchsia Warden house = 481, Seafoam gym = 146, old Silph lobby = 402.
Old stand-ins: Mt. Moon 107 / 448, Rock Tunnel 108 / 452, Victory Road 124 / 178 / 179.
Johto Union Room = header 2 (link-only; reached only from map 81 at (7,2); the one NULL read the Johto sweep found, benign).

## Header record (24 bytes at ARM9 0x020F6BE0 + 24*id; extension records via map_header_extension.records)
byte 0 wild table, 1 area, 4-5 matrix, 6-7 script bank, 16-17 event file, 18 mapsec (name row, text bank 279), 20 bit0 = Kanto flag.
Kanto-flagged headers: 234 (222 with warps); Johto: 302 with warps.

## NARC files (a/0/...)
1/2 script banks, 2/7 texts, 3/2 events, 3/7 wild tables, 4/0 building models (343), 4/1 matrices, 4/2 areas (field 0 = building set id, field 2 = map texture bank id), 4/3 area building sets (u16 count then model ids),
4/4 texture banks, 6/5 land chunks (perm 2048 B, 48-byte building entries, model, bdhc). Building ids: 69 dun_stairup, 70 dun_stairdw (cave ladders), 66 / 67 d15_stairup / d15_stairdw, 124 ele_door_dun (elevator door), 177 warp_j01 (warp pad, native maps 339 / 402), doors 13-16...
Tile behaviours used: 110 = warp from any direction, 101 = down only, 107 = left only, 8 + flag 0x0a = plain cave floor that rolls wild encounters.

## RAM / ARM9 facts
Player position u16 at 0x021DA6F6 (x) and 0x021DA6FE (z); overlay 129 always resident (0x23D8000-0x23DFFF0); NULL guard stub for the Cerulean crash at 0x23DEBE8, patched site 0x0202407E (tools/null_guard.py). Route 2 north crash site 0x02050650 / caller 0x020402F0 (3DS only, no emulator NULL).

## ROM chain (build/NNNN-name/, copies in /mnt/c/RetroArch-Win64/downloads/)
0145 null guard (3DS-verified) -> 0150 single-tile warps + art for all caves and facilities, built straight from 0145 by tools/warp_tiles.py (0146-0149 were earlier, superseded steps of the same work).

## For the two custom PKHeX repos (Met Location / location ids and other custom ids)
PKHeX's Met Location is the header's mapsec byte (record byte 18, row in text bank 279), NOT the header id. Mapsec of the extension maps, read from the ROM 0148 header records:
Tower 540-546 = 70; old Hideout clones 547-550 = 213; old Silph clones 551-554 = 148; Mt. Moon 555-557 = 198; Rock Tunnel 558-559 = 200; Hideout 560-563 = 213; Silph 564-574 = 148; Mansion 575-578 = 213; Viridian Gym 579 = 139; Victory Road 580-582 = 221; Safari 583-586 = 213.
Looks wrong, to check against text bank 279 before relying on it: Mansion and Safari share Hideout's 213 (cloned template value), so their area names / Met Locations may read "Rocket" something. Native references seen: Union Cave-type 197-198, Rock Tunnel stand-ins 200, Cerulean-area caves 203, Victory Road stand-ins 221.
Custom ids seen in builders/notes (verify in source before use): items Lift Key 878, Secret Key 872; species above the vanilla limit start at 1534 (starters Psyduck 1563 and the species 1561; TM/HM compat literal moved 1534 -> 1582 in overlay 129 at 0x23DB208).
Flags/variables already allocated (never reuse): persistent flags must stay below 0xAA0; used A7D, A7F, A87, A9D, A9E, A9F, Mega 0x9D6, Victory Road barriers 0x956-0x959, Mt. Moon ball TM12 0xB36; variables: bedroom PC 0x4152-0x4165, Mt. Moon stage/choice 0x4140/0x4141, Victory Road dummy 0x4179.

## Actors, trainers, NPCs
data/ids-actors.md (generated by tools/id_dump.py from the newest ROM; re-run after every build, do not edit by hand) lists, for every extension map 540-586, each actor's object id, sprite, flag, script id, tile, facing and trainer id.
Rules: script 1..N = the map's own bank, 3000+ = shared trainer scripts (trainer id = script - 2999), 10000+ = common scripts (10001 = Rock Smash rock sprite 85, 10002 = Strength boulder sprite 84 after vr_boulder_fix). Trainer defeat flag = 0x550 + id (must stay < 0xAA0, so ids < 1360); hand-added trainers need trainer_alloc.add (ids >= 1030 otherwise do not battle).
Known trainer id blocks (from the dump): Mt. Moon 1F 766-772 (7 trainers; Yellow's B1F has none, B2F has 4 Rockets/fossil Super Nerd); Pokemon Tower floors 842-845 and neighbours. Item balls = sprite 87 with the pickup's flag (Mt. Moon 0xB2C-0xB30, TM12 0xB36). Trainer names are blank in text 729 for these ids (class only).
