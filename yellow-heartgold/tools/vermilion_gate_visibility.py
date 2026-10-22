"""Keep the Route 6 gate model available while approaching from Vermilion."""
import struct
import ndspy.narc
from viridian_tutorial import TABLE

def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 area_id=rom.filenames.idOf('a/0/4/2');areas=ndspy.narc.NARC(rom.files[area_id])
 lists=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/3')]);textures=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/7/0')])
 city=bytearray(areas.files[d[TABLE+54*24+1]]);route=areas.files[d[TABLE+14*24+1]]
 city_list=struct.unpack_from('<H',city)[0];route_list=struct.unpack_from('<H',route)[0]
 def models(i):
  raw=lists.files[i];values=struct.unpack('<'+'H'*(len(raw)//2),raw);assert values[0]==len(values)-1;return values[1:]
 assert set(models(city_list)).issubset(models(route_list))
 assert set(models(route_list))-set(models(city_list))=={342}
 assert textures.files[city_list]==textures.files[route_list], 'Never substitute an incompatible prop texture bank'
 struct.pack_into('<H',city,0,route_list);new_area=len(areas.files);assert new_area<256
 areas.files.append(bytes(city));d[TABLE+54*24+1]=new_area
 rom.files[area_id]=areas.save();rom.arm9=main.save(compress=True)
 return {'map':54,'old_model_list':city_list,'new_model_list':route_list,'added_model':342,'new_area':new_area,'native_gameplay_validation_pending':True}