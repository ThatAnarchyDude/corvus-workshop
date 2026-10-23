import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ss_anne_rival import scene,DONE,HIDE,CUT_GIVEN
from progression_cleanup import RIVAL_PICKED,RIVAL_DUCK,RIVAL_FEMALE
IDS={'54_male':809,'54_female':810,'133_male':811,'133_female':812,54:809,133:812}
def run(flags=(),win=True,starter=133,code=None,coordinates=(49,16),initial_vars=None):
 data=scene(IDS) if code is None else code;pc=0;flags=set(flags);vars=dict(initial_vars or {});messages=[];battles=[];writes=[];movements=[];blackouts=0;locked=False;field_loaded=True;heals=0
 def word():
  nonlocal pc
  n=struct.unpack_from('<H',data,pc)[0];pc+=2;return n
 def val(n):return vars.get(n,0) if n>=0x4000 else n
 for _ in range(200):
  op=word()
  if op==2:return dict(flags=flags,messages=messages,battles=battles,writes=writes,movements=movements,blackouts=blackouts,locked=locked,heals=heals)
  if op==32:comparison=0 if word() in flags else -1
  elif op in (30,31):
   f=word();writes.append((op,f));flags.add(f) if op==30 else flags.discard(f)
  elif op in (100,101):assert word() in (0,30)
  elif op in (80,81):word()
  elif op==82:pass
  elif op==96:locked=True
  elif op==97:locked=False
  elif op==17:
   a,b=word(),word();comparison=(val(a)>val(b))-(val(a)<val(b))
  elif op==28:
   c=data[pc];pc+=1;o=struct.unpack_from('<i',data,pc)[0];pc+=4;assert c in (1,5)
   if (comparison==0)==(c==1):pc+=o
  elif op==22:
   o=struct.unpack_from('<i',data,pc)[0];pc+=4;pc+=o
  elif op in (190,191):pc+=1
  elif op==45:
   assert field_loaded, 'Cannot display field dialogue after a normal trainer loss before WhiteOut'
   messages.append(data[pc]);pc+=1
  elif op in (50,53,95):pass
  elif op==105:
   x,z=word(),word();vars[x],vars[z]=coordinates
  elif op==41:
   a,b=word(),word();vars[a]=val(b)
  elif op==206:vars[word()]=starter
  elif op==213:
   tid,partner=word(),word();args=data[pc:pc+2];pc+=2;assert partner==0 and args==bytes([1,0]);battles.append(tid);field_loaded=True;heals+=int(not win)
  elif op==220:vars[word()]=int(win)
  elif op==219:blackouts+=1;field_loaded=True
  elif op==94:
   obj=word();offset=struct.unpack_from('<i',data,pc)[0];pc+=4;at=pc+offset;assert at%4==0
   actions=[]
   for _ in range(10):
    action,count=struct.unpack_from('<2H',data,at);at+=4
    if action==254:break
    actions.append((action,count))
   movements.append((obj,actions))
  else:raise AssertionError(('Unapproved operation',op,pc-2))
 raise AssertionError('Nonterminating scene')
class RivalSceneTests(unittest.TestCase):
 def test_all_four_saved_starter_choices(self):
  for duck in (False,True):
   for female in (False,True):
    flags={HIDE,RIVAL_PICKED}|({RIVAL_DUCK} if duck else set())|({RIVAL_FEMALE} if female else set());result=run(flags)
    self.assertEqual(result['battles'],[IDS[f'{54 if duck else 133}_{"female" if female else "male"}']]);self.assertIn(DONE,result['flags']);self.assertIn(HIDE,result['flags']);self.assertFalse(result['locked'])
 def test_optional_loss_heals_and_finishes_scene_without_blackout(self):
  result=run([HIDE,RIVAL_PICKED,RIVAL_DUCK],False)
  self.assertEqual(result['blackouts'],0);self.assertEqual(result['heals'],1)
  self.assertIn(DONE,result['flags']);self.assertIn(HIDE,result['flags'])
  self.assertEqual(result['messages'],[0,2,3]);self.assertFalse(result['locked'])
  self.assertEqual(result['movements'],[(255,[(2,1)]),(0,[(14,6),(12,6)])])
  self.assertFalse(run(result['flags'])['battles'])
 def test_completed_or_legacy_cut_save_does_not_repeat_battle(self):
  for flag in (DONE,CUT_GIVEN):
   result=run([flag]);self.assertFalse(result['battles']);self.assertFalse(result['writes']);self.assertFalse(result['messages'])
 def test_win_exits_on_walkable_native_landing(self):
  result=run([HIDE]);self.assertEqual(result['messages'],[0,1,3]);self.assertEqual(result['movements'],[(255,[(2,1)]),(0,[(14,6),(12,6)])]);self.assertEqual(result['blackouts'],0)
 def test_legacy_selection_fallback(self):
  self.assertEqual(run(starter=133)['battles'],[809]);self.assertEqual(run(starter=54)['battles'],[812])
if __name__=='__main__':unittest.main()
