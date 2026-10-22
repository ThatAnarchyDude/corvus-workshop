"""Private floor/cabin connection stage; boarding, actors and other ship areas remain pending."""
import hashlib,json,struct
from pathlib import Path
import ndspy.narc,ndspy.code
from keystone import Ks,KS_ARCH_ARM,KS_MODE_THUMB
from opening import events_decode,events_encode
from viridian_tutorial import TABLE
from ss_anne_banner import SOURCE,SITE,END,assemble as old_banner

NEW_MAPS=(256,257,259,260,261)
SHIP_MAPS=(254,255)+NEW_MAPS
HALL_DOORS=((13,8),(19,8),(30,8),(36,8),(13,14),(19,14))
CABIN_DOORS=((9,11),(23,11),(41,11),(55,11),(73,2),(87,2))
BANNER_SOURCE=SOURCE.replace('cmp r4,#254\nbeq named\ncmp r4,#255\nbeq named',
    'movs r0,r4\nbl 0x0203B36C\ncmp r0,#235\nbeq named')

def banner_code():
    raw=bytes(Ks(KS_ARCH_ARM,KS_MODE_THUMB).asm(BANNER_SOURCE,addr=SITE)[0])
    assert len(raw)<=END-SITE and len(raw)%2==0
    return raw+bytes.fromhex('c046')*((END-SITE-len(raw))//2)

def warp(x,z,destination,anchor):
    return struct.pack('<6H',x,z,destination,anchor,0,0)

def floor_connections():
    groups={}
    # Retain captain return anchor0 from the already tested254/255 pair.
    groups[254]=[warp(49,15,255,0)]+[warp(x,z,260,i) for i,(x,z) in enumerate(HALL_DOORS)]
    groups[254].append(warp(42,9,256,6))
    groups[256]=[warp(x,z,259,i) for i,(x,z) in enumerate(HALL_DOORS)]
    groups[256]+=[warp(24,3,254,7),warp(42,9,257,5)]
    groups[257]=[warp(x,z,261,i) for i,(x,z) in enumerate(HALL_DOORS[:5])]
    groups[257].append(warp(42,9,256,7))
    for cabin,hall,count in ((259,256,6),(260,254,6),(261,257,5)):
        start=1 if hall==254 else 0
        groups[cabin]=[warp(x,z,hall,start+i) for i,(x,z) in enumerate(CABIN_DOORS[:count])]
    return groups

def patch(rom):
    audit=json.loads(Path('yellow-heartgold/build/0030-ship-floor-slots-v1/audit.json').read_text())
    assert not any(audit[k] for k in ('incoming','matrix_refs','raw_warp_matches','source_refs'))
    main=rom.loadArm9();data=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/3/2','a/0/4/1');events,matrices=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    header254=bytes(data[TABLE+254*24:TABLE+255*24]);script,init,text=struct.unpack_from('<3H',header254,6)
    nativehall=struct.unpack_from('<H',data,TABLE+307*24+4)[0]
    paired=struct.unpack_from('<H',data,TABLE+309*24+4)[0]
    native_pair=matrices.files[paired];assert native_pair[:4]==bytes((1,1,0,0))
    land_ids=[]
    for donor in (311,311,309):
        mid=struct.unpack_from('<H',data,TABLE+donor*24+4)[0];raw=matrices.files[mid]
        assert raw[:4]==bytes((1,1,0,0))
        land_ids.append(struct.unpack_from('<H',raw,5+raw[4])[0])
    assert land_ids==[648,648,646]
    room_matrix=bytes((3,1,0,0,native_pair[4]))+native_pair[5:5+native_pair[4]]+struct.pack('<3H',*land_ids)
    connections=floor_connections();rows=[]
    for mid in (254,)+NEW_MAPS:
        at=TABLE+mid*24;before=bytes(data[at:at+24])
        if mid in NEW_MAPS:
            assert before.hex()==audit['placeholder_headers'][str(mid)]
            row=bytearray(header254 if mid in (256,257) else data[TABLE+311*24:TABLE+312*24])
            nm=len(matrices.files);matrices.files.append(matrices.files[nativehall] if mid in (256,257) else room_matrix)
            struct.pack_into('<4H',row,4,nm,script,init,text)
            # Explicit native Vermilion world position; new clones are Kanto interiors.
            move=struct.unpack_from('<H',row,2)[0]&15
            struct.pack_into('<H',row,2,move|(40<<4)|(9<<10))
            row[18]=235;row[19]=(row[19]&0xF0)|9
            struct.pack_into('<I',row,20,struct.unpack_from('<I',row,20)[0]|1)
        else:row=bytearray(before)
        ne=len(events.files);events.files.append(events_encode([[],[],connections[mid],[]]))
        struct.pack_into('<H',row,16,ne);data[at:at+24]=row
        rows.append(dict(map=mid,matrix=struct.unpack_from('<H',row,4)[0],event=ne,warps=[list(struct.unpack('<6H',w)) for w in connections[mid]]))
    # Captain255 event, actor, reward, scripts, text and scenery remain byte-identical.
    for path,archive in zip(paths,(events,matrices)):rom.files[rom.filenames.idOf(path)]=archive.save()
    overlays=rom.loadArm9Overlays();overlay=overlays[1];offset=SITE-overlay.ramAddress
    assert bytes(overlay.data[offset:offset+64])==old_banner()
    overlay.data[offset:offset+64]=banner_code()
    rom.files[overlay.fileID]=overlay.save(compress=overlay.compressed)
    rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays);rom.arm9=main.save(compress=True)
    return dict(maps=rows,ship_maps=list(SHIP_MAPS),native_land_ids=land_ids,passenger_cabins=17,
        isolated_campaign=True,boarding_connected=False,passenger_actors_trainers_pending=True,
        kitchen_bow_3f_pending=True,unused_native_hall_doors_pending=True,
        original_aqua_preserved=True,extra_itcm_bytes=0,native_playtest_pending=True)
