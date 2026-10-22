import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ss_anne_departure import arrival,guarded_gate,CUT_GIVEN,DEPARTED

def run(data,flags=(),position=(23,18),direction=1,ticket=1):
 flags=set(flags);pc=0;variables={};messages=[];moves=[];warps=[];writes=[];locked=False
 def word():
  nonlocal pc
  v=struct.unpack_from('<H',data,pc)[0];pc+=2;return v
 def value(v):return variables.get(v,0) if v>=0x4000 else v
 for _ in range(200):
  op=word()
  if op==2:return dict(flags=flags,messages=messages,moves=moves,warps=warps,writes=writes,locked=locked)
  if op==0:pass
  elif op==41:
   k,v=word(),word();variables[k]=v
  elif op==32:comparison=0 if word() in flags else -1
  elif op==30:
   f=word();flags.add(f);writes.append(f)
  elif op==105:
   x,y=word(),word();variables[x],variables[y]=position
  elif op==386:variables[word()]=direction
  elif op==17:
   a,b=word(),word();comparison=(value(a)>value(b))-(value(a)<value(b))
  elif op==28:
   cond=data[pc];pc+=1;off=struct.unpack_from('<i',data,pc)[0];pc+=4;assert cond in (1,5)
   if (comparison==0)==(cond==1):pc+=off
  elif op==22:
   off=struct.unpack_from('<i',data,pc)[0];pc+=4;pc+=off
  elif op==96:locked=True
  elif op==97:locked=False
  elif op in (190,191):pc+=1
  elif op==45:messages.append(data[pc]);pc+=1
  elif op in (50,53,95,175):pass
  elif op in (73,75):word()
  elif op==174:
   for _ in range(4):word()
  elif op==176:warps.append(tuple(word() for _ in range(5)))
  elif op==723:
   scene,direction=data[pc:pc+2];pc+=2;assert scene==1 and direction==0
   destination,x,z=word(),word(),word();warps.append((destination,-1,x,z,direction))
  elif op==128:
   item,n,target=word(),word(),word();assert item==456;variables[target]=int(ticket>=n)
  elif op==94:
   obj=word();off=struct.unpack_from('<i',data,pc)[0];pc+=4;at=pc+off;assert obj==255 and at%4==0
   movement=[]
   for _ in range(10):
    action,count=struct.unpack_from('<2H',data,at);at+=4
    if action==254:break
    movement.append((action,count))
   moves.append(movement)
  else:raise AssertionError(('Unsupported mutation/opcode',op,pc-2))
 raise AssertionError('Nonterminating script')

class DepartureTests(unittest.TestCase):
 def test_without_cut_ship_return_does_not_depart(self):
  r=run(arrival());self.assertFalse(r['writes']);self.assertFalse(r['moves']);self.assertFalse(r['messages'])
 def test_cut_does_not_depart_on_city_side_or_unrelated_positions(self):
  for xy in [(12,z) for z in range(12,21)]+[(23,17),(23,20),(22,18),(24,18)]:
   r=run(arrival(),[CUT_GIVEN],xy);self.assertFalse(r['writes'],xy);self.assertFalse(r['moves'],xy)
 def test_return_after_cut_departs_once_and_releases_control(self):
  r=run(arrival(),[CUT_GIVEN]);self.assertEqual(r['writes'],[DEPARTED]);self.assertEqual(r['moves'],[[(13,2),(14,11),(12,7)]]);self.assertEqual(r['warps'],[(263,-1,7,11,0)]);self.assertFalse(r['locked'])
  repeated=run(arrival(),r['flags']);self.assertFalse(repeated['writes']);self.assertFalse(repeated['warps'])
 def test_departed_blocks_even_with_ticket_without_consuming_it(self):
  r=run(guarded_gate(4),[DEPARTED]);self.assertEqual(r['messages'],[4]);self.assertEqual(r['moves'],[[(12,1)]]);self.assertFalse(r['writes']);self.assertFalse(r['locked'])
 def test_northbound_exit_always_allowed(self):
  r=run(guarded_gate(4),[DEPARTED],direction=0,ticket=0);self.assertFalse(r['messages']);self.assertFalse(r['moves'])
 def test_cut_alone_does_not_close_boarding(self):
  r=run(guarded_gate(4),[CUT_GIVEN]);self.assertEqual(r['messages'],[1,2]);self.assertFalse(r['moves'])
if __name__=='__main__':unittest.main()

