# Prototype 004 — work in progress

Psyduck/Eevee/Togepi field selection, visible Oak approach/escort, animated
field capture, Blue rival teams and bedroom PC items are implemented in
source. Oak's battle back sprite is not implemented. Native Johto starter
selection is restored. Shiny and bonus perfect-IV rolls are independent
1/16,384 each; ordinary random IVs remain the fallback. Each supported
native ability has a one-third chance. Psyduck is male, Eevee female,
Togepi natural. Espeon uses Synchronize because Magic Bounce is absent.

53 source/native-hook checks pass. Emulator verified PC withdrawals and
repeat interaction. The remaining opening choreography, table, rival battle,
evolution and final save/reload need testing. This is not a playtest release.

Never commit full ROMs. The planned browser download tool applies a patch
locally to the player's original HeartGold file without uploading it.
Earlier ROM ZIPs were removed from all six remote branches using an atomic
history rewrite with explicit leases. Cached objects and third-party copies
are outside the rewrite's control.
