"""TEST ONLY: vr_solve.py <rom> <map id> <boulder index> <stand x,z> <goal tiles x,z;x,z...>: Sokoban BFS moving one boulder; prints the move list and tap plan (a push is two taps, a free step one). Remove warp tiles from the free set before planning: stepping on one leaves the map."""
import collections, sys
from vr_free import load
DIRS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}

def solve(free, obstacles, player, boulder, goals):
    start = (player, boulder)
    prev = {start: None}
    q = collections.deque([start])
    while q:
        s = q.popleft()
        p, b = s
        if b in goals:
            path = []
            while prev[s]:
                s, d = prev[s][0], prev[s][1]
                path.append(d)
            return path[::-1]
        for name, (dx, dz) in DIRS.items():
            n = (p[0] + dx, p[1] + dz)
            if n == b:
                nb = (b[0] + dx, b[1] + dz)
                if nb in free and nb not in obstacles:
                    ns = (n, nb)
                    if ns not in prev:
                        prev[ns] = (s, name, True); q.append(ns)
            elif n in free and n not in obstacles:
                ns = (n, b)
                if ns not in prev:
                    prev[ns] = (s, name, False); q.append(ns)
    return None

def taps(free, obstacles, player, boulder, path):
    out = []
    p, b = player, boulder
    for d in path:
        dx, dz = DIRS[d]
        n = (p[0] + dx, p[1] + dz)
        if n == b:
            out += [d, d]; b = (b[0] + dx, b[1] + dz)
        else:
            out.append(d)
        p = n
    return out, p, b

if __name__ == '__main__':
    rom, mid, bi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    sx, sz = (int(v) for v in sys.argv[4].split(','))
    goals = {tuple(int(v) for v in g.split(',')) for g in sys.argv[5].split(';')}
    free, actors, g = load(rom, mid)
    boulders = [a[4] for a in actors if a[1] == 84 and a[2] == 10002]
    others = {a[4] for a in actors if not (a[1] == 84 and a[2] == 10002 and a[4] == boulders[bi])}
    path = solve(free, others, (sx, sz), boulders[bi], goals)
    print('boulder', boulders[bi], 'solution', None if path is None else len(path))
    if path:
        t, p, b = taps(free, others, (sx, sz), boulders[bi], path)
        print('taps', len(t), 'end player', p, 'end boulder', b)
        print(' '.join(t))
