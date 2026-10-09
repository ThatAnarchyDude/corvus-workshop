"""Use Blue's existing HG textures for the rival naming icon only."""
import struct
import ndspy.narc
import ndspy.texture
import ndspy.lz10
import ndspy.color


def patch(rom):
    names = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/1')])
    models = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/8/1')])
    blue = ndspy.texture.NSBTX(models.files[169])
    textures = dict(blue.textures)
    cells = ndspy.lz10.decompress(names.files[12])
    graphics = bytearray(ndspy.lz10.decompress(names.files[10]))
    palette = bytearray(names.files[1])
    # Palette 7 is used exclusively by the naming icon's three rival cells.
    for cell in range(70):
        n, _, offset = struct.unpack_from('<HHI', cells, 48+8*cell)
        for i in range(n):
            attr2, = struct.unpack_from('<H', cells, 48+70*8+offset+6*i+4)
            if attr2 >> 12 == 7:
                assert cell in (54,55,56)
    colors = [ndspy.color.pack(*c) for c in blue.palettes[0][1].colors]
    struct.pack_into('<16H', palette, 40+7*32, *colors)
    for cell, frame in zip((54,55,56),(6,5,7)):
        n, _, offset = struct.unpack_from('<HHI', cells, 48+8*cell)
        assert n == 1
        attrs = struct.unpack_from('<3H', cells, 48+70*8+offset)
        assert attrs[:2] == (0,0x8000)  # A 32x32 square, no flips.
        start = 48+(attrs[2]&1023)*32
        tex = textures[f'gsleader16.{frame}']
        assert (tex.width,tex.height) == (32,32)
        # NSBTX indexed textures are linear; NCGR objects use 8x8 tiles.
        raw = tex.data1
        tiled = bytearray()
        for ty in range(4):
            for tx in range(4):
                for y in range(8):
                    at = (ty*8+y)*16+tx*4
                    tiled.extend(raw[at:at+4])
        graphics[start:start+512] = tiled
    names.files[1] = bytes(palette)
    names.files[10] = ndspy.lz10.compress(bytes(graphics))
    rom.files[rom.filenames.idOf('a/0/3/1')] = names.save()
    return {'naming_icon':'Blue', 'original_overworld_and_battle_silver_preserved':True}
