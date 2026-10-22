import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from route6_connected import patch,native_materials
from route5_connected import patch_connected_probe,matrix_offset
from opening import events_decode
from viridian_tutorial import TABLE

class Route6Connected(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0029-route6-trainers-v1/private-trainer-records.nds'))
        cls.layout=json.loads((PROJECT/'build/0029-route6-foundation-v1/compact-topology.json').read_text())
        cls.trainers=json.loads((PROJECT/'build/0029-route6-trainers-v1/report.json').read_text())
        cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch(cls.after,cls.layout,cls.trainers,diagnostic=True)
    def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
    def test_change_boundary_and_original_archive_members(self):
        paths=('a/0/4/1','a/0/6/5','a/0/3/2','a/0/4/2','a/0/4/3','a/0/7/0','a/0/1/2','a/0/2/7');ids={self.before.filenames.idOf(p) for p in paths}
        for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
            if i not in ids:self.assertEqual(a,b)
        for p in paths:
            a=self.arc(self.before,p);b=self.arc(self.after,p)
            if p!='a/0/4/1':self.assertEqual(a.files,b.files[:len(a.files)])
            else:
                at=matrix_offset(a.files[0],40,8)
                self.assertEqual(a.files[0][:at],b.files[0][:at]);self.assertEqual(a.files[0][at+2:],b.files[0][at+2:]);self.assertEqual(a.files[1:],b.files[1:])
        a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+0x14,a.codeSettingsOffs+0x18))
        allowed.update(range(TABLE+14*24,TABLE+15*24))
        for m in (389,470):allowed.update(range(TABLE+m*24+16,TABLE+m*24+18))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
    def test_water_actors_doors_and_native_materials(self):
        lands=self.arc(self.after,'a/0/6/5');raw=lands.files[self.report['land']];permissions=struct.unpack_from('<1024H',raw,20)
        self.assertEqual(sum(p==0x410 for p in permissions),73)
        self.assertEqual(sum(p==0x402 for p in permissions),sum(c['collision_tile']==82 for c in self.layout['cells']))
        d=self.after.loadArm9().sections[0].data;events=self.arc(self.after,'a/0/3/2');g=events_decode(events.files[struct.unpack_from('<H',d,TABLE+14*24+16)[0]])
        self.assertEqual(len(g[1]),6);self.assertEqual(len(g[2]),4)
        for a,t,b in zip(g[1],self.layout['trainers'],self.trainers['trainers']):
            self.assertEqual(struct.unpack_from('<2H',a,24),(1292+t['position'][0],256+t['position'][1]))
            self.assertEqual(struct.unpack_from('<H',a,10)[0],3000+b['id']-1)
            self.assertEqual(struct.unpack_from('<H',a,14)[0],t['vision'])
        m,bindings,count=native_materials(lands.files[130]);self.assertEqual(count,26);self.assertIn('pond_on',bindings)
        with self.assertRaises(ValueError):native_materials(bytes(100))
    def test_route5_reproduces_released_terrain_exactly(self):
        r=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'))
        source=json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text())
        patch_connected_probe(r,source,diagnostic=True,native_trees=True,visible_ledges=True,north_access=True,native_fences=True,north_wall=True)
        released=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0028-native-interiors-v1/Pokemon-Psyduck-Yellow-prototype-0028.nds'))
        def land(rom):
            m=self.arc(rom,'a/0/4/1').files[0];lid=struct.unpack_from('<H',m,matrix_offset(m,40,5))[0];return self.arc(rom,'a/0/6/5').files[lid]
        self.assertEqual(land(r),land(released))
    def test_city_links_preserve_city_models_and_collision_planes(self):
        r=ndspy.rom.NintendoDSRom(self.before.save());report=patch(r,self.layout,self.trainers,diagnostic=True,native_city_links=True)
        self.assertEqual(report['changed_main_cells'],[[40,8],[40,7]])
        m=self.arc(r,'a/0/4/1').files[0];newid=struct.unpack_from('<H',m,matrix_offset(m,40,7))[0]
        old=self.arc(self.before,'a/0/6/5').files[135];new=self.arc(r,'a/0/6/5').files[newid]
        self.assertEqual(len(old),len(new));allowed=set()
        for z in (29,30,31):
            for x in (21,22):allowed.update((20+2*(32*z+x),21+2*(32*z+x)))
        allowed.update((20+2*(32*29+20),21+2*(32*29+20)))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(old,new)) if x!=y))
        land=self.arc(r,'a/0/6/5').files[report['land']]
        for x in range(20,27):self.assertEqual(struct.unpack_from('<H',land,20+2*(31*32+x))[0],0x400)

if __name__=='__main__':unittest.main()
