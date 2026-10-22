import unittest,sys,struct,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from build_rom import PROJECT
from opening import events_decode
from viridian_tutorial import TABLE
from kanto_cut_obstacles import cut_badge_helper
class CutAccessTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0032-release-package-v1/Pokemon-Psyduck-Yellow-prototype-0032.nds'))
  cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0033-cut-access-v1/private-cut-access.nds'))
  cls.report=json.loads((PROJECT/'build/0033-cut-access-v1/report.json').read_text())
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files
 def test_direct_cut_keeps_hive_and_accepts_cascade(self):
  code=cut_badge_helper()
  for mask in range(1<<16):
   pc=0;result=None;cmp=None
   for _ in range(12):
    op=struct.unpack_from('<H',code,pc)[0];pc+=2
    if op==294:
     badge,var=struct.unpack_from('<2H',code,pc);pc+=4;self.assertEqual(var,0x800C);result=(mask>>badge)&1
    elif op==17:
     var,value=struct.unpack_from('<2H',code,pc);pc+=4;self.assertEqual(var,0x800C);cmp=(result>value)-(result<value)
    elif op==28:
     condition=code[pc];offset=struct.unpack_from('<i',code,pc+1)[0];pc+=5;self.assertEqual(condition,5)
     if cmp!=0:pc+=offset
    elif op==27:break
    else:self.fail(f'Unexpected opcode {op}')
   else:self.fail('No return')
   self.assertEqual(result,int(bool(mask&((1<<1)|(1<<9)))))
 def test_restored_native_tree_and_no_other_city_changes(self):
  old=self.arc(self.old,'a/0/3/2');new=self.arc(self.new,'a/0/3/2');r=self.report
  a=events_decode(old[r['original_event']]);b=events_decode(new[r['event']])
  self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:]);self.assertEqual(a[1],b[1][:-1]);tree=b[1][-1]
  self.assertEqual(struct.unpack_from('<2H',tree),(11,86));self.assertEqual(struct.unpack_from('<2H',tree,24),(1300,319));self.assertEqual(struct.unpack_from('<H',tree,10)[0],10000)
  self.assertEqual(new[:len(old)],old)
 def test_original_field_scripts_and_relative_bodies_preserved(self):
  old=self.arc(self.old,'a/0/1/2');new=self.arc(self.new,'a/0/1/2');r=self.report;self.assertEqual(new[:len(old)],old)
  src=old[146];out=new[r['script']];at=r['call_offset'];target=r['helper_offset']
  self.assertEqual(struct.unpack_from('<H',out,at)[0],26);self.assertEqual(at+6+struct.unpack_from('<i',out,at+2)[0],target)
  self.assertEqual(out[target:],cut_badge_helper())
  oldhead=min(i*4+4+struct.unpack_from('<I',src,i*4)[0] for i in range(19));body=bytearray(out[oldhead+4:oldhead+4+len(src)-oldhead]);body[at-oldhead-4:at-oldhead+2]=src[at-4:at+2];self.assertEqual(body,src[oldhead:])
 def test_no_unrelated_map_files_or_executable_changes(self):
  allowed={self.old.filenames.idOf(p) for p in ('a/0/1/2','a/0/3/2')}
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in allowed:self.assertEqual(a,b,f'file {i}')
  for key in ('arm7','arm9OverlayTable','arm7OverlayTable','iconBanner'):self.assertEqual(getattr(self.old,key),getattr(self.new,key))
  old=self.old.loadArm9();new=self.new.loadArm9()
  for i,(a,b) in enumerate(zip(old.sections,new.sections)):
   if i:self.assertEqual(a.data,b.data)
   else:
    expected=bytearray(a.data);meta=old.codeSettingsOffs+20;expected[meta:meta+4]=b.data[meta:meta+4]
    for at,size in ((TABLE+54*24+16,2),(self.report['dispatch_offset']+2,2)):expected[at:at+size]=b.data[at:at+size]
    self.assertEqual(expected,b.data)
if __name__=='__main__':unittest.main()
