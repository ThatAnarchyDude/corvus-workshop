import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from underground_path_yellow import patch
from viridian_tutorial import TABLE
from opening import events_decode

class UndergroundPathYellow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0029-route6-foundation-v1/private-route6-foundation.nds'))
        cls.after=ndspy.rom.NintendoDSRom(cls.before.save());patch(cls.after)
    def test_no_geometry_shared_archive_or_johto_changes(self):
        paths=('a/0/1/2','a/0/2/7','a/0/3/2');ids={self.before.filenames.idOf(p) for p in paths}
        for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
            if i not in ids:self.assertEqual(a,b)
        for p in paths:
            fid=self.before.filenames.idOf(p);a=ndspy.narc.NARC(self.before.files[fid]);b=ndspy.narc.NARC(self.after.files[fid])
            self.assertEqual(a.files,b.files[:len(a.files)])
        a=self.before.loadArm9();b=self.after.loadArm9()
        allowed=set(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
        for m in (470,532):allowed.update(range(TABLE+m*24,TABLE+(m+1)*24))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
        for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
    def test_all_warps_and_hidden_items_retained(self):
        def groups(rom,m):
            d=rom.loadArm9().sections[0].data;arc=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
            return events_decode(arc.files[struct.unpack_from('<H',d,TABLE+m*24+16)[0]])
        for m in (470,532):
            a=groups(self.before,m);b=groups(self.after,m)
            for i in (0,2,3):self.assertEqual(a[i],b[i])
        self.assertEqual(groups(self.after,532)[1],[])
        girl=groups(self.after,470)[1];self.assertEqual(len(girl),1)
        self.assertEqual(struct.unpack_from('<2H',girl[0],24),(3,5))

if __name__=='__main__':unittest.main()
