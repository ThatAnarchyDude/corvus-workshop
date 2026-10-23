"""Cumulative save repair, Kanto Trainer Card and friendship testing checkpoint."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from save_compatibility import patch as compatibility
from trainer_card_kanto import patch as trainer_card
from friendship_charm import patch as friendship
INPUT_SHA='3bfbb2218be4ef8925d49dde1e760c5967e9e96f1a87685f148a5cbf302a7f3b'

def build(output='build/0022-development.nds'):
    source=PROJECT/'build/yellow-heartgold-prototype-0021.nds';assert sha(source.read_bytes())==INPUT_SHA
    target=PROJECT/output
    if target.exists():raise FileExistsError('Preserve the existing artifact and use a new path.')
    r=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0022',input_sha256=INPUT_SHA,
        save_compatibility=compatibility(r),trainer_card=trainer_card(r),friendship_charm=friendship(r))
    main=r.loadArm9();itcm=main.sections[1];assert len(itcm.data)%4==0
    assert struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0]==itcm.ramAddress+len(itcm.data)
    banner=bytearray(r.iconBanner);title='Pokemon Psyduck Yellow\nSave repair checkpoint 0022\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));r.iconBanner=bytes(banner);r.saveToFile(str(target))
    report['output_sha256']=sha(target.read_bytes());(PROJECT/'build/0022-development-report.json').write_text(json.dumps(report,indent=2)+'\n');return target,report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='build/0022-development.nds');a=p.parse_args();print(build(a.output)[1]['output_sha256'])
