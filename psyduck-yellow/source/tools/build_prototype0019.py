"""Build cumulative prototype 0019 without overwriting any artifact."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from field_interaction_fixes import patch as interactions
from item_collision import patch as collision
from route4 import patch as route
from route4_tm import patch as tm
from route4_save_refresh import patch as refresh

INPUT_SHA='5ce1b82b86b568169540520ed77e3500d216d234c61c4afc4117179cd59a69dc'


def build(output='build/0019-development.nds'):
    source=PROJECT/'build/yellow-heartgold-prototype-0018.nds';assert sha(source.read_bytes())==INPUT_SHA
    target=PROJECT/output
    if target.exists():raise FileExistsError('Preserve the existing artifact and use a new path.')
    r=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0019',input_sha256=INPUT_SHA,interactions=interactions(r),item_collision=collision(r),route4=route(r),whirlwind=tm(r),route4_save_refresh=refresh(r))
    banner=bytearray(r.iconBanner);title='Pokemon Psyduck Yellow\nRoute 4 checkpoint 0019\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));r.iconBanner=bytes(banner);r.saveToFile(str(target));report['output_sha256']=sha(target.read_bytes());(PROJECT/'build/0019-development-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['output_sha256']);return target,report

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',default='build/0019-development.nds');build(p.parse_args().output)
