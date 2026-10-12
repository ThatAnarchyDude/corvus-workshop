"""Guard/ambush ordering, passable paths, and corrected fossil rendering."""
import os,struct,sys,json,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon_corrections import guard,guard_paths,rocket_ambush,blocked_exit,REFRESHED
from mtmoon_story import STAGE
from mtmoon_rockets import JESSIE,JAMES,HIDE_JESSIE,HIDE_JAMES
from test_mtmoon_story import run_script
from viridian_tutorial import TABLE
from opening import events_decode
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP
from item_collision import SITE,NATIVE
class Corrections(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0023_ROM','build/yellow-heartgold-prototype-0023.nds')))
  cls.report=json.loads((PROJECT/'build/0023-development-report.json').read_text())['mtmoon_corrections']
 def test_every_guard_approach_battles_then_requires_fossil_and_returns(self):
  for x,z in guard_paths():
   r=run_script(guard(776,0),stage=0,x=x,z=z)
   self.assertEqual(r[0][STAGE],1);self.assertIn(776,r[5]);self.assertEqual(r[4],[0,1,2]);self.assertEqual(len(r[3]),3)
   lost=run_script(guard(776,0),stage=0,x=x,z=z,win=False);self.assertEqual(lost[0][STAGE],0);self.assertNotIn(776,lost[5])
  for stage in (1,2,3):self.assertEqual(run_script(guard(776,0),stage=stage)[0][STAGE],stage)
 def test_exit_cannot_request_fossil_before_guard_battle(self):
  for z in (22,23):
   for x in range(20,25):
    r=run_script(blocked_exit(776,0,4),stage=0,x=x,z=z)
    self.assertEqual(r[0][STAGE],1);self.assertIn(776,r[5]);self.assertEqual(r[4],[0,1,2])
    waiting=run_script(blocked_exit(776,0,4),stage=1,x=x,z=z)
    self.assertEqual(waiting[4],[4]);self.assertEqual(waiting[5],set())
 def test_ambush_both_exit_approach_rows_and_fossil_prerequisite(self):
  for z in (21,22,23):
   for x in range(20,25):
    r=run_script(rocket_ambush(777,0),stage=2,x=x,z=z)
    self.assertEqual(r[0][STAGE],3);self.assertEqual(r[2],[JAMES,JESSIE]);self.assertEqual(r[5],{777,HIDE_JESSIE,HIDE_JAMES})
    lost=run_script(rocket_ambush(777,0),stage=2,x=x,z=z,win=False);self.assertEqual(lost[0][STAGE],2);self.assertEqual(lost[5],set())
  for stage in (0,1,3):self.assertEqual(run_script(rocket_ambush(777,0),stage=stage)[3],[])
 def test_every_guard_and_rocket_walk_is_passable_and_avoids_fossils_and_items(self):
  a=lambda p:ndspy.narc.NARC(self.rom.files[self.rom.filenames.idOf(p)]).files
  d=self.rom.loadArm9().sections[0].data;matrix=a('a/0/4/1')[struct.unpack_from('<H',d,TABLE+107*24+4)[0]];land=a('a/0/6/5')[struct.unpack_from('<H',matrix,5+matrix[4])[0]]
  g=events_decode(a('a/0/3/2')[self.report['event']]);fixed={struct.unpack_from('<2H',row,24) for row in g[1] if struct.unpack_from('<H',row)[0] not in (21,JESSIE,JAMES)}
  step={12:(0,-1),13:(0,1),14:(-1,0),15:(1,0)}
  def walk(pos,moves,blocked):
   for op,count in moves:
    if op not in step:continue
    dx,dz=step[op]
    for _ in range(count):
     pos=(pos[0]+dx,pos[1]+dz);x,z=pos
     self.assertFalse(struct.unpack_from('<H',land,20+2*(z*32+x))[0]&0x8000,pos);self.assertNotIn(pos,blocked)
   return pos
  for player,(moves,face,pface) in guard_paths().items():walk((16,20),moves,fixed|{player})
  j=walk((18,23),[(12,1),(15,3)],fixed|{(22,22),(19,23)})
  k=walk((19,23),[(12,2),(15,4),(13,1)],fixed|{(22,22),j})
  self.assertEqual(j,(21,22));self.assertEqual(k,(23,22))
  walk(k,[(13,1),(14,1)],fixed|{(22,22),j});walk(j,[(13,1),(15,1)],fixed|{(22,22)})
 def test_fossils_have_item_render_flags_and_only_new_solid_sprites_change(self):
  report=self.report['rendering'];self.assertEqual(report['item_flags'],0x420)
  for sprite in (87,93,94,317,338):
   c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
   for sec in self.rom.loadArm9().sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
   c.mem_write(0x02300010,struct.pack('<I',sprite));c.reg_write(UC_ARM_REG_R0,0x02300000);c.reg_write(UC_ARM_REG_SP,0x023F0000);c.reg_write(UC_ARM_REG_LR,0x023FF001)
   def hook(c,address,size,_):
    if address==NATIVE:c.reg_write(UC_ARM_REG_R0,1);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
   c.hook_add(UC_HOOK_CODE,hook);c.emu_start(int(report['collision_hook'],16)|1,0x023FF000,count=300)
   self.assertEqual(c.reg_read(UC_ARM_REG_R0),0 if sprite in (87,93,94) else 1)
  self.assertLess(REFRESHED,0xAA0)
 def test_all_passable_exit_neighbors_have_the_fossil_ambush(self):
  a=lambda p:ndspy.narc.NARC(self.rom.files[self.rom.filenames.idOf(p)]).files
  g=events_decode(a('a/0/3/2')[self.report['event']])
  self.assertIn((22,23),[struct.unpack_from('<2H',w) for w in g[2]])
  triggers=[struct.unpack('<8H',row) for row in g[3]]
  for x,z in ((22,22),(21,23),(23,23)):
   self.assertTrue(any(entry==13 and value==2 and left<=x<left+width and top<=z<top+height for entry,left,top,width,height,unused,value,state in triggers),(x,z))
if __name__=='__main__':unittest.main()
