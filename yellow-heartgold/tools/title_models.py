"""Original low-poly Psyduck geometry and compact Nitro model/animation writers.

The models are generated here rather than extracted from a Nintendo archive.
Coordinates use DS fixed point. Joints and motion are indexed consistently.
"""
import math
import struct
from ndspy import _common, texture


def info(names, values):
    return _common.saveInfoBlock([(name,0,1,value) for name,value in zip(names,values)],4)


def container(magic, blocks, version=1):
    header=16+4*len(blocks); offset=header; out=bytearray()
    for block in blocks:
        out.extend(struct.pack('<I',offset));offset+=len(block)
    return struct.pack('<4sHHIHH',magic,0xfeff,version,offset,16,len(blocks))+out+b''.join(blocks)


def single_block(magic, name, payload):
    dictionary=info([name],[struct.pack('<I',48)])
    return magic+struct.pack('<I',48+len(payload))+dictionary+payload


def rgb(c):
    return sum(max(0,min(31,round(v*31/255)))<<(5*i) for i,v in enumerate(c))


def fifo(commands):
    out=bytearray()
    for at in range(0,len(commands),4):
        batch=commands[at:at+4];out.extend(bytes([cmd for cmd,_ in batch]).ljust(4,b'\0'))
        for _,params in batch:
            for p in params:out.extend(struct.pack('<I',p&0xffffffff))
    return bytes(out)


def vertex(p):
    xyz=[round(v*4096)&65535 for v in p]
    return (0x23,[xyz[0]|xyz[1]<<16,xyz[2]])


def ellipsoid(center, radius, color, segments=12, rings=7):
    def point(i,j):
        lat=-math.pi/2+math.pi*j/rings;lon=2*math.pi*i/segments
        return tuple(center[k]+radius[k]*v for k,v in enumerate(
            (math.cos(lat)*math.cos(lon),math.sin(lat),math.cos(lat)*math.sin(lon))))
    tris=[]
    for j in range(rings):
        for i in range(segments):
            a,b,c,d=point(i,j),point(i+1,j),point(i+1,j+1),point(i,j+1)
            if j:tris.append((a,b,c,color))
            if j<rings-1:tris.append((a,c,d,color))
    return tris


def cone(start,end,radius,color):
    # Hair tufts point mostly upwards; a six-sided tapered strand.
    points=[(start[0]+radius*math.cos(i*math.pi/3),start[1],start[2]+radius*math.sin(i*math.pi/3)) for i in range(6)]
    return [(points[i],points[(i+1)%6],end,color) for i in range(6)]


def mesh(tris):
    cmds=[(0x29,[(31<<16)|0xc0]),(0x2a,[0]),(0x40,[0])]
    for a,b,c,color in tris:
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        length=math.sqrt(sum(x*x for x in normal)) or 1
        # Soft painted vertex colors give the native DS flat-shaded appearance.
        light=.74+.26*abs(sum(normal[i]*(-.3,.8,.5)[i] for i in range(3))/length)
        cmds.append((0x20,[rgb([v*light for v in color])]))
        cmds.extend(vertex(p) for p in (a,b,c))
    cmds.append((0x41,[]))
    return fifo(cmds)


def model(name, shapes, node_positions, *, scale=64, tex=None):
    node_names=['body','left_paddle','right_paddle','wake'][:len(node_positions)]
    node_dict=info(node_names,[struct.pack('<I',0)]*len(node_positions))
    # A translated identity node is 16 bytes; offsets are relative to nodeInfo.
    node_start=len(node_dict)
    node_dict=info(node_names,[struct.pack('<I',node_start+16*i) for i in range(len(node_positions))])
    nodes=b''.join(struct.pack('<HH3i',6,0,*[round(v*4096) for v in pos]) for pos in node_positions)
    sbc=bytearray([0x26,0,0,0,0,2,0,1])
    for i in range(len(shapes)):
        if i:sbc.extend([0x66,i,0,0,i,0])
        sbc.extend([4,0,0x0b,5,i,0x2b])
    sbc.extend([1]);sbc.extend(b'\0'*(-len(sbc)%4))
    # One material, optionally linked to a single indexed water texture.
    empty=info([],[])
    matdict=info(['paint'],[struct.pack('<I',4+40+2*len(empty))])
    mapping=empty
    if tex:
        # A mapping entry names the texture; its value locates a material-ID list.
        mapping=info(['water'],[struct.pack('<HBB',4+40+2*40,1,0)])
        matdict=info(['paint'],[struct.pack('<I',128)])
    material=struct.pack('<HH6I2H2H2I',0,44,0x7fff|0x8000|(0x7fff<<16),0,
        (31<<16)|0xc0,0xffffffff,(3<<26)|(5<<20)|(5<<23)|(3<<16) if tex else 0,
        0xffffffff,0,0x11cf if tex else 0x07cf,256 if tex else 0,256 if tex else 0,4096,4096)
    mats=struct.pack('<HH',4+len(matdict),4+len(matdict)+len(mapping))+matdict+mapping+mapping
    if tex:mats+=b'\0'*4 # material index zero, with alignment
    assert len(mats)==struct.unpack_from('<I',matdict,20)[0]
    mats+=material
    shdict=info([f'part{i}' for i in range(len(shapes))],[struct.pack('<I',0)]*len(shapes))
    at=len(shdict);offsets=[];pieces=bytearray()
    for shape in shapes:
        offsets.append(at);piece=struct.pack('<HHIII',0,16,0,16,len(shape))+shape
        pieces.extend(piece);at+=len(piece)
    shdict=info([f'part{i}' for i in range(len(shapes))],[struct.pack('<I',off) for off in offsets])
    offsets=[64+len(node_dict)+len(nodes)]
    offsets.append(offsets[0]+len(sbc));offsets.append(offsets[1]+len(mats));offsets.append(offsets[2]+len(shdict)+len(pieces))
    header=struct.pack('<5I8B2i4H6h2i',offsets[-1],*offsets,0,1,0,len(nodes)//16,1,len(shapes),len(nodes)//16,0,
        scale*4096,round(4096/scale),0,0,0,0,-4096,-4096,-4096,8192,8192,8192,scale*4096,round(4096/scale))
    mdl=header+node_dict+nodes+sbc+mats+shdict+pieces
    blocks=[single_block(b'MDL0',name,mdl)]
    if tex:
        tx=texture.NSBTX();tx.textures=[('water',tex[0])];tx.palettes=[('water',tex[1])]
        saved=tx.save();off=struct.unpack_from('<I',saved,16)[0];blocks.append(saved[off:])
    return container(b'BMD0',blocks,2)


def psyduck():
    yellow=(248,207,52);cream=(232,205,150);black=(35,31,31);white=(251,247,229)
    tris=ellipsoid((0,.17,-.04),(.43,.43,.39),yellow)
    tris+=ellipsoid((0,.84,.15),(.43,.42,.39),yellow,16,9)
    tris+=ellipsoid((0,.7,.60),(.35,.115,.275),cream,14,5)
    for x in [-.17,.17]:
        tris+=ellipsoid((x,.91,.48),(.14,.18,.058),white,10,5)
        tris+=ellipsoid((x,.92,.532),(.028,.061,.018),black,8,4)
    for x in [-.105,.105]:tris+=ellipsoid((x,.798,.72),(.023,.009,.025),black,6,3)
    for i in [-1,0,1]:tris+=cone((i*.055,1.235,.12),(i*.09,1.5-abs(i)*.05,.05),.018,black)
    tris+=ellipsoid((0,.19,-.46),(.17,.14,.18),yellow,8,5)
    paddles=[mesh(ellipsoid((0,0,0),(.12,.25,.14),yellow,8,5)) for _ in range(2)]
    wake=[]
    for factor,color in [(1,(191,240,246)),(1.18,(141,219,240)),(1.36,(163,230,242))]:
        for i in range(32):
            a=2*math.pi*i/32;b=2*math.pi*(i+1)/32
            def p(angle,f):return (.59*f*math.cos(angle),0,.52*f*math.sin(angle))
            aa,bb,cc,dd=p(a,factor),p(b,factor),p(b,factor-.025),p(a,factor-.025)
            wake.extend([(aa,bb,cc,color),(aa,cc,dd,color)])
    return model('Psyduck',[mesh(tris),*paddles,mesh(wake)],[(0,0,0),(-26,15,3),(26,15,3),(0,.6,0)])


def animation(name, centers, frames=120, water=False):
    n=len(centers);data_start=20+2*n;data_start+=-data_start%4
    curves=bytearray();samples=bytearray();offsets=[]
    for i,center in enumerate(centers):
        offsets.append(data_start+len(curves))
        # Three sampled translations, identity rotation and unit scale.
        curves.extend(struct.pack('<HBB',0x480,0,i))
        for axis in range(3):
            curves.extend(struct.pack('<II',frames<<16,0))
            seq=[]
            for f in range(frames):
                angle=2*math.pi*f/frames
                if water:delta=(0,0,256*f/frames)[axis]
                elif i==0:delta=(1.5*math.sin(angle),2.5*math.sin(angle),0)[axis]
                elif i==3:delta=(0,-2.5*math.sin(angle),0)[axis]
                else:delta=(0,2.5*math.sin(angle+(i-1)*math.pi),5*math.cos(angle+(i-1)*math.pi))[axis]
                seq.append(round((center[axis]+delta)*4096))
            samples.extend(struct.pack('<'+str(frames)+'i',*seq))
    base=data_start+len(curves)
    for i in range(n):
        for axis in range(3):struct.pack_into('<I',curves,i*28+8+axis*8,base+(i*3+axis)*frames*4)
    anm=struct.pack('<4sHHIII',b'J\0AC',frames,n,0,0,0)+struct.pack('<'+str(n)+'H',*offsets)
    anm+=b'\0'*(data_start-len(anm));anm+=curves+samples
    return container(b'BCA0',[single_block(b'JNT0',name,anm)])


def water_model(indexed):
    palette=indexed.getpalette();colors=[rgb(palette[i:i+3]) for i in range(0,48,3)]
    raw=bytes(indexed.getdata());packed=bytes(raw[i]|raw[i+1]<<4 for i in range(0,len(raw),2))
    tx=texture.Texture.fromFlags(0,1,True,True,False,False,256,256,texture.TextureFormat.I4,False,
        texture.TextureCoordinatesTransformationMode.NONE,0,packed,b'')
    pal=texture.Palette(0,1,0,struct.pack('<16H',*colors))
    cmds=[(0x20,[0x7fff]),(0x29,[(31<<16)|0xc0]),(0x40,[1])]
    for p,uv in zip([(-7,0,-7),(7,0,-7),(7,0,7),(-7,0,7)],[(-1792,-1792),(1792,-1792),(1792,1792),(-1792,1792)]):
        cmds.append((0x22,[(uv[0]*16&65535)|(uv[1]*16&65535)<<16]));cmds.append(vertex(p))
    cmds.append((0x41,[]))
    return model('Water',[fifo(cmds)],[(0,0,0)],scale=256,tex=(tx,pal))
