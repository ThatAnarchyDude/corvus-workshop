"""Read-only audit of Yellow's Underground content and the current native room."""
import re,hashlib,struct
from pathlib import Path
import ndspy.narc
from opening import events_decode
from viridian_tutorial import TABLE
def audit(rom,yellow_source):
 source=Path(yellow_source);inputs={}
 def read(path):
  raw=(source/path).read_bytes();inputs[path]=hashlib.sha256(raw).hexdigest();return raw.decode()
 hidden=read('data/events/hidden_events.asm')
 block=re.search(r'hidden_events_for UNDERGROUND_PATH_NORTH_SOUTH\s*\n(.*?)(?=\s*db -1)',hidden,re.S).group(1)
 expected=[{'yellow_position':[int(x),int(z)],'name':name,'item':{'FULL_RESTORE':23,'X_SPECIAL':61}[name]} for x,z,name in re.findall(r'hidden_event\s+(\d+),\s*(\d+),\s*HiddenItems,\s*(\w+)',block)]
 trades=read('data/events/trades.asm');trade=re.search(r'npctrade\s+(\w+),\s*(\w+),\s*(\w+),\s*"RICKY"',trades)
 read('scripts/UndergroundPathRoute5.asm')
 evolution=read('engine/events/in_game_trades.asm')
 section=evolution.split('InGameTrade_CheckForTradeEvo:')[1].split('InGameTrade_TrainerString:')[0]
 assert 'cp MACHOKE' in section and 'callfar TryEvolvingMon' in section
 m=rom.loadArm9();d=m.sections[0].data;e=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')]);g=events_decode(e.files[struct.unpack_from('<H',d,TABLE+532*24+16)[0]])
 prefix=struct.pack('<HBBHH',17,1,0,0,0)+struct.pack('<HBBHH',92,1,0,0,1)+struct.pack('<HBBHH',92,1,0,0,225);itcm=m.sections[1].data;assert itcm.count(prefix)==1;start=itcm.index(prefix);native=[]
 for bg in g[0]:
  sid,kind,x,z,h,face=struct.unpack('<HHiiiH2x',bg);assert kind==2
  rows=[at for at in range(start,start+231*8,8) if struct.unpack_from('<H',itcm,at+6)[0]==sid-8000];assert len(rows)==1
  item=struct.unpack_from('<H',itcm,rows[0])[0];native.append({'script':sid,'position':[x,z],'item':item,'flag':0x320+sid-8000})
 assert sorted(v['item'] for v in native)==sorted(v['item'] for v in expected)
 assert trade.group(1,2)==('CUBONE','MACHOKE')
 return {'yellow_hidden':expected,'native_hidden':native,'hidden_rewards_already_match':True,'native_positions_retained_per_interior_preference':True,'north_trade':{'requested_species':104,'offered_species':67,'nickname':'RICKY','trade_evolution_species':68,'trade_evolution_name':'MACHAMP','dialogue_set':trade.group(3),'implemented':False},'source_hashes':inputs,'rom_modified':False}