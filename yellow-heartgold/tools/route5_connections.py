"""PRIVATE city boundary transitions for the standalone Yellow Route 5 probe.

Interim native HG city entry points, not final Yellow city layouts or save migration.
Original main matrix/lands remain intact. All added events are Kanto-only.
"""
import struct
import ndspy.narc
from opening import Script,script_bank,events_decode,events_encode
from parcel_quest import split_bank
from viridian_tutorial import TABLE
# source, rectangle, destination, x, z, facing (0 north,1 south)
LINKS=((52,(1291,157,3,1),13,9,1,1),(52,(1306,157,3,1),13,24,1,1),
       (59,(1300,199,2,1),13,16,34,0),
       (13,(6,0,15,1),52,1292,156,0),(13,(21,0,5,1),52,1307,156,0),
       (13,(6,35,20,1),59,1300,200,1))
def transition_script(m,x,z,facing):
 return Script().emit(96).emit(174,6,6,0,0).emit(175).emit(176,m,0,x,z,facing).emit(174,6,6,1,0).emit(175).emit(97).emit(2).finish()
def patch_probe_connections(rom,*,diagnostic=False):
 if not diagnostic:raise ValueError('Interim private city links require diagnostic=True')
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=('a/0/1/2','a/0/3/2');scripts,events=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths];old=[list(scripts.files),list(events.files)];changes=[]
 for m in (13,52,59):
  at=TABLE+m*24;assert d[at+20]&1,'Refuse non-Kanto source'
  sid=struct.unpack_from('<H',d,at+6)[0];eid=struct.unpack_from('<H',d,at+16)[0];bank=split_bank(scripts.files[sid]);groups=events_decode(events.files[eid])
  for source,rectangle,target,x,z,facing in LINKS:
   if source!=m:continue
   bank.append(transition_script(target,x,z,facing));scriptid=len(bank)
   sx,sz,w,h=rectangle;groups[3].append(struct.pack('<Hhh5H',scriptid,sx,sz,w,h,0,0,0))
  ns=len(scripts.files);scripts.files.append(script_bank(bank));ne=len(events.files);events.files.append(events_encode(groups));struct.pack_into('<H',d,at+6,ns);struct.pack_into('<H',d,at+16,ne);changes.append(m)
 for arc,p,prefix in zip((scripts,events),paths,old):assert arc.files[:len(prefix)]==prefix;rom.files[rom.filenames.idOf(p)]=arc.save()
 rom.arm9=main.save(compress=True)
 return dict(private=True,released=False,changed_headers=changes,links=[list(v) for v in LINKS],main_matrix_unchanged=True,pending=['native bidirectional tests','legacy save migration','final Yellow city geometry','Fly/followers/camera'])
