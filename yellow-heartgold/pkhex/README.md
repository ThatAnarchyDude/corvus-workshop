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

`PsyduckYellow.Plugin` implements the real upstream IPlugin API and builds
successfully as a Windows .NET 10 DLL. It adds a Tools entry with an explicitly
opt-in project view: player PC item stacks, Shiny/Friendship Charm labels,
parcel state, and project shiny classification (XOR < 16). It can apply the
project's already-supported Hidden Ability to the currently edited Psyduck,
Eevee or Togepi. The user must still Set the Pokémon into a slot and export.

The cloud runner is Linux: **Windows GUI loading and ability-edit round trips
have not been verified**. This is source for an experimental plugin, not a
released or fully validated editor. Do not use it on the only copy of a save.
It cannot distinguish a hack from ordinary HGSS solely by save format, so its
project view asks for explicit confirmation and never runs automatically.
It does not rewrite the official legality engine, stock species names/types,
item lists or shiny icons. Custom rules can therefore still disagree with the
standard editor's displays and legality checks. Further integration is needed
before claiming full project compatibility.

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
