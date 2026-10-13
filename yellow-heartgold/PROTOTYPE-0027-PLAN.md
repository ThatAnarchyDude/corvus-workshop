# Prototype 0027 — current development plan

0026 is the latest released prototype. 0027 remains a private development build.

The owner has approved trimming spacing to fit HeartGold's connected overworld when Yellow's functional layout and intent are preserved. Route 5 now fits one 20-by-32 area and connects outdoors through the native main matrix. Indoor doors and separate floors retain normal transitions. Earlier separate-map/fade experiments are historical.

Completed private checks: connected Cerulean and Saffron road crossings; Day Care, Underground Path and both gate entrances/returns; one normal older Route 5 save loading with preserved party, bag, quest/PC, Dex, Day Care and actor data; sign interaction, grass walking and one-way ledge behavior. Native HeartGold trees and 40 joined cliff ledges are implemented. Two small gaps at the northern tree/fence boundary now align the existing side stairs with Yellow's central approach, leaving 48 rendered trees and preserving all grass, ledges, doors and the southern gate roadblock. Continuous native tests from both Cerulean entrances and an actual live walk reach Day Care through normal walking. All 55 focused Route 5 checks pass. Real gameplay and audio were shown live and recorded locally with prepared-save labels.

Next: finish fences and the visible northern seam, gate interior and cloned door animation; broaden older-save positions, Fly, follower, camera and integrated guard progression checks; produce and verify the cumulative pristine-base patch; publish the patching page and a labeled audiovisual recording when the prototype is ready.

Preserve Johto maps, scripts, encounters and gameplay. Keep Kanto Day Care's approved shared native services. Preserve the supplied Oak intro/naming screens and intentional starter, shiny, PC, typing and evolution changes. Blue remains Kanto rival before the first Hall of Fame, with Giovanni leading Team Rocket and Viridian Gym; the later Blue takeover and Johto access remain planned. Repeated area-name banners and final Jessie/James graphics remain pending.

Keep ROMs, originals, saves and private controls local. Project Recovery stays read-only. Keep the viewing server/tunnel connected and display gameplay/audio only during actual tests. Update the plain-language log with completed checkpoints.


## October 13 — opening/save regression follow-up

Tester report: standalone DeSmuME 0.9.13-4 under Linux Xvfb has unreliable bedroom movement and an unconfirmed recurring black screen. Clean exact released 0026 on the development DeSmuME libretro core passes unchanged Oak/name intro, native bedroom walking, stairs to map503, normal first-floor save and fresh Continue. Local direct-input Linux kit also passes Continue and one-tile Down with stereo audio; input save remains intact. Two opening-metrics checks and eleven live/bridge checks pass. Original ROM and owner campaign save are unchanged. Keep this report open until the tester compares the verified first-floor save/core or supplies reproducible black-screen steps. No new prototype release from these diagnostic checks.


## October 13 — complete offline Linux tester bundle

The requested local bundle now includes the Python runner, exact DeSmuME libretro core, explicit configuration, portable Python, pinned Pillow packages, offline setup and the separate fresh first-floor save. It contains no ROM or owner campaign save. Base Linux runtime libraries are checked at startup.

An extracted-copy test using the bundled Python and packages passed Continue and one-tile movement, captured both screens and real stereo audio, and preserved the supplied save. No Xvfb, pip or network download was required for setup. The bundle remains local for transfer to the tester. Prototype 0026 remains the release, and the standalone DeSmuME/Xvfb black-screen report remains open pending comparison.
