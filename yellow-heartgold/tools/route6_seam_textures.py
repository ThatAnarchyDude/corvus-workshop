"""Union native terrain textures for the seamless Route6/Saffron/Vermilion chain."""
import struct,copy
import ndspy.narc,ndspy.texture
from ndspy import _common
from viridian_tutorial import TABLE
from nitro_dictionary import rebuild_nodes
MAPS=(14,59,54)
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=("a/0/4/2","a/0/4/4");areas,tex=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 records={mid:bytearray(areas.files[d[TABLE+mid*24+1]]) for mid in MAPS}
 banks=sorted({struct.unpack_from("<H",a,2)[0] for a in records.values()});assert banks==[11,12]
 source=[ndspy.texture.NSBTX(tex.files[i]) for i in banks];combined=copy.deepcopy(source[0]);added={}
 for kind in ("textures","palettes"):
  entries=getattr(combined,kind);seen=dict(entries);added[kind]=[]
  for n,v in getattr(source[1],kind):
   if n in seen:
    # These fields are dictionary-node metadata, not graphics/texture parameters.
    old={k:x for k,x in seen[n].__dict__.items() if k not in ("unk00","unk02")}
    new={k:x for k,x in v.__dict__.items() if k not in ("unk00","unk02")}
    assert old==new,(kind,n)
   else:entries.append((n,copy.deepcopy(v)));seen[n]=v;added[kind].append(n)
 def palette_offsets(raw):
  at=struct.unpack_from("<I",raw,16)[0];block=raw[at:];values=struct.unpack_from("<IHH3IHH4IHH2I",block,8)
  return {name:struct.unpack_from("<H",header)[0]*8 for name,_,_,header in _common.loadInfoBlock(block,values[14],4)}
 offsets=[palette_offsets(tex.files[i]) for i in banks]
 rawbank=tex.files[banks[0]];rawat=struct.unpack_from("<I",rawbank,16)[0];rawblock=rawbank[rawat:];rawvals=struct.unpack_from("<IHH3IHH4IHH2I",rawblock,8)
 palette_data=bytearray(rawblock[rawvals[15]:rawvals[15]+rawvals[12]*8]);new_offsets=dict(offsets[0])
 for n,p in combined.palettes:
  if n in new_offsets:continue
  new_offsets[n]=len(palette_data);palette_data.extend(p.save()[-1])
 # Compressed4x4 blocks store offsets into the whole palette bank, independent
 # of the named palette binding. Keep bank11 offsets; relocate bank12 additions.
 ranges=sorted((off,n) for n,off in offsets[1].items())
 for n,t in combined.textures:
  if n not in added["textures"] or t.format!=ndspy.texture.TextureFormat.TEXELED:continue
  raw=bytearray(t.data2)
  for at in range(0,len(raw),2):
   word=struct.unpack_from("<H",raw,at)[0];off=(word&0x3fff)*4
   start,palname=max((start,palname) for start,palname in ranges if start<=off)
   moved=new_offsets[palname]+off-start;assert moved%4==0 and moved//4<0x4000
   struct.pack_into("<H",raw,at,(word&0xc000)|(moved//4))
  t.data2=bytes(raw)
 for kind in ("textures","palettes"):rebuild_nodes(getattr(combined,kind))
 saved=bytearray(combined.save());txat=struct.unpack_from("<I",saved,16)[0];block=bytearray(saved[txat:]);vals=list(struct.unpack_from("<IHH3IHH4IHH2I",block,8));palinfo=vals[14]
 count=block[palinfo+1];entryat=palinfo+12+4*count+4
 assert count==len(combined.palettes)
 for i,(name,_) in enumerate(combined.palettes):struct.pack_into("<H",block,entryat+4*i,new_offsets[name]//8)
 block[vals[15]:]=palette_data;vals[12]=len(palette_data)//8
 struct.pack_into("<IHH3IHH4IHH2I",block,8,*vals);struct.pack_into("<I",block,4,len(block))
 saved[txat:]=block;struct.pack_into("<I",saved,8,len(saved))
 newbank=len(tex.files);tex.files.append(bytes(saved));newareas={}
 for mid,a in records.items():
  struct.pack_into("<H",a,2,newbank);idx=len(areas.files);assert idx<256
  areas.files.append(bytes(a));d[TABLE+mid*24+1]=idx;newareas[mid]=idx
 for p,arc in zip(paths,(areas,tex)):rom.files[rom.filenames.idOf(p)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {"maps":list(MAPS),"native_source_banks":banks,"new_texture_bank":newbank,"new_areas":newareas,"added":added,"no_geometry_or_gameplay_edits":True,"native_render_validation_pending":True}