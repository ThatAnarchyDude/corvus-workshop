"""Build the unpublished cumulative 0018 development ROM; no release packaging.

Run from yellow-heartgold with .venv/bin/python tools/build_prototype0018.py.
The previous checkpoint must already exist locally and match its recorded hash.
"""
import json
import ndspy.rom
from build_rom import PROJECT, sha
from mtmoon import patch as patch_mtmoon, INPUT_SHA
from bulk_rare_candy import patch as patch_candy


def build():
    source = PROJECT / 'build/yellow-heartgold-prototype-0017.nds'
    assert sha(source.read_bytes()) == INPUT_SHA
    rom = ndspy.rom.NintendoDSRom.fromFile(str(source))
    report = dict(status='unpublished; Mt. Moon story work remains',
                  input_sha256=INPUT_SHA, mtmoon=patch_mtmoon(rom),
                  bulk_rare_candy=patch_candy(rom))
    target = PROJECT / 'build/0018-bulk-candy-development.nds'
    rom.saveToFile(str(target))
    report['output_sha256'] = sha(target.read_bytes())
    (PROJECT / 'build/0018-development-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(status=report['status'], output=str(target),
                         output_sha256=report['output_sha256']), indent=2))
    return target, report


if __name__ == '__main__':
    build()
