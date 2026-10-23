# Checkpoint (2026-10-23)
Newest ROM: downloads/Pokemon-Psyduck-Yellow-0056-dex-kanto.nds (build/0056-dex-kanto-v1/dexkanto.nds), chain on 0053 gleam.
Area: Pokedex numbers + Kanto-first Pokedex.
- Starters/forms register as their base species and show national numbers (tools/dex_fix.py).
- Regional list = Kanto 1-151; Pokedex opens on Kanto; Johto/rest only in National mode (tools/dex_kanto.py).
- Title says KANTO POKeDEX, switch label says KANTO (tools/dex_labels.py).
Test: New Game, get Pokedex, open it: title/label/toggle; check a starter's Summary Dex No.
Known gaps: Novareon registers as Umbreon; Oak/Johto completion texts unchanged; other "Johto" strings in search page unchecked.
Next: continue Kanto campaign order; owner playtest feedback.
