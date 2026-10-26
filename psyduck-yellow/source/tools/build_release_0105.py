"""Build the public prototype-0105 BETA release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

The release folder is self-contained: it copies the older patch stages the page chains through from prototype-0042, adds the new
final stage (0039 art -> 0105), and rewrites the page, manifest, read-me, the repository README and the development log.
The finished ROM the page hands out is named "Psyduck Yellow Prototype 0105.nds".

Usage: build_release_0105.py <releases-repo clone> <0039-art-to-0105.xdelta> <0039 art ROM> <0105 ROM> <corvus-workshop clone (its DEVELOPMENT-LOG.md is appended to)>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 26, 2026'
VERSION = '0105-BETA'
FOLDER = 'prototype-0105'
PAGE = f'https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/{FOLDER}/index.html'
OUT_NAME = 'Psyduck Yellow Prototype 0105.nds'
PATCH_NAME = '0039-art-to-0105.xdelta'

BLURB = ('<p><strong>Prototype 0105 — BETA PRE-RELEASE.</strong> Still the Kanto campaign from Pallet Town to the first Hall of Fame. New since 0086: '
         'the <strong>Pokémon Tower</strong>, <strong>Mt. Moon</strong>, <strong>Rock Tunnel</strong>, <strong>Rocket Hideout</strong>, <strong>Silph Co.</strong>, the <strong>Pokémon Mansion</strong>, <strong>Viridian Gym</strong>, <strong>Victory Road</strong> and the <strong>Safari Zone</strong> are rebuilt from Yellow\'s own maps with their puzzles, plus a fix for a black screen in Vermilion\'s Pokémon Center and a Pokédex registration fix.</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Cerulean. Everything after that has only been checked in small emulator tests, not played through. '
         'Expect bugs, including possible softlocks. <strong>Known:</strong> one freeze was reported when arriving in Cerulean after Route 25 (not reproduced yet; it may have involved an old renamed save).</p>'
         '<p><strong>Johto is not ready. Do not go there.</strong> After the Hall of Fame the Route 22 gate opens a path toward Johto; do not take it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

NEW_IN_0050 = [
    '**Pokémon Tower** is rebuilt to Yellow\'s floor plans (seven floors, trainers, the purified zone, Mr. Fuji\'s rescue scenes).',
    '**Mt. Moon, Rock Tunnel, Rocket Hideout and Silph Co.** are rebuilt from Yellow\'s maps: cave floors roll wild encounters, the Hideout has its spin-tile mazes and Lift Key, Silph Co. has 11 floors with Card Key doors.',
    '**Pokémon Mansion** (four floors, statue switches and gates, holes, diaries) and its Secret Key, which opens the Cinnabar Gym door.',
    '**Viridian Gym** has Yellow\'s layout, spin tiles and all eight trainers. **Victory Road** has Yellow\'s three floors with boulder switches.',
    '**Safari Zone** (four areas, wild Pokémon, items), the Gold Teeth, the Fishing Guru\'s Surf and the Warden\'s Strength swap in Fuchsia.',
    '**Fix:** Vermilion\'s Pokémon Center and two houses no longer show a black screen (an invalid character sprite).',
    '**Pokédex:** all 1,026 entries were checked; registering a Pokémon from No. 650 onward no longer wipes the "seen" marks of other entries.',
]

READ_ME = f'''Pokemon Psyduck Yellow - prototype 0105 BETA PRE-RELEASE - {DATE}

*** BETA PRE-RELEASE, FOR TESTING ONLY. NOT A COMPLETE GAME. ***
Only the Kanto campaign, up to your first Hall of Fame induction, has been developed.
JOHTO IS NOT READY. DO NOT GO THERE. After the Hall of Fame, the gate on Route 22 opens a path toward Johto - do not take it.

HOW TO PLAY
1. Open the patching page: {PAGE}
2. Choose your OWN, original, unmodified USA HeartGold .nds file (not another prototype).
3. Click "Create my playable NDS", wait for the checks to finish, then download the result ("{OUT_NAME}") and load it in your DS emulator.
4. Start a NEW GAME. Saves from older prototypes do not work (a renamed old save may behave strangely). Keep this build and its saves separate, and never reuse emulator save states between versions.
Nothing is uploaded; the patching happens in your browser and every step is hash-checked. Expected final SHA256: {{sha}}

WHAT IS NEW SINCE 0086
''' + '\n'.join('- ' + x.replace('**', '') for x in NEW_IN_0050) + '''
- Everything from 0086 is still here.

WHAT HAS BEEN TESTED
- The developer has played New Game through Cerulean.
- Everything after Cerulean has only had small emulator checks on prepared test saves: each rebuilt area was entered, one reward and one battle checked, and the exit used; all 587 maps were entered once without a crash; the Pokedex was opened for sample entries of every generation. The Safari Zone chain (Gold Teeth, Surf, Strength), the Mansion in order and the boulder switches with a real Strength Pokemon have not been played through by hand.

NOT BUILT YET
Elevator floor-selection menus in Silph Co. and Rocket Hideout (the floors are joined by stairs instead); some of the rebuilt interiors still use stand-in wall and floor textures; Game Corner and Department Store extras. Novareon's stats, ability and moves are placeholders; every Eeveelution Mega uses Mega Eevee's shape.

KNOWN ISSUES
One freeze was reported when arriving in Cerulean (from Nugget Bridge, or by Fly) after fighting a Route 25 trainer who blocked the path; walking up from Vermilion worked. Not reproduced yet; the save involved may have been an old renamed one.
The VS banner under Champion Blue reads GIOVANNI. Oak's complete-Pokedex check may still expect 256 species. Novareon's follower is a recolored Umbreon placeholder. The Forms page of a few Pokemon shows the species name twice.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data from pret/pokeyellow.
'''

LOG_ENTRY = f'''

## {DATE} — prototype 0105 (BETA pre-release)

**BETA PRE-RELEASE, FOR TESTING ONLY. Not a complete game. Only the Kanto campaign, up to the first Hall of Fame, has been developed. Johto is NOT ready — do not go there.**

[Create prototype 0105]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded. The finished game is named "{OUT_NAME}".

What changed since 0086 (internal builds 0087–0105):
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''
- Not changed: the save layout and Johto.

Reported, not fixed: a freeze when arriving in Cerulean after Route 25 (not reproduced). Checked: small emulator tests on prepared saves and a sweep of all 587 maps (see the read-me).
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

## What's new since 0086
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''

## How much has been tested
The developer has played New Game through **Cerulean**. Everything after that has only had small emulator checks on prepared test saves. Expect bugs, including possible softlocks.

## Known issues
A freeze was reported when arriving in Cerulean after a blocked Route 25 (not reproduced; may involve an old renamed save). The VS banner under Champion Blue reads GIOVANNI. Elevators are stairs for now. Novareon's stats are placeholders.

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
    html = (rel / 'prototype-0086' / 'index.html').read_text(encoding='utf-8')
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
                               status='BETA PRE-RELEASE for testing only: Kanto through the first Hall of Fame; Johto not ready; owner-played to Cerulean only',
                               browser_patch_stages=[{'url': s['url'], 'bytes': s['bytes'], 'sha256': s['manifest']['patch_sha256']} for s in stages])
    package['patchURL'], package['patchBytes'] = PATCH_NAME, size_patch
    html = html[:m.start(2)] + json.dumps(package, ensure_ascii=False) + html[m.end(2):]
    html = html.replace('0086-BETA', '0105-BETA').replace('Prototype 0086.nds', OUT_NAME).replace('Prototype 0086', 'Prototype 0105')
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0105'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0086' not in visible.replace('since 0086', ''), 'stale 0086 label left in the page'
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
    readme = readme.replace('prototype 0086 BETA', 'prototype 0105 BETA')
    readme = re.sub(r'\[hosted prototype 0105 BETA patching page\]\([^)]*\)', f'[hosted prototype 0105 BETA patching page]({PAGE})', readme)
    readme = re.sub(r'- \*\*New in 0086:\*\*[^\n]*\n- \*\*Not built yet:\*\*[^\n]*\n',
                    "- **New in 0105:** Pokémon Tower, Mt. Moon, Rock Tunnel, Rocket Hideout, Silph Co., the Pokémon Mansion, Viridian Gym, Victory Road and the Safari Zone rebuilt from Yellow's maps with their puzzles; a black-screen fix in Vermilion's Pokémon Center; a Pokédex registration fix.\n"
                    "- **Not built yet:** elevator floor menus (stairs for now), some stand-in textures, some Game Corner and Department Store extras, and **all of Johto**.\n", readme, count=1)
    assert 'prototype 0105 BETA patching page' in readme and 'New in 0105' in readme, 'README not updated'
    entry = (f'- **0105 BETA — {DATE} (pre-release, testing only).** Nine Kanto dungeons and gyms rebuilt from Yellow\u2019s maps (Pok\u00e9mon Tower, Mt. Moon, Rock Tunnel, Rocket Hideout, Silph Co., Mansion, Viridian Gym, Victory Road, Safari Zone), a Vermilion black-screen fix and a Pok\u00e9dex fix. Kanto only; Johto not ready.\n')
    marker = '## Release history (newest first)\n'
    assert marker in readme
    readme = readme.replace(marker, marker + entry)
    (rel / 'README.md').write_text(readme, encoding='utf-8')
    (rel.parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha), encoding='utf-8')
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch, 'out_name': OUT_NAME}))


if __name__ == '__main__':
    main(*sys.argv[1:6])
