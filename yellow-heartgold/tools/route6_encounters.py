"""Yellow Route 6 grass and Surf encounters, confined to Kanto map 14.

Fishing and rock-smash tables remain unchanged pending their source audit.
This is a development step, not the complete Route 6 reconstruction.
"""
import struct
import ndspy.narc
from forest_progression import SLOT_MAP
from viridian_tutorial import TABLE

GRASS=((16,15),(19,14),(63,7),(16,16),(19,16),(16,17),(17,17),(39,3),(39,5),(39,7))
SURF=((54,15),(54,15),(54,15),(55,15),(55,20))

def encounter_table(original):
    if len(original)!=196:raise ValueError('Unexpected native encounter table size')
    b=bytearray(original);b[0:2]=bytes((15,3))
    slots=[GRASS[i] for i in SLOT_MAP];b[8:20]=bytes(lv for _,lv in slots)
    for period in range(3):struct.pack_into('<12H',b,20+24*period,*(sp for sp,_ in slots))
    # Native radio/swarm substitutions must not reintroduce unrelated species.
    for at in (0x5C,0x60):struct.pack_into('<2H',b,at,16,19)
    for i,(sp,lv) in enumerate(SURF):struct.pack_into('<BBH',b,0x64+4*i,lv,lv,sp)
    struct.pack_into('<2H',b,0xBC,16,54)
    return bytes(b)

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+14*24
    assert d[rec+20]&1,'Refusing a non-Kanto map'
    path='a/0/3/7';fid=rom.filenames.idOf(path);arc=ndspy.narc.NARC(rom.files[fid]);old=d[rec]
    if old>=len(arc.files):raise ValueError('Missing Route 6 encounter template')
    wid=len(arc.files)
    if wid>=255:raise ValueError('Encounter header index exhausted')
    arc.files.append(encounter_table(arc.files[old]));d[rec]=wid
    rom.files[fid]=arc.save();rom.arm9=main.save(compress=True)
    return dict(map=14,original_wild=old,wild=wid,grass_rate=15,surf_rate=3,
                original_members_preserved=True,geometry_changed=False,
                pending=['Route6 terrain/trainers/story','native grass and Surf checks','fishing source audit'])
