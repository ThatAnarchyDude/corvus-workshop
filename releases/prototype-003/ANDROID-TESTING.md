# Pallet and first Route 1 grass test — prototype 003

Rebuild Prototype 003 locally from your own matching, legally obtained US HeartGold ROM or apply the `.xdelta` found in `yellow-heartgold-prototype-003-android-patch.zip` to the untouched original. Open the resulting `.nds` file in a Nintendo DS emulator such as melonDS. Complete modified `.nds.zip` ROM archives have been removed from the GitHub branch contents. See `yellow-heartgold/BUILDING.md` for reproducible commands and required hashes. Keep older builds and their saves separate. Start a NEW GAME; do not load a prototype 001/002 save or save state. The original HeartGold title screen remains for now.

Name your Kanto rival during Oak's introduction, after naming your player. Rejecting the name at confirmation reopens the naming screen. The chosen rival name is used in lab dialogue and battle messages. HeartGold's separate Johto rival is reserved for later and will use the default name Silver, without a second naming sequence.

Leave the Pallet bedroom via the northeast stairs, go downstairs and leave the house. Try walking north toward Route 1. Oak stops you and takes you to his lab. Speak to him and choose a level-5 Pikachu, Eevee or Togepi. Your partner follows immediately, and the National Pokédex is granted at starter receipt. Moving that grant to Yellow's parcel-return event remains deferred.

Your rival picks his starter after yours: Eevee against Pikachu, Togepi against Eevee, or Pikachu against Togepi. Walk toward the lab door; he stops you for a level-5 battle. You may continue whether you win or lose. Both outcomes have separate Yellow dialogue, heal your party, and send the rival out of the lab. Re-entering the lab must not repeat the battle. Oak heals your party when spoken to again.

The accessible Route 1 grass uses Yellow's Pidgey/Rattata encounters and original weighted species/level probabilities (levels 2–7), applied at every time of day. The route has no trainer battles. Yellow's Potion sample NPC is near the entrance; the second NPC's ledge explanation is farther north, beyond this test's boundary. The northward path is blocked at the first grass path so you cannot reach the unadapted later route or Viridian.

Test Oak's stop, each starter/follower/Dex branch, the rival's starter and exit challenge, both battle outcomes, the Potion NPC, wild encounters and the northward barrier. Use the normal in-game Save, restart the emulator, and choose Continue. Report which starter you chose and where any problem occurred.

Original HeartGold Kanto event assets, including the removed Route 1 trainers, remain intact in their original archive entries for later adaptation into Johto's postgame. These opening events use appended assets instead.

Known limits: Oak's escort currently uses a transition to the lab; Yellow's full wild-Pikachu capture scene is not implemented. Blue has his HG overworld sprite, but naming and battle portraits retain HG's rival presentation. Gift dialogue adapts Yellow's forced Eevee theft to the requested three-starter chronology. This is a bounded opening test; the later Yellow campaign, gym balancing, all-species acquisition paths, Johto postgame and new title screen remain unfinished. This version has not been tested on a physical Android phone.

The patch ZIP is an alternative: apply its `.xdelta` to the untouched US HeartGold ROM, not to another prototype. Exact input/output checksums and verification results are in `build-report.json` and `validation.json`.

Original HeartGold SHA-256: `65f02a56842b75aa92d775d56d657a56fe3fa993550b04dc20704ab82d760105`.

Prototype 003 output SHA-256: `1cd5dd980e9c9a542783fe261e5b4b9c59df7b1061e1be2d97f6fa2dd9e635db`.

## Additional user-reported testing

The project owner reports testing **Prototype 003 with melonDS DS on PC and Android**, with functionality working as intended so far. This is a user report, separate from the recorded DeSmuME automation/screenshots, and is not a claim that every feature and save-state edge case has been verified on both devices.

Citra emulates **Nintendo 3DS** software and does not serve as a Nintendo DS ROM test environment. A real 3DS/2DS can run most DS cartridges using hardware backward compatibility, but that does not make `.nds` files directly playable in Citra. Use melonDS or another compatible DS emulator for this project.
