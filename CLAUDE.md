# Psyduck Yellow — working rules (keep this file short)

Goal: a complete, playable Yellow Kanto campaign in HeartGold's engine
(new game -> Champion Blue -> first Hall of Fame). Johto is postgame, later.
Priority: 1) softlocks/progression bugs, 2) required maps/trainers/events/HMs/badges,
3) polish, 4) optional content. Simplest faithful version wins. Do not polish.

## USAGE RULES (most important)
- NEVER read yellow-heartgold/PC-TRANSFER/HANDOFF.md or psyduck-yellow/DEVELOPMENT-LOG.md
  in full. They are 350 KB and 106 KB. Use grep, or read only the last ~60 lines.
- Read yellow-heartgold/CAMPAIGN-FIRST-PLAN.md only when asked. Never read the
  old PROTOTYPE-00xx-PLAN.md or validation-*.json files unless a task names one.
- Search with grep/glob. Do not list or read whole directories.
- ## CHECKPOINT LOOP (overrides the one-task-per-session rule)
Work through the dependency order below, one area at a time, until the
usage limit. After EACH area:
1. Build into a new ignored path from the previous build's ROM.
2. Run one check: entry, one required event/reward, one trainer battle, exit.
3. Commit source changes only, locally. NEVER git push.
4. Copy the stable ROM to /mnt/c/RetroArch-Win64/downloads/ with a new
   name (Pokemon-Psyduck-Yellow-0041-<area>.nds). Never overwrite one.
5. Overwrite yellow-heartgold/CHECKPOINT.md (max 15 lines): newest ROM
   path, area just finished, what to test, known gaps, next area.
6. Tell me in 5 lines or fewer, then continue to the next area.
Do not stop to ask whether to continue. If an area fails twice in a row
for the same reason, stop retrying: save the last good ROM, write the
blocker into CHECKPOINT.md, tell me, and move to the next area if it does
not depend on the blocked one. Do not guess your remaining usage; the
checkpoint after every area is the safeguard.
- Ask a question only if blocked.

## SKIP these (they are paused to save usage)
Live video/audio streaming, Cloudflare tunnels, recordings, Discord updates,
GitHub log/plain-language entries, public patch pages, PKHeX/ALM/Android editor
work, scheduled heartbeats. Do them only if the task explicitly says so.
Local setup never authorizes a public push. Never publish ROMs, saves or source.

## Build and test
- Build steps: read the first 60 lines of yellow-heartgold/BUILDING.md.
- Base is prototype 0040: yellow-heartgold/build/0040-release-v1/ (expanded hg-engine build)
  (Eonite bedroom pickup, SHA starts f2748917). Each new build starts from the
  previous build's ROM, never from an older one. Never change the save
  layout or hg-engine internals. Testing is New Game only; old saves are unsupported.
- New outputs go in new ignored build/ paths. Never overwrite released builds
  (0037, 0038, 0039) or anything in Recovery/ (read-only). ROMs and saves stay
  local and ignored.
- Test with ONE check per change: entry, required event/reward, exit. Use ordinary
  inputs. Label any prepared save or fixture as such; it is not campaign proof.

## Hard constraints
- Preserve the supplied Oak intro and both naming screens exactly.
- Preserve approved customizations: starters Psyduck/Togepi/Eevee, shiny and IV
  rules, bedroom PC supplies, Moon Stone Psyduck, Water/Psychic Golduck, shared
  Day Care, Kanto Mart shared stock system, Jenny's free-party-slot gift, Soul
  Badge Surf in both regions, optional pre-Champion Blue battles (loss heals the
  party; first Champion Blue win is required).
- Keep native HeartGold interiors; fit Yellow's events into them.
- Do not touch Johto maps/scripts/encounters except where a traversal/HM need
  actually arises. Mega Evolution stays locked until the Johto postgame.
- Flags/variables: never allocate persistent flags at or above 0xAA0 (daily flags).
  Bedroom PC slots use variables 0x4152..0x4165; do not reuse them. Grep every
  script bank and actor list before allocating a new flag. Already used:
  A7D, A7F, A87, A9D, A9E, A9F and the Mega flag 0x9D6.
- Match Yellow's teams, levels, moves, encounters and dialogue. Dialogue changes
  come only from the owner's lists.

## Dependency order for remaining Kanto work
Rock Tunnel trainers/encounters -> Lavender/Pokemon Tower/Silph Scope -> Celadon,
Erika, Rocket Hideout -> routes to Fuchsia, Safari/Surf/Strength/Koga ->
Saffron/Silph/Sabrina -> Seafoam/Cinnabar/Blaine -> Giovanni/Viridian ->
Route 22/23/Victory Road -> League/Champion/Hall of Fame -> Johto unlock.
Record each deferred detail in one line in CAMPAIGN-FIRST-PLAN.md (append only).

## Standing owner order (2026-10-22) — overrides "one small task per session"
Keep working through the dependency order until the usage limit. After each
completed area: commit source changes only on a local branch, build into a new
ignored build/ path, and copy the ROM to /mnt/c/RetroArch-Win64/downloads/ with
a new name as a stable checkpoint for the owner to test. "Push through" means
local commit + checkpoint ROM, NOT git push (no push without an explicit order).
Halt rule: stop starting new areas when about 10% of the token budget remains;
use the remainder to ship one final stable, tested checkpoint and a short report.
