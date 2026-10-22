"""Prototype 005: an animated Psyduck title, preserving all opening gameplay."""
import json
import struct
import subprocess
from pathlib import Path

import ndspy.code
import ndspy.model
import ndspy.narc
import ndspy.rom
from PIL import Image
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from build_rom import BASE, EXPECTED, PROJECT, sha
from prototype import thumb_bl
from title_models import psyduck, animation, water_model

INPUT_SHA='4018c164fe5ba818134d457f5ac0b923e2b5fdf44d5035be73714680d3f035df'
ART=PROJECT/'art/title'


def logo_assets(palette):
    image=Image.open(ART/'logo.png').convert('RGBA').resize((256,128),Image.Resampling.LANCZOS)
    colors=struct.unpack_from('<256H',palette,40)
    rgb=[tuple(((c>>(5*i))&31)*255//31 for i in range(3)) for c in colors]
    cache={}
    pixels=[]
    for r,g,b,a in image.getdata():
        if a<128:pixels.append(0);continue
        key=(r,g,b)
        if key not in cache:cache[key]=min(range(1,256),key=lambda i:sum((rgb[i][k]-key[k])**2 for k in range(3)))
        pixels.append(cache[key])
    tiles=[bytes(64)];lookup={tiles[0]:0};entries=[0]*1024
    for ty in range(16):
        for tx in range(32):
            tile=bytes(pixels[(ty*8+y)*256+tx*8+x] for y in range(8) for x in range(8))
            if tile not in lookup:lookup[tile]=len(tiles);tiles.append(tile)
            entries[(ty+4)*32+tx]=lookup[tile]
    tiles += [bytes(64)]*(-len(tiles)%32)
    raw=b''.join(tiles)
    char=struct.pack('<4sIHH5I',b'RAHC',32+len(raw),len(tiles)//32,32,4,0,0,len(raw),24)+raw
    ncgr=struct.pack('<4sHHIHH',b'RGCN',0xfeff,0x101,16+len(char),16,1)+char
    raw=struct.pack('<1024H',*entries)
    screen=struct.pack('<4sIHHII',b'NRCS',20+len(raw),256,256,1,len(raw))+raw
    nscr=struct.pack('<4sHHIHH',b'RCSN',0xfeff,0x100,16+len(screen),16,1)+screen
    return ncgr,nscr


def patch_overlay(rom):
    overlays=rom.loadArm9Overlays();ov=overlays[60];old=bytes(ov.data)
    assert ov.ramAddress==0x021e5900 and ov.bssSize==0 and len(old)==24448
    data=ov.data
    # Our models have their own joint animation; the original material and
    # texture-pattern animations reference Ho-Oh's discarded material tables.
    for at,expected,replacement in [(0x966,b'\x1d\x20',b'\x00\x20'),(0x96a,b'\x1c\x20',b'\x00\x20'),
        (0x974,b'\x1b\x23',b'\x00\x23'),(0x97c,b'\x28\x23',b'\x00\x23'),
        (0x1a4,b'\xfa\x20',b'\x36\x20')]:
        assert data[at:at+2]==expected,(hex(at),data[at:at+2].hex())
        data[at:at+2]=replacement
    # Keep the camera above the water and use gentle side-to-side movement.
    table=0x5640
    original=[(180,177,301,10),(335,-293,296,5),(180,177,301,5),(625,152,256,10),(0,0,0,0)]
    target=[(-100,260,270,10),(100,260,270,5),(-100,260,270,5),(100,260,270,10),(0,0,0,0)]
    for i,(before,after) in enumerate(zip(original,target)):
        at=table+16*i;assert struct.unpack_from('<4i',data,at)==(*[v*4096 for v in before[:3]],before[3])
        struct.pack_into('<4i',data,at,*[v*4096 for v in after[:3]],after[3])
    address=ov.ramAddress+len(data)
    source='''
push {r4,lr}
movs r4,r0
bl 0x021E68B0
ldr r2, field_offset
adds r2,r4,r2
ldr r3, camera_values
movs r1,#12
copy_camera:
ldr r0,[r3]
str r0,[r2]
adds r3,#4
adds r2,#4
subs r1,#1
bne copy_camera
ldr r2,speed_offset
adds r2,r4,r2
movs r0,#1
lsls r0,r0,#11
str r0,[r2]
pop {r4,pc}
.align 2
field_offset: .word 0x1AC
speed_offset: .word 0x1EC
camera_values: .word values
values:
.word 409600,1064960,1105920
.word 409600,1064960,1105920
.word 122880,532480,0
.word 122880,532480,0
'''
    raw,_=Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(source,addr=address)
    hook=0x021e624e;at=hook-ov.ramAddress;assert data[at:at+4]==thumb_bl(hook,0x021e68b0)
    data.extend(bytes(raw));data[at:at+4]=thumb_bl(hook,address)
    assert len(data)<0x10000
    rom.files[ov.fileID]=ov.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    return {'overlay':60,'camera_helper':hex(address),'original_sha256':sha(old),'output_sha256':sha(data),'cry_species':54}


def build():
    previous=PROJECT/'build/yellow-heartgold-prototype-004.nds'
    if sha(previous.read_bytes())!=INPUT_SHA or sha(BASE.read_bytes())!=EXPECTED:raise ValueError('Wrong base or prototype 004 input')
    rom=ndspy.rom.NintendoDSRom.fromFile(str(previous));before=list(rom.files)
    arc_id=rom.filenames.idOf('a/0/4/6');arc=ndspy.narc.NARC(rom.files[arc_id]);original=list(arc.files)
    arc.files[3],arc.files[0]=logo_assets(arc.files[4])
    arc.files[25]=psyduck();arc.files[26]=animation('Paddling',[(0,0,0),(-26,15,3),(26,15,3),(0,.6,0)])
    water=Image.open(ART/'water.png').convert('RGB').resize((256,256),Image.Resampling.LANCZOS).quantize(colors=16,dither=Image.Dither.NONE)
    arc.files[38]=water_model(water);arc.files[39]=animation('Current',[(0,0,0)],frames=480,water=True)
    for i in [25,38]:ndspy.model.NSBMD(arc.files[i])
    changed=[i for i,(a,b) in enumerate(zip(original,arc.files)) if a!=b]
    assert changed==[0,3,25,26,38,39]
    rom.files[arc_id]=arc.save();hooks=patch_overlay(rom)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nSwimming title prototype 005\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    target=PROJECT/'build/yellow-heartgold-prototype-005.nds';output=rom.save();target.write_bytes(output)
    check=ndspy.rom.NintendoDSRom(output)
    overlay_id=rom.loadArm9Overlays()[60].fileID
    assert len(check.files)==len(before)
    assert [i for i,(a,b) in enumerate(zip(before,check.files)) if a!=b]==sorted([arc_id,overlay_id])
    assert check.arm9==rom.arm9 and check.arm7==rom.arm7
    patcher=PROJECT/'.tools/xdelta3';patch=target.with_suffix('.xdelta');decoded=PROJECT/'build/title-roundtrip.nds'
    subprocess.run([str(patcher),'-f','-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(patcher),'-f','-d','-s',str(BASE),str(patch),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(output)
    report={'version':'005','output_sha256':sha(output),'patch_sha256':sha(patch.read_bytes()),'preserved_gameplay_from':'004','changed_title_members':changed,'model_bytes':len(arc.files[25]),'water_bytes':len(arc.files[38]),'hooks':hooks,'gameplay_verified':False}
    (PROJECT/'build/title-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
