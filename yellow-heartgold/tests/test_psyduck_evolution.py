"""Execute native evolution checks and verify unrelated evolution data survives."""
import struct
import unittest
import ndspy.rom
import ndspy.narc
import test_rare_candy_evolution as candy_tests
from build_rom import PROJECT
from psyduck_evolution import patch


class PsyduckEvolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=str(PROJECT/'build/yellow-heartgold-prototype-015.nds')
        cls.old=ndspy.rom.NintendoDSRom.fromFile(path)
        cls.new=ndspy.rom.NintendoDSRom.fromFile(path)
        cls.report=patch(cls.new)

    def native(self,species=54,**options):
        runner=candy_tests.RareCandyEvolutionTests(methodName='runTest')
        runner.rom=self.new
        return runner.native_evolution(species,**options)

    def test_moon_stone_works_in_native_eligibility_and_execution(self):
        for context in (2,3):
            for level in (5,33,100):
                with self.subTest(context=context,level=level):
                    self.assertEqual(self.native(level=level,context=context,evo_parameter=81),55)

    def test_no_level_up_or_water_stone_evolution(self):
        for level in (32,33,34,100):
            self.assertEqual(self.native(level=level),0)
        for context in (2,3):
            self.assertEqual(self.native(context=context,evo_parameter=84),0)
            self.assertEqual(self.native(context=context,evo_parameter=82),0)

    def test_native_table_only_has_moon_stone_and_other_species_preserved(self):
        file=self.old.filenames.idOf('a/0/3/4')
        old,new=[ndspy.narc.NARC(r.files[file]) for r in (self.old,self.new)]
        self.assertEqual([i for i,(a,b) in enumerate(zip(old.files,new.files)) if a!=b],[54])
        self.assertEqual(bytes(new.files[54]),struct.pack('<3H',7,81,55)+bytes(38))
        self.assertEqual(self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data)
        a,b=[r.loadArm9().sections[1].data for r in (self.old,self.new)]
        self.assertEqual(sum(x!=y for x,y in zip(a,b)),1)
        self.assertEqual(self.old.arm7,self.new.arm7)
        self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)

    def test_other_custom_stone_evolutions_still_work(self):
        self.assertEqual(self.native(175,context=3,evo_parameter=109),176)
        self.assertEqual(self.native(133,context=3,evo_parameter=108),197)
        self.assertEqual(self.native(133,context=3,evo_parameter=84),134)

    def test_existing_stones_work_at_level_100(self):
        for species,item,target in ((133,83,135),(133,84,134),(133,82,136),
                                    (133,109,196),(133,108,197),(133,246,471),
                                    (133,85,470),(175,109,176),(25,83,26)):
            with self.subTest(species=species,item=item):
                self.assertEqual(self.native(species,level=100,context=3,evo_parameter=item),target)
