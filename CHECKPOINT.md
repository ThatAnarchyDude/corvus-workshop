# CHECKPOINT (campaign-loop)

## Area: Lavender / Pokemon Tower / Silph Scope — NOT BUILT (no new ROM; latest stable is still 0040)
Date: 2026-10-22. Owner decision: host Tower floors by cloning Sprout/Burned/Bell(Tin) Tower layouts.
Findings:
- Map header table (ARM9 0xF6BE0, 24 B/rec) holds only 540 records; records after 539 are other data, so NEW map IDs cannot be added without relocating it (hg-engine internals, forbidden). Floors must reuse existing IDs.
- Warp-unreferenced IDs (candidates, still need a script-warp scan): Mystery Zone 0,1,3,4,5,516; Battle Tower 266-271,274 (likely script-warped, risky); Embedded Tower 524-526 (1 ref each).
- Clone sources: Sprout Tower 110/155/156, Burned Tower 7/217, Bell Tower 332-341.
- No driver chains tools/route10_progression.py / rock_tunnel_progression.py (patch(rom, refs) functions only); a new driver is needed.
Next: scan script banks for Warp targets to confirm 7 free IDs, write tools/pokemon_tower.py + driver from the 0040 ROM, then Fuji/Marowak scripts, Silph Scope (Rocket Hideout, same host problem).
Known gaps: everything above; no tests run.
