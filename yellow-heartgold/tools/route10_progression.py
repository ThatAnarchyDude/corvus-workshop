"""Yellow Route10 trainers and encounters on preserved HG north/south paths."""
import struct
import ndspy.narc
from opening import actor,events_decode,events_encode
from viridian_tutorial import TABLE
from forest_progression import SLOT_MAP
from route6_trainers import patch as install_trainers

PLACEMENTS=((18,1430,186),(388,1416,201),(388,1430,205),(18,1429,167),(388,1415,210),(388,1425,215))
TEMPLATES={'Pokemaniac':23,'Hiker':25,'JrTrainerF':27}
SPRITES={'Pokemaniac':332,'Hiker':333,'JrTrainerF':346}
FACING={'UP':0,'DOWN':1,'LEFT':2,'RIGHT':3}
def patch(rom,reference):
 report=install_trainers(rom,reference,map_name='Route10',expected_count=6,templates=TEMPLATES)
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 events=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')]);wild=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/7')]);maps=[]
 for map_id in (18,388):
  rec=TABLE+map_id*24;old=struct.unpack_from('<H',d,rec+16)[0];g=events_decode(events.files[old]);others=[a for a in g[1] if not 3000<=struct.unpack_from('<H',a,10)[0]<4000]
  ids={struct.unpack_from('<H',a)[0] for a in others};added=[]
  for i,((m,x,y),entry,battle) in enumerate(zip(PLACEMENTS,reference['trainers'],report['trainers'])):
   if m!=map_id:continue
   obj=next(n for n in range(32) if n not in ids);ids.add(obj)
   a=bytearray(actor(obj,SPRITES[entry['role']],3000+battle['id']-1,x,y,facing=FACING[entry['facing']]))
   struct.pack_into('<H',a,6,1);struct.pack_into('<H',a,14,entry['vision']);added.append(bytes(a))
  g[1]=others+added;new=len(events.files);events.files.append(events_encode(g));struct.pack_into('<H',d,rec+16,new);maps.append(dict(map=map_id,original_event=old,event=new))
 rec=TABLE+18*24;old_wild=d[rec];row=bytearray(wild.files[old_wild]);assert len(row)==196
 row[:6]=bytes([15,0,0,0,0,0]);slots=[reference['grass'][i] for i in SLOT_MAP];row[8:20]=bytes(p['level'] for p in slots)
 for period in range(3):struct.pack_into('<12H',row,20+period*24,*(p['species'] for p in slots))
 for at in (0x5C,0x60,0xBC):struct.pack_into('<2H',row,at,81,19)
 wid=len(wild.files);assert wid<255;wild.files.append(bytes(row));d[rec]=wid
 rom.files[rom.filenames.idOf('a/0/3/2')]=events.save();rom.files[rom.filenames.idOf('a/0/3/7')]=wild.save();rom.arm9=main.save(compress=True)
 return dict(trainers=report['trainers'],common=report['common'],common_sites=report['common_reference_sites'],maps=maps,wild=wid,positions=PLACEMENTS,native_test='pending',preserved='native terrain, warps, triggers, nontrainer actors and unrelated maps')
