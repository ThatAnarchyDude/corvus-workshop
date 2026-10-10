# Opening progression plan

Global base shiny odds are 1/4,096, or 1/2,048 with the passive Shiny Charm supplied through the bedroom PC. Perfect Legendary IVs apply only to the 17 existing Yellow/HGSS encounter species listed in the release notes.

Prototype 013 responds to the prototype 012 playtest with safe League/Johto gates, Yellow’s early Route 22 rival levels with Blue’s chosen lab starter, including a persistent 50/50 Psyduck/Eevee choice of opposite gender for Togepi players and matching player shiny/perfect-IV odds and walking scene, exact level-6 lab experience, automatic Oak Poké Balls, corrected Daisy/Trainer House dialogue and readable long messages. See [PROTOTYPE-013.md](PROTOTYPE-013.md).

Prototype 014 implements Yellow’s zero-badge Route 2 and Viridian Forest progression. Prototype 015 is the Pewter gym checkpoint: Yellow gym teams and moves, Boulder Badge, native single-use Bide TM, outdoor NPCs and walking guides, and Water/Psychic Golduck. Pewter's optional interiors remain to be converted before the town is considered complete; then proceed with Route 3 and Mt. Moon. Blue's Eevee evolution decision is now resolved below; Psyduck/Togepi evolve normally. Add the separate late Route 22 encounter when campaign progression reaches the League. Keep HeartGold’s shop progression and Johto intact. Original HG Kanto events remain preserved for later Johto relocation.

Testing policy (owner, 2026-10-10): continue town/route implementation with incremental desktop DS emulator checks. Do not wait for owner Android testing between prototypes. Keep source/release checkpoints and normal-save compatibility evidence; reserve Android compatibility testing for the completed game. A checkpoint is not a finished campaign release.

## Campaign continuation and publication authorization

Maintain the living public log at `psyduck-yellow/DEVELOPMENT-LOG.md`, published
on `main` at https://github.com/ThatAnarchyDude/corvus-workshop/blob/main/psyduck-yellow/DEVELOPMENT-LOG.md.
Update the same page after meaningful development changes and each published
checkpoint. Include each checkpoint’s publication date and AM/PM time in
America/New_York (Eastern Time), after its successful push, and mark unpublished
checkpoints accordingly. Do not substitute build times for confirmed future
publication times. Clearly distinguish released features, unpublished work and plans;
keep the URL stable and preserve Git history. Log publication is authorized by
the owner and does not require publishing an unfinished prototype.

The owner authorizes continued implementation through Giovanni's eighth Kanto badge without waiting for their playtests. Publish a separate patch checkpoint after each completed area passes the available checks, and provide its download link in the conversation. Preserve every published version; do not overwrite a patch without the owner's explicit instruction. Apply later playtest feedback to the shared implementation so subsequent versions include the fixes.

Each checkpoint is cumulative: build on the preceding prototype, retaining its features and fixes while adding the next area. The downloadable patch still targets the original unmodified USA HeartGold ROM; players do not need to apply a chain of earlier patches. Use separate version directories and immutable commit links for publication.

Retain HeartGold's maps, but remove inherited Cut trees, Rock Smash rocks, Strength boulders and similar terrain gates in Kanto. Leave Johto's terrain untouched. Do not add further terrain obstacles unless requested in playtest feedback. Map changes are necessary only when an asset required for the agreed goals, such as a gym, is missing. Yellow's story events that gate progression must still be implemented. The owner explicitly confirmed that the two previously requested Viridian Cut trees remain in place.

Johto's terrain remains entirely unchanged while Kanto is being completed. Only previously agreed Johto changes, including trainer/gym scaling, are in scope; do not redesign its maps or terrain as part of the Kanto conversion.

Use the established design for routine decisions. Ask the owner when a faithful implementation cannot be achieved or an unresolved reserved decision is reached. Distribute patches and browser-based local ROM reconstruction only; do not publish ROM files.

## Item improvements — owner decisions for prototype 016

Prioritize easy, less complex work first (owner, 2026-10-10). Finish Pewter's
simple event and reward fixes before the bulk-use interface and larger systems.

Make all TMs reusable. Add a shop-style Rare Candy quantity selector with normal
move learning/evolution for each candy and exact consumption. At level 100, a
Rare Candy may trigger an eligible level-up evolution while leaving level and
experience unchanged; preserve B cancellation and consume nothing if ineligible.
Stone evolutions also remain usable at level 100.

Psyduck must evolve into Golduck only with a Moon Stone. Remove its original
level-33 evolution and the prototype-006 Water Stone shortcut. This supersedes
the earlier instruction to retain Psyduck's ordinary evolution methods. Other
species retain their existing methods; Golduck stays Water/Psychic. These changes
are unpublished until the next checkpoint is released. See ITEM-QUALITY-OF-LIFE.md
for implementation and remaining quantity-selector work.

## Blue's Eevee evolution — owner decision

When later rival battles call for an evolved starter, Blue's Eevee becomes Jolteon (species 135) if the player's originally selected starter was Togepi (species 175), and Umbreon (species 197) if the player's originally selected starter was Psyduck (species 54). Use the saved original starter selection, even after the player evolves or stores that Pokémon. The Togepi branch still gives Blue a persistent random Psyduck/Eevee choice; this evolution rule applies only when he picked Eevee. Preserve the existing opposite-gender rule and saved starter properties. Early battles keep Eevee unevolved; this decision does not modify published prototype 014.

Typing note: in Generation IV, Jolteon's Electric attacks are super effective against Togetic and Togekiss (Normal/Flying). Umbreon's Dark attacks are neutral against Psyduck (Water) but super effective against the owner's Water/Psychic Golduck described below.

## Golduck typing and later move changes — owner decision

Prototype 015 makes Golduck Water/Psychic. Psyduck remains Water. `tools/pewter_progression.py` applies `tools/species_changes.py`; the species personal-data edit applies to player, rival and wild Golduck and is also read for existing Golduck in ordinary saves. Published prototype 014 remains unchanged.

Keep Golduck's current moves, learnset and other attributes for now. Revisit its moves after the Kanto portion is complete, as explicitly requested by the owner.

### Prototype 0016 verification checkpoint

Pewter's houses, Mart, Center and two-floor museum are converted. Custom miniature exhibit models remain deferred; the museum uses native HeartGold displays with Yellow dialogue. The final build (SHA-256 `05ed484e1ddff00944063733031e2e3b4921c1e9cf145d58252fbd0c7b342242`) passed 212 automated tests. Its museum loads both floors, returns downstairs, and grants exactly one Old Amber with repeat dialogue in the DS emulator. The browser downloader reproduces this ROM with the four-digit filename and rejects incorrect input. The earlier slow Old Amber attempt was resolved by stepping through the complete dialogue; final checks passed. Route 3 is the next campaign area. Bulk Rare Candy selection is still unfinished and explicitly deferred while simpler campaign work continues.

New checkpoint names use at least four digits (`0016`, `0017`, etc.). Preserve old published URLs/files; do not republish or rename historical artifacts merely for padding. Prototype 016 is now named 0016.
