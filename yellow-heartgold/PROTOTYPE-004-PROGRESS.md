# Prototype 004 — work in progress

Psyduck/Eevee/Togepi field selection, visible Oak approach/escort, animated
field capture, Blue rival teams and bedroom shared player-PC item storage are implemented in
source. Oak's battle back sprite is not implemented. Native Johto starter
selection is restored. Shiny and bonus perfect-IV rolls are independent
1/16,384 each; ordinary random IVs remain the fallback. Each supported
native ability has a one-third chance. Psyduck is male, Eevee female,
Togepi natural. Espeon uses Synchronize because Magic Bounce is absent.

53 source/native-hook checks pass. Emulator verified PC withdrawals and
repeat interaction. Native PC menus and initial withdrawals are verified; deposits and persistence
are still under test. The remaining table presentation, rival battle,
evolution and final save/reload need testing. This is not a playtest release.

Never commit full ROMs. The browser download tool passed a real Chromium download/checksum test. It applies a patch
locally to the player's original HeartGold file without uploading it.
Earlier ROM ZIPs were removed from all six remote branches using an atomic
history rewrite with explicit leases. Cached objects and third-party copies
are outside the rewrite's control.
