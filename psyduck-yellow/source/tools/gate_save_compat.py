"""Private Kanto-only compatibility for saves from the former larger gate."""
import struct
import ndspy.narc
from opening import Script,script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE
# Native scratch variables; no new persistent story flags or saved allocations.
TEMP0=0x4000;TEMP1=0x4001

def compatibility_scripts(cells):
 valid=sorted((c['x'],c['y']) for c in cells if c['walkable'])
 # ON_RESUME is immediate: inspect actors/coordinates and only schedule a scene.
 # Never invoke an asynchronous Warp from an immediate load script.
 s=Script().emit(106,0,TEMP0,TEMP1).compare(TEMP0,1).jump('migrate',5).compare(TEMP1,3).jump('migrate',5).emit(105,TEMP0,TEMP1)
 for i,(x,z) in enumerate(valid):
  s.compare(TEMP0,x).jump('next'+str(i),5).compare(TEMP1,z).jump('valid',1).label('next'+str(i))
 s.label('migrate').emit(41,TEMP0,1).emit(2)
 s.label('valid').emit(41,TEMP0,0).emit(41,TEMP1,0).emit(2)
 resume=s.finish()
 s=Script().emit(96).emit(41,TEMP0,0).emit(41,TEMP1,0).emit(105,0x8004,0x8005).compare(0x8005,8).jump('south',4)
 for label,z,facing in (('north',2,1),('south',4,0)):
  s.label(label).emit(174,6,6,0,0).emit(175).emit(176,391,0,3,z,facing).emit(174,6,6,1,0).emit(175).emit(97).emit(2)
 return resume,s.finish()

def patch_gate_save_compatibility(rom,topology,*,diagnostic=False):
 if not diagnostic:raise ValueError('Private compatibility scene requires diagnostic=True')
 assert topology['map']=='Route5Gate' and topology['dimensions']==[8,6]
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data);rec=TABLE+391*24;assert d[rec+20]&1
 fid=rom.filenames.idOf('a/0/1/2');scripts=ndspy.narc.NARC(rom.files[fid]);old=list(scripts.files)
 sid,iid=struct.unpack_from('<2H',d,rec+6);assert scripts.files[iid]==bytes(4)
 bank=split_bank(scripts.files[sid]);assert len(bank)==2
 resume,scene=compatibility_scripts(topology['cells']);resume_id=len(bank)+1;scene_id=resume_id+1
 ns=len(scripts.files);scripts.files.append(script_bank(bank+[resume,scene]));ni=len(scripts.files)
 scripts.files.append(struct.pack('<BHHBI',3,resume_id,0,1,1)+bytes(1)+struct.pack('<3H',TEMP0,1,scene_id)+bytes(2))
 struct.pack_into('<2H',d,rec+6,ns,ni);rom.arm9=main.save(compress=True);rom.files[fid]=scripts.save();assert scripts.files[:len(old)]==old
 return dict(private=True,map=391,script=ns,init=ni,resume_script=resume_id,migration_scene=scene_id,temporary_variables=[TEMP0,TEMP1],new_story_flags=False,pending=['native old north/south saves','normal new-room save no-repeat','bag/party/PC/guard-flag preservation'])
