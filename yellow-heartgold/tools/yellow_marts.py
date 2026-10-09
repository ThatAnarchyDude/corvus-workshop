"""Prototype 009: fixed Yellow Viridian stock, with native marts preserved."""
import json
import struct
import subprocess
import ndspy.narc
import ndspy.rom
from build_rom import BASE, EXPECTED, PROJECT, sha
from starter_properties import append_code, CMD_TABLE
from parcel_quest import split_bank, append_bank
from opening import script_bank

INPUT_SHA='48af56b6369c82911de476437753fae43f8d842bd83a03fd1fcda2caf678f46f'
SENTINEL=0x3FFE
VIRIDIAN_STOCK=[4,17,18,22,19]
TABLE=0xF6BE0


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-008.nds'
    assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));previous=ndspy.rom.NintendoDSRom.fromFile(str(source))
    main=rom.loadArm9();data=bytearray(main.sections[0].data);main.sections[0].data=data
    assert struct.unpack_from('<I',data,CMD_TABLE+275*4)[0]==0x02048061
    old_end=main.sections[1].ramAddress+len(main.sections[1].data)
    hook,code=append_code(main,(PROJECT/'asm/yellow-mart.s').read_text())
    struct.pack_into('<I',data,CMD_TABLE+275*4,hook|1)
    main.sections[1].data.extend(b'\0'*(-len(main.sections[1].data)%4))
    assert struct.unpack_from('<I',data,0xD2C68)[0]==old_end
    struct.pack_into('<I',data,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
    rec=TABLE+500*24;sid,iid=struct.unpack_from('<2H',data,rec+6)
    file=rom.filenames.idOf('a/0/1/2');arc=ndspy.narc.NARC(rom.files[file]);old=list(arc.files)
    entries=split_bank(arc.files[sid]);old_arg=struct.pack('<3H',41,0x8004,1)
    assert entries[1].count(old_arg)==1
    entries[1]=entries[1].replace(old_arg,struct.pack('<3H',41,0x8004,SENTINEL))
    new_sid=len(arc.files);arc.files.append(script_bank(entries));struct.pack_into('<H',data,rec+6,new_sid)
    assert arc.files[:len(old)]==old
    rom.files[file]=arc.save();rom.arm9=main.save(compress=True)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nYellow shop prototype 009\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    output=rom.save();target=PROJECT/'build/yellow-heartgold-prototype-009.nds';target.write_bytes(output)
    assert [i for i,(a,b) in enumerate(zip(previous.files,rom.files)) if a!=b]==[file]
    assert rom.arm7==previous.arm7 and rom.arm9OverlayTable==previous.arm9OverlayTable
    target_patch=target.with_suffix('.xdelta');decoded=PROJECT/'build/shops-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(target_patch)],check=True)
    subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(target_patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(output)
    report=dict(version='009',output_sha256=sha(output),patch_sha256=sha(target_patch.read_bytes()),hook=hex(hook),stock=VIRIDIAN_STOCK,original_archive_members_preserved=True)
    (PROJECT/'build/shops-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
