"""Owner-approved party-only Jenny reward safety."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from vermilion_jenny import jenny,GIVEN,THUNDER,SPECIES,LEVEL
from test_prototype0021 import run
class JennyReward(unittest.TestCase):
 def test_only_thunder_badge_can_open_offer(self):
  self.assertEqual(THUNDER,10);self.assertIn(struct.pack('<3H',294,10,0x800C),jenny(9))
  r=run(jenny(9),badge=False);self.assertNotIn('pokemon7',r['bag']);self.assertNotIn(GIVEN,r['flags']);self.assertEqual(r['messages'],[9])
 def test_awards_squirtle10_once_and_preserves_other_flags(self):
  self.assertEqual((SPECIES,LEVEL),(7,10));self.assertIn(struct.pack('<7H',137,7,10,0,0,0,0x800C),jenny(9))
  for count in range(1,6):
   r=run(jenny(9),badge=True,count=count,flags={0x75,0xA9F});self.assertEqual(r['bag'],{'pokemon7':1});self.assertEqual(r['flags'],{0x75,0xA9F,GIVEN})
   again=run(jenny(9),badge=True,count=count+1,flags=r['flags'],bag=r['bag']);self.assertEqual(again['bag'],r['bag']);self.assertEqual(again['flags'],r['flags']);self.assertEqual(again['messages'],[13])
 def test_decline_and_full_party_never_consume_reward(self):
  for options in ({'yes':False},{'count':6}):
   r=run(jenny(9),badge=True,**options);self.assertNotIn('pokemon7',r['bag']);self.assertNotIn(GIVEN,r['flags'])
   retry=run(jenny(9),badge=True,flags=r['flags'],bag=r['bag'],count=5);self.assertEqual(retry['bag'],{'pokemon7':1});self.assertIn(GIVEN,retry['flags'])
 def test_full_party_skips_offer_and_keeps_reward_available(self):
  r=run(jenny(9),badge=True,count=6);self.assertEqual(r['messages'],[15]);self.assertEqual(r['bag'],{});self.assertNotIn(GIVEN,r['flags'])
if __name__=='__main__':unittest.main()