"""Build the unpublished cumulative 0018 development ROM; no release packaging.

Run from yellow-heartgold with .venv/bin/python tools/build_prototype0018.py.
The previous checkpoint must already exist locally and match its recorded hash.
"""
import json
import argparse
import ndspy.rom
from build_rom import PROJECT, sha
from mtmoon import patch as patch_mtmoon, INPUT_SHA
from bulk_rare_candy import patch as patch_candy
from mtmoon_story import patch as patch_story
from mtmoon_center import patch as patch_center
from mtmoon_tms import patch as patch_tms
from mtmoon_items import patch as patch_items
from mtmoon_rockets import patch as patch_rockets
from mtmoon_encounters import patch as patch_encounters


def build(output=None):
    source = PROJECT / 'build/yellow-heartgold-prototype-0017.nds'
    assert sha(source.read_bytes()) == INPUT_SHA
    rom = ndspy.rom.NintendoDSRom.fromFile(str(source))
    report = dict(status='unpublished; Mt. Moon story work remains',
                  input_sha256=INPUT_SHA, mtmoon=patch_mtmoon(rom),
                  mtmoon_story=patch_story(rom),
                  mtmoon_center=patch_center(rom),
                  bulk_rare_candy=patch_candy(rom),
                  yellow_cave_tms=patch_tms(rom),
                  remaining_cave_items=patch_items(rom),
                  mtmoon_rockets=patch_rockets(rom),
                  mtmoon_deep_encounters=patch_encounters(rom))
    report['release_pending'] = [
        'Custom Jessie/James graphics and fossil props',
        'Final native cave traversal, hidden rewards and story/save checks',
        'Immutable cumulative patch packaging and publication',
    ]
    target = PROJECT / (output or 'build/0018-development.nds')
    rom.saveToFile(str(target))
    report['output_sha256'] = sha(target.read_bytes())
    (PROJECT / 'build/0018-development-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(status=report['status'], output=str(target),
                         output_sha256=report['output_sha256']), indent=2))
    return target, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', help='Private development ROM path; never a publication command.')
    build(parser.parse_args().output)
