# CHECKPOINT (campaign-loop)

## Area: Lavender Town / Pokemon Tower / Silph Scope — STARTED, NOT BUILT
Date: 2026-10-22. Base: build/0040-release-v1 ROM (SHA f2748917...). No ROM built, no tests run.

Findings (read-only, from the 0040 ROM header table; map-name index = low byte of header offset 18):
- HG Lavender Town = map 53 (7 doors to maps 433-439) plus map 494 (reached from 434). No Pokemon Tower floors exist in HG.
- Yellow reference cloned read-only to the session scratchpad (pret/pokeyellow); not committed.
- Method modules found: tools/route10_progression.py, tools/rock_tunnel_progression.py (trainer actors + wild rows appended, headers repointed). No driver script that chains them into a build was found in tools/.

Blocked on: which HG maps host the 7 Pokemon Tower floors (new headers vs repurposed tower maps). Needs owner decision.
Deferred: Mr. Fuji rescue, Marowak ghost, Silph Scope (Rocket Hideout item, Celadon area) — follow in dependency order.
