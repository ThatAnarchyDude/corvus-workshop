# PKHeX compatibility investigation

PKHeX's official source is https://github.com/kwsch/PKHeX. This work targets
upstream commit `66ef5983a5d349efa2dd615f2926a1b1ee97306e`, version 26.08.26,
and .NET 10. The upstream Core package declares GPL-3.0-or-later. The included
plugin and probe source use that license. Preserve license/notices and provide
corresponding source when distributing derivatives; a fork being public does
not by itself establish its license terms.

## Verified

PKHeX Core recognized a copied prototype 0022 native DeSmuME battery save.
An unchanged export preserved the entire 1,100-byte event-variable/flag block,
Pokédex block and decrypted party. Export retained the emulator footer and
passed the native save checksums. Both that export and a deliberately edited
export booted through **Continue** in the native DS emulator. Both retained
National Pokédex access, parcel-complete progress and the party. The explicit
money increase and lead HP IV change were observed in live game RAM after
Continue. Original private saves were not overwritten.

These checks used one prepared test save, not the owner's actual save or every
possible game state. Stock PKHeX already supports the basic HGSS save format;
a separate full editor fork is not required for these tested edits.

## Experimental plugin

`PsyduckYellow.Plugin` implements the real upstream IPlugin API. It builds
as a Windows .NET 10 DLL and edits a selected saved party slot directly. The
previous approach through the normal Pokémon editor was replaced: upstream
`GetAbilityIndex4` falls back to the first normal ability for unknown Gen IV
abilities, and `SaveMisc4` writes that dropdown value during preparation.
Apply project abilities after other editing and export the save; do not Set a
stale Pokémon from the normal editor over the edited slot.

The plugin shows project shiny status (XOR < 16), lists ten player PC stacks,
and supports explicit stack edits with bounds/initialization checks. Supported
Hidden Abilities cover Psyduck/Golduck, Eevee's supported evolutions, and
Togepi/Togetic/Togekiss. Espeon's Magic Bounce is unavailable in Gen IV.

The exact shared editing code passed 12 species export tests. Checksum, gender,
PID, nature, shiny XOR and unrelated fields remained intact. Shiny boundaries
0/7/8/15/16/65535, invalid edits and PC storage were checked. Three prepared
starter fixtures with project-only shiny XOR 12 and Hidden Abilities loaded via
normal Continue in the emulator, retaining those properties, National Pokédex
access and parcel completion. An edited stack of 25 Poké Balls also persisted
in the PC after Continue. Fixtures are synthetic tests, not ordinary playthroughs.

A Windows host probe covers IPlugin initialization, Tools menu insertion,
form construction, party selection, project shiny display, the initialized-PC
gate and disabling the plugin for non-HGSS saves. The Windows run passed, including loading the DLL through the pinned upstream
PluginLoader: https://github.com/ThatAnarchyDude/corvus-workshop/actions/runs/38168315938. These tests do not constitute a complete
manual PKHeX editing session. A separate full fork is not required for tested
native edits; standard editor icons/legality/types/item lists remain unchanged.

## Public repositories

- Upstream fork: https://github.com/ThatAnarchyDude/PKHeX-Psyduck-Yellow
- Plugin source: https://github.com/ThatAnarchyDude/psyduck-yellow-pkhex-plugin
- Plugin releases: https://github.com/ThatAnarchyDude/psyduck-yellow-pkhex-plugin/releases

The owner created both repositories and granted this integration access. The
prepared plugin history was merged with the repository's initial README commit,
without rewriting that history. Further plugin development belongs in the
standalone plugin repository; this directory records the initial investigation.
The fork retains upstream's application and license and includes a project note.

## Build

Build the pinned upstream PKHeX.Core with .NET SDK 10, then:

```sh
dotnet build PsyduckYellow.Plugin -c Release \
  -p:PKHeXCorePath=/absolute/path/to/PKHeX.Core.dll
dotnet run --project CompatibilityProbe -c Release \
  -p:PKHeXCorePath=/absolute/path/to/PKHeX.Core.dll \
  -- /private/copied-save.dsv /private/output-directory
```

The default Core path uses the ignored `.tools/PKHeX` checkout. Build outputs,
ROMs and saves stay out of Git. For future Windows testing, copy only
PsyduckYellow.Plugin.dll to a `plugins` directory beside the matching PKHeX
application. Keep the source and GPL license with any eventual distribution.
