"""Build cumulative prototype 0020 without overwriting any artifact."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from testing_travel import patch as travel

INPUT_SHA='29d274454fd191bf0e41192322113f1ecb6961e74ca55dda3566b11fc13637cd'


def build(output='build/0020-development.nds'):
    source=PROJECT/'build/yellow-heartgold-prototype-0019.nds';assert sha(source.read_bytes())==INPUT_SHA
    target=PROJECT/output
    if target.exists():raise FileExistsError('Preserve the existing artifact and use a new path.')
    r=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0020',input_sha256=INPUT_SHA,testing_travel=travel(r))
    banner=bytearray(r.iconBanner);title='Pokemon Psyduck Yellow\nTesting travel checkpoint 0020\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));r.iconBanner=bytes(banner);r.saveToFile(str(target));report['output_sha256']=sha(target.read_bytes());(PROJECT/'build/0020-development-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['output_sha256']);return target,report

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',default='build/0020-development.nds');build(p.parse_args().output)
