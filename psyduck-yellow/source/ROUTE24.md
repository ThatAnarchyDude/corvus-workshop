# Prototype 0023: Route 24 and Nugget Bridge

Cumulative from 0022; older patch pages remain unchanged. HeartGold's map,
bridge geometry and collision data are retained. Johto is unchanged.

The five contest trainers use Yellow's original teams, levels and moves:
Bug Catcher (Caterpie/Weedle 14), Lass (Pidgey/Nidoran female 14), Youngster
(Rattata/Ekans/Zubat 14), Lass (Pidgey/Nidoran female 16), and Camper (Mankey 18).
The optional grass Camper has Rattata/Ekans 14. The disguised recruiter gives
one Nugget after five wins, then battles with Ekans/Zubat 15. A full Bag does
not consume the reward; losing the Rocket battle permits a retry without a
second Nugget.

Damian offers one level-10 Charmander. Make room in the party before accepting:
this uses HeartGold's native party gift operation, rather than Yellow's
full-party transfer to PC storage. Declining or a full party retains the gift.
The ground ball gives reusable TM45 Thunder Wave (spare item ID 122), with
Yellow compatibility for Generation I and HeartGold Thunder Wave compatibility
for later species. It uses the normal TM pocket; native TM73 remains intact.
The ball stays solid until collected and requires A-button interaction.

Grass uses Yellow's ten encounter slots mapped to HeartGold's twelve-slot
weights, identically for morning/day/night. Species and levels: Oddish and
Bellsprout 12/14, Pidgey 13/15/17, Venonat 13/16, Pidgeotto 17. Surfing and
fishing are not part of this checkpoint's encounter conversion.

Blue's Cerulean approach now covers all five bridge lanes. His actor stands
at the bridge deck's height and visibly approaches before battling; his saved
starter and rare properties carry forward. An old normal save refreshes only
the changed Cerulean Blue and Route 24 actors once. Party data, inventory,
parcel progress and National Pokédex records retain the native save layout.

Persistent flags A8D–A92 are below HeartGold's daily-reset range AA0–AFF and
below its B60 save boundary. Native trainer flags for IDs 787–793 are also in
bounds. Script banks and old trainer records remain archived and unchanged.

## Testing

Use the normal Continue screen and back up the save before changing versions.
Emulator save states belong to the exact ROM that created them. See
`validation-prototype-0023.json` for completed checks and their limits.
Private staging transports, trainer-flag grants and test Pokemon are never
included in the published prototype. A test warp into the bridge's center can
place a character below its elevated deck; normal testing approaches from
Cerulean instead.

Next: Route 25 and Bill, then the returning robbed-house/Dig event in separate
checkpoints. The broader dialogue review awaits the owner's correction list.

This cumulative checkpoint also includes [the Mt. Moon corrections](MTMOON-CORRECTIONS.md) requested during testing.
