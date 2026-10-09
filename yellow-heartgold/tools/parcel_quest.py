"""Prototype 007: Mom's shoes, Viridian cashier escort, Oak's parcel and Dex."""
import json
import heapq
import struct
import subprocess
import ndspy.narc
import ndspy.rom
from build_rom import BASE, EXPECTED, PROJECT, sha
from opening import Script, end, actor, trigger, events_decode, events_encode, script_bank, encode_text, talk, command, yellow_dialogue
from prototype import decode_messages, encode_messages
from starter_properties import append_code, CMD_TABLE
from escort import ball_choice, lab_init, music
from player_pc import script as pc_script, EVOLUTION_TEXT

INPUT_SHA='3ae1f3042633886583df22dc8f69bb13ca4fc0b75ba2770dbf4a689c336c0042'
PARCEL_STATE=0x416A
SHOES_STATE=0x4169
CLERK_STATE=0x416D
BOUNDARY=0x416B
BALLS_GIVEN=0xB53
SHOES_ITEM=113
PARCEL_ITEM=459
MOM_HIDE=0xB57
BLUE_HIDE=0xB56
CLERK_HIDE=0xB55
GUIDE_HIDE=0xB54
QUEST_INIT=0xB52
PH=[65534,259,2,0,0]
Y=yellow_dialogue()
TOWN_ADDED=["MOM: {PLAYER}! Wait a moment!", "MOM: You forgot your RUNNING SHOES under your bed.\rI brought them for you!", "{PLAYER} received RUNNING SHOES!", "MOM: Hold B to run, or touch the shoe button.\rTake care of yourself and your POKEMON!", "Make room in your KEY ITEMS pocket, then try heading north again.", "MOM: Take care of yourself and your POKEMON!"]
CITY_LINES=["Hey! You came from PALLET TOWN?", "Come with me to the POKEMON MART. I need your help!", "You know PROF.OAK, right?\rHis order came in. Will you take it to him?\rSince you came from PALLET TOWN, you can deliver it on your way back!", "{PLAYER} got OAK's PARCEL!", "Okay! Say hi to PROF.OAK for me!", "Make room in your KEY ITEMS pocket, then speak to me again.", "The next area is not ready for this prototype. Please test VIRIDIAN and OAK's PARCEL first.", "The GYM is closed right now.", "VIRIDIAN CITY\rThe Eternally Green Paradise", "POKEMON MART", "POKEMON CENTER", "MOM has something for you. Please return to PALLET TOWN."]
LAB_ADDED=[Y['_OaksLabOak1DeliverParcelText'],Y['_OaksLabOak1ParcelThanksText'],Y['_OaksLabRivalGrampsText'],Y['_OaksLabRivalMyPokemonHasGrownStrongerText'],Y['_OaksLabOakIHaveARequestText'],Y['_OaksLabOakMyInventionPokedexText'].replace('POKEDEX','NATIONAL POKEDEX'),Y['_OaksLabOakGotPokedexText'].replace('POKEDEX','NATIONAL POKEDEX'),Y['_OaksLabOakThatWasMyDreamText'].replace('150','493'),Y['_OaksLabRivalLeaveItAllToMeText'],Y['_OaksLabOak1PokemonAroundTheWorldText'],Y['_OaksLabOak1ReceivedPokeballsText'],Y['_OaksLabGivePokeballsExplanationText'],"OAK: Please bring my PARCEL from VIRIDIAN CITY's POKEMON MART.","OAK: Let me heal your POKEMON.\rVisit VIRIDIAN CITY to the north!","There is not enough room in your Bag."]


def dex_gate():
    s=Script().emit(32,QUEST_INIT).jump('initialized',1)
    s.emit(41,PARCEL_STATE,0).emit(41,SHOES_STATE,0).emit(41,CLERK_STATE,0).emit(30,QUEST_INIT)
    s.label('initialized').compare(PARCEL_STATE,2).jump('done',1)
    s.emit(31,0x6B).emit(41,0x416B,4).emit(1).emit(41,0x416B,0)
    return s.label('done').emit(2).finish()



def town_reload():
    # Normal saves restore their saved actor list. Older Pallet saves have no
    # new Mom actor; create it only on first migration, never on regular reloads.
    s=Script().emit(32,QUEST_INIT).jump('done',1)
    s.data.extend(dex_gate()[:-2])
    s.emit(32,0x6A).jump('done',5).emit(31,MOM_HIDE).emit(100,6)
    s.label('done');s.data.extend(dex_gate())
    return s.finish()


def walking_paths(rom):
    matrices=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')])
    lands=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')])
    matrix=matrices.files[0];w,h,headers,heights,name=matrix[:5]
    at=5+name+w*h*(2*headers+heights)
    def walkable(x,z):
        land=struct.unpack_from('<H',matrix,at+2*(z//32*w+x//32))[0]
        return not (struct.unpack_from('<H',lands.files[land],20+2*((z%32)*32+x%32))[0]&0x8000)
    def path(start,goal,bounds,obstacles=()):
        blocked=set(obstacles)-{start,goal};todo=[(0,start)];parents={start:None};cost={start:0}
        while todo:
            _,p=heapq.heappop(todo)
            if p==goal:
                result=[]
                while p is not None:result.append(p);p=parents[p]
                return result[::-1]
            for dx,dz in [(0,-1),(-1,0),(1,0),(0,1)]:
                q=(p[0]+dx,p[1]+dz)
                if not (bounds[0]<=q[0]<=bounds[1] and bounds[2]<=q[1]<=bounds[3]) or q in blocked or (q!=goal and not walkable(*q)):continue
                n=cost[p]+1
                if n<cost.get(q,10000):
                    cost[q]=n;parents[q]=p;heapq.heappush(todo,(n+abs(q[0]-goal[0])+abs(q[1]-goal[1]),q))
        raise ValueError(f'No walking path from {start} to {goal}')
    city_blocks=[(1045,239),(1034,244),(1036,253),(1032,262),(1036,280),(1037,280),(1036,254),(1034,245),(1045,240)]
    result={'mom':{},'cashier':{}}
    for x in [1038,1039,1040,1041]:
        result['mom'][x]={'approach':path((1032,364),(x,357),(1030,1043,352,365)),
                          'return':path((x,357),(1033,363),(1030,1043,352,365)),
                          'retry':path((x,357),(1032,364),(1030,1043,352,365))}
    for x in [1036,1037]:
        approach=path((1042,254),(x,277),(1002,1053,231,279),city_blocks)
        escort=[(x,278)]+path((x,277),(1042,253),(1002,1053,231,279),city_blocks)
        result['cashier'][x]={'approach':approach,'escort':escort}
    return result


def steps(points):
    dirs={(0,-1):12,(0,1):13,(-1,0):14,(1,0):15};result=[]
    for a,b in zip(points,points[1:]):
        op=dirs[(b[0]-a[0],b[1]-a[1])]
        if result and result[-1][0]==op:result[-1]=(op,result[-1][1]+1)
        else:result.append((op,1))
    return result


def mom_scene(base,paths):
    s=Script().emit(32,0x6A).jump('done',5).compare(SHOES_STATE,1).jump('done',1)
    s.emit(96).emit(105,0x4000,0x4001).emit(20,2036).msg(base)
    for x in [1038,1039,1040,1041]:s.compare(0x4000,x).jump(f'approach{x}',1)
    for x in [1038,1039,1040,1041]:s.label(f'approach{x}').movement(6,f'approach_move{x}').emit(95).jump('give')
    s.label('give').movement(255,'north').emit(95).msg(base+1)
    s.emit(125,SHOES_ITEM,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(293).emit(41,SHOES_STATE,1).emit(78,1187).msg(base+2).emit(79).msg(base+3)
    for x in [1038,1039,1040,1041]:s.compare(0x4000,x).jump(f'return{x}',1)
    for x in [1038,1039,1040,1041]:s.label(f'return{x}').movement(6,f'return_move{x}').emit(95).jump('home')
    s.label('home').emit(30,MOM_HIDE).emit(101,6).emit(20,2038);end(s)
    s.label('full').msg(base+4)
    for x in [1038,1039,1040,1041]:s.compare(0x4000,x).jump(f'retry{x}',1)
    for x in [1038,1039,1040,1041]:s.label(f'retry{x}').movement(6,f'retry_move{x}').emit(95).jump('retry_done')
    s.label('retry_done').emit(20,2038);end(s)
    s.label('done').emit(2).moves('north',[(0,1)])
    for x in [1038,1039,1040,1041]:
        s.moves(f'approach_move{x}',steps(paths[x]['approach'])+[(1,1)])
        s.moves(f'return_move{x}',steps(paths[x]['return']))
        s.moves(f'retry_move{x}',steps(paths[x]['retry']))
    return s.finish()


def parcel_gift(s):
    s.msg(2).emit(125,PARCEL_ITEM,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(41,PARCEL_STATE,1).emit(41,CLERK_STATE,2).emit(78,1187).msg(3).emit(79).msg(4)
    end(s)
    s.label('full').msg(5)
    return end(s)


def cashier_escort(paths):
    s=Script().compare(SHOES_STATE,1).jump('allowed',1).emit(96).msg(11);end(s)
    s.label('allowed').compare(CLERK_STATE,0).jump('done',5).emit(96).emit(105,0x4000,0x4001).emit(73,1500)
    s.compare(0x4000,1036).jump('approach1036',1).jump('approach1037')
    for x in [1036,1037]:s.label(f'approach{x}').movement(8,f'approach_move{x}').emit(95).jump('greet')
    s.label('greet').movement(255,'north_face').emit(95).msg(0).msg(1)
    s.compare(0x4000,1036).jump('escort1036',1).jump('escort1037')
    for x in [1036,1037]:
        s.label(f'escort{x}').movement(8,f'escort_npc{x}').movement(255,f'escort_player{x}').emit(95).jump('door')
    s.label('door').emit(73,1540).emit(30,CLERK_HIDE).emit(101,8).movement(255,'door_player').emit(95)
    s.emit(41,CLERK_STATE,1).emit(31,GUIDE_HIDE)
    s.emit(174,6,6,0,0).emit(175).emit(176,500,0,4,10,0)
    s.emit(174,6,6,1,0).emit(175)
    s.movement(6,'inside').movement(255,'inside').emit(95).movement(6,'south_face').emit(95)
    parcel_gift(s);s.label('done').emit(2)
    for x in [1036,1037]:
        escort=paths[x]['escort']
        s.moves(f'approach_move{x}',steps(paths[x]['approach'])+[(1,1)])
        s.moves(f'escort_npc{x}',steps(escort[1:]))
        s.moves(f'escort_player{x}',steps(escort[:-1]))
    s.moves('north_face',[(0,1)]).moves('door_player',[(12,1)])
    s.moves('inside',[(12,2)]).moves('south_face',[(1,1)])
    return s.finish()


def clerk_talk():
    s=Script().emit(96).emit(104).compare(PARCEL_STATE,2).jump('shop',1)
    s.compare(PARCEL_STATE,0).jump('give',1)
    s.emit(669,PARCEL_ITEM,0x800C).compare(0x800C,0).jump('give',1).msg(4)
    end(s)
    s.label('give');parcel_gift(s)
    s.label('shop').emit(20,2011).emit(50).emit(41,0x8004,1).emit(20,2048)
    return end(s).finish()


def oak_parcel(base):
    s=Script().emit(96).emit(104).emit(32,0x6A).jump('before_starter',5)
    s.compare(PARCEL_STATE,2).jump('complete',1)
    s.emit(669,PARCEL_ITEM,0x800C).compare(0x800C,0).jump('no_parcel',1)
    s.msg(base).emit(126,PARCEL_ITEM,1,0x800C).compare(0x800C,0).jump('no_parcel',1)
    # Completion precedes the Dex grant. Access is never enabled on the receive leg.
    s.emit(41,PARCEL_STATE,2).msg(base+1)
    music(s,1088).msg(base+2).emit(73,1540).emit(31,BLUE_HIDE).emit(100,9)
    s.movement(9,'arrive').emit(95).msg(base+3)
    music(s,1103).msg(base+4).msg(base+5)
    s.emit(291).emit(30,0x6B).emit(477);s.data.append(1);s.emit(0x800C)
    s.emit(78,1187).msg(base+6).emit(79).msg(base+7).msg(base+8)
    music(s,1088).movement(9,'leave').emit(95).emit(73,1540).emit(30,BLUE_HIDE).emit(101,9)
    s.emit(82).msg(base+9);end(s)
    s.label('no_parcel').msg(base+13).emit(282);end(s)
    s.label('complete').emit(32,BALLS_GIVEN).jump('adventure',1)
    s.emit(125,4,5,0x800C).compare(0x800C,0).jump('bag_full',1)
    s.emit(30,BALLS_GIVEN).emit(78,1187).msg(base+10).emit(79).msg(base+11);end(s)
    s.label('bag_full').msg(base+14);end(s)
    s.label('adventure').msg(base+9).emit(282);end(s)
    s.label('before_starter').msg(2);end(s)
    s.moves('arrive',[(12,6),(15,2),(12,1),(2,1)])
    s.moves('leave',[(13,1),(14,2),(13,6)])
    return s.finish()


def closed(index, direction):
    s=Script().emit(96).msg(index).movement(255,'back').emit(95)
    return end(s).moves('back',[(direction,1)]).finish()


def split_bank(data):
    count=next(i for i in range(400) if struct.unpack_from('<H',data,4*i)[0]==0xFD13)
    starts=[i*4+4+struct.unpack_from('<I',data,4*i)[0] for i in range(count)]
    return [data[a:b] for a,b in zip(starts,starts[1:]+[len(data)])]


def append_bank(data, additions):
    count=next(i for i in range(400) if struct.unpack_from('<H',data,4*i)[0]==0xFD13)
    starts=[i*4+4+struct.unpack_from('<I',data,4*i)[0] for i in range(count)]
    old_header=min(starts);new_header=old_header+4*len(additions)
    out=bytearray(new_header)+data[old_header:]
    for i,at in enumerate(starts):struct.pack_into('<I',out,i*4,at+4*len(additions)-i*4-4)
    for n,code in enumerate(additions):
        out.extend(b'\0'*(-len(out)%4));i=count+n
        struct.pack_into('<I',out,i*4,len(out)-i*4-4);out.extend(code)
    struct.pack_into('<H',out,(count+len(additions))*4,0xFD13)
    return out,count


def center_assets(original_bank, standard_text, local_text):
    count=len(decode_messages(standard_text)[1]);assert count+len(EVOLUTION_TEXT)<255
    service=pc_script(evolution_items=True,text_offset=count,service_only=True)
    native=bytearray(original_bank)
    signature=command(73,1548)+command(190)+b'\0'+command(45)+b'\x24'+command(22)
    at=native.find(signature);assert at>=0 and native.count(signature)==1
    goto=at+len(signature)-2
    # The nearby native player-PC exit branches already point to the root menu.
    native_root=0xA2E
    assert native[native_root:native_root+3]==command(190)+b'\0'
    service_at=(len(native)+3)&~3
    native.extend(b'\0'*(service_at-len(native)));native.extend(service)
    wrapper=(len(native)+3)&~3;native.extend(b'\0'*(wrapper-len(native)))
    native.extend(command(26)+struct.pack('<i',service_at-wrapper-6))
    native.extend(command(22)+struct.pack('<i',native_root-(wrapper+6)-6))
    struct.pack_into('<i',native,goto+2,wrapper-goto-6)
    nurse=command(41,0x8007,0)+command(20,2002)+command(2)
    npc_offset=count+len(EVOLUTION_TEXT)
    first=Script().emit(96).emit(104).emit(32,0x129).jump('before',5).msg(npc_offset+1)
    end(first);first.label('before').msg(npc_offset);end(first)
    new,entries=append_bank(bytes(native),[nurse,dex_gate(),first.finish(),talk(npc_offset+2),talk(npc_offset+3)])
    key,msg=decode_messages(standard_text)
    msg.extend(decode_messages(encode_text(EVOLUTION_TEXT,PH))[1])
    msg.extend(decode_messages(local_text)[1])
    return bytes(new),encode_messages(key,msg),entries


def patch(rom,original):
    main=rom.loadArm9();main.sections[0].data=bytearray(main.sections[0].data);data=main.sections[0].data
    old_end=main.sections[1].ramAddress+len(main.sections[1].data)
    assert struct.unpack_from('<I',data,CMD_TABLE+4)[0]==0x01FF8621
    hook,code=append_code(main,(PROJECT/'asm/parcel-dex-gate.s').read_text())
    struct.pack_into('<I',data,CMD_TABLE+4,hook|1)
    main.sections[1].data.extend(b'\0'*(-len(main.sections[1].data)%4))
    assert struct.unpack_from('<I',data,0xD2C68)[0]==old_end
    struct.pack_into('<I',data,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
    pristine=original.loadArm9().sections[0].data
    table=pristine.index(struct.pack('<3H',740,513,451))-6-505*24
    paths=['a/0/1/2','a/0/2/7','a/0/3/2','a/0/1/7']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,items=[arcs[p] for p in paths];before={p:list(a.files) for p,a in arcs.items()}
    mappings=[]
    walks=walking_paths(rom)
    def record(map):return table+map*24
    def current(map):
        rec=record(map);sid,init,tid=struct.unpack_from('<3H',data,rec+6);eid=struct.unpack_from('<H',data,rec+16)[0]
        return split_bank(scripts.files[sid]),decode_messages(texts.files[tid]),events_decode(events.files[eid])
    def install(map, bank, text, groups, init):
        rec=record(map);sid=len(scripts.files);scripts.files.append(bank)
        reload_code=gate_prefix(split_bank(bank)[18]) if map==505 else town_reload() if map==49 else dex_gate()
        bank,count=append_bank(scripts.files[sid],[reload_code]);scripts.files[sid]=bank
        iid=len(scripts.files);scripts.files.append(struct.pack('<BHHBHH',2,init,0,3,count+1,0)+b'\0\0')
        tid=len(texts.files);texts.files.append(text)
        eid=len(events.files);events.files.append(events_encode(groups))
        struct.pack_into('<3H',data,rec+6,sid,iid,tid);struct.pack_into('<H',data,rec+16,eid)
        mappings.append(dict(map_id=map,script=sid,init=iid,text=tid,event=eid))
    def gate_prefix(code):return dex_gate()[:-2]+code
    # Preserve every original map bank and event member in the archive.
    bank,(key,msg),groups=current(49);base=len(msg);msg.extend(decode_messages(encode_text(TOWN_ADDED,PH))[1])
    bank.append(mom_scene(base,walks['mom']));mom_id=len(bank)
    bank.append(talk(base+5))
    init=bank[8]
    # A new init ends with the former town init, with Mom visibility set first.
    si=Script().emit(32,0x6A).jump('hide',5).compare(SHOES_STATE,1).jump('hide',1).emit(31,MOM_HIDE).jump('done')
    si.label('hide').emit(30,MOM_HIDE).label('done')
    si.data.extend(init);bank[8]=gate_prefix(si.finish())
    groups[1].append(actor(6,393,mom_id+1,1032,364,MOM_HIDE,0))
    groups[3].append(trigger(mom_id,1038,358,4,SHOES_STATE,0))
    install(49,script_bank(bank),encode_messages(key,msg),groups,9)
    bank,(key,msg),groups=current(505);base=len(msg);msg.extend(decode_messages(encode_text(LAB_ADDED,PH))[1])
    msg[3]=decode_messages(encode_text([Y['_OaksLabOak1YourPokemonCanFightText']],PH))[1][0]
    bank[0]=oak_parcel(base)
    for i in range(3):
        assert bank[15+i].startswith(ball_choice(i))
        bank[15+i]=ball_choice(i,grant_dex=False)
    bank[14]=gate_prefix(command(30,BLUE_HIDE)+lab_init())
    groups[1].append(actor(9,375,0,8,14,BLUE_HIDE,0))
    install(505,script_bank(bank),encode_messages(key,msg),groups,15)
    for map in [503,504,506,9,527]:
        bank,(key,msg),groups=current(map)
        init=dex_gate()
        if map==9:
            init_id=len(bank)+1;bank.append(init)
            groups[3]=[trigger(4,1024,344,32,SHOES_STATE,0)]
            bank[3]=closed(4,13)
            msg[4]=decode_messages(encode_text([CITY_LINES[11]],PH))[1][0]
        elif map==506:
            bank[2]=gate_prefix(bank[2]);init_id=3
        elif map==503:
            bank[0]=talk(0,heal=True);init_id=len(bank)+1;bank.append(init)
        else:
            sid=struct.unpack_from('<H',data,record(map)+6)[0]
            preserved,entry=append_bank(scripts.files[sid],[init])
            install(map,preserved,encode_messages(key,msg),groups,entry+1)
            continue
        install(map,script_bank(bank),encode_messages(key,msg),groups,init_id)
    # Viridian and its gatehouse are peaceful; retain the old actors/events only
    # in their untouched archive members, ready for later HeartGold relocation.
    bank,_,groups=current(50)
    bank=[talk(8),talk(8),talk(8),talk(7),talk(9),talk(10),talk(7),talk(7),cashier_escort(walks['cashier']),closed(6,13),closed(6,15)]
    init=Script().compare(CLERK_STATE,0).jump('visible',1).emit(30,CLERK_HIDE).jump('done')
    init.label('visible').emit(31,CLERK_HIDE).label('done').emit(2);bank.append(gate_prefix(init.finish()))
    groups[1]=[actor(0,330,4,1045,240),actor(1,330,8,1036,254),actor(2,330,8,1034,245),actor(8,334,5,1042,254,CLERK_HIDE,1)]
    groups[0]=[struct.pack('<HHiiiH2x',script,1,x,z,0,4) for script,x,z in [(1,1025,256),(5,1042,254),(6,1032,263)]]
    groups[3]=[trigger(9,1036,278,2,CLERK_STATE,0),trigger(10,992,230,96,BOUNDARY,0),struct.pack('<Hhh5H',11,1001,224,1,64,0,0,BOUNDARY)]
    install(50,script_bank(bank),encode_text(CITY_LINES,PH),groups,len(bank))
    bank,_,groups=current(500)
    bank=[clerk_talk(),clerk_talk(),talk(4),talk(4),talk(4),talk(4),clerk_talk()]
    init=Script().compare(CLERK_STATE,1).jump('guide',1).compare(CLERK_STATE,2).jump('guide',1).emit(30,GUIDE_HIDE).jump('done')
    init.label('guide').emit(31,GUIDE_HIDE).label('done').emit(2);bank.append(gate_prefix(init.finish()))
    groups[1]=groups[1][:4]+[actor(6,334,7,4,9,GUIDE_HIDE,1)]
    groups[3]=[]
    install(500,script_bank(bank),encode_text(CITY_LINES,PH),groups,len(bank))
    # Local copy of the native Center PC: its normal storage services remain.
    # Only this map's Player PC branch gains the shared item storage menu.
    _,(local_key,local_msg),groups=current(501)
    center_bank,center_text,entries=center_assets(scripts.files[3],texts.files[40],encode_messages(local_key,local_msg))
    groups[1]=[row for row in groups[1] if struct.unpack_from('<H',row)[0] in [0,1,2,3]]
    for n,row in enumerate(groups[1]):
        row=bytearray(row)
        original_id=struct.unpack_from('<H',row)[0]
        if original_id==0:struct.pack_into('<H',row,10,entries+1)
        else:struct.pack_into('<H',row,10,entries+2+original_id)
        groups[1][n]=bytes(row)
    # The existing BG event at (4,8) is the town map. The PC's native
    # metatile is (11,12); a north-facing BG event overrides its common script.
    groups[0].append(struct.pack('<HHiiiH2x',11,0,11,12,0,0))
    install(501,center_bank,center_text,groups,entries+2)
    # Add a tangible Running Shoes key item in a verified unused item ID.
    mapping=0x100194
    assert struct.unpack_from('<4H',data,mapping+SHOES_ITEM*8)==(0,793,794,0)
    parcel_index=struct.unpack_from('<H',data,mapping+PARCEL_ITEM*8)[0];assert parcel_index==436
    item=bytearray(items.files[parcel_index]);item[10:14]=b'\0'*4
    new_item=len(items.files);items.files.append(bytes(item));struct.pack_into('<H',data,mapping+SHOES_ITEM*8,new_item)
    for text_id,item_id,line in [(222,SHOES_ITEM,'Running Shoes'),(221,SHOES_ITEM,'Comfortable shoes for running. Hold B or use the shoe button.'),(222,PARCEL_ITEM,"Oak's Parcel"),(221,PARCEL_ITEM,'A special POKE BALL order to deliver to PROF.OAK in PALLET TOWN.')]:
        key,msg=decode_messages(texts.files[text_id]);msg[item_id]=decode_messages(encode_text([line],PH))[1][0];texts.files[text_id]=encode_messages(key,msg)
    main.sections[0].data=data;rom.arm9=main.save(compress=True)
    for path,arc in arcs.items():
        allowed={221,222} if path=='a/0/2/7' else set()
        assert all(old==arc.files[i] for i,old in enumerate(before[path]) if i not in allowed)
        rom.files[rom.filenames.idOf(path)]=arc.save()
    return dict(mappings=mappings,dex_gate_hook=hex(hook),shoes_item=SHOES_ITEM,shoes_param_member=new_item,parcel_item=PARCEL_ITEM,variables={'parcel':PARCEL_STATE,'shoes':SHOES_STATE,'cashier':CLERK_STATE,'balls':BALLS_GIVEN},original_assets_preserved=True,walking_paths=walks)


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-006.nds'
    assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    rom=ndspy.rom.NintendoDSRom.fromFile(str(source));previous=ndspy.rom.NintendoDSRom.fromFile(str(source));before=list(rom.files)
    report=patch(rom,ndspy.rom.NintendoDSRom.fromFile(str(BASE)))
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nOak parcel prototype 007\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner)
    output=rom.save();check=ndspy.rom.NintendoDSRom(output)
    changed=[i for i,(a,b) in enumerate(zip(before,check.files)) if a!=b]
    assert changed==sorted(rom.filenames.idOf(p) for p in ['a/0/1/2','a/0/2/7','a/0/3/2','a/0/1/7'])
    assert check.arm9==rom.arm9 and check.arm7==previous.arm7 and check.arm9OverlayTable==previous.arm9OverlayTable
    target=PROJECT/'build/yellow-heartgold-prototype-007.nds';target.write_bytes(output)
    patcher=PROJECT/'.tools/xdelta3';patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/parcel-roundtrip.nds'
    subprocess.run([str(patcher),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True)
    subprocess.run([str(patcher),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True)
    assert sha(decoded.read_bytes())==sha(output)
    report.update(version='007',output_sha256=sha(output),patch_sha256=sha(patchfile.read_bytes()),changed_file_ids=changed)
    (PROJECT/'build/parcel-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':build()
