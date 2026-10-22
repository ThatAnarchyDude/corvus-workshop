"""Derive Yellow walking/ledge topology for a private DS terrain reference."""
import argparse,re,json,hashlib
from pathlib import Path
from collections import deque
from PIL import Image,ImageDraw
from yellow_layout_reference import read_layout,source_tileset
from build_rom import PROJECT

def topology(source,map_name):
 layout,reference=read_layout(source,map_name)
 collision=(source/'data/tilesets/collision_tile_ids.asm').read_text()
 token=re.sub(r'(?<=[a-z0-9])(?=[A-Z])','_',map_name).upper();token=re.sub(r'(?<=[A-Z])(?=[0-9])','_',token)
 tileset,stem=source_tileset(source,map_name,token)
 normalize=lambda name:re.sub(r'[^a-z0-9]','',name.lower())
 labels=[m for m in re.finditer(r'([A-Za-z0-9]+)_Coll::\s*',collision) if normalize(m[1])==normalize(tileset)]
 if len(labels)!=1:raise ValueError('Missing unique source collision label')
 matches=re.match(r'(?:[A-Za-z0-9]+_Coll::\s*)*coll_tiles ([^\n]+)',collision[labels[0].end():])
 if not matches:raise ValueError('Missing source passable tile table')
 passable={int(v,16) for v in re.findall(r'\$([0-9a-fA-F]+)',matches[1])}
 if re.search(r'db\s+'+re.escape(tileset)+r'\s*,', (source/'data/tilesets/pair_collision_tile_ids.asm').read_text()):raise ValueError('Unhandled source tileset elevation-pair exception')
 w,h=layout['logical_tiles'];cells={(c['x'],c['y']):dict(c,collision_tile=c['tiles'][2],walkable=c['tiles'][2] in passable) for c in layout['cells']}
 ledges=[];rules=[]
 for direction,a,b in (re.findall(r'db SPRITE_FACING_(DOWN|UP|LEFT|RIGHT),\s*\$([0-9a-fA-F]+),\s*\$([0-9a-fA-F]+)',(source/'data/tilesets/ledge_tiles.asm').read_text()) if tileset=='OVERWORLD' else []):
  delta={'DOWN':(0,1),'UP':(0,-1),'LEFT':(-1,0),'RIGHT':(1,0)}[direction];rules.append((delta,int(a,16),int(b,16)))
 adjacency={p:[] for p,c in cells.items() if c['walkable']}
 for p,c in cells.items():
  if not c['walkable']:continue
  x,y=p
  for dx,dy in ((0,1),(0,-1),(-1,0),(1,0)):
   q=(x+dx,y+dy)
   if q in adjacency:adjacency[p].append(q)
  for (dx,dy),stand,ledge in rules:
   mid=(x+dx,y+dy);dest=(x+2*dx,y+2*dy)
   if c['collision_tile']==stand and mid in cells and cells[mid]['collision_tile']==ledge and dest in adjacency:
    adjacency[p].append(dest);ledges.append(dict(start=list(p),ledge=list(mid),landing=list(dest),one_way=True))
 warps=[]
 for x,y,destination,entry in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*([A-Z0-9_]+),\s*(\d+)',layout['events_source']):
  p=(int(x),int(y));assert p in cells
  warps.append(dict(position=list(p),destination=destination,entry=int(entry),walkable=cells[p]['walkable']))
 starts=[p for p in adjacency if p[1]==0];reachable=set(starts);queue=deque(starts)
 while queue:
  for q in adjacency[queue.popleft()]:
   if q not in reachable:reachable.add(q);queue.append(q)
 for v in warps:v['reachable_from_north']=tuple(v['position']) in reachable
 result=dict(map=map_name,dimensions=[w,h],passable_tiles=sorted(passable),cells=list(cells.values()),one_way_ledges=ledges,warps=warps,walkable_count=len(adjacency),north_reachable_count=len(reachable),scope='Walking topology only; excludes actors, external connections, Surf, Cut and DS permission translation',source_sha256=layout['source_sha256'])
 for f in ('data/tilesets/collision_tile_ids.asm','data/tilesets/ledge_tiles.asm','data/tilesets/pair_collision_tile_ids.asm','engine/gfx/sprite_oam.asm','engine/overworld/player_state.asm'):
  result['source_sha256'][f]=hashlib.sha256((source/f).read_bytes()).hexdigest()
 image=Image.new('RGB',(w*24,h*24),'#27303d');draw=ImageDraw.Draw(image)
 for (x,y),c in cells.items():
  color='#43855c' if c['walkable'] else '#27303d';draw.rectangle((x*24,y*24,x*24+22,y*24+22),fill=color)
 for ledge in ledges:
  x,y=ledge['ledge'];draw.rectangle((x*24+3,y*24+3,x*24+19,y*24+19),fill='#dcad48')
 for i,warp in enumerate(warps):
  x,y=warp['position'];draw.text((x*24+4,y*24+3),str(i+1),fill='white')
 return result,image
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--yellow-source',type=Path,required=True);p.add_argument('--map',default='Route5');p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
 if not out.is_relative_to((PROJECT/'build').resolve()) or out.exists():p.error('Use a new ignored build output directory')
 result,img=topology(a.yellow_source,a.map);out.mkdir(parents=True);(out/'topology.json').write_text(json.dumps(result,indent=2)+'\n');img.save(out/'walking-grid.png');print(json.dumps({k:result[k] for k in ('map','dimensions','walkable_count','north_reachable_count','one_way_ledges','warps')}))
