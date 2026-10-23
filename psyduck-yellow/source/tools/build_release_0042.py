"""Build the public prototype-0042 BETA release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

Everything the page needs, including the older patch stages it chains through, is copied into <releases>/prototype-0042 so the release does not depend on any other repository.

Usage: build_release_0042.py <clone of corvus-workshop main (read only)> <0039-art-to-0042.xdelta> <0039 art ROM> <0042 ROM> <releases-repo clone>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 22, 2026'
VERSION = '0042-BETA'
PAGE = 'https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/prototype-0042/index.html'
OUT_NAME = 'Pokemon-Psyduck-Yellow-prototype-0042-BETA.nds'

BANNER = ('<p style="border:3px solid #c00;padding:10px;background:#fff0f0;color:#600"><strong>BETA PRE-RELEASE — FOR TESTING ONLY.</strong> '
          'This is <strong>not</strong> a complete game. Only the Kanto campaign, up to your first Hall of Fame induction, has been developed. '
          '<strong>Johto is NOT ready. Do NOT go there.</strong></p>')

BLURB = ('<p><strong>Prototype 0042 — BETA PRE-RELEASE.</strong> The Kanto campaign now runs from Pallet Town to the first Hall of Fame: '
         'Silph Co. (rival, Giovanni, Lapras, Master Ball), Victory Road, a second rival battle on Route 22, a Route 22 gate that checks for all eight '
         'Kanto badges, the Indigo Plateau League and Champion Blue, on top of everything from 0041 (Pokémon Tower, Celadon Gym, Rocket Hideout, '
         'Routes 8 and 11–18, the Fuchsia, Saffron, Seafoam and Viridian gyms, Mega Psyduck and the Mega Stones).</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Vermilion. Everything after that, including all the '
         'new work in this release, has only been checked in small emulator tests, not played through. Expect bugs, including possible softlocks.</p>'
         '<p><strong>Johto is not ready. Do not go there.</strong> After the Hall of Fame the Route 22 gate opens a path toward Johto; do not take it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

READ_ME = f'''Pokemon Psyduck Yellow - prototype 0042 BETA PRE-RELEASE - {DATE}

*** BETA PRE-RELEASE, FOR TESTING ONLY. NOT A COMPLETE GAME. ***
Only the Kanto campaign, up to your first Hall of Fame induction, has been developed.
JOHTO IS NOT READY. DO NOT GO THERE. After the Hall of Fame, the gate on Route 22 opens a path toward Johto - do not take it.

HOW TO PLAY
1. Open the patching page: {PAGE}
2. Choose your OWN, original, unmodified USA HeartGold .nds file (not another prototype).
3. Click "Create my playable NDS", wait for the checks to finish, then download the result and load it in your DS emulator.
4. Start a NEW GAME. Saves from older prototypes do not work. Keep this build and its saves separate, and never reuse emulator save states between versions.
Nothing is uploaded; the patching happens in your browser and every step is hash-checked. Expected final SHA256: {{sha}}

WHAT IS IN THIS RELEASE
- The Kanto story of Pokemon Yellow, rebuilt inside HeartGold: from Oak's lab and your starter (Psyduck, Togepi or Eevee) to the Hall of Fame.
- New since 0041: Silph Co. (four floors with Yellow's trainers, your rival, Giovanni, the Lapras gift and the Master Ball), Victory Road trainers, a second rival battle on Route 22, the Route 22 gate that now lets you through to Victory Road once you hold all eight Kanto badges, and the path from the Hall of Fame onward.
- Already in 0041: Pokemon Tower with Mr. Fuji and the Poke Flute, the Celadon Gym, the Rocket Hideout, Routes 8 and 11-18, the Fuchsia, Saffron, Seafoam (Blaine) and Viridian gyms, the Elite Four and Champion Blue, Mega Psyduck and Mega Eevee, and every Mega Stone for free in the Vermilion Mart.

WHAT HAS BEEN TESTED
- The developer has played New Game through Vermilion (including the Pewter and Cerulean gyms and Mega Evolution).
- EVERYTHING AFTER THAT, including all new work here, has only had small emulator checks (for example: entering Silph Co. and starting a battle; walking into the Route 22 rival scene; the Route 22 gate). Winning those battles, the full League and the Hall of Fame have NOT been played end to end on a real save.

NOT BUILT YET
Silph Co. Card Key doors and item balls; Moltres; Victory Road item balls; the Safari Zone and Gold Teeth (a Warden in Fuchsia gives Strength and Surf instead); the Cinnabar Mansion; Game Corner and Department Store extras; some of Yellow's extra gym trainers (HeartGold's gyms have fewer). Silph Co. and the Rocket Hideout reuse HeartGold's building layouts rather than Yellow's floor plans, and only part of Victory Road holds trainers.

KNOWN ISSUE
The top screen went black once after leaving Viridian Forest by the north exit; saving and reloading fixed it. Not investigated yet.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data and dialogue are referenced from pret/pokeyellow. Unofficial fan project, not affiliated with Nintendo, Game Freak, Creatures or The Pokemon Company.
'''

LOG_ENTRY = f'''

## {DATE} — prototype 0042 (BETA pre-release)

**BETA PRE-RELEASE, FOR TESTING ONLY. Not a complete game. Only the Kanto campaign, up to the first Hall of Fame, has been developed. Johto is NOT ready — do not go there.**

[Create prototype 0042]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded.

What changed since 0041:
- **Silph Co.**: HeartGold has only one small Silph building, so it was cloned into four floors holding Yellow's trainers (2F–11F), Yellow's rival fight, Giovanni, the Lapras gift and the Master Ball. Card Key doors and item balls are not included.
- **Victory Road**: Yellow's 11 trainers were added; they stand only in the parts of the cave reachable on foot (the rest of HeartGold's cave needs HMs).
- **Route 22 gate**: the League reception gate used to block every corridor, which made Victory Road and the League unreachable. It now lets you through to Victory Road once you hold all eight Kanto badges.
- **Route 22 rival**: Blue's second battle (Yellow's higher-level team) now happens there once all eight badges are in hand; it is optional and a loss heals your party.
- **After the Hall of Fame**: the southern arm of the Route 22 gate opens toward Johto. Johto is not ready; do not go there.
- Internally: a 28-flag "safe pool" for future extra trainers was researched (trainer IDs are nearly used up); nothing from it is in this build.

Checked: small emulator tests of the Silph Co. entrance and a trainer battle, a Victory Road trainer sight-battle, the Route 22 gate in both directions, the second rival scene (with prepared flags and badges), and a normal start to the bedroom. **Not checked:** winning the new battles, the full League, the Hall of Fame, or anything in Johto. The developer has played New Game only through Vermilion.
'''

RELEASE_BODY = f'''# ⚠️ BETA PRE-RELEASE — FOR TESTING ONLY

**This is a beta pre-release for testing purposes only. It is NOT a complete version of the game.**

Only the **Kanto campaign, up to your first Hall of Fame induction**, has been developed. **Johto is NOT ready — DO NOT go there.** After the Hall of Fame, the gate on Route 22 opens a path toward Johto; please do not take it.

## How to play
1. Open the **[patching page]({PAGE})**.
2. Pick your **own, original, unmodified USA HeartGold `.nds`** file.
3. Click *Create my playable NDS*, wait for the checks, then download it and load it in your DS emulator.
4. Start a **New Game** (older saves do not work).

Nothing is uploaded; the patching runs in your browser. This release ships **no ROM or save files**; you must supply your own legally obtained game.

## What's new since 0041
- **Silph Co.** with Yellow's trainers, your rival, Giovanni, the Lapras gift and the Master Ball
- **Victory Road** trainers
- A **second rival battle on Route 22**
- The **Route 22 gate** now opens to Victory Road once you hold all eight Kanto badges
- The League, Champion Blue and the **Hall of Fame** can now be reached (not yet played end to end)

## How much has been tested
The developer has played New Game through **Vermilion**. Everything after that, including all of the above, has only had small emulator checks. Expect bugs, including possible softlocks.

## Not built yet
Silph Co. Card Key doors and item balls · Moltres · Safari Zone / Gold Teeth (a Warden gives Strength and Surf instead) · Cinnabar Mansion · some of Yellow's extra gym trainers · parts of Victory Road

## Known issue
The top screen went black once after leaving Viridian Forest (saving and reloading fixed it).

Files below: the patch stage for this version, the manifest (hashes) and a plain-text read-me. Expected final SHA256: `{{sha}}`
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main(tree, delta, art_rom, new_rom, releases):
    root = Path(tree) / 'psyduck-yellow'
    old, out = root / 'prototype-0041', Path(releases) / 'prototype-0042'
    out.mkdir(exist_ok=True)
    shutil.copyfile(delta, out / '0039-art-to-0042.xdelta')
    for name in ('HG-ENGINE-CREDITS.md', 'LICENSE.txt'):
        shutil.copyfile(old / name, out / name)
    html = (old / 'index.html').read_text()
    m = re.search(r'(<script id="package" type="application/json">)(.*?)(</script>)', html, re.S)
    package = json.loads(m.group(2))
    stages = package['stages']
    assert len(stages) == 5 and stages[3]['manifest']['output_sha256'] == sha(art_rom)
    for st in stages[:4]:                                  # mirror the older stages so this release is self-contained
        src = root / st['url'].split('/psyduck-yellow/')[1]
        shutil.copyfile(src, out / src.name)
        assert sha(out / src.name) == st['manifest']['patch_sha256']
        st['url'] = src.name
    art_sha, new_sha, patch_sha = sha(art_rom), sha(new_rom), sha(delta)
    size_art, size_new, size_patch = Path(art_rom).stat().st_size, Path(new_rom).stat().st_size, Path(delta).stat().st_size
    stages[4] = {'url': '0039-art-to-0042.xdelta', 'bytes': size_patch,
                 'manifest': {'source_sha256': art_sha, 'source_bytes': size_art, 'output_sha256': new_sha,
                              'output_bytes': size_new, 'patch_sha256': patch_sha, 'patch_bytes': size_patch}}
    package['manifest'] = dict(version=VERSION, source_sha256=package['manifest']['source_sha256'],
                               source_bytes=package['manifest']['source_bytes'], output_sha256=new_sha, output_bytes=size_new,
                               cumulative=True, roundtrip_verified=True,
                               status='BETA PRE-RELEASE for testing only: Kanto through the first Hall of Fame; Johto not ready; owner-played to Vermilion only',
                               browser_patch_stages=[{'url': s['url'], 'bytes': s['bytes'], 'sha256': s['manifest']['patch_sha256']} for s in stages])
    package['patchURL'], package['patchBytes'] = '0039-art-to-0042.xdelta', size_patch
    html = html[:m.start(2)] + json.dumps(package, ensure_ascii=False) + html[m.end(2):]
    html = html.replace('Psyduck Yellow prototype 0041-EXPERIMENTAL', 'Psyduck Yellow prototype 0042-BETA')
    html = html.replace('Expanded engine — Kanto campaign build · Prototype 0041-EXPERIMENTAL', 'Expanded engine — Kanto campaign build · Prototype 0042-BETA (pre-release, testing only)')
    html = html.replace('Download prototype 0041-EXPERIMENTAL.nds', 'Download prototype 0042-BETA.nds')
    html = html.replace('Pokemon-Psyduck-Yellow-prototype-0041-EXPERIMENTAL.nds', OUT_NAME)
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0041'))
    lines[i] = BLURB
    j = next(k for k, l in enumerate(lines) if l.startswith('<h1>'))
    lines.insert(j + 1, BANNER)
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0041-EXPERIMENTAL' not in visible and 'prototype 0041' not in visible.lower().replace('everything from 0041', ''), 'stale 0041 label left in the page'
    (out / 'index.html').write_text(html)
    (out / 'manifest.json').write_text(json.dumps(package['manifest'], indent=2, ensure_ascii=False) + '\n')
    (out / 'READ-ME-FIRST.txt').write_text(READ_ME.replace('{sha}', new_sha))
    log = root / 'DEVELOPMENT-LOG.md'
    text = log.read_text()
    text = re.sub(r'\*\*Last updated: [^*]*\.\*\*', f'**Last updated: {DATE}.**', text, count=1)
    log_text = text + LOG_ENTRY
    # releases repository: plain-language README and a copy of the full development log
    rel = Path(releases)
    readme = (rel / 'README.md').read_text()
    start = readme.index('## Play it')
    end = readme.index('## What is (and isn\'t) here')
    top = readme[:start]
    new_top = top.rstrip() + f'''

> ## ⚠️ BETA PRE-RELEASE — FOR TESTING ONLY
> The newest release (**prototype 0042 BETA**) is a **pre-release for testing. It is NOT a complete game.**
> Only the **Kanto campaign, up to your first Hall of Fame induction,** has been developed.
> **Johto is NOT ready — DO NOT go there.**

## The game in plain words
Psyduck Yellow retells **Pokémon Yellow's Kanto story inside Pokémon HeartGold**. You start with **Psyduck, Togepi or Eevee**; Psyduck and Eevee can **Mega Evolve**; and Kanto's towns, gyms, Team Rocket plots, Elite Four and Champion Blue follow Yellow's teams and dialogue. The goal of this project is a finished Kanto adventure from Pallet Town to the first Hall of Fame; Johto (HeartGold's own region) is meant to come later as a postgame.

## Where it stands right now (prototype 0042 BETA)
- **Built:** Pallet Town through Vermilion, Pokémon Tower, Celadon and the Rocket Hideout, Routes 8 and 11–18, Fuchsia, Saffron (with Silph Co.), Seafoam and Viridian gyms, Route 22, Victory Road, the Indigo Plateau League and the Hall of Fame.
- **Played by the developer:** New Game through Vermilion. Everything after that has only had small emulator tests, so expect bugs, including softlocks.
- **Not built yet:** some side content (Card Key doors, Moltres, Safari Zone, Cinnabar Mansion, some extra gym trainers) and **all of Johto**.

''' + '\n'
    rest = readme[start:]
    rest = rest.replace('Open the latest page from the [Releases](../../releases) section (or the [hosted prototype 0041 patching page](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0041/index.html)).',
                        f'Open the latest page from the [Releases](../../releases) section (or the [hosted prototype 0042 BETA patching page]({PAGE})).')
    assert '0042' in rest, 'README link not updated'
    changelog = '''
## Release history (newest first)
- **0042 BETA — October 22, 2026 (pre-release, testing only).** Silph Co., Victory Road, the second Route 22 rival battle, the Route 22 badge gate, and the way to the League and Hall of Fame. Kanto only; Johto not ready.
- **0041 EXPERIMENTAL — October 22, 2026.** Pokémon Tower, Celadon Gym, Rocket Hideout, Routes 8 and 11–18, the Fuchsia/Saffron/Seafoam/Viridian gyms, the Indigo League, Mega Psyduck and the free Mega Stones.
- Earlier prototypes (0016–0039) built the opening, starters, Pewter/Cerulean and the engine base; see the full dated list in [DEVELOPMENT-LOG.md](DEVELOPMENT-LOG.md).
'''
    (rel / 'README.md').write_text(new_top + rest.rstrip() + '\n' + changelog)
    (rel / 'DEVELOPMENT-LOG.md').write_text(log_text)
    (Path(releases).parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha))
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch}))


if __name__ == '__main__':
    main(*sys.argv[1:6])
