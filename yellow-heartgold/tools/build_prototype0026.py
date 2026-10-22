"""Build a separate cumulative 0026 development ROM; never overwrite artifacts."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from route5 import patch
from saffron_gates import patch as gates_patch
INPUT_SHA='52853b58ad6d2e1f51b74409024c53657870273d63e727c05a9e42a578bf9af2'

def build(output='build/0026-route5-foundation.nds', with_gates=False):
    source=PROJECT/'build/yellow-heartgold-prototype-0025.nds'
    if sha(source.read_bytes())!=INPUT_SHA:raise ValueError('Wrong 0025 baseline')
    target=PROJECT/output;report_path=target.with_suffix('.json')
    if target.exists() or report_path.exists():raise FileExistsError('Use new output paths')
    target.parent.mkdir(parents=True,exist_ok=True)
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0026-development',input_sha256=INPUT_SHA,route5=patch(rom))
    if with_gates: report['saffron_gates']=gates_patch(rom)
    report.update(release_scope='Route 5 encounters and native Day Care', unfinished=['Yellow Route 5 geometry and Day Care placement', 'Saffron drink roadblock', 'area banners and Blue title'])
    main=rom.loadArm9();itcm=main.sections[1]
    assert len(itcm.data)%4==0 and len(itcm.data)<=0x8000
    assert struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0]==itcm.ramAddress+len(itcm.data)
    report['startup']=dict(itcm_bytes=len(itcm.data),remaining_bytes=0x8000-len(itcm.data))
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nRoute 5 development 0026\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    rom.saveToFile(str(target));report['output_sha256']=sha(target.read_bytes());report_path.write_text(json.dumps(report,indent=2)+'\n')
    assert sha(source.read_bytes())==INPUT_SHA
    return target,report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='build/0026-route5-foundation.nds');p.add_argument('--with-gates',action='store_true');a=p.parse_args()
    target,report=build(a.output,a.with_gates);print(target);print(report['output_sha256'])
