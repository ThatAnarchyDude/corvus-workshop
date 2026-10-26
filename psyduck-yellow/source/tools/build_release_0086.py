"""Build the public prototype-0086 BETA release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

The release folder is self-contained: it copies the older patch stages the page chains through from prototype-0042, adds the new
final stage (0039 art -> 0050), and rewrites the page, manifest, read-me, the repository README and the development log.
The finished ROM the page hands out is named "Psyduck Yellow Prototype 0086.nds".

Usage: build_release_0086.py <releases-repo clone> <0039-art-to-0086.xdelta> <0039 art ROM> <0086 ROM> <corvus-workshop clone (its DEVELOPMENT-LOG.md is appended to)>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 24, 2026'
VERSION = '0086-BETA'
FOLDER = 'prototype-0086'
PAGE = f'https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/{FOLDER}/index.html'
OUT_NAME = 'Psyduck Yellow Prototype 0086.nds'
PATCH_NAME = '0039-art-to-0086.xdelta'

BLURB = ('<p><strong>Prototype 0086 — BETA PRE-RELEASE.</strong> Still the Kanto campaign from Pallet Town to the first Hall of Fame. New since 0081: '
         'the <strong>Pokémon Tower is recolored</strong> in dark violet stone, the <strong>Hall of Fame</strong> speech is Yellow\'s Oak (not Lance), several <strong>trainers use the right sprites</strong>, '
         'the <strong>Sandwich</strong> has its own bag description, and a Route 25 trainer no longer blocks the path.</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Cerulean. Everything after that has only been checked in small emulator tests on prepared saves, not played through. '
         'Expect bugs, including possible softlocks. <strong>Known:</strong> one freeze was reported when arriving in Cerulean after Route 25 (not reproduced yet; it may have involved an old renamed save).</p>'
         '<p><strong>Johto is not ready. Do not go there.</strong> After the Hall of Fame the Route 22 gate opens a path toward Johto; do not take it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

NEW_IN_0050 = [
    '**Route 25:** the mid-route Camper (in the alcove) now spots you one tile later, so he no longer walks out early and stops you in a gap between the trees.',
    '**Pokémon Tower:** all seven floors use a recolored copy of the Bell Tower interior textures (dark violet stone instead of brown wood). Layouts are still the Bell Tower\'s; pillars and lamps keep their old colors.',
    '**Hall of Fame:** the speech is Yellow\'s Oak ("Er-hem! Congratulations...") instead of HeartGold\'s Lance (the Johto postgame shares this room text for now).',
    '**Trainer sprites:** nine Bug Catchers, a Youngster, a Hiker and a Super Nerd now use the sprite that matches their class.',
    '**Sandwich:** its bag description is now its own ("A hearty sandwich that makes certain Eevee evolve.") instead of another text\'s line.',
]

READ_ME = f'''Pokemon Psyduck Yellow - prototype 0086 BETA PRE-RELEASE - {DATE}

*** BETA PRE-RELEASE, FOR TESTING ONLY. NOT A COMPLETE GAME. ***
Only the Kanto campaign, up to your first Hall of Fame induction, has been developed.
JOHTO IS NOT READY. DO NOT GO THERE. After the Hall of Fame, the gate on Route 22 opens a path toward Johto - do not take it.

HOW TO PLAY
1. Open the patching page: {PAGE}
2. Choose your OWN, original, unmodified USA HeartGold .nds file (not another prototype).
3. Click "Create my playable NDS", wait for the checks to finish, then download the result ("{OUT_NAME}") and load it in your DS emulator.
4. Start a NEW GAME. Saves from older prototypes do not work (a renamed old save may behave strangely). Keep this build and its saves separate, and never reuse emulator save states between versions.
Nothing is uploaded; the patching happens in your browser and every step is hash-checked. Expected final SHA256: {{sha}}

WHAT IS NEW SINCE 0081
- Route 25: the mid-route Camper spots you one tile later, so he no longer blocks the gap between the trees.
- Pokemon Tower: all seven floors use dark violet stone textures (layout is still the Bell Tower's; pillars and lamps keep their old colors).
- Hall of Fame: Yellow's Oak speech instead of Lance.
- Trainer sprites: nine Bug Catchers, a Youngster, a Hiker and a Super Nerd use the sprite that matches their class.
- Sandwich: its own bag description.
- Everything from 0081 is still here.

WHAT HAS BEEN TESTED
- The developer has played New Game through Cerulean and found the Camper problem and a freeze (below).
- Everything after Cerulean has only had small emulator checks on prepared test saves. For this release: the Camper's sight (old versus new), the Tower floors on screen, the Sandwich text in the bag, a Bug Catcher fight after the sprite change; the Hall of Fame text was audited but not watched in-game. Static checks of every message pass.

NOT BUILT YET
Silph Co. Card Key doors and the Take Down TM; Victory Road's Sky Attack, Submission and Mega Kick TMs and its boulder switches; the Safari Zone and Gold Teeth (a Warden in Fuchsia gives Strength and Surf instead); the Cinnabar Mansion; Game Corner and Department Store extras; some of Yellow's extra gym trainers. Pokemon Tower is not laid out like Yellow's yet. Novareon's stats, ability and moves are placeholders; every Eeveelution Mega uses Mega Eevee's shape.

KNOWN ISSUES
One freeze was reported when arriving in Cerulean (from Nugget Bridge, or by Fly) after fighting a Route 25 trainer who blocked the path; walking up from Vermilion worked. Not reproduced yet; the save involved may have been an old renamed one.
The VS banner under Champion Blue reads GIOVANNI. The Pokedex "seen/obtained" totals skip Novareon. Oak's complete-Pokedex check may still expect 256 species. Novareon's follower is a recolored Umbreon placeholder. The top screen went black once after leaving Viridian Forest by the north exit.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data and dialogue are referenced from pret/pokeyellow; Novareon artwork from the developer's own sprite library. Unofficial fan project, not affiliated with Nintendo, Game Freak, Creatures or The Pokemon Company.
'''

LOG_ENTRY = f'''

## {DATE} — prototype 0086 (BETA pre-release)

**BETA PRE-RELEASE, FOR TESTING ONLY. Not a complete game. Only the Kanto campaign, up to the first Hall of Fame, has been developed. Johto is NOT ready — do not go there.**

[Create prototype 0086]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded. The finished game is named "{OUT_NAME}".

What changed since 0081 (internal builds 0082–0086):
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''
- Not changed: the save layout and Johto.

Reported, not fixed: a freeze when arriving in Cerulean after Route 25 (not reproduced). Checked: small emulator tests on prepared saves (see the read-me).
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

## What's new since 0081
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''

## How much has been tested
The developer has played New Game through **Cerulean**. Everything after that has only had small emulator checks on prepared test saves. Expect bugs, including possible softlocks.

## Known issues
A freeze was reported when arriving in Cerulean after a blocked Route 25 (not reproduced; may involve an old renamed save). The VS banner under Champion Blue reads GIOVANNI. Pokemon Tower is recolored but not laid out like Yellow's. Novareon's stats are placeholders.

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
    html = (rel / 'prototype-0081' / 'index.html').read_text(encoding='utf-8')
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
    html = html.replace('0081-BETA', '0086-BETA').replace('Prototype 0081.nds', OUT_NAME).replace('Prototype 0081', 'Prototype 0086')
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0086'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0081' not in visible.replace('since 0081', ''), 'stale 0081 label left in the page'
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
    readme = readme.replace('prototype 0081 BETA', 'prototype 0086 BETA')
    readme = re.sub(r'\[hosted prototype 0086 BETA patching page\]\([^)]*\)', f'[hosted prototype 0086 BETA patching page]({PAGE})', readme)
    readme = readme.replace("- **Not built yet:**", "- **New in 0086:** a recolored Pokémon Tower, Yellow's Oak speech in the Hall of Fame, corrected trainer sprites, the Sandwich's bag description, and a Route 25 trainer who no longer blocks the path.\n- **Not built yet:**", 1)
    assert 'prototype 0086 BETA patching page' in readme and 'New in 0086' in readme, 'README not updated'
    entry = (f'- **0086 BETA — {DATE} (pre-release, testing only).** Recolored Pokémon Tower, Oak’s Hall of Fame speech, trainer sprite fixes, Sandwich description, Route 25 Camper sight. Kanto only; Johto not ready.\n')
    marker = '## Release history (newest first)\n'
    assert marker in readme
    readme = readme.replace(marker, marker + entry)
    (rel / 'README.md').write_text(readme, encoding='utf-8')
    (rel.parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha), encoding='utf-8')
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch, 'out_name': OUT_NAME}))


if __name__ == '__main__':
    main(*sys.argv[1:6])
