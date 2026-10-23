"""Testing-only Fly shop access and the Route 4 return gap."""
import unittest,sys,json,struct,collections
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from testing_travel import *
from yellow_tms import ITEM_TABLE

class TravelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0019.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0020-travel-development.nds'));cls.report=json.loads((PROJECT/'build/0020-development-report.json').read_text())['testing_travel'];cls.cache={}
 def arc(self,r,p):
  key=(id(r),p)
  if key not in self.cache:self.cache[key]=ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
  return self.cache[key]
 def cpu(self):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x1ff8000,0x8000);u.mem_map(0x2000000,0x400000)
  for s in self.new.loadArm9().sections[:2]:u.mem_write(s.ramAddress,bytes(s.data))
  u.reg_write(UC_ARM_REG_SP,0x23d0000);u.reg_write(UC_ARM_REG_LR,0x23f0001);return u
 def test_only_authorized_main_code_stock_and_loader_change(self):
  a=bytearray(self.old.loadArm9().sections[0].data);b=self.new.loadArm9().sections[0].data
  settings=self.old.loadArm9().codeSettingsOffs
  for offset in (BADGE_CALL-0x2000000,STOCK_PTR,0xD2C68,settings,settings+4,settings+20):a[offset:offset+4]=b[offset:offset+4]
  self.assertEqual(a,b)
  old,new=self.old.loadArm9().sections[1],self.new.loadArm9().sections[1];self.assertEqual(bytes(old.data),bytes(new.data[:len(old.data)]));self.assertLess(len(new.data),0x8000)
 def test_only_celadon_TM_stock_adds_native_free_fly(self):
  d=self.new.loadArm9().sections[0].data;ptr=struct.unpack_from('<I',d,STOCK_PTR)[0];section=self.new.loadArm9().sections[1];items=struct.unpack_from('<14H',section.data,ptr-section.ramAddress)
  self.assertEqual(items,(HM_FLY,*self.report['fly']['original_stock'],65535));param=struct.unpack_from('<H',d,ITEM_TABLE+HM_FLY*8)[0];self.assertEqual(struct.unpack_from('<H',self.arc(self.new,'a/0/1/7')[param])[0],0)
 def test_free_fly_quantity_one_even_with_no_money_and_other_divisions_delegate(self):
  hook=int(self.report['fly']['quantity_hook'],16)
  for money in (0,1,4262,999999):
   cpu=self.cpu();cpu.mem_write(0x23e0284,struct.pack('<H',HM_FLY));cpu.reg_write(UC_ARM_REG_R5,0x23e0000);cpu.reg_write(UC_ARM_REG_R0,money);cpu.reg_write(UC_ARM_REG_R1,0);cpu.emu_start(hook|1,0x23f0000,count=80);self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),1)
  for item,price in ((328,1000),(HM_FLY,100),(328,0)):
   cpu=self.cpu();cpu.mem_write(0x23e0284,struct.pack('<H',item));cpu.reg_write(UC_ARM_REG_R5,0x23e0000);cpu.reg_write(UC_ARM_REG_R0,4262);cpu.reg_write(UC_ARM_REG_R1,price);seen=[]
   def callback(u,a,n,x):
    if a==DIVIDE:seen.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)));u.emu_stop()
   cpu.hook_add(UC_HOOK_CODE,callback);cpu.emu_start(hook|1,0x23f0000,count=80);self.assertEqual(seen,[(4262,price)])
 def test_fly_needs_no_badge_but_preserves_map_and_safety_checks(self):
  for mid,mode,follower,costume,safari,pal,expected in ((52,0,0,0,0,0,0),(372,0,0,0,0,0,1),(52,2,0,0,0,0,1),(52,3,0,0,0,0,1),(52,0,1,0,0,0,3),(52,0,0,1,0,0,5),(52,0,0,0,1,0,1),(52,0,0,0,0,1,1)):
   cpu=self.cpu();cpu.mem_write(0x23e0000,struct.pack('<2I',mid,0x23e1000));cpu.mem_write(0x23e1070,struct.pack('<I',mode));called=[];returns={0x2028e9c:0,0x20503d0:0,0x2066644:follower,0x20666b4:costume,0x2066860:safari,0x20668a0:pal}
   def callback(u,a,n,x):
    if a==0x2028f98:called.append(a)
    if a in returns:u.reg_write(UC_ARM_REG_R0,returns[a]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,callback);cpu.reg_write(UC_ARM_REG_R0,0x23e0000);cpu.emu_start(0x206800d,0x23f0000,count=1000);self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),expected,(mid,mode,follower,costume,safari,pal));self.assertFalse(called)
 def test_single_gap_changes_no_other_terrain_or_assets(self):
  a,b=self.arc(self.old,'a/0/6/5'),self.arc(self.new,'a/0/6/5');r=self.report['return_gap'];self.assertEqual(a,b[:len(a)]);raw=bytearray(a[r['land']]);x,z=GAP;struct.pack_into('<H',raw,20+2*(z%32*32+x%32),0);self.assertEqual(raw,b[r['new_land']]);ma,mb=self.arc(self.old,'a/0/4/1'),self.arc(self.new,'a/0/4/1');m=bytearray(ma[0]);w,h,hdr,alt,n=m[:5];off=5+n+w*h*(2*hdr+alt);struct.pack_into('<H',m,off+2*r['matrix_cell'],r['new_land']);self.assertEqual(m,mb[0]);self.assertEqual(ma[1:],mb[1:])
  for p in ('a/0/3/2','a/0/1/2','a/0/2/7','a/0/1/7','a/0/0/2','a/0/5/5','a/0/5/6','a/0/3/7','a/0/8/1'):self.assertEqual(self.arc(self.old,p),self.arc(self.new,p),p)
 def test_terrain_path_between_moon_exit_and_cerulean_without_any_ledge(self):
  m=self.arc(self.new,'a/0/4/1')[0];w,h,hdr,alt,n=m[:5];off=5+n+w*h*(2*hdr+alt);lands=self.arc(self.new,'a/0/6/5');start=(1195,113);seen={start};q=collections.deque(seen)
  while q:
   x,z=q.popleft()
   for nx,nz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
    if not 1180<=nx<=1285 or not 96<=nz<=135 or (nx,nz) in seen:continue
    li=struct.unpack_from('<H',m,off+2*(nz//32*w+nx//32))[0];p=struct.unpack_from('<H',lands[li],20+2*(nz%32*32+nx%32))[0]
    if p&0x8000 or p&255 in (16,17):continue
    seen.add((nx,nz));q.append((nx,nz))
  self.assertIn((1280,120),seen)

if __name__=='__main__':unittest.main()
