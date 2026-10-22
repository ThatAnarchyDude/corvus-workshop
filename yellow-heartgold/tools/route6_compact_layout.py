"""Fit Yellow Route 6 into one connected HG cell by shortening repeated rows.

Keep every grass tile, trainer, door and ledge. One repeated pond row is
shortened, retaining both water regions and their shores. This is a reference
step; it does not change a ROM or replace any native interior.
"""
import copy
from collections import deque

REMOVE_ROWS=(0,5,9,34)

def water_regions(cells):
    remaining={(c['x'],c['y']) for c in cells if c['collision_tile']==0x14};sizes=[]
    while remaining:
        start=remaining.pop();queue=deque([start]);size=1
        while queue:
            x,y=queue.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in remaining:remaining.remove(p);queue.append(p);size+=1
        sizes.append(size)
    return sorted(sizes)

def compact_layout(source,trainers):
    if source['map']!='Route6' or source['dimensions']!=[20,36]:raise ValueError('Expected Yellow Route 6 20x36')
    if len(trainers)!=6:raise ValueError('Expected all six Yellow trainers')
    cells={(c['x'],c['y']):c for c in source['cells']}
    protected={w['position'][1] for w in source['warps']}|{t['yellow_position'][1] for t in trainers}|{15}
    for e in source['one_way_ledges']:protected.update(e[k][1] for k in ('start','ledge','landing'))
    if protected.intersection(REMOVE_ROWS):raise ValueError('Cannot shorten an event, trainer, sign or ledge landing row')
    for y in REMOVE_ROWS:
        neighbor=1 if y==0 else y-1
        for x in range(20):
            a,b=cells[x,y],cells[x,neighbor]
            if a['collision_tile']==0x52:raise ValueError('Cannot remove grass')
            if (a['collision_tile'],a['walkable'])!=(b['collision_tile'],b['walkable']):raise ValueError('Only repeated spacing rows may be shortened')
    mapping={y:i for i,y in enumerate(y for y in range(36) if y not in REMOVE_ROWS)}
    out=copy.deepcopy(source);out.update(dimensions=[20,32],source_dimensions=[20,36],removed_spacing_rows=list(REMOVE_ROWS),row_mapping=mapping)
    out['cells']=[]
    for c in source['cells']:
        if c['y'] in mapping:
            v=copy.deepcopy(c);v['source_position']=[c['x'],c['y']];v['y']=mapping[c['y']];out['cells'].append(v)
    for e in out['one_way_ledges']:
        for k in ('start','ledge','landing'):e[k][1]=mapping[e[k][1]]
        if e['landing'][1]-e['start'][1]!=2:raise ValueError('Ledge jump distance changed')
    for w in out['warps']:w['source_position']=list(w['position']);w['position'][1]=mapping[w['position'][1]]
    out['trainers']=copy.deepcopy(trainers)
    for t in out['trainers']:t['position']=[t['yellow_position'][0],mapping[t['yellow_position'][1]]]
    out['sign_position']=[19,mapping[15]]
    walk={(c['x'],c['y']) for c in out['cells'] if c['walkable']}
    jumps={tuple(e['start']):tuple(e['landing']) for e in out['one_way_ledges']}
    reachable={p for p in walk if p[1]==0};queue=deque(reachable)
    while queue:
        x,y=queue.popleft();neighbors=[(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
        if (x,y) in jumps:neighbors.append(jumps[x,y])
        for p in neighbors:
            if p in walk and p not in reachable:reachable.add(p);queue.append(p)
    for w in out['warps']:w['reachable_from_north']=tuple(w['position']) in reachable
    if [w['reachable_from_north'] for w in out['warps']]!=[w['reachable_from_north'] for w in source['warps']]:raise ValueError('Gate and door reachability changed')
    out['walkable_count']=len(walk);out['north_reachable_count']=len(reachable)
    before=water_regions(source['cells']);after=water_regions(out['cells'])
    if len(before)!=len(after) or not all(after):raise ValueError('Water region removed or split')
    out['water_region_sizes']={'original':before,'compact':after}
    out['scope']='Approved spacing reduction reference only; pond height shortened by one repeated row. No ROM change.'
    return out
