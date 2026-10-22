"""Kanto-only Route 5 foundation and approved shared native Day Care.

This is an intermediate build: Yellow geometry and gate progression remain work.
Original archive members and all Johto headers/resources are preserved.
"""
import json,struct
import ndspy.narc
from build_rom import PROJECT
from viridian_tutorial import TABLE
from opening import events_decode,events_encode,encode_text
from parcel_quest import PH
from forest_progression import SLOT_MAP,HG_WEIGHTS
from field_interaction_fixes import sign
from opening import script_bank

DATA=json.loads((PROJECT/'data/route5.json').read_text())
MAP=13
DAYCARE_MAP=517

def encounter_table(original):
    if len(original)!=196:raise ValueError('Unexpected encounter table size')
    b=bytearray(original);b[0]=DATA['encounter_rate'];b[1:6]=bytes(5)
    slots=[DATA['wild_slots'][i] for i in SLOT_MAP]
    b[8:20]=bytes(s['level'] for s in slots)
    species=[s['species'] for s in slots]
    for period in range(3):struct.pack_into('<12H',b,20+period*24,*species)
    for at in (0x5C,0x60,0x64,0x68,0xBC):struct.pack_into('<2H',b,at,*species[:2])
    return bytes(b)

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    old_headers=bytes(d[TABLE:TABLE+540*24])
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/3/7')
    scripts,texts,events,wild=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    archived=[list(a.files) for a in arcs]
    rec=TABLE+MAP*24;old_wild=d[rec];old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6);old_eid=struct.unpack_from('<H',d,rec+16)[0]
    g=events_decode(events.files[old_eid]);original_events=[list(x) for x in g]
    # Yellow has neither outdoor trainers nor NPCs/items on Route 5.
    g[1]=[];g[3]=[]
    if len(g[0])!=1:raise ValueError('Unexpected Route 5 sign count')
    entry,kind,x,z,y,facing=struct.unpack('<HHiiiH2x',g[0][0])
    g[0]=[struct.pack('<HHiiiH2x',1,0,x,z,y,facing)]
    sid=len(scripts.files);scripts.files.append(script_bank([sign(0)]))
    iid=len(scripts.files);scripts.files.append(bytes(4))
    tid=len(texts.files);texts.files.append(encode_text([DATA['messages']['underground_sign']],PH))
    eid=len(events.files);events.files.append(events_encode(g))
    wid=len(wild.files)
    if wid>=255:raise ValueError('Encounter header index exhausted')
    wild.files.append(encounter_table(wild.files[old_wild]));d[rec]=wid
    struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid)
    # Clone the native two-entry Day Care bank; entry 1 handles eggs/compatibility,
    # entry 2 handles deposit/withdrawal. The original Johto bank is untouched.
    house=TABLE+DAYCARE_MAP*24;hs,hi,ht=struct.unpack_from('<3H',d,house+6);he=struct.unpack_from('<H',d,house+16)[0]
    hg=events_decode(events.files[he]);assert len(hg[1])==2
    for row,entry in enumerate((1,2)):
        actor=bytearray(hg[1][row]);struct.pack_into('<H',actor,10,entry);struct.pack_into('<H',actor,8,0);hg[1][row]=bytes(actor)
    ds=len(scripts.files);scripts.files.append(scripts.files[265])
    di=len(scripts.files);scripts.files.append(bytes(4))
    dt=len(texts.files);texts.files.append(texts.files[439])
    de=len(events.files);events.files.append(events_encode(hg))
    struct.pack_into('<3H',d,house+6,ds,di,dt);struct.pack_into('<H',d,house+16,de)
    changed_headers=[m for m in range(540) if old_headers[m*24:(m+1)*24]!=d[TABLE+m*24:TABLE+(m+1)*24]]
    assert changed_headers==[MAP,DAYCARE_MAP]
    for old,a in zip(archived,arcs):assert a.files[:len(old)]==old
    for path,a in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=a.save()
    rom.arm9=main.save(compress=True)
    return dict(status='development foundation, not release',changed_map_headers=changed_headers,
        route=dict(map=MAP,script=sid,init=iid,text=tid,event=eid,wild=wid,sign=[x,z],removed_outdoor_actors=len(original_events[1]),
        original=dict(script=old_sid,init=old_iid,text=old_tid,event=old_eid,wild=old_wild)),
        daycare=dict(map=DAYCARE_MAP,script=ds,init=di,text=dt,event=de,source_script=265,source_text=439,shared_native_storage=True,
        original=dict(script=hs,init=hi,text=ht,event=he)),original_archive_members_preserved=True,
        johto_headers_unchanged=True,geometry_changed=False,pending=['Yellow Route 5 geometry/Day Care placement','Saffron drink gate','native deposit/withdraw/save validation'])
