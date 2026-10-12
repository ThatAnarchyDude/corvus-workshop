"""Cumulative Route 24 checkpoint; existing artifacts are never replaced."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from route24 import patch
from mtmoon_corrections import patch as moon_fixes
INPUT_SHA='a26d9003ec23d9ebc60cc721a6aec169dd33af4ff657d9726bd89ab1cb2e89da'
def build(output='build/0023-development.nds'):
    source=PROJECT/'build/yellow-heartgold-prototype-0022.nds';assert sha(source.read_bytes())==INPUT_SHA
    target=PROJECT/output
    if target.exists():raise FileExistsError('Use a new path; existing checkpoints are preserved.')
    r=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0023',input_sha256=INPUT_SHA,route24=patch(r),mtmoon_corrections=moon_fixes(r))
    main=r.loadArm9();itcm=main.sections[1];assert len(itcm.data)%4==0
    assert struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0]==itcm.ramAddress+len(itcm.data)
    report['startup']=dict(word_aligned=True,itcm_bytes=len(itcm.data),remaining_bytes=0x8000-len(itcm.data))
    banner=bytearray(r.iconBanner);title='Pokemon Psyduck Yellow\nNugget Bridge checkpoint 0023\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));r.iconBanner=bytes(banner);r.saveToFile(str(target))
    report['output_sha256']=sha(target.read_bytes());(PROJECT/'build/0023-development-report.json').write_text(json.dumps(report,indent=2)+'\n');return target,report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='build/0023-development.nds');a=p.parse_args();print(build(a.output)[1]['output_sha256'])
