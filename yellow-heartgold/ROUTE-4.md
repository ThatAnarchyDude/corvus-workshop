# Prototype 0019 — Route 4 and field interactions

This cumulative checkpoint follows prototype 0018. Never distribute the base
ROM, saves, or private test fixtures; the download page embeds only the patch.
The next unconverted area is Cerulean City. Earlier downloads remain separate.

## Requested corrections first

Kanto background signs now use type 0 (A interaction), rather than native type 1
(automatic northward approach). Story coordinate triggers are preserved. Route 2
sign events return to the physical native boards at (1029,218) and (1047,139).
Viridian Forest now has six visible native information boards, with Yellow's
existing tip scripts. Their heights were measured using native field warps from
a copy of the last 0018 normal save. One board moved from a tree at (32,57) to
the adjacent reachable grass tile (32,58). The route through the forest remains
connected. Background scripts do not issue an NPC-facing command.

Ground item balls retain native active-object and height-aware collision. A
small hook at 0x02060C34 prevents sprite 87 from using the pass-through flag in
player collision checks, including carried saved-object flags. Other sprites
use the original routine, so followers and scripted camera objects keep their
normal behavior. Collected/removed items do not block movement.

## Route 4

Yellow's encounter table runs in all three time periods: Spearow, Mankey,
Sandshrew and Rattata at levels 8–12, with the original slot probabilities.
Native water/fishing replacements and inherited high-level trainers are inactive.
The optional Lass uses Yellow's actual level-31 Paras, Paras and Parasect team,
with explicit Scratch, Stun Spore, Leech Life and Spore. She is on a northern
side path at (1250,109), facing east, clear of the main eastbound route.
This level is intentional and does not scale with badges.

The route sign, west-side Geodude conversation and reusable TM04 Whirlwind
pickup carry over Yellow's content. HeartGold separates Yellow's west-side
Route 4 into its Route 3 map, so the Geodude NPC is placed beside the Center
there. The existing route terrain and warps remain. No new HM gates or
progression obstacles are added.

Whirlwind uses spare item 118 and compatibility bit 103. Gen I compatibility
comes from Yellow's base-stat TM lists; later species use HeartGold's Roar TM
compatibility. Existing HeartGold TM04 Calm Mind and the earlier custom Bide,
Water Gun and Mega Punch machines are preserved. Save structures and native
pocket capacity are unchanged.

## Carried saves

A one-time Route 4 scene refresh replaces the older saved Route 4 actor list
with the new Lass and uncollected Whirlwind ball. It runs before field input
after loading, since HeartGold skips load/resume scripts while restoring a
normal save. Flag B3A and variable 4142 track completion. Byte-wise marker reads work at
all script alignments, and native object removal does not collect an item. Party data, item
storage, money, fossil choice and quest progress keep their normal layout.

## Testing

Tests execute item-collision and TM hooks in Thumb mode, verify every original
item lookup, preserve Johto headers and existing trainers/art, check sign
registration and board heights, and validate encounter probabilities. Native
tests start from the last ordinary 0018 save, with separate native-command
fixtures for focused checks. In-game saves are backed up between checks;
save states stay with the exact ROM. See validation-prototype-0019.json for
exact build hashes, completed checks and remaining limitations.

## Published download

[Create prototype 0019 locally](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/732edbaea0dfbe33dc038db31747b173a21d1f27/psyduck-yellow/prototype-0019/index.html).
Select the original USA HeartGold ROM, rather than an earlier prototype.
Successful publication: 2026-10-11T04:01:19.942348+00:00. Previous patch trees are
unchanged. The public development log lists the Eastern release time.
