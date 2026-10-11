"""Unbypassable Brock story escort using walkable tiles on the unchanged map."""
import json,struct
import ndspy.narc
from build_rom import PROJECT
from opening import Script,events_decode,events_encode,script_bank,end
from parcel_quest import split_bank
from viridian_tutorial import TABLE
from pewter_museum import TICKET

STATE=0x4146
PATH=json.loads((PROJECT/'data/pewter-guide-path.json').read_text())

def step(a,b):
    delta=(b[0]-a[0],b[1]-a[1]);return {(-1,0):14,(1,0):15,(0,-1):12,(0,1):13}[delta]

def escort():
    s=Script().emit(96).emit(294,8,0x800C).compare(0x800C,1).jump('open',1)
    s.msg(0).emit(105,0x4000,0x4001)
    # Manual interaction can originate on any side of the guide. Move onto
    # the east lane before joining the same single-file escort.
    s.compare(0x4000,1084).jump('from_west',1)
    s.compare(0x4000,1085).jump('from_vertical',1)
    for z in range(101,107):s.compare(0x4001,z).jump(f'lane{z}',1)
    s.jump('lane104')
    for z in range(101,107):s.label(f'lane{z}').movement(255,f'align{z}').emit(95).jump('walk')
    s.label('from_west').movement(255,'align_west').emit(95).jump('walk')
    s.label('from_vertical').compare(0x4001,103).jump('from_north',1)
    s.movement(255,'align_south').emit(95).jump('walk')
    s.label('from_north').movement(255,'align_north').emit(95).jump('walk')
    s.label('walk')
    route=PATH['escort']
    for i in range(1,len(route)):
        s.movement(12,f'lead{i}').movement(255,f'follow{i}').emit(95)
    s.movement(12,'face').movement(255,'face').emit(95).msg(1)
    for i in range(1,len(PATH['return'])):s.movement(12,f'return{i}').emit(95)
    end(s)
    s.label('open').msg(2);end(s)
    s.moves('align_west',[(13,1),(15,2),(12,1)])
    s.moves('align_north',[(15,1),(13,1)])
    s.moves('align_south',[(15,1),(12,1)])
    for z in range(101,107):s.moves(f'align{z}',[(13,104-z)] if z<104 else [(12,z-104)] if z>104 else [(2,1)])
    for i in range(1,len(route)):
        s.moves(f'lead{i}',[(step(route[i-1],route[i]),1)])
        s.moves(f'follow{i}',[(14 if i==1 else step(route[i-2],route[i-1]),1)])
    s.moves('face',[(0,1)])
    for i in range(1,len(PATH['return'])):s.moves(f'return{i}',[(step(PATH['return'][i-1],PATH['return'][i]),1)])
    return s.finish()

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/3/2');scripts,events=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    rec=TABLE+51*24;sid=struct.unpack_from('<H',d,rec+6)[0];eid=struct.unpack_from('<H',d,rec+16)[0];bank=split_bank(scripts.files[sid]);bank[0]=escort()
    init=Script().emit(31,TICKET).emit(294,8,0x800C).compare(0x800C,1).jump('after',1).emit(41,STATE,0).jump('done')
    init.label('after').emit(41,STATE,1).label('done').emit(2);bank[-1]=init.finish()
    ns=len(scripts.files);scripts.files.append(script_bank(bank));struct.pack_into('<H',d,rec+6,ns)
    g=events_decode(events.files[eid])
    for i,row in enumerate(g[1]):
        if struct.unpack_from('<H',row)[0]==12:
            b=bytearray(row);struct.pack_into('<2H',b,24,*PATH['start']);g[1][i]=bytes(b)
    # Cover every walkable lane across the exit; this is Yellow's story event,
    # not an added terrain obstacle. Use a dedicated state instead of the old
    # boundary variable shared with other areas.
    g[3]=[struct.pack('<Hhh5H',1,1086,101,1,6,0,0,STATE)]
    ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,ne)
    for path,arc in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=51,script=ns,event=ne,state=STATE,start=PATH['start'],player_finish=PATH['player_finish'],guide_finish=PATH['escort'][-1],path_source='data/pewter-guide-path.json',trigger=[1086,101,1,6],open_after_boulder=True,original_script=sid,original_event=eid)
