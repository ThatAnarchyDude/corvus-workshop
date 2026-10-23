"""Extract Yellow ship doorway requirements without changing source or ROMs."""
import argparse, hashlib, json, re
from pathlib import Path

ROOM_GROUPS = {'SS_ANNE_1F_ROOMS': 6, 'SS_ANNE_2F_ROOMS': 6, 'SS_ANNE_B1F_ROOMS': 5}

def extract(root):
    maps = {}
    for path in sorted(root.glob('SSAnne*.asm')):
        source = path.read_text()
        name = re.search(r'def_warps_to\s+(\w+)', source).group(1)
        warps = [dict(index=i+1, x=int(x), y=int(y), destination=dest, anchor=int(anchor))
                 for i, (x,y,dest,anchor) in enumerate(re.findall(r'^\s*warp_event\s+(\d+),\s*(\d+),\s*(\w+),\s*(\d+)', source, re.M))]
        maps[name] = dict(source=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), warps=warps)
    assert len(maps) == 10
    def node(name, warp):
        # Group adjacent exits by their shared hall destination, not by map ID.
        if name in ROOM_GROUPS:
            return f"{name}:cabin-to-{warp['destination']}-door-{warp['anchor']}"
        return name
    edges=[]
    for name, info in maps.items():
        if name in ROOM_GROUPS:
            assert len({node(name,w) for w in info['warps']}) == ROOM_GROUPS[name]
        for warp in info['warps']:
            dest=warp['destination']
            if dest not in maps:
                assert name == 'SS_ANNE_1F' and dest == 'VERMILION_DOCK'
                continue
            assert 1 <= warp['anchor'] <= len(maps[dest]['warps'])
            arrival=maps[dest]['warps'][warp['anchor']-1]
            assert arrival['destination'] == name, (name, warp, arrival)
            return_anchor=arrival['anchor']
            assert 1 <= return_anchor <= len(info['warps'])
            assert node(name, info['warps'][return_anchor-1]) == node(name,warp)
            edges.append(dict(source=node(name,warp), destination=node(dest,arrival), source_warp=warp['index'], destination_warp=warp['anchor']))
    reached={'SS_ANNE_1F'}
    while True:
        expanded=reached|{e['destination'] for e in edges if e['source'] in reached}
        if expanded == reached: break
        reached=expanded
    nodes={e[k] for e in edges for k in ('source','destination')}
    assert reached==nodes and len(nodes)==24
    assert 'SS_ANNE_CAPTAINS_ROOM' in reached
    return dict(source_maps=maps, directed_internal_doorways=edges, logical_room_count=len(nodes), cabin_count=17,
                all_logical_rooms_connected=True, native_walkability_verified=False,
                caveat='Source doorway requirements only. Hall connectivity is assumed from Yellow; native collision, arrival orientation, actors and campaign access require separate playtests.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('source',type=Path); parser.add_argument('output',type=Path)
    args=parser.parse_args(); result=extract(args.source)
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'topology.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_maps','directed_internal_doorways')}))
