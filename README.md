# Corvus Workshop ⚙️

A shared workshop for building applications, exploring science, and experimenting with engineering ideas. Different projects live in their own folders in this repository.

## Projects

### [Power Simulator](./power-simulator/)
A mobile-friendly interactive battery and capacitor simulator with electrothermal modeling, current limits, protection behavior, charts, and CSV export.

- [Open the latest stable HTML file](./power-simulator/index.html)
- [Project notes and usage instructions](./power-simulator/README.md)
- [Version 02.1 archive](./power-simulator/versions/bench-02.1.html)

### [Pokémon Psyduck Yellow](./psyduck-yellow/)

An unofficial fan project that rebuilds **Pokémon Yellow's Kanto campaign inside Pokémon HeartGold's engine** ([hg-engine](https://github.com/BluRosie/hg-engine)). You start with **Psyduck, Togepi or Eevee**; Psyduck and Eevee can **Mega Evolve**; and Kanto's towns, gyms, Team Rocket plots, Elite Four and Champion Blue follow Yellow's teams and dialogue, from Pallet Town to the first Hall of Fame. Johto (HeartGold's own region) is planned as a postgame.

> **⚠️ Latest: prototype 0050 BETA — a pre-release for testing only. It is not a complete game.** Only the Kanto campaign, up to the first Hall of Fame, has been developed. **Johto is NOT ready — do not go there.**

- **[Download / releases](https://github.com/ThatAnarchyDude/Psyduck-Yellow-Releases/releases)** — patches and notes for every prototype; no ROMs or saves are distributed, so you need your own legally obtained USA HeartGold.
- **[Patching page for 0050 (builds the game in your browser)](https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/prototype-0050/index.html)**
- **[Source code and tools](./psyduck-yellow/source/)** — the Python build tools, tests, data and notes that produce the patches (see its README for what is and isn't included)
- **[Plain-language development log](./psyduck-yellow/DEVELOPMENT-LOG.md)** — dated changes, current work and plans
- **[Project folder](./psyduck-yellow/)** — hosted patching pages for earlier prototypes and playtest clips

**What 0050 adds (since 0042):** your starter Eevee can evolve into all eight Eeveelutions and into the new **Novareon** (use a Sandwich on it), each with its own Mega Evolution; Novareon is the first **Stellar**-type Pokémon (takes normal damage from everything, same-type bonus on every move); a rainbow STELLAR type tag plus new Sandwich and Novareon icons; and fixes for the starters' evolution screen, summary-screen sprites and shiny Mega colours.

**What 0042 added (since 0041):** Silph Co., Victory Road, a second rival battle on Route 22, the Route 22 badge gate, and the way to the Indigo League and Hall of Fame. **0041** brought Pokémon Tower, the Celadon Gym, the Rocket Hideout, Routes 8 and 11–18, the Fuchsia, Saffron, Seafoam and Viridian gyms, the League, Mega Psyduck and free Mega Stones.

**How much has been played:** the developer has played New Game through Vermilion. Everything after that has only had small emulator tests, so expect bugs, including softlocks. Still to build: some side content (Silph Co. Card Key doors, Moltres, Safari Zone, Cinnabar Mansion, some extra gym trainers) and all of Johto.

## How the workshop is organized

Each project gets its own directory, documentation, and version history. We keep a consistent `index.html` for the latest stable standalone simulator and preserve versioned snapshots separately.

## Licensing and safety

Licensing is **per project**, not repository-wide. For Psyduck Yellow: the documentation in the [Releases repository](https://github.com/ThatAnarchyDude/Psyduck-Yellow-Releases) is CC BY-NC-SA 4.0; the source in [psyduck-yellow/source](./psyduck-yellow/source/) is published for reference and carries no licence grant beyond what GitHub's terms allow until a licence file is added; the game patches modify a Nintendo game and may only be used with your own copy, non-commercially. The project is not affiliated with Nintendo, Game Freak, Creatures or The Pokémon Company. The [Power Simulator](./power-simulator/) is offered for permitted noncommercial use under the [PolyForm Strict License 1.0.0](./power-simulator/LICENSE.md). That license does not grant permission to distribute copies, modify the software, or use it commercially. For permission beyond those terms, contact [@ThatAnarchyDude](https://github.com/ThatAnarchyDude).

No blanket license is granted for the workshop's other materials or future projects. Each project will specify its own terms, and any license applies only to rights the owner can lawfully grant. GitHub platform terms and applicable law may provide separate rights.

**Project credit:** Workshop projects are maintained by ThatAnarchyDude in collaboration with an AI assistant presented as Zander Corvus.

Experimental simulators are educational tools and must not be used as the sole basis for building or sizing real electrical systems.
