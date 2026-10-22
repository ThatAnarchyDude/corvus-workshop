import base64, hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def exists(p):
    return p.exists() or p.is_symlink()

def verify(p, size, expected):
    if p.is_symlink() or not p.is_file() or p.stat().st_size != size or digest(p) != expected:
        raise ValueError(f'Size/SHA-256 mismatch: {p.name}; preserved unchanged')

def install(staged, destination, size, expected):
    try:
        os.link(staged, destination)
    except FileExistsError:
        verify(destination, size, expected)

repo = Path.cwd()
build = repo / 'yellow-heartgold/build'
original = repo / 'Pokemon - HeartGold Version (USA).nds'
tag = '<script id="package" type="application/json">'

try:
    for version in ('0024', '0025'):
        page = repo / f'psyduck-yellow/prototype-{version}/index.html'
        html = page.read_text(encoding='utf-8')
        if html.count(tag) != 1 or '</script>' not in html.split(tag, 1)[1]:
            raise ValueError(f'Invalid package script: {page.name}')
        package = json.loads(html.split(tag, 1)[1].split('</script>', 1)[0])
        m = package['manifest']
        if m['version'] != version:
            raise ValueError('Package version mismatch')
        verify(original, m['source_bytes'], m['source_sha256'])
        patch = base64.b64decode(package['patch'], validate=True)
        if hashlib.sha256(patch).hexdigest() != m['patch_sha256']:
            raise ValueError(f'Prototype {version} patch SHA-256 mismatch')
        build.mkdir(parents=True, exist_ok=True)
        output = build / f'yellow-heartgold-prototype-{version}.nds'
        receipt = json.dumps({'package': str(page.relative_to(repo)), 'manifest': m}, indent=2, sort_keys=True).encode() + b'\n'
        with tempfile.TemporaryDirectory(prefix='checkpoint-restore-', dir=build) as temp:
            temp = Path(temp)
            sp, so, sr = temp/'patch.xdelta', temp/'output.nds', temp/'receipt.json'
            sp.write_bytes(patch)
            sr.write_bytes(receipt)
            files = [
                (sp, output.with_suffix('.xdelta'), len(patch), m['patch_sha256']),
                (so, output, m['output_bytes'], m['output_sha256']),
                (sr, build/f'checkpoint-{version}-recovery.json', len(receipt), hashlib.sha256(receipt).hexdigest())
            ]
            for _, destination, size, expected in files:
                if exists(destination):
                    verify(destination, size, expected)
            if not exists(output):
                tool = shutil.which('xdelta3') or str(build.parent/'.tools/xdelta3')
                subprocess.run([tool, '-d', '-s', str(original), str(sp), str(so)], check=True)
                verify(so, m['output_bytes'], m['output_sha256'])
            for staged, destination, size, expected in files:
                if staged.exists():
                    install(staged, destination, size, expected)
            print(f'Prototype {version} verified: {output.name}')
except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
    raise SystemExit(f'Restore stopped: {error}')
