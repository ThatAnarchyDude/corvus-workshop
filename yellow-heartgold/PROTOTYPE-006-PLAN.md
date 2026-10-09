# Prototype 006 — evolution testing

Status: planned; begin implementation only after the user verifies prototype 005 on their device.

Add evolution items to the shared player's PC item storage so they can be withdrawn from the bedroom PC for testing. Keep the existing Potion and Rare Candy supplies. Use 95 of each evolution item unless the user requests another amount; verify storage capacity and compatibility with existing saves.

| Item | Requested evolution |
| --- | --- |
| Thunder Stone | Eevee → Jolteon |
| Water Stone | Eevee → Vaporeon; Psyduck → Golduck |
| Fire Stone | Eevee → Flareon |
| Dawn Stone | Eevee → Espeon; Togepi → Togetic |
| Dusk Stone | Eevee → Umbreon |
| NeverMeltIce | Eevee → Glaceon |
| Leaf Stone | Eevee → Leafeon |

“Together” in the request is interpreted as Togepi. HeartGold already contains Dawn and Dusk Stones, but not Ice Stone, so use the requested NeverMeltIce fallback. These are intentional custom evolution methods, including Water Stone for Psyduck. Preserve the existing level, friendship, time and location evolution methods alongside the new options where the engine permits. Preserve existing unrelated uses of these items.

Verify each item can be withdrawn, targets the correct species, evolves to the correct result and is consumed appropriately. Check unsupported targets, full bags, normal-save compatibility and the previously working opening. Publish a patch-only playtest builder after validation; keep all ROMs out of Git and public hosting.
