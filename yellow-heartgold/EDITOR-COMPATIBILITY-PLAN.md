# PKHeX compatibility before prototype 0023

Owner preference: provide a plugin for the normal PKHeX application first.
Use a separate project-specific version only if the required functionality
cannot be implemented through the plugin interfaces.

Before implementation, read the current upstream license and plugin API,
back up an ordinary prototype save, and verify native HGSS parsing and an
unchanged round trip. Then identify custom item names, changed evolution/type
rules, and any project-specific state that needs editor support. Keep standard
HGSS behavior intact. Custom legality rules must be distinguished from official
HGSS legality; do not present intentional hack changes as official legality.

Investigate this before continuing prototype 0023. It is not a released compatible editor or part of prototype 0022.
Prepared test-save Pokémon are separate from ordinary player progression.


Investigation result: basic native save parsing, preservation and two in-game
Continue reloads passed using upstream PKHeX Core 26.08.26. A plugin skeleton
with project PC/shiny information and starter Hidden Ability editing compiles.
See `pkhex/README.md` for exact scope, GPL terms and remaining Windows GUI tests.
A full editor fork is not currently necessary for the tested use cases.
