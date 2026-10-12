"""Cumulative Route 25/Bill checkpoint; never replace existing artifacts."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from route25 import patch
INPUT_SHA='3a861684a79452d6c6418e29ddc1e7b89c48345d638ad35cf75ea77cbbbb29de'
def build(output='build/0024-development.nds'):
    source=PROJECT/'build/yellow-heartgold-prototype-0023.nds';assert sha(source.read_bytes())==INPUT_SHA
    target=PROJECT/output
    if target.exists():raise FileExistsError('Use a new path; existing checkpoints are preserved.')
    r=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0024',input_sha256=INPUT_SHA,route25=patch(r))
    main=r.loadArm9();itcm=main.sections[1];assert len(itcm.data)%4==0
    assert struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0]==itcm.ramAddress+len(itcm.data)
    report['startup']=dict(word_aligned=True,itcm_bytes=len(itcm.data),remaining_bytes=0x8000-len(itcm.data))
    banner=bytearray(r.iconBanner);title='Pokemon Psyduck Yellow\nRoute 25 and Bill checkpoint 0024\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));r.iconBanner=bytes(banner);r.saveToFile(str(target))
    report['output_sha256']=sha(target.read_bytes());(PROJECT/'build/0024-development-report.json').write_text(json.dumps(report,indent=2)+'\n');return target,report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='build/0024-development.nds');a=p.parse_args();print(build(a.output)[1]['output_sha256'])
