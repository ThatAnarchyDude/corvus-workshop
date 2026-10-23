"""Verify Yellow encounter probabilities and the complete Kanto-only change boundary."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route5 import encounter_table,patch
from viridian_tutorial import TABLE
from opening import events_decode

class Route5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0025.nds'))
        cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after)
    def archive(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)])
    def test_exact_yellow_probabilities_all_periods(self):
        expected={(16,15):20,(19,14):20,(63,7):15,(16,16):10,(19,16):10,(16,17):10,(17,17):5,(39,3):5,(39,5):4,(39,7):1}
        d=self.after.loadArm9().sections[0].data
        w=self.archive(self.after,'a/0/3/7').files[d[TABLE+13*24]]
        for period in range(3):
            species=struct.unpack_from('<12H',w,20+24*period);actual={}
            for s,lv,weight in zip(species,w[8:20],(20,20,10,10,10,10,5,5,4,4,1,1)):
                actual[s,lv]=actual.get((s,lv),0)+weight
            self.assertEqual(actual,expected)
        self.assertEqual(w[0],15);self.assertEqual(w[1:6],bytes(5))
    def test_only_two_kanto_headers_and_no_shared_code_change(self):
        a=self.before.loadArm9();b=self.after.loadArm9()
        allowed=set(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
        self.assertEqual(struct.unpack_from('<I',b.sections[0].data,b.codeSettingsOffs+0x14)[0],b.ramAddress+len(self.after.arm9))
        for m in (13,517):allowed.update(range(TABLE+m*24,TABLE+(m+1)*24))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
        self.assertEqual(len(a.sections[0].data),len(b.sections[0].data))
        for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
        self.assertEqual(self.before.arm7,self.after.arm7)
        self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable)
    def test_all_old_members_and_unrelated_files_unchanged(self):
        paths=('a/0/1/2','a/0/2/7','a/0/3/2','a/0/3/7')
        ids={self.before.filenames.idOf(p) for p in paths}
        for p in paths:
            a=self.archive(self.before,p);b=self.archive(self.after,p)
            self.assertEqual(a.files,b.files[:len(a.files)])
        for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
            if i not in ids:self.assertEqual(a,b,f'Unexpected changed file {i}')
    def test_route5_has_no_npcs_trainers_or_coordinate_events(self):
        r=self.report['route'];g=events_decode(self.archive(self.after,'a/0/3/2').files[r['event']])
        self.assertEqual(g[1],[]);self.assertEqual(g[3],[])
        old=events_decode(self.archive(self.before,'a/0/3/2').files[r['original']['event']])
        self.assertEqual(g[2],old[2]);self.assertEqual(struct.unpack_from('<2H',g[0][0]),(1,0))
    def test_daycare_reuses_native_bank_and_text_without_johto_edits(self):
        r=self.report['daycare'];s=self.archive(self.after,'a/0/1/2');t=self.archive(self.after,'a/0/2/7')
        self.assertEqual(s.files[r['script']],s.files[265]);self.assertEqual(t.files[r['text']],t.files[439])
        g=events_decode(self.archive(self.after,'a/0/3/2').files[r['event']])
        self.assertEqual([struct.unpack_from('<H',x,10)[0] for x in g[1]],[1,2])
        self.assertTrue(r['shared_native_storage'])
    def test_bad_encounter_template_rejected(self):
        with self.assertRaises(ValueError):encounter_table(bytes(195))

if __name__=='__main__':unittest.main()
