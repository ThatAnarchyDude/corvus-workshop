"""Old Rod retry/ownership behavior and native-resource scope."""
import sys,json,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from vermilion_old_rod import guru,OLD_ROD,ROD_GIVEN,MAP
from test_prototype0021 import run
from viridian_tutorial import TABLE
from build_rom import PROJECT
class OldRodGift(unittest.TestCase):
 def test_award_and_repeat_preserve_other_flags(self):
  for flags in (set(),{0x75},{0xA9E,0x89}):
   r=run(guru(2),flags=flags);self.assertEqual(r['bag'],{OLD_ROD:1});self.assertEqual(r['flags'],flags|{ROD_GIVEN})
   repeat=run(guru(2),flags=r['flags'],bag=r['bag']);self.assertEqual(repeat['bag'],r['bag']);self.assertEqual(repeat['flags'],r['flags'])
 def test_already_owned_decline_and_full_bag(self):
  r=run(guru(2),bag={OLD_ROD:1});self.assertEqual(r['bag'],{OLD_ROD:1});self.assertEqual(r['flags'],set())
  for options in ({'yes':False},{'room':False}):
   r=run(guru(2),**options);self.assertEqual(r['bag'],{});self.assertNotIn(ROD_GIVEN,r['flags'])
   retry=run(guru(2),flags=r['flags'],bag=r['bag']);self.assertEqual(retry['bag'],{OLD_ROD:1})
 def test_room_and_all_other_maps_archives_preserved(self):
  a=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0030-fan-club-voucher-v2/private-fan-club.nds'));b=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0030-old-rod-v1/private-old-rod.nds'))
  allowed={a.filenames.idOf(p) for p in ('a/0/1/2','a/0/2/7')}
  for i,(x,y) in enumerate(zip(a.files,b.files)):
   if i not in allowed:self.assertEqual(x,y,i)
  da=a.loadArm9().sections[0].data;db=b.loadArm9().sections[0].data
  for mid in range(540):
   x=da[TABLE+mid*24:TABLE+(mid+1)*24];y=db[TABLE+mid*24:TABLE+(mid+1)*24]
   if mid==MAP:self.assertEqual(x[:6]+x[8:10]+x[12:],y[:6]+y[8:10]+y[12:])
   else:self.assertEqual(x,y,mid)
  for p in ('a/0/1/2','a/0/2/7'):
   x=ndspy.narc.NARC(a.files[a.filenames.idOf(p)]);y=ndspy.narc.NARC(b.files[b.filenames.idOf(p)]);self.assertEqual(x.files,y.files[:len(x.files)])
  arc=ndspy.narc.NARC(b.files[b.filenames.idOf('a/0/1/2')]);self.assertEqual(arc.files[781][4:],arc.files[1138][4:len(arc.files[781])]);self.assertGreaterEqual(struct.unpack_from('<I',arc.files[1138])[0]+4,len(arc.files[781]))
if __name__=='__main__':unittest.main()