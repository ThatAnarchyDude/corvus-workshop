"""Yellow's Cerulean Bicycle voucher exchange in a preserved HG bike interior."""
import struct
import ndspy.narc
from opening import Script, actor, events_decode, events_encode, script_bank, encode_text, talk, end
from parcel_quest import PH
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE
from yellow_tms import ITEM_TABLE

MAP=432
VOUCHER=120
BICYCLE=450
RECEIVED=0xB60


def clerk():
    s=Script().emit(73,1500).emit(96).emit(104).emit(32,RECEIVED).jump('owned',1)
    s.emit(127,BICYCLE,1,0x800C).compare(0x800C,1).jump('owned',1)
    s.emit(127,VOUCHER,1,0x800C).compare(0x800C,1).jump('exchange',1)
    s.msg(0).msg(1).emit(63,0x800C).compare(0x800C,0).jump('cancel',5).msg(2)
    s.label('cancel').msg(3);end(s)
    s.label('exchange').msg(4).emit(125,BICYCLE,1,0x800C).compare(0x800C,0).jump('full',1)
    # Award first. Keep the voucher when the key-item pocket cannot accept it.
    s.emit(126,VOUCHER,1,0x800C).emit(30,RECEIVED).emit(30,0x89)
    s.emit(78,1185).msg(5).emit(79);end(s)
    s.label('owned').msg(6);end(s)
    s.label('full').msg(7);return end(s).finish()


def youngster():
    s=Script().emit(73,1500).emit(96).emit(104).emit(127,BICYCLE,1,0x800C)
    s.compare(0x800C,1).jump('owned',1).msg(9);end(s)
    s.label('owned').msg(10);return end(s).finish()


def patch(rom,messages):
    main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
    paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/4/1','a/0/1/7')
    scripts,texts,events,matrices,items=arcs=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    rec=TABLE+MAP*24;original=bytes(d[rec:rec+24]);native=TABLE+182*24
    template=struct.unpack_from('<H',d,native+16)[0];g=events_decode(events.files[template])
    # Clone the Goldenrod interior and its matrix; leave every Johto asset and
    # header intact. Its counter and bicycle displays replace the empty HG house.
    matrix=struct.unpack_from('<H',d,native+4)[0];new_matrix=len(matrices.files);matrices.files.append(matrices.files[matrix])
    struct.pack_into('<H',d,rec+4,new_matrix)
    g[1]=[actor(0,328,1,8,6,0,1),actor(1,330,2,9,9,0,0),actor(2,315,3,3,8,0,3)]
    g[2]=[struct.pack('<6H',6,11,52,6,0,0)];g[0]=[];g[3]=[]
    labels=('BikeShopClerkWelcomeText','BikeShopClerkDoYouLikeItText','BikeShopCantAffordText','BikeShopComeAgainText','BikeShopClerkOhThatsAVoucherText','BikeShopExchangedVoucherText','BikeShopClerkHowDoYouLikeYourBicycleText','BikeShopBagFullText','BikeShopMiddleAgedWomanText','BikeShopYoungsterTheseBikesAreExpensiveText','BikeShopYoungsterCoolBikeText')
    lines=[messages[x] for x in labels];lines[1]='BICYCLE: 1,000,000 Pokedollars.\r'+lines[1]
    sid=len(scripts.files);scripts.files.append(script_bank([clerk(),talk(8),youngster()]));iid=len(scripts.files);scripts.files.append(bytes(4));tid=len(texts.files);texts.files.append(encode_text(lines,PH));eid=len(events.files);events.files.append(events_encode(g));struct.pack_into('<3H',d,rec+6,sid,iid,tid);struct.pack_into('<H',d,rec+16,eid)
    assert struct.unpack_from('<H',d,ITEM_TABLE+VOUCHER*8)[0]==0
    source,icon,palette,_=struct.unpack_from('<4H',d,ITEM_TABLE+460*8) # Coupon: paper key item, not usable/registerable.
    index=len(items.files);items.files.append(items.files[source]);struct.pack_into('<4H',d,ITEM_TABLE+VOUCHER*8,index,icon,palette,0)
    for bank,line in ((222,'BIKE VOUCHER'),(221,'A voucher that can be exchanged for a BICYCLE at the CERULEAN CITY BIKE SHOP.')):
        key,words=decode_messages(texts.files[bank]);words[VOUCHER]=decode_messages(encode_text([line],PH))[1][0];texts.files[bank]=encode_messages(key,words)
    for path,arc in zip(paths,arcs):rom.files[rom.filenames.idOf(path)]=arc.save()
    rom.arm9=main.save(compress=True)
    return dict(map=MAP,script=sid,text=tid,event=eid,matrix=new_matrix,source_matrix=matrix,original_header=original.hex(),voucher=VOUCHER,bicycle=BICYCLE,received_flag=RECEIVED,voucher_source='Vermilion fan club, in its later area checkpoint',johto_unchanged=True)
