# Prototype 0025 — returning Cerulean and the stolen Dig TM

Continue cumulatively from published 0024. Preserve earlier releases and use
a copy of the ordinary saved game after helping Bill for native testing.

First fix the owner's trainer-visibility report: Nugget Bridge trainers pop
in/out when the player is already nearby, and other newly added sight-trainers
show similar behavior. Compare native and added actor records, initial/updated
heights, visibility/culling flags, sprite allocation and saved actor snapshots.
Use slow approaches, retreat/reapproach, map entry, Bag open/close and normal
Save/Continue to distinguish delayed graphics loading from height or visibility
errors. Test the bridge and representative added route/cave trainers. Trainers
must be visible before a nearby approach and remain visible while on screen;
do not hide the symptom with a blanket render-distance or collision bypass.
The two owner screenshots are evidence, not permission to publish their files.

Restore Yellow's robbed-house/Rocket/Dig follow-up after Bill opens the police
gate, then prepare the southbound Route 5 campaign in later checkpoints.

Keep Johto terrain and archived HeartGold events unchanged. Add no HM terrain
barriers; retain required story gates. Save in-game frequently. Keep private
test transports and grants outside published builds. Review remaining ARM9
extension space before adding engine hooks: 0024 currently has 1,076 ITCM
bytes free. Prefer script/data changes and plan a verified allocation strategy
before the section fills. Do not assume spare RAM is safe.

The owner's broader dialogue corrections and Blue teams reacting to the
player's Eevee evolution await their lists. Android editor work remains paused.
The reported melonDS 0023 freeze is parked at the owner's request, with no
confirmed cause. Resume its investigation if it recurs or a matching save and
emulator configuration become available.
