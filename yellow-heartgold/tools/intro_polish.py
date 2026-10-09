"""Prototype 009 intro: FireRed Blue portrait and native-resource shiny Eevee."""
import argparse
import json
import math
import struct
import subprocess
from pathlib import Path
import ndspy.code
import ndspy.lz10
import ndspy.narc
import ndspy.rom
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from build_rom import PROJECT, BASE, EXPECTED, sha
from prototype import thumb_bl

INPUT_SHA='48af56b6369c82911de476437753fae43f8d842bd83a03fd1fcda2caf678f46f'
FIRERED_SHA='729041b940afe031302d630fdbe57c0c145f3f7b6d9b8eca5e98678d0ca4d059'
BLUE_GRAPHICS=0xE60894
BLUE_PALETTE=0xE60B4C
SHINY_SE=1808


def tiled(pixels,w,h):
    assert len(pixels)==w*h and w%8==h%8==0
    return bytes(pixels[(ty+y)*w+tx+x]|pixels[(ty+y)*w+tx+x+1]<<4
                 for ty in range(0,h,8) for tx in range(0,w,8)
                 for y in range(8) for x in range(0,8,2))


def replace_ncgr(old,raw):
    assert old[:4]==b'RGCN' and old[16:20]==b'RAHC'
    b=bytearray(old[:48])+raw
    struct.pack_into('<I',b,8,len(b));struct.pack_into('<I',b,20,len(b)-16)
    struct.pack_into('<I',b,40,len(raw));return bytes(b)


def nitro(signature,block,payload):
    chunk=block+struct.pack('<I',len(payload)+8)+payload
    return signature+struct.pack('<HHIHH',0xFEFF,0x100,16+len(chunk),16,1)+chunk


def cells_encode(cells):
    records=bytearray();oam=bytearray()
    for objects in cells:
        records.extend(struct.pack('<HHI',len(objects),0,len(oam)))
        for obj in objects:oam.extend(struct.pack('<3H',*obj))
    payload=struct.pack('<HH5I',len(cells),0,24,0,0,0,0)+records+oam
    payload+=b'\0'*(-len(payload)%4)
    return nitro(b'RECN',b'KBEC',payload)


def anim_decode(b):
    n=struct.unpack_from('<H',b,24)[0];seq,frames,data=struct.unpack_from('<3I',b,28)
    result=[]
    for i in range(n):
        count,loop,typ,play,offset=struct.unpack_from('<HHIII',b,24+seq+i*16)
        width={0:4,1:16,2:8}[typ&0xFFFF];elements=[]
        for j in range(count):
            at,duration,pad=struct.unpack_from('<IHH',b,24+frames+offset+8*j)
            elements.append((b[24+data+at:24+data+at+width],duration))
        result.append((loop,typ,play,elements))
    return result


def anim_encode(sequences):
    seq=bytearray();frames=bytearray();data=bytearray()
    for loop,typ,play,elements in sequences:
        seq.extend(struct.pack('<HHIII',len(elements),loop,typ,play,len(frames)))
        for element,duration in elements:
            frames.extend(struct.pack('<IHH',len(data),duration,0xBEEF));data.extend(element)
    payload=struct.pack('<HH5I',len(sequences),len(frames)//8,24,24+len(seq),24+len(seq)+len(frames),0,0)+seq+frames+data
    return nitro(b'RNAN',b'KNBA',payload)


def extract_blue(path):
    source=Path(path).read_bytes();assert sha(source)==FIRERED_SHA,'Unsupported FireRed revision'
    art=ndspy.lz10.decompress(source[BLUE_GRAPHICS:BLUE_GRAPHICS+10000])
    palette=ndspy.lz10.decompress(source[BLUE_PALETTE:BLUE_PALETTE+300])
    assert len(art)==2048 and len(palette)==32
    return art,palette


def intro_portrait(rom,art,palette):
    file=rom.filenames.idOf('a/1/2/0');arc=ndspy.narc.NARC(rom.files[file])
    # Reserved Ethan animation frame 2 is unused in HG's static player pictures.
    # Append new art instead of overwriting the original portrait resources.
    canvas=bytes(32*64//2)+art+bytes(32*64//2)
    # BG portrait is 64x128 tiled, with the full 64x64 battle art centered.
    character=len(arc.files);arc.files.append(replace_ncgr(arc.files[12],canvas))
    colors=bytearray(arc.files[16]);colors[40:72]=palette
    palette_id=len(arc.files);arc.files.append(bytes(colors));rom.files[file]=arc.save()
    return character,palette_id


def eevee_art(rom):
    arc=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/0/4')])
    raw=arc.files[133*6+3][48:];assert len(raw)==6400
    words=list(struct.unpack('<3200H',raw));seed=words[0]
    for i in range(3200):words[i]^=seed&65535;seed=(seed*1103515245+24691)&0xFFFFFFFF
    raw=struct.pack('<3200H',*words);pixels=bytes(c for byte in raw for c in [byte&15,byte>>4])
    palette=arc.files[133*6+5][40:72];assert not({14,15}&set(pixels))
    return pixels,palette


def eevee_sequence(rom):
    file=rom.filenames.idOf('a/1/2/0');arc=ndspy.narc.NARC(rom.files[file]);before=list(arc.files)
    pixels,palette=eevee_art(rom);raw=bytearray(arc.files[64][48:]);cells=[]
    def add_image(image,w,h,x,y,shape,size):
        tile=len(raw)//32;raw.extend(tiled(image,w,h));assert tile<1024
        return (y&255|shape<<14,x&511|size<<14,tile)
    # Keep HG's original ball cell and its graphics exactly.
    old=arc.files[65];n,_,offset=struct.unpack_from('<HHI',old,48+16*2)
    ball=[struct.unpack_from('<3H',old,48+3*16+offset+6*i) for i in range(n)]
    fragments=[(0,0,64,64,0,3),(64,0,16,32,2,2),(64,32,16,32,2,2),(0,64,32,16,1,2),(32,64,32,16,1,2),(64,64,16,16,0,1)]
    for pose in [0,1]:
        objects=[]
        for x,y,w,h,shape,size in fragments:
            image=bytes(pixels[(y+py)*160+pose*80+x+px] for py in range(h) for px in range(w))
            objects.append(add_image(image,w,h,x-80,y-72,shape,size))
        cells.append(objects)
    cells.append(ball)
    # Use the texture from HG's actual shiny animation 11, particle resource 31.
    particles=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/9')]);spa=particles.files[31]
    assert spa[:8]==b' APS12_1';assert struct.unpack_from('<HH',spa,8)==(2,1)
    texture=struct.unpack_from('<I',spa,24)[0];assert spa[texture:texture+4]==b' TPS'
    assert struct.unpack_from('<I',spa,texture+4)[0]&0xFFF==0x336
    alpha=spa[texture+32:texture+32+4096]
    stars={}
    for size in [8,16]:
        for color in [14,15]:
            image=bytes((10 if a>=27 else color if a>=6 else 0)
                        for y in range(size) for x in range(size)
                        for a in [alpha[(y*64//size)*64+x*64//size]>>3])
            stars[(size,color)]=add_image(image,size,size,0,0,0,0 if size==8 else 1)
    for frame in range(12):
        objects=list(cells[0])
        for index in range(6):
            # Two waves of rotating star glints, converted to intro-safe 2D cells.
            phase=frame-index//3*2
            if not 0<=phase<=9:continue
            radius=22+phase*2;angle=index*math.pi/3+phase*.14
            size=8 if phase in [0,1,8,9] else 16
            template=stars[(size,14 if index%2==0 else 15)]
            x=round(math.cos(angle)*radius)-40-size//2;y=round(math.sin(angle)*radius)-40-size//2
            objects.append((y&255,x&511|((0 if size==8 else 1)<<14),template[2]))
        cells.append(objects)
    arc.files[64]=replace_ncgr(arc.files[64],bytes(raw));arc.files[65]=cells_encode(cells)
    colors=bytearray(arc.files[63]);colors[40:72]=palette
    # Eevee's two unused palette entries can tint stars without altering its art.
    struct.pack_into('<2H',colors,40+14*2,0x7F01,0x03FF);arc.files[63]=bytes(colors)
    sequences=anim_decode(arc.files[66]);sequences[2]=(0,0x10000,1,[(struct.pack('<HH',3+i,0),3) for i in range(12)]+[(struct.pack('<HH',0,0),4)])
    arc.files[66]=anim_encode(sequences)
    assert [i for i,(a,b) in enumerate(zip(before,arc.files)) if a!=b]==[63,64,65,66]
    rom.files[file]=arc.save();return dict(native_shiny_animation=11,particle_member=31,particle_sha256=sha(spa),sound=SHINY_SE,sparkle_adapter='2D Nitro cell animation',sparkle_frames=40,eevee_species=133)


def patch_overlay(rom,blue_ids):
    overlays=rom.loadArm9Overlays();o=overlays[53];old=bytes(o.data)
    assert old[0x1E94:0x1E96]==b'\xb7\x20'
    assert old[0x1E98:0x1E9C]==thumb_bl(0x021E7798,0x02006218)
    source='''push {r4, r5, r6, lr}
bl 0x02006218
ldr r0, sound
bl 0x0200604C
pop {r4, r5, r6, pc}
.align 2
sound: .word 1808'''
    address=o.ramAddress+len(o.data);o.data.extend(bytes(Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(source,addr=address)[0]))
    o.data[0x1E94:0x1E96]=b'\x85\x20';o.data[0x1E98:0x1E9C]=thumb_bl(0x021E7798,address)
    assert struct.unpack_from('<2I',o.data,0x2DF0+3*8)==(13,16)
    struct.pack_into('<2I',o.data,0x2DF0+3*8,*blue_ids)
    rival_source='\n'.join(line.split('@')[0] for line in (PROJECT/'asm/oak-rival-name-polish.s').read_text().splitlines())
    o.data.extend(b'\0'*(-len(o.data)%4));rival_address=o.ramAddress+len(o.data)
    o.data.extend(bytes(Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(rival_source,addr=rival_address)[0]))
    o.data[0x15C:0x160]=thumb_bl(0x021E5A5C,rival_address)
    assert len(o.data)<0x4000
    rom.files[o.fileID]=o.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    return dict(overlay=53,cry_species=133,release_helper=hex(address),rival_helper=hex(rival_address),blue_pic_ids=list(blue_ids),input_sha256=sha(old),output_sha256=sha(o.data))


def build(firered):
    source=PROJECT/'build/yellow-heartgold-prototype-008.nds';assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));old=ndspy.rom.NintendoDSRom.fromFile(str(source))
    art,palette=extract_blue(firered);effect=eevee_sequence(rom);blue_ids=intro_portrait(rom,art,palette);overlay=patch_overlay(rom,blue_ids)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nShiny Eevee intro prototype 009\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    assert rom.arm9==old.arm9 and rom.arm7==old.arm7
    output=rom.save();target=PROJECT/'build/yellow-heartgold-prototype-009.nds';target.write_bytes(output)
    tool=PROJECT/'.tools/xdelta3';patch=target.with_suffix('.xdelta');decoded=PROJECT/'build/intro-roundtrip.nds'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True)
    subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patch),str(decoded)],check=True);assert sha(decoded.read_bytes())==sha(output)
    report=dict(version='009',base_version='008',output_sha256=sha(output),patch_sha256=sha(patch.read_bytes()),blue_source_sha256=FIRERED_SHA,blue_graphics_offset=hex(BLUE_GRAPHICS),blue_palette_offset=hex(BLUE_PALETTE),blue_dimensions=[64,64],naming_archive_unchanged=True,shiny_effect=effect,overlay=overlay,changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b])
    (PROJECT/'build/intro-polish-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('firered',type=Path);build(parser.parse_args().firered)
