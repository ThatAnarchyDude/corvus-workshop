# Prototype 0026 — Yellow’s southbound Route 5

Continue cumulatively from published 0025. Use a copy of the private normal
save after the Cerulean Rocket event for testing. Retain earlier versions,
patches, recordings and user saves under their existing filenames.

Convert Route 5’s encounters, signs and NPC/event structure from Yellow,
using Yellow’s Kanto layout as the target, rendered with HeartGold’s DS assets. Preserve the necessary story progression
and the eventual connection toward Vermilion. Restore missing campaign assets
when needed; do not add HM terrain barriers. Audit visible signs for accurate
A-button interactions and sight-trainers near seamless map boundaries for
early visibility. Keep the two specifically requested Viridian Cut trees.

Investigate the native Day Care services and connect the Yellow location
without breaking the original Johto facility or save records. Confirm what
can faithfully fit the retained assets before inventing new story behavior.
Ask the owner if a meaningful campaign choice cannot be implemented faithfully.

Use ordinary Save/Continue across versions, saving in-game at checkpoints.
Private transports/grants may prepare isolated fixtures; exclude them from
the release and label prepared test parties in recordings. Difficulty checks
need separate level-appropriate saves. A private PC-hosted live stream with game audio is established; keep its URL and access token out of public files.

0025 uses 32,024 bytes of the 32 KiB ITCM extension, leaving 744 bytes. Prefer
script/data edits; verify an allocation strategy before exceeding that limit.
Retain Johto terrain and archived HeartGold events. The owner's broader
dialogue revisions and Blue teams reacting to the player's Eevee evolution
await their lists. Android editor development is paused. Revisit the parked
melonDS movement freeze if it recurs with matching save/emulator evidence.


## Owner-confirmed direction — October 12, 2026

Recreate Yellow’s Kanto layout, characters, events, progression and story roadblocks;
audit earlier conversions where retained HeartGold geometry differs. Preserve the
approved starters, shiny odds, bedroom PC supplies, Water/Psychic Golduck and item
evolution rules. Leave Johto maps, events, encounters and gameplay unchanged.
Kanto Day Care sharing the native Johto Day Care storage and interactions is
explicitly approved; do not modify Johto’s existing facility.

Keep Blue as Kanto’s rival before the first Elite Four victory and Hall of Fame,
without a Leader title. Giovanni leads Team Rocket and Viridian Gym until then;
Blue takes over Viridian Gym afterward. Johto access is planned after that first
Hall of Fame. These later campaign transitions are requirements, not completed features.

Preserve the entire Oak new-game introduction and player/rival naming screens
exactly as in the owner-supplied prototype 0025. No redesign or dialogue changes
are authorized for those screens. Research suitable color Jessie/James overworld
and battle sprites that fit HeartGold’s style, retaining current assets until replacements
have been checked. Ask about unclear intentional departures from Yellow; defer those
choices while continuing independent work.

Continue local development autonomously until complete or the owner requests a pause.
An hourly continuation attempt is configured, subject to app/PC availability and usage.
Update the public plan and plain-language log accurately. Each completed prototype
update must include a labeled gameplay test recording and a usable prototype link.
Private ROMs, saves, raw RAM and stream access details remain excluded.

## Current local progress — not a released checkpoint

The 0026 foundation appends Yellow’s Route 5 encounter table, removes its inherited
outdoor NPC, supplies an A-button Underground Path sign and connects the existing
Kanto Route 5 house to cloned native Day Care interactions. All original archive
members are preserved; only Kanto map headers 13 and 517 change. Six focused checks
pass, including exact weighted encounters at all times of day and unchanged Johto
resources. ARM9 changes outside those headers are limited to verified compression-
length metadata; the ITCM extension remains 32,024 bytes.

Native tests loaded the owner’s copied save through Continue and reached the Kanto
Day Care. Its greeting, deposit selection and a successful deposit were observed.
These tests use an isolated private transport fixture; no transports or grants are
included in the development ROM. Withdrawal, normal save/reload, egg handling,
Yellow geometry/Day Care placement and the Saffron drink gate remain unverified or
unfinished. Do not publish this foundation as a completed 0026 checkpoint.


## Incremental 0026 checkpoint delivered locally — October 12

The tested Route 5 encounter/Day Care foundation has been delivered as 0026, with its own copied normal save and a 40-second native audio/video recording. The cumulative pristine-base xdelta round trip matches SHA256 c3085440e6f27d02898c6a9dd56ab0f64a4ede4f92c7dcd61dbbde4a6c1be9d4. Six focused Route 5 checks pass. Deposit, separate withdrawal/100 fee and normal save/Continue preservation were observed on private copies; egg handling remains untested. The recording shows Continue and attendant dialogue, not a complete deposit cycle.

Do not describe Route 5 as fully rebuilt. Yellow geometry and Day Care placement remain unfinished. Continue them and the native Saffron gate checks toward the next checkpoint. Exclude unverified gates from the delivered 0026 ROM. Development gate builds v1/v2/v3 contain colliding saved-variable choices and must never be used as release evidence. Current gate source uses only flag 0xA9D and a literal-zero coordinate condition; four compiled checks pass, native validation pending. Bedroom PC dynamically occupies 0x4152 through 0x4165. Preserve Johto and all owner saves.

Public artifact publication is pending; no ROM/save or source push is authorized by local packaging. Existing public 0025 remains available. The owner explicitly authorizes plan/log updates; preserve their added live-stream link while access changes await approval.
