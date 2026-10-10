"""Build cumulative prototype 015 from the immutable prototype 014 output."""
import json
import struct
import subprocess

import ndspy.rom
from ndspy import _common

from build_rom import BASE, EXPECTED, PROJECT, sha
from species_changes import patch as species_patch
from yellow_tms import patch as tm_patch
from pewter_gym import patch as gym_patch
from pewter_city import patch as city_patch

INPUT_SHA = 'edcd95d49ad2a2c8959b2b946934793bdf8c6f506138d2f4087c246c1b08e79f'


def build():
    source = PROJECT/'build/yellow-heartgold-prototype-014.nds'
    assert sha(source.read_bytes()) == INPUT_SHA
    assert sha(BASE.read_bytes()) == EXPECTED
    old = ndspy.rom.NintendoDSRom.fromFile(str(source))
    rom = ndspy.rom.NintendoDSRom.fromFile(str(source))
    report = dict(species=species_patch(rom), tms=tm_patch(rom),
                  gym=gym_patch(rom), city=city_patch(rom))
    banner = bytearray(rom.iconBanner)
    title = 'Pokemon Psyduck Yellow\nPewter and Boulder Badge 015\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):
        banner[at:at+0x100] = title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]))
    rom.iconBanner = bytes(banner)
    assert rom.arm7 == old.arm7
    target = PROJECT/'build/yellow-heartgold-prototype-015.nds'
    target.write_bytes(rom.save())
    patch = target.with_suffix('.xdelta')
    decoded = PROJECT/'build/pewter-roundtrip.nds'
    tool = PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes()) == sha(target.read_bytes())
    report.update(version='015', input_sha256=INPUT_SHA,
                  output_sha256=sha(target.read_bytes()), patch_sha256=sha(patch.read_bytes()),
                  changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b])
    (PROJECT/'build/pewter-progression-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    build()
