"""Anchor only the isolated S.S. Anne rooms to native Vermilion.

Native Pokegear uses explicit interior world coordinates to look up the main
matrix header. Zero coordinates instead fall back to the last outdoor warp,
which is unreliable for copied-save tests and future ship transitions.
"""
import struct
import ndspy.narc
from viridian_tutorial import TABLE

CLONES = (254, 255)
VERMILION = 54
REFERENCE_INTERIOR = 358
SECTION = 235


def patch(rom):
    main = rom.loadArm9()
    data = main.sections[0].data = bytearray(main.sections[0].data)
    reference = struct.unpack_from('<H', data, TABLE + REFERENCE_INTERIOR * 24 + 2)[0]
    x, y = (reference >> 4) & 63, (reference >> 10) & 63
    assert (x, y) == (40, 9)
    matrix = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/4/1')]).files[0]
    width, height, has_headers, _, name_length = matrix[:5]
    assert has_headers and x < width and y < height
    assert struct.unpack_from('<H', matrix, 5 + name_length + 2 * (y * width + x))[0] == VERMILION
    changed = []
    for mid in CLONES:
        at = TABLE + mid * 24
        assert data[at + 18] == SECTION
        assert struct.unpack_from('<I', data, at + 20)[0] & 1
        old = struct.unpack_from('<H', data, at + 2)[0]
        assert ((old >> 4) & 63, (old >> 10) & 63) == (25, 14)
        # Preserve the low four move-model-bank bits.
        new = (old & 15) | (x << 4) | (y << 10)
        struct.pack_into('<H', data, at + 2, new)
        changed.append({'map': mid, 'old_word': old, 'new_word': new})
    rom.arm9 = main.save(compress=True)
    return {'changed_headers': changed, 'world_coordinates': [x, y],
            'main_matrix_location': VERMILION, 'section': SECTION,
            'native_pokegear_check_pending': True}
