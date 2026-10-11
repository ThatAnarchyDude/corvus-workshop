"""Cerulean rewards, native trainer data and terrain-safe Pewter guide."""
import unittest,sys,struct,json
from pathlib import Path
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from opening import events_decode
from viridian_tutorial import TABLE
from cerulean_bike import clerk,VOUCHER,BICYCLE,RECEIVED
from cerulean import misty,melanie,MISTY_TM,BULBA_GIVEN,BULBA_HIDE,rival_scene,RIVAL_DONE,RIVAL_HIDE
from pewter_guide_fix import PATH,STATE,escort,step


def run(code,*,flags=(),bag=None,room=True,yes=True,badge=False,win=True,friendship=200,count=1,z=104,x=1086,starter=133):
 vars={};flags=set(flags);bag=dict(bag or {});msgs=[];walks=[];badges=[];battles=[];music=[];pc=0;cmp=0
 def half():
  nonlocal pc
  n=struct.unpack_from('<H',code,pc)[0];pc+=2;return n
 for _ in range(2000):
  op=half()
  if op in (2,219):return dict(flags=flags,bag=bag,messages=msgs,walks=walks,badges=badges,whiteout=op==219,battles=battles,music=music)
  if op in (73,78,80,81,36):
   arg=half()
   if op==80:music.append(arg)
  elif op in (96,97,104,50,53,79,95,82):pass
  elif op in (190,191,45):
   n=code[pc];pc+=1
   if op==45:msgs.append(n)
  elif op==17:
   a,b=half(),half();v=vars.get(a,0);cmp=-1 if v<b else 1 if v>b else 0
  elif op==28:
   cond=code[pc];pc+=1;off=struct.unpack_from('<i',code,pc)[0];pc+=4
   if (cond==1 and cmp==0) or (cond==5 and cmp!=0) or (cond==0 and cmp<0):pc+=off
  elif op==22:off=struct.unpack_from('<i',code,pc)[0];pc+=4;pc+=off
  elif op==32:cmp=0 if half() in flags else 1
  elif op in (30,31):
   f=half()
   if op==30:flags.add(f)
   else:flags.discard(f)
  elif op==41:a,b=half(),half();vars[a]=b
  elif op==63:vars[half()]=0 if yes else 1
  elif op==128:a,b,c=half(),half(),half();vars[c]=int(bag.get(a,0)>=b)
  elif op==125:
   a,b,c=half(),half(),half();vars[c]=int(room)
   if room:bag[a]=bag.get(a,0)+b
  elif op==126:
   a,b,c=half(),half(),half();bag[a]=bag.get(a,0)-b;vars[c]=1
  elif op==294:half();vars[half()]=int(badge)
  elif op==295:badges.append(half())
  elif op==206:vars[half()]=starter
  elif op==213:battles.append(half());half();pc+=2
  elif op==220:vars[half()]=int(win)
  elif op==382:out=half();half();vars[out]=friendship
  elif op==332:vars[half()]=count
  elif op==137:
   args=[half() for _ in range(6)];vars[args[-1]]=1;bag['bulbasaur']=bag.get('bulbasaur',0)+1
  elif op==101:half()
  elif op==105:vars[half()]=x;vars[half()]=z
  elif op==94:
   obj=half();off=struct.unpack_from('<i',code,pc)[0];pc+=4;at=pc+off;arr=[]
   while True:
    mv,num=struct.unpack_from('<2H',code,at);at+=4
    if mv==254:break
    arr.append((mv,num))
   walks.append((obj,arr))
  else:raise AssertionError((op,pc))
 raise AssertionError('Script did not terminate')

class Decisions(unittest.TestCase):
 def test_bike_requires_voucher_and_commits_only_successfully(self):
  for options in ({},{'yes':False}):
   r=run(clerk(),**options);self.assertNotIn(BICYCLE,r['bag']);self.assertNotIn(RECEIVED,r['flags'])
  r=run(clerk(),bag={VOUCHER:1});self.assertEqual(r['bag'],{VOUCHER:0,BICYCLE:1});self.assertIn(RECEIVED,r['flags'])
  r=run(clerk(),bag={VOUCHER:1},room=False);self.assertEqual(r['bag'],{VOUCHER:1});self.assertNotIn(RECEIVED,r['flags'])
  r=run(clerk(),bag={BICYCLE:1,VOUCHER:1});self.assertEqual(r['bag'],{BICYCLE:1,VOUCHER:1})
  r=run(clerk(),flags={RECEIVED},bag={BICYCLE:1});self.assertEqual(r['bag'],{BICYCLE:1})
 def test_misty_awards_badge_on_win_and_TM_retries_bag_full(self):
  r=run(misty(800,[798,799]));self.assertEqual(r['badges'],[9]);self.assertEqual(r['bag'],{119:1});self.assertIn(MISTY_TM,r['flags'])
  r=run(misty(800,[798,799]),win=False);self.assertTrue(r['whiteout']);self.assertEqual((r['bag'],r['badges']),({},[]))
  r=run(misty(800,[798,799]),room=False);self.assertEqual(r['badges'],[9]);self.assertNotIn(MISTY_TM,r['flags'])
  r=run(misty(800,[798,799]),badge=True);self.assertEqual(r['bag'],{119:1});self.assertEqual(r['badges'],[])
  r=run(misty(800,[798,799]),badge=True,flags={MISTY_TM});self.assertEqual(r['bag'],{})
 def test_bulbasaur_friendship_decline_full_party_and_repeat(self):
  for options in ({'friendship':146},{'yes':False},{'count':6},{'flags':{BULBA_GIVEN}}):
   r=run(melanie(),**options);self.assertNotIn('bulbasaur',r['bag'])
  r=run(melanie(),friendship=147);self.assertEqual(r['bag']['bulbasaur'],1);self.assertTrue({BULBA_GIVEN,BULBA_HIDE}<=r['flags'])
 def test_guide_covers_all_exit_lanes_and_stops_after_brock(self):
  for z in range(101,107):
   r=run(escort(),z=z);self.assertEqual(r['messages'],[0,1]);self.assertTrue(r['walks'])
  self.assertEqual(run(escort(),badge=True)['walks'],[])
 def test_blue_keeps_choice_and_only_completes_after_win(self):
  ids={'54_male':782,'54_female':783,'133_male':784,'133_female':785,54:782,133:785}
  for x in range(1329,1333):
   for female in [False,True]:
    for duck in [False,True]:
     flags={0xB41}|({0xB40} if duck else set())|({0xB3F} if female else set())
     r=run(rival_scene(ids),x=x,flags=flags)
     self.assertEqual(r['battles'],[782+int(female) if duck else 784+int(female)])
     self.assertTrue({RIVAL_DONE,RIVAL_HIDE}<=r['flags']);self.assertEqual(r['music'],[1088,1089])
  self.assertEqual(run(rival_scene(ids),flags={RIVAL_DONE})['battles'],[])
  r=run(rival_scene(ids),win=False);self.assertTrue(r['whiteout']);self.assertNotIn(RIVAL_DONE,r['flags'])
 def test_manual_guide_interaction_aligns_from_each_side(self):
  for x,z in [(1084,104),(1085,103),(1085,105),(1086,104)]:
   r=run(escort(),x=x,z=z)
   moves=r['walks'][0][1]
   for direction,n in moves:
    dx,dz={12:(0,-1),13:(0,1),14:(-1,0),15:(1,0),2:(0,0)}[direction]
    x+=dx*n;z+=dz*n
   self.assertEqual((x,z),(1086,104))
 def test_guide_entire_escort_and_return_avoids_solid_terrain(self):
  rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0020.nds'));m=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')]).files[0];w,h,hdr,alt,n=m[:5];off=5+n+w*h*(2*hdr+alt);lands=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/6/5')]).files
  for route in (PATH['escort'],PATH['return']):
   for i,(x,z) in enumerate(route):
    li=struct.unpack_from('<H',m,off+2*(z//32*w+x//32))[0];p=struct.unpack_from('<H',lands[li],20+2*(z%32*32+x%32))[0];self.assertFalse(p&0x8000,(x,z));self.assertNotIn([x,z],PATH['blocked'])
    if i:self.assertIn(step(route[i-1],route[i]),(12,13,14,15))
  self.assertNotIn(PATH['player_finish'],PATH['return'])

if __name__=='__main__':unittest.main()
