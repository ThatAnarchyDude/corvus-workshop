# Psyduck Yellow PKHeX plugin — experimental 0.1.0

[Download the Windows plugin and source](PsyduckYellow.Plugin-0.1.0-experimental.zip?raw=true).
Use **PKHeX 26.08.26**. Extract `PsyduckYellow.Plugin.dll` into the `plugins`
folder beside PKHeX, restart it, and open a **copy** of your normal battery save.
Select **Tools → Pokémon Psyduck Yellow**. Export the save after applying edits.
The ZIP also contains complete plugin source, build scripts and the GPL license
under `source/`. It contains no ROMs or saves.

## What was checked

- Hidden Ability export for 12 supported species; personality, gender, IVs,
  shiny status, quest flags and Pokédex data stayed intact.
- Native Continue reloads for Psyduck, Eevee, Togepi and a PC item edit.
- The actual pinned upstream PKHeX loader discovers and loads the DLL on Windows.
- Windows form controls, party selection, shiny display and PC storage gating.

[Passing Windows check](https://github.com/ThatAnarchyDude/corvus-workshop/actions/runs/38168315938).
[Detailed source and findings](https://github.com/ThatAnarchyDude/corvus-workshop/tree/7137a96a526306225def58c26095597f752e22b1/yellow-heartgold/pkhex).
[Verification report](validation.json) · [Package checksum](SHA256SUMS).

## Current limits

A full manual editing session in the PKHeX application remains to be tested.
This plugin edits saved party slots directly and shows project shiny status;
it does not replace the official legality engine, stock item menus or species
information. Its project profile requires explicit selection because normal
HeartGold saves share the same format.

**Apply custom Hidden Abilities last**, after other Pokémon editing, then
export. Normal PKHeX's Gen IV editor can replace them with a standard ability.
Do not Set a stale Pokémon from that editor over a plugin-edited party slot.
The project's shiny rules use XOR < 16; normal Gen IV shiny icons/checks use
XOR < 8. Espeon's Magic Bounce is unavailable in Gen IV.

The standalone plugin repository and upstream fork are prepared but have not
been created on GitHub: the integration cannot create new repositories. The
package is temporarily published through the existing project. Earlier game
patches and recordings remain unchanged.
