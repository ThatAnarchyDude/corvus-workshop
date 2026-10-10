"""Yellow museum events and a second floor built from native HG resources."""
import struct
import ndspy.narc
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, talk, end
from parcel_quest import PH, split_bank
from pewter_interiors import DATA
from viridian_tutorial import TABLE

TICKET=0xB23
AMBER=0xB24
UPSTAIRS=538  # Native unused map slot: no Johto or Kanto location replaced.
STAIR_X,STAIR_Z=18,5

KEYS=[
 '_Museum1FScientist1WouldYouLikeToComeInText',
 '_Museum1FScientist1ThankYouText',
 '_Museum1FScientist1DontHaveEnoughMoneyText',
 '_Museum1FScientist1ComeAgainText',
 '_Museum1FScientist1TakePlentyOfTimeText',
 '_Museum1FScientist2TakeThisToAPokemonLabText',
 '_Museum1FScientist2ReceivedOldAmberText',
 '_Museum1FScientist2GetTheOldAmberCheckText',
 '_Museum1FScientist2YouDontHaveSpaceText',
 '_Museum1FGamblerText','_Museum1FScientist3Text',
 '_Museum2FYoungsterText','_Museum2FGrampsText','_Museum2FScientistText',
 '_Museum2FBrunetteGirlText','_Museum2FHikerText',
 '_Museum1FOldAmberText','_Museum2FSpaceShuttleSignText','_Museum2FMoonStoneSignText',
]

def admission(automatic=False):
    s=Script().emit(96)
    if automatic:s.emit(41,0x4000,1)
    else:s.emit(73,1500).emit(104)
    s.emit(32,TICKET).jump('paid',1).msg(0).emit(63,0x800C)
    s.compare(0x800C,1).jump('decline',1)
    s.emit(112,0x800C,50,0).compare(0x800C,0).jump('poor',1)
    s.emit(111,50,0).emit(30,TICKET).msg(1).jump('done')
    s.label('poor').msg(2).jump('leave')
    s.label('decline').msg(3)
    s.label('leave')
    # A refused admission returns through the normal entrance. The on-frame
    # scene starts on the door landing; a visible step precedes the warp.
    if automatic:
        s.movement(255,'exit').emit(95).emit(174,6,6,0,0).emit(175)
        s.emit(176,51,0,1048,79,1).emit(174,6,6,1,0).emit(175)
    s.jump('done').label('paid')
    if not automatic:s.msg(4)
    s.label('done');end(s)
    if automatic:s.moves('exit',[(13,1)])
    return s.finish()

def amber():
    s=Script().emit(73,1500).emit(96).emit(104).emit(32,AMBER).jump('received',1)
    s.msg(5).emit(125,103,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,AMBER).emit(78,1185).msg(6).emit(79).jump('done')
    s.label('received').msg(7).jump('done').label('full').msg(8)
    s.label('done');return end(s).finish()

def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events=arcs.values();rec=TABLE+471*24
    old_sid,old_iid,old_tid=struct.unpack_from('<3H',d,rec+6)
    old_eid=struct.unpack_from('<H',d,rec+16)[0]
    groups=events_decode(events.files[old_eid])
    bank=[amber(),admission(),talk(10),talk(10),talk(9)]
    bank += [talk(i) for i in (11,13,14,15,16,17,18)]
    bank += [talk(19),talk(20),admission(True)]
    init=Script().emit(41,0x4000,0).emit(32,TICKET).jump('done',0)
    init.emit(41,0x4000,1).label('done').emit(2)
    bank.append(init.finish())
    # Existing HG actors have local scripts 2,1,5,4,3. All five keep their
    # positions. Archive Steven, Enigma Stone and postgame fossil routines.
    groups[1]=[r for r in groups[1] if struct.unpack_from('<H',r)[0]<5]
    # Steven and the HG fossil enthusiast are archived with the original bank.
    # Their active Yellow roles are scientists, not those named HG characters.
    for index,row in enumerate(groups[1]):
        if struct.unpack_from('<H',row)[0] in (1,3):
            row=bytearray(row);struct.pack_into('<H',row,2,338)
            groups[1][index]=bytes(row)
    # Upstairs visitors are installed on their own map below.
    # Reuse existing fossil/exhibit models rather than importing new maps.
    for i,row in enumerate(groups[0]):
        b=bytearray(row);old=struct.unpack_from('<H',b)[0]
        entry=13 if old in (6,7) else 14 if old in (8,9) else 12 if old==10 else 11 if old==11 else 10
        struct.pack_into('<H',b,0,entry);groups[0][i]=b
    sid=len(scripts.files);scripts.files.append(script_bank(bank))
    iid=len(scripts.files)
    scripts.files.append(struct.pack('<BHHBI',2,16,0,1,1)+bytes(1)
                         +struct.pack('<3H',0x4000,0,15)+bytes(2))
    lines=[DATA[k] for k in KEYS]+['AERODACTYL fossil.','KABUTOPS fossil.']
    tid=len(texts.files);texts.files.append(encode_text(lines,PH))
    eid=len(events.files);events.files.append(events_encode(groups))
    struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid)
    # Reset admission only after leaving the museum for Pewter, never during
    # an ordinary save/reload inside the museum.
    city=TABLE+51*24;city_sid=struct.unpack_from('<H',d,city+6)[0]
    city_bank=split_bank(scripts.files[city_sid])
    city_bank.append(Script().emit(31,TICKET).emit(2).finish())
    new_city_sid=len(scripts.files);scripts.files.append(script_bank(city_bank))
    city_iid=len(scripts.files);scripts.files.append(struct.pack('<BHHB',2,len(city_bank),0,0))
    struct.pack_into('<2H',d,city+6,new_city_sid,city_iid)
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    floors=add_second_floor(rom)
    return dict(map=471,script=sid,init=iid,text=tid,event=eid,
                original_script=old_sid,original_init=old_iid,original_text=old_tid,original_event=old_eid,
                ticket_price=50,ticket_flag=TICKET,amber_flag=AMBER,amber_item=103,
                layout='Two floors',city_script=new_city_sid,city_init=city_iid,floors=floors)


def add_second_floor(rom):
    """Clone museum geometry, with independent matrices, stairs and events.

    Only the unused map 538 is repurposed. Stair graphics and the stair tile
    behavior come from the native player house; native area 44 already loads
    that staircase model, so no global model or texture tables change.
    """
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2','a/0/4/1','a/0/6/5']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,matrices,lands=arcs.values()
    lower=TABLE+471*24;upper=TABLE+UPSTAIRS*24
    original_header=bytes(d[upper:upper+24])
    museum_matrix=struct.unpack_from('<H',d,lower+4)[0]
    matrix=matrices.files[museum_matrix]
    assert matrix[:4]==bytes([1,1,0,0])
    at=5+matrix[4];old_land=struct.unpack_from('<H',matrix,at)[0]
    original_land=lands.files[old_land]
    # Native interior staircase prop from Pallet's house, with translation
    # adjusted in 16-unit tiles. Its model is present in museum area 44.
    house=lands.files[362];perm_size,prop_size=struct.unpack_from('<2I',house)
    stair=bytearray(house[20+perm_size+48:20+perm_size+96])
    assert struct.unpack_from('<I',stair)[0]==4
    x,y,z=struct.unpack_from('<3i',stair,4)
    struct.pack_into('<3i',stair,4,x+(STAIR_X-9)*65536,y,z+(STAIR_Z-3)*65536)
    geometry=[]
    for upstairs in (False,True):
        land=bytearray(original_land);ps,bs=struct.unpack_from('<2I',land)
        props=bytes(stair)
        land[20+ps+bs:20+ps+bs]=props
        struct.pack_into('<I',land,4,bs+len(props))
        struct.pack_into('<H',land,20+2*(STAIR_Z*32+STAIR_X),0x5E)
        # Match the native east-facing staircase: its next tile is a wall.
        # Otherwise the player can walk off the trigger before the field
        # controller handles the stair transition.
        struct.pack_into('<H',land,20+2*(STAIR_Z*32+STAIR_X+1),0x8000)
        if upstairs:
            # Seal the former ground-floor street door with native wall
            # collision. Upstairs has exactly one exit: its staircase.
            struct.pack_into('<H',land,20+2*(19*32+10),0x8000)
        lid=len(lands.files);lands.files.append(land)
        new_matrix=bytearray(matrix);struct.pack_into('<H',new_matrix,at,lid)
        mid=len(matrices.files);matrices.files.append(new_matrix)
        geometry.append(dict(matrix=mid,land=lid,original_matrix=museum_matrix,original_land=old_land))
    old_lower_eid=struct.unpack_from('<H',d,lower+16)[0]
    g=events_decode(events.files[old_lower_eid])
    g[2].append(struct.pack('<6H',STAIR_X,STAIR_Z,UPSTAIRS,0,0,0))
    lower_eid=len(events.files);events.files.append(events_encode(g))
    lines=[DATA[k] for k in ('_Museum2FYoungsterText','_Museum2FGrampsText',
         '_Museum2FScientistText','_Museum2FBrunetteGirlText','_Museum2FHikerText',
         '_Museum2FSpaceShuttleSignText','_Museum2FMoonStoneSignText')]
    bank=[talk(i) for i in range(len(lines))]
    sid=len(scripts.files);scripts.files.append(script_bank(bank))
    iid=len(scripts.files);scripts.files.append(bytes(4))
    tid=len(texts.files);texts.files.append(encode_text(lines,PH))
    upstairs_events=[[],[actor(0,315,1,12,7),actor(1,330,2,6,5),
         actor(2,338,3,17,8),actor(3,319,4,16,10),actor(4,332,5,17,10)],
         [struct.pack('<6H',STAIR_X,STAIR_Z,471,1,0,0)],[]]
    upstairs_events[0]=[struct.pack('<HHiiiH2x',6,1,12,9,0,4),struct.pack('<HHiiiH2x',7,1,23,9,0,4)]
    eid=len(events.files);events.files.append(events_encode(upstairs_events))
    struct.pack_into('<H',d,lower+4,geometry[0]['matrix'])
    struct.pack_into('<H',d,lower+16,lower_eid)
    d[upper:upper+24]=d[lower:lower+24]
    struct.pack_into('<4H',d,upper+4,geometry[1]['matrix'],sid,iid,tid)
    struct.pack_into('<H',d,upper+16,eid)
    for path,arc in arcs.items():rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(upper_map=UPSTAIRS,original_unused_header=original_header.hex(),geometry=geometry,
                lower_event=lower_eid,upper_event=eid,upper_script=sid,upper_text=tid,
                stair=[STAIR_X,STAIR_Z],stair_model=4,upper_area=d[upper+1],exhibits="Native HeartGold displays with Yellow dialogue")
