"""Prototype 006: saved PC supplies and additional native item evolutions."""
import json
import struct
import subprocess
import ndspy.narc
import ndspy.rom
from build_rom import BASE, EXPECTED, PROJECT, sha
from starter_properties import append_code
from prototype import thumb_bl
from opening import script_bank, talk, command, encode_text
from player_pc import script, EVOLUTION_TEXT, EVOLUTION_ITEMS

INPUT_SHA = '3c78ed017788e39d6a35aacaae5206df635bbada0ac203f610eaa459498fc144'
RULES = ((54,84,55),(133,109,196),(133,108,197),(133,246,471),(133,85,470),(175,109,176))


def patch_native(main):
    data = main.sections[0].data
    old_end = main.sections[1].ramAddress + len(main.sections[1].data)
    assert old_end == 0x01FF88E0
    assert struct.unpack_from('<I',data,0xD2C68)[0] == old_end
    at=0x70E34
    assert data[at:at+6] == bytes.fromhex('f0b591b00f1c')
    hook,code=append_code(main,(PROJECT/'asm/evolution-items.s').read_text())
    # Save the caller's link register before BL overwrites it.
    data[at:at+6]=bytes.fromhex('f446')+thumb_bl(0x02070E36,hook)
    main.sections[1].data.extend(b'\0' * (-len(main.sections[1].data) % 4))
    end=main.sections[1].ramAddress+len(main.sections[1].data)
    struct.pack_into('<I',data,0xD2C68,end)
    return dict(evolution_hook=hex(hook),hook_bytes=len(code),itcm_end=hex(end))


def patch(rom, original):
    main=rom.loadArm9();main.sections[0].data=bytearray(main.sections[0].data)
    details=patch_native(main)
    pristine=original.loadArm9().sections[0].data
    table=pristine.index(struct.pack('<3H',740,513,451))-6-505*24
    at=table+506*24+6
    old_script,init,old_text=struct.unpack_from('<3H',main.sections[0].data,at)
    assert (old_script,init,old_text)==(983,984,838)
    scripts_id=rom.filenames.idOf('a/0/1/2');texts_id=rom.filenames.idOf('a/0/2/7')
    scripts=ndspy.narc.NARC(rom.files[scripts_id]);texts=ndspy.narc.NARC(rom.files[texts_id])
    room_init=b''.join(command(30,flag) for flag in range(0x11B,0x11F))+command(2)
    assert scripts.files[old_script]==script_bank([talk(23),script(),room_init])
    new_script=len(scripts.files);new_text=len(texts.files)
    scripts.files.append(script_bank([talk(23),script(evolution_items=True),room_init]))
    # Use the same native name/item/quantity placeholder codes as prototype 004.
    placeholders=[65534, 259, 2, 0, 0]
    texts.files.append(encode_text(EVOLUTION_TEXT,placeholders))
    assert texts.files[old_text]==encode_text(EVOLUTION_TEXT[:-1],placeholders)
    struct.pack_into('<3H',main.sections[0].data,at,new_script,init,new_text)
    rom.arm9=main.save(compress=True)
    rom.files[scripts_id]=scripts.save();rom.files[texts_id]=texts.save()
    items_id=rom.filenames.idOf('a/0/1/7');items=ndspy.narc.NARC(rom.files[items_id])
    # Native item IDs are NOT archive indices after the unused item-ID gap.
    # NeverMeltIce (246) maps to member 224 through the ARM9 item table.
    mapping=0x100194
    assert struct.unpack_from('<4H',main.sections[0].data,mapping+246*8)==(224,314,315,212)
    assert struct.unpack_from('<4H',main.sections[0].data,mapping+84*8)==(84,123,124,97)
    ice=bytearray(items.files[224]);stone=items.files[84]
    assert len(ice)==len(stone)==34 and ice[2:4]==bytes.fromhex('5114')
    # Keep NeverMeltIce's held effect, pocket, art and name. Enable its native
    # field party-selection action and evolution flag, like existing stones.
    ice[10]=stone[10];ice[12]=stone[12];ice[15]|=8
    items.files[224]=bytes(ice);rom.files[items_id]=items.save()
    return {**details,'pc_items':list(EVOLUTION_ITEMS),'quantity_each':95,'old_script':old_script,'new_script':new_script,'new_text':new_text,'custom_rules':RULES}


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-005.nds'
    assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));before=list(rom.files)
    original=ndspy.rom.NintendoDSRom.fromFile(str(BASE));details=patch(rom,original)
    banner=bytearray(rom.iconBanner)
    title='Pokemon Psyduck Yellow\nEvolution test prototype 006\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    output=rom.save();check=ndspy.rom.NintendoDSRom(output)
    changed=[i for i,(a,b) in enumerate(zip(before,check.files)) if a!=b]
    assert changed==sorted(rom.filenames.idOf(p) for p in ('a/0/1/2','a/0/2/7','a/0/1/7'))
    previous=ndspy.rom.NintendoDSRom.fromFile(str(source))
    assert check.arm9OverlayTable==previous.arm9OverlayTable and check.arm7==previous.arm7
    assert check.arm9==rom.arm9 and len(check.files)==len(before)
    target=PROJECT/'build/yellow-heartgold-prototype-006.nds';target.write_bytes(output)
    patcher=PROJECT/'.tools/xdelta3';patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/evolution-roundtrip.nds'
    subprocess.run([str(patcher),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True)
    subprocess.run([str(patcher),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(output)
    report=dict(version='006',output_sha256=sha(output),patch_sha256=sha(patchfile.read_bytes()),changed_file_ids=changed,**details)
    (PROJECT/'build/evolution-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
