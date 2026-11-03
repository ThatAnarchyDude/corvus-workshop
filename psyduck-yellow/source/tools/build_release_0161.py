"""Build the public prototype-0161 (BETA 0.1.61) release inside the Psyduck-Yellow-Releases repo (patches and documentation only; never a ROM, save or source).

Same layout as build_release_0110.py: a self-contained prototype-0161 folder (the four older patch stages, the new final stage 0039 art -> 0157, the page, manifest and read-me),
the repository README and the development log. The page is derived from prototype-0110's. Only labels are replaced, never bare numbers.
The finished ROM the page hands out is named "Pokemon Psyduck Yellow BETA 0.1.61.nds" (the owner's own naming). The workshop's own development log is not touched (only the releases copy).

Usage: build_release_0161.py <releases-repo clone> <0039-art-to-0161.xdelta> <0039 art ROM> <0161 ROM>
"""
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

DATE = 'November 3, 2026'
VERSION = '0161-BETA'
LABEL = 'BETA 0.1.61'
FOLDER, PREVIOUS = 'prototype-0161', 'prototype-0110'
OWNER = os.environ.get('RELEASE_OWNER', 'ThatAnarchyDude')       # the account whose Psyduck-Yellow-Releases repo gets this release (the supplied token can only write to Doctor-Pokemon's fork)
PAGE = f'https://raw.githack.com/{OWNER}/Psyduck-Yellow-Releases/main/{FOLDER}/index.html'
OUT_NAME = 'Pokemon Psyduck Yellow BETA 0.1.61.nds'
PATCH_NAME = '0039-art-to-0161.xdelta'
SOURCE_URL = 'https://github.com/Doctor-Pokemon/corvus-workshop/tree/publish-0161/psyduck-yellow/source'   # branch of the owner's second account (the token cannot push to ThatAnarchyDude/corvus-workshop); a pull request proposes it there

NEW_IN_0157 = [
    '**Replaces BETA 0.1.60, 0.1.58 and 0.1.57.** 0.1.57 crashed in battle (the first move you used); 0.1.58 fixed that but its Town Map could still be scrolled into Johto early; 0.1.60 fixed that. 0.1.61 adds the Pokédex change below. Use 0.1.61.',
    '**Pokédex:** a New Game now starts with the Kanto Pokédex (the 151 Kanto Pokémon, no National switch) instead of the National Pokédex. Oak upgrades it to the National Pokédex later, at Mr. Pokémon\'s house in the Johto postgame, as planned.',
    '**Town Map fix:** the Town Map and the Fly map now stay Kanto-only until Elm calls you in Johto, even if your game already set New Bark Town\'s Fly point. Before, walking into Pallet Town set that Fly point at the start of the game, and the lock took it as "Johto unlocked".',
    '**Fly points:** walking into Pallet Town no longer unlocks New Bark Town\'s Fly point, and Pallet Town itself can now be a Fly destination.',
    '**Johto postgame, first parts (unfinished):** after the first Hall of Fame the credits lead back to your room in Pallet Town; Mom hands over the Pokégear if you lack it and Oak gives an S.S. Aqua ticket. The ferry from Vermilion is the only way to Johto (the Route 22 gate, the Magnet Train and Fly stay closed until you arrive). On arrival Elm phones, Fly to New Bark Town unlocks, Elm gives a Johto starter and the Mega Ring, Mr. Pokémon gives the matching Mega Stone, and Oak upgrades the Pokédex to National. All of this has only been checked on prepared saves.',
    '**Johto scales with your Johto badges:** Gym Leaders, Silver and scripted Johto battles use level 60 + 5 per Johto badge; ordinary Johto trainers and wild Pokémon climb from their original level to 100 at eight badges. The Johto League needs all 16 badges and has six level-100 Pokémon per member; Red on Mt. Silver is level 100 with a small stat boost.',
    '**Town Map:** shows only Kanto (opens on Pallet Town, the cursor cannot leave Kanto) until you reach Johto; Johto and the New Bark Town Fly point appear after Elm\'s call.',
    '**Starter line redesigned:** the starter Psyduck evolves with a Moon Stone into the Water/Psychic Golduck; Eevee gets nine new Eeveelutions (Brawleon, Venomeon, Duneon, Zephyreon, Chryseon, Strateon, Wraitheon, Wyrmeon, Ferreon) through stones, Sun/Moon, the Dusk Stone and held items, and the Stellar-type **Stellareon** (the old Novareon, renamed) through the Stellar Sandwich. Every starter-line Pokémon has its own Mega, new battle sprites and icons, and a Pokédex entry (501–509).',
    '**Mega Typhlosion** (with Typhlosionite) for the Johto starter, and the Mega Stones are no longer sold in the Marts.',
    '**Kanto Marts:** one shared badge-based stock in every Kanto Mart; the Viridian Mart now sells Poké Balls (its second vendor used to be attached to a hidden NPC).',
    '**Bedroom:** no item ball any more; the bedroom PC starts with 999 Max Repel, 999 Rare Candy and 999 of each evolution item.',
    '**Rare Candy fix:** using several candies at once now offers the moves learned on the way (the starters never did, for about 50 versions).',
    '**Caves and facilities:** Mt. Moon, Rock Tunnel and Victory Road have ladder art and proper single-block warps, the cave exits glow, Mt. Moon has its blockade, and every rebuilt floor has art on its warps.',
    '**3DS fixes:** a crash in Cerulean (a missing sprite animation) is guarded, Pewter\'s entry script and the Viridian Forest gatehouse NPCs were fixed; the Cerulean fix was confirmed on a real 3DS, the others are untested on hardware.',
    '**Banner:** the title reads "Psyduck Yellow (BETA)" with a Psyduck icon.',
]

BLURB = ('<p><strong>BETA 0.1.61 (prototype 0161) — for testing.</strong> The Kanto campaign from Pallet Town to the first Hall of Fame, plus the <strong>first parts of the Johto postgame</strong>. New since 0110: '
         'the redesigned Eevee/Psyduck starter line (nine new Eeveelutions and Stellareon), the Town Map that shows only Kanto until you reach Johto, the S.S. Aqua trip, Elm, the Mega Ring, difficulty that scales with the Johto badges, '
         'the Johto League and Red, shared Kanto Mart stock, a Rare Candy fix and 3DS crash fixes.</p>'
         '<p><strong>How much has been played:</strong> the developer has played New Game through Cerulean on earlier builds. Everything after Cerulean, and all of Johto, has only been checked in small emulator tests on prepared saves, not played through. '
         'Expect bugs, including possible softlocks. <strong>Johto is unfinished:</strong> the postgame steps listed in the notes exist, but the rest of Johto has not been checked.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')

READ_ME = f'''Pokemon Psyduck Yellow - {LABEL} (prototype 0161) BETA - {DATE}

*** BETA, FOR TESTING ONLY. NOT A COMPLETE GAME. ***
The Kanto campaign (Pallet Town to your first Hall of Fame) is built. The first parts of the Johto postgame are built too, but Johto as a whole is UNFINISHED and has not been played through.

HOW TO PLAY
1. Open the patching page: {PAGE}
2. Choose your OWN, original, unmodified USA HeartGold .nds file (not another prototype).
3. Click "Create my playable NDS", wait for the checks to finish, then download the result ("{OUT_NAME}") and load it in your DS emulator.
4. Start a NEW GAME. Saves from older prototypes do not work (a renamed old save may behave strangely). Keep this build and its saves separate, and never reuse emulator save states between versions.
Nothing is uploaded; the patching happens in your browser and every step is hash-checked. Expected final SHA256: {{sha}}

WHAT IS NEW SINCE 0110 (internal builds 0111-0157)
''' + '\n'.join('- ' + x.replace('**', '') for x in NEW_IN_0157) + '''
- Everything from 0110 is still here. The save layout is unchanged.

WHAT HAS BEEN TESTED
- The developer has played New Game through Cerulean on earlier builds.
- Everything after Cerulean, and every Johto step above, has only had small emulator checks on prepared test saves (the area entered, one reward and one battle checked, the exit used). Examples from this release: the Fly map and the Pokegear map opened with Johto locked and unlocked; the Vermilion Mart's stock listed; Red's boosted team and the level curve checked in battle (Silver, Falkner, Moltres at 0 / 3 / 8 Johto badges); Mt. Moon, Rock Tunnel and Victory Road ladders walked.
- The bedroom PC's new starting stock was checked in the game data, not by opening the PC in the emulator. The whole Johto trip (ferry, Elm, Mr. Pokemon, Oak's Pokedex upgrade) was built in small steps and has never been played through in one go.

NOT BUILT YET
Elevator floor-selection menus in Silph Co. and Rocket Hideout (stairs instead); some stand-in wall and floor textures; Game Corner and Department Store extras; the Stellar type icon on the Pokedex info page and the PC storage preview (a placeholder shows); most of Johto beyond the steps above has not been checked.

KNOWN ISSUES
Reported by the developer: the top screen can turn black in the overworld; saving and reloading fixes it (not investigated).
The Union Room (Pokemon Center 2nd floor) reads a missing structure and is left alone until online play exists.
One freeze was reported when arriving in Cerulean after fighting a Route 25 trainer who blocked the path (not reproduced).
In the emulator used for testing (DeSmuME), item balls, rocks and boulders are not drawn while you stand directly south of them (they stay solid and come back when you step away).
Fuchsia Gym's leader is still HeartGold's Janine (with Koga's Yellow team and her own lines), and Sabrina gives HeartGold's TM48 instead of Yellow's TM46.
Oak's complete-Pokedex check may still expect 256 species. The Forms page of a few Pokemon shows the species name twice.

Public files are patches and documentation only. No ROM, save or game file is distributed; you must supply your own legally obtained game. The source needed to rebuild this version (tools, data, notes, BUILDING.md) is at {SOURCE_URL} and is proposed to ThatAnarchyDude/corvus-workshop (psyduck-yellow/source) by pull request. Credits: BluRosie/hg-engine and contributors; the patch decoder is RomPatcher.js by Marc Robledo (MIT); Pokemon Yellow data from pret/pokeyellow.
'''

LOG_ENTRY = f'''

## {DATE} — {LABEL} (prototype 0161, BETA)

**BETA, FOR TESTING ONLY. Not a complete game. The Kanto campaign is built; the first parts of the Johto postgame are built but Johto is unfinished and has not been played through.**

[Create {LABEL}]({PAGE}). It builds from your original USA HeartGold file in your browser; nothing is uploaded. The finished game is named "{OUT_NAME}".

What changed since 0110 (internal builds 0111–0157):
''' + '\n'.join('- ' + x for x in NEW_IN_0157) + '''
- Not changed: the save layout.

Reported, not fixed: the top screen sometimes turns black in the overworld (a save and reload fixes it); a freeze when arriving in Cerulean after Route 25 (not reproduced); the Union Room. Checked: small emulator tests on prepared saves (see the read-me). Source to rebuild this version: [{SOURCE_URL}]({SOURCE_URL}), proposed to ThatAnarchyDude/corvus-workshop (psyduck-yellow/source) by pull request.
'''

RELEASE_BODY = f'''# ⚠️ BETA — FOR TESTING ONLY

**This is a beta for testing. It is NOT a complete version of the game.**

The **Kanto campaign (Pallet Town to your first Hall of Fame)** is built, and the **first parts of the Johto postgame** are in, but **Johto is unfinished and has not been played through**. Expect bugs, including possible softlocks.

## How to play
1. Open the **[patching page]({PAGE})**.
2. Pick your **own, original, unmodified USA HeartGold `.nds`** file.
3. Click *Create my playable NDS*, wait for the checks, then download it (**{OUT_NAME}**) and load it in your DS emulator.
4. Start a **New Game** (older saves do not work).

Nothing is uploaded; the patching runs in your browser. This release ships **no ROM or save files**; you must supply your own legally obtained game. The source needed to rebuild this version (tools, data, notes, `BUILDING.md`) is published at **[{SOURCE_URL}]({SOURCE_URL})** and is proposed to [corvus-workshop](https://github.com/ThatAnarchyDude/corvus-workshop) (`psyduck-yellow/source`) by pull request.

## What's new since 0110
''' + '\n'.join('- ' + x for x in NEW_IN_0157) + '''

## How much has been tested
The developer has played New Game through **Cerulean** on earlier builds. Everything after that, and every Johto step, has only had small emulator checks on prepared test saves.

## Known issues
The top screen can turn black in the overworld (a save and reload fixes it). A freeze was reported when arriving in Cerulean after a blocked Route 25 (not reproduced). The Union Room is left alone until online play exists. In the test emulator (DeSmuME), item balls, rocks and boulders are not drawn while you stand directly south of them. Fuchsia Gym's leader is still HeartGold's Janine, and Sabrina gives TM48 instead of TM46.

Files below: the patch stage for this version, the manifest (hashes) and a plain-text read-me. Expected final SHA256: `{sha}`
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
                               status='BETA for testing only: Kanto through the first Hall of Fame plus the first parts of the Johto postgame; Johto unfinished; owner-played to Cerulean only',
                               browser_patch_stages=[{'url': s['url'], 'bytes': s['bytes'], 'sha256': s['manifest']['patch_sha256']} for s in stages])
    package['patchURL'], package['patchBytes'] = PATCH_NAME, size_patch
    html = html[:m.start(2)] + json.dumps(package, ensure_ascii=False) + html[m.end(2):]
    html = html.replace('0110-BETA', VERSION)
    html = re.sub(r'(?:Psyduck Yellow )+Prototype 0110\.nds', OUT_NAME, html)
    html = html.replace('Prototype 0110 — BETA PRE-RELEASE', 'Prototype 0157 — BETA')
    html = html.replace('(pre-release, testing only)', '(beta, testing only)')
    banner_old = '<strong>BETA PRE-RELEASE — FOR TESTING ONLY.</strong> This is <strong>not</strong> a complete game. Only the Kanto campaign, up to your first Hall of Fame induction, has been developed. <strong>Johto is NOT ready. Do NOT go there.</strong>'
    banner_new = '<strong>BETA — FOR TESTING ONLY.</strong> This is <strong>not</strong> a complete game. The Kanto campaign (up to your first Hall of Fame) is built and the first parts of the Johto postgame are in, but <strong>Johto is unfinished and has not been played through</strong>; expect bugs, including softlocks.'
    assert html.count(banner_old) == 1, 'page warning banner changed'
    html = html.replace(banner_old, banner_new)
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0157'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    visible = re.sub(r'<script id="package".*?</script>', '', html, flags=re.S)
    assert '0110' not in visible.replace('since 0110', ''), 'stale 0110 label left in the page'
    assert html.count('Psyduck Yellow Psyduck') == 0 and html.count(OUT_NAME) >= 2, 'download name not normalised'
    assert source_sha in html, 'HeartGold source hash lost'
    (out / 'index.html').write_text(html, encoding='utf-8')
    (out / 'manifest.json').write_text(json.dumps(package['manifest'], indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (out / 'READ-ME-FIRST.txt').write_text(READ_ME.replace('{sha}', new_sha).replace('{SOURCE_URL}', SOURCE_URL), encoding='utf-8')
    log = rel / 'DEVELOPMENT-LOG.md'                       # the releases copy only
    text = log.read_text(encoding='utf-8')
    text = re.sub(r'\*\*Last updated: [^*]*\.\*\*', f'**Last updated: {DATE}.**', text, count=1)
    log.write_text(text + LOG_ENTRY.replace('{SOURCE_URL}', SOURCE_URL), encoding='utf-8')
    # plain-language README of the releases repository (it already carries the 0160 text: relabel it and add the 0161 entries)
    readme = (rel / 'README.md').read_text(encoding='utf-8')
    for old, new_text in (('**BETA 0.1.60, prototype 0160**', f'**{LABEL}, prototype 0161**'), ('(BETA 0.1.60, prototype 0160)', f'({LABEL}, prototype 0161)')):
        assert readme.count(old) == 1, old
        readme = readme.replace(old, new_text)
    readme = re.sub(r'\[hosted BETA 0\.1\.60 patching page\]\([^)]*\)', f'[hosted {LABEL} patching page]({PAGE})', readme)
    new_line = "- **New in 0161:** a New Game starts with the Kanto Pokédex (no National switch); Oak upgrades it to the National Pokédex later in the Johto postgame.\n"
    marker_line = '- **New in 0160:**'
    assert readme.count(marker_line) == 1
    readme = readme.replace(marker_line, new_line + marker_line)
    entry = (f'- **{LABEL} (prototype 0161) — {DATE} (beta, testing only).** A New Game starts with the Kanto Pokédex instead of the National one (Oak upgrades it in the Johto postgame). Everything else as in 0.1.60. Kanto complete to the first Hall of Fame; Johto unfinished.\n')
    marker = '## Release history (newest first)\n'
    assert marker in readme
    readme = readme.replace(marker, marker + entry)
    (rel / 'README.md').write_text(readme, encoding='utf-8')
    (rel.parent / 'RELEASE_BODY.md').write_text(RELEASE_BODY.replace('{sha}', new_sha).replace('{SOURCE_URL}', SOURCE_URL), encoding='utf-8')
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch, 'out_name': OUT_NAME}))


if __name__ == '__main__':
    main(*sys.argv[1:5])
