"""Execute the actual save functions against a bounded native-sized block."""
import sys,struct,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT,BASE
from save_compatibility import patch,assert_persistent,RELOCATIONS
from opening import events_decode

class Saves(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0021.nds'))
  cls.fixed=ndspy.rom.NintendoDSRom(cls.original.save());cls.report=patch(cls.fixed)
 def cpu(self,fixed=True):
  c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
  for s in (self.fixed if fixed else self.original).loadArm9().sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
  c.reg_write(UC_ARM_REG_SP,0x023F8000);c.reg_write(UC_ARM_REG_LR,0x023FF001)
  return c
 def test_reject_out_of_range_allocations(self):
  for f in RELOCATIONS:
   with self.assertRaises(ValueError):assert_persistent(f)
   assert_persistent(RELOCATIONS[f])
 def test_native_flag_write_never_touches_save_trailer(self):
  for f in [1,0xA80,0xB5F,0xB60,0xB69,0x3FFF]:
   c=self.cpu();c.mem_write(0x02300000,bytes(1100)+b'CHECKSUM')
   c.reg_write(UC_ARM_REG_R0,0x02300000);c.reg_write(UC_ARM_REG_R1,f)
   c.emu_start(0x02050409,0x023FF000,count=1000)
   self.assertEqual(bytes(c.mem_read(0x0230044C,8)),b'CHECKSUM')
   if f<0xB60:self.assertEqual(c.mem_read(0x023002E0+f//8,1)[0],1<<(f%8))
 def test_original_0021_write_reproduces_trailer_corruption(self):
  c=self.cpu(False);c.mem_write(0x02300000,bytes(1100)+bytes(8))
  def ignore_assert(c,a,size,_):
   if a==0x0202551C:c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
  c.hook_add(UC_HOOK_CODE,ignore_assert);c.reg_write(UC_ARM_REG_R0,0x02300000);c.reg_write(UC_ARM_REG_R1,0xB69)
  c.emu_start(0x02050409,0x023FF000,count=1000)
  self.assertEqual(c.mem_read(0x0230044D,1)[0],2)
 def test_daily_reset_preserves_quest_reward_and_seed_flags(self):
  c=self.cpu();flags=0x02300000;c.mem_write(flags+0x2E0+0xAA0//8,bytes([255])*24)
  def save(c,a,size,_):
   if a==0x020503D0:c.reg_write(UC_ARM_REG_R0,flags);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
  c.hook_add(UC_HOOK_CODE,save);c.reg_write(UC_ARM_REG_R0,0x02310000)
  c.emu_start(0x02040471,0x023FF000,count=1000)
  self.assertEqual(bytes(c.mem_read(flags+0x2E0+0xAA0//8,24)),bytes(12)+bytes([255])*12)
 def test_recovery_preserves_new_game_and_restores_completed_rewards(self):
  for badge,gear,parcel,done in [(0,0,0,False),(0,1,0,True),(1,0,0,True),(0,0,2,True)]:
   c=self.cpu();blocks={1:0x02310000,3:0x02320000,4:0x02330000,6:0x02340000}
   c.mem_write(blocks[1]+35,bytes([badge]));c.mem_write(blocks[4]+0x313,bytes([gear<<4]))
   c.mem_write(blocks[4]+0x2D4,struct.pack('<H',parcel))
   c.mem_write(blocks[3],struct.pack('<6H',115,2,119,1,450,1));c.mem_write(blocks[6],bytes([0xA5])*0x336)
   def array(c,a,size,_):
    if a==0x020272C8:
     c.reg_write(UC_ARM_REG_R0,blocks[c.reg_read(UC_ARM_REG_R1)]);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
   c.hook_add(UC_HOOK_CODE,array);c.reg_write(UC_ARM_REG_R0,0x02300000)
   c.emu_start(0x020503D1,0x023FF000,count=10000)
   b=bytes(c.mem_read(blocks[4],1100));flag=lambda n:bool(b[0x2E0+n//8]&(1<<(n%8)))
   self.assertEqual(flag(0xB52),done);self.assertEqual(struct.unpack_from('<H',b,0x2D4)[0],2 if done else 0)
   self.assertTrue(flag(0xB22));self.assertTrue(flag(0xA80));self.assertTrue(flag(0xA89))
   self.assertEqual(bytes(c.mem_read(blocks[6],0x336)),bytes([0xA5])*0x336)
   self.assertEqual(bytes(c.mem_read(blocks[6]+0x336,2)),bytes([1,1]) if done else bytes(2))
   self.assertEqual(bytes(c.mem_read(blocks[3],12)),struct.pack('<6H',115,2,119,1,450,1))
 def test_relocations_do_not_occupy_native_flags(self):
  base=ndspy.rom.NintendoDSRom.fromFile(str(BASE));scripts=ndspy.narc.NARC(base.files[base.filenames.idOf('a/0/1/2')]).files
  for f in [*RELOCATIONS.values(),0xA8B,0xA8C]:
   for op in (30,31,32):self.assertFalse(any(struct.pack('<HH',op,f) in s for s in scripts),(f,op))
  events=ndspy.narc.NARC(base.files[base.filenames.idOf('a/0/3/2')]).files
  for raw in events:
   for row in events_decode(raw)[1]:self.assertNotIn(struct.unpack_from('<H',row,8)[0],[*RELOCATIONS.values(),0xA8B,0xA8C])
 def test_continue_filters_stale_custom_actors_and_keeps_player_and_johto(self):
  c=self.cpu();manager,field,flags,objects=0x02300000,0x02301000,0x02302000,0x02303000
  c.mem_write(manager+0x128,struct.pack('<I',field));c.mem_write(field+12,struct.pack('<I',0x02304000))
  cases=[(0xB55,True,False),(0xB46,True,False),(0xB4C,True,False),(0xB4D,False,True),(0,False,True),(0x2F4,True,True),(0xB62,True,False)]
  for i,(f,hidden,active) in enumerate(cases):
   row=bytearray(80);struct.pack_into('<I',row,0,0x101);struct.pack_into('<H',row,22,f);c.mem_write(objects+i*80,bytes(row))
   effective=RELOCATIONS.get(f,f)
   if hidden:c.mem_write(flags+0x2E0+effective//8,bytes([1<<(effective%8)]))
  captured=[];native=int(self.report['actor_restore_trampoline'],16)
  def hook(c,a,size,_):
   if a==0x020503D0:c.reg_write(UC_ARM_REG_R0,flags);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
   elif a==native:
    captured.append(tuple(c.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)));c.emu_stop()
  c.hook_add(UC_HOOK_CODE,hook);c.reg_write(UC_ARM_REG_R0,manager);c.reg_write(UC_ARM_REG_R1,objects);c.reg_write(UC_ARM_REG_R2,len(cases))
  c.emu_start(0x0205E649,0x023FF000,count=2000)
  self.assertEqual(captured,[(manager,objects,len(cases))])
  for i,(f,hidden,active) in enumerate(cases):
   row=bytes(c.mem_read(objects+i*80,80));self.assertEqual(bool(struct.unpack_from('<I',row)[0]&1),active)
   self.assertEqual(struct.unpack_from('<H',row,22)[0],RELOCATIONS.get(f,f));self.assertEqual(struct.unpack_from('<I',row)[0]&0x100,0x100)

if __name__=='__main__':unittest.main()
