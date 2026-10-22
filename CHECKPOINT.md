# CHECKPOINT (campaign-loop)

Newest ROM: /mnt/c/RetroArch-Win64/downloads/Pokemon-Psyduck-Yellow-0041-engine-map-extension.nds
  (source: yellow-heartgold/build/0041-map-extension-v1/, built from 0040; SHA starts 2ab4c748)
Area just finished: ENGINE — map header table extension (tools/map_header_extension.py). ROM-only, stock-emulator safe.
  Header ID check (ARM9 0x3B268) -> trampoline; IDs >= 540 read 24-byte records appended to resident hg-engine ov129
  (capacity 305 new maps). No Johto/hg-engine data moved. No gameplay change yet.
Test: boot, Continue from the 0040 fixture save, bedroom + menu OK (fixture only, not campaign proof). ID>=540 is only
  RAM-verified (records+trampoline present after boot); first live warp comes with the Tower.
Known gaps: Pokemon Tower floors, Marowak ghost, Mr. Fuji, Silph Scope (all not built); no new-map warp tested yet.
Next: Lavender/Pokemon Tower using install() -> floors cloned from Sprout/Burned/Bell Tower layouts, new event/script/text banks.
