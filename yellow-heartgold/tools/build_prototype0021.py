"""Build cumulative prototype 0021 without replacing any checkpoint."""
import argparse,json,struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT,sha
from cerulean_tm import patch as tm
from cerulean import patch as city,DATA
from cerulean_bike import patch as bike
from pewter_guide_fix import patch as guide
INPUT_SHA='39f0fbb43d345fe34fdd7db57a2ce766c712bf7b21a741f81e91316a0d201191'
def build(output='build/0021-development.nds'):
 source=PROJECT/'build/yellow-heartgold-prototype-0020.nds';assert sha(source.read_bytes())==INPUT_SHA
 target=PROJECT/output
 if target.exists():raise FileExistsError('Use a new output path to preserve the existing artifact.')
 r=ndspy.rom.NintendoDSRom.fromFile(str(source));report=dict(version='0021',input_sha256=INPUT_SHA,tms=tm(r),cerulean=city(r),bike_shop=bike(r,DATA['messages']),pewter_guide=guide(r))
 main=r.loadArm9();itcm=main.sections[1]
 assert len(itcm.data)%4==0, 'The native autoload copier requires whole words'
 assert struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0]==itcm.ramAddress+len(itcm.data)
 report['startup']=dict(itcm_bytes=len(itcm.data),word_aligned=True,end_pointer_matches=True)
 banner=bytearray(r.iconBanner);title='Pokemon Psyduck Yellow\nCerulean checkpoint 0021\nCorvus Workshop'.encode('utf-16le')
 for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
 struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));r.iconBanner=bytes(banner);r.saveToFile(str(target));report['output_sha256']=sha(target.read_bytes());(PROJECT/'build/0021-development-report.json').write_text(json.dumps(report,indent=2)+'\n');return target,report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='build/0021-development.nds');args=p.parse_args();print(build(args.output)[1]['output_sha256'])
