"""Cumulative visibility/robbed-house checkpoint; preserve existing artifacts."""
import argparse, json, struct
import ndspy.rom
from ndspy import _common
from build_rom import PROJECT, sha
from trainer_visibility import patch as visibility
from cerulean_robbery import patch as robbery
from bill_pc_visual import patch as bill_pc
from nugget_bridge_sign import patch as bridge_sign

INPUT_SHA = '38c4ae17ae724549880cf5e1d21ad7a8eb1d7033719a9b12b88653749339f142'

def build(output='build/0025-development.nds'):
    source = PROJECT / 'build/yellow-heartgold-prototype-0024.nds'
    assert sha(source.read_bytes()) == INPUT_SHA
    target = PROJECT / output
    if target.exists():raise FileExistsError('Use a new path; earlier checkpoints are preserved.')
    r = ndspy.rom.NintendoDSRom.fromFile(str(source))
    report = dict(version='0025', input_sha256=INPUT_SHA,
                  visibility=visibility(r), robbery=robbery(r),
                  bill_pc=bill_pc(r), bridge_sign=bridge_sign(r))
    main = r.loadArm9();itcm = main.sections[1]
    assert len(itcm.data) % 4 == 0 and len(itcm.data) <= 0x8000
    assert struct.unpack_from('<I', main.sections[0].data, 0xD2C68)[0] == itcm.ramAddress + len(itcm.data)
    report['startup'] = dict(word_aligned=True, itcm_bytes=len(itcm.data), remaining_bytes=0x8000-len(itcm.data))
    banner = bytearray(r.iconBanner)
    title = 'Pokemon Psyduck Yellow\nCerulean Dig checkpoint 0025\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240, 0x840, 0x100):banner[at:at+0x100] = title + bytes(0x100-len(title))
    struct.pack_into('<H', banner, 2, _common.crc16(banner[0x20:0x840]));r.iconBanner = bytes(banner)
    r.saveToFile(str(target));report['output_sha256'] = sha(target.read_bytes())
    (PROJECT/'build/0025-development-report.json').write_text(json.dumps(report, indent=2)+'\n')
    return target, report

if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('--output', default='build/0025-development.nds')
    a = p.parse_args();print(build(a.output)[1]['output_sha256'])
