"""Build the public prototype-0050 BETA release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

The release folder is self-contained: it copies the older patch stages the page chains through from prototype-0042, adds the new
final stage (0039 art -> 0050), and rewrites the page, manifest, read-me, the repository README and the development log.
The finished ROM the page hands out is named "Psyduck Yellow Prototype 0056.nds".

Usage: build_release_0050.py <releases-repo clone> <0039-art-to-0056.xdelta> <0039 art ROM> <0050 ROM> <corvus-workshop clone (its DEVELOPMENT-LOG.md is appended to)>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 23, 2026'
VERSION = '0056-BETA'
FOLDER = 'prototype-0056'
PAGE = f'https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/{FOLDER}/index.html'
OUT_NAME = 'Psyduck Yellow Prototype 0056.nds'
PATCH_NAME = '0039-art-to-0056.xdelta'

BLURB = ('<p><strong>Prototype 0056 — BETA PRE-RELEASE.</strong> Still the Kanto campaign from Pallet Town to the first Hall of Fame. New since 0050: '
         '<strong>Moonblast and Dazzling Gleam</strong> are TMs (Fairy moves for Sylveon), the <strong>Pokédex now opens on Kanto</strong> (Pokémon 1–151; '
         'Johto and the rest only in National mode), and your starter Pokémon register under their <strong>real National Pokédex numbers</strong>.</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Vermilion. Everything after that, including all the '
         'new work in this release, has only been checked in small emulator tests, not played through. Expect bugs, including possible softlocks.</p>'
         '<p><strong>Johto is not ready. Do not go there.</strong> After the Hall of Fame the Route 22 gate opens a path toward Johto; do not take it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

NEW_IN_0050 = [
    '**Pokédex:** the starter Eevee line and the starter Psyduck now register as their ordinary species and show their real National Pokédex numbers (no more 1511/1513).',
    'The **Pokédex opens on the Kanto list** (Pokémon 1–151) with a "KANTO POKéDEX" title and a KANTO switch label. Johto and every other Pokémon appear only in National mode.',
    '**TM34 is now Moonblast and TM58 is Dazzling Gleam** (Fairy moves, so Eevee can evolve into Sylveon). Moonblast hits at 30% for its Sp. Atk drop; Charge Beam (TM57) is also learnable by Thundurus, Tapu Koko, Regieleki and Miraidon.',
    'Several Fairy-type moves now match the owner\'s specifications.',
]

READ_ME = f'''Pokemon Psyduck Yellow - prototype 0056 BETA PRE-RELEASE - {DATE}

*** BETA PRE-RELEASE, FOR TESTING ONLY. NOT A COMPLETE GAME. ***
Only the Kanto campaign, up to your first Hall of Fame induction, has been developed.
JOHTO IS NOT READY. DO NOT GO THERE. After the Hall of Fame, the gate on Route 22 opens a path toward Johto - do not take it.

HOW TO PLAY
1. Open the patching page: {PAGE}
2. Choose your OWN, original, unmodified USA HeartGold .nds file (not another prototype).
3. Click "Create my playable NDS", wait for the checks to finish, then download the result ("{OUT_NAME}") and load it in your DS emulator.
4. Start a NEW GAME. Saves from older prototypes do not work. Keep this build and its saves separate, and never reuse emulator save states between versions.
Nothing is uploaded; the patching happens in your browser and every step is hash-checked. Expected final SHA256: {{sha}}

WHAT IS NEW SINCE 0050
- Pokedex: the starter Eevee line and starter Psyduck register as their ordinary species with their real National numbers. The Pokedex opens on the Kanto list (1-151); Johto and the rest only show in National mode. The title and switch label say KANTO.
- TM34 is Moonblast and TM58 is Dazzling Gleam (Fairy moves for Sylveon); Charge Beam (TM57) is also learnable by Thundurus, Tapu Koko, Regieleki and Miraidon. Some Fairy-type moves were adjusted to the owner's specifications.
- Everything from 0050 is still here (starter Eevee line, Novareon, Stellar type, Mega Evolutions).

WHAT HAS BEEN TESTED
- The developer has played New Game through Vermilion (including the Pewter and Cerulean gyms and Mega Evolution).
- Everything after that has only had small emulator checks. For the new work: the Pokedex title, switch label and Kanto/National toggle, and a starter's Summary Dex number, checked on a prepared test save (not campaign proof). The TM changes were checked in the data only; the TMs were not used in battle. The other Eeveelution evolutions were not each tried. Winning the League and the Hall of Fame have NOT been played end to end on a real save.

NOT BUILT YET
Silph Co. Card Key doors and item balls; Moltres; Victory Road item balls; the Safari Zone and Gold Teeth (a Warden in Fuchsia gives Strength and Surf instead); the Cinnabar Mansion; Game Corner and Department Store extras; some of Yellow's extra gym trainers (HeartGold's gyms have fewer). Every Eeveelution's Mega currently uses Mega Eevee's look; Novareon's stats are placeholders.

KNOWN ISSUES
The top screen went black once after leaving Viridian Forest by the north exit; saving and reloading fixed it. Not investigated yet.
Novareon registers in the Pokedex as Umbreon (it has no entry of its own). Oak's Pokedex evaluation text still mentions Johto, the Pokedex search page may still say Johto, and not every Kanto slot has been checked in the list.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data and dialogue are referenced from pret/pokeyellow; Novareon artwork from the developer's own sprite library. Unofficial fan project, not affiliated with Nintendo, Game Freak, Creatures or The Pokemon Company.
'''

LOG_ENTRY = f'''

## {DATE} — prototype 0056 (BETA pre-release)

**BETA PRE-RELEASE, FOR TESTING ONLY. Not a complete game. Only the Kanto campaign, up to the first Hall of Fame, has been developed. Johto is NOT ready — do not go there.**

[Create prototype 0056]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded. The finished game is named "{OUT_NAME}".

What changed since 0050 (internal builds 0051–0056):
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''
- Under the hood: the starter species ids (1076 and up) are mapped back to their base species through the engine's own alias table in the Pokédex number routine and in the seen/caught registration; the regional Pokédex list was replaced by Kanto 1–151.
- Not changed: the Kanto campaign itself, the save layout, and Johto.

Checked: the Pokédex screens and a Summary Dex number on a prepared test save. Not checked: TMs in battle, every Kanto list slot, the Pokédex search page and Oak's evaluation text.
'''

RELEASE_BODY = f'''# ⚠️ BETA PRE-RELEASE — FOR TESTING ONLY

**This is a beta pre-release for testing purposes only. It is NOT a complete version of the game.**

Only the **Kanto campaign, up to your first Hall of Fame induction**, has been developed. **Johto is NOT ready — DO NOT go there.** After the Hall of Fame, the gate on Route 22 opens a path toward Johto; please do not take it.

## How to play
1. Open the **[patching page]({PAGE})**.
2. Pick your **own, original, unmodified USA HeartGold `.nds`** file.
3. Click *Create my playable NDS*, wait for the checks, then download it (**{OUT_NAME}**) and load it in your DS emulator.
4. Start a **New Game** (older saves do not work).

Nothing is uploaded; the patching runs in your browser. This release ships **no ROM or save files**; you must supply your own legally obtained game.

## What's new since 0050
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''

## How much has been tested
The developer has played New Game through **Vermilion**. Everything after that, including all of the above, has only had small emulator checks on prepared test saves. Expect bugs, including possible softlocks.

## Not built yet
Silph Co. Card Key doors and item balls · Moltres · Safari Zone / Gold Teeth (a Warden gives Strength and Surf instead) · Cinnabar Mansion · some of Yellow's extra gym trainers · parts of Victory Road · real Novareon stats

## Known issues
The top screen went black once after leaving Viridian Forest (saving and reloading fixed it). Novareon registers in the Pokédex as Umbreon; Oak's evaluation text still mentions Johto.

Files below: the patch stage for this version, the manifest (hashes) and a plain-text read-me. Expected final SHA256: `{{sha}}`
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main(releases, delta, art_rom, new_rom, workshop):
    rel = Path(releases)
    old, out = rel / 'prototype-0042', rel / FOLDER
    out.mkdir(exist_ok=True)
    shutil.copyfile(delta, out / PATCH_NAME)
    for name in ('HG-ENGINE-CREDITS.md', 'LICENSE.txt'):
        shutil.copyfile(old / name, out / name)
    html = (rel / 'prototype-0050' / 'index.html').read_text(encoding='utf-8')
    m = re.search(r'(<script id="package" type="application/json">)(.*?)(</script>)', html, re.S)
    package = json.loads(m.group(2))
    stages = package['stages']
    art_sha, new_sha, patch_sha = sha(art_rom), sha(new_rom), sha(delta)
    assert len(stages) == 5 and stages[3]['manifest']['output_sha256'] == art_sha
    for st in stages[:4]:                                  # mirror the older stages so this release is self-contained
        src = old / st['url']
        shutil.copyfile(src, out / src.name)
        assert sha(out / src.name) == st['manifest']['patch_sha256']
    size_art, size_new, size_patch = Path(art_rom).stat().st_size, Path(new_rom).stat().st_size, Path(delta).stat().st_size
    stages[4] = {'url': PATCH_NAME, 'bytes': size_patch,
                 'manifest': {'source_sha256': art_sha, 'source_bytes': size_art, 'output_sha256': new_sha,
                              'output_bytes': size_new, 'patch_sha256': patch_sha, 'patch_bytes': size_patch}}
    package['manifest'] = dict(version=VERSION, source_sha256=package['manifest']['source_sha256'],
                               source_bytes=package['manifest']['source_bytes'], output_sha256=new_sha, output_bytes=size_new,
                               output_name=OUT_NAME, cumulative=True, roundtrip_verified=True,
                               status='BETA PRE-RELEASE for testing only: Kanto through the first Hall of Fame; Johto not ready; owner-played to Vermilion only',
                               browser_patch_stages=[{'url': s['url'], 'bytes': s['bytes'], 'sha256': s['manifest']['patch_sha256']} for s in stages])
    package['patchURL'], package['patchBytes'] = PATCH_NAME, size_patch
    html = html[:m.start(2)] + json.dumps(package, ensure_ascii=False) + html[m.end(2):]
    html = html.replace('0050-BETA', '0056-BETA').replace('Prototype 0056.nds', OUT_NAME).replace('Prototype 0050', 'Prototype 0056')
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0056'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0050' not in visible.replace('since 0050', ''), 'stale 0050 label left in the page'
    (out / 'index.html').write_text(html, encoding='utf-8')
    (out / 'manifest.json').write_text(json.dumps(package['manifest'], indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (out / 'READ-ME-FIRST.txt').write_text(READ_ME.replace('{sha}', new_sha), encoding='utf-8')
    # development logs: append the entry to the releases copy and to the workshop's own (both keep their large bodies untouched)
    for log in (rel / 'DEVELOPMENT-LOG.md', Path(workshop) / 'psyduck-yellow' / 'DEVELOPMENT-LOG.md'):
        text = log.read_text(encoding='utf-8')
        text = re.sub(r'\*\*Last updated: [^*]*\.\*\*', f'**Last updated: {DATE}.**', text, count=1)
        log.write_text(text + LOG_ENTRY, encoding='utf-8')
    # plain-language README of the releases repository
    readme = (rel / 'README.md').read_text(encoding='utf-8')
    readme = readme.replace('prototype 0050 BETA', 'prototype 0056 BETA')
    readme = readme.replace('(**prototype 0050 BETA**)', '(**prototype 0056 BETA**)')
    readme = re.sub(r'\[hosted prototype 0056 BETA patching page\]\([^)]*\)', f'[hosted prototype 0056 BETA patching page]({PAGE})', readme)
    readme = readme.replace("- **Not built yet:**", "- **New in 0056:** the Pokédex opens on Kanto (1-151) with real National numbers for the starter Pokémon; TM34 is Moonblast and TM58 is Dazzling Gleam.\n- **Not built yet:**", 1)
    assert 'prototype 0056 BETA patching page' in readme and 'New in 0056' in readme, 'README not updated'
    entry = (f'- **0056 BETA — {DATE} (pre-release, testing only).** Pokédex opens on Kanto with real National numbers for the starters; Moonblast and Dazzling Gleam TMs; Fairy-move fixes. Kanto only; Johto not ready.\n')
    marker = '## Release history (newest first)\n'
    assert marker in readme
    readme = readme.replace(marker, marker + entry)
    (rel / 'README.md').write_text(readme, encoding='utf-8')
    (rel.parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha), encoding='utf-8')
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch, 'out_name': OUT_NAME}))


if __name__ == '__main__':
    main(*sys.argv[1:6])
