"""Prototype 011: unavoidable coffee gate and native intro panel/pose fixes."""
import json,struct,subprocess
from pathlib import Path
import ndspy.rom,ndspy.narc,ndspy.code,ndspy.texture,ndspy.color
from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
from build_rom import PROJECT,BASE,EXPECTED,sha
from intro_polish import FIRERED_SHA,extract_blue,replace_ncgr,cells_encode,anim_decode,anim_encode
from viridian_tutorial import (TABLE,TUTORIAL_DONE,BLOCKER_HIDE,PASSED_HIDE,untile)
from parcel_quest import split_bank,PARCEL_STATE,BOUNDARY,dex_gate
from opening import Script,command,end,events_decode,events_encode,script_bank,actor,trigger
from prototype import thumb_bl
from starter_properties import append_code,CMD_TABLE
INPUT_SHA='f9e25b1a196c81d879350d57bbb2b870bd43a596badd7a6f4a8c6f0a0965757e'
GATE_MIGRATED=0xB4B
LYING_SPRITE=89
GATE_X,GATE_Z=1027,235
SIDE_X,SIDE_Z=1029,237
BARRIER_TILES=[(x,GATE_Z) for x in [1021,1024,1025,1026,1028,1029,1032]]


def cells_decode(b):
    n,typ,off=struct.unpack_from('<HHI',b,24);width=16 if typ&1 else 8
    result=[]
    for i in range(n):
        count,_,at=struct.unpack_from('<HHI',b,24+off+i*width)
        result.append([struct.unpack_from('<3H',b,24+off+n*width+at+j*6) for j in range(count)])
    return result


def intro_fix(rom,firered):
    art,pal=extract_blue(firered);file=rom.filenames.idOf('a/1/2/0');arc=ndspy.narc.NARC(rom.files[file])
    # Keep player sprite banks intact. Render Blue inside the same SUB BG3
    # rectangle, using dedicated appended character and screen resources.
    char_id=len(arc.files);blue=bytearray();tile_palettes=[]
    # BG3 is the lowest plane, so transparent OBJ color zero needs the frame
    # fill color. Use two palettes to retain every original Blue color exactly.
    for tile in range(64):
        data=art[tile*32:(tile+1)*32];indices={v for b in data for v in [b&15,b>>4]}
        fill=5 if 13 in indices else 13;slot=10 if fill==5 else 6
        assert fill not in indices;tile_palettes.append(slot)
        blue.extend((fill if (b&15)==0 else b&15)|((fill if (b>>4)==0 else b>>4)<<4) for b in data)
    raw=arc.files[32][48:48+5120]+blue
    chars=bytearray(replace_ncgr(arc.files[32],raw));struct.pack_into('<H',chars,14,1)
    arc.files.append(chars);screens=[]
    for gender in [0,1]:
        screen=bytearray(arc.files[51]);assert screen[:4]==b'RCSN'
        tiles=list(struct.unpack_from('<1024H',screen,36))
        for y in range(23):
            for x in range(16):tiles[y*32+16*(gender^1)+x]=1
        for y in range(8):
            for x in range(8):
                tile=y*8+x;tiles[(9+y)*32+4+16*gender+x]=(5120//32+tile)|(tile_palettes[tile]<<12)
        struct.pack_into('<1024H',screen,36,*tiles);screens.append(len(arc.files));arc.files.append(screen)
    palettes=[]
    for fill in [13,5]:
        colors=bytearray(arc.files[68]);struct.pack_into('<H',colors,40+fill*2,0x229B);palettes.append(len(arc.files));arc.files.append(colors)
    # Match Marill's 80x80 cell origin. Keep its ball-release path, and carry
    # the final (-44,+70) transform into every sparkle cell and the rest pose.
    cells=cells_decode(arc.files[65])
    for i,objs in enumerate(cells):
        if i==2:continue
        for j,(a0,a1,a2) in enumerate(objs):
            x=a1&511;x=x-512 if x>=256 else x
            cells[i][j]=(a0,(a1&~511)|((x+40)&511),a2)
    arc.files[65]=cells_encode(cells)
    seq=anim_decode(arc.files[66]);seq[2]=(0,0x10002,1,[(struct.pack('<HHhh',3+i,0,-44,70),3) for i in range(12)]+[(struct.pack('<HHhh',0,0,-44,70),4)])
    arc.files[66]=anim_encode(seq);rom.files[file]=arc.save()
    overlays=rom.loadArm9Overlays();o=overlays[53];ks=Ks(KS_ARCH_ARM,KS_MODE_THUMB)
    def asm(file,**replace):
        text=(PROJECT/'asm'/file).read_text()
        for k,v in replace.items():text=text.replace(k,str(v))
        text='\n'.join(line.split('@')[0] for line in text.splitlines())
        o.data.extend(bytes(-len(o.data)%4));addr=o.ramAddress+len(o.data);o.data.extend(bytes(ks.asm(text,addr=addr)[0]));return addr
    panel=asm('oak-blue-touch-panel.s',BLUE_CHAR=char_id,BLUE_SCREEN=screens[0],BLUE_PALETTE_A=palettes[0],BLUE_PALETTE_B=palettes[1]);wrapper=asm('oak-rival-touch-panel.s',BLUE_PANEL=hex(panel))
    o.data[0x15C:0x160]=thumb_bl(0x021E5A5C,wrapper);assert len(o.data)<0x4000
    rom.files[o.fileID]=o.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    return dict(blue_panel=hex(panel),rival_wrapper=hex(wrapper),blue_character=char_id,blue_screens=screens,blue_palettes=palettes,player_resources_preserved=True,eevee_origin=[-40,-72],eevee_rest_translation=[-44,70])


def collision_barriers(rom):
    mf=rom.filenames.idOf('a/0/4/1');lf=rom.filenames.idOf('a/0/6/5')
    matrices=ndspy.narc.NARC(rom.files[mf]);lands=ndspy.narc.NARC(rom.files[lf]);matrix=bytearray(matrices.files[0]);w,h,headers,heights,name=matrix[:5];at=5+name+w*h*(2*headers+heights)
    clones={};records=[]
    for x,z in BARRIER_TILES:
        cell=z//32*w+x//32;pos=at+2*cell
        if cell not in clones:
            old=struct.unpack_from('<H',matrix,pos)[0];new=len(lands.files);lands.files.append(bytearray(lands.files[old]));struct.pack_into('<H',matrix,pos,new);clones[cell]=new;records.append(dict(cell=cell,old_land=old,new_land=new))
        b=lands.files[clones[cell]];i=20+2*((z%32)*32+x%32);value=struct.unpack_from('<H',b,i)[0];assert not value&0x8000;struct.pack_into('<H',b,i,value|0x8000)
    matrices.files[0]=matrix;rom.files[mf]=matrices.save();rom.files[lf]=lands.save();return records


def lying_model(rom,main,firered):
    raw=Path(firered).read_bytes();assert sha(raw)==FIRERED_SHA
    pixels=untile(raw[0x375B18:0x375B18+512],32,32);colors=struct.unpack_from('<16H',raw,0x36D8B8)
    file=rom.filenames.idOf('a/0/8/1');models=ndspy.narc.NARC(rom.files[file]);tex=ndspy.texture.NSBTX(models.files[128]);packed=bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,1024,2))
    for _,t in tex.textures:assert t.format==ndspy.texture.TextureFormat.I4;t.data1=packed
    tex.palettes[0][1].colors=[ndspy.color.unpack(c) for c in colors]
    model=len(models.files);models.files.append(tex.save());rom.files[file]=models.save()
    overlays=rom.loadArm9Overlays();o=overlays[1];old_address=struct.unpack_from('<I',o.data,0x021F92FC-o.ramAddress)[0];at=old_address-main.sections[1].ramAddress;rows=bytearray();i=0
    while struct.unpack_from('<H',main.sections[1].data,at+i*6)[0]!=65535:
        rows.extend(main.sections[1].data[at+i*6:at+(i+1)*6]);i+=1
    rows.extend(struct.pack('<3H',LYING_SPRITE,model,0));rows.extend(main.sections[1].data[at+i*6:at+(i+1)*6]);main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));address=main.sections[1].ramAddress+len(main.sections[1].data);main.sections[1].data.extend(rows)
    for p in [0x021F92FC,0x021FA280]:assert struct.unpack_from('<I',o.data,p-o.ramAddress)[0]==old_address;struct.pack_into('<I',o.data,p-o.ramAddress,address)
    rom.files[o.fileID]=o.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    return dict(sprite=LYING_SPRITE,model=model,lookup=hex(address),source_graphics='0x375b18',source_palette='0x36d8b8')


def wake_hook(main):
    previous=struct.unpack_from('<I',main.sections[0].data,CMD_TABLE+4)[0]
    source=f'''push {{r4, lr}}
movs r4, r0
adds r0, #128
ldr r0, [r0]
ldr r1, variable
bl 0x020403AC
cmp r0, #8
bne delegate
movs r0, r4
adds r0, #128
ldr r0, [r0]
movs r1, #12
bl 0x02041C70
cmp r0, #0
beq done
ldr r1, sprite
bl 0x0205E38C
done:
movs r0, #0
pop {{r4, pc}}
delegate:
movs r0, r4
ldr r3, previous
blx r3
pop {{r4, pc}}
.align 2
variable: .word {BOUNDARY}
sprite: .word 330
previous: .word {previous}'''
    addr,_=append_code(main,source);struct.pack_into('<I',main.sections[0].data,CMD_TABLE+4,addr|1);return hex(addr)


def old_man(base,interaction=False,clear_objects=(),companion=None,companion_after=None):
    s=Script().emit(32,TUTORIAL_DONE).jump('finished',1).emit(96)
    if interaction:s.emit(104)
    s.compare(PARCEL_STATE,2).jump('coffee',5).emit(32,0x6B).jump('coffee',5)
    s.emit(41,BOUNDARY,8).emit(1).emit(41,BOUNDARY,0)
    s.movement(12,'face_player').emit(95).msg(base+1).msg(base+2)
    s.emit(41,BOUNDARY,5).emit(1).emit(41,BOUNDARY,0).emit(251)
    s.emit(41,BOUNDARY,6).emit(1).emit(41,BOUNDARY,0).msg(base+3)
    s.emit(105,0x4000,0x4001).compare(0x4000,GATE_X).jump('aside',5)
    s.compare(0x4001,GATE_Z+1).jump('aside',5).movement(255,'make_room').emit(95)
    s.label('aside').movement(12,'aside_move').emit(95)
    if companion:s.movement(companion[0],'companion_aside').emit(95)
    s.emit(30,TUTORIAL_DONE).emit(30,BLOCKER_HIDE).emit(31,PASSED_HIDE)
    for obj in clear_objects:s.emit(101,obj)
    if companion_after:s.emit(101,companion[0]).emit(100,companion_after)
    end(s)
    s.label('coffee').msg(base)
    if not interaction:s.movement(255,'back').emit(95)
    end(s)
    s.label('finished')
    if interaction:s.emit(96).emit(104).msg(base+4);end(s)
    else:s.emit(2)
    s.moves('face_player',[(1,1)]).moves('make_room',[(14,1),(0,1)]).moves('aside_move',[(13,2),(15,2),(1,1)]).moves('back',[(13,1)])
    if companion:s.moves('companion_aside',companion[1])
    return s.finish()


def migration():
    s=Script().emit(32,GATE_MIGRATED).jump('done',1)
    s.emit(101,12).emit(101,13).emit(32,TUTORIAL_DONE).jump('passed',1)
    s.emit(31,BLOCKER_HIDE).emit(30,PASSED_HIDE).emit(100,12).jump('done')
    s.label('passed').emit(30,BLOCKER_HIDE).emit(31,PASSED_HIDE).emit(100,13)
    return s.label('done').emit(30,GATE_MIGRATED).finish()


def gate_fix(rom,main):
    data=main.sections[0].data;rec=TABLE+50*24;sid,iid,tid=struct.unpack_from('<3H',data,rec+6);eid=struct.unpack_from('<H',data,rec+16)[0]
    sf=rom.filenames.idOf('a/0/1/2');ef=rom.filenames.idOf('a/0/3/2');scripts=ndspy.narc.NARC(rom.files[sf]);events=ndspy.narc.NARC(rom.files[ef]);bank=split_bank(scripts.files[sid]);groups=events_decode(events.files[eid]);assert len(bank)==16
    # Existing message indices and unrelated city scripts are unchanged.
    bank[13]=old_man(12);bank[14]=old_man(12,True)
    bank[11]=command(30,GATE_MIGRATED)+bank[11];bank[15]=migration()+bank[15]
    for i,a in enumerate(groups[1]):
        ident=struct.unpack_from('<H',a)[0]
        if ident==12:groups[1][i]=actor(12,LYING_SPRITE,15,GATE_X,GATE_Z,BLOCKER_HIDE,0)
        if ident==13:groups[1][i]=actor(13,330,15,SIDE_X,SIDE_Z,PASSED_HIDE,1)
    # The auto trigger is script 14; the talk entry is 15.
    for i,t in enumerate(groups[3]):
        if struct.unpack_from('<H',t)[0]==14:groups[3][i]=trigger(14,GATE_X,GATE_Z+1,1,BOUNDARY,0)
    new_sid=len(scripts.files);scripts.files.append(script_bank(bank));new_iid=len(scripts.files);scripts.files.append(scripts.files[iid]);new_eid=len(events.files);events.files.append(events_encode(groups));struct.pack_into('<HH',data,rec+6,new_sid,new_iid);struct.pack_into('<H',data,rec+16,new_eid)
    rom.files[sf]=scripts.save();rom.files[ef]=events.save();return dict(script=new_sid,init=new_iid,event=new_eid,gate=[GATE_X,GATE_Z],cleared_position=[SIDE_X,SIDE_Z],barriers=BARRIER_TILES,migration_flag=GATE_MIGRATED)


def build(firered):
    source=PROJECT/'build/yellow-heartgold-prototype-010.nds';assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));old=ndspy.rom.NintendoDSRom.fromFile(str(source));report={'intro':intro_fix(rom,firered)}
    main=rom.loadArm9();main.sections[0].data=bytearray(main.sections[0].data);end=main.sections[1].ramAddress+len(main.sections[1].data)
    report['lying']=lying_model(rom,main,firered);report['wake_hook']=wake_hook(main);report['gate']=gate_fix(rom,main);report['land_clones']=collision_barriers(rom)
    assert struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0]==end
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));struct.pack_into('<I',main.sections[0].data,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));assert len(main.sections[1].data)<0x8000;rom.arm9=main.save(compress=True)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nOpening corrections prototype 011\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    assert rom.arm7==old.arm7;target=PROJECT/'build/yellow-heartgold-prototype-011.nds';target.write_bytes(rom.save());patch=target.with_suffix('.xdelta');decoded=PROJECT/'build/corrections-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patch)],check=True);subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patch),str(decoded)],check=True);assert sha(decoded.read_bytes())==sha(target.read_bytes())
    report.update(version='011',base_version='010',input_sha256=INPUT_SHA,output_sha256=sha(target.read_bytes()),patch_sha256=sha(patch.read_bytes()),changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b]);(PROJECT/'build/opening-corrections-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('firered',type=Path);build(parser.parse_args().firered)
