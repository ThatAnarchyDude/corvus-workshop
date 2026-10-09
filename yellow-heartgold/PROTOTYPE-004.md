# Pikachu Yellow: Prototype 004 engineering brief

**Starting point:** the owner-tested Prototype 003 on branch `android-prototype-003`. Stage subsequent changes only on `pikachu-yellow-development`.

**Playable target:** a continuous loop from Pallet Town across Route 1 to **Viridian City**, receive Professor Oak's Parcel at the Poké Mart, and return to Oak in Pallet Town. Route 2, Viridian Forest, and the first gym remain locked until this bounded slice passes testing.

## Protect what already works

- Preserve the recorded Prototype 003 checksum as the baseline and keep a separately reconstructed local copy.
- No changes to starter choices (Pikachu, Eevee, Togepi), first rival branches, intro naming, immediate following Pokémon, or the lab battle.
- Keep the agreed early National Pokédex gift. **Do not grant a second Pokédex** on parcel return. Relocating the Dex grant to the parcel event is explicitly deferred.
- Original HeartGold Kanto scripts and event data remain intact for later Johto postgame. Use appended assets for Yellow-era changes.
- Keep produced ROM images and emulator saves in ignored local build folders.

## Implementation sequence

1. **Audit before editing.** Identify verified HeartGold US revision 0 map headers, scripts, text banks, warps, flags, events, and encounter references for Route 1 and Viridian. Compare original Yellow story and map behavior against the disassembly. Record actual IDs; don't guess offsets.
2. **Route 1 traversal.** Remove the temporary northern guard only after both neighboring maps are ready. Preserve Yellow encounters, one-time Potion NPC, and no unintended HG-era trainer battles.
3. **Viridian City.** Adapt exits, Pokémon Center, Poké Mart, NPCs, and field events. Gate unfinished routes and confirm following-Pokémon map transitions.
4. **Parcel sequence.** First Poké Mart visit grants Oak's Parcel exactly once; Oak accepts it exactly once upon return, using persistent event flags and dialogue adapted for our already-granted Dex.
5. **Return travel.** Verify backtracking to Pallet, heals, reentry to lab and houses, save/Continue, and blackout behavior without softlocks.
6. **Reproducible release.** Record input/output hashes, preservation assertions, patch roundtrip, emulator evidence, and a patch-only delivery. Never distribute a complete ROM.

## Mandatory acceptance tests

- All three starters can reach Viridian with expected party/follower behavior.
- Initial rival battle and chosen name persist across travel and save/reload.
- Route 1 Potion NPC does not duplicate its gift.
- Viridian Poké Mart grants one parcel; repeat visits do not grant another.
- Oak accepts the parcel once, without repeating the starter or National Dex gift.
- Viridian Pokémon Center heals; Save and Continue preserve story progression.
- No original unadapted story events activate. All open exits are traversable or safely guarded.
- Record PC emulator evidence separately from **owner-reported** melonDS Android tests. Untested behavior remains labeled untested.

## Deliberately outside scope

Viridian Forest, Brock, gyms, full Yellow Pikachu capture scene, replacement title, complete 493-species acquisition, and Johto postgame.

## Repository hygiene

Check tracked files and ZIP archives before each push. The repository's root GitHub Actions workflow runs this check automatically.

Removing complete ROM archives from current branch contents does **not** erase their presence in previous Git history. Historical removal requires a separate planned migration; private/public visibility alone does not authorize uploading copyrighted ROMs.
