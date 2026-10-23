"""Separate Mt. Moon actor models and a paired trainer class, without Johto edits."""
import struct
from collections import deque
from PIL import Image
import ndspy.narc
import ndspy.texture
import ndspy.color
import ndspy.code
from build_rom import PROJECT
from opening import events_decode, events_encode, encode_text
from prototype import decode_messages, encode_messages, thumb_bl
from parcel_quest import PH
from viridian_tutorial import TABLE
from starter_properties import append_code
from intro_polish import tiled, replace_ncgr

ART = PROJECT/'art/mtmoon'
CLASS = 129
SPRITES = {'jessie':91, 'james':92, 'helix':93, 'dome':94}
GENDER = 0x020735F8
PAYOUT = 0x0223FBC0
INTRO = 0x02051868


def indexed(image):
    """Convert RGBA source to the native fifteen opaque colors plus index zero."""
    image=image.convert('RGBA')
    opaque=Image.new('RGB',(sum(a>=128 for *_,a in image.getdata()),1))
    opaque.putdata([p[:3] for p in image.getdata() if p[3]>=128])
    colors=opaque.quantize(colors=15,method=Image.Quantize.MAXCOVERAGE)
    palette=colors.getpalette()[:45]
    rgb=[tuple(palette[i:i+3]) for i in range(0,45,3)]
    result=[]
    for r,g,b,a in image.getdata():
        result.append(0 if a<128 else 1+min(range(15),key=lambda i:sum((v-w)**2 for v,w in zip((r,g,b),rgb[i]))))
    words=[0]+[(r//8)|((g//8)<<5)|((b//8)<<10) for r,g,b in rgb]
    return bytes(result),words


def linear(pixels):
    return bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,len(pixels),2))


def battle_image():
    # Port the original Yellow sprite. Only edge-connected white is background;
    # enclosed white pixels in the uniforms remain opaque white.
    im=Image.open(ART/'yellow-jessie-james.png').convert('RGBA')
    w,h=im.size;queue=deque((x,y) for x in range(w) for y in (0,h-1))
    queue.extend((x,y) for y in range(h) for x in (0,w-1));seen=set()
    while queue:
        x,y=queue.popleft()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y))
        if im.getpixel((x,y))[:3]!=(255,255,255):continue
        im.putpixel((x,y),(255,255,255,0))
        queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    target=Image.new('RGBA',(80,80));target.paste(im,((80-w)//2,(80-h)//2))
    return indexed(target)


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    assert struct.unpack_from('<I',d,0xD2C68)[0]==main.sections[1].ramAddress+len(main.sections[1].data)
    overlays=rom.loadArm9Overlays();field=overlays[1];battle=overlays[12]
    previous=struct.unpack_from('<I',field.data,0x021F92FC-field.ramAddress)[0]
    section=main.sections[1];at=previous-section.ramAddress;i=0
    while struct.unpack_from('<H',section.data,at+i*6)[0]!=65535:i+=1
    existing=section.data[at:at+i*6]
    assert not(set(SPRITES.values())&{v[0] for v in struct.iter_unpack('<3H',existing)})
    models_id=rom.filenames.idOf('a/0/8/1');models=ndspy.narc.NARC(rom.files[models_id]);rows=[];added={}
    fossils=Image.open(ART/'fossils.png')
    for name,base in (('jessie',173),('james',174),('helix',94),('dome',94)):
        tex=ndspy.texture.NSBTX(models.files[base])
        im=Image.open(ART/(name+'-sheet.png')) if name in ('jessie','james') else fossils.crop((0 if name=='helix' else 16,0,16 if name=='helix' else 32,16))
        pixels,words=indexed(im)
        tex.palettes[0][1].colors=[ndspy.color.unpack(v) for v in words]
        for label,texture in tex.textures:
            if name in ('jessie','james'):
                n=int(label.split('.')[-1])-1;x=n%4*32;y=n//4*32
                frame=b''.join(pixels[(y+z)*128+x:(y+z)*128+x+32] for z in range(32))
            else:frame=pixels
            texture.data1=linear(frame);texture.isColor0Transparent=True
        model=len(models.files);models.files.append(tex.save());rows.append(struct.pack('<3H',SPRITES[name],model,0));added[name]=dict(sprite=SPRITES[name],model=model)
    rom.files[models_id]=models.save()
    section.data.extend(bytes(-len(section.data)%4));lookup=section.ramAddress+len(section.data)
    section.data.extend(existing+b''.join(rows)+section.data[at+i*6:at+(i+1)*6])
    for pointer in (0x021F92FC,0x021FA280):
        offset=pointer-field.ramAddress;assert struct.unpack_from('<I',field.data,offset)[0]==previous
        struct.pack_into('<I',field.data,offset,lookup)
    events_id=rom.filenames.idOf('a/0/3/2');events=ndspy.narc.NARC(rom.files[events_id])
    eid=struct.unpack_from('<H',d,TABLE+107*24+16)[0];groups=events_decode(events.files[eid])
    for n,row in enumerate(groups[1]):
        actor=struct.unpack_from('<H',row)[0]
        if actor in (22,23,30,31):
            row=bytearray(row);struct.pack_into('<H',row,2,SPRITES[{22:'dome',23:'helix',30:'jessie',31:'james'}[actor]]);groups[1][n]=bytes(row)
    new_eid=len(events.files);events.files.append(events_encode(groups));struct.pack_into('<H',d,TABLE+107*24+16,new_eid);rom.files[events_id]=events.save()
    trainer_id=rom.filenames.idOf('a/0/5/5');trainers=ndspy.narc.NARC(rom.files[trainer_id])
    assert trainers.files[777][1]==55
    row=bytearray(trainers.files[777]);row[1]=CLASS;trainers.files[777]=bytes(row);rom.files[trainer_id]=trainers.save()
    resource_id=rom.filenames.idOf('a/0/5/8');resources=ndspy.narc.NARC(rom.files[resource_id]);assert len(resources.files)==CLASS*5
    pixels,words=battle_image();native=resources.files[55*5:56*5]
    # Native OAM uses 64-byte tile units and six fragments covering 80x80.
    fragments=((0,0,64,64),(64,0,16,32),(64,32,16,32),(0,64,32,16),(32,64,32,16),(64,64,16,16))
    raw=b''.join(tiled(b''.join(pixels[(y+dy)*80+x:(y+dy)*80+x+w] for dy in range(h)),w,h) for x,y,w,h in fragments)
    palette=bytearray(native[1]);palette[40:72]=struct.pack('<16H',*words)
    ncbr_pixels=b''.join(pixels[y*80:y*80+80]*2 for y in range(80));raw_ncbr=linear(ncbr_pixels)
    values=list(struct.unpack('<3200H',raw_ncbr));seed=0x1234
    for n in range(3200):values[n]^=seed&65535;seed=(seed*1103515245+24691)&0xFFFFFFFF
    ncbr=replace_ncgr(native[4],struct.pack('<3200H',*values))
    resources.files.extend((replace_ncgr(native[0],raw),bytes(palette),native[2],native[3],ncbr));rom.files[resource_id]=resources.save()
    texts_id=rom.filenames.idOf('a/0/2/7');texts=ndspy.narc.NARC(rom.files[texts_id])
    for bank in (730,731):
        key,messages=decode_messages(texts.files[bank]);assert len(messages)==CLASS
        # Native personal trainer names are capped at seven characters. Put the
        # complete pair name in the uncapped class label instead.
        messages.extend(decode_messages(encode_text(['JESSIE & JAMES'],PH))[1]);texts.files[bank]=encode_messages(key,messages)
    key,names=decode_messages(texts.files[729]);names[777]=[0xFFFF]
    texts.files[729]=encode_messages(key,names)
    rom.files[texts_id]=texts.save()
    offset=GENDER-0x02000000;assert d[offset:offset+8]==bytes.fromhex('0149085c7047c046')
    table=struct.unpack_from('<I',d,offset+8)[0]
    code,_=append_code(main,f'cmp r0, #129\nbne old\nmovs r0, #0\nbx lr\nold:\nldr r1, original\nldrb r0, [r1,r0]\nbx lr\n.align 2\noriginal: .word {table}\n')
    d[offset:offset+8]=bytes.fromhex('004b1847')+struct.pack('<I',code|1)
    offset=PAYOUT-battle.ramAddress;assert battle.data[offset:offset+4]==bytes.fromhex('42781f49')
    code,_=append_code(main,'ldrb r2,[r0,#1]\ncmp r2,#129\nbne native\nmovs r2,#55\nnative:\nldr r1, money\nbx lr\n.align 2\nmoney: .word 0x0226C4C4\n')
    battle.data[offset:offset+4]=thumb_bl(PAYOUT,code)
    # The new visual class must still use Rocket's transition and battle music.
    # Retain the original lookup for every other class, including Johto's.
    offset=INTRO-0x02000000;assert d[offset:offset+8]==bytes.fromhex('094b002219888905')
    table=struct.unpack_from('<I',d,offset+40)[0]
    code,_=append_code(main,f'cmp r0,#129\nbne old\nmovs r0,#29\nbx lr\nold:\nldr r3, table\nmovs r2,#0\nloop:\nldrh r1,[r3]\nlsls r1,r1,#22\nlsrs r1,r1,#22\ncmp r0,r1\nbne next\nldr r0,table\nlsls r1,r2,#1\nldrh r0,[r0,r1]\nlsls r0,r0,#16\nlsrs r0,r0,#26\nbx lr\nnext:\nadds r2,#1\nadds r3,#2\ncmp r2,#32\nblo loop\nmovs r0,#41\nbx lr\n.align 2\ntable: .word {table}\n')
    d[offset:offset+8]=bytes.fromhex('004b1847')+struct.pack('<I',code|1)
    for overlay in (field,battle):rom.files[overlay.fileID]=overlay.save(compress=overlay.compressed)
    rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)
    struct.pack_into('<I',d,0xD2C68,section.ramAddress+len(section.data));rom.arm9=main.save(compress=True)
    return dict(actor_models=added,lookup=hex(lookup),trainer_class=CLASS,trainer=777,
                battle_portrait='Original Yellow paired portrait ported to native HeartGold resources',
                gender_hook=hex(GENDER),payout_hook=hex(PAYOUT),intro_hook=hex(INTRO),
                native_rocket_payout_preserved=True,native_rocket_music_and_transition_preserved=True,event=new_eid)
