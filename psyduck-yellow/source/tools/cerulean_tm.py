"""Yellow's Cerulean BubbleBeam TM without replacing any of HeartGold's existing TMs.

Reuse spare item IDs and unused compatibility bits. The save format and pocket
capacity remain native. Existing reusable-TM teaching also covers these items.
"""
import json
import struct
import ndspy.narc
import ndspy.code
from build_rom import PROJECT
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages, encode_messages, thumb_bl
from starter_properties import append_code
from yellow_tms import ITEM_TABLE, MOVE_ENTRY, INDEX_ENTRY

TMS = (
    dict(item=119,move=61,index=104,number=11,name='BUBBLEBEAM',key='BUBBLEBEAM',
         template=330,later_index=2,description='A spray of bubbles strikes the target and may lower its Speed.'),
)


def patch(rom, configs=TMS, yellow_compatibility=None, later_name='Water Pulse'):
    TMS = configs
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    assert struct.unpack_from('<I',d,0xD2C68)[0]==main.sections[1].ramAddress+len(main.sections[1].data)
    assert d[0x825B4:0x825B8]==bytes.fromhex('c046c046'), 'Reusable TM patch required'
    lookups=[]
    for site,field in ((MOVE_ENTRY,'move'),(INDEX_ENTRY,'index')):
        at=site-0x02000000
        assert d[at:at+4]==bytes.fromhex('004b1847'), 'Existing Bide lookup required'
        previous=struct.unpack_from('<I',d,at+4)[0]
        source=''
        for tm in TMS:source+=f"cmp r0, #{tm['item']}\nbeq tm{tm['item']}\n"
        source+='ldr r3, previous\nbx r3\n'
        for tm in TMS:source+=f"tm{tm['item']}:\nmovs r0, #{tm[field]}\nbx lr\n"
        source+=f'.align 2\nprevious: .word {previous}\n'
        address,_=append_code(main,source)
        d[at:at+8]=bytes.fromhex('004b1847')+struct.pack('<I',address|1)
        lookups.append(dict(site=hex(site),hook=hex(address),previous=hex(previous)))

    # The native UI computes the displayed TM number from a contiguous item
    # range. Substitute only the display value, retaining the actual bag ID.
    overlays=rom.loadArm9Overlays();bag=overlays[15];display=[]
    # Later checkpoints replace these display hooks. Retain every earlier
    # custom TM number instead of showing a native contiguous-range number.
    numbers = {item:number for item,number in
               ((115,34),(116,12),(117,1),(118,4),(119,11),(122,45))
               if struct.unpack_from('<H',d,ITEM_TABLE+item*8)[0]}
    numbers.update((tm['item'],tm['number']) for tm in TMS)
    for site,load in ((0x021FE920,'ldrh r1, [r7]'),(0x021FF5B2,'ldrh r1, [r3, r7]')):
        at=site-bag.ramAddress
        assert bag.data[at+1]&0xF8==0xF0 and bag.data[at+3]&0xF8==0xF8
        source=load+'\n'
        for item in numbers:source+=f'cmp r1, #{item}\nbeq item{item}\n'
        source+='b finish\n'
        for item,number in numbers.items():
            source+=f'item{item}:\nldr r1, value{item}\nb finish\n'
        source+='finish:\nlsls r0, r0, #2\nbx lr\n.align 2\n'
        for item,number in numbers.items():source+=f'value{item}: .word {327+number}\n'
        address,_=append_code(main,source);bag.data[at:at+4]=thumb_bl(site,address)
        display.append(dict(site=hex(site),hook=hex(address)))
    rom.files[bag.fileID]=bag.save(compress=bag.compressed)
    rom.arm9OverlayTable=ndspy.code.saveOverlayTable(overlays)

    personal_id=rom.filenames.idOf('a/0/0/2');personal=ndspy.narc.NARC(rom.files[personal_id])
    yellow=yellow_compatibility if yellow_compatibility is not None else {'BUBBLEBEAM':json.loads((PROJECT/'data/cerulean.json').read_text())['bubblebeam_compatible_species']}
    compatible={tm['key']:[] for tm in TMS}
    for species,row in enumerate(personal.files):
        b=bytearray(row)
        for tm in TMS:
            assert not row[28+tm['index']//8] & (1<<(tm['index']%8)), 'Compatibility bit already used'
            eligible=species in yellow[tm['key']] if species<=151 else bool(row[28+tm['later_index']//8] & (1<<(tm['later_index']%8)))
            if eligible:
                b[28+tm['index']//8]|=1<<(tm['index']%8);compatible[tm['key']].append(species)
        personal.files[species]=bytes(b)
    rom.files[personal_id]=personal.save()
    item_id=rom.filenames.idOf('a/0/1/7');items=ndspy.narc.NARC(rom.files[item_id])
    text_id=rom.filenames.idOf('a/0/2/7');texts=ndspy.narc.NARC(rom.files[text_id])
    for tm in TMS:
        assert struct.unpack_from('<H',d,ITEM_TABLE+tm['item']*8)[0]==0
        source,icon,palette,_=struct.unpack_from('<4H',d,ITEM_TABLE+tm['template']*8)
        row=bytearray(items.files[source]);struct.pack_into('<H',row,0,0)
        index=len(items.files);items.files.append(row)
        struct.pack_into('<4H',d,ITEM_TABLE+tm['item']*8,index,icon,palette,0)
        for bank,line in ((222,f"TM{tm['number']:02d}"),(221,'A reusable TM containing '+tm['name']+'. '+tm['description'])):
            key,messages=decode_messages(texts.files[bank]);messages[tm['item']]=decode_messages(encode_text([line],PH))[1][0]
            texts.files[bank]=encode_messages(key,messages)
    rom.files[item_id]=items.save();rom.files[text_id]=texts.save()
    struct.pack_into('<I',d,0xD2C68,main.sections[1].ramAddress+len(main.sections[1].data))
    rom.arm9=main.save(compress=True)
    return dict(tms=TMS,lookup_hooks=lookups,display_hooks=display,compatible_species=compatible,
                generation_one_compatibility='Yellow',later_compatibility=later_name,
                native_tm_items_preserved=True,native_save_layout_preserved=True)
