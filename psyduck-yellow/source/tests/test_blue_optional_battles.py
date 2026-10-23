import unittest
from test_ss_anne_rival import run
from progression_cleanup import rival_scene as route_scene,R22_DONE,R22_HIDE,RIVAL_PICKED,RIVAL_DUCK,RIVAL_FEMALE
from cerulean import rival_scene as city_scene,RIVAL_DONE,RIVAL_HIDE
from parcel_quest import PARCEL_STATE

class OptionalBlueTests(unittest.TestCase):
 def test_all_branches_and_approaches_complete_after_either_outcome(self):
  for generator,first,done,hide,positions,kw in ((route_scene,747,R22_DONE,R22_HIDE,[(982,z) for z in range(265,269)],{}),(city_scene,782,RIVAL_DONE,RIVAL_HIDE,[(x,100) for x in range(1325,1330)],{'lanes':range(1325,1330)})):
   ids={f'{s}_{g}':first+i for i,(s,g) in enumerate(((54,'male'),(54,'female'),(133,'male'),(133,'female')))};ids.update({54:first,133:first+3});code=generator(ids,**kw)
   for duck in (False,True):
    for female in (False,True):
     flags={RIVAL_PICKED}|({RIVAL_DUCK} if duck else set())|({RIVAL_FEMALE} if female else set())
     for xy in positions:
      for win in (False,True):
       with self.subTest(first=first,duck=duck,female=female,xy=xy,win=win):
        r=run(flags,win,code=code,coordinates=xy,initial_vars={PARCEL_STATE:2})
        self.assertEqual(r['battles'],[ids[f'{54 if duck else 133}_{"female" if female else "male"}']]);self.assertEqual(r['messages'],[0,1 if win else 2,3]);self.assertIn(done,r['flags']);self.assertIn(hide,r['flags']);self.assertFalse(r['locked']);self.assertEqual(r['blackouts'],0);self.assertEqual(r['heals'],int(not win));self.assertEqual(len(r['movements']),3)
        self.assertFalse(run(r['flags'],code=code,initial_vars={PARCEL_STATE:2})['battles'])
if __name__=='__main__':unittest.main()
