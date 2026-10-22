# Prototype 0027 — Saffron guards and faithful Route 5 terrain

Continue from the published 0026 checkpoint. This plan supersedes older
milestone lists for current work. No 0027 release is ready yet.

**CURRENT DIRECTION — owner-approved compact connected overworld:** fit Route5 into
20x32 by trimming four spacing rows, preserving all functional Yellow features. Keep
HG's main matrix and global coordinates, with seamless outdoor travel. Normal
interior/floor transitions are allowed. Older 36-row separate-matrix and city-fade
probes below are historical experiments and must not guide new production work.
Use tools/build_prototype0027_connected_private.py for the active private probe.
The owner authorizes similar shortening elsewhere without another question when it
preserves Yellow's intent; preserve events, characters, roadblocks and progression.

## Verified guard work

Only four Kanto gatehouse headers change, with appended script/text/event members.
Original archive members, Johto resources and the complete 0025 intro/naming screens
remain unchanged. One shared flag (0xA9D) controls all guards; no saved variable is
allocated over bedroom PC slots. Trigger conditions are literal zero.

Four compiled checks pass. Native north refusal returns the player to its route
side. Offering Fresh Water consumes exactly one, opens all gates and survives normal
save/fresh Continue on the candidate without test transports. Native passages at the
other three gates preserve the remaining drink and bedroom PC bytes. These isolated
prepared-save tests do not establish campaign difficulty or full Yellow progression.

Native Soda Pop/Lemonade acceptance and refusal at all four approaches now pass.
Before release, record actual gameplay with audio and verify a cumulative pristine-base
patch round trip. Preserve all earlier checkpoints.

## Route 5 geometry

Yellow is 20 by 36 walking tiles. HeartGold currently provides one 32 by 32 matrix
cell. Do not shrink Yellow's layout to fit. The source-derived private topology has
490 passable tiles, 449 reachable from the north and 40 directed ledge edges. Preserve
the exact Day Care door (10,21), Underground Path door (17,27), sign (17,29), gate
entrances (9,29)/(10,29), southern gate exit (10,33) and north/south city connections.
The southern exit is separated from north-side walking until crossing the gate.

Use tools/yellow_walk_topology.py for collision/ledge references and
 tools/yellow_layout_reference.py for original blocks and event sources. Reference
outputs remain ignored/local. The private two-cell terrain, native walking permissions, grass, ledges and doors are implemented and tested; detailed progress follows below.
Inspect existing Nitro model writers and native HG terrain/material/prop data; choose
a two-cell Kanto layout strategy, then rebuild HG-style visuals, heights, permissions
and warps together. Do not edit Johto cells or gameplay. Check continuity, cameras,
followers, encounter terrain, each door, each ledge and normal save compatibility.

## Preserved requirements and later work

All approved starters, shiny odds, PC supplies, Golduck typing and custom evolution
methods remain intentional. Kanto Day Care uses the native shared storage and
interactions without changing Johto's facility; egg handling needs separate checks.
Preserve every Oak introduction and naming screen exactly as the supplied 0025.
Blue is the Kanto rival before first Elite Four/Hall of Fame, without Leader title;
Giovanni remains Rocket/Viridian leader until then, followed by Blue's gym takeover
and Johto access. Title/promotion logic, repeated area-name banners and HG-style
Jessie/James replacements remain unfinished. Defer unclear intentional differences.

Use new build paths, leave originals/saves private and ignored, maintain handoff and
plain-language logs, and include a labeled audiovisual test recording with completed
checkpoints. No public push is authorized by this local plan. Existing stream stays
paused during editing. The owner explicitly approved separate private controls; the existing public stream URL is now view-only. Ten bridge tests and actual remote permission checks passed.


## Private terrain probe progress — October 12

An appended 1x2 matrix and two new land members load Route 5 at its full 20x36 tile
size without changing matrix 0 or original archive members. Source walking permissions
are translated with blocked padding and 40 native south-ledges (0x803B). A native
probe moved from row 2 to row 4 and rejected movement back north across that ledge.
One-frame test inputs were too brief for the hop; normal held inputs verified it.
The initial temporary color geometry remains historical diagnostic work. Later probes add native materials, selected props, grass behavior and doors. Remaining work includes
final scenery, region connections and legacy save migration. Lower-cell loading and same-layout save/Continue are verified below.
Private probe files remain ignored; do not release them or replace 0026 with them.

## More local Route 5 terrain progress — not a new download

The private two-cell map now has all48 of Yellow's grass tiles. Native grass walking
triggered Pidgeotto at level17; an actual live grass test triggered Abra at level7,
matching the route's Yellow encounter table. The lower cell loads at row34, permits
walking to row35 and blocks the temporary padding beyond it. A normal save and fresh
Continue retained the lower-cell position and existing party/quest/Pokédex state.

The reusable diagnostic compiler passes four checks, including reproduction of the
native-tested ROM and preservation of all original resources. The visuals remain
temporary colors; buildings, doors, city connections and old-save coordinate migration
are unfinished. The live feed showed the real diagnostic test and paused afterward.
Prototype0026 remains the latest public patch. No public push occurred in this run.

## Local Route 5 doors — still a private development build

The new Day Care and Underground doors now enter their existing interiors and return
at the intended Route 5 positions. Both gate entrances and the second north doorway
also pass native round-trip checks. The Underground sign responds to A at Yellow's
position. Five checks confirm the door compiler and preservation of original resources;
Johto and the locked intro/naming screens remain unchanged.

Native HeartGold building and terrain texture assets have been identified for replacing
the diagnostic visuals. Visible buildings, Yellow's smaller gate interior, neighboring
city connections and old-save coordinate migration are unfinished. The diagnostic
terrain is not ready for release. Prototype0026 remains the public playable checkpoint.
No public push occurred in this run.

## Local native Route 5 graphics — October 12 afternoon

New tools/route5_materials.py reuses the original Route 5 material section and native
external texture bindings: grass01gs, egrass and cliff01gs. Native screenshots confirm
rendering; permissions, door events, heights and all original members remain unchanged.
Flat cliff strips are diagnostic placeholders for future visible ledge geometry.

New tools/route5_props.py places native Underground house290 and sign31 by translating
the original measured door/event-to-prop offsets. Native sign text reads UNDERGROUND
PATH. Native entry to469 and return to13(23,28) pass; party3/parcel2/Dex state retained.
Day Care model/door alignment, gate model, trees and complete scenery remain unfinished.
Eight new focused material/prop tests pass; the full Route 5 suite passes23 checks.

Private build/0027-route5-native-props-v1 is NOT a released prototype. It retains the
native textured private terrain and existing door plumbing, cloning lands697/698 and
matrix299. All original archive members, Johto and locked opening/naming preserved.
City connections, saved-coordinate migration, smaller Yellow gate interior and production
matrix integration remain prerequisites. Guard candidate remains separate for now.
No public push; latest public prototype remains0026.

Actual live native building test uses build/0027-live-native-props-v1 (runner52932),
separate copied prepared save and explicit unfinished-art label. Same public viewing
URL/private controls; video/audio paused after gameplay. The first return assertion read
transient coordinates during a map transition; settled native status was23,28. The helper
now waits for both map and coordinates, and a repeat live round trip passes.

## Local mirrored scenery and guard integration — October 12 afternoon

The native Day Care house and its door leaf are mirrored together so the visible
right-hand doorway meets Yellow's warp at(16,21). Native entry517/return13(16,22)
passes. The native north–south gate renders from both matrix cells; both entrance
checks pass. Trees, ledge geometry, the smaller Yellow gate interior and cloned door
animation still need work; the scenery is not final.

New tools/route5_mirror_materials.py clones three building models, their metadata,
the prop model list/texture bank and the area descriptor. Existing archive members
remain byte-for-byte intact. The model shape lookup adds three records while retaining
all existing records and payload. Only Route5's Kanto area/matrix pointers change;
Johto headers, executable overlays/ITCM/ARM7 and supplied intro/naming remain intact.
Negative scale alone hid faces; missing companion metadata/shape/texture tables caused
failed intermediate probes. Only build/0027-route5-native-scenery-v5 passed visual
and native doorway checks. Keep earlier failures private; do not release any probe.

The terrain chain already started from0027-gates-development-v1, so shared-drink
scripts were already present. The earlier full crossing stopped at its active thirst
roadblock, not an obsolete guard. The new integrated probe reapplies guard banks after
warp edits and preserves both Route5 returns. Prepared native tests confirm one of two
Fresh Waters consumed, open flag set, south crossing and repeat north crossing,
remaining one drink and unchanged bedroom PC slots; empty-bag refusal returns y5.
A held input expired during a map transition; a separate input completed the repeat
crossing. Integration evidence: build/0027-integrated-route5-guards-v1/native-integration.json.

All33 focused Route5 tests pass. New tools/build_prototype0027_private.py requires
--diagnostic, ignored build output and a new path; it reproduces the private integrated
ROM from checked baseline. No release/public push. Prototype0026 remains public latest.

A labeled24-second native audiovisual DayCare recording is local/ignored at
build/0027-scenery-recording-v1/daycare-scenery-audio.mp4. Both maps13/517 observed,
real44100Hz stereo PCM,23.986sec video/23.999sec audio, pitch preserved. Actual LIVE
DayCare round trip passes using runner29241 and separate copied save folder
build/0027-live-native-scenery-v5; same viewing URL/private controls, feed paused after
playtest. Next prioritize city connections/matrix architecture and old-save migration,
then finish scenery/gate interior and verify animations/Fly/followers before release.

## Local city boundary links — October12 evening

New tools/route5_connections.py adds explicit coordinate-script transitions between
private Route5 and native HG Cerulean52/Saffron59. Cerulean road approaches use
(1291..1293,157)→13(9,1) and(1306..1308,157)→13(24,1). Route5 north row0 splits to
city(1292,156)/(1307,156); its south row35 returns59(1300,200). Saffron approach
(1300..1301,199) enters13(16,34). Arrival points sit outside source trigger rows,
preventing immediate bounce. Central Route5 exit routing is an interim HG-city mapping;
final Yellow city geometry remains required. No saved variables allocated.

Native tests pass for all six directions, plus same-core repeated roundtrips at each
approach preserving PC slots/drinks/guard state. Party3/parcel2/Dex retained. First v1
Cerulean coordinate1296,158 was in raised tree geometry and failed;v2 visible road
points are validated. Existing city actors/warps/story triggers/scripts preserved,
with only script-bank alignment zero padding changing in copied bank encodings.
Main matrix0/lands/textures/Johto/overlays/ITCM/ARM7 remain untouched.

Three new focused connection tests pass; full Route5 suite36 checks pass. Native
build/0027-route5-city-links-v2 has SHA f9e1879eb67ebd04edc820989f21e336b40aeb3e67bd2192d8cb79f485bfb6b5.
Builder --diagnostic --city-links reproduces this exactly in a new ignored output.
Old-save world-coordinate migration, final city geometry/seam handling and
Fly/follower/camera validation remain blockers for release. No public push.

Previous stream processes stopped between runs. Local city-link runner69278 recovered
with separate build/0027-live-city-links-v2 save folder; actual live city roundtrip
passes. Cloudflare recovery PID1316 uses new origin
https://remedies-regression-lawyer-ins.trycloudflare.com . Existing viewing credential
remains live-token; controls live-control-token unchanged/private. Remote JPEG11787bytes,
44100Hz nonzero PCM, can_controlFalse and viewer POST403 verified. Feed paused after
gameplay. Public GitHub log still old URL because this heartbeat prohibits public push;
local log URL updated. Do not claim remote viewing was available before recovery.

## Standing stream operation

Keep the streaming server and remote viewing tunnel connected between tests. Pause
only the displayed video/audio outside actual playtesting; do not stop the services
merely because development is editing code. Enable video/audio during real gameplay
checks. Preserve the healthy tunnel URL and private controls.

## Active compact connected probe — October12 owner clarification

The owner authorizes shortening spacing when fitting Yellow areas into HeartGold's
connected overworld, including future similar cases without another question when
Yellow's intent is preserved. Outdoor travel should be seamless; normal interior,
floor and cave transitions are allowed. This supersedes the earlier strict36-row
separate-matrix strategy and temporary outdoor fade-link prototypes.

Source-derived Route5 reference now20x32, removing rows2/14/16/34. All48 grass tiles,
40 ledges, allfive doors and sign retained; allbuilding rows retained. Gate-required
south-door reachability unchanged. Four protection checks pass. Shift inside HG cell
uses x+10, matching native Cerulean side roads and Saffron's center road.

New tools/route5_connected.py retains main matrix0 and original global coordinates.
Only Kanto cells(40,5)/(40,6) reference appended lands692/694. Route5 terrain is at
native ground32worldunits/height4, matching the existing Saffron flat collision plane.
The obsolete native Saffron gate prop is removed from a cloned land; its north road
corridor opened. Source land133 remains intact. No city fade/transport scripts installed;
52/59 headers untouched. Outdoor boundary samples every4frames show no black screens
in five native crossings. DayCare517/Underground469/bothgate391 entries and returns pass.

Shared Kanto graphics list12 now retains its original23 IDs and adds cloned340..342,
so neighboring native city buildings still render. Its sole area13 users are all Kanto:
12/13/17/18/28/29/52. No Johto headers, cells, original assets or executable code changed.
Only scoped matrix0/list12 tables and extended shape lookup differ; alloriginal shape
records/payload and other archive members preserved. Intro/naming stays locked.

A normal old-layout0026save onRoute5(1292,172,height4) loads via Continue directly into
this map at the same position, WITHOUT a migration or executable hook. Party/bag/
flags-variables/Dex/DayCare/savedactors blocks2/3/4/6/7/10 remain byte-for-byte unchanged.
This proves that location, not every older save position; additional positions remain
pending. Native savedplayer/follower records use mapID1, not actualregion13, so don't
mistakenly filter savedactors by regionID if a future narrow repair is needed.

45 full Route5 suite checks passed, then a sixth connected resource-preservation
check passed alongside allother connected checks:46 focused checks currently passing.
New active builder tools/build_prototype0027_connected_private.py requires--diagnostic,
ignored output/new paths and checked baseline. Old standalone builders are historical.
Connected native24second audiovisual recording stored locally at
build/0027-connected-recording-v1/connected-boundary-audio.mp4; maps13/52 observed,
44100Hz stereo/nonzero PCM and23.986187video/23.995011audio, pitch-preserved correction.

Actual LIVE connected road roundtrip passes, remote video/audio/viewer403 verified.
Tunnel PID1316 and viewing URL preserved. Backend switched only to load the new test
ROM; runner77973 now owns build/0027-live-connected-route5-v1 copiedsave directory.
Services stay running between tests; display/audio paused afterward. No public push
or new release.0026 remains latest playable; finish trees/visibleledges/smallgateinterior/
cloneddooranimation and broader save/Fly/follower/camera checks before releasing0027.

## Compact native interaction verification

Sign/A check passed: Underground Path text visually inspected. Grass step passed
(1296,163)->(1297,163), height4. Native south hop161->163 and north refusal163->163
passed with8-frame presses. Initial1-frame missed input is not a map failure.
Party3/parcel2/NationalDex retained. All46 Route5 checks passed together.
Evidence build/0027-connected-interactions-v1. One grass step/oneledge verified;
encounter frequency, allledges and fullcompactgateprogress remain pending.
Live western road approach was blocked by the source tree barrier before grass;
do not claim it entered grass. Backend/tunnel remain running, feed paused, current
map13 world1294,167,height4. Original native tree/cliff mesh mapping inspected;
no newscenery installed. Texture preview/shared palette extent unresolved.

## Native trees and visible ledges — current private terrain

Use build_prototype0027_connected_private.py --diagnostic --native-trees
--visible-ledges --output build/NEW/private-terrain.nds. Default options preserve
older connected probe bytes. Tree-only V1 retained; current joined ledges V2 is
build/0027-native-trees-ledges-v2/private-terrain.nds, SHA
056b55fc21edfc22dc6f1ae73bb9cfeb0a8db33d171d70b90ca3323e0ab972e2.
All49 Yellow tree cells render native tree01gs canopies; all40 ledges use native
allpeakgs center texture strip on lowcliff quads. Physics/events/resources outside
terrain unchanged. V1 corner-UV gaps fixed inV2; failed1stlivehop corrected.
All52 focusedRoute5 checks pass together. Native andcorrectedlive southhop161->163
andnorthrefusal163 pass; tree-only actualgrasswalking andnativeaudio pass.
24sec labelednative AVrecording local build/0027-native-terrain-recording-v2.

Livebackend69540/copiedsave build/0027-live-native-terrain-v2, map13/1296,163,h4,
feedpausedaftertests; tunnel/URLunchanged. Servicesremainrunning. Publicplainlog
textcheckpoint appendedcommitbb66aab understandingexplicitauthorization; noROMs,
saves/source/control/media published.0026 stillrelease. Remainingfences,northvisual
seam,gateinterior,cloneddooranimation,broaderlegacy/travel/guardchecks thenpatch/AV.

## Integrated compact guard progression — October13

PureV2 productionROM unchanged. Newnativepreparedcopy provesoutdoor13->391 drink
acceptance/consumeexactly1of2FreshWaters->south13->seamless59. NativeSave andfresh
Continue onPURE V2 retainsopenflag/remainingwater/PCslots/map59. Repeatnorthcross
ends13world1300,186,h4 withnoadditionalconsumption. Nodatachangesclaimedbeyond
normalnativewalking: bag/Dexexact, oneClefairyfriendship+1/128stepcounterrollover,
12DayCareeggcountersteps andscratch4000reset explained/decryptedchecksumsvalid.
No-drinkguard returns391(5,5) withflagfalse. Native/live evidenceunder
build/0027-integrated-gate-v1 andbuild/0027-live-integrated-gate-v1.
80sec labelednativePCMrecording localbuild/0027-integrated-gate-recording-v1.
Livebackend21926,current59/1300,195,h4; feedpaused,service/tunnel/URLunchanged.
52focusedsourcechecksremainpassing; no sourcechange/publicpushthisscheduledrun.
Finishfences,northernvisualseam,gateinterior/dooranimation,broadersave/travelthenrelease.

## Current natural-access alignment probe

ActiveprivateROM build/0027-native-north-access-v1/private-terrain.nds SHA
 a8c91c21ef9256ecb8a6e4bfd93d30a1b4f51a4d23828b74506fab8e595c71be.
Build flags--diagnostic --native-trees --visible-ledges --north-access. Twofirstrow
cells source5,0/14,0 openside-stairs->centralnorthpath; treecount48 vs49historic,
all48grass/40ledges/doors/buildings/sign intact. City/Johto/header/code unchanged.
NativecontinuouspathsfromBOTHnativeCeruleanstairsintoDayCare517 verified (prepared
citystartonly;nointermediatetransport). Liveleftpathresumedafterstale-statusassertion
andalsoentered517. All55Route5checks pass together;11livechecks previouspass.
Backend19854 ownsbuild/0027-live-natural-access-v1,517/4,8,h0/feedpaused,tunnelunchanged.
Exactnativeactions capturedforAVinbuild/0027-natural-access-recording-v1; verify
recordingcompletion. Nextfences/northseam/gateinterior/dooranimation/broadersave-travel,
pristinepatch/AVrelease.0026 remainsreleased. SourceYellowreferenceimmutable.

## Native fence graphics — current private probe

Currentbuild build/0027-native-fences-v1/private-terrain.nds SHA
7dac1b0a1a6674346ac2b083f474307917bcf93232922483521d802599a8b529.
Useflags--diagnostic --native-trees --visible-ledges --north-access --native-fences.
64nativefence boundarysegments rendered; allpermissions/props/BDHC/events/other
resources/code unchanged. Fifthmesh/node supportadded; old<=4outputs preserved.
55oldfullchecks plus3newfencechecks pass. Nativefourdoors/returns andcontinuous
DayCarewalkpass;24sec labelednativeaudio/video localrecording complete.
Oneearlygrasswalkblue/blackstallnotreproduced/causeunclassified; testwildbattle
transitions before release. Backend55323/copyfolderbuild/0027-live-native-fences-v1,
verifylive-roundtripjson/status; tunnel/URLunchanged. No publicpush/newrelease.
Nextnorthernvisualseam/gateinterior/dooranimation/broadsave-travel/patchandAV.
LivefencefollowupV2 confirmed517->13/1300,179,h4 withnativeaudio. Backend38202 owns
build/0027-live-native-fences-v2/feedpaused/server+tunnelrunning. V1missedinitial
inputduringfixturetransport; V2 verifieseachactualdoortransitionbeforecontinuing.
Activebuilderpendingmetadataupdated; remainingnorthseam/gateinterior/dooranimation/
wildbattle-travel/legacychecksandreleasepackage,notalreadyimplementedscenery.

## Natural wild encounter and cloned door verification

FencesV1 ROMunchanged. Nativegrass->wildAbraLv7->Run->Route13 fieldreturn passes;
independentliveAbra encounter/escape also passeswithnativeaudio. Evidence
build/0027-wild-transition-v1 andbuild/0027-live-wild-transition-v1. Priorblueframe
consistentwithnormalbattleload,notretrospectivelyproved;broaderencountersstillpending.
ClonedDayCaredoor341 opensvisibly beforeentry andreturnsclosed; existingmetadata
supportsanimation,NO codefixrequired. Frameevidencebuild/0027-door-animation-observation-v1.
Currentlivebackend72507/copysavebuild/0027-live-wild-transition-v1/map13/1297,163,h4,
feedpausedaftertests/server+tunnelrunning. NoROM/publicpush;58Route5/11streamchecks
previouspass. Remainingnorthvisualseam/smallYellowgateinterior/broadersave-travel,
pristinepatchandreleaseAV. PrivatebuilderPENDINGmetadataupdatedforcompletedchecks.

## Current northern cliff probe

Currentprivatebuild build/0027-north-cliff-v2/private-terrain.nds SHA
1739e30e16f3aeb91844ab66699b4ba2004b210188b0d45c7bc36773c92d6a57.
Flags--diagnostic --native-trees --visible-ledges --north-access --native-fences
--north-wall.26nativecliffquads covervisualgap,leaving6staircellsopen;opaqueUV22..31
correctsV1transparentstrip. Entiregameplay/collision/props/events/city/Johtounchanged.
All61Route5checksfullPASS;5nativeoutdoorcrossings+actualLIVEroundtripPASS withaudio,
view-onlypermissionsverified. Native24secAVlocalbuild/0027-north-cliff-recording-v2.
Backend30818 ownsbuild/0027-live-north-cliff-v2/feedpaused/server+tunnelrunning,
URLunchanged. No publicpush/newrelease. NextsmallYellowgateinterior,broadersave/travel,
pristinepatchandreleaseAVpackage. Privatebuilderpendingmetadataupdated forwallflag.

## Small Yellow gate — unfinished independent diagnostic probe

Source reference now uses GATE tileset, 8x6/22 walkable/four warps/guard1,3,
closed-corridor BFS verified. tools/yellow_layout_reference.py and
 yellow_walk_topology.py retain prior Route5 outputs exactly; 5newsourcechecksPASS.
Opt-in tools/route5_gate_interior.py patches391ONLY with appended land/matrix/event;
5newscopechecksPASS. Does NOT integrate into connected private builder yet.
Builds build/0027-small-gate-v1 and-v2/private-small-gate.nds, native materials,
flatworldY16/playerheight2. Precise copied-save nativeV1 no-drink rejection,
consume-one/sharedflag/southernexit pass; PCslots preserved. See native-guard-checks.json.
ART PENDING: floor appears but walls/counters invisible/black; doublesidedV2
made no improvement. Inspect actual material lighting/UV/texture bindings and
native gate displaylists next; then both outdoor entrance/return pairs, reload/
repeat guard, legacy interior positions BEFORE integration/release. Existing
north-cliffV2 remains active/livestreamROM;0026 remains release. No publicpush.

## October 13 — prototype 0026 bedroom report checked

The other tester uses standalone DeSmuME 0.9.13-4 under Linux Xvfb. Their movement
and black-screen reports remain open. In a clean run of the exact released 0026,
our DeSmuME libretro runner completed the supplied intro, walked normally in the
bedroom, used the stairs and saved on the first floor. A fresh Continue boot
loaded that save successfully. The separate Linux runner also moved one tile.

A local Linux test kit includes that fresh first-floor .dsv, a direct-input
runner, setup instructions and a verified official core downloader. It needs no
Xvfb and contains no ROM or owner campaign save. It captures screenshots and
real stereo audio and preserves its input save. Two opening-metrics checks and
eleven live/bridge checks pass. The plain-language log and plan on GitHub were
updated with these findings; private files remain local. This comparison does
not yet explain the tester's black-screen failure. No new prototype was released.

## October 13 — complete Linux testing bundle verified

The tester's requested bundle now includes the Python runner, exact DeSmuME
libretro core, explicit configuration, a portable Python runtime, pinned Pillow
packages and offline setup instructions. It also includes the separate fresh
first-floor save and source/license notices. No ROM or owner campaign save is
included. Base Linux runtime libraries are checked at startup.

After extracting the archive into a fresh folder, its bundled Python and
packages loaded Continue and moved the player one tile, with both screens and
real stereo audio. The supplied save was preserved. Setup needed no Xvfb, pip
or network download. The bundle remains local for transfer to the tester;
prototype 0026 and the reported standalone/Xvfb black-screen issue are unchanged.

## October 13 — prototype 0027 ready locally

Prototype 0027 is on the laptop in RetroArch's downloads folder. It rebuilds
Route 5 with Yellow's shortened layout in HeartGold's connected overworld,
including native trees, fences, ledges and Day Care placement. The smaller
Yellow gate now displays correctly and preserves its separate northern doors.
The Saffron guards share the drink roadblock; one drink opens their passage.

Older saves made inside the larger gate migrate safely to the corresponding
side of the smaller room. Both sides passed, and a new in-game save reloaded
without repeating migration. Party, Bag, quest variables, Pokédex and Day Care
storage stayed identical in stable checks. All 71 focused Route 5 checks pass.
The delivered ROM also loads the owner's campaign save and an older Route 5
save with normal walking. The full Oak intro, naming screens, approved changes
and Johto resources are preserved. A separate campaign-save copy is provided.

A 50-second recording with real stereo audio is saved locally:
[Watch the 0027 native test recording](../yellow-heartgold/build/0027-release-recording-v1/prototype-0027-gate-audio.mp4).
It is labeled as a prepared-save/drink test. No test grants or transport were
included in the delivered game. The cumulative patch reproduces the ROM exactly
from the unchanged original HeartGold ROM.

The live tunnel was restored after the old one stopped. Its current link is
[Watch live testing](https://wit-banana-suddenly-virtue.trycloudflare.com/#token=SaBO46q-TKH_m6lLAib088MTzb7drRISjWaqa7IlVxM).
The service stays connected and pauses video/audio between tests. The owner
reported the separate Linux testing problem fixed by the supplied kit.

This checkpoint and recording remain local under the current no-public-push
instruction. The public patching page is still 0026. The full remake remains
in development; later Kanto content, area-name banners and regional progression
are still being completed.

## Superseding owner correction — native interiors, prototype 0028

Do not recreate interior geometry to match Yellow. Preserve HeartGold native
interior graphics/layout and fit Yellow story/events within them. Route 5's
small interior is superseded, not the connected exterior. Delivered local 0028:
build/0028-native-interiors-v1, SHA256
0de636af251081172fafcfcfee1017c3dd68c15a654ff97b76e7972a68270a52.
Native matrix/land/model exact vs pristine HG; owner/legacy Continue, walking,
small-room save return and stable blocks2/3/4/6/7 exact; native drink passage
recording build/0028-native-recording-v2/prototype-0028-native-gate-audio.mp4.
No public push. Continue Route6/UndergroundPath/Saffron exterior/event work with
native interiors retained, then pending area banners and Blue/Giovanni roles.

### Active next checkpoint: private 0029 Route 6 / Underground Path

Encounter foundation and Underground girl/empty corridor implemented; five
focused tests pass and native Rattata level 14 battle/Run and girl dialogue
observed. Native interior geometry retained. Finish six Yellow Route 6 trainers,
connected exterior, Surf/fishing validation, northern Yellow trade, hidden-item
audit and both path exits before release. Private output folders start0029;
latest delivered0028 remains unchanged. See current HANDOFF for exact evidence.

### Route 6 next-action evidence

Both Underground Path stairs and entrance doors passed native traversal to
Route 5 and Route 6; native interiors retained. Six trainer source references
are extracted and tested in build/0029-route6-foundation-v1/trainer-reference.json.
Install trainer records/dialogue and verify native battles next, then finish the
connected Route 6 exterior. No 0029 release yet.

### Trainer installation preparation complete

Six trainer battle records803..808 built privately and three preservation/team
checks pass. Prepared placement fixture verified native Weepinbell16 battle,
victory flag and repeat dialogue. Final Route6 actors/terrain not installed yet.
Current live backend35486 uses that fixture, feed paused; URL unchanged.
Continue terrain placement, other five native battles and remaining audits.

### Connected Route 6 reference ready for terrain compilation

compact-topology.json fits20x32, removes repeatedrows0/5/9/34 with bothwater
regions retained (one pond one row shorter). All grass/events/trainers/ledges
and gate reachability checked;2tests pass. Next compile native-textured terrain,
water/shoreline, doors and validated Saffron/Vermilion boundary connections.
Native land130 has32extra bytes beforeBMD; seeHANDOFF before parsingmaterials.
No finished terrain or0029release yet.

### Connected Route 6 ROM now running — private v3

Native-textured terrain, water, six actors, Yellow sign and relocated doors built.
Native gate/UG entry-return and both city boundary round trips pass. Fourfocused
checks pass, including oldRoute5exactreproduction and cityasset preservation.
Livecurrent43161 sourcev3, viewingpaused. SeeHANDOFF fornativepermissioncallback
proof andshortsouthernroadbend. Finish gameplay/save/Surf/visual/recording checks
and pending Underground trade/hiddenitems before0029release. No publicpush.
