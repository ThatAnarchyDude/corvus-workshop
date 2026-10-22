"""Published predecessors and Johto assets remain intact in the cumulative build."""
import unittest,sys,os,struct,json
from pathlib import Path
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from viridian_tutorial import TABLE
from cerulean_tm import MOVE_ENTRY,INDEX_ENTRY
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
class Assets(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0020.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0021_ROM','build/0021-development-6.nds')));cls.main=cls.new.loadArm9();cls.report=json.loads((PROJECT/'build/0021-development-report.json').read_text())
 def files(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
 def test_original_maps_scripts_trainers_and_terrain_are_archived(self):
  for path in ['a/0/1/2','a/0/3/2','a/0/4/1','a/0/6/5','a/0/5/5','a/0/5/6']:
   old,new=self.files(self.old,path),self.files(self.new,path);self.assertEqual(old,new[:len(old)],path)
  a,b=self.old.loadArm9().sections[0].data,self.main.sections[0].data
  # All 540 native headers, except the eight authorized Kanto maps, are exact.
  for mid in range(540):
   if mid in [51,52,426,427,428,429,430,431,432]:continue
   self.assertEqual(a[TABLE+mid*24:TABLE+(mid+1)*24],b[TABLE+mid*24:TABLE+(mid+1)*24],mid)
 def test_yellow_trainer_teams_are_serialized_correctly(self):
  rows=self.files(self.new,'a/0/5/6');trainers=self.files(self.new,'a/0/5/5')
  for record in self.report['cerulean']['trainers']:
   tid=record['id'];self.assertEqual(trainers[tid][3],len(record['team']))
   for i,(species,level,moves,gender) in enumerate(record['team']):
    raw=struct.unpack_from('<BB3H4H',rows[tid],i*16)
    self.assertEqual((raw[1],raw[2],raw[3],list(raw[5:])),(gender,level,species,moves))
 def test_custom_tm_lookups_chain_existing_moves(self):
  for entry,expect in [(MOVE_ENTRY,{115:117,116:55,117:5,118:18,119:61}),(INDEX_ENTRY,{115:100,116:101,117:102,118:103,119:104})]:
   for item,result in expect.items():
    c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
    for sec in self.main.sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
    c.reg_write(UC_ARM_REG_R0,item);c.reg_write(UC_ARM_REG_SP,0x023E0000);c.reg_write(UC_ARM_REG_LR,0x023F0001);c.emu_start(entry|1,0x023F0000,count=500);self.assertEqual(c.reg_read(UC_ARM_REG_R0),result)
if __name__=='__main__':unittest.main()
