"""Build the public prototype-0110 BETA release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

Same layout as build_release_0105.py: a self-contained prototype-0110 folder (the four older patch stages, the new final stage 0039 art -> 0110, the page, manifest and read-me),
the repository README and the development log. The page is derived from prototype-0105's. Two differences from the earlier builders: the output name is normalised (the 0042-0105 pages
repeat "Psyduck Yellow " in the download name), and only labels are replaced, never bare numbers (the HeartGold USA file's SHA-256 itself ends in 0105).
The finished ROM the page hands out is named "Psyduck Yellow Prototype 0110.nds". The workshop's own development log is not touched (only the releases copy).

Usage: build_release_0110.py <releases-repo clone> <0039-art-to-0110.xdelta> <0039 art ROM> <0110 ROM>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 28, 2026'
VERSION = '0110-BETA'
FOLDER, PREVIOUS = 'prototype-0110', 'prototype-0105'
PAGE = f'https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/{FOLDER}/index.html'
OUT_NAME = 'Psyduck Yellow Prototype 0110.nds'
PATCH_NAME = '0039-art-to-0110.xdelta'

BLURB = ('<p><strong>Prototype 0110 — BETA PRE-RELEASE.</strong> Still the Kanto campaign from Pallet Town to the first Hall of Fame. New since 0105: '
         'the <strong>VS banners</strong> show each trainer\'s own name (the Elite Four and Champion Blue), <strong>Strength works with Kanto badges</strong>, '
         '<strong>Victory Road</strong> has real Strength boulders, visible switches and Yellow\'s puzzle (push a boulder onto the first switch on 2F to open the way), '
         'and <strong>Novareon</strong> counts on the Trainer Card.</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Cerulean on earlier builds and is starting a full playthrough with this one. '
         'Everything after Cerulean has only been checked in small emulator tests, not played through. '
         'Expect bugs, including possible softlocks. <strong>Known:</strong> one freeze was reported when arriving in Cerulean after Route 25 (not reproduced yet; it may have involved an old renamed save).</p>'
         '<p><strong>Johto is not ready. Do not go there.</strong> After the Hall of Fame the Route 22 gate opens a path toward Johto; do not take it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

NEW_IN_0110 = [
    '**VS banners** now show the real trainer: the Elite Four (Lorelei, Bruno, Agatha, Lance) and Champion Blue each have their own name (Champion Blue used to read GIOVANNI).',
    '**Novareon** now counts in the Pokédex number on the Trainer Card.',
    '**Strength** works with Kanto badges: the Rainbow Badge (or the Plain Badge) is enough, both in the party menu and on boulders. Before, a player with only Kanto badges could never use it.',
    '**Victory Road:** the puzzle boulders are real Strength boulders (they were Rock Smash rocks), the switches and the 3F hole are drawn, and the barriers sit where Yellow\'s do. With Strength (HM04 from the Warden in Fuchsia) and the Rainbow Badge, push a boulder onto the first switch on 2F to open the way, as in Yellow. The boulder that blocks the main route on 2F cannot be pushed.',
]

READ_ME = f'''Pokemon Psyduck Yellow - prototype 0110 BETA PRE-RELEASE - {DATE}

*** BETA PRE-RELEASE, FOR TESTING ONLY. NOT A COMPLETE GAME. ***
Only the Kanto campaign, up to your first Hall of Fame induction, has been developed.
JOHTO IS NOT READY. DO NOT GO THERE. After the Hall of Fame, the gate on Route 22 opens a path toward Johto - do not take it.

HOW TO PLAY
1. Open the patching page: {PAGE}
2. Choose your OWN, original, unmodified USA HeartGold .nds file (not another prototype).
3. Click "Create my playable NDS", wait for the checks to finish, then download the result ("{OUT_NAME}") and load it in your DS emulator.
4. Start a NEW GAME. Saves from older prototypes do not work (a renamed old save may behave strangely). Keep this build and its saves separate, and never reuse emulator save states between versions.
Nothing is uploaded; the patching happens in your browser and every step is hash-checked. Expected final SHA256: {{sha}}

WHAT IS NEW SINCE 0105
''' + '\n'.join('- ' + x.replace('**', '') for x in NEW_IN_0110) + '''
- Everything from 0105 is still here.

WHAT HAS BEEN TESTED
- The developer has played New Game through Cerulean on earlier builds and is starting a full playthrough with this one.
- Everything after Cerulean has only had small emulator checks on prepared test saves: each rebuilt area was entered, one reward and one battle checked, and the exit used; all 587 maps were entered once without a crash (last swept on build 0104); the Pokedex was opened for sample entries of every generation.
- Since 0105, on prepared saves with only Kanto badges: the trash-can switches in Vermilion Gym, the warp pads in Saffron Gym and the hidden walls in Fuchsia Gym were walked through to their leaders; Cut, Surf, Strength, the Route 23 guard and the Saffron guards were used; Victory Road's 2F puzzle was solved with a real Strength Pokemon and the road walked to Indigo Plateau, and the 1F switch and barrier were tested. Victory Road 3F's switch and the Safari Zone chain (Gold Teeth, Surf, Strength) and the Mansion in order have not been played through by hand.

NOT BUILT YET
Elevator floor-selection menus in Silph Co. and Rocket Hideout (the floors are joined by stairs instead); some of the rebuilt interiors still use stand-in wall and floor textures; Game Corner and Department Store extras. Novareon's stats, ability and moves are placeholders; every Eeveelution Mega uses Mega Eevee's shape.

KNOWN ISSUES
One freeze was reported when arriving in Cerulean (from Nugget Bridge, or by Fly) after fighting a Route 25 trainer who blocked the path; walking up from Vermilion worked. Not reproduced yet; the save involved may have been an old renamed one.
In the emulator used for testing (DeSmuME), item balls, rocks and boulders are not drawn while you stand directly south of them (they stay solid and come back when you step away). The same happens on the previous prototype and in HeartGold's own maps; it may look different in your emulator.
Fuchsia Gym's leader is still HeartGold's Janine (with Koga's Yellow team and her own lines), and Sabrina gives HeartGold's TM48 instead of Yellow's TM46.
Oak's complete-Pokedex check may still expect 256 species. Novareon's follower is a recolored Umbreon placeholder. The Forms page of a few Pokemon shows the species name twice.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data from pret/pokeyellow.
'''

LOG_ENTRY = f'''

## {DATE} — prototype 0110 (BETA pre-release)

**BETA PRE-RELEASE, FOR TESTING ONLY. Not a complete game. Only the Kanto campaign, up to the first Hall of Fame, has been developed. Johto is NOT ready — do not go there.**

[Create prototype 0110]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded. The finished game is named "{OUT_NAME}".

What changed since 0105 (internal builds 0106–0110):
''' + '\n'.join('- ' + x for x in NEW_IN_0110) + '''
- Not changed: the save layout and Johto.

Reported, not fixed: a freeze when arriving in Cerulean after Route 25 (not reproduced). Checked: small emulator tests on prepared saves, the puzzles of the Vermilion, Saffron and Fuchsia gyms, and Victory Road's 1F and 2F puzzles (see the read-me).
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

## What's new since 0105
''' + '\n'.join('- ' + x for x in NEW_IN_0110) + '''

## How much has been tested
The developer has played New Game through **Cerulean** on earlier builds and is starting a full playthrough with this one. Everything after that has only had small emulator checks on prepared test saves. Expect bugs, including possible softlocks.

## Known issues
A freeze was reported when arriving in Cerulean after a blocked Route 25 (not reproduced; may involve an old renamed save). In the test emulator (DeSmuME), item balls, rocks and boulders are not drawn while you stand directly south of them (same on the previous prototype and in HeartGold's own maps). Fuchsia Gym's leader is still Janine with Koga's team. Elevators are stairs for now. Novareon's stats are placeholders.

Files below: the patch stage for this version, the manifest (hashes) and a plain-text read-me. Expected final SHA256: `{{sha}}`
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main(releases, delta, art_rom, new_rom):
    rel = Path(releases)
    old, out = rel / PREVIOUS, rel / FOLDER
    out.mkdir(exist_ok=True)
    shutil.copyfile(delta, out / PATCH_NAME)
    for name in ('HG-ENGINE-CREDITS.md', 'LICENSE.txt'):
        shutil.copyfile(old / name, out / name)
    html = (old / 'index.html').read_text(encoding='utf-8')
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
    source_sha = package['manifest']['source_sha256']
    package['manifest'] = dict(version=VERSION, source_sha256=source_sha,
                               source_bytes=package['manifest']['source_bytes'], output_sha256=new_sha, output_bytes=size_new,
                               output_name=OUT_NAME, cumulative=True, roundtrip_verified=True,
                               status='BETA PRE-RELEASE for testing only: Kanto through the first Hall of Fame; Johto not ready; owner-played to Cerulean only',
                               browser_patch_stages=[{'url': s['url'], 'bytes': s['bytes'], 'sha256': s['manifest']['patch_sha256']} for s in stages])
    package['patchURL'], package['patchBytes'] = PATCH_NAME, size_patch
    html = html[:m.start(2)] + json.dumps(package, ensure_ascii=False) + html[m.end(2):]
    html = html.replace('0105-BETA', VERSION)
    html = re.sub(r'(?:Psyduck Yellow )+Prototype 0105\.nds', OUT_NAME, html)
    html = html.replace('Prototype 0105', 'Prototype 0110')
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0110'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0105' not in visible.replace('since 0105', ''), 'stale 0105 label left in the page'
    assert html.count('Psyduck Yellow Psyduck') == 0 and html.count(OUT_NAME) >= 2, 'download name not normalised'
    assert source_sha in html, 'HeartGold source hash lost'
    (out / 'index.html').write_text(html, encoding='utf-8')
    (out / 'manifest.json').write_text(json.dumps(package['manifest'], indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (out / 'READ-ME-FIRST.txt').write_text(READ_ME.replace('{sha}', new_sha), encoding='utf-8')
    log = rel / 'DEVELOPMENT-LOG.md'                       # the releases copy only
    text = log.read_text(encoding='utf-8')
    text = re.sub(r'\*\*Last updated: [^*]*\.\*\*', f'**Last updated: {DATE}.**', text, count=1)
    log.write_text(text + LOG_ENTRY, encoding='utf-8')
    # plain-language README of the releases repository
    readme = (rel / 'README.md').read_text(encoding='utf-8')
    readme = readme.replace('prototype 0105 BETA', 'prototype 0110 BETA')
    played_old = '- **Played by the developer:** New Game through Vermilion. Everything after that has only had small emulator tests, so expect bugs, including softlocks.'
    played_new = '- **Played by the developer:** New Game through Cerulean on earlier builds; a full playthrough with prototype 0110 is starting. Everything after Cerulean has only had small emulator tests, so expect bugs, including softlocks.'
    assert readme.count(played_old) == 1, 'README played-by line changed'
    readme = readme.replace(played_old, played_new)
    readme = re.sub(r'\[hosted prototype 0110 BETA patching page\]\([^)]*\)', f'[hosted prototype 0110 BETA patching page]({PAGE})', readme)
    new_line = ("- **New in 0110:** the VS banners name the Elite Four and Champion Blue, Strength works with Kanto badges, Victory Road has real boulders, visible switches and Yellow's first-switch puzzle on 2F, and Novareon counts on the Trainer Card.\n")
    marker_line = '- **Not built yet:**'
    assert readme.count(marker_line) == 1 and 'New in 0105' in readme
    readme = readme.replace(marker_line, new_line + marker_line)
    assert 'prototype 0110 BETA patching page' in readme and 'New in 0110' in readme, 'README not updated'
    entry = (f'- **0110 BETA — {DATE} (pre-release, testing only).** The VS banners name the Elite Four and Champion Blue, Strength works with Kanto badges, Victory Road has real Strength boulders, visible switches and Yellow’s puzzle, and Novareon counts on the Trainer Card. Kanto only; Johto not ready.\n')
    marker = '## Release history (newest first)\n'
    assert marker in readme
    readme = readme.replace(marker, marker + entry)
    (rel / 'README.md').write_text(readme, encoding='utf-8')
    (rel.parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha), encoding='utf-8')
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch, 'out_name': OUT_NAME}))


if __name__ == '__main__':
    main(*sys.argv[1:5])
