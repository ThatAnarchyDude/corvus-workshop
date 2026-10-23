import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ss_anne_boarding import ticket_gate,TICKET

def run(direction,ticket):
 data=ticket_gate();pc=0;variables={};messages=[];movements=[];has_checks=[];locked=False
 def read():
  nonlocal pc
  value=struct.unpack_from('<H',data,pc)[0];pc+=2;return value
 def value(v):return variables.get(v,0) if v>=0x4000 else v
 for _ in range(120):
  op=read()
  if op==2:return dict(messages=messages,movements=movements,checks=has_checks,locked=locked,ticket=ticket,variables=variables)
  if op==386:variables[read()]=direction
  elif op==17:
   left,right=read(),read();comparison=(value(left)>value(right))-(value(left)<value(right))
  elif op==28:
   cond=data[pc];pc+=1;off=struct.unpack_from('<i',data,pc)[0];pc+=4
   assert cond in (1,5)
   if (comparison==0)==(cond==1):pc+=off
  elif op==22:
   off=struct.unpack_from('<i',data,pc)[0];pc+=4;pc+=off
  elif op==96:locked=True
  elif op==97:locked=False
  elif op in (190,191):pc+=1
  elif op==45:messages.append(data[pc]);pc+=1
  elif op in (50,53,95):pass
  elif op==128:
   item,count,target=read(),read(),read();assert item==TICKET and count==1;has_checks.append(item);variables[target]=int(ticket>=count)
  elif op==94:
   obj=read();offset=struct.unpack_from('<i',data,pc)[0];pc+=4;at=pc+offset
   self_move=struct.unpack_from('<2H',data,at);assert obj==255 and self_move==(12,1);movements.append('one_step_north')
  else:raise AssertionError(('Unapproved opcode or state write',op,pc-2))
 raise AssertionError('Script did not terminate')

class BoardingTests(unittest.TestCase):
 def test_ticket_is_checked_and_not_consumed(self):
  result=run(1,1);self.assertEqual(result['messages'],[1,2]);self.assertEqual(result['checks'],[456]);self.assertEqual(result['ticket'],1);self.assertFalse(result['movements']);self.assertFalse(result['locked']);self.assertEqual(set(result['variables']),{0x800C})
 def test_missing_ticket_pushback_is_repeatable(self):
  for _ in range(3):
   result=run(1,0);self.assertEqual(result['messages'],[1,3]);self.assertEqual(result['movements'],['one_step_north']);self.assertEqual(result['ticket'],0);self.assertFalse(result['locked'])
 def test_northbound_exit_needs_no_ticket_or_dialogue(self):
  result=run(0,0);self.assertFalse(result['messages']);self.assertFalse(result['movements']);self.assertFalse(result['checks']);self.assertFalse(result['locked'])
if __name__=='__main__':unittest.main()
