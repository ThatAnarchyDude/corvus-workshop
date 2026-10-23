"""Verify the base ROM and generate a payload-verified baseline repack."""
import hashlib
import json
from pathlib import Path
import ndspy.rom
import ndspy.fnt

PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT.parent / 'Pokemon - HeartGold Version (USA).nds'
EXPECTED = '65f02a56842b75aa92d775d56d657a56fe3fa993550b04dc20704ab82d760105'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run():
    original = BASE.read_bytes()
    if sha(original) != EXPECTED:
        raise ValueError('Wrong base ROM: refusing to build')
    rom = ndspy.rom.NintendoDSRom(original)
    output = rom.save()
    check = ndspy.rom.NintendoDSRom(output)
    for name in ['arm9', 'arm7', 'arm9OverlayTable', 'arm7OverlayTable', 'iconBanner', 'rsaSignature']:
        if getattr(rom, name) != getattr(check, name):
            raise ValueError(f'Repack changed {name}')
    if rom.files != check.files or ndspy.fnt.save(rom.filenames) != ndspy.fnt.save(check.filenames):
        raise ValueError('Repack changed filesystem payloads or filenames')
    outdir = PROJECT / 'build'
    outdir.mkdir(exist_ok=True)
    target = outdir / 'heartgold-baseline.nds'
    target.write_bytes(output)
    report = dict(stage='baseline-repack', input_sha256=sha(original), output_sha256=sha(output),
                  input_bytes=len(original), output_bytes=len(output), byte_identical=original == output,
                  file_payloads_verified=len(rom.files), executable_payloads_verified=True,
                  gameplay_verified=False)
    (outdir / 'baseline-report.json').write_text(json.dumps(report, indent=2) + '\n')
    if sha(BASE.read_bytes()) != EXPECTED:
        raise ValueError('Original changed during build')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
