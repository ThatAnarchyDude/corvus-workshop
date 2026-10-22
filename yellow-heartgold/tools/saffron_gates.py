"""Yellow's drink roadblock across all four Kanto Saffron gatehouses."""
import struct
import ndspy.narc
from opening import Script,end,script_bank,events_decode,events_encode,encode_text
from parcel_quest import PH
from viridian_tutorial import TABLE
DRINK_GIVEN=0xA9D
# No saved variable: literal-zero triggers defer to the shared flag.
DRINKS=(30,31,32)
# map, trigger rectangle, direction to return the player to its route side
GATES=((391,(0,7,13,1),12),(389,(0,7,13,1),13),(493,(6,0,1,13),14),(390,(5,0,1,13),15))
LINES=["I'm on guard duty.\rGee, I'm thirsty, though!\rOh, wait there, the road's closed.",
       "Whoa, boy! I'm parched!\r... Huh? I can have this drink?\rGee, thanks!",
       "... Glug, glug... Gulp...\rIf you want to go to SAFFRON CITY...\rYou can go on through.\rI'll share this with the other guards!",
       "Hi, thanks for the cool drinks!"]

def guard_script(back_direction,coordinate=False):
    s=Script().emit(96)
    if not coordinate:s.emit(73,1500).emit(104)
    s.emit(32,DRINK_GIVEN).jump('open',1)
    for item in DRINKS:
        s.emit(128,item,1,0x800C).compare(0x800C,1).jump('drink'+str(item),1)
    s.jump('thirsty')
    for item in DRINKS:
        s.label('drink'+str(item)).emit(126,item,1,0x800C).compare(0x800C,0).jump('thirsty',1)
        s.msg(1).emit(78,1185).emit(79).msg(2).emit(30,DRINK_GIVEN)
        end(s)
    s.label('thirsty').msg(0)
    if coordinate:s.movement(255,'back').emit(95)
    end(s)
    s.label('open')
    if not coordinate:s.msg(3)
    end(s)
    if coordinate:s.moves('back',[(back_direction,2)])
    return s.finish()

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    before=bytes(d[TABLE:TABLE+540*24]);paths=('a/0/1/2','a/0/2/7','a/0/3/2')
    scripts,texts,events=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    old=[list(a.files) for a in arcs];changes=[]
    for mapid,rectangle,back in GATES:
        rec=TABLE+mapid*24
        if not d[rec+20]&1:raise ValueError('Refusing a non-Kanto gate')
        sid,iid,tid=struct.unpack_from('<3H',d,rec+6);eid=struct.unpack_from('<H',d,rec+16)[0]
        g=events_decode(events.files[eid]);assert len(g[1])==1 and len(g[2])==2
        actor=bytearray(g[1][0]);struct.pack_into('<H',actor,10,1);struct.pack_into('<H',actor,8,0);g[1]=[bytes(actor)]
        x,z,width,height=rectangle
        g[3]=[struct.pack('<Hhh5H',2,x,z,width,height,0,0,0)]
        ns=len(scripts.files);scripts.files.append(script_bank([guard_script(back),guard_script(back,True)]))
        ni=len(scripts.files);scripts.files.append(bytes(4))
        nt=len(texts.files);texts.files.append(encode_text(LINES,PH))
        ne=len(events.files);events.files.append(events_encode(g))
        struct.pack_into('<3H',d,rec+6,ns,ni,nt);struct.pack_into('<H',d,rec+16,ne)
        changes.append(dict(map=mapid,script=ns,init=ni,text=nt,event=ne,trigger=rectangle,return_direction=back,original=dict(script=sid,init=iid,text=tid,event=eid)))
    changed=[m for m in range(540) if before[m*24:(m+1)*24]!=d[TABLE+m*24:TABLE+(m+1)*24]]
    assert changed==sorted(m for m,_,_ in GATES)
    for a,b in zip(old,arcs):assert b.files[:len(a)]==a
    for path,a in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=a.save()
    rom.arm9=main.save(compress=True)
    return dict(gates=changes,flag=DRINK_GIVEN,shared_state_flag=DRINK_GIVEN,drinks=list(DRINKS),
        changed_map_headers=changed,johto_unchanged=True,original_members_preserved=True,
        pending=['native no-drink/consume/repeat/reload checks','Yellow gatehouse geometry'])
