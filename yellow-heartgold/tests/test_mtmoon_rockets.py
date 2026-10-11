"""Fossil ambush outcomes, Yellow roster, and safe native walking paths."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.narc
import ndspy.rom
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon import patch as cave
from mtmoon_story import patch as story,STAGE
from mtmoon_items import patch as items
from mtmoon_rockets import patch,ambush,JESSIE,JAMES,HIDE_JESSIE,HIDE_JAMES
from test_mtmoon_story import run_script
from opening import events_decode
from viridian_tutorial import TABLE


class MtMoonRocketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        cave(cls.old);story(cls.old);items(cls.old)
        cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)

    def arc(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def test_only_fossil_chosen_stage_battles_and_loss_never_completes_quest(self):
        code=ambush(self.report['trainer'],0)
        for stage in (0,1,3):
            result=run_script(code,stage=stage,x=22,z=22)
            self.assertEqual(result[0][STAGE],stage);self.assertEqual(result[2:],([],[],[],set()))
        result=run_script(code,stage=2,win=False,x=22,z=22)
        self.assertEqual(result[0][STAGE],2);self.assertEqual(result[2],[])
        self.assertNotIn(HIDE_JESSIE,result[5]);self.assertNotIn(HIDE_JAMES,result[5])

    def test_victory_walks_pair_to_exit_before_hiding_and_commits_once(self):
        for x in range(20,25):
            result=run_script(ambush(self.report['trainer'],0),stage=2,x=x,z=22)
            self.assertEqual(result[0][STAGE],3);self.assertEqual(result[2],[JAMES,JESSIE])
            self.assertEqual(result[3][-2:],[(JAMES,[(13,2),(14,1)]),(JESSIE,[(13,2),(15,1)])])
            self.assertEqual(result[4],[0,1,2,3]);self.assertEqual(result[5],{self.report['trainer'],HIDE_JESSIE,HIDE_JAMES})

    def test_exact_yellow_team_and_moves_single_battle(self):
        row=self.arc(self.new,'a/0/5/5')[self.report['trainer']]
        self.assertEqual((row[0],row[3],row[16]),(1,3,0))
        rows=list(struct.iter_unpack('<BB3H4H',self.arc(self.new,'a/0/5/6')[self.report['trainer']]))
        self.assertEqual([(r[3],r[2]) for r in rows],[(23,14),(52,14),(109,14)])
        self.assertEqual([r[5:] for r in rows],[(35,43,40,0),(10,45,44,0),(33,123,0,0)])

    def test_approach_and_departure_paths_use_native_passable_tiles_without_other_actor_collision(self):
        d=self.new.loadArm9().sections[0].data;matrix=self.arc(self.new,'a/0/4/1')[struct.unpack_from('<H',d,TABLE+107*24+4)[0]]
        land=self.arc(self.new,'a/0/6/5')[struct.unpack_from('<H',matrix,5+matrix[4])[0]]
        groups=events_decode(self.arc(self.new,'a/0/3/2')[self.report['event']])
        others={struct.unpack_from('<2H',r,24) for r in groups[1] if struct.unpack_from('<H',r)[0] not in (JESSIE,JAMES)}
        routes=[(20,21),(21,21),(23,20),(23,21),(23,22),(23,23),(22,23),(21,22),(21,23)]
        for x,z in routes:
            self.assertFalse(struct.unpack_from('<H',land,20+2*(z*32+x))[0]&0x8000,(x,z))
            self.assertNotIn((x,z),others)
        # Ordinary vision battles must not take priority over the ambush on
        # the exit row; otherwise the player could step past its trigger.
        for row in groups[1]:
            if struct.unpack_from('<H',row,6)[0]==1:
                self.assertNotEqual(struct.unpack_from('<H',row,26)[0],22)
        before=events_decode(self.arc(self.old,'a/0/3/2')[self.report['original']['event']])
        self.assertEqual(groups[2],before[2]);self.assertEqual(groups[0],before[0])
        self.assertIn(struct.pack('<Hhh5H',self.report['entry'],20,22,5,1,0,2,STAGE),groups[3])
        for path in ('a/0/4/1','a/0/6/5','a/0/8/1'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(path)],self.new.files[self.new.filenames.idOf(path)])

if __name__=='__main__':unittest.main()
