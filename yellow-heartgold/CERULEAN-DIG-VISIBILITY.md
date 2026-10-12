# Prototype 0025: Cerulean’s stolen Dig TM and visible bridge trainers

This checkpoint builds on 0024. Earlier patches remain available separately.

Nugget Bridge’s first three trainers now appear while the player is still on
the Cerulean side of the bridge. Previously, they did not exist in the active
actor list until the player entered Route 24, making them appear suddenly.
HeartGold’s native neighboring-map NPC aliases keep the same actors visible
across that boundary. A refresh adds missing aliases to older normal saves;
it does not delete and recreate already-present bridge trainers. Visual
aliases cannot start a battle using their sentinel script number. Real
trainers retain their ordinary sight, approach, battle and defeat behavior.

The board west of the southern bridge entrance now reads “ROUTE 24”,
“NUGGET BRIDGE”, and “Five trainers await your challenge!” when you press A.
The retained standalone boards in Routes 3, 4 and 25 were also checked against
their existing interaction positions. This is not a claim that every sign in
the unfinished campaign has been converted.

Bill’s left-wall PC interaction now has a visible HeartGold computer terminal
with a monitor and controls, rather than relying on the room’s decorative
books. It is solid. The separation machine, ticket reward and later Pokémon
collection menu keep their existing scripts. Its placement recalls Yellow’s
computer while using HeartGold’s graphics.

After helping Bill, the police officer leaves the robbed-house entrance.
Enter the house and use the new jagged passage in its back wall. Outside,
the Rocket automatically stops adjacent approaches or can be spoken to.
He uses Yellow’s Machop and Drowzee, both level 17. Winning returns one
reusable TM28 Dig; he then walks along the northern yard and leaves. If the
TM pocket is full, he stays for a reward retry without another battle. Losing
does not mark the event complete. The rear entrance cannot bypass Bill’s
earlier story gate. Normal saving preserves the completed event and reward.

The passage is the only new room geometry here. The original front door,
furniture, outdoor terrain, Johto headers and earlier trainer records stay
unchanged. Original event/script/land archive members are retained.

## Validation

The 31 focused and regression checks cover map ownership, old actor snapshots,
native trainer sight classification, reward loss/full-pocket/repeat paths,
daily flag rollover, archive preservation, previous rewards, Trainer Card,
friendship storage and earlier TM lookups. Native DeSmuME runs also checked
the bridge from both directions, an older Continue save, the board’s full
text, Bill’s computer and machine, the Rocket battle and reward, both rear
house transitions, and normal Save/Continue with Dig retained and the Rocket
gone. The browser patcher reconstructs the expected ROM from the original
USA HeartGold file and rejects a previous prototype as its input.

These are focused checks using private prepared saves, including a Golduck
starting at level 21 and a private test Pikachu. They do not establish normal
campaign difficulty or exhaustive rendering coverage across every area.
Private transports, Pokémon grants, saves and raw RAM are excluded from the
published patch. The owner’s Android movement-freeze report remains parked;
its cause has not been established.

Audio recordings use the game’s sound. The recorder aligns small emulator
audio/video clock differences while preserving audio pitch, records that
adjustment in its JSON log, and rejects discrepancies over one percent.
Previous recordings are preserved.

See [validation-prototype-0025.json](validation-prototype-0025.json) for the
artifact hashes and observed checks. Route 5 is the next campaign checkpoint.
