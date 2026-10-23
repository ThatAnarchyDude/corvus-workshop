# Mt. Moon corrections in prototype 0023

The figure directly in front of Gold at the fossil display came from the
custom fossil sprites' ordinary NPC rendering settings. Both fossil sprite
entries now use HeartGold's item rendering flags. Their graphics remain
separate, and both enforce solid collision until collected.

The Super Nerd automatically stops approaches to the fossil area from both
sides and below. Trying to leave before his battle starts that battle first;
only victory enables fossil selection and its reminder. His approaches and
returns go around the fossils and ground items. His sprite now matches
HeartGold's Super Nerd overworld actors.

Jessie and James wait around the left side of the southern exit. Choosing a
fossil enables an automatic ambush across all five exit approach lanes and
both approach rows, including the side neighbors of the exit warp. They visibly approach in sequence without crossing each
other, use their existing Yellow team (Ekans, Meowth and Koffing, all level 14),
and walk to the exit before disappearing after victory. Losing preserves the
selected fossil and permits another attempt. Their music and dialogue remain.

No terrain or warp is changed. A normal save refreshes this cave's ordinary
actors once, preserving collected items, fossil choice and completed battles.
The refresh flag A93 stays outside the daily-reset and save-boundary ranges.
