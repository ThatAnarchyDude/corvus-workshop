import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from viridian_tutorial import TABLE
from vermilion_gym import TEAMS,SURGE_MOVES
class GymTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0031-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0031.nds'))
  cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0032-vermilion-gym-v1/private-vermilion-gym.nds'))
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
 def test_yellow_teams_and_surges_four_moves(self):
  for t,team in TEAMS.items():
   header=self.arc(self.new,'a/0/5/5')[t]; self.assertEqual(header[3],len(team));self.assertEqual(header[4:12],bytes(8))
   fmt='<BB3H4H' if t==255 else '<BB3H'
   rows=list(struct.iter_unpack(fmt,self.arc(self.new,'a/0/5/6')[t]))
   self.assertEqual([(r[3],r[2]) for r in rows],team)
   if t==255:self.assertEqual(rows[0][5:],SURGE_MOVES)
 def test_native_puzzle_badge_loss_retry_preserved(self):
  d=self.new.loadArm9().sections[0].data;sid=struct.unpack_from('<H',d,TABLE+365*24+6)[0]
  before=self.arc(self.old,'a/0/1/2')[778];after=self.arc(self.new,'a/0/1/2')[sid]
  self.assertEqual(len(before),len(after));self.assertEqual([i for i,(a,b) in enumerate(zip(before,after)) if a!=b],[909])
  self.assertEqual(struct.unpack_from('<H',after,909)[0],351)
 def test_unrelated_files_maps_executables_preserved(self):
  allowed={self.old.filenames.idOf(p) for p in ('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6')}
  self.assertEqual(len(self.old.files),len(self.new.files))
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in allowed:self.assertEqual(a,b,f'file {i}')
  for field in ('arm7','arm9OverlayTable','arm7OverlayTable','iconBanner'):self.assertEqual(getattr(self.old,field),getattr(self.new,field))
  old=self.old.loadArm9();new=self.new.loadArm9()
  for i,(a,b) in enumerate(zip(old.sections,new.sections)):
   if i: self.assertEqual(a.data,b.data)
   else:
    expected=bytearray(a.data);at=TABLE+365*24
    # ndspy updates only the documented compressedStaticEnd metadata on repack.
    self.assertEqual(old.codeSettingsOffs,new.codeSettingsOffs)
    meta=old.codeSettingsOffs+20;expected[meta:meta+4]=b.data[meta:meta+4]
    expected[at+6:at+8]=b.data[at+6:at+8];expected[at+10:at+12]=b.data[at+10:at+12]
    self.assertEqual(expected,b.data)
 def test_archived_scripts_texts_other_trainers_preserved(self):
  for path in ('a/0/1/2','a/0/2/7'):
   old=self.arc(self.old,path);new=self.arc(self.new,path);self.assertEqual(new[:len(old)],old);self.assertEqual(len(new),len(old)+1)
  for path in ('a/0/5/5','a/0/5/6'):
   old=self.arc(self.old,path);new=self.arc(self.new,path);self.assertEqual(len(old),len(new))
   self.assertEqual({i for i,(a,b) in enumerate(zip(old,new)) if a!=b},set(TEAMS))
if __name__=='__main__':unittest.main()

