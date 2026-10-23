"""Yellow characters in unchanged native north/south Underground Path rooms."""
import struct
import ndspy.narc
from opening import actor,talk,script_bank,events_decode,events_encode,encode_text
from parcel_quest import PH
from viridian_tutorial import TABLE

GIRL_TEXT='People often lose\rthings in that\nUNDERGROUND PATH.'

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2')
    scripts,texts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    changes=[]
    for mapid in (470,532):
        rec=TABLE+mapid*24;assert d[rec+20]&1,'Refusing a non-Kanto interior'
        eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[eid])
        if mapid==470:
            # Fit Yellow's girl in HG's existing entrance, away from both doors.
            g[1]=[actor(0,319,1,3,5,facing=1)]
            ns=len(scripts.files);scripts.files.append(script_bank([talk(0)]))
            ni=len(scripts.files);scripts.files.append(bytes(4))
            nt=len(texts.files);texts.files.append(encode_text([GIRL_TEXT],PH))
            struct.pack_into('<3H',d,rec+6,ns,ni,nt)
        else:
            # Yellow's passage contains no visible people. Hidden items remain
            # native until their own Yellow source audit; no geometry changes.
            g[1]=[]
        ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,ne)
        changes.append(dict(map=mapid,event=ne))
    for path,arc in zip(paths,(scripts,texts,events)):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(changed_maps=changes,geometry_changed=False,
                pending=['native girl dialogue and both path exits','northern Yellow trade','Yellow hidden items'])
