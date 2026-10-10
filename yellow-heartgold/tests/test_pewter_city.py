"""Check Pewter's outdoor story, retained geometry, and archived events."""
import struct
import sys
import unittest
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from opening import events_decode
from pewter_city import patch, ROUTE_GUIDE, MUSEUM_GUIDE
from viridian_tutorial import TABLE


class PewterCityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=str(PROJECT/'build/yellow-heartgold-prototype-014.nds')
        cls.old=ndspy.rom.NintendoDSRom.fromFile(source)
        cls.new=ndspy.rom.NintendoDSRom.fromFile(source)
        cls.report=patch(cls.new)

    def arc(self,r,path):
        return ndspy.narc.NARC(r.files[r.filenames.idOf(path)]).files

    def events(self,r,m):
        d=r.loadArm9().sections[0].data
        i=struct.unpack_from('<H',d,TABLE+24*m+16)[0]
        return events_decode(self.arc(r,'a/0/3/2')[i])

    def test_outdoor_npcs_and_yellow_escort_trigger_preserve_native_warps(self):
        a,b=self.events(self.old,51),self.events(self.new,51)
        self.assertEqual(a[2],b[2])
        actors={struct.unpack_from('<H',x)[0]:x for x in b[1]}
        self.assertEqual(set(actors),{0,1,2,4,5,ROUTE_GUIDE,MUSEUM_GUIDE})
        self.assertEqual(struct.unpack_from('<H',actors[ROUTE_GUIDE],10)[0],1)
        self.assertEqual(struct.unpack_from('<H',actors[MUSEUM_GUIDE],10)[0],2)
        self.assertEqual(struct.unpack('<Hhh5H',b[3][0])[:5],(1,1086,104,1,4))
        for obj in (4,5):
            self.assertEqual(actors[obj],next(x for x in a[1] if struct.unpack_from('<H',x)[0]==obj))

    def test_route2_development_boundary_removed_without_changing_other_events(self):
        a,b=self.events(self.old,414),self.events(self.new,414)
        self.assertEqual(a[:3],b[:3])
        removed=[x for x in a[3] if x not in b[3]]
        self.assertEqual(len(removed),1)
        self.assertEqual(struct.unpack_from('<hh',removed[0],2),(1024,128))

    def test_every_other_map_and_original_scripts_events_and_graphics_preserved(self):
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in (51,414):
                self.assertEqual(a[TABLE+24*m:TABLE+24*(m+1)],b[TABLE+24*m:TABLE+24*(m+1)])
        for path in ('a/0/1/2','a/0/3/2'):
            a,b=self.arc(self.old,path),self.arc(self.new,path)
            self.assertEqual(a,b[:len(a)])
        for path in ('a/1/2/0','a/0/3/1','a/0/6/5','a/0/8/1'):
            self.assertEqual(self.arc(self.old,path),self.arc(self.new,path))


if __name__=='__main__':unittest.main()
