"""Native legacy-gate compatibility modifies only appended Kanto scripts."""
import sys,json,struct,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from gate_save_compat import patch_gate_save_compatibility,compatibility_scripts
from parcel_quest import split_bank
from viridian_tutorial import TABLE
class GateCompatibility(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-small-gate-v7-anchors/private-small-gate.nds'));cls.after=ndspy.rom.NintendoDSRom(cls.before.save());cls.topology=json.loads((PROJECT/'build/0027-yellow-gate-topology-v1/topology.json').read_text());cls.report=patch_gate_save_compatibility(cls.after,cls.topology,diagnostic=True)
 def test_only_kanto_gate_script_header_changes(self):
  a=self.before.loadArm9();b=self.after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))|set(range(TABLE+391*24+6,TABLE+391*24+10))
  self.assertTrue(all(i in allowed for i,(u,v) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if u!=v))
  for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
  self.assertEqual(self.before.arm7,self.after.arm7);self.assertEqual(self.before.arm9OverlayTable,self.after.arm9OverlayTable)
  fid=self.before.filenames.idOf('a/0/1/2')
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i!=fid:self.assertEqual(a,b)
 def test_original_guard_scripts_and_members_preserved(self):
  fid=self.before.filenames.idOf('a/0/1/2');a=ndspy.narc.NARC(self.before.files[fid]);b=ndspy.narc.NARC(self.after.files[fid]);self.assertEqual(a.files,b.files[:len(a.files)]);self.assertEqual(len(b.files),len(a.files)+2)
  sid=struct.unpack_from('<H',self.before.loadArm9().sections[0].data,TABLE+391*24+6)[0];self.assertEqual(split_bank(a.files[sid]),split_bank(b.files[self.report['script']])[:2])
  self.assertEqual(self.report['temporary_variables'],[0x4000,0x4001]);self.assertFalse(self.report['new_story_flags'])
 def test_exact_private_compatibility_build_and_diagnostic_guard(self):
  expected=(PROJECT/'build/0027-small-gate-v8-save-compat/private-compatible-gate.nds').read_bytes();self.assertEqual(hashlib.sha256(expected).hexdigest(),hashlib.sha256(self.after.save()).hexdigest())
  with self.assertRaises(ValueError):patch_gate_save_compatibility(self.before,self.topology)
if __name__=='__main__':unittest.main()
