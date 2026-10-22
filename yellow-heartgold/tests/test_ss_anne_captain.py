import sys,struct,unittest
sys.path.insert(0,'yellow-heartgold/tools')
from ss_anne_captain import captain,GIVEN,HM_CUT
class CaptainReward(unittest.TestCase):
 def run_script(self,flags,capacity):
  code=captain();at=0;comparison=False;values={};gifts=[];messages=[];self.trace=[]
  def words(n):
   nonlocal at
   v=struct.unpack_from('<'+'H'*n,code,at);at+=n*2;return v
  for _ in range(150):
   op=words(1)[0]
   if op==73:words(1)
   elif op==78:self.trace.append((op,words(1)[0]))
   elif op in (96,97,104,50,53,79):self.trace.append((op,))
   elif op in (190,191):at+=1
   elif op==45:messages.append(code[at]);self.trace.append((op,code[at]));at+=1
   elif op==32:comparison=words(1)[0] in flags
   elif op==17:
    var,value=words(2);comparison=values.get(var,0)==value
   elif op in (22,28):
    take=True
    if op==28:
     self.assertEqual(code[at],1);at+=1;take=comparison
    delta=struct.unpack_from('<i',code,at)[0];at+=4
    if take:at+=delta
   elif op==125:
    item,count,out=words(3);self.assertEqual((item,count),(HM_CUT,1));values[out]=int(capacity)
    if capacity:gifts.append(item)
   elif op==30:flags.add(words(1)[0])
   elif op==2:return gifts,messages
   else:self.fail('Unexpected command '+str(op))
  self.fail('Script did not end')
 def test_one_time_reward_preserves_other_flags(self):
  flags={0xA87,0xA9E};self.assertEqual(self.run_script(flags,True),([420],[0,1,2]));self.assertEqual(flags,{0xA87,0xA9E,GIVEN});self.assertEqual(self.run_script(flags,True),([],[3]))
 def test_full_bag_does_not_consume_reward_and_allows_retry(self):
  flags={0xA9F};self.assertEqual(self.run_script(flags,False),([],[0,1,4]));self.assertEqual(flags,{0xA9F});self.assertEqual(self.run_script(flags,True),([420],[0,1,2]));self.assertIn(GIVEN,flags)
 def test_recovery_wait_and_facing_precede_thanks_without_healing_party(self):
  self.run_script(set(),True)
  first=self.trace.index((45,0))
  self.assertEqual(self.trace[first:first+7],[(45,0),(50,),(53,),(78,1183),(79,),(104,),(45,1)])
  self.run_script({GIVEN},True)
  self.assertNotIn((78,1183),self.trace)
if __name__=='__main__':unittest.main()
