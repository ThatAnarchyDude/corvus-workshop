"""Copied native lower passages connect each ship hall's separated regions."""
import json,struct
from pathlib import Path
import ndspy.narc
from opening import events_encode
from ss_anne_floors import HALL_DOORS,warp
from viridian_tutorial import TABLE

def routes():
    groups={}
    groups[254]=[warp(49,15,255,0)]+[warp(x,z,260,i) for i,(x,z) in enumerate(HALL_DOORS)]
    groups[254]+=[warp(24,19,256,6),warp(24,3,258,3),warp(42,9,258,4)]
    groups[256]=[warp(x,z,259,i) for i,(x,z) in enumerate(HALL_DOORS)]
    groups[256]+=[warp(30,14,254,7),warp(36,14,257,5),warp(24,3,258,0),warp(42,9,258,1)]
    groups[257]=[warp(x,z,261,i) for i,(x,z) in enumerate(HALL_DOORS[:5])]
    groups[257]+=[warp(24,19,256,7),warp(24,3,258,6),warp(42,9,258,7)]
    groups[258]=[]
    for offset,hall,left,right in ((0,256,8,9),(64,254,8,9),(128,257,6,7)):
        groups[258]+=[warp(24+offset,3,hall,left),warp(42+offset,9,hall,right),warp(42+offset,8,hall,right)]
    return groups

def patch(rom):
    audit=json.loads(Path('yellow-heartgold/build/0030-ship-bridge-slot-v1/audit.json').read_text())
    assert not any(audit[k] for k in ('incoming','matrix_refs','raw_warp_matches','source_refs'))
    main=rom.loadArm9();data=main.sections[0].data=bytearray(main.sections[0].data)
    events,matrices=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in ('a/0/3/2','a/0/4/1')]
    at=TABLE+258*24;assert bytes(data[at:at+24]).hex()==audit['placeholder_headers']['258']
    donor=bytearray(data[TABLE+329*24:TABLE+330*24]);mid=struct.unpack_from('<H',donor,4)[0];raw=matrices.files[mid]
    assert raw[:4]==bytes((2,1,0,0));lands=struct.unpack_from('<2H',raw,5+raw[4]);assert lands==(650,651)
    nm=len(matrices.files);matrices.files.append(bytes((6,1,0,0,raw[4]))+raw[5:5+raw[4]]+struct.pack('<6H',*(lands*3)))
    source=data[TABLE+254*24:TABLE+255*24]
    donor[2:4]=source[2:4];donor[6:12]=source[6:12];donor[18:20]=source[18:20]
    struct.pack_into('<H',donor,4,nm);struct.pack_into('<I',donor,20,struct.unpack_from('<I',donor,20)[0]|1)
    data[at:at+24]=donor
    records=[]
    for hall,warps in routes().items():
        eid=len(events.files);events.files.append(events_encode([[],[],warps,[]]));struct.pack_into('<H',data,TABLE+hall*24+16,eid)
        records.append(dict(map=hall,event=eid,warps=[list(struct.unpack('<6H',w)) for w in warps]))
    for path,arc in zip(('a/0/3/2','a/0/4/1'),(events,matrices)):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(maps=records,bridge_matrix=nm,bridge_land_ids=list(lands)*3,passenger_cabins=17,
        native_aqua_unchanged=True,connecting_doors_layout_adaptation=True,boarding_3f_kitchen_bow_actors_story_pending=True,native_playtest_pending=True)
