# Pokémon Psyduck Yellow — parcel prototype 007

Mom stops you before leaving Pallet, walks over from your house, explains that you left your Running Shoes under the bed, and gives you a Running Shoes key item. HeartGold’s running controls unlock immediately. Route 1 then continues north to Viridian. Its Yellow-style NPCs and low-level Pidgey/Rattata encounters remain.

Upon entering Viridian from the south, a cashier walks over from the Mart. After greeting you outside, they escort you along the streets and through the Mart doorway. Inside, they explain Oak’s order and ask you to deliver it because you came from Pallet. You receive Oak’s Parcel and return to Oak’s lab. Oak accepts the parcel, Blue arrives, and Oak gives you the **National Pokédex**. Starter selection no longer gives a Pokédex. Speak to Oak again afterward for five Poké Balls, as in Yellow.

Viridian’s Pokémon Center retains native healing and Pokémon storage. Its Player PC menu also includes the same item storage used in your bedroom, alongside native personal services. The evolution supplies and custom item evolution methods from prototype 006 remain. Only this Center’s copy of the PC script changes; Johto PCs and the original common script remain untouched.

Route 2 and Route 22 remain blocked for this test. Other unadapted buildings remain guarded. The original HeartGold Kanto script/event members are preserved for later relocation. Johto remains unchanged.

## Download and saves

Open the browser downloader, choose the **original unmodified USA HeartGold .nds**, select **Create my playable NDS**, and download **Pokemon-Psyduck-Yellow-prototype-007.nds**. The page builds the playable file locally; the original file stays on your device. Public files contain a patch and browser decoder, with no full ROM or emulator save.

Back up your normal save before importing or renaming it for the new ROM. Earlier prototype normal saves use the same save format. Prototype 007 initializes its quest state once; existing caught/seen records remain, while Pokédex access waits for parcel delivery. Emulator save states must not be carried between builds. A new game is recommended for testing the complete opening; an imported post-starter save can test the new quest directly.

## Android playtest checklist

1. Choose a starter and finish the lab rival battle. Check that the follower appears immediately and that no Pokédex is granted yet.
2. Head north from Pallet. Check Mom’s walk, dialogue, Running Shoes item and running controls. Confirm that returning home does not repeat the gift.
3. Follow Route 1 into Viridian. Check the cashier’s approach, outside greeting, walking escort, door entry and inside explanation. Confirm that Oak’s Parcel is in Key Items and the Pokédex remains unavailable.
4. Save normally with the parcel, restart the emulator, and continue. Confirm that the parcel and shoes remain and the cashier does not repeat the outside escort.
5. Test the Center’s nurse, Pokémon storage and Player PC item storage. Existing bedroom quantities should be shared, rather than duplicated.
6. Return the parcel to Oak. Check Blue’s entrance/exit, original Yellow dialogue, parcel removal and National Pokédex grant. Previously seen/caught species should remain recorded.
7. Speak to Oak again for five Poké Balls, save normally, and reload. Check that the Dex remains available and neither the parcel scene nor gifts repeat.

## Rebuild and evidence

See [BUILDING.md](BUILDING.md) for commands and `releases/prototype-007/validation.json` for exact hashes and completed checks. Generated ROMs, saves, screenshots, patches and emulator fixtures stay ignored under `build/`.

## Verification — October 9, 2026

82 local tests passed without skips. They execute the compiled quest scripts and Thumb Dex gate, including missing parcels, repeated interactions, full-bag retries, one-time migration, retained records and native fallback arguments/registers. The Center override is checked against the actual PC metatile; the town-map board remains unchanged.

DeSmuME completed the shoes and parcel loop, with the outside cashier greeting, visible escort, inside explanation, Blue’s return and National Dex grant. The parcel and shoes survived a normal save/reload before delivery. A genuine prototype-006 save made outdoors in Pallet imported correctly, created the new Mom actor, and completed her walk and gift. The Center’s native nurse, Pokémon box UI and shared item-storage withdrawal were exercised. Live RAM confirmed parcel removal, retained seen/caught species and five Poké Balls on the next Oak interaction. A normal save/reload after delivery preserved the National Dex, completed quest, gifts and PC withdrawal.

xdelta decoding reproduced the exact output. The phone-width Chromium downloader rejected a wrong input and downloaded the verified output without browser errors. The original title/evolution archives, ARM7 and overlay table remain identical to prototype 006; old script/event members are preserved.

No Android run, listening test or full fresh-game opening playthrough was performed here. Emulator checks used imported normal saves and the normal 1040 Pallet / 1036 Viridian approaches; alternative approaches have compiled-script checks. Running Shoes currently use an unused generic key-item icon. Public hosting is verified through Git publication; external page loading is not tested from this environment.
