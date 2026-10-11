"""Manual Kanto sign interactions and visible Viridian Forest information boards."""
import struct
import ndspy.narc
from opening import Script,end,events_decode,events_encode,script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE

FOREST_BOARDS=((26,41),(12,46),(47,46),(49,18),(32,58),(11,17))
# Terrain heights measured through native field warps from the 0018 save.
BOARD_HEIGHTS=(3,4,3,2,2,2)


def sign(index):
    # Background events have no NPC to turn towards the player.
    return end(Script().emit(96).msg(index)).finish()


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/3/2','a/0/4/1','a/0/6/5')
    scripts,events,matrices,lands=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    changes=[]
    for m in range(540):
        rec=TABLE+m*24
        if not d[rec+20]&1:continue
        eid=struct.unpack_from('<H',d,rec+16)[0];groups=events_decode(events.files[eid]);changed=False
        for i,row in enumerate(groups[0]):
            script,kind,x,z,y,direction=struct.unpack('<HHiiiH2x',row)
            if kind==1:
                groups[0][i]=struct.pack('<HHiiiH2x',script,0,x,z,y,direction);changed=True
        if m in (10,414):
            row=bytearray(groups[0][0]);struct.pack_into('<i',row,4,1029 if m==10 else 1047);groups[0][0]=bytes(row);changed=True
        if m==147:
            for i,row in enumerate(groups[0]):
                if struct.unpack_from('<2i',row,4)==(32,57):
                    row=bytearray(row);struct.pack_into('<i',row,8,58);groups[0][i]=bytes(row);changed=True
        # Converted outdoor sign entries all use plain message scripts.
        if m in (10,414,147,51,11):
            sid=struct.unpack_from('<H',d,rec+6)[0];bank=split_bank(scripts.files[sid]);replaced=[]
            for row in groups[0]:
                entry,kind=struct.unpack_from('<2H',row)
                if kind!=0:continue
                body=bank[entry-1]
                assert body[:4]==struct.pack('<2H',96,104)
                bank[entry-1]=body[:2]+body[4:];replaced.append(entry)
            ns=len(scripts.files);scripts.files.append(script_bank(bank));struct.pack_into('<H',d,rec+6,ns)
            changes.append(dict(map=m,manual_signs=replaced,original_script=sid,script=ns))
        if changed:
            ne=len(events.files);events.files.append(events_encode(groups));struct.pack_into('<H',d,rec+16,ne)
            changes.append(dict(map=m,original_event=eid,event=ne))
    # The six supposed Forest boards were invisible hidden-item positions.
    # Native Forest area already loads model 31 and its board textures.
    template=None
    for raw in lands.files:
        if len(raw)<20:continue
        ps,bs=struct.unpack_from('<2I',raw)
        if 20+ps+bs>len(raw):continue
        for at in range(20+ps,20+ps+bs,48):
            if struct.unpack_from('<I',raw,at)[0]==31:template=bytearray(raw[at:at+48]);break
        if template is not None:break
    assert template is not None
    rec=TABLE+147*24;old_mid=struct.unpack_from('<H',d,rec+4)[0];matrix=bytearray(matrices.files[old_mid]);w,h,headers,heights,n=matrix[:5]
    offset=5+n+(2*w*h if headers else 0)+(w*h if heights else 0);clones={};props=[]
    for (x,z),height in zip(FOREST_BOARDS,BOARD_HEIGHTS):
        cell=z//32*w+x//32
        if cell not in clones:
            old_lid=struct.unpack_from('<H',matrix,offset+cell*2)[0];lid=len(lands.files);lands.files.append(bytearray(lands.files[old_lid]));struct.pack_into('<H',matrix,offset+cell*2,lid);clones[cell]=lid
        raw=lands.files[clones[cell]];ps,bs=struct.unpack_from('<2I',raw);row=bytearray(template)
        struct.pack_into('<3i',row,4,int((x%32-15.5)*65536),height*65536,int((z%32-15.5)*65536))
        raw[20+ps+bs:20+ps+bs]=row;struct.pack_into('<I',raw,4,bs+48)
        at=20+2*(z%32*32+x%32);value=struct.unpack_from('<H',raw,at)[0];struct.pack_into('<H',raw,at,value|0x8000)
        props.append(dict(x=x,z=z,height=height,model=31,land=clones[cell],previous_permission=value))
    mid=len(matrices.files);matrices.files.append(matrix);struct.pack_into('<H',d,rec+4,mid)
    for path,a in zip(paths,(scripts,events,matrices,lands)):rom.files[rom.filenames.idOf(path)]=a.save()
    rom.arm9=main.save(compress=True)
    return dict(manual_sign_changes=changes,forest_boards=props,forest_original_matrix=old_mid,forest_matrix=mid)
