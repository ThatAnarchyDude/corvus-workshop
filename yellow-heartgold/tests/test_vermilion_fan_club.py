"""Voucher reaches Cerulean exchange exactly once; native room boundaries preserved."""
import sys,json,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from vermilion_fan_club import chairman,VOUCHER_GIVEN,MAP
from cerulean_bike import clerk,VOUCHER,BICYCLE,RECEIVED
from test_prototype0021 import run
from opening import events_decode
from parcel_quest import split_bank
from prototype import decode_messages
from viridian_tutorial import TABLE
from build_rom import PROJECT
class FanClubVoucher(unittest.TestCase):
 def test_voucher_exchange_and_repeat_do_not_duplicate_reward(self):
  r=run(chairman(19));self.assertEqual(r['bag'],{VOUCHER:1});self.assertEqual(r['flags'],{VOUCHER_GIVEN})
  exchange=run(clerk(),bag=r['bag'],flags=r['flags']);self.assertEqual(exchange['bag'],{VOUCHER:0,BICYCLE:1});self.assertIn(RECEIVED,exchange['flags'])
  repeat=run(chairman(19),bag=exchange['bag'],flags=exchange['flags']);self.assertEqual(repeat['bag'],exchange['bag']);self.assertEqual(repeat['flags'],exchange['flags'])
 def test_decline_and_full_bag_allow_later_success(self):
  for options in ({'yes':False},{'room':False}):
   r=run(chairman(19),**options);self.assertEqual(r['bag'],{});self.assertNotIn(VOUCHER_GIVEN,r['flags'])
   retry=run(chairman(19),bag=r['bag'],flags=r['flags']);self.assertEqual(retry['bag'],{VOUCHER:1})
 def test_native_room_and_other_resources_preserved(self):
  a=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0029-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0029.nds'));b=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0030-fan-club-voucher-v2/private-fan-club.nds'))
  changed={a.filenames.idOf(p) for p in ('a/0/1/2','a/0/2/7')}
  for i,(x,y) in enumerate(zip(a.files,b.files)):
   if i not in changed:self.assertEqual(x,y,i)
  da=a.loadArm9().sections[0].data;db=b.loadArm9().sections[0].data
  for mid in range(540):
   ha=da[TABLE+mid*24:TABLE+(mid+1)*24];hb=db[TABLE+mid*24:TABLE+(mid+1)*24]
   if mid!=MAP:self.assertEqual(ha,hb,mid)
   else:self.assertEqual(ha[:6]+ha[8:10]+ha[12:],hb[:6]+hb[8:10]+hb[12:])
  for p in ('a/0/1/2','a/0/2/7'):
   old=ndspy.narc.NARC(a.files[a.filenames.idOf(p)]);new=ndspy.narc.NARC(b.files[b.filenames.idOf(p)]);self.assertEqual(old.files,new.files[:len(old.files)])
  s=ndspy.narc.NARC(b.files[b.filenames.idOf('a/0/1/2')]);self.assertEqual(s.files[782][4:],s.files[1137][4:len(s.files[782])]);self.assertGreaterEqual(struct.unpack_from('<I',s.files[1137])[0]+4,len(s.files[782]))
  t=ndspy.narc.NARC(b.files[b.filenames.idOf('a/0/2/7')]);self.assertEqual(decode_messages(t.files[488])[1],decode_messages(t.files[911])[1][:19])
if __name__=='__main__':unittest.main()