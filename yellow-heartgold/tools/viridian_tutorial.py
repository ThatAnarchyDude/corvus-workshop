"""Prototype 010: Yellow's coffee gate, old-man catching demo, visible Dex handoff."""
import json
import struct
import subprocess
from pathlib import Path
import ndspy.code
import ndspy.color
import ndspy.lz10
import ndspy.narc
import ndspy.rom
import ndspy.texture
from build_rom import PROJECT, BASE, EXPECTED, sha
from opening import Script, actor, trigger, events_decode, events_encode, script_bank, encode_text, talk, end, command
from parcel_quest import (PH, PARCEL_STATE, BOUNDARY, BLUE_HIDE, BALLS_GIVEN, LAB_ADDED,
                         dex_gate, split_bank, oak_parcel as previous_oak_parcel)
from escort import ball_choice, music
from prototype import decode_messages, encode_messages, thumb_bl
from starter_properties import append_code, CMD_TABLE
from intro_polish import FIRERED_SHA, tiled, replace_ncgr

INPUT_SHA='73c6994b7b4e458064397ea2821077f2719f13f36a67565070801e278e70c5a4'
TABLE=0xF6BE0
TUTORIAL_DONE=0xB4F
DEX_HIDE=0xB50
LAB_MIGRATED=0xB51
CITY_MIGRATED=0xB4E
BLOCKER_HIDE=0xB4C
PASSED_HIDE=0xB4D
DEX_SPRITE=88
CITY_LINES=["Grumble... I haven't had my coffee yet!\rYou can't go through here. Come back later.",
 "Ahh, I've had my coffee now and I feel great!\rSure, you can go through! I'm sorry I was so rude to you!\rI see you're using a POKEDEX. I'll show you how to catch POKEMON as my apology.",
 "First, you need to weaken the target POKEMON.\rWatch closely!",
 "Use a POKE BALL after weakening a wild POKEMON.\rKeep some POKE BALLS with you on your adventure!",
 "My coffee has done the trick!\rGood luck catching POKEMON!",
 "Route 2 and VIRIDIAN FOREST are next. They are not open in this prototype yet."]
LAB_LINES=["This is Oak's last starter. You should leave it here.",
 "Two NATIONAL POKEDEXES are waiting on the table.",
 "OAK: These are the NATIONAL POKEDEXES for you two.\rLet me get them from the table."]


def old_man(base, *, interaction=False):
    s=Script().emit(32,TUTORIAL_DONE).jump('finished',1)
    s.emit(96)
    if interaction:s.emit(104)
    s.compare(PARCEL_STATE,2).jump('coffee',5).emit(32,0x6B).jump('coffee',5)
    s.msg(base+1).msg(base+2)
    # Mark only this battle as the old man's demonstration. Johto uses the
    # unchanged native tutorial setup, trainer graphics and names.
    s.emit(41,BOUNDARY,5).emit(1).emit(41,BOUNDARY,0).emit(251)
    s.emit(41,BOUNDARY,6).emit(1).emit(41,BOUNDARY,0)
    s.msg(base+3).movement(12,'aside').emit(95)
    # Keep the walking actor on screen until departure; on the next map entry,
    # the stationary counterpart appears at the exact same final position.
    s.emit(30,TUTORIAL_DONE).emit(30,BLOCKER_HIDE).emit(31,PASSED_HIDE)
    end(s)
    s.label('coffee').msg(base)
    if not interaction:s.movement(255,'back').emit(95)
    end(s)
    s.label('finished')
    if interaction:s.emit(96).emit(104).msg(base+4);end(s)
    else:s.emit(2)
    return s.moves('aside',[(13,1),(15,2),(1,1)]).moves('back',[(13,1)]).finish()


def props_init():
    s=Script().compare(PARCEL_STATE,2).jump('hidden',1)
    s.emit(31,DEX_HIDE).jump('done').label('hidden').emit(30,DEX_HIDE)
    return s.label('done').emit(30,LAB_MIGRATED).finish()


def props_reload():
    s=Script().emit(32,LAB_MIGRATED).jump('raised',1)
    s.compare(PARCEL_STATE,2).jump('hidden',1)
    s.emit(31,DEX_HIDE).emit(100,10).emit(100,11).jump('ready')
    s.label('hidden').emit(30,DEX_HIDE)
    s.label('ready').emit(30,LAB_MIGRATED)
    s.label('raised').emit(41,BOUNDARY,7).emit(1).emit(41,BOUNDARY,0)
    return s.finish()


def city_init():
    s=Script().emit(32,TUTORIAL_DONE).jump('passed',1)
    s.emit(31,BLOCKER_HIDE).emit(30,PASSED_HIDE).jump('done')
    s.label('passed').emit(30,BLOCKER_HIDE).emit(31,PASSED_HIDE)
    return s.label('done').emit(30,CITY_MIGRATED).finish()


def city_reload():
    s=Script().emit(32,CITY_MIGRATED).jump('done',1)
    s.emit(32,TUTORIAL_DONE).jump('passed',1)
    s.emit(31,BLOCKER_HIDE).emit(30,PASSED_HIDE).emit(100,12).jump('done')
    s.label('passed').emit(30,BLOCKER_HIDE).emit(31,PASSED_HIDE).emit(100,13)
    return s.label('done').emit(30,CITY_MIGRATED).finish()


def oak_parcel(base,pickup_message):
    s=Script().emit(96).emit(104).emit(32,0x6A).jump('before_starter',5)
    s.compare(PARCEL_STATE,2).jump('complete',1)
    s.emit(669,459,0x800C).compare(0x800C,0).jump('no_parcel',1)
    s.msg(base).emit(126,459,1,0x800C).compare(0x800C,0).jump('no_parcel',1)
    s.emit(41,PARCEL_STATE,2).msg(base+1)
    music(s,1088).msg(base+2).emit(73,1540).emit(31,BLUE_HIDE).emit(100,9)
    s.movement(9,'arrive').emit(95).msg(base+3)
    music(s,1103).msg(base+4).msg(base+5).msg(pickup_message)
    # Make room if the player spoke to Oak from the north, on his walking path.
    s.emit(105,0x4000,0x4001).compare(0x4000,8).jump('walk',5)
    s.compare(0x4001,5).jump('walk',5)
    s.movement(255,'make_room').emit(95)
    s.label('walk').movement(0,'to_table').emit(95).emit(73,1500)
    s.movement(0,'away_from_table').emit(95)
    s.emit(30,DEX_HIDE).emit(101,10).emit(101,11)
    s.movement(0,'return_to_player').emit(95).emit(104)
    s.emit(291).emit(30,0x6B).emit(477);s.data.append(1);s.emit(0x800C)
    s.emit(78,1187).msg(base+6).emit(79).msg(base+7).msg(base+8)
    music(s,1088).movement(9,'leave').emit(95).emit(73,1540).emit(30,BLUE_HIDE).emit(101,9)
    s.emit(82).msg(base+9);end(s)
    s.label('no_parcel').msg(base+13).emit(282);end(s)
    s.label('complete').emit(32,BALLS_GIVEN).jump('adventure',1)
    s.emit(125,4,5,0x800C).compare(0x800C,0).jump('bag_full',1)
    s.emit(30,BALLS_GIVEN).emit(78,1187).msg(base+10).emit(79).msg(base+11);end(s)
    s.label('bag_full').msg(base+14);end(s)
    s.label('adventure').msg(base+9).emit(282);end(s)
    s.label('before_starter').msg(2);end(s)
    s.moves('arrive',[(12,6),(15,2),(12,1),(2,1)]).moves('leave',[(13,1),(14,2),(13,6)])
    s.moves('make_room',[(15,1),(2,1)]).moves('to_table',[(12,2),(0,1)])
    s.moves('away_from_table',[(13,1)]).moves('return_to_player',[(13,1)])
    return s.finish()


def extract_art(path):
    raw=Path(path).read_bytes();assert sha(raw)==FIRERED_SHA
    return raw[0x369E18:0x369E18+128],raw[0x36D898:0x36D898+32],raw[0xE70EBC:0xE70EBC+8192],ndspy.lz10.decompress(raw[0xE76F34:0xE76F34+200])


def untile(raw,w,h):
    pixels=bytearray(w*h)
    for ty in range(h//8):
        for tx in range(w//8):
            for y in range(8):
                for x in range(8):
                    at=(ty*(w//8)+tx)*32+y*4+x//2
                    pixels[(ty*8+y)*w+tx*8+x]=(raw[at]>>(4*(x%2)))&15
    return pixels


def graphics(rom,main,art):
    dex,dexpal,back,backpal=art
    model_file=rom.filenames.idOf('a/0/8/1');models=ndspy.narc.NARC(rom.files[model_file]);obj=ndspy.texture.NSBTX(models.files[94])
    pixels=untile(dex,16,16);indices=sorted(set(pixels));assert indices[0]==0 and len(indices)<=8
    mapping={c:i for i,c in enumerate(indices)};tex=obj.textures[0][1]
    tex.data1=bytes(mapping[pixels[i]]|mapping[pixels[i+1]]<<4 for i in range(0,256,2))
    colors=struct.unpack('<16H',dexpal);pal=obj.palettes[0][1]
    pal.colors=[ndspy.color.unpack(colors[c]) for c in indices]+[ndspy.color.unpack(0)]*(8-len(indices))
    model_id=len(models.files);models.files.append(obj.save());rom.files[model_file]=models.save()
    # Relocate the complete graphics lookup rather than repurpose a Johto sprite.
    overlays=rom.loadArm9Overlays();o=overlays[1];table_address=0x022074A8;at=table_address-o.ramAddress;rows=bytearray();ids=[]
    while True:
        record=o.data[at+len(rows):at+len(rows)+6];sid=struct.unpack_from('<H',record)[0]
        if sid==65535:break
        ids.append(sid);rows.extend(record)
    assert DEX_SPRITE not in ids
    rows.extend(struct.pack('<3H',DEX_SPRITE,model_id,0x420));rows.extend(record)
    main.sections[1].data.extend(b'\0'*(-len(main.sections[1].data)%4));new_address=main.sections[1].ramAddress+len(main.sections[1].data);main.sections[1].data.extend(rows)
    for address in [0x021F92FC,0x021FA280]:
        at=address-o.ramAddress;assert struct.unpack_from('<I',o.data,at)[0]==table_address
        struct.pack_into('<I',o.data,at,new_address)
    rom.files[o.fileID]=o.save(compress=True);rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    # Append a separate old-man trainer-back bank. Original Johto graphics stay.
    file=rom.filenames.idOf('a/0/0/6');bank=ndspy.narc.NARC(rom.files[file]);back_id=len(bank.files)//5;assert len(bank.files)%5==0
    old=list(bank.files[:5]);pixels=untile(back,64,256);frames=[]
    fragments=[(0,0,64,64),(64,0,16,32),(64,32,16,32),(0,64,32,16),(32,64,32,16),(64,64,16,16)]
    for pose in [0,0,1,1,2,2,3,3]:
        canvas=bytearray(80*80)
        for y in range(64):canvas[(y+16)*80+8:(y+16)*80+72]=pixels[(pose*64+y)*64:(pose*64+y+1)*64]
        frames.append(canvas)
    raw=b''.join(tiled(bytes(frame[(y+py)*80+x+px] for py in range(h) for px in range(w)),w,h)
                  for frame in frames for x,y,w,h in fragments)
    assert len(raw)==25600;old[0]=replace_ncgr(old[0],raw)
    colors=bytearray(old[1]);colors[40:]=backpal*16;old[1]=bytes(colors)
    pair=bytes(frames[0][y*80+x] if x<80 else frames[-1][y*80+x-80] for y in range(80) for x in range(160))
    raw=bytes(pair[i]|pair[i+1]<<4 for i in range(0,len(pair),2));words=struct.unpack('<3200H',raw);seed=0x1234;enc=[]
    for value in words:enc.append(value^(seed&65535));seed=(seed*1103515245+24691)&0xFFFFFFFF
    old[4]=old[4][:48]+struct.pack('<3200H',*enc);bank.files.extend(old);rom.files[file]=bank.save()
    return dict(dex_sprite=DEX_SPRITE,dex_model=model_id,sprite_table=hex(new_address),sprite_records_preserved=len(ids),old_man_back=back_id)


def hooks(main,back_id):
    data=main.sections[0].data;main.sections[1].data.extend(b'\0'*(-len(main.sections[1].data)%4))
    flag=main.sections[1].ramAddress+len(main.sections[1].data);main.sections[1].data.extend(bytes(4));previous=struct.unpack_from('<I',data,CMD_TABLE+4)[0]
    source=f'''push {{r4, r5, r6, lr}}
movs r4, r0
adds r0, #128
ldr r5, [r0]
movs r0, r5
ldr r1, variable
bl 0x020403AC
movs r6, r0
cmp r0, #5
beq start
cmp r0, #6
beq stop
cmp r0, #7
beq raise
movs r0, r4
ldr r3, previous
blx r3
cmp r6, #2
beq raise
b done
start:
ldr r1, flag
movs r0, #1
str r0, [r1]
b done
stop:
ldr r1, flag
movs r0, #0
str r0, [r1]
b done
raise:
movs r6, #10
loop:
movs r0, r5
movs r1, r6
bl 0x02041C70
cmp r0, #0
beq next
ldr r1, [r0]
movs r2, #1
lsls r2, r2, #23
bics r1, r2
str r1, [r0]
adds r0, #80
movs r1, #0
str r1, [r0]
str r1, [r0, #12]
str r1, [r0, #24]
str r1, [r0, #36]
movs r1, #16
lsls r1, r1, #12
str r1, [r0, #60]
next:
adds r6, #1
cmp r6, #12
blo loop
done:
movs r0, #0
pop {{r4, r5, r6, pc}}
.align 2
variable: .word {BOUNDARY}
previous: .word {previous}
flag: .word {flag}'''
    dummy,_=append_code(main,source);struct.pack_into('<I',data,CMD_TABLE+4,dummy|1)
    source=f'''push {{r4, lr}}
ldr r3, flag
ldr r3, [r3]
cmp r3, #0
beq native
movs r0, #{back_id}
pop {{r4, pc}}
native:
bl 0x0207280C
pop {{r4, pc}}
.align 2
flag: .word {flag}'''
    back,_=append_code(main,source);assert data[0x70D66:0x70D6A]==thumb_bl(0x02070D66,0x0207280C);data[0x70D66:0x70D6A]=thumb_bl(0x02070D66,back)
    source=f'''push {{r4, lr}}
ldr r3, flag
ldr r3, [r3]
cmp r3, #0
beq native
movs r1, #2
native:
bl 0x0200BB6C
pop {{r4, pc}}
.align 2
flag: .word {flag}'''
    name,_=append_code(main,source);assert data[0x51B00:0x51B04]==thumb_bl(0x02051B00,0x0200BB6C);data[0x51B00:0x51B04]=thumb_bl(0x02051B00,name)
    return dict(dummy=hex(dummy),previous_dummy=hex(previous),mode_flag=hex(flag),back_hook=hex(back),name_hook=hex(name))


def patch(rom,firered):
    main=rom.loadArm9();main.sections[0].data=bytearray(main.sections[0].data);data=main.sections[0].data
    previous_end=main.sections[1].ramAddress+len(main.sections[1].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2'];arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths};scripts,texts,events=[arcs[p] for p in paths];originals={p:list(a.files) for p,a in arcs.items()}
    art=graphics(rom,main,extract_art(firered));hook=hooks(main,art['old_man_back'])
    key,msg=decode_messages(texts.files[445]);assert len(msg)==2;msg.extend(decode_messages(encode_text(['OLD MAN'],PH))[1]);texts.files[445]=encode_messages(key,msg)
    mappings=[]
    for map_id in [505,50]:
        rec=TABLE+map_id*24;sid,iid,tid=struct.unpack_from('<3H',data,rec+6);eid=struct.unpack_from('<H',data,rec+16)[0]
        bank=split_bank(scripts.files[sid]);key,msg=decode_messages(texts.files[tid]);groups=events_decode(events.files[eid]);base=len(msg)
        if map_id==505:
            msg.extend(decode_messages(encode_text(LAB_LINES,PH))[1]);parcel_base=base-len(LAB_ADDED)
            assert bank[0].startswith(previous_oak_parcel(parcel_base))
            bank[0]=oak_parcel(parcel_base,base+2)
            for i in range(3):
                code=ball_choice(i,grant_dex=False);assert bank[15+i].startswith(code)
                needle=command(45)+bytes([19]);assert code.count(needle)==1
                bank[15+i]=code.replace(needle,command(45)+bytes([base]))
            bank[14]=props_init()+bank[14];bank[19]=props_reload()+bank[19]
            groups[1].extend([actor(10,DEX_SPRITE,len(bank)+1,7,3,DEX_HIDE,0),actor(11,DEX_SPRITE,len(bank)+1,8,3,DEX_HIDE,0)])
            bank.append(talk(base+1));init_id=15;reload_id=20
        else:
            msg.extend(decode_messages(encode_text(CITY_LINES,PH))[1]);auto_id=len(bank)+1;bank.append(old_man(base));talk_id=len(bank)+1;bank.append(old_man(base,interaction=True))
            groups[1].extend([actor(12,330,talk_id,1032,235,BLOCKER_HIDE,1),actor(13,330,talk_id,1034,236,PASSED_HIDE,1)])
            groups[3].append(trigger(auto_id,1032,236,1,BOUNDARY,0))
            bank[11]=city_init()+bank[11]
            reload_id=len(bank)+1;bank.append(city_reload()+dex_gate());init_id=12
            # The existing prototype boundary stays beyond the now-passable old man.
            messages=decode_messages(encode_text([CITY_LINES[-1]],PH))[1];msg[6]=messages[0]
        new_sid=len(scripts.files);scripts.files.append(script_bank(bank));new_iid=len(scripts.files)
        scripts.files.append(struct.pack('<BHHBHH',2,init_id,0,3,reload_id,0)+b'\0\0')
        new_tid=len(texts.files);texts.files.append(encode_messages(key,msg));new_eid=len(events.files);events.files.append(events_encode(groups))
        struct.pack_into('<3H',data,rec+6,new_sid,new_iid,new_tid);struct.pack_into('<H',data,rec+16,new_eid)
        mappings.append(dict(map_id=map_id,script=new_sid,init=new_iid,text=new_tid,event=new_eid))
    assert struct.unpack_from('<I',data,0xD2C68)[0]==previous_end
    main.sections[1].data.extend(b'\0'*(-len(main.sections[1].data)%4));struct.pack_into('<I',data,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
    assert len(main.sections[1].data)<0x8000;rom.arm9=main.save(compress=True)
    for path,arc in arcs.items():
        assert all(before==arc.files[i] for i,before in enumerate(originals[path]) if not(path=='a/0/2/7' and i==445))
        rom.files[rom.filenames.idOf(path)]=arc.save()
    return dict(mappings=mappings,graphics=art,hooks=hook,flags={'tutorial':TUTORIAL_DONE,'dex_props':DEX_HIDE,'lab_migration':LAB_MIGRATED,'city_migration':CITY_MIGRATED},preserved_original_map_members=True)


def build(firered):
    source=PROJECT/'build/yellow-heartgold-prototype-009.nds';assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));old=ndspy.rom.NintendoDSRom.fromFile(str(source));report=patch(rom,firered)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nViridian tutorial prototype 010\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    output=rom.save();target=PROJECT/'build/yellow-heartgold-prototype-010.nds';target.write_bytes(output);patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/tutorial-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True);subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True);assert sha(decoded.read_bytes())==sha(output)
    assert rom.arm7==old.arm7
    report.update(version='010',input_sha256=INPUT_SHA,output_sha256=sha(output),patch_sha256=sha(patchfile.read_bytes()),changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b]);(PROJECT/'build/viridian-tutorial-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('firered',type=Path);build(parser.parse_args().firered)
