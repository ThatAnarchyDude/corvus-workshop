"""0019 manual sign use, solid items, Yellow Route 4 and cumulative invariants."""
import json,struct,sys,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from viridian_tutorial import TABLE
from opening import events_decode
from parcel_quest import split_bank
from field_interaction_fixes import FOREST_BOARDS,BOARD_HEIGHTS
from item_collision import SITE
from yellow_tms import MOVE_ENTRY,INDEX_ENTRY
from forest_progression import HG_WEIGHTS

class Prototype0019Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0018.nds'))
  cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0019.nds'))
  cls.cache={};cls.headers={id(cls.old):cls.old.loadArm9().sections[0].data,id(cls.new):cls.new.loadArm9().sections[0].data}
  cls.report=json.loads((PROJECT/'build/0019-development-report.json').read_text());cls.d=cls.new.loadArm9().sections[0].data
 def arc(self,r,p):
  key=(id(r),p)
  if key not in self.cache:self.cache[key]=ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
  return self.cache[key]
 def groups(self,r,m):
  d=self.headers[id(r)];return events_decode(self.arc(r,'a/0/3/2')[struct.unpack_from('<H',d,TABLE+m*24+16)[0]])
 def cpu(self,r):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x01FF8000,0x8000);u.mem_map(0x02000000,0x400000)
  for s in r.loadArm9().sections[:2]:u.mem_write(s.ramAddress,bytes(s.data))
  return u
 def test_all_Kanto_signs_require_interaction_and_hidden_items_remain(self):
  for m in range(540):
   if not self.d[TABLE+m*24+20]&1:continue
   before,after=self.groups(self.old,m)[0],self.groups(self.new,m)[0]
   self.assertFalse(any(struct.unpack_from('<H',r,2)[0]==1 for r in after),m)
   if m!=12:self.assertEqual([r for r in before if struct.unpack_from('<H',r,2)[0]==2],[r for r in after if struct.unpack_from('<H',r,2)[0]==2],m)
  for m,x in ((10,1029),(414,1047)):self.assertEqual(struct.unpack_from('<i',self.groups(self.new,m)[0][0],4)[0],x)
 def test_forest_boards_have_correct_heights_and_reachable_interactions(self):
  import collections
  matrix=self.arc(self.new,'a/0/4/1')[struct.unpack_from('<H',self.d,TABLE+147*24+4)[0]];w,h,hdr,alt,n=matrix[:5];off=5+n+2*w*h*hdr+w*h*alt
  lands=self.arc(self.new,'a/0/6/5')
  def permission(x,z):
   raw=lands[struct.unpack_from('<H',matrix,off+2*(z//32*w+x//32))[0]];return struct.unpack_from('<H',raw,20+2*(z%32*32+x%32))[0]
  seen={(32,77)};q=collections.deque(seen)
  while q:
   x,z=q.popleft()
   for nx,nz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
    if 0<=nx<w*32 and 0<=nz<h*32 and (nx,nz) not in seen and not permission(nx,nz)&0x8000:seen.add((nx,nz));q.append((nx,nz))
  self.assertIn((12,16),seen)
  for (x,z),height in zip(FOREST_BOARDS,BOARD_HEIGHTS):
   raw=lands[struct.unpack_from('<H',matrix,off+2*(z//32*w+x//32))[0]];ps,bs=struct.unpack_from('<2I',raw);matching=[]
   for at in range(20+ps,20+ps+bs,48):
    model,px,py,pz=struct.unpack_from('<I3i',raw,at)
    if model==31 and px==int((x%32-15.5)*65536) and pz==int((z%32-15.5)*65536):matching.append(py)
   self.assertEqual(matching,[height*65536]);self.assertTrue(permission(x,z)&0x8000)
   self.assertTrue(any(p in seen for p in ((x-1,z),(x+1,z),(x,z-1),(x,z+1))),(x,z))
 def test_background_messages_do_not_turn_a_nonexistent_NPC(self):
  for m in (10,414,147,51,11,12):
   bank=split_bank(self.arc(self.new,'a/0/1/2')[struct.unpack_from('<H',self.d,TABLE+m*24+6)[0]])
   for row in self.groups(self.new,m)[0]:
    sid,kind=struct.unpack_from('<2H',row)
    if kind==0:self.assertNotEqual(bank[sid-1][:4],struct.pack('<2H',96,104))
 def test_johto_headers_and_0018_models_teams_services_preserved(self):
  old=self.old.loadArm9().sections[0].data
  for m in range(540):
   a=TABLE+m*24
   if not old[a+20]&1:self.assertEqual(old[a:a+24],self.d[a:a+24],m)
  for p in ('a/0/8/1','a/0/5/8','a/0/0/3','a/0/3/7','a/0/5/5','a/0/5/6'):
   before,after=self.arc(self.old,p),self.arc(self.new,p);self.assertEqual(before,after[:len(before)],p)
  for m in (107,448,511):self.assertEqual(self.groups(self.old,m)[1:],self.groups(self.new,m)[1:])
 def test_ordinary_objects_keep_collision_flags_and_items_ignore_pass_through_flag(self):
  old,new=self.cpu(self.old),self.cpu(self.new)
  for sprite in range(1024):
   for flags in (0,1,0x40000,0x40001,0xffffffff):
    for cpu in (old,new):
     data=bytearray(32);struct.pack_into('<I',data,0,flags);struct.pack_into('<I',data,16,sprite);cpu.mem_write(0x023E0000,bytes(data));cpu.reg_write(UC_ARM_REG_R0,0x023E0000);cpu.reg_write(UC_ARM_REG_R1,0x40000);cpu.emu_start(SITE|1,SITE+4,count=60)
    expected=0 if sprite==87 else old.reg_read(UC_ARM_REG_R0)
    self.assertEqual(new.reg_read(UC_ARM_REG_R0),expected);self.assertEqual(new.reg_read(UC_ARM_REG_R1),0x40000)
  a=self.old.loadArm9().sections[0].data;b=self.d
  self.assertEqual(a[0x60BFC:0x60C34],b[0x60BFC:0x60C34]);self.assertEqual(a[0x60C38:0x60CA8],b[0x60C38:0x60CA8])
 def test_route4_has_yellow_optional_lass_and_one_item_preserving_warps(self):
  r=self.report['route4'];tid=r['trainer'];header=self.arc(self.new,'a/0/5/5')[tid];self.assertEqual((header[0],header[1],header[3]),(1,3,3))
  team=list(struct.iter_unpack('<BB3H4H',self.arc(self.new,'a/0/5/6')[tid]));self.assertEqual([(p[3],p[2],p[5:]) for p in team],[(46,31,(10,78,141,147)),(46,31,(10,78,141,147)),(47,31,(10,78,141,147))])
  g=self.groups(self.new,12);self.assertEqual(self.groups(self.old,12)[2],g[2]);self.assertEqual(len(g[1]),2);self.assertEqual(struct.unpack_from('<2H',g[1][1]),(3,87));self.assertFalse(g[3])
 def test_route4_species_levels_and_probabilities_all_time_periods(self):
  data=self.arc(self.new,'a/0/3/7')[self.report['route4']['wild']];self.assertEqual(data[:6],bytes((20,0,0,0,0,0)))
  slots=json.loads((PROJECT/'data/route4.json').read_text())['wild_slots'];weights=[20,20,15,10,10,10,5,5,4,1]
  for period in range(3):
   mons=struct.unpack_from('<12H',data,20+period*24);seen={}
   for p,l,w in zip(mons,data[8:20],HG_WEIGHTS):seen[(p,l)]=seen.get((p,l),0)+w
   wanted={(s['species'],s['level']):w for s,w in zip(slots,weights)};self.assertEqual(seen,wanted)
 def test_whirlwind_lookup_preserves_every_other_item_and_machine(self):
  old,new=self.cpu(self.old),self.cpu(self.new)
  for site,value in ((MOVE_ENTRY,18),(INDEX_ENTRY,103)):
   for item in range(537):
    for cpu in (old,new):cpu.reg_write(UC_ARM_REG_R0,item);cpu.reg_write(UC_ARM_REG_LR,0x023F0001);cpu.emu_start(site|1,0x023F0000,count=180)
    self.assertEqual(new.reg_read(UC_ARM_REG_R0),value if item==118 else old.reg_read(UC_ARM_REG_R0))
 def test_save_refresh_deletes_only_existing_objects_and_preserves_unrelated_noops(self):
  from route4_save_refresh import MARKER,GET_OBJECT,DELETE_OBJECT
  hook=int(self.report['route4_save_refresh']['noop_hook'],16);previous=int(self.report['route4_save_refresh']['previous_hook'],16)&~1
  for existing,alignment in ((ids,a) for ids in ((0,1,2,3),(1,3),()) for a in range(4)):
   cpu=self.cpu(self.new);ctx=0x023E0000;script=0x023E1000+alignment;field=0x023E2000;manager=0x023E4000
   cpu.mem_write(ctx+8,struct.pack('<I',script));cpu.mem_write(ctx+128,struct.pack('<I',field));cpu.mem_write(field+60,struct.pack('<I',manager));cpu.mem_write(script,struct.pack('<IH',MARKER,2))
   seen=[];deleted=[]
   def stub(u,address,size,data):
    if address==GET_OBJECT:
     self.assertEqual(u.reg_read(UC_ARM_REG_R0),manager);i=u.reg_read(UC_ARM_REG_R1);seen.append(i);u.reg_write(UC_ARM_REG_R0,0x023E5000+i*512 if i in existing else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    elif address==DELETE_OBJECT:
     pointer=u.reg_read(UC_ARM_REG_R0);self.assertNotEqual(pointer,0);deleted.append((pointer-0x023E5000)//512);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,stub);cpu.reg_write(UC_ARM_REG_R0,ctx);cpu.reg_write(UC_ARM_REG_SP,0x023D0000);cpu.reg_write(UC_ARM_REG_LR,0x023F0001);cpu.emu_start(hook|1,0x023F0000,count=400)
   self.assertEqual(seen,[0,1,2,3]);self.assertEqual(deleted,list(existing));self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),0);self.assertEqual(struct.unpack('<I',cpu.mem_read(ctx+8,4))[0],script+4);self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x023D0000)
  for tag in (0,2,MARKER^1,MARKER^65536):
   cpu=self.cpu(self.new);ctx=0x023E0000;script=0x023E1000;cpu.mem_write(ctx+8,struct.pack('<I',script));cpu.mem_write(script,struct.pack('<I',tag));seen=[]
   def delegated(u,address,size,data):
    if address==previous:seen.append(u.reg_read(UC_ARM_REG_R0));u.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,delegated);cpu.reg_write(UC_ARM_REG_R0,ctx);cpu.reg_write(UC_ARM_REG_SP,0x023D0000);cpu.reg_write(UC_ARM_REG_LR,0x023F0001);cpu.emu_start(hook|1,0x023F0000,count=100)
   self.assertEqual(seen,[ctx]);self.assertEqual(struct.unpack('<I',cpu.mem_read(ctx+8,4))[0],script)
 def test_refresh_is_once_only_on_frame_and_preserves_collected_item(self):
  from route4_save_refresh import MIGRATED,MARKER
  r=self.report['route4_save_refresh'];bank=split_bank(self.arc(self.new,'a/0/1/2')[r['script']]);script=bank[r['entry']-1]
  self.assertEqual(script[:4],struct.pack('<2H',32,MIGRATED));self.assertIn(struct.pack('<HI',1,MARKER),script);self.assertIn(struct.pack('<2H',100,1),script);self.assertIn(struct.pack('<2H',32,0xB39),script)
  self.assertEqual(self.arc(self.new,'a/0/1/2')[r['init']],struct.pack('<BI',1,1)+b'\0'+struct.pack('<4H',0x4142,0,r['entry'],0))
 def test_only_new_whirlwind_compatibility_bit_changes(self):
  a,b=self.arc(self.old,'a/0/0/2'),self.arc(self.new,'a/0/0/2');compatible=set(self.report['whirlwind']['compatible_species']['WHIRLWIND'])
  for species,(before,after) in enumerate(zip(a,b)):
   expected=bytearray(before)
   if species in compatible:expected[40]|=128
   self.assertEqual(bytes(expected),after,species)
  self.assertIn(16,compatible);self.assertNotIn(54,compatible);self.assertNotIn(133,compatible)


 def test_geodude_npc_and_interaction_tile_are_walkable(self):
  row=next(r for r in self.groups(self.new,11)[1] if struct.unpack_from('<H',r)[0]==20)
  self.assertEqual(struct.unpack_from('<2H',row,24),(1165,108))
  m=self.arc(self.new,'a/0/4/1')[0];w,h,heads,heights,n=m[:5];off=5+n+w*h*(2*heads+heights);lands=self.arc(self.new,'a/0/6/5')
  for x,z in ((1165,108),(1165,109)):
   land=struct.unpack_from('<H',m,off+2*(z//32*w+x//32))[0];permission=struct.unpack_from('<H',lands[land],20+2*(z%32*32+x%32))[0]
   self.assertFalse(permission&0x8000);self.assertNotIn(permission&255,(16,17))

if __name__=='__main__':unittest.main()
