"""Prototype 014: Yellow Route 2 and Viridian Forest in HeartGold's maps."""
import json,struct,subprocess
import ndspy.rom,ndspy.narc
from build_rom import PROJECT,BASE,EXPECTED,sha
from opening import Script,actor,events_decode,events_encode,script_bank,encode_text,talk,end,command
from parcel_quest import PH,split_bank,BOUNDARY
from viridian_tutorial import TABLE
from prototype import decode_messages,encode_messages
INPUT_SHA='7b7a1ee57b972f3f8e18bdc1611e32eface19f18db368180a27fa5eedf640c9d'
DATA=json.loads((PROJECT/'data/route2-forest.json').read_text())
SPECIES={'RATTATA':19,'PIDGEY':16,'NIDORAN_M':32,'NIDORAN_F':29,'CATERPIE':10,'METAPOD':11,'PIDGEOTTO':17}
HG_WEIGHTS=(20,20,10,10,10,10,5,5,4,4,1,1)
SLOT_MAP=(0,1,2,3,4,5,2,6,7,8,7,9)
ITEM_FLAGS=(0xB25,0xB26,0xB27,800+85,800+87,0xB2A,0xB2B)


def remove_kanto_terrain_gates(d, events):
    """Remove inherited HM objects without altering maps or Johto event banks."""
    removed=[]
    for m in range(540):
        rec=TABLE+24*m
        if not d[rec+20]&1:
            continue
        eid=struct.unpack_from('<H',d,rec+16)[0]
        if eid>=len(events.files):
            continue
        groups=events_decode(events.files[eid]);keep=[];objects=[]
        for row in groups[1]:
            obj,sprite=struct.unpack_from('<2H',row)
            script=struct.unpack_from('<H',row,10)[0]
            # These two trees were specifically requested beside the old man.
            approved=m==50 and obj in (19,20)
            if sprite in (84,85,86) and script in (10000,10001,10002) and not approved:
                objects.append(dict(id=obj,sprite=sprite,script=script))
            else:
                keep.append(row)
        if objects:
            groups[1]=keep;new_id=len(events.files)
            events.files.append(events_encode(groups))
            struct.pack_into('<H',d,rec+16,new_id)
            removed.append(dict(map=m,original_event=eid,event=new_id,objects=objects))
    return removed


def wild_table(original,slots):
    b=bytearray(original);assert len(b)==196
    b[0]=25;b[1:6]=bytes(5) # No water, fishing or rock-smash in these Yellow tables.
    mapped=[slots[i] for i in SLOT_MAP];b[8:20]=bytes(s['level'] for s in mapped)
    species=[SPECIES[s['species']] for s in mapped]
    for period in range(3):struct.pack_into('<12H',b,20+period*24,*species)
    # Later radio/radar/swarm replacement species must not introduce HG's
    # postgame tables. Ordinary grass slots, levels and exact weights remain.
    for at in [0x5C,0x60,0x64,0x68]:struct.pack_into('<2H',b,at,species[0],species[1])
    struct.pack_into('<2H',b,0xBC,species[0],species[1])
    return bytes(b)


def expanded_common(original,count):
    # Original 0..738 share a single script body; index 739 is trainer vision.
    # Insert aliases without duplicating/repacking relative branch bodies.
    n=0
    while struct.unpack_from('<H',original,n*4)[0]!=0xFD13:n+=1
    assert n>=740 and count>=n
    growth=4*(count-n);out=bytearray()
    for i in range(count):
        old=i if i<n else 0
        destination=old*4+4+struct.unpack_from('<I',original,old*4)[0]+growth
        out.extend(struct.pack('<I',destination-i*4-4))
    out.extend(original[n*4:]);return bytes(out)


def pickup(item,flag,message,obj=None):
    s=Script().emit(96).emit(32,flag).jump('done',1)
    s.emit(125,item,1,0x800C).compare(0x800C,0).jump('full',1)
    s.emit(30,flag).emit(78,1185).msg(message).emit(79)
    if obj is not None:s.emit(101,obj)
    end(s);s.label('full').msg(message+1);end(s)
    s.label('done');return end(s).finish()


def patch(rom):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=['a/0/1/2','a/0/2/7','a/0/3/2','a/0/5/5','a/0/5/6','a/0/3/7','a/0/5/7','a/1/3/1']
    arcs={p:ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    scripts,texts,events,trainers,parties,wild,trtable,offsets=arcs.values();report={'mappings':[],'trainers':[],'wild':[]}
    def current(m):
        rec=TABLE+24*m;sid,iid,tid=struct.unpack_from('<3H',d,rec+6);eid=struct.unpack_from('<H',d,rec+16)[0]
        return split_bank(scripts.files[sid]),tid,events_decode(events.files[eid])
    def install(m,bank,lines,g):
        rec=TABLE+24*m;sid=len(scripts.files);scripts.files.append(script_bank(bank));iid=len(scripts.files);scripts.files.append(bytes(4));tid=len(texts.files);texts.files.append(encode_text(lines,PH));eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid);report['mappings'].append(dict(map=m,script=sid,init=iid,text=tid,event=eid))
    # Remove only the north development boundary, keeping the coffee lesson,
    # Cut trees, parcel escort and western guard intact.
    bank,tid,g=current(50);g[3]=[row for row in g[3] if struct.unpack_from('<Hhh',row)!=(10,992,230)]
    eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,TABLE+50*24+16,eid);report['viridian_event']=eid
    # Both halves of Route 2 have no Yellow trainers. Inherited terrain gates
    # are removed separately after all area event edits.
    for m,item,flag,name in [(10,81,ITEM_FLAGS[5],'MOON STONE'),(414,45,ITEM_FLAGS[6],'HP UP')]:
        _,_,g=current(m);g[1]=[row for row in g[1] if struct.unpack_from('<H',row,6)[0]!=1]
        balls=[i for i,row in enumerate(g[1]) if struct.unpack_from('<H',row,2)[0]==87]
        assert len(balls)==1;i=balls[0];row=bytearray(g[1][i]);obj=struct.unpack_from('<H',row)[0];struct.pack_into('<2H',row,8,flag,2);g[1][i]=row
        lines=[DATA['messages']['Route2SignText'] if m==10 else DATA['messages']['Route2DiglettsCaveSignText'],f'You found a {name}!',"Your BAG is full. Make some room and come back."]
        g[0]=[struct.pack('<HHiiiH2x',1,1,1037,218 if m==10 else 139,0,4)]
        install(m,[talk(0),pickup(item,flag,1,obj)],lines,g)
        rec=TABLE+24*m;old=d[rec];wid=len(wild.files);wild.files.append(wild_table(wild.files[old],DATA['wild_slots']['Route2']));assert wid<255;d[rec]=wid;report['wild'].append(dict(map=m,original=old,member=wid))
    # Original trainer records remain archived. New native ordinary trainers
    # retain HG's vision, walking, reward, defeat flags and blackout behavior.
    _,_,g=current(147);key,names=decode_messages(texts.files[729]);msgkey,trmessages=decode_messages(texts.files[728]);table=bytearray(trtable.files[0]);ofs=bytearray(offsets.files[0]);new_ids=[]
    for entry in DATA['trainers']:
        trainer=len(trainers.files);new_ids.append(trainer);row=bytearray(trainers.files[entry['original_hg_trainer']]);row[0]=0;row[1]=entry['class'];row[3]=len(entry['team']);row[4:12]=bytes(8);struct.pack_into('<I',row,12,1);row[16]=0;trainers.files.append(row);parties.files.append(b''.join(struct.pack('<BB3H',128,0,level,species,0) for species,level in entry['team']));names.append(names[entry['original_hg_trainer']])
        while len(ofs)<2*(trainer+1):ofs.extend(struct.pack('<H',len(table)))
        struct.pack_into('<H',ofs,trainer*2,len(table))
        for kind,suffix in enumerate(['BattleText','EndBattleText','AfterBattleText']):
            table.extend(struct.pack('<2H',trainer,kind));trmessages.extend(decode_messages(encode_text([DATA['messages'][entry['dialogue']+suffix]],PH))[1])
        for i,a in enumerate(g[1]):
            if struct.unpack_from('<H',a)[0]==entry['actor']:
                b=bytearray(a);struct.pack_into('<H',b,10,3000+trainer-1)
                if entry['class']==3:struct.pack_into('<H',b,2,320)
                g[1][i]=b
        report['trainers'].append(dict(id=trainer,defeat_flag=0x550+trainer,**entry))
    texts.files[729]=encode_messages(key,names);texts.files[728]=encode_messages(msgkey,trmessages);trtable.files[0]=bytes(table);offsets.files[0]=bytes(ofs)
    common=len(scripts.files);scripts.files.append(expanded_common(scripts.files[953],max(new_ids)))
    for trigger in [3000,5000]:
        needle=struct.pack('<3H',trigger,953,40);assert d.count(needle)==1;at=d.index(needle);struct.pack_into('<H',d,at+2,common)
    report['trainer_common_bank']=common
    # Yellow's two Potions and one Poke Ball replace the four postgame items.
    # The original Bugsy event is retained in its original event/script members.
    lines=[DATA['messages']['ViridianForestYoungster1Text'],DATA['messages']['ViridianForestYoungster6Text']]
    bank=[talk(0),talk(1)];g[1]=[a for a in g[1] if struct.unpack_from('<H',a)[0] not in [0,1,2,3,4]]
    g[1].extend([actor(0,318,1,31,75,0,3),actor(12,318,2,25,71,0,3)])
    for obj,item,flag,x,z,name in [(1,17,ITEM_FLAGS[0],50,60,'POTION'),(2,17,ITEM_FLAGS[1],42,32,'POTION'),(3,4,ITEM_FLAGS[2],20,49,'POKE BALL')]:
        idx=len(lines);lines.extend([f'You found a {name}!',"Your BAG is full. Make some room and come back."]);sid=len(bank)+1;bank.append(pickup(item,flag,idx,obj));g[1].append(actor(obj,87,sid,x,z,flag,0))
    # Reuse two archived forest hidden-item IDs with a cloned native table.
    # Native item pickup and Dowsing Machine behavior remain functional.
    g[0]=[struct.pack('<HHiiiH2x',8085,2,32,75,0,4),struct.pack('<HHiiiH2x',8087,2,14,27,0,4)]
    prefix=struct.pack('<HBBHH',17,1,0,0,0)+struct.pack('<HBBHH',92,1,0,0,1)+struct.pack('<HBBHH',92,1,0,0,225)
    assert d.count(prefix)==1;table_at=d.index(prefix);native_table=bytearray(d[table_at:table_at+231*8]);assert len(native_table)==231*8
    for i in range(231):
        index=struct.unpack_from('<H',native_table,8*i+6)[0]
        if index in [85,87]:struct.pack_into('<H',native_table,8*i,17 if index==85 else 18)
    old_end=main.sections[1].ramAddress+len(main.sections[1].data);assert struct.unpack_from('<I',d,0xD2C68)[0]==old_end
    main.sections[1].data.extend(bytes(-len(main.sections[1].data)%4));address=main.sections[1].ramAddress+len(main.sections[1].data);main.sections[1].data.extend(native_table)
    pointer=struct.pack('<I',0x02000000+table_at);assert d.count(pointer)==2
    d[:]=d.replace(pointer,struct.pack('<I',address));struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data));assert len(main.sections[1].data)<0x8000
    report['hidden_items']=dict(original_table=hex(0x02000000+table_at),active_table=hex(address),ids=[8085,8087],items=[17,18])
    # Display Yellow's six tips at existing HG ground-sign positions.
    for label,x,z in [('TrainerTips1',26,41),('UseAntidoteSign',12,46),('TrainerTips2',47,46),('TrainerTips3',49,18),('TrainerTips4',32,57),('LeavingSign',11,17)]:
        idx=len(lines);lines.append(DATA['messages']['ViridianForest'+label+'Text']);sid=len(bank)+1;bank.append(talk(idx));g[0].append(struct.pack('<HHiiiH2x',sid,1,x,z,0,4))
    install(147,bank,lines,g);rec=TABLE+147*24;old=d[rec];wid=len(wild.files);wild.files.append(wild_table(wild.files[old],DATA['wild_slots']['ViridianForest']));d[rec]=wid;report['wild'].append(dict(map=147,original=old,member=wid))
    # Both gatehouses get Yellow's two informational NPCs and native warps.
    for m,labels,sprites in [(419,['ViridianForestSouthGateGirlText','ViridianForestSouthGateLittleGirlText'],[320,7]),(420,['ViridianForestNorthGateSuperNerdText','ViridianForestNorthGateGrampsText'],[331,330])]:
        _,_,g=current(m);g[1]=[actor(0,sprites[0],1,2,5,0,3),actor(1,sprites[1],2,8,8,0,2)];install(m,[talk(0),talk(1)],[DATA['messages'][v] for v in labels],g)
    # Do not expose untouched Pewter/endgame content before its conversion.
    bank,tid,g=current(414);key,msg=decode_messages(texts.files[tid]);idx=len(msg);msg.extend(decode_messages(encode_text(['Pewter City is the next area being prepared. Please explore Route 2 and VIRIDIAN FOREST for now.'],PH))[1]);s=Script().emit(96).msg(idx).movement(255,'back').emit(95);end(s).moves('back',[(13,1)]);sid=len(bank)+1;bank.append(s.finish());g[3].append(struct.pack('<Hhh5H',sid,1024,128,64,1,0,0,BOUNDARY));ns=len(scripts.files);scripts.files.append(script_bank(bank));nt=len(texts.files);texts.files.append(encode_messages(key,msg));ne=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,TABLE+414*24+6,ns);struct.pack_into('<H',d,TABLE+414*24+10,nt);struct.pack_into('<H',d,TABLE+414*24+16,ne);report['pewter_boundary']=dict(script=ns,text=nt,event=ne)
    report['removed_terrain_gates']=remove_kanto_terrain_gates(d,events)
    for p,a in arcs.items():rom.files[rom.filenames.idOf(p)]=a.save()
    rom.arm9=main.save(compress=True);report['item_flags']=list(ITEM_FLAGS);return report


def build():
    source=PROJECT/'build/yellow-heartgold-prototype-013.nds';assert sha(source.read_bytes())==INPUT_SHA and sha(BASE.read_bytes())==EXPECTED
    old=ndspy.rom.NintendoDSRom.fromFile(str(source));rom=ndspy.rom.NintendoDSRom.fromFile(str(source));report=patch(rom)
    banner=bytearray(rom.iconBanner);title='Pokemon Psyduck Yellow\nRoute 2 and Viridian Forest 014\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):banner[at:at+0x100]=title+bytes(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]));rom.iconBanner=bytes(banner);assert rom.arm7==old.arm7
    target=PROJECT/'build/yellow-heartgold-prototype-014.nds';target.write_bytes(rom.save());patchfile=target.with_suffix('.xdelta');decoded=PROJECT/'build/forest-roundtrip.nds';tool=PROJECT/'.tools/xdelta3'
    subprocess.run([str(tool),'-f','-e','-S','none','-s',str(BASE),str(target),str(patchfile)],check=True);subprocess.run([str(tool),'-f','-d','-s',str(BASE),str(patchfile),str(decoded)],check=True);assert sha(decoded.read_bytes())==sha(target.read_bytes())
    report.update(version='014',input_sha256=INPUT_SHA,output_sha256=sha(target.read_bytes()),patch_sha256=sha(patchfile.read_bytes()),changed_file_ids=[i for i,(a,b) in enumerate(zip(old.files,rom.files)) if a!=b]);(PROJECT/'build/forest-progression-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':build()
