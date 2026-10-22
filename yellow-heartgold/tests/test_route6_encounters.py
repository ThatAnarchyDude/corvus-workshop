import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route6_encounters import patch,encounter_table
from viridian_tutorial import TABLE

class Route6Encounters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0028-native-interiors-v1/Pokemon-Psyduck-Yellow-prototype-0028.nds'))
        cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after)
    def test_grass_matches_yellow_all_times(self):
        arc=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/3/7')]);w=arc.files[self.report['wild']]
        expected={(16,15):20,(19,14):20,(63,7):15,(16,16):10,(19,16):10,(16,17):10,(17,17):5,(39,3):5,(39,5):4,(39,7):1}
        for period in range(3):
            actual={}
            for sp,lv,p in zip(struct.unpack_from('<12H',w,20+period*24),w[8:20],(20,20,10,10,10,10,5,5,4,4,1,1)):
                actual[sp,lv]=actual.get((sp,lv),0)+p
            self.assertEqual(actual,expected)
        self.assertEqual(w[:2],bytes((15,3)))
        self.assertEqual([struct.unpack_from('<BBH',w,100+4*i) for i in range(5)],[(15,15,54)]*3+[(15,15,55),(20,20,55)])
    def test_only_route6_header_and_encounter_archive_change(self):
        a=self.before.loadArm9();b=self.after.loadArm9();allowed={TABLE+14*24}
        allowed.update(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
        self.assertEqual(len(a.sections[0].data),len(b.sections[0].data))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
        for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
        fid=self.before.filenames.idOf('a/0/3/7')
        for i,(x,y) in enumerate(zip(self.before.files,self.after.files)):
            if i!=fid:self.assertEqual(x,y)
        old=ndspy.narc.NARC(self.before.files[fid]);new=ndspy.narc.NARC(self.after.files[fid])
        self.assertEqual(old.files,new.files[:-1])
        w=new.files[-1];template=old.files[self.report['original_wild']]
        self.assertEqual(w[2:8],template[2:8]);self.assertEqual(w[120:188],template[120:188]);self.assertEqual(w[192:],template[192:])
    def test_invalid_table_rejected(self):
        with self.assertRaises(ValueError):encounter_table(bytes(195))

if __name__=='__main__':unittest.main()
