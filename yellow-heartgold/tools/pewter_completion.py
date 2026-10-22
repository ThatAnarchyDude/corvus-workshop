"""Build immutable cumulative prototype 0016 from verified prototype 015."""
import json
import struct
import subprocess
import ndspy.rom
from ndspy import _common
from build_rom import BASE, EXPECTED, PROJECT, sha
from pewter_interiors import patch as interiors_patch
from pewter_museum import patch as museum_patch
from reusable_tms import patch as tm_patch
from rare_candy_evolution import patch as candy_evolution_patch
from psyduck_evolution import patch as psyduck_evolution_patch

INPUT_SHA='b15097292e8dfcbc0a1c0d1f58eabb9132b0c117f95a79d266b0abe528f2ac84'

def build():
    source=PROJECT/'build/yellow-heartgold-prototype-015.nds'
    assert sha(source.read_bytes())==INPUT_SHA
    assert sha(BASE.read_bytes())==EXPECTED
    old=ndspy.rom.NintendoDSRom.fromFile(str(source))
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source))
    report=dict(interiors=interiors_patch(rom),museum=museum_patch(rom),reusable_tms=tm_patch(rom))
    report['rare_candy_evolution']=candy_evolution_patch(rom)
    report['psyduck_evolution']=psyduck_evolution_patch(rom)
    banner=bytearray(rom.iconBanner)
    title='Pokemon Psyduck Yellow\nPewter interiors 0016\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    assert rom.arm7==old.arm7
    target=PROJECT/'build/yellow-heartgold-prototype-0016.nds';target.write_bytes(rom.save())
    patch=target.with_suffix('.xdelta');decoded=PROJECT/'build/pewter-0016-roundtrip.nds'
    tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(target.read_bytes())
    report.update(version='0016',input_sha256=INPUT_SHA,output_sha256=sha(target.read_bytes()),
                  patch_sha256=sha(patch.read_bytes()),
                  changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b])
    (PROJECT/'build/pewter-completion-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':build()
