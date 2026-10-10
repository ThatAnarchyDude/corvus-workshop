"""Validate temporary gate collisions, native Cut events and one-time reward."""
import json,struct,sys,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc,ndspy.texture
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from adventure_ready import *
from test_viridian_tutorial import EventRun
import test_opening_corrections as geometry_tests
from progression_cleanup import repair_scroll


class RewardRun(EventRun):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cards=[];self.map_levels=[];self.shown=[];self.hidden=[]
    def read(self,fmt='H'):
        at=self.at;v=super().read(fmt)
        if fmt=='H' and v in [145,804]:
            (self.cards if v==145 else self.map_levels).append(super().read('B'));return 1
        if fmt=='H' and at>=2:
            op=self.code[at-2:at]
            if op==command(100):self.shown.append(v)
            if op==command(101):self.hidden.append(v)
        return v


class Progression(unittest.TestCase):
    def test_reward_requires_delivery_and_is_given_once_before_shop(self):
        code=upper_clerk(13,14)
        for parcel in [0,1]:
            r=RewardRun(code,variables={PARCEL_STATE:parcel},bag={459:1}).run();self.assertEqual(r.cards,[]);self.assertNotIn(GEAR_REWARD,r.flags);self.assertNotIn(0x9C,r.flags)
        r=RewardRun(code,variables={PARCEL_STATE:2}).run();self.assertEqual(r.cards,[1]);self.assertEqual(r.map_levels,[2]);self.assertEqual(r.messages,[13,14]);self.assertIn(GEAR_REWARD,r.flags);self.assertIn(0x9C,r.flags);self.assertIn(0x9A,r.flags)
        r=RewardRun(code,variables=r.variables,flags=r.flags).run();self.assertEqual(r.cards,[]);self.assertEqual(r.messages,[])
    def test_completed_legacy_save_still_receives_reward(self):
        r=RewardRun(upper_clerk(13,14),variables={PARCEL_STATE:2},flags={0x9C,TUTORIAL_DONE}).run();self.assertEqual(r.cards,[1]);self.assertIn(TUTORIAL_DONE,r.flags)
    def test_west_exit_blocks_before_delivery_and_clears_after(self):
        for parcel in [0,1,2]:
            r=RewardRun(west_guard(18),variables={PARCEL_STATE:parcel}).run();self.assertEqual(r.messages,[18] if parcel!=2 else []);self.assertEqual(94 in r.commands,parcel!=2)
    def test_barriers_removed_only_after_lesson(self):
        code=old_man(12,clear_objects=[v[0] for v in BLOCKERS])
        for parcel,flags in [(0,set()),(1,{0x6B}),(2,set()),(2,{0x6B})]:
            r=RewardRun(code,variables={PARCEL_STATE:parcel},flags=flags,x=1027,z=236).run();self.assertEqual(r.hidden,[v[0] for v in BLOCKERS] if parcel==2 and 0x6B in flags else [])
    def test_migration_adds_missing_actors_without_replaying_or_duplicating(self):
        for parcel in [0,2]:
            for done in [False,True]:
                flags={TUTORIAL_DONE} if done else set();r=RewardRun(world_sync(True)+command(2),variables={PARCEL_STATE:parcel},flags=flags).run()
                expected=([v[0] for v in BLOCKERS] if not done else [22])+[19,20]+([21] if parcel!=2 else [])
                self.assertEqual(r.shown,expected);self.assertEqual(r.hidden,[]);self.assertEqual(WEST_HIDE in r.flags,parcel==2)
                r=RewardRun(world_sync(True)+command(2),variables=r.variables,flags=r.flags).run();self.assertEqual(r.shown,[]);self.assertEqual(r.hidden,[])
    def test_saved_guard_removed_only_if_it_previously_existed(self):
        r=RewardRun(world_sync(True)+command(2),variables={PARCEL_STATE:2},flags={WORLD_MIGRATED}).run();self.assertEqual(r.hidden,[21]);self.assertIn(WEST_HIDE,r.flags)
    def test_granddaughter_walks_aside_and_becomes_a_wandering_npc(self):
        code=old_man(12,clear_objects=[v[0] for v in BLOCKERS if v[0]!=17],companion=(17,[(13,3),(0,1)]),companion_after=22)
        r=RewardRun(code,variables={PARCEL_STATE:2},flags={0x6B},x=1027,z=236).run();self.assertEqual(r.hidden,[14,15,16,18,17]);self.assertEqual(r.shown,[22]);self.assertNotIn(PASSED_HIDE,r.flags)


class Binary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-011.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-012.nds'));cls.report=json.loads((PROJECT/'build/adventure-ready-report.json').read_text())
    def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
    def test_gate_is_closed_by_objects_then_opens_without_permanent_walls(self):
        geometry=geometry_tests.BinaryChecks();self.assertFalse(geometry.can_pass(self.new,BARRIER_TILES+[(1027,235)]));self.assertTrue(geometry.can_pass(self.new,[(x,z) for _,x,z,_ in TREES]+[(1029,237)]))
        walk=geometry.walkable(self.new);self.assertTrue(all(walk(x,z) for x,z in BARRIER_TILES))
    def test_cut_trees_use_native_sprites_standard_script_and_separate_temp_flags(self):
        d=self.new.loadArm9().sections[0].data;e=struct.unpack_from('<H',d,TABLE+50*24+16)[0];rows=events_decode(self.arc(self.new,'a/0/3/2')[e])[1];decoded=[struct.unpack('<6Hh5h2Hi',r) for r in rows];self.assertEqual(len({r[0] for r in decoded}),len(decoded))
        for obj,x,z,flag in TREES:
            r=next(v for v in decoded if v[0]==obj);self.assertEqual((r[1],r[4],r[5],r[12],r[13]),(86,flag,10000,x,z))
        girl=next(v for v in decoded if v[0]==17);wandering=next(v for v in decoded if v[0]==22)
        self.assertEqual((girl[1],girl[2],girl[12],girl[13]),(7,0,1028,235));self.assertEqual((wandering[1],wandering[2],wandering[10],wandering[11]),(7,3,1,1))
    def test_invisible_model_is_fully_transparent_and_original_models_remain(self):
        a,b=self.arc(self.old,'a/0/8/1'),self.arc(self.new,'a/0/8/1');self.assertEqual(a,b[:len(a)]);tex=ndspy.texture.NSBTX(b[self.report['invisible']['model']]);self.assertTrue(all(t.isColor0Transparent and not any(t.data1) for _,t in tex.textures))
    def test_intro_johto_and_center_unchanged(self):
        for p in ['a/1/2/0','a/0/3/1']:self.assertEqual(self.arc(self.old,p),self.arc(self.new,p))
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in [50,500]:self.assertEqual(a[TABLE+m*24:TABLE+(m+1)*24],b[TABLE+m*24:TABLE+(m+1)*24])
        self.assertEqual(self.old.arm7,self.new.arm7)
    def test_both_cashier_scenes_have_the_promise_and_lower_cashier_stays_non_shop(self):
        d=self.new.loadArm9().sections[0].data
        for m in [50,500]:
            tid=struct.unpack_from('<H',d,TABLE+m*24+10)[0];msg=decode_messages(self.arc(self.new,'a/0/2/7')[tid])[1][4];self.assertEqual(repair_scroll(msg),decode_messages(encode_text(["Okay! Say hi to PROF.OAK for me!\r"+PROMISE],PH))[1][0])
        sid=struct.unpack_from('<H',d,TABLE+500*24+6)[0];self.assertNotIn(command(20,2048),split_bank(self.arc(self.new,'a/0/1/2')[sid])[0])
