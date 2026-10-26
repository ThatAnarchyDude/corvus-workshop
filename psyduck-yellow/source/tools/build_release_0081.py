"""Build the public prototype-0081 BETA release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

The release folder is self-contained: it copies the older patch stages the page chains through from prototype-0042, adds the new
final stage (0039 art -> 0050), and rewrites the page, manifest, read-me, the repository README and the development log.
The finished ROM the page hands out is named "Psyduck Yellow Prototype 0081.nds".

Usage: build_release_0050.py <releases-repo clone> <0039-art-to-0081.xdelta> <0039 art ROM> <0050 ROM> <corvus-workshop clone (its DEVELOPMENT-LOG.md is appended to)>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 24, 2026'
VERSION = '0081-BETA'
FOLDER = 'prototype-0081'
PAGE = f'https://raw.githack.com/ThatAnarchyDude/Psyduck-Yellow-Releases/main/{FOLDER}/index.html'
OUT_NAME = 'Psyduck Yellow Prototype 0081.nds'
PATCH_NAME = '0039-art-to-0081.xdelta'

BLURB = ('<p><strong>Prototype 0081 — BETA PRE-RELEASE.</strong> Still the Kanto campaign from Pallet Town to the first Hall of Fame. New since 0056: '
         '<strong>Novareon has its own Pokédex entry</strong> (No. 1026) and follower, <strong>Mega Novareon</strong> has its own battle art, the <strong>Champion is now Blue</strong> '
         '(not Lance), several <strong>trainer-team and text bugs are fixed</strong> (Celadon Game Corner, Silph Co. exit, Celadon/Saffron/Viridian gym trainers), '
         'and Silph Co., Pokémon Tower, the Rocket Hideout and Victory Road have their <strong>item balls</strong>; <strong>Moltres</strong> waits on Victory Road 2F.</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Vermilion. Everything after that, including all the '
         'new work in this release, has only been checked in small emulator tests on prepared saves, not played through. Expect bugs, including possible softlocks.</p>'
         '<p><strong>Johto is not ready. Do not go there.</strong> After the Hall of Fame the Route 22 gate opens a path toward Johto; do not take it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

NEW_IN_0050 = [
    '**Bug fixes:** 17 trainer records were read with the wrong party size, so some Celadon, Saffron and Viridian Gym trainers had garbage second Pokémon (a Celadon Gym trainer\'s second Pokémon was a Lv77 Rapidash); the Celadon Game Corner\'s own NPCs read garbage text; leaving the first Silph Co. floor by its door dropped the player into a black "Mystery Zone".',
    '**Champion Blue:** the League\'s Champion room now shows Blue (rival class and name, rival sprite, Yellow\'s lines) instead of HeartGold\'s Lance. The whole League was played end to end on a test warp: Champion fight, Hall of Fame, save prompt.',
    '**Item balls** from Yellow in Silph Co. (12), the Pokémon Tower (7), the Rocket Hideout (8) and Victory Road (5), and **Moltres** (Lv50) on Victory Road 2F. Yellow\'s TM balls that have no TM in this game are left out.',
    '**Novareon:** its own Pokédex entry (National No. 1026, "Star Chart Pokémon", entry text from the design document), its own follower, a blue party icon, and Mega Novareon with new battle sprites (a rainbow disk tail behind the body). Novareonite and Eonite have their own descriptions.',
    '**New icons:** Psyduckite and Novareonite in the engine\'s Mega Stone style, a new Sandwich icon (a low sub).',
    '**Pokédex and Summary:** the Pokédex opens on the Kanto list and Oak\'s evaluation says Kanto; the Summary\'s Type row shows the STELLAR chip in correct (violet and pink) colors; each Eeveelution Mega has its own color accent.',
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

WHAT IS NEW SINCE 0056
- Bug fixes: 17 trainer records were read with the wrong party size (some Celadon, Saffron and Viridian Gym trainers had garbage second Pokemon); the Celadon Game Corner NPCs read garbage text; leaving the first Silph Co. floor by its door dropped you into a black "Mystery Zone".
- Champion Blue: the Champion room shows Blue (rival name, sprite, Yellow's lines) instead of Lance.
- Item balls from Yellow in Silph Co., the Pokemon Tower, the Rocket Hideout and Victory Road; Moltres (Lv50) on Victory Road 2F.
- Novareon: its own Pokedex entry (No. 1026), follower, blue party icon; Mega Novareon has new battle sprites; new Mega Stone and Sandwich icons and descriptions.
- Pokedex opens on Kanto and Oak's evaluation says Kanto; the Summary's STELLAR chip has correct colors; each Eeveelution Mega has its own color accent.
- Everything from 0056 is still here.

WHAT HAS BEEN TESTED
- The developer has played New Game through Vermilion (including the Pewter and Cerulean gyms and Mega Evolution).
- Everything after that has only had small emulator checks on prepared test saves. For this release: item pickups in each of the four dungeon sets, Moltres' battle start, the Champion fight through the Hall of Fame and the save prompt, a Celadon Gym trainer's corrected team, the Game Corner guard, the Silph exit, Novareon's Pokedex pages and follower, Mega Novareon's sprites in battle, and the new icons in the bag. Static checks of every warp, message, script reference, trainer party and wild encounter table pass. Winning the League has NOT been played on a real save.

NOT BUILT YET
Silph Co. Card Key doors and the Take Down TM; Victory Road's Sky Attack, Submission and Mega Kick TMs and its boulder switches; the Safari Zone and Gold Teeth (a Warden in Fuchsia gives Strength and Surf instead); the Cinnabar Mansion; Game Corner and Department Store extras; some of Yellow's extra gym trainers. Novareon's stats, ability and moves are placeholders; every Eeveelution Mega uses Mega Eevee's shape.

KNOWN ISSUES
The top screen went black once after leaving Viridian Forest by the north exit; saving and reloading fixed it. Not investigated yet.
The Sandwich's bag description shows another map's text. The VS banner under Champion Blue reads GIOVANNI. The Hall of Fame walk-in still has Lance narrating. The Pokedex "seen/obtained" totals skip Novareon. Oak's complete-Pokedex check may still expect 256 species. Novareon's follower is a recolored Umbreon placeholder.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data and dialogue are referenced from pret/pokeyellow; Novareon artwork from the developer's own sprite library. Unofficial fan project, not affiliated with Nintendo, Game Freak, Creatures or The Pokemon Company.
'''

LOG_ENTRY = f'''

## {DATE} — prototype 0081 (BETA pre-release)

**BETA PRE-RELEASE, FOR TESTING ONLY. Not a complete game. Only the Kanto campaign, up to the first Hall of Fame, has been developed. Johto is NOT ready — do not go there.**

[Create prototype 0081]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded. The finished game is named "{OUT_NAME}".

What changed since 0056 (internal builds 0057–0081):
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''
- Under the hood: Novareon's Pokédex identity is the unused species id 500 (the SIZE page breaks above id 1075); the Summary's type-chip drawing code uses a spare chip for Stellar; trainer type bytes now match their parties; static audits (tools/audit_*.py) and an emulator smoke test of the new maps are in the source.
- Not changed: the save layout and Johto.

Checked: small emulator tests on prepared saves (see the read-me). Not checked: a real-save League win.
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

## What's new since 0056
''' + '\n'.join('- ' + x for x in NEW_IN_0050) + '''

## How much has been tested
The developer has played New Game through **Vermilion**. Everything after that, including all of the above, has only had small emulator checks on prepared test saves. Expect bugs, including possible softlocks.

## Not built yet
Silph Co. Card Key doors and Take Down TM · Victory Road TMs and boulder switches · Safari Zone / Gold Teeth (a Warden gives Strength and Surf instead) · Cinnabar Mansion · some of Yellow's extra gym trainers · real Novareon stats

## Known issues
The top screen went black once after leaving Viridian Forest (saving and reloading fixed it). The Sandwich's bag description shows another map's text; the VS banner under Champion Blue reads GIOVANNI; the Hall of Fame walk-in still has Lance narrating.

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
    html = (rel / 'prototype-0056' / 'index.html').read_text(encoding='utf-8')
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
    html = html.replace('0056-BETA', '0081-BETA').replace('Prototype 0056.nds', OUT_NAME).replace('Prototype 0056', 'Prototype 0081')
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0081'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0056' not in visible.replace('since 0056', ''), 'stale 0056 label left in the page'
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
    readme = readme.replace('prototype 0056 BETA', 'prototype 0081 BETA')
    readme = readme.replace('(**prototype 0056 BETA**)', '(**prototype 0081 BETA**)')
    readme = re.sub(r'\[hosted prototype 0081 BETA patching page\]\([^)]*\)', f'[hosted prototype 0081 BETA patching page]({PAGE})', readme)
    readme = readme.replace("- **Not built yet:**", "- **New in 0081:** Novareon's own Pokédex entry and follower, Mega Novareon art, Champion Blue, item balls in Silph Co., the Tower, the Rocket Hideout and Victory Road, Moltres, and fixes for trainer teams, the Game Corner and the Silph exit.\n- **Not built yet:**", 1)
    assert 'prototype 0081 BETA patching page' in readme and 'New in 0081' in readme, 'README not updated'
    entry = (f'- **0081 BETA — {DATE} (pre-release, testing only).** Novareon Pokédex entry/follower, Mega Novareon art, Champion Blue, dungeon item balls and Moltres, trainer-team/Game Corner/Silph fixes. Kanto only; Johto not ready.\n')
    marker = '## Release history (newest first)\n'
    assert marker in readme
    readme = readme.replace(marker, marker + entry)
    (rel / 'README.md').write_text(readme, encoding='utf-8')
    (rel.parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha), encoding='utf-8')
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch, 'out_name': OUT_NAME}))


if __name__ == '__main__':
    main(*sys.argv[1:6])
