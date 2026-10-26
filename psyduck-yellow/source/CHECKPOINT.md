# CHECKPOINT (2026-10-27, session 007 continued)
Newest ROM: downloads/Pokemon-Psyduck-Yellow-0105-dex-fix.nds (= build/0105-dex-fix/dx.nds, chain base; sha 642014a6fed6). Chain: ...safari_yellow -> dex_lang_fix.py.
Finished: POKEDEX PASS. Static audit (tools/dex_audit.py, all 1,026 entries): list is a permutation, all name/category/entry/height/weight rows present and non-blank.
Live (tools/dex_live.py style, fixture_party.py FIXTURE_EXTRA + ds_tap.py x/start keys): Gen1-9 and Novareon 1026 open with correct text, types, HT/WT, AREA/SIZE/FORMS pages.
BUG FOUND + FIXED: registering any species id >= 700 (Gen 6, early Gen 7, incl. Sylveon) overwrote the SEEN bytes of low species (language array overran the seen array). dex_lang_fix.py skips the language write for ids >= 700.
Verified after fix: Chespin 650, Sylveon 700, Rowlet 722, Grookey 810 register at their own entries.
Minor, not fixed: Pecharunt/Victini/Melmetal forms page shows the species name twice (cosmetic); footprints identical to blank for 8 old species (13,16,123,124,409,423,424,477) and size data a/2/2/1 blank for Gen 9 ids 1023-1075 (SIZE page still renders).
Not done: elevator menus, texture polish, Safari/Mansion hand tests, ~40 no-warp outdoor maps, PKHeX work.
Deleted this session (mine): 0104 ROM, build/0094, scratch fixtures; owner approved deleting private/hg-engine-0037-v1 (no engine source on disk now; re-clone BluRosie/hg-engine if ever needed).
