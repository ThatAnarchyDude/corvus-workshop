# Mt. Moon artwork

Jessie and James have separate 16-frame, 32-pixel overworld sprite sheets in
HeartGold's visual style. The fossil sheet contains 16-pixel Helix and Dome
props. These are generated project art, converted to the native limited palette
when building. Existing HeartGold models and Rocket trainer resources are kept.

The paired battle portrait is a direct port of Yellow's original 56-pixel
Jessie/James sprite, centered in HeartGold's 80-pixel battle resource. Source:
pret/pokeyellow, `gfx/trainers/jessiejames.png`, commit
`e89ead154b9968aa50eed9328ff2b38b6c194382`. It retains the original monochrome
appearance. Only edge-connected background pixels become transparent.

`tools/mtmoon_art.py` adds sprite IDs 91–94 and trainer class 129 for trainer 777.
Original trainer classes, Johto Rocket graphics and existing sprites are preserved.
