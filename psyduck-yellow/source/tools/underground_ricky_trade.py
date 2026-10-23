"""Yellow RICKY trade in the unchanged native Route5 Underground entrance."""
import struct
import ndspy.narc
from build_rom import BASE
from viridian_tutorial import TABLE
from opening import events_decode,events_encode,script_bank,encode_text
from parcel_quest import split_bank,PH
from prototype import decode_messages,encode_messages

TRADE=9
DONE=0x133
MESSAGES=[
 '', '', '',
 'Hi! Do you have\rCUBONE?\nWant to trade it\rfor MACHOKE?',
 'Thanks, pal!',
 '...This is no\rCUBONE.\nIf you get one,\rtrade it with me!',
 "That's too bad.",
 'How is my old\rMACHOKE?\nMy CUBONE is\rdoing great!',
]
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/1/1/2')
 scripts,texts,events,trades=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 # Record9 belonged to the already-removed Kanto Pewter clinic trader. It is
 # absent from all active map script banks; keep other13 native trade IDs.
 needle=struct.pack('<HB',470,TRADE)
 for mid in range(540):
  sid=struct.unpack_from('<H',d,TABLE+mid*24+6)[0];assert needle not in scripts.files[sid],(mid,sid)
 original=ndspy.rom.NintendoDSRom.fromFile(str(BASE));arc=ndspy.narc.NARC(original.files[original.filenames.idOf('a/0/1/2')])
 native=split_bank(arc.files[753])[1]
 assert native.count(needle)==1 and struct.pack('<HH',30,DONE) in native
 rec=TABLE+469*24;assert d[rec+20]&1
 eid=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[eid]);assert len(g[1])==1
 actor=bytearray(g[1][0]);struct.pack_into('<H',actor,4,0);struct.pack_into('<H',actor,10,1);g[1]=[bytes(actor)]
 ns=len(scripts.files);scripts.files.append(script_bank([native]))
 ni=len(scripts.files);scripts.files.append(bytes(4));nt=len(texts.files);texts.files.append(encode_text(MESSAGES,PH));ne=len(events.files);events.files.append(events_encode(g))
 struct.pack_into('<3H',d,rec+6,ns,ni,nt);struct.pack_into('<H',d,rec+16,ne)
 row=bytearray(trades.files[TRADE]);assert len(row)==84
 struct.pack_into('<i',row,0,67);struct.pack_into('<i',row,19*4,104);struct.pack_into('<i',row,15*4,0)
 trades.files[TRADE]=bytes(row)
 key,names=decode_messages(texts.files[200]);assert len(names)==26
 converted=decode_messages(encode_text(['RICKY','TRAINER'],PH))[1];names[9]=converted[0];names[22]=converted[1];texts.files[200]=encode_messages(key,names)
 for p,a in zip(paths,(scripts,texts,events,trades)):rom.files[rom.filenames.idOf(p)]=a.save()
 rom.arm9=main.save(compress=True)
 return {'map':469,'trade':TRADE,'requested':104,'offered':67,'nickname':'RICKY','ot':'TRAINER','native_trade_flag':DONE,'event':ne,'scripts':ns,'init':ni,'messages':nt,'geometry_unchanged':True,'native_script_copied_exactly':True,'other_trade_records_preserved':True,'yellow_trade_evolution_expected':68,'native_trade_and_evolution_tests_pending':True}