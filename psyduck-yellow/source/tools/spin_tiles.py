"""Yellow's spinner (arrow) tiles as triggers: every arrow tile of a map is a one-tile trigger whose script slides the player along the precomputed path from pokeyellow's own table.

pokeyellow's `map_coord_movement x, y, ListLabel` lists each arrow tile and the movement it starts; the lists are `db PAD_DIR, count` read from the end backwards.
The map is built at cave_floor.SCALE (one Yellow step = SCALE x SCALE tiles), so every count is multiplied by SCALE.
"""
import re
from opening import Script, end

CODE = {'PAD_UP': 12, 'PAD_DOWN': 13, 'PAD_LEFT': 14, 'PAD_RIGHT': 15}


def load(source, asm):
    """-> {(x, y): ((direction code, steps), ...)} in execution order"""
    text = open(f'{source}/scripts/{asm}.asm').read()
    lists = {}
    for m in re.finditer(r'^(\w+Movement\w*):\n((?:\s+db [^\n]*\n)+)', text, re.M):
        rows = re.findall(r'db (PAD_\w+), (\d+)', m.group(2))
        assert re.search(r'db -1', m.group(2)), m.group(1)
        lists[m.group(1)] = tuple((CODE[d], int(n)) for d, n in reversed(rows))
    tiles = {}
    for m in re.finditer(r'map_coord_movement\s+(\d+),\s*(\d+),\s*(\w+)', text):
        tiles[(int(m.group(1)), int(m.group(2)))] = lists[m.group(3)]
    assert tiles, asm
    return tiles


def distinct(tiles):
    """Movement lists in order of first use (one script each)."""
    out = []
    for xy in sorted(tiles):
        if tiles[xy] not in out:
            out.append(tiles[xy])
    return out


def script(moves, scale):
    s = Script().emit(96).movement(255, 'slide').emit(95)
    end(s)
    s.moves('slide', [(code, n * scale) for code, n in moves])
    return s.finish()
