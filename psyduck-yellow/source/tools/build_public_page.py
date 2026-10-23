"""Build the public prototype-0041 patch page files (patches and documentation only; never a ROM, save or source).

Usage: build_public_page.py <worktree of origin/main> <0039-art-to-0041.xdelta> <0039 art ROM> <0041 ROM>
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

DATE = 'October 22, 2026'
BASE = 'https://raw.githubusercontent.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow'
OUT_NAME = 'Pokemon-Psyduck-Yellow-prototype-0041-EXPERIMENTAL.nds'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


BLURB = ('<p><strong>Prototype 0041 — EXPERIMENTAL.</strong> Adds a large part of the Kanto campaign: Pokémon Tower, the Celadon Gym, '
         'the Rocket Hideout, Routes 8 and 11–18, the Fuchsia, Saffron, Seafoam and Viridian gyms, the Indigo Plateau League, '
         'a starter Psyduck with Mega Psyduck and Psyduckite (with its own art), and every Mega Stone for ₣0 in the Vermilion Mart.</p>'
         '<p><strong>Played so far by the owner:</strong> New Game through Vermilion (Pewter and Cerulean gyms, Mega Evolution, the Mega switch, '
         'the Mart). <strong>Everything from Nugget Bridge onward has not been played through</strong>, including the SS Anne, Vermilion Gym, '
         'Pokémon Tower, Rocket Hideout and the later gyms and League. Silph Co., the Safari Zone and the Cinnabar Mansion are not built. '
         'Known issue: the top screen can go black after leaving Viridian Forest; saving and reloading fixed it.</p>'
         '<p>Start a <strong>New Game</strong>; saves from older prototypes are not supported. Keep this build and its saves separate.</p>')


def main(tree, delta, art_rom, new_rom):
    root = Path(tree) / 'psyduck-yellow'
    old = root / 'prototype-0039'
    out = root / 'prototype-0041'
    out.mkdir(exist_ok=True)
    shutil.copyfile(delta, out / '0039-art-to-0041.xdelta')
    for name in ('HG-ENGINE-CREDITS.md', 'LICENSE.txt'):
        shutil.copyfile(old / name, out / name)
    html = (old / 'index-art.html').read_text()
    m = re.search(r'(<script id="package" type="application/json">)(.*?)(</script>)', html, re.S)
    package = json.loads(m.group(2))
    stages = package['stages']
    stages[3]['url'] = BASE + '/prototype-0039/' + stages[3]['url']
    art_sha, new_sha = sha(art_rom), sha(new_rom)
    patch_sha = sha(delta)
    size_art, size_new, size_patch = Path(art_rom).stat().st_size, Path(new_rom).stat().st_size, Path(delta).stat().st_size
    assert art_sha == stages[3]['manifest']['output_sha256']
    stages.append({'url': '0039-art-to-0041.xdelta', 'bytes': size_patch,
                   'manifest': {'source_sha256': art_sha, 'source_bytes': size_art, 'output_sha256': new_sha,
                                'output_bytes': size_new, 'patch_sha256': patch_sha, 'patch_bytes': size_patch}})
    package['manifest'] = dict(version='0041-EXPERIMENTAL', source_sha256=package['manifest']['source_sha256'],
                               source_bytes=package['manifest']['source_bytes'], output_sha256=new_sha, output_bytes=size_new,
                               cumulative=True, roundtrip_verified=True,
                               status='experimental 0041: Kanto content through the League, Mega Psyduck; owner-played to Vermilion only',
                               browser_patch_stages=[{'url': s['url'], 'bytes': s['bytes'], 'sha256': s['manifest']['patch_sha256']} for s in stages])
    package['patchURL'], package['patchBytes'] = '0039-art-to-0041.xdelta', size_patch
    html = html[:m.start(2)] + json.dumps(package, ensure_ascii=False) + html[m.end(2):]
    html = html.replace('<title>Psyduck Yellow prototype 0039-SPRITE-UPDATE</title>', '<title>Psyduck Yellow prototype 0041-EXPERIMENTAL</title>')
    html = html.replace('<p>Expanded engine — Mega Eevee sprite update · Prototype 0039-SPRITE-UPDATE</p>', '<p>Expanded engine — Kanto campaign build · Prototype 0041-EXPERIMENTAL</p>')
    html = html.replace('Download prototype 0039-SPRITE-UPDATE.nds', 'Download prototype 0041-EXPERIMENTAL.nds')
    html = html.replace('Pokemon-Psyduck-Yellow-prototype-0039-SPRITE-UPDATE.nds', OUT_NAME)
    lines = html.split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('<p><strong>Prototype 0039'))
    lines[i] = BLURB
    html = '\n'.join(lines)
    assert '0039' not in re.sub(r'<script id="package".*?</script>', '', html, flags=re.S), 'stale 0039 text left in the page'
    (out / 'index.html').write_text(html)
    manifest = package['manifest']
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    (out / 'READ-ME-FIRST.txt').write_text(f'''Pokemon Psyduck Yellow - prototype 0041 EXPERIMENTAL - {DATE}

An experimental build, not a finished game. Start a NEW GAME; saves from older prototypes are not supported. Keep this build and its saves separate and never reuse emulator save states between ROM versions.

NEW since 0039: Pokemon Tower (Fuji and the Poke Flute, rival, Jessie and James, the Marowak ghost as an Alolan Marowak), the Celadon Gym, the Rocket Hideout under the Game Corner (Giovanni and the Silph Scope), Yellow trainers and wild Pokemon on Routes 8 and 11-18 (the Route 11/12 Snorlax wake to the Poke Flute), the Fuchsia, Saffron, Seafoam (Blaine) and Viridian gyms with Yellow teams, the Fuchsia Warden's HM Strength and Surf, the Indigo Plateau League (Lorelei, Bruno, Agatha, Lance, Champion Blue), a starter Psyduck with Mega Psyduck (supplied art) and Psyduckite, and all Mega Stones at 0 yen in the Vermilion Mart supplies list.

PLAYED BY THE OWNER: New Game through Vermilion - the Pewter and Cerulean gyms and badges, Mega Psyduck and Mega Eevee (activation in battle and reversion after), the bedroom Mega on/off switch, the Mart, the new Mega Psyduck sprites. NOT PLAYED: Nugget Bridge onward - Bill, the SS Anne, Vermilion Gym, Pokemon Tower, Rocket Hideout, Fuchsia and later gyms, the League. Those were only started in an emulator test, never won through, so expect rough edges: gym and League dialogue is still HeartGold's, some trainers may stand on awkward tiles, rewards and badges there are unconfirmed.

NOT BUILT: Silph Co., the Safari Zone and Gold Teeth, the Cinnabar Mansion, the Rocket Hideout Lift Key and item balls, Victory Road and Route 22/23 trainer work, Hall of Fame follow-up, Johto unlock changes. The Mega Evolution lock described in earlier notes is not enforced for the Stones in the Mart.

KNOWN ISSUE: the top screen went black once after leaving Viridian Forest by the north exit; saving and reloading fixed it. Not investigated yet.

Patching: select your ORIGINAL unmodified USA HeartGold .nds, not another prototype. The browser applies five verified stages locally and checks every output hash. No ROM is uploaded. Expected output SHA256: {new_sha}.

Public files are patches and documentation only; ROMs and saves stay local. Credits: BluRosie/hg-engine and contributors; decoder RomPatcher.js, Marc Robledo, MIT. Pokemon Yellow data and dialogue are referenced from the pret/pokeyellow disassembly for compatibility and are not redistributed.
''')
    log = root / 'DEVELOPMENT-LOG.md'
    text = log.read_text()
    text = text.replace('**Last updated: October 21, 2026.**', f'**Last updated: {DATE}.**', 1)
    text += f'''

## {DATE} — prototype 0041 (experimental)

[Create prototype 0041](https://raw.githack.com/ThatAnarchyDude/corvus-workshop/main/psyduck-yellow/prototype-0041/index.html). It builds from your original USA HeartGold file in your browser; nothing is uploaded.

A large Kanto update: Pokémon Tower, the Celadon Gym, the Rocket Hideout, Routes 8 and 11–18, the Fuchsia, Saffron, Seafoam and Viridian gyms, the Indigo Plateau League, a starter Psyduck with Mega Psyduck and Psyduckite using supplied art, and every Mega Stone for ₣0 in the Vermilion Mart.

Played so far: New Game through Vermilion, including Mega Psyduck/Mega Eevee activation and reversion. Not played: everything from Nugget Bridge onward. Silph Co., the Safari Zone and the Cinnabar Mansion are not built. Known issue: a one-time black top screen after Viridian Forest, fixed by saving and reloading. Start a New Game; old saves are unsupported. Public artifacts are patches and documentation only.
'''
    log.write_text(text)
    print(json.dumps({'output_sha256': new_sha, 'patch_sha256': patch_sha, 'patch_bytes': size_patch}))


if __name__ == '__main__':
    main(*sys.argv[1:5])
