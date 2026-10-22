"""Check clone-only mirror repair and required native model metadata alignment."""
import unittest,sys,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from route5_mirror_materials import patch_probe_mirror_materials,double_sided_model
from viridian_tutorial import TABLE
from build_rom import PROJECT
class MirrorMaterials(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-route5-native-scenery-v1/route5-native-scenery-probe.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.report=patch_probe_mirror_materials(cls.after,diagnostic=True)
 def arc(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)])
 def test_model_clones_change_only_material_culling_and_keep_metadata_aligned(self):
  a=self.arc(self.before,'a/0/4/0');b=self.arc(self.after,'a/0/4/0');meta=self.arc(self.after,'a/1/0/7');originalmeta=self.arc(self.before,'a/1/0/7')
  self.assertEqual(len(b.files),len(meta.files))
  for old,new in self.report['model_remap'].items():
   expected,changes=double_sided_model(a.files[old]);self.assertEqual(b.files[new],expected);self.assertEqual(meta.files[new],originalmeta.files[old]);allowed=set()
   for at,previous,value in changes:self.assertEqual(value,previous|0xc0);allowed.update(range(at,at+4))
   self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.files[old],b.files[new])) if x!=y))
 def test_kanto_area_preserves_textures_lighting_and_only_remaps_three_models(self):
  before=self.arc(self.before,'a/0/4/2').files[13];after=self.arc(self.after,'a/0/4/2').files[self.report['area']];self.assertEqual(before[2:],after[2:])
  self.assertEqual(self.arc(self.after,'a/0/7/0').files[self.report['model_list']],self.arc(self.before,'a/0/7/0').files[struct.unpack_from('<H',before)[0]])
  source=self.arc(self.before,'a/0/4/3').files[struct.unpack_from('<H',before)[0]];new=self.arc(self.after,'a/0/4/3').files[self.report['model_list']]
  oldids=struct.unpack('<'+'H'*(len(source)//2),source);newids=struct.unpack('<'+'H'*(len(new)//2),new)
  self.assertEqual(newids,(oldids[0],)+tuple(self.report['model_remap'].get(v,v) for v in oldids[1:]))
 def test_original_archives_code_and_all_johto_headers_unchanged(self):
  paths=('a/0/4/0','a/0/4/2','a/0/4/3','a/0/4/1','a/0/6/5','a/1/0/7','a/0/7/0');ids={self.before.filenames.idOf(p) for p in paths}|{self.before.filenames.idOf('fielddata/build_model/bm_field_matshp.dat')}
  for p in paths:self.assertEqual(self.arc(self.before,p).files,self.arc(self.after,p).files[:len(self.arc(self.before,p).files)])
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i not in ids:self.assertEqual(a,b)
  a=self.before.loadArm9();b=self.after.loadArm9();allowed={TABLE+13*24+1,TABLE+13*24+4,TABLE+13*24+5}|set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
  self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable);self.assertEqual(self.before.arm7,self.after.arm7)
 def test_original_shape_lookups_and_payload_are_preserved(self):
  fid=self.before.filenames.idOf('fielddata/build_model/bm_field_matshp.dat');a=self.before.files[fid];b=self.after.files[fid];count,shapes=struct.unpack_from('<2H',a);newcount,newshapes=struct.unpack_from('<2H',b)
  self.assertEqual((newcount,newshapes),(count+3,shapes));self.assertEqual(a[4:4+count*4],b[4:4+count*4]);self.assertEqual(a[4+count*4:],b[4+newcount*4:])
  for old,new in self.report['model_remap'].items():self.assertEqual(a[4+old*4:8+old*4],b[4+new*4:8+new*4])
 def test_land_changes_only_prop_model_identifiers(self):
  d=self.before.loadArm9().sections[0].data;matrix=self.arc(self.before,'a/0/4/1').files[struct.unpack_from('<H',d,TABLE+13*24+4)[0]]
  for old,new in zip(struct.unpack_from('<2H',matrix,5),self.report['lands']):
   a=self.arc(self.before,'a/0/6/5').files[old];b=self.arc(self.after,'a/0/6/5').files[new];ps,os=struct.unpack_from('<2I',a);allowed=set()
   for at in range(20+ps,20+ps+os,48):
    model=struct.unpack_from('<I',a,at)[0]
    if model in self.report['model_remap']:allowed.update(range(at,at+4));self.assertEqual(struct.unpack_from('<I',b,at)[0],self.report['model_remap'][model])
   self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a,b)) if x!=y));self.assertEqual(len(a),len(b))
 def test_matches_native_probe_and_rejects_implicit_correction(self):
  target=PROJECT/'build/0027-route5-native-scenery-v5/route5-native-scenery-probe.nds';self.assertEqual(hashlib.sha256(self.after.save()).hexdigest(),hashlib.sha256(target.read_bytes()).hexdigest())
  with self.assertRaises(ValueError):patch_probe_mirror_materials(self.before)
if __name__=='__main__':unittest.main()
