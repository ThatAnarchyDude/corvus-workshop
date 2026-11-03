"""Builds the animated 3DS HOME-menu banner as a .glb (for CBC for YANBF, which converts it with pycgfx): the still banner picture on a flat panel, sparkles that twinkle (scale/turn) and a soft shine that sweeps across the lettering.

Layout follows CBC's rules: a root node COMMON holding `world` (an invisible stub; the HOME menu may spin it) and `name` (a billboard that always faces the camera) which carries the picture and every animated child.
The HOME menu's banner camera is at (0, 1, 44.786) looking down -Z with a 30 degree vertical field of view and aspect 5:3, so a panel at z = 0 shows 40 x 24 units; the picture (2:1) is 40 x 20 units centred at y = 1.
Only simple node animation (scale, rotation, translation) is used: the community reports that skinned animation froze real HOME menus.

Usage: make_banner_glb.py <banner without sparkles.png (256x128)> <out.glb>
"""
import json
import math
import struct
import sys
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

UNIT = 40 / 256                          # world units per picture pixel
R = 24                                   # the stone's radius in pixels (see make_banner.py: STONE)
SPARKLES = ((1.45, -0.95, 0.5), (-1.55, 0.75, 0.38), (1.65, 0.7, 0.28), (-1.3, -1.0, 0.26), (0.12, 1.22, 0.5), (0.48, -0.5, 0.55),
            (-0.95, 0.05, 0.17), (1.05, 0.1, 0.15), (-0.55, -1.2, 0.17), (0.7, 1.0, 0.15), (-0.35, 1.12, 0.14))
LENGTH, FPS = 3.0, 30


def png(img):
    b = BytesIO()
    img.save(b, 'PNG')
    return b.getvalue()


def star_texture():
    s = 8
    im = Image.new('RGBA', (32 * s, 32 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, q = 16 * s, 15 * s
    d.polygon([(c, c - q), (c + q * 0.16, c - q * 0.16), (c + q, c), (c + q * 0.16, c + q * 0.16), (c, c + q), (c - q * 0.16, c + q * 0.16), (c - q, c), (c - q * 0.16, c - q * 0.16)], fill=(255, 252, 235, 255))
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([c - q * 0.4, c - q * 0.4, c + q * 0.4, c + q * 0.4], fill=(255, 245, 200, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(3 * s))
    glow.alpha_composite(im)
    return glow.resize((32, 32), Image.LANCZOS)


def shine_texture():
    im = Image.new('RGBA', (32, 128), (255, 255, 255, 0))
    for x in range(32):
        a = max(0.0, math.sin(math.pi * x / 31)) ** 2
        for y in range(128):
            im.putpixel((x, y), (255, 255, 235, int(150 * a)))
    return im


def quad(w, h):
    x, y = w / 2, h / 2
    pos = [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)]
    uv = [(0, 1), (1, 1), (1, 0), (0, 0)]
    return pos, uv, [0, 1, 2, 0, 2, 3]


class Glb:
    def __init__(self):
        self.bin = bytearray()
        self.views, self.accessors, self.meshes, self.materials, self.images, self.textures, self.nodes = [], [], [], [], [], [], []
        self.samplers = [{'magFilter': 9729, 'minFilter': 9729, 'wrapS': 33071, 'wrapT': 33071}]

    def view(self, data, target=None):
        while len(self.bin) % 4:
            self.bin.append(0)
        v = {'buffer': 0, 'byteOffset': len(self.bin), 'byteLength': len(data)}
        if target:
            v['target'] = target
        self.bin += data
        self.views.append(v)
        return len(self.views) - 1

    def accessor(self, data, ctype, count, comp=5126, mm=None, target=None):
        a = {'bufferView': self.view(data, target), 'componentType': comp, 'count': count, 'type': ctype}
        if mm:
            a['min'], a['max'] = mm
        self.accessors.append(a)
        return len(self.accessors) - 1

    def image(self, img):
        self.images.append({'bufferView': self.view(png(img)), 'mimeType': 'image/png'})
        self.textures.append({'sampler': 0, 'source': len(self.images) - 1})
        return len(self.textures) - 1

    def material(self, name, tex, blend):
        m = {'name': name, 'pbrMetallicRoughness': {'baseColorTexture': {'index': tex}, 'metallicFactor': 0.0, 'roughnessFactor': 1.0}, 'doubleSided': True}
        if blend:
            m['alphaMode'] = 'BLEND'
        self.materials.append(m)
        return len(self.materials) - 1

    def mesh(self, name, w, h, material):
        pos, uv, idx = quad(w, h)
        P = self.accessor(b''.join(struct.pack('<3f', *p) for p in pos), 'VEC3', 4, mm=([min(p[i] for p in pos) for i in range(3)], [max(p[i] for p in pos) for i in range(3)]), target=34962)
        N = self.accessor(b''.join(struct.pack('<3f', 0, 0, 1) for _ in pos), 'VEC3', 4, target=34962)
        T = self.accessor(b''.join(struct.pack('<2f', *t) for t in uv), 'VEC2', 4, target=34962)
        I = self.accessor(struct.pack('<6H', *idx), 'SCALAR', 6, comp=5123, target=34963)
        self.meshes.append({'name': name, 'primitives': [{'attributes': {'POSITION': P, 'NORMAL': N, 'TEXCOORD_0': T}, 'indices': I, 'material': material}]})
        return len(self.meshes) - 1

    def node(self, **kw):
        self.nodes.append(kw)
        return len(self.nodes) - 1


def main(picture, out):
    g = Glb()
    base = g.mesh('nameModel', 40, 20, g.material('banner', g.image(Image.open(picture).convert('RGBA')), False))
    star_mat = g.material('sparkle', g.image(star_texture()), True)
    shine_mat = g.material('shine', g.image(shine_texture()), True)
    stub_mat = g.material('stub', g.image(Image.new('RGBA', (4, 4), (0, 0, 0, 0))), True)
    stub = g.mesh('worldModel', 0.01, 0.01, stub_mat)
    children, channels, samplers = [], [], []

    def animate(node, path, times, values, ctype):
        t = g.accessor(struct.pack('<%df' % len(times), *times), 'SCALAR', len(times), mm=([min(times)], [max(times)]))
        fmt = '<%df' % (len(values) * len(values[0]))
        v = g.accessor(struct.pack(fmt, *[c for row in values for c in row]), ctype, len(values))
        samplers.append({'input': t, 'output': v, 'interpolation': 'LINEAR'})
        channels.append({'sampler': len(samplers) - 1, 'target': {'node': node, 'path': path}})

    star = g.mesh('sparkle', 2, 2, star_mat)
    for i, (dx, dy, size) in enumerate(SPARKLES):
        px, py, q = 128 + dx * R, 65 + dy * R, size * R
        x, y = (px - 128) * UNIT, 1 + (64 - py) * UNIT
        n = g.node(name='sparkle%d' % i, mesh=star, translation=[x, y, 0.2], scale=[q * UNIT, q * UNIT, 1])
        children.append(n)
        # twinkle: grow from nothing, peak, shrink again, with its own start time; one full turn of 90 degrees
        start = (i * 0.37) % LENGTH
        keys = sorted({0.0, LENGTH, start, (start + 0.35) % LENGTH, (start + 0.7) % LENGTH})
        def s_at(t):
            u = ((t - start) % LENGTH) / 0.7
            return math.sin(math.pi * u) if u < 1 else 0.0
        animate(n, 'scale', keys, [[q * UNIT * max(0.001, s_at(t)), q * UNIT * max(0.001, s_at(t)), 1.0] for t in keys], 'VEC3')
        half = math.sin(math.radians(22.5))
        animate(n, 'rotation', [0.0, LENGTH / 2, LENGTH], [[0, 0, 0, 1], [0, 0, math.sin(math.radians(45)), math.cos(math.radians(45))], [0, 0, math.sin(math.radians(90)), math.cos(math.radians(90))]], 'VEC4')
    # shine: a soft band, tilted, moving left to right once per loop and staying inside the picture
    tilt = math.radians(-18)
    shine = g.mesh('shine', 7, 26, shine_mat)
    sn = g.node(name='shine', mesh=shine, translation=[-17, 1, 0.1], rotation=[0, 0, math.sin(tilt / 2), math.cos(tilt / 2)])
    children.append(sn)
    animate(sn, 'translation', [0.0, 0.5, LENGTH - 0.5, LENGTH], [[-17, 1, 0.1], [-17, 1, 0.1], [17, 1, 0.1], [17, 1, 0.1]], 'VEC3')
    name = g.node(name='name', mesh=base, children=children, translation=[0, 1, 0])
    world = g.node(name='world', mesh=stub)
    common = g.node(name='COMMON', children=[world, name])
    gltf = {'asset': {'version': '2.0', 'generator': 'make_banner_glb.py'}, 'scene': 0, 'scenes': [{'nodes': [common]}], 'nodes': g.nodes, 'meshes': g.meshes,
            'materials': g.materials, 'images': g.images, 'textures': g.textures, 'samplers': g.samplers, 'accessors': g.accessors, 'bufferViews': g.views,
            'animations': [{'name': 'Twinkle', 'samplers': samplers, 'channels': channels}], 'buffers': [{'byteLength': len(g.bin)}]}
    js = json.dumps(gltf, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    bn = bytes(g.bin) + b'\0' * (-len(g.bin) % 4)
    data = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(bn)) + struct.pack('<I4s', len(js), b'JSON') + js + struct.pack('<I4s', len(bn), b'BIN\0') + bn
    open(out, 'wb').write(data)
    print('wrote', out, len(data), 'bytes;', len(g.nodes), 'nodes,', len(channels), 'animation channels')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
