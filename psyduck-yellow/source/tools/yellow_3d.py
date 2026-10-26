"""3D version of a Yellow Tower floor: floor, raised walls and stone markers built from the walk grid, textured with HeartGold's own (recoloured) Bell Tower textures.

Input is the step grid from yellow_floor (True = walkable). Blocked steps that connect to the outside of the room are walls; blocked steps sitting inside the room are stones
(gravestone stand-ins). Geometry is emitted as one polygon per material in a Nintendo .imd (see yellow_imd.py) for g3dcvtr.
Units: 1.0 = 64 world units; one step = one HeartGold tile = 0.25.
"""
from collections import deque

TILE = 0.25
WALL_H = 0.30
PILASTERS = True
OLDSIDE = False
STONE_H = 0.17
STONE_INSET = 0.04


def classify(walk, keep):
    """-> dict (sx, sy) -> 'floor' | 'wall' | 'stone'. keep = steps that must stay walkable (warps)."""
    h, w = len(walk), len(walk[0])
    free = lambda x, y: 0 <= x < w and 0 <= y < h and (walk[y][x] or (x, y) in keep)
    outside, queue = set(), deque()
    for x in range(-1, w + 1):
        for y in (-1, h):
            queue.append((x, y))
    for y in range(-1, h + 1):
        for x in (-1, w):
            queue.append((x, y))
    outside.update(queue)
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if -1 <= p[0] <= w and -1 <= p[1] <= h and p not in outside and not free(*p):
                outside.add(p)
                queue.append(p)
    kinds = {}
    for y in range(h):
        for x in range(w):
            if free(x, y):
                kinds[(x, y)] = 'floor'
            elif (x, y) in outside:
                kinds[(x, y)] = 'wall'
            else:
                kinds[(x, y)] = 'stone'
    return kinds


def runs(cells):
    """Merge horizontally adjacent cells (set of (x, y)) into (x0, y, n) runs."""
    out = []
    for y in sorted({c[1] for c in cells}):
        xs = sorted(c[0] for c in cells if c[1] == y)
        start = prev = xs[0]
        for x in xs[1:]:
            if x != prev + 1:
                out.append((start, y, prev - start + 1))
                start = x
            prev = x
        out.append((start, y, prev - start + 1))
    return out


def geometry(kinds, x0, z0):
    """-> {material: [quad]} where quad = 4 x (x, y, z, s, t, nx, ny, nz); texels per tile are set by the caller's texture size via S[material]."""
    quads = {'floor': [], 'wall_top': [], 'wall_side': [], 'stone_top': [], 'stone_side': []}
    X = lambda sx: x0 + sx * TILE
    Z = lambda sy: z0 + sy * TILE
    floors = {p for p, k in kinds.items() if k in ('floor', 'stone')}
    for sx, sy, n in runs(floors):
        quads['floor'].append(((X(sx), 0, Z(sy), 0, 0, 0, 1, 0), (X(sx), 0, Z(sy + 1), 0, 1, 0, 1, 0), (X(sx + n), 0, Z(sy + 1), n, 1, 0, 1, 0), (X(sx + n), 0, Z(sy), n, 0, 0, 1, 0)))
    walls = {p for p, k in kinds.items() if k == 'wall'}
    for sx, sy, n in runs(walls):
        quads['wall_top'].append(((X(sx), WALL_H, Z(sy), 0, 0, 0, 1, 0), (X(sx), WALL_H, Z(sy + 1), 0, 1, 0, 1, 0), (X(sx + n), WALL_H, Z(sy + 1), n, 1, 0, 1, 0), (X(sx + n), WALL_H, Z(sy), n, 0, 0, 1, 0)))
    def side(a, b, height, key, normal):
        """vertical face from point a to b (x, z), height up from y=0; texture u along the face in tiles."""
        (ax, az), (bx, bz) = a, b
        length = max(abs(bx - ax), abs(bz - az)) / TILE
        v = height / TILE
        quads[key].append(((ax, 0, az, 0, v, *normal), (ax, height, az, 0, 0, *normal), (bx, height, bz, length, 0, *normal), (bx, 0, bz, length, v, *normal)))
    for (sx, sy), k in kinds.items():
        if k == 'wall':
            for dx, dy, normal, (a, b) in (
                    (0, 1, (0, 0, 1), ((X(sx + 1), Z(sy + 1)), (X(sx), Z(sy + 1)))),      # south face, seen from the south
                    (-1, 0, (-1, 0, 0), ((X(sx), Z(sy + 1)), (X(sx), Z(sy)))),
                    (1, 0, (1, 0, 0), ((X(sx + 1), Z(sy)), (X(sx + 1), Z(sy + 1)))),
                    (0, -1, (0, 0, -1), ((X(sx), Z(sy)), (X(sx + 1), Z(sy))))):
                if kinds.get((sx + dx, sy + dy)) in ('floor', 'stone'):
                    side(a, b, WALL_H, 'wall_side', normal)
        elif k == 'stone':
            i = STONE_INSET
            xa, xb, za, zb = X(sx) + i, X(sx + 1) - i, Z(sy) + i, Z(sy + 1) - i
            quads['stone_top'].append(((xa, STONE_H, za, 0, 0, 0, 1, 0), (xa, STONE_H, zb, 0, 1, 0, 1, 0), (xb, STONE_H, zb, 1, 1, 0, 1, 0), (xb, STONE_H, za, 1, 0, 0, 1, 0)))
            side((xb, zb), (xa, zb), STONE_H, 'stone_side', (0, 0, 1))
            side((xa, zb), (xa, za), STONE_H, 'stone_side', (-1, 0, 0))
            side((xb, za), (xb, zb), STONE_H, 'stone_side', (1, 0, 0))
            side((xa, za), (xb, za), STONE_H, 'stone_side', (0, 0, -1))
    return quads


def geometry_tiles(kinds, full, x0, z0, inset=0.10):
    """Tile-resolution version for the 2x-scaled rooms. kinds: this chunk's tiles {(lx, lz): kind}; full: the same coordinate system incl. neighbouring chunks' tiles
    (for wall faces across chunk edges); x0, z0: model-space origin of local tile (0, 0). A 'stone' step is a 2x2 block of stone tiles: one box per block (blocks never straddle a chunk)."""
    quads = {'floor': [], 'wall_top': [], 'wall_side': [], 'stone_top': [], 'stone_side': []}
    X = lambda lx: x0 + lx * TILE
    Z = lambda lz: z0 + lz * TILE

    def top(key, cells, y):
        for sx, sy, n in runs(cells):
            quads[key].append(((X(sx), y, Z(sy), 0, 0, 0, 1, 0), (X(sx), y, Z(sy + 1), 0, 1, 0, 1, 0), (X(sx + n), y, Z(sy + 1), n, 1, 0, 1, 0), (X(sx + n), y, Z(sy), n, 0, 0, 1, 0)))

    def side(a, b, height, key, normal, tiles_long):
        (ax, az), (bx, bz) = a, b
        v = height / TILE
        quads[key].append(((ax, 0, az, 0, v, *normal), (ax, height, az, 0, 0, *normal), (bx, height, bz, tiles_long, 0, *normal), (bx, 0, bz, tiles_long, v, *normal)))
    top('floor', {p for p, k in kinds.items() if k in ('floor', 'stone')}, 0)
    top('wall_top', {p for p, k in kinds.items() if k == 'wall'}, WALL_H)
    for key in ('plinth_side', 'plinth_top', 'cornice_side', 'cornice_top', 'pillar_side', 'pillar_top'):
        quads[key] = []
    BASE_H, CORN_H = (0.0, 0.0) if OLDSIDE else (0.07, 0.05)

    def shell(a, b, normal, y0, y1, off, side_key, top_key, caps=True):
        """A slab on a wall face: a and b are the face's end points (x, z), normal points out of the wall; the slab sticks out by `off`."""
        (ax, az), (bx, bz) = a, b
        nx, nz = normal[0], normal[2]
        ax2, az2, bx2, bz2 = ax + nx * off, az + nz * off, bx + nx * off, bz + nz * off
        length = max(abs(bx - ax), abs(bz - az)) / TILE
        v = (y1 - y0) / TILE
        quads[side_key].append(((ax2, y0, az2, 0, v, *normal), (ax2, y1, az2, 0, 0, *normal), (bx2, y1, bz2, length, 0, *normal), (bx2, y0, bz2, length, v, *normal)))
        quads[top_key].append(((ax, y1, az, 0, 0, 0, 1, 0), (ax2, y1, az2, 0, 1, 0, 1, 0), (bx2, y1, bz2, length, 1, 0, 1, 0), (bx, y1, bz, length, 0, 0, 1, 0)))
        if caps:
            for (px, pz), (qx, qz), cn in (((ax, az), (ax2, az2), (-(bx - ax), 0, -(bz - az))), ((bx2, bz2), (bx, bz), (bx - ax, 0, bz - az))):
                m = max(abs(cn[0]), abs(cn[2])) or 1
                cn = (cn[0] / m, 0, cn[2] / m)
                quads[side_key].append(((px, y0, pz, 0, v, *cn), (px, y1, pz, 0, 0, *cn), (qx, y1, qz, off / TILE, 0, *cn), (qx, y0, qz, off / TILE, v, *cn)))

    faces = {(0, 1): {}, (0, -1): {}, (-1, 0): {}, (1, 0): {}}          # direction -> {plane tile: [along tiles]}
    for (lx, lz), k in kinds.items():
        if k != 'wall':
            continue
        for dx, dz in faces:
            if full.get((lx + dx, lz + dz)) in ('floor', 'stone'):
                plane, along = (lz, lx) if dz else (lx, lz)
                faces[(dx, dz)].setdefault(plane, []).append(along)
    ends = {                                  # (dx, dz) -> normal, function (plane, start, n) -> (a, b) with the same orientation as before
        (0, 1): ((0, 0, 1), lambda p, s0, n: ((X(s0 + n), Z(p + 1)), (X(s0), Z(p + 1)))),
        (0, -1): ((0, 0, -1), lambda p, s0, n: ((X(s0), Z(p)), (X(s0 + n), Z(p)))),
        (-1, 0): ((-1, 0, 0), lambda p, s0, n: ((X(p), Z(s0 + n)), (X(p), Z(s0)))),
        (1, 0): ((1, 0, 0), lambda p, s0, n: ((X(p + 1), Z(s0)), (X(p + 1), Z(s0 + n)))),
    }
    for (dx, dz), planes in faces.items():
        normal, ends_fn = ends[(dx, dz)]
        for plane, alongs in planes.items():
            alongs = sorted(alongs)
            start = prev = alongs[0]
            segs = []
            for t in alongs[1:] + [None]:
                if t is None or t != prev + 1:
                    segs.append((start, prev - start + 1))
                    start = t
                prev = t
            for s0, n in segs:
                a, b = ends_fn(plane, s0, n)
                v = (WALL_H - BASE_H - CORN_H) / TILE
                (ax, az), (bx, bz) = a, b
                quads['wall_side'].append(((ax, BASE_H, az, 0, v, *normal), (ax, WALL_H - CORN_H, az, 0, 0, *normal), (bx, WALL_H - CORN_H, bz, n, 0, *normal), (bx, BASE_H, bz, n, v, *normal)))
                shell(a, b, normal, 0, BASE_H, 0.025, 'plinth_side', 'plinth_top', caps=False)
                shell(a, b, normal, WALL_H - CORN_H, WALL_H, 0.035, 'cornice_side', 'cornice_top', caps=False)
                # pilasters on this strip: every 4th tile, centred, only where the neighbours on both sides are part of the same strip
                for t in range(s0 + 1, s0 + n - 1):
                    if not PILASTERS or t % 4 != 1:
                        continue
                    if dz:
                        m = (X(t) + X(t + 1)) / 2
                        mx, mz = m, a[1]
                        ux, uz = (1, 0)
                    else:
                        mx, mz = a[0], (Z(t) + Z(t + 1)) / 2
                        ux, uz = (0, 1)
                    w = TILE * 0.28
                    shell((mx - ux * w, mz - uz * w), (mx + ux * w, mz + uz * w), normal, 0, WALL_H, 0.06, 'pillar_side', 'pillar_top')
    for (lx, lz), k in kinds.items():
        if False:
            pass
        elif k == 'stone' and lx % 2 == 0 and lz % 2 == 0:
            xa, xb, za, zb = X(lx) + inset, X(lx + 2) - inset, Z(lz) + inset, Z(lz + 2) - inset
            h = STONE_H
            quads['stone_top'].append(((xa, h, za, 0, 0, 0, 1, 0), (xa, h, zb, 0, 1, 0, 1, 0), (xb, h, zb, 1, 1, 0, 1, 0), (xb, h, za, 1, 0, 0, 1, 0)))
            for a, b, normal in (((xb, zb), (xa, zb), (0, 0, 1)), ((xa, zb), (xa, za), (-1, 0, 0)), ((xb, za), (xb, zb), (1, 0, 0)), ((xa, za), (xb, za), (0, 0, -1))):
                side(a, b, h, 'stone_side', normal, 2)
    return quads


SLOPE = 0.5 * TILE        # how far a wall's top edge is pulled back from its foot: walls lean back like masonry
VISIBLE_DEPTH = 3         # wall tiles farther than this from any floor tile are left out (the void behind them is black anyway)


def geometry_sloped(kinds, full, x0, z0):
    """Sloped-wall version of geometry_tiles (same inputs). Wall tops are inset on every side that faces the room and a sloped face joins them to the floor;
    exposed convex corners meet in a clean diagonal crease. Gravestone stones taper towards the top. Materials: floor, wall_top, wall_slope, stone_top, stone_side."""
    quads = {'floor': [], 'wall_top': [], 'wall_slope': [], 'stone_top': [], 'stone_side': []}
    X = lambda lx: x0 + lx * TILE
    Z = lambda lz: z0 + lz * TILE
    openk = ('floor', 'stone')
    floors = {p for p, k in kinds.items() if k in openk}
    for sx, sy, n in runs(floors):
        quads['floor'].append(((X(sx), 0, Z(sy), 0, 0, 0, 1, 0), (X(sx), 0, Z(sy + 1), 0, 1, 0, 1, 0), (X(sx + n), 0, Z(sy + 1), n, 1, 0, 1, 0), (X(sx + n), 0, Z(sy), n, 0, 0, 1, 0)))

    def near(p):
        return any(full.get((p[0] + dx, p[1] + dz)) in openk for dx in range(-VISIBLE_DEPTH, VISIBLE_DEPTH + 1) for dz in range(-VISIBLE_DEPTH, VISIBLE_DEPTH + 1))
    plain = set()
    h = WALL_H
    norm = lambda nx, ny, nz: tuple(c / ((nx * nx + ny * ny + nz * nz) ** 0.5) for c in (nx, ny, nz))
    slope_len = ((h * h + SLOPE * SLOPE) ** 0.5) / TILE
    for (lx, lz), k in kinds.items():
        if k != 'wall' or not near((lx, lz)):
            continue
        ex = {d: full.get((lx + d[0], lz + d[1])) in openk for d in ((-1, 0), (1, 0), (0, -1), (0, 1))}
        if not any(ex.values()):
            plain.add((lx, lz))
            continue
        xa, xb, za, zb = X(lx), X(lx + 1), Z(lz), Z(lz + 1)
        iw, ie = SLOPE if ex[(-1, 0)] else 0, SLOPE if ex[(1, 0)] else 0
        inn, iss = SLOPE if ex[(0, -1)] else 0, SLOPE if ex[(0, 1)] else 0
        ta, tb, tc, td = xa + iw, xb - ie, za + inn, zb - iss
        quads['wall_top'].append(((ta, h, tc, 0, 0, 0, 1, 0), (ta, h, td, 0, 1, 0, 1, 0), (tb, h, td, 1, 1, 0, 1, 0), (tb, h, tc, 1, 0, 0, 1, 0)))
        if ex[(0, 1)]:       # south side: foot along z = zb, top edge pulled back to z = td
            quads['wall_slope'].append(((xb, 0, zb, 0, slope_len, *norm(0, SLOPE, 1)), (tb, h, td, 0, 0, *norm(0, SLOPE, 1)), (ta, h, td, 1, 0, *norm(0, SLOPE, 1)), (xa, 0, zb, 1, slope_len, *norm(0, SLOPE, 1))))
        if ex[(0, -1)]:
            quads['wall_slope'].append(((xa, 0, za, 0, slope_len, *norm(0, SLOPE, -1)), (ta, h, tc, 0, 0, *norm(0, SLOPE, -1)), (tb, h, tc, 1, 0, *norm(0, SLOPE, -1)), (xb, 0, za, 1, slope_len, *norm(0, SLOPE, -1))))
        if ex[(-1, 0)]:
            quads['wall_slope'].append(((xa, 0, zb, 0, slope_len, *norm(-1, SLOPE, 0)), (ta, h, td, 0, 0, *norm(-1, SLOPE, 0)), (ta, h, tc, 1, 0, *norm(-1, SLOPE, 0)), (xa, 0, za, 1, slope_len, *norm(-1, SLOPE, 0))))
        if ex[(1, 0)]:
            quads['wall_slope'].append(((xb, 0, za, 0, slope_len, *norm(1, SLOPE, 0)), (tb, h, tc, 0, 0, *norm(1, SLOPE, 0)), (tb, h, td, 1, 0, *norm(1, SLOPE, 0)), (xb, 0, zb, 1, slope_len, *norm(1, SLOPE, 0))))
    for sx, sy, n in runs(plain):
        quads['wall_top'].append(((X(sx), h, Z(sy), 0, 0, 0, 1, 0), (X(sx), h, Z(sy + 1), 0, 1, 0, 1, 0), (X(sx + n), h, Z(sy + 1), n, 1, 0, 1, 0), (X(sx + n), h, Z(sy), n, 0, 0, 1, 0)))
    # gravestones: one tapered block per 2x2 stone step
    for (lx, lz), k in kinds.items():
        if k == 'stone' and lx % 2 == 0 and lz % 2 == 0:
            ba, bb, bc, bd = X(lx) + 0.08, X(lx + 2) - 0.08, Z(lz) + 0.08, Z(lz + 2) - 0.08
            t = 0.035
            ta, tb, tc, td = ba + t, bb - t, bc + t, bd - t
            hh = STONE_H
            # pitched top: a ridge along x, 0.05 above the taper line, two sloping faces and two gable ends
            rz = (tc + td) / 2
            rh = hh + 0.05
            quads['stone_top'].append(((ta, hh, tc, 0, 0, *norm(0, 1, -1)), (ta, rh, rz, 0, 1, *norm(0, 1, -1)), (tb, rh, rz, 1, 1, *norm(0, 1, -1)), (tb, hh, tc, 1, 0, *norm(0, 1, -1))))
            quads['stone_top'].append(((ta, rh, rz, 0, 0, *norm(0, 1, 1)), (ta, hh, td, 0, 1, *norm(0, 1, 1)), (tb, hh, td, 1, 1, *norm(0, 1, 1)), (tb, rh, rz, 1, 0, *norm(0, 1, 1))))
            for xe, nx in ((ta, -1), (tb, 1)):
                quads['stone_side'].append(((xe, hh, tc, 0, 1, *norm(nx, .3, 0)), (xe, rh, rz, .5, 0, *norm(nx, .3, 0)), (xe, rh, rz, .5, 0, *norm(nx, .3, 0)), (xe, hh, td, 1, 1, *norm(nx, .3, 0))))
            for (p0, q0, p1, q1, nrm) in (((bb, bd), (tb, td), (ba, bd), (ta, td), (0, .5, 1)), ((ba, bd), (ta, td), (ba, bc), (ta, tc), (-1, .5, 0)),
                                         ((bb, bc), (tb, tc), (bb, bd), (tb, td), (1, .5, 0)), ((ba, bc), (ta, tc), (bb, bc), (tb, tc), (0, .5, -1))):
                n3 = norm(*nrm)
                quads['stone_side'].append(((p0[0], 0, p0[1], 0, 1, *n3), (q0[0], hh, q0[1], 0, 0, *n3), (q1[0], hh, q1[1], 1, 0, *n3), (p1[0], 0, p1[1], 1, 1, *n3)))
    return quads
