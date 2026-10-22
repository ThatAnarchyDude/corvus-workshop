import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import ndspy.rom,ndspy.narc
from underground_ricky_trade import patch
from viridian_tutorial import TABLE
from opening import events_decode
from prototype import decode_messages
class RickyTradeResources(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ndspy.rom.NintendoDSRom.fromFile("yellow-heartgold/build/0029-route6-fishing-v1/private-route6-fishing.nds")
  cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)
 def archive(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)])
 def test_other_resources_and_maps(self):
  allowed={self.old.filenames.idOf(p) for p in ("a/0/1/2","a/0/2/7","a/0/3/2","a/1/1/2")}
  for i,(a,b) in enumerate(zip(self.old.files,self.new.files)):
   if i not in allowed:self.assertEqual(a,b)
  self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
  a=self.old.loadArm9().sections[0].data;b=self.new.loadArm9().sections[0].data
  for mid in range(540):
   if mid!=469:self.assertEqual(a[TABLE+mid*24:TABLE+(mid+1)*24],b[TABLE+mid*24:TABLE+(mid+1)*24])
  for p in ("a/0/1/2","a/0/3/2"):
   old=self.archive(self.old,p);new=self.archive(self.new,p);self.assertEqual(old.files,new.files[:len(old.files)])
 def test_native_interior_and_warps(self):
  d=self.old.loadArm9().sections[0].data;eid=struct.unpack_from("<H",d,TABLE+469*24+16)[0]
  a=events_decode(self.archive(self.old,"a/0/3/2").files[eid]);b=events_decode(self.archive(self.new,"a/0/3/2").files[self.report["event"]])
  self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:])
  aa=bytearray(a[1][0]);bb=bytearray(b[1][0])
  aa[4:6]=bb[4:6];aa[10:12]=bb[10:12];self.assertEqual(aa,bb)
 def test_only_discarded_kanto_trade_and_names(self):
  a=self.archive(self.old,"a/1/1/2");b=self.archive(self.new,"a/1/1/2")
  for i in range(13):
   if i!=9:self.assertEqual(a.files[i],b.files[i])
  row=b.files[9];self.assertEqual(struct.unpack_from("<i",row,0)[0],67);self.assertEqual(struct.unpack_from("<i",row,76)[0],104)
  a=self.archive(self.old,"a/0/2/7");b=self.archive(self.new,"a/0/2/7")
  for i in range(len(a.files)):
   if i!=200:self.assertEqual(a.files[i],b.files[i])
  ka,na=decode_messages(a.files[200]);kb,nb=decode_messages(b.files[200]);self.assertEqual(ka,kb)
  for i in range(26):
   if i not in (9,22):self.assertEqual(na[i],nb[i])
if __name__=="__main__":unittest.main()