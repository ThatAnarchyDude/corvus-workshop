# Prototype 0022: normal saves and testing friendship

Two problems affected earlier checkpoints. Our custom quest/reward flags were
inside HeartGold's daily-reset range. A new calendar day could erase their
completion markers, causing Oak's Parcel to initialize again and Brock to offer
Bide again. Prototype 0021 also allocated Cerulean flags beyond the native saved
flag array, where writes could affect adjacent checksum bytes. Earlier tests
missed both boundaries.

0022 preserves the older custom flag addresses and their saved data while
excluding that reserved extension from daily clearing. HeartGold's used daily
flags still reset normally. Cerulean's new flags move to an unused persistent
range. Build-time checks reject future overflow, and the native flag function
rejects invalid persistent addresses instead of writing past the array.

On first use, recovery examines retained parcel state, Pokégear ownership and
Kanto badges. Evidence of completed early progression restores Pokédex access
and the associated Pallet/Viridian event states. A Boulder Badge also restores
completion of the old man's tutorial. A new game receives none of those early
quest completions. Bag ownership of Bide, BubbleBeam or the Bicycle restores
the corresponding reward marker without granting, removing or duplicating an
item. Seen/caught Pokédex entries and party data are retained.

Continue also restores saved NPC records without checking their event flags.
0022 filters stale hidden custom NPCs before restoring those records, removing
the outdoor cashier, west guard and coffee blockers when their repaired flags
require it. Ordinary NPCs, the player and follower are preserved.

Keep a backup of the normal save, use the game's **Continue** option and save
again after loading 0022. A save state belongs to the exact ROM that made it.
Recovery cannot reconstruct arbitrary erased history with no remaining
evidence; this is not a promise to restore every lost flag or random roll.

The Trainer Card displays Kanto's leaders and badges above Johto's. The native
saved badge numbers and the gym leaders who award them remain unchanged.

Withdraw the **Friendship Charm** from the bedroom PC. While carried in the
Bag, it sets non-Egg party Pokémon to native maximum friendship, 255. It does
not change levels, IVs or shininess, and time, held-item and other evolution
requirements still apply. The raised friendship is actual saved Pokémon data,
not a temporary display override. If all ten PC stacks are occupied, withdraw
a stack, close the PC and reopen it to receive the charm. Existing Center PCs
access the same storage.

0022 keeps the campaign at the areas completed in 0021. Route 24/25, Bill and
the returning robbed-house event follow after this compatibility checkpoint.
