"""Read-only Yellow map layout extraction for Kanto DS reconstruction.

Extracted graphics/layouts are local reference material, never release assets.
Outputs must remain under the project's ignored build directory.
"""
import argparse,hashlib,json,re
from pathlib import Path
from PIL import Image
from build_rom import PROJECT

def source_tileset(source,map_name,token):
    header=(source/f'data/maps/headers/{map_name}.asm').read_text()
    declared=re.search(r'map_header\s+'+re.escape(map_name)+r',\s*'+re.escape(token)+r',\s*([A-Z0-9_]+)',header)
    if not declared:raise ValueError('Missing matching map header / tileset')
    tileset=declared.group(1)
    normalize=lambda name:re.sub(r'[^a-z0-9]','',name.lower())
    candidates=[p.stem for p in (source/'gfx/blocksets').glob('*.bst') if normalize(p.stem)==normalize(tileset)]
    if len(candidates)!=1:raise ValueError(f'Cannot uniquely resolve source tileset {tileset}')
    stem=candidates[0]
    return tileset,stem

def read_layout(source,map_name):
    if not re.fullmatch(r'[A-Za-z0-9]+',map_name):raise ValueError('Invalid map name')
    dims=(source/'constants/map_constants.asm').read_text()
    # Map constants use UPPER_CASE names; filenames use CamelCase.
    token=re.sub(r'(?<=[a-z0-9])(?=[A-Z])','_',map_name).upper()
    token=re.sub(r'(?<=[A-Z])(?=[0-9])','_',token)
    match=re.search(r'map_const\s+'+re.escape(token)+r',\s*(\d+),\s*(\d+)',dims)
    if not match:raise ValueError(f'Missing dimensions for {token}')
    width,height=map(int,match.groups());raw=(source/'maps'/f'{map_name}.blk').read_bytes()
    if len(raw)!=width*height:raise ValueError('Block count differs from map dimensions')
    _,stem=source_tileset(source,map_name,token)
    block_path=f'gfx/blocksets/{stem}.bst';tile_path=f'gfx/tilesets/{stem}.png'
    blockset=(source/block_path).read_bytes()
    if len(blockset)%16 or max(raw)*16+16>len(blockset):raise ValueError('Invalid source tileset block IDs')
    tiles=Image.open(source/tile_path).convert('RGB')
    if tiles.width%8 or tiles.height%8:raise ValueError('Invalid source tile sheet')
    canvas=Image.new('RGB',(width*32,height*32))
    cells=[];columns=tiles.width//8
    for by in range(height):
        for bx in range(width):
            block=blockset[raw[by*width+bx]*16:raw[by*width+bx]*16+16]
            for i,tile in enumerate(block):
                tx,ty=tile%columns*8,tile//columns*8
                if ty+8>tiles.height:raise ValueError('Tile exceeds source graphics')
                canvas.paste(tiles.crop((tx,ty,tx+8,ty+8)),(bx*32+i%4*8,by*32+i//4*8))
            for y in range(2):
                for x in range(2):
                    at=y*8+x*2
                    cells.append(dict(x=bx*2+x,y=by*2+y,block=raw[by*width+bx],tiles=[block[at],block[at+1],block[at+4],block[at+5]]))
    inputs=['constants/map_constants.asm',f'maps/{map_name}.blk',block_path,tile_path,f'data/maps/headers/{map_name}.asm',f'data/maps/objects/{map_name}.asm']
    manifest=dict(map=map_name,blocks=[width,height],logical_tiles=[width*2,height*2],
        source_sha256={f:hashlib.sha256((source/f).read_bytes()).hexdigest() for f in inputs},
        cells=sorted(cells,key=lambda c:(c['y'],c['x'])),
        connections_source=(source/f'data/maps/headers/{map_name}.asm').read_text(),
        events_source=(source/f'data/maps/objects/{map_name}.asm').read_text(),
        collision_status='Not yet translated to DS permissions; do not infer walkability from rendered colors.')
    return manifest,canvas

def main():
    p=argparse.ArgumentParser();p.add_argument('--yellow-source',type=Path,required=True)
    p.add_argument('--map',default='Route5');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();private=(PROJECT/'build').resolve()
    if not out.is_relative_to(private):p.error('Reference outputs must stay in ignored build storage')
    if out.exists():p.error('Use a new output directory to preserve references')
    data,image=read_layout(a.yellow_source,a.map);out.mkdir(parents=True)
    (out/'layout.json').write_text(json.dumps(data,indent=2)+'\n');image.save(out/'yellow-layout.png')
    print(json.dumps({k:data[k] for k in ('map','blocks','logical_tiles','collision_status')}))
if __name__=='__main__':main()
