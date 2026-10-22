"""Install Yellow Route 6 battle records; placement is a separate terrain step.

Original trainers, their parties and script bodies remain intact. New records
are not added to the overworld here, so an unfinished layout cannot activate
trainers on blocked terrain.
"""
import struct
import ndspy.narc
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages,encode_messages
from forest_progression import expanded_common

TEMPLATES={'JrTrainerM':26,'JrTrainerF':27,'BugCatcher':4}

def patch(rom,reference,*,map_name="Route6",expected_count=6,templates=None):
    entries=reference['trainers']
    if reference['map']!=map_name or len(entries)!=expected_count:raise ValueError('Unexpected verified route trainer reference')
    templates=TEMPLATES if templates is None else templates
    paths=('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1')
    scripts,texts,trainers,parties,trtable,offsets=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    namekey,names=decode_messages(texts.files[729]);textkey,lines=decode_messages(texts.files[728])
    assert len(trainers.files)==len(parties.files)==len(names)
    table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0]);added=[]
    for entry in entries:
        tid=len(trainers.files)
        if tid>=1000 or 0x550+tid>=0xB60:raise ValueError('Native trainer or save-flag capacity exceeded')
        team=entry['team'];row=bytearray(trainers.files[templates[entry['role']]])
        row[0]=1;row[3]=len(team);row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0
        trainers.files.append(bytes(row));parties.files.append(b''.join(struct.pack('<BB3H4H',128,0,m['level'],m['species'],0,*m['moves']) for m in team))
        names.append([0xFFFF])
        while len(ofs)<2*(tid+1):ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,tid*2,len(table))
        for kind,suffix in enumerate(('BattleText','EndBattleText','AfterBattleText')):
            table.extend(struct.pack('<2H',tid,kind));lines.extend(decode_messages(encode_text([entry['messages'][suffix]],PH))[1])
        added.append(dict(id=tid,defeat_flag=0x550+tid,**entry))
    texts.files[729]=encode_messages(namekey,names);texts.files[728]=encode_messages(textkey,lines)
    trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);sites=[]
    for trigger in (3000,5000):
        matches=[at for at in range(0,len(d)-6,2) if struct.unpack_from('<H',d,at)[0]==trigger and struct.unpack_from('<H',d,at+4)[0]==40 and struct.unpack_from('<H',d,at+2)[0]<len(scripts.files)]
        assert len(matches)==1;sites.append(matches[0])
    original=struct.unpack_from('<H',d,sites[0]+2)[0];assert struct.unpack_from('<H',d,sites[1]+2)[0]==original
    common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[original],added[-1]['id']))
    for at in sites:struct.pack_into('<H',d,at+2,common)
    for path,arc in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(trainers=added,common=common,original_common=original,common_reference_sites=sites,
                actors_installed=False,geometry_changed=False,pending=['native battles and defeat/repeat checks','final Route 6 actor placement'])

