"""Isolated S.S. Anne room-copy experiment; not connected to the campaign.

Slots254/255 are unreachable Sinnoh placeholders, not existing Johto rooms.
Shared native geometry stays read-only. Only appended private events, scripts
and matrices are used. Boarding, story, names and rewards remain unfinished.
"""
import struct,json
from pathlib import Path
import ndspy.narc
from opening import events_decode,events_encode,script_bank,command
from viridian_tutorial import TABLE
CLONES=((254,307),(255,308))
def patch(rom):
 main=rom.loadArm9();d=main.sections[0].data=bytearray(main.sections[0].data)
 paths=('a/0/1/2','a/0/3/2','a/0/4/1');scripts,events,matrices=[ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
 audit=json.loads(Path('yellow-heartgold/build/0030-ship-map-slots-audit-v1/audit.json').read_text())
 assert not audit['inbound_native_warps'] and not audit['map_matrix_references'] and not audit['raw_unparsed_warp_matches'] and not audit['available_native_source_symbol_references']
 ns=len(scripts.files);scripts.files.append(script_bank([command(2)]));ni=len(scripts.files);scripts.files.append(b'\0')
 reports=[]
 for target,donor in CLONES:
  rec=TABLE+target*24;old=bytes(d[rec:rec+24]);source=bytes(d[TABLE+donor*24:TABLE+(donor+1)*24])
  reference=next(h for h in audit['candidate_header_records'] if h['map']==target)
  assert old.hex()==reference['header'] and reference['actors']==0 and not reference['warps']
  row=bytearray(source);matrix=struct.unpack_from('<H',row,4)[0];raw=bytearray(matrices.files[matrix]);w,h,heads,alts,n=raw[:5]
  if heads:
   for cell in range(w*h):
    at=5+n+cell*2;mid=struct.unpack_from('<H',raw,at)[0]
    assert mid in (donor,0,0xFFFF),('unexpected owned matrix map',donor,mid)
    if mid==donor:struct.pack_into('<H',raw,at,target)
  nm=len(matrices.files);matrices.files.append(bytes(raw))
  # Only the paired native captain doorway is active; no native Aqua exits.
  native_event=struct.unpack_from('<H',row,16)[0];g=events_decode(events.files[native_event])
  if target==254:
   warps=[x for x in g[2] if struct.unpack_from('<H',x,4)[0]==308];assert len(warps)==1
   warp=bytearray(warps[0]);struct.pack_into('<2H',warp,4,255,0)
  else:
   assert len(g[2])==1;warp=bytearray(g[2][0]);struct.pack_into('<2H',warp,4,254,0)
  ne=len(events.files);events.files.append(events_encode([[],[],[bytes(warp)],[]]))
  struct.pack_into('<3H',row,4,nm,ns,ni);struct.pack_into('<H',row,16,ne)
  # These clones belong to Kanto. Native shared ship header/region stays unchanged.
  flags=struct.unpack_from('<I',row,20)[0];struct.pack_into('<I',row,20,flags|1)
  d[rec:rec+24]=row
  reports.append({'map':target,'donor':donor,'old_placeholder_header':old.hex(),'matrix':nm,'events':ne,'script':ns,'init':ni,'active_warp':list(struct.unpack('<6H',warp)),'temporary_native_aqua_map_section':True})
 for p,arc in zip(paths,(scripts,events,matrices)):rom.files[rom.filenames.idOf(p)]=arc.save()
 rom.arm9=main.save(compress=True)
 return {'clones':reports,'isolated_experiment':True,'campaign_connected':False,'native_aqua_resources_preserved':True,'boarding_story_names_rewards_pending':True}