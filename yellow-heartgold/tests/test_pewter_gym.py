"""Check Yellow's gym teams, native dispatch and preserved HG gym assets."""
import struct
import sys
import unittest
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from opening import events_decode
from pewter_gym import patch, GYM_MAP
from viridian_tutorial import TABLE


class PewterGymTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-014.nds'))
        cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-014.nds'))
        cls.report=patch(cls.new)

    def arc(self,rom,path):
        return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def test_brock_and_junior_levels_and_moves_match_yellow(self):
        teams=[[(50,11,[10,0,0,0]),(27,11,[10,28,0,0])],
               [(74,12,[33,111,0,0]),(95,14,[33,103,117,0])]]
        for row,expected in zip(self.report['trainers'],teams):
            t=self.arc(self.new,'a/0/5/5')[row['id']]
            self.assertEqual((t[0],t[3],t[16]),(1,2,0))
            self.assertEqual(t[4:12],bytes(8))
            p=self.arc(self.new,'a/0/5/6')[row['id']]
            actual=[(v[3],v[2],list(v[5:])) for v in struct.iter_unpack('<BB3H4H',p)]
            self.assertEqual(actual,expected)

    def test_gym_has_one_junior_brock_and_guide_with_original_warps(self):
        oldmain=self.old.loadArm9().sections[0].data
        oldid=struct.unpack_from('<H',oldmain,TABLE+GYM_MAP*24+16)[0]
        old=events_decode(self.arc(self.old,'a/0/3/2')[oldid])
        new=events_decode(self.arc(self.new,'a/0/3/2')[self.report['event']])
        self.assertEqual(new[2],old[2])
        actors={struct.unpack_from('<H',a)[0]:a for a in new[1]}
        self.assertEqual(set(actors),{0,1,2})
        self.assertEqual(struct.unpack_from('<2H',actors[1],8),(0,1))
        self.assertEqual(struct.unpack_from('<H',actors[2],10)[0],3755)

    def test_old_assets_and_every_other_map_header_are_preserved(self):
        for path in ('a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6'):
            old,new=self.arc(self.old,path),self.arc(self.new,path)
            self.assertEqual(new[:len(old)],old)
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m!=GYM_MAP:self.assertEqual(a[TABLE+24*m:TABLE+24*(m+1)],b[TABLE+24*m:TABLE+24*(m+1)])
        self.assertEqual(self.old.arm7,self.new.arm7)
        self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)


if __name__=='__main__':unittest.main()
