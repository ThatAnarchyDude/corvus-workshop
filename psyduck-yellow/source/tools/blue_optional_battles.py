"""Owner-approved optional wins for existing pre-Champion Blue encounters."""
import struct
import ndspy.narc
from parcel_quest import split_bank
from opening import script_bank
from viridian_tutorial import TABLE
from progression_cleanup import rival_scene as route_scene
from cerulean import rival_scene as city_scene

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 fid=rom.filenames.idOf('a/0/1/2');arc=ndspy.narc.NARC(rom.files[fid]);report=[]
 for map_id,first,generator,args in ((27,747,route_scene,{}),(52,782,city_scene,{'lanes':range(1325,1330)})):
  ids={f'{s}_{g}':first+i for i,(s,g) in enumerate(((54,'male'),(54,'female'),(133,'male'),(133,'female')))};ids.update({54:first,133:first+3})
  at=TABLE+map_id*24;old_sid=struct.unpack_from('<H',d,at+6)[0];bank=split_bank(arc.files[old_sid]);old=generator(ids,optional=False,**args)
  assert bank[0].startswith(old),(map_id,'Scene does not match expected predecessor')
  assert len(bank[0])-len(old)<=3 and not any(bank[0][len(old):])
  preserved=bank[1:];bank[0]=generator(ids,optional=True,**args);new_sid=len(arc.files);arc.files.append(script_bank(bank));struct.pack_into('<H',d,at+6,new_sid)
  assert split_bank(arc.files[new_sid])[1:]==preserved
  report.append(dict(map=map_id,old_script_bank=old_sid,new_script_bank=new_sid,trainers=list(range(first,first+4)),native_party_heal_on_loss=True,scene_completes_on_loss=True))
 rom.files[fid]=arc.save();rom.arm9=main.save(compress=True);return report
