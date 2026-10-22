"""Align connecting door faces with native entry/exit movement."""
import struct
import ndspy.narc
from opening import events_decode,events_encode
from viridian_tutorial import TABLE
from ss_anne_floors import warp

TWO_FLOOR_DOORS=((13,8),(19,8),(30,8),(13,14),(19,14),(30,14))
TWO_FLOOR_CABINS=((9,11),(23,11),(41,11),(73,2),(87,2),(105,2))
BASEMENT_DOORS=TWO_FLOOR_DOORS[:5]

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    events,matrices=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in ('a/0/3/2','a/0/4/1')]
    def original(mid):return events_decode(events.files[struct.unpack_from('<H',d,TABLE+mid*24+16)[0]])
    groups={mid:original(mid) for mid in (254,257,260,261)}
    for i,(x,z) in enumerate(TWO_FLOOR_DOORS):groups[254][2][i+1]=warp(x,z,260,i)
    groups[254][2][7]=warp(36,8,256,6)
    for i,(x,z) in enumerate(BASEMENT_DOORS):groups[257][2][i]=warp(x,z,261,i)
    groups[257][2][5]=warp(36,8,256,7)
    groups[260][2]=[warp(x,z,254,i+1) for i,(x,z) in enumerate(TWO_FLOOR_CABINS)]
    groups[261][2]=[warp(x,z,257,i) for i,(x,z) in enumerate(TWO_FLOOR_CABINS[:5])]
    # Three north-exit and three south-exit cabins need four intact paired cells.
    # Unwired room components remain inaccessible; original land assets are untouched.
    old=matrices.files[struct.unpack_from('<H',d,TABLE+260*24+4)[0]];assert old[:4]==bytes((3,1,0,0))
    nm=len(matrices.files);matrices.files.append(bytes((4,1,0,0,old[4]))+old[5:5+old[4]]+struct.pack('<4H',648,648,646,646))
    struct.pack_into('<H',d,TABLE+260*24+4,nm)
    for mid,g in groups.items():
        ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,TABLE+mid*24+16,ne)
    for p,arc in zip(('a/0/3/2','a/0/4/1'),(events,matrices)):rom.files[rom.filenames.idOf(p)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(changed_maps=list(groups),second_floor_cabin_matrix=nm,door_facing_corrected=True,native_retest_pending=True)
