"""Vermilion integration of the shared Kanto Mart stock and native menu flow."""
import json,struct
from pathlib import Path
import ndspy.narc
from opening import Script
from kanto_mart_inventory import badge_count_script
from kanto_mart_inline import assemble,inline_catalog,SITE,RESUME
from prototype import thumb_bl
from viridian_tutorial import TABLE
IDS={'POKE_BALL':4,'GREAT_BALL':3,'ULTRA_BALL':2,'POTION':17,'ANTIDOTE':18,'BURN_HEAL':19,'ICE_HEAL':20,'AWAKENING':21,'PARLYZ_HEAL':22,'HYPER_POTION':25,'SUPER_POTION':26,'FULL_HEAL':27,'REVIVE':28,'SUPER_REPEL':76,'MAX_REPEL':77,'ESCAPE_ROPE':78,'REPEL':79}

def vendor_script(stages,vendor):
 s=Script().emit(73,1500).emit(96).emit(104).emit(20,2011).emit(54)
 s.label('menu').emit(746).emit(749);s.data.extend(bytes((1,1,0,1))+struct.pack('<H',0x800C))
 for message,value in ((321,0),(322,1),(323,2)):s.emit(751,message,255,value)
 s.emit(752).compare(0x800C,0).jump('buy',1).compare(0x800C,1).jump('sell',1).jump('exit')
 s.label('buy');s.data.extend(badge_count_script());s.emit(42,0x8005,0x8004).emit(41,0x8004,30)
 for count in range(8):s.compare(0x8005,count).jump('stage'+str(count),1)
 s.jump('stage8')
 for stage in stages:
  s.label('stage'+str(stage['badges'])).emit(276,0x8004)
  s.data.extend(inline_catalog(IDS[name] for name in stage[vendor]));s.jump('return')
 s.label('sell').emit(782).jump('return')
 s.label('return').emit(438,3,0x800C).emit(440,0x800C,6).emit(54).jump('menu')
 s.label('exit').emit(747).emit(438,3,0x800C).emit(440,0x800C,1).emit(50).emit(53).emit(97).emit(2)
 return s.finish()

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);base=main.sections[0].ramAddress
 old=Path('yellow-heartgold/build/0030-mart-stock-v1/report.json');report=json.loads(old.read_text());address=report['hook'];size=report['hook_bytes'];itcm=main.sections[1]
 assert size==44 and address+size==itcm.ramAddress+len(itcm.data)
 reference=__import__('ndspy.rom',fromlist=['NintendoDSRom']).NintendoDSRom.fromFile('yellow-heartgold/build/0030-mart-stock-v1/private-mart-stock.nds').loadArm9()
 assert itcm.data[-size:]==reference.sections[1].data[-size:]
 assert d[SITE-base:RESUME-base]==reference.sections[0].data[SITE-base:RESUME-base]
 raw=assemble(address);itcm.data[-size:]=raw+bytes(size-len(raw))
 d[SITE-base:RESUME-base]=thumb_bl(SITE,address)+bytes.fromhex('c046')*5
 stages=json.loads(Path('yellow-heartgold/data/kanto-mart-inventory.json').read_text())['verified_stages'];assert len(stages)==9
 fid=rom.filenames.idOf('a/0/1/2');arc=ndspy.narc.NARC(rom.files[fid]);rec=TABLE+360*24;sid=struct.unpack_from('<H',d,rec+6)[0];native=arc.files[sid];bank=bytearray(native)
 # Native actor1 is at y4 (north) and uses entry1; actor0 at y6 uses entry0.
 for entry,vendor in ((0,'supplies'),(1,'balls')):
  bank.extend(bytes(-len(bank)%4));at=len(bank);bank.extend(vendor_script(stages,vendor));struct.pack_into('<I',bank,entry*4,at-entry*4-4)
 assert bank[8:len(native)]==native[8:]
 ns=len(arc.files);arc.files.append(bytes(bank));rom.files[fid]=arc.save();struct.pack_into('<H',d,rec+6,ns);rom.arm9=main.save(compress=True)
 return {'map':360,'script':ns,'old_script':sid,'hook':address,'hook_bytes':len(raw),'reserved_hook_bytes':size,'itcm_remaining':32768-len(itcm.data),'native_common_scripts_unchanged':True,'northern_entry':1,'southern_entry':0,'stock_stages':9,'native_buy_sell_cancel_pending':True}