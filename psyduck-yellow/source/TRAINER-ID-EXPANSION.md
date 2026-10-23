# Trainer ID expansion (investigated 2026-10-22, NOT implemented: no necessary trainer needs it)

- The 1000 cap is only an assert in tools (TrainerBook.new, route6_trainers.patch). The engine accepts script ids 3000..4999 (trainer id = script - 3000 + 1; 5000+ is double-battle partners). Scratch experiment: trainer id 1003 (flag 0x93B) with filler records for ids 997-1002 starts its battle normally.
- Real limit: defeat flag = 0x550 + id must be a persistent flag (< 0xAA0), unused by the game. Ids 741-996 (flags 0x835-0x934) are verified clear in the decomp.
- Strict safe pool (decomp-unreferenced by name, outside indexed blocks 0x96B-0x96D, 0x97B-0x98B, 0x988-0x991, 0x9B0-0x9D5, no byte hit in the vanilla or current ROM): 28 flags -> trainer ids
  1003, 1024, 1036, 1112, 1160, 1183, 1184, 1187, 1189, 1193, 1196, 1197, 1231, 1232, 1235, 1236, 1237, 1239, 1245, 1247, 1248, 1249, 1252, 1253, 1257, 1263, 1267, 1268.
  (Up to ~92 if the current-ROM byte hits are judged coincidental.) hg-engine's own flag use is not visible from the decomp, so this is static evidence only.
- To use an id: skipped ids need filler records (copy of an existing row, empty party), then call tower_scenes._cover_common(rom, last_id) so the common trainer script covers it; relax the `tid < 1000` asserts to "flag in pool".
- Policy (owner, 2026-10-22): only add a trainer if it is necessary (cannot be avoided on first pass). Gym extras, route/sea optional trainers and similar are not.
