import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route6_trainers import patch
from prototype import decode_messages

class Route6Trainers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0029-underground-foundation-v1/private-underground-foundation.nds'))
        cls.reference=json.loads((PROJECT/'build/0029-route6-foundation-v1/trainer-reference.json').read_text())
        cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after,cls.reference)
    def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
    def test_teams_moves_flags_and_blank_names(self):
        trainers=self.arc(self.after,'a/0/5/5');parties=self.arc(self.after,'a/0/5/6');names=decode_messages(self.arc(self.after,'a/0/2/7').files[729])[1]
        for entry in self.report['trainers']:
            tid=entry['id'];self.assertEqual(trainers.files[tid][3],len(entry['team']));self.assertEqual(names[tid],[0xFFFF])
            self.assertLess(entry['defeat_flag'],0xB60)
            rows=[struct.unpack_from('<BB3H4H',parties.files[tid],16*i) for i in range(len(entry['team']))]
            self.assertEqual([(r[2],r[3],list(r[5:])) for r in rows],[(m['level'],m['species'],m['moves']) for m in entry['team']])
    def test_original_records_interiors_and_map_headers_unchanged(self):
        paths=('a/0/1/2','a/0/2/7','a/0/5/5','a/0/5/6','a/0/5/7','a/1/3/1');ids={self.before.filenames.idOf(p) for p in paths}
        for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
            if i not in ids:self.assertEqual(a,b)
        for p in ('a/0/1/2','a/0/5/5','a/0/5/6'):
            a=self.arc(self.before,p);b=self.arc(self.after,p);self.assertEqual(a.files,b.files[:len(a.files)])
        for index in (728,729):
            a=decode_messages(self.arc(self.before,'a/0/2/7').files[index])[1];b=decode_messages(self.arc(self.after,'a/0/2/7').files[index])[1];self.assertEqual(a,b[:len(a)])
        a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
        for at in self.report['common_reference_sites']:allowed.update((at+2,at+3))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
        for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
    def test_original_common_aliases_keep_identical_bodies(self):
        arc=self.arc(self.after,'a/0/1/2');old=arc.files[self.report['original_common']];new=arc.files[self.report['common']]
        def count(b):
            n=0
            while struct.unpack_from('<H',b,n*4)[0]!=0xFD13:n+=1
            return n
        n=count(old);nn=count(new);growth=(nn-n)*4;self.assertEqual(old[n*4:],new[nn*4:])
        for i in range(n):self.assertEqual(struct.unpack_from('<I',new,4*i)[0],struct.unpack_from('<I',old,4*i)[0]+growth)

if __name__=='__main__':unittest.main()
