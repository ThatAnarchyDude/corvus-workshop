"""The northern visual wall must leave all gameplay and stair openings intact."""
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom,ndspy.narc
from ndspy import _common
from build_rom import PROJECT
from route5_connected import patch_connected_probe
class NorthernCliff(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-native-fences-v1/private-terrain.nds'));cls.after=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0027-gates-development-v1.nds'));cls.report=patch_connected_probe(cls.after,json.loads((PROJECT/'build/0027-route5-walking-reference-v1/topology.json').read_text()),diagnostic=True,native_trees=True,visible_ledges=True,north_access=True,native_fences=True,north_wall=True)
 def test_only_art_changes(self):
  fid=self.before.filenames.idOf('a/0/6/5');self.assertEqual(self.before.arm9,self.after.arm9);self.assertEqual(self.before.arm7,self.after.arm7)
  for i,(a,b) in enumerate(zip(self.before.files,self.after.files)):
   if i!=fid:self.assertEqual(a,b)
  a=ndspy.narc.NARC(self.before.files[fid]);b=ndspy.narc.NARC(self.after.files[fid]);self.assertEqual(len(a.files),len(b.files))
  for x,y in zip(a.files,b.files):
   xp,xo,xm,xb,xt=struct.unpack_from('<5I',x);yp,yo,ym,yb,yt=struct.unpack_from('<5I',y);self.assertEqual((xp,xo,xb,xt),(yp,yo,yb,yt));self.assertEqual(x[20:20+xp+xo],y[20:20+yp+yo]);self.assertEqual(x[20+xp+xo+xm:],y[20+yp+yo+ym:])
 def test_wall_leaves_native_stair_openings_clear(self):
  a=ndspy.narc.NARC(self.after.files[self.after.filenames.idOf('a/0/6/5')]);raw=a.files[self.report['route_land']];ps,os,ms,_,_=struct.unpack_from('<5I',raw);b=raw[20+ps+os:20+ps+os+ms];mdl=struct.unpack_from('<I',b,16)[0];base=mdl+struct.unpack('<I',_common.loadInfoBlock(b,mdl+8,4)[0][3])[0];shape=base+struct.unpack_from('<I',b,base+12)[0];entry=shape+struct.unpack('<I',_common.loadInfoBlock(b,shape,4)[2][3])[0];off,size=struct.unpack_from('<2I',b,entry+8);data=b[entry+off:entry+off+size];at=0;vertices=[];counts={0:0,0x20:1,0x21:1,0x22:1,0x23:2,0x40:1,0x41:0}
  while at<len(data):
   ops=data[at:at+4];at+=4
   for op in ops:
    n=counts[op];v=struct.unpack_from('<'+'I'*n,data,at);at+=4*n
    if op==0x23:
     def signed(v):return v-65536 if v>=32768 else v
     vertices.append((signed(v[0]&65535),signed(v[0]>>16),signed(v[1]&65535)))
  wall=[vertices[i:i+4] for i in range(160,len(vertices),4)];self.assertEqual(len(wall),26)
  xs={16+v[0][0]/512 for v in wall};self.assertEqual(xs,set(range(32))-{11,12,13,26,27,28});self.assertTrue(all({p[2] for p in v}=={-8192} and {p[1] for p in v}=={0,512} for v in wall))
 def test_reproduces_private_probe(self):self.assertEqual(self.after.save(),(PROJECT/'build/0027-north-cliff-v2/private-terrain.nds').read_bytes())
if __name__=='__main__':unittest.main()
