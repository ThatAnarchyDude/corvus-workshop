"""Owner-approved Route5 spacing reduction; preserve Yellow's functional features.

This produces a reference, not a released map. Connected HG terrain follows next.
"""
import copy
from collections import deque
REMOVE_ROWS=(2,14,16,34)
BUILDING_ROWS=set(range(18,22))|set(range(24,28))|set(range(30,34))
def compact_layout(source):
 if source['dimensions']!=[20,36]:raise ValueError('Expected original Yellow20x36 grid')
 if BUILDING_ROWS.intersection(REMOVE_ROWS):raise ValueError('Cannot remove building rows')
 if any(c['collision_tile']==0x52 and c['y'] in REMOVE_ROWS for c in source['cells']):raise ValueError('Cannot remove grass')
 if any(e['ledge'][1] in REMOVE_ROWS for e in source['one_way_ledges']):raise ValueError('Cannot remove ledges')
 if any(w['position'][1] in REMOVE_ROWS for w in source['warps']):raise ValueError('Cannot remove doors')
 rows=[y for y in range(36) if y not in REMOVE_ROWS];mapping={y:i for i,y in enumerate(rows)};out=copy.deepcopy(source)
 out.update(dimensions=[20,32],source_dimensions=[20,36],removed_spacing_rows=list(REMOVE_ROWS),scope='Private compact reference; owner permits shortening without losing Yellow intent')
 out['cells']=[]
 for c in source['cells']:
  if c['y'] in mapping:
   v=copy.deepcopy(c);v['source_position']=[c['x'],c['y']];v['y']=mapping[c['y']];out['cells'].append(v)
 out['one_way_ledges']=[]
 for e in source['one_way_ledges']:
  v=copy.deepcopy(e);x,y=e['ledge'];ny=mapping[y];v.update(start=[x,ny-1],ledge=[x,ny],landing=[x,ny+1]);out['one_way_ledges'].append(v)
 for w in out['warps']:w['source_position']=list(w['position']);w['position'][1]=mapping[w['position'][1]]
 cells={(v['x'],v['y']):v for v in out['cells']};walk={p for p,v in cells.items() if v['walkable']};jumps={tuple(v['start']):tuple(v['landing']) for v in out['one_way_ledges']};reachable={p for p in walk if p[1]==0};q=deque(reachable)
 while q:
  x,y=q.popleft();neighbors=[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
  if (x,y) in jumps:neighbors.append(jumps[x,y])
  for p in neighbors:
   if p in walk and p not in reachable:reachable.add(p);q.append(p)
 out['walkable_count']=len(walk);out['north_reachable_count']=len(reachable)
 for w in out['warps']:w['reachable_from_north']=tuple(w['position']) in reachable
 if [w['reachable_from_north'] for w in out['warps']]!=[w['reachable_from_north'] for w in source['warps']]:raise ValueError('Compaction changes gate/door reachability')
 out['sign_position']=[17,mapping[29]];out['row_mapping']=mapping
 return out
