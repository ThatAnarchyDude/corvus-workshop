# Psyduck Yellow title artwork

`logo.png` and `water.png` were generated for this title-screen change. The logo uses the requested HeartGold lettering style with the words Pokémon / Psyduck Yellow / Version. The water is an original tileable painted texture. Runtime graphics are resized and quantized by `tools/title.py`; the original HeartGold logo palette is read only from the locally supplied ROM.

The animated Psyduck, paddles and ripple wake are original procedural geometry defined in `tools/title_models.py`. No extracted Nintendo model, palette or SDK is stored here. Nintendo's original title backdrop, theme and control flow remain in the locally patched game.

Nitro binary layouts were checked against the pret/pokeheartgold reference and scurest/apicula's format reader. The runtime format writers use the project's pinned ndspy dependency. These fan-made modifications do not grant rights to Nintendo game content or trademarks.
