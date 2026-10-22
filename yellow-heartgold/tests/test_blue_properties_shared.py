"""Compare the actual old/shared Thumb wrappers with identical native API/RNG stubs."""
import sys,struct,unittest,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from blue_properties_shared import patch,helper,OLD,LATEST
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'build/0031-departure-v3/private-departure.nds'

@unittest.skipUnless(SOURCE.exists(),'Requires private candidate')
class SharedBlueProperties(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=ndspy.rom.NintendoDSRom.fromFile(str(SOURCE));cls.changed=ndspy.rom.NintendoDSRom(cls.original.save());cls.report=patch(cls.changed);cls.before=cls.original.loadArm9();cls.after=cls.changed.loadArm9()
 def execute(self,code,tid,species=54,gender=0,rare=0,initialized=True):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x120000);cpu.mem_map(0x02300000,0x20000)
  cpu.mem_write(0x01FF8000,bytes(code.sections[1].data));cpu.mem_write(0x02000000,bytes(code.sections[0].data))
  ctx,save,state,party,mon=0x02300000,0x02301000,0x02304000,0x02308000,0x02309000
  cpu.mem_write(ctx+24,struct.pack('<I',tid));cpu.mem_write(ctx+4,struct.pack('<I',party));cpu.mem_write(ctx+0x1C0,struct.pack('<I',save));cpu.mem_write(party+4,struct.pack('<I',4))
  memory=bytearray([0xA5]*0x500);struct.pack_into('<I',memory,0x440,0x12AB34CD);memory[0x447]=0x83|(16|rare if initialized else 0);cpu.mem_write(state,bytes(memory))
  vals={0:0x12345678,5:species,7:0x13572468,10:33 if species==54 else 107,111:gender,**{70+i:v for i,v in enumerate([3,6,9,12,15,18])}}
  rng=0x76543210;native_calls=0;stats=0;done=False
  def hook(uc,address,size,_):
   nonlocal rng,native_calls,stats,done
   if address==0x020FF000:done=True;uc.emu_stop();return
   a,b,c=[uc.reg_read(v) for v in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];result=None
   if address==0x02073604:native_calls+=1;result=0
   elif address==0x02074644:
    assert a==party and b==3;result=mon
   elif address==0x020503D0:assert a==save;result=state
   elif address in (0x0201FD44,0x01FFCA64):
    rng=(rng*0x41C64E6D+0x6073)&0xFFFFFFFF;result=rng>>16
   elif address==0x0201FD2C:result=rng
   elif address==0x0201FD38:rng=a
   elif address==0x0206E540:assert a==mon;result=vals[b]
   elif address==0x0206EC40:assert a==mon;vals[b]=int.from_bytes(uc.mem_read(c,4),'little')
   elif address==0x0207235C:assert a==mon;vals[0]=b
   elif address==0x020722DC:assert a==mon # Existing hidden ability retained by native API stub.
   elif address==0x0206E250:assert a==mon;stats+=1
   else:return
   if result is not None:uc.reg_write(UC_ARM_REG_R0,result)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_SP,0x0231F000);cpu.reg_write(UC_ARM_REG_LR,0x020FF001);cpu.reg_write(UC_ARM_REG_R0,ctx);cpu.reg_write(UC_ARM_REG_R1,0);cpu.reg_write(UC_ARM_REG_R2,11)
  for reg in (UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7):cpu.reg_write(reg,0x44332211+reg)
  cpu.emu_start(LATEST|1,0x020FF000,count=100000)
  self.assertTrue(done or cpu.reg_read(UC_ARM_REG_PC)==0x020FF000,hex(cpu.reg_read(UC_ARM_REG_PC)));self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x0231F000);self.assertEqual(native_calls,1)
  for reg in (UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7):self.assertEqual(cpu.reg_read(reg),0x44332211+reg)
  return vals,bytes(cpu.mem_read(state,0x500)),rng,stats
 def test_all_existing_eligible_trainers_preserve_results(self):
  for tid in list(range(741,751))+list(range(782,786)):
   for species,gender in ((54,0),(54,1),(133,0),(133,1)):
    with self.subTest(tid=tid,species=species,gender=gender):self.assertEqual(self.execute(self.before,tid,species,gender),self.execute(self.after,tid,species,gender))
 def test_independent_shiny_perfect_flags_and_initial_seed(self):
  for tid,species,gender,rare in itertools.product((741,782),(54,133),(0,1),(0,32,64,96)):
   self.assertEqual(self.execute(self.before,tid,species,gender,rare),self.execute(self.after,tid,species,gender,rare))
  for tid in (741,745,750,782,785):self.assertEqual(self.execute(self.before,tid,initialized=False),self.execute(self.after,tid,initialized=False))
 def test_new_ship_records_share_the_same_starter(self):
  for i,(species,gender) in enumerate(((54,0),(54,1),(133,0),(133,1))):
   for rare in (0,32,64,96):self.assertEqual(self.execute(self.before,782+i,species,gender,rare),self.execute(self.after,809+i,species,gender,rare))
 def test_unrelated_native_trainers_unchanged(self):
  for tid in (0,1,23,242,495,599,740,751,781,786,808,813,900):self.assertEqual(self.execute(self.before,tid),self.execute(self.after,tid))
 def test_helper_all_trainer_ids_and_boundaries(self):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_write(OLD,helper(809))
  for tid in range(1000):
   cpu.reg_write(UC_ARM_REG_R3,tid);cpu.reg_write(UC_ARM_REG_R2,0x1234ABCD);cpu.reg_write(UC_ARM_REG_LR,0x01FF8001);cpu.emu_start(OLD|1,0x01FF8000,count=100)
   self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),int(741<=tid<=750 or 782<=tid<=785 or 809<=tid<=812));self.assertEqual(cpu.reg_read(UC_ARM_REG_R2),0x1234ABCD)
 def test_no_additional_itcm_or_unrelated_resource_changes(self):
  self.assertEqual(len(self.before.sections[1].data),len(self.after.sections[1].data));self.assertEqual(self.original.files,self.changed.files);self.assertEqual(self.original.arm7,self.changed.arm7);self.assertEqual(self.original.arm9OverlayTable,self.changed.arm9OverlayTable)
if __name__=='__main__':unittest.main()
