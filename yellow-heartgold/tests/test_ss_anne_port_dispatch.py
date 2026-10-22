import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ss_anne_port_dispatch import dispatch,STATE,GAME_CLEAR

def execute(cleared):
 data=dispatch();pc=0;writes={};warps=[];fades=[];locked=False
 def word():
  nonlocal pc
  v=struct.unpack_from('<H',data,pc)[0];pc+=2;return v
 for _ in range(30):
  op=word()
  if op==2:return writes,warps,fades,locked
  if op==41:
   key,value=word(),word();writes[key]=value
  elif op==32:
   assert word()==GAME_CLEAR;condition=cleared
  elif op==28:
   kind=data[pc];pc+=1;offset=struct.unpack_from('<i',data,pc)[0];pc+=4
   assert kind==1
   if condition:pc+=offset
  elif op==96:locked=True
  elif op==97:locked=False
  elif op==174:fades.append(tuple(word() for _ in range(4)))
  elif op==175:pass
  elif op==176:warps.append(tuple(word() for _ in range(5)))
  else:raise AssertionError(('Unexpected instruction/state mutation',op,pc-2))
 raise AssertionError('Unterminated dispatch')

class DispatchTests(unittest.TestCase):
 def test_before_hall_of_fame_stays_in_anne_port(self):
  self.assertEqual(execute(False),({STATE:1},[],[],False))
 def test_after_hall_of_fame_restores_native_port(self):
  writes,warps,fades,locked=execute(True)
  self.assertEqual(writes,{0x4000:1});self.assertEqual(warps,[(386,0,7,3,0)])
  self.assertEqual(fades,[(6,6,0,0),(6,6,1,0)]);self.assertFalse(locked)
 def test_repeated_entries_do_not_change_persistent_state(self):
  for cleared in (False,True,False,True):
   self.assertEqual(execute(cleared)[0],{STATE:1})
if __name__=='__main__':unittest.main()
