import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import ndspy.rom,ndspy.narc,ndspy.texture
from ndspy import _common
from route6_seam_textures import patch,MAPS
from viridian_tutorial import TABLE
class SeamTextures(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile("yellow-heartgold/build/0029-underground-ricky-v5/private-ricky-trade.nds")
  cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)
 def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
 def test_only_cloned_graphics_headers(self):
  allowed={self.old.filenames.idOf(p) for p in ("a/0/4/2","a/0/4/4")}
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in allowed:self.assertEqual(a,b)
  self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
  a=self.old.loadArm9();b=self.new.loadArm9()
  self.assertEqual(a.sections[1].data,b.sections[1].data)
  self.assertEqual(struct.unpack_from("<I",b.sections[0].data,b.codeSettingsOffs+20)[0],0x2000000+len(self.new.arm9))
  changed={TABLE+mid*24+1 for mid in MAPS}|set(range(b.codeSettingsOffs+20,b.codeSettingsOffs+24))
  self.assertFalse([i for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y and i not in changed])
  for p in ("a/0/4/2","a/0/4/4"):
   old=self.arc(self.old,p);new=self.arc(self.new,p);self.assertEqual(old.files,new.files[:len(old.files)])
 def test_original_graphics_payloads_and_missing_names(self):
  arc=self.arc(self.new,"a/0/4/4");original=ndspy.texture.NSBTX(arc.files[11]);combined=ndspy.texture.NSBTX(arc.files[self.report["new_texture_bank"]])
  for kind in ("textures","palettes"):
   b=dict(getattr(combined,kind))
   for n,v in getattr(original,kind):
    aa={k:x for k,x in v.__dict__.items() if k not in ("unk00","unk02")};bb={k:x for k,x in b[n].__dict__.items() if k not in ("unk00","unk02")}
    self.assertEqual(aa,bb,n)
  self.assertEqual(set(self.report["added"]["textures"]),{"wall01_h","ymb_hole","ymb_shouka"})
 def test_serialized_patricia_lookup(self):
  raw=self.arc(self.new,"a/0/4/4").files[self.report["new_texture_bank"]];at=struct.unpack_from("<I",raw,16)[0];block=raw[at:];vals=struct.unpack_from("<IHH3IHH4IHH2I",block,8)
  for off,width in [(vals[2],8),(vals[14],4)]:
   entries=_common.loadInfoBlock(block,off,width);nodes=[tuple(block[off+8+4*i:off+12+4*i]) for i in range(len(entries)+1)]
   self.assertEqual(nodes[0],(127,1,0,0))
   for expected,(name,*_) in enumerate(entries):
    key=int.from_bytes(name.encode("latin1").ljust(16,b"\0"),"little");parent=0;child=1;seen=set()
    while nodes[parent][0]>nodes[child][0]:
     self.assertNotIn(child,seen);seen.add(child)
     parent,child=child,nodes[child][2 if (key>>nodes[child][0])&1 else 1]
    self.assertEqual(nodes[child][3],expected,name)
if __name__=="__main__":unittest.main()