"""Reward failure/retry paths, serialised teams, save bounds and asset safety."""
import json,struct,sys,unittest,os
from pathlib import Path
import ndspy.rom,ndspy.narc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from route24 import recruiter,damian,NUGGET_GIVEN,ROCKET_BEAT,CHARMANDER_GIVEN,TM_TAKEN,TM_ITEM
from cerulean import rival_scene,RIVAL_DONE
from opening import events_decode
from viridian_tutorial import TABLE
from test_prototype0021 import run

class Rewards(unittest.TestCase):
    def test_all_five_wins_required_before_nugget(self):
        for missing in range(5):
            r=run(recruiter(list(range(787,792)),793),defeated=set(range(787,792))-{787+missing},x=1327,z=74)
            self.assertEqual(r['bag'],{});self.assertEqual(r['battles'],[]);self.assertNotIn(NUGGET_GIVEN,r['flags'])
    def test_reward_once_before_battle_and_loss_retry_without_duplicate(self):
        script=recruiter(list(range(787,792)),793)
        lost=run(script,defeated=range(787,792),win=False,x=1327,z=74)
        self.assertEqual(lost['bag'],{92:1});self.assertTrue(lost['whiteout']);self.assertIn(NUGGET_GIVEN,lost['flags']);self.assertNotIn(ROCKET_BEAT,lost['flags'])
        retry=run(script,defeated=range(787,792),flags=lost['flags'],bag=lost['bag'],x=1327,z=74)
        self.assertEqual(retry['bag'],{92:1});self.assertIn(ROCKET_BEAT,retry['flags'])
        again=run(script,flags=retry['flags'],bag=retry['bag'],x=1327,z=74)
        self.assertEqual(again['bag'],{92:1});self.assertEqual(again['battles'],[])
    def test_full_bag_retains_reward_and_moves_player_back_in_every_lane(self):
        for x in range(1325,1330):
            r=run(recruiter(list(range(787,792)),793),defeated=range(787,792),room=False,x=x,z=74)
            self.assertNotIn(NUGGET_GIVEN,r['flags']);self.assertEqual(r['battles'],[]);self.assertIn((255,[(13,1)]),r['walks'])
            retry=run(recruiter(list(range(787,792)),793),defeated=range(787,792),x=x,z=74)
            self.assertEqual(retry['bag'],{92:1})
    def test_charmander_decline_party_full_and_repeat_do_not_consume_gift(self):
        for options in ({'yes':False},{'count':6},{'flags':{CHARMANDER_GIVEN}}):
            r=run(damian(),**options);self.assertNotIn('pokemon4',r['bag'])
        r=run(damian());self.assertEqual(r['bag']['pokemon4'],1);self.assertIn(CHARMANDER_GIVEN,r['flags'])

class Assets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0022.nds'))
        cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0023_ROM','build/yellow-heartgold-prototype-0023.nds')))
        cls.report=json.loads((PROJECT/'build/0023-development-report.json').read_text())
    def archive(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
    def test_geometry_and_johto_and_previous_trainer_records_unchanged(self):
        for p in ('a/0/4/1','a/0/6/5','a/0/4/0'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(p)],self.new.files[self.new.filenames.idOf(p)],p)
        for p in ('a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6'):
            old=self.archive(self.old,p);self.assertEqual(old,self.archive(self.new,p)[:len(old)],p)
        a=self.old.loadArm9().sections[0].data;b=self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in (28,52,107):self.assertEqual(a[TABLE+m*24:TABLE+(m+1)*24],b[TABLE+m*24:TABLE+(m+1)*24],m)
    def test_yellow_teams_and_wild_levels_and_slot_weighting(self):
        tr=self.archive(self.new,'a/0/5/5');parties=self.archive(self.new,'a/0/5/6');r=self.report['route24']
        self.assertEqual([[p['level'] for p in t['team']] for t in r['trainers']],[[14,14],[14,14],[14,14,14],[16,16],[18],[14,14],[15,15]])
        for t in r['trainers']:
            self.assertEqual(tr[t['id']][1],t['trainer_class'])
            for i,p in enumerate(t['team']):
                v=struct.unpack_from('<BB3H4H',parties[t['id']],i*16);self.assertEqual((v[2],v[3],list(v[5:])),(p['level'],p['species'],p['moves']))
        w=self.archive(self.new,'a/0/3/7')[r['wild']];self.assertEqual(list(w[8:20]),[12,12,13,14,14,15,13,13,16,17,16,17])
        self.assertEqual(struct.unpack_from('<12H',w,20),struct.unpack_from('<12H',w,44));self.assertEqual(w[1:6],bytes(5))
    def test_flags_are_persistent_and_item_solid_and_startup_aligned(self):
        flags=self.report['route24']['flags'];self.assertEqual(flags,list(range(0xA8D,0xA93)));self.assertTrue(all(f<0xAA0 for f in flags))
        g=events_decode(self.archive(self.new,'a/0/3/2')[self.report['route24']['event']]);items=[r for r in g[1] if struct.unpack_from('<H',r,2)[0]==87]
        self.assertEqual(len(items),1);self.assertEqual(struct.unpack_from('<H',items[0],8)[0],TM_TAKEN)
        main=self.new.loadArm9();self.assertEqual(len(main.sections[1].data)%4,0);self.assertEqual(struct.unpack_from('<I',main.sections[0].data,0xD2C68)[0],main.sections[1].ramAddress+len(main.sections[1].data))
    def test_old_native_thunder_wave_and_custom_tms_remain_and_blue_lanes_cover_bridge(self):
        old=self.archive(self.old,'a/0/0/2');new=self.archive(self.new,'a/0/0/2')
        for a,b in zip(old,new):self.assertEqual(a[:41],b[:41]) # Only unused bit 105 in byte 41 may change.
        r=self.report['route24'];self.assertEqual(r['tm']['tms'][0]['item'],TM_ITEM);self.assertEqual(r['tm']['tms'][0]['number'],45)
        for x in range(1325,1330):
            battle=run(rival_scene({'54_male':782,'54_female':783,'133_male':784,'133_female':785,54:782,133:785},range(1325,1330)),x=x,z=100)
            self.assertIn(RIVAL_DONE,battle['flags']);self.assertEqual(battle['battles'],[782]);self.assertTrue(battle['walks'])

if __name__=='__main__':unittest.main()
