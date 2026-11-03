"""Static softlock audit: for every warp (from any map) that leads into a rebuilt extension map (id >= 540), the arrival tile must be walkable and the walkable region around it must contain a way out
(a firing warp tile that leaves the map or goes to another anchor). Catches walled-in arrivals like Silph 10F's pad (found 2026-11-02 by hand). Collision comes from the map's land chunks (blocked = byte 1 & 0x80);
NPCs, boulders, scripted gates and trigger-only exits (Hideout lift doors) are not modelled, so a region whose only exits are scripted is reported as 'trigger exits only'.
Usage: audit_arrivals.py <rom.nds>"""
import struct
import sys
from collections import deque
import ndspy.narc
import ndspy.rom
import cave_ladders as cl
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    mats = ndspy.narc.NARC(rom.getFileByName('a/0/4/1'))
    lands = ndspy.narc.NARC(rom.getFileByName('a/0/6/5'))
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    d = bytes(rom.loadArm9().sections[0].data)
    recs = [d[TABLE + 24 * m:TABLE + 24 * m + 24] for m in range(ext.NATIVE_COUNT)] + list(ext.records(rom))
    cache = {}

    def info(m):
        if m not in cache:
            rec = recs[m]
            g = events_decode(bytes(events[struct.unpack_from('<H', rec, 16)[0]]))
            mat = bytes(mats.files[struct.unpack_from('<H', rec, 4)[0]])
            w, h, hd, ht, n = mat[:5]
            ids = struct.unpack_from('<%dH' % (w * h), mat, 5 + n + w * h * (2 * hd + ht))
            perm = {}
            for i, lid in enumerate(ids):
                if lid != 65535 and lid < len(lands.files):
                    perm[(i % w, i // w)] = cl.parse(bytes(lands.files[lid]))[0]
            warps = [struct.unpack_from('<4H', e, 0) for e in g[2]]
            triggers = [struct.unpack_from('<Hhh5H', t, 0) for t in g[3]]
            cache[m] = (perm, warps, triggers)
        return cache[m]

    def walkable(m, x, z):
        p = info(m)[0].get((x // 32, z // 32))
        return p is not None and not p[((z % 32) * 32 + x % 32) * 2 + 1] & 0x80

    problems, checked = [], set()
    for src in range(len(recs)):
        try:
            warps = info(src)[1]
        except Exception:
            continue
        for k, (x, z, dm, anchor) in enumerate(warps):
            if dm < ext.NATIVE_COUNT or dm >= len(recs) or (dm, anchor) in checked:
                continue
            checked.add((dm, anchor))
            try:
                dwarps = info(dm)[1]
                ax, az = dwarps[anchor][:2]
            except Exception as error:
                problems.append((src, k, dm, anchor, 'destination anchor missing: %r' % error))
                continue
            if not walkable(dm, ax, az):
                problems.append((src, k, dm, anchor, 'arrival tile (%d,%d) is blocked' % (ax, az)))
                continue
            seen, q = {(ax, az)}, deque([(ax, az)])
            while q:
                a, b = q.popleft()
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    t = (a + dx, b + dz)
                    if t not in seen and walkable(dm, *t):
                        seen.add(t)
                        q.append(t)
            own = {(w[0], w[1]) for i, w in enumerate(dwarps) if w[2] == dm and w[3] == i}               # this map's own arrival entries
            exits = [(w[0], w[1]) for w in dwarps if (w[0], w[1]) in seen and (w[0], w[1]) not in own and not (w[2] == dm and w[3] < len(dwarps) and dwarps[w[3]][:2] == (w[0], w[1]))]
            trig = [t for t in info(dm)[2] if any(((t[1] + i), (t[2] + j)) in seen for i in range(t[3]) for j in range(t[4]))]
            if not exits:
                problems.append((src, k, dm, anchor, 'region of %d tiles around arrival (%d,%d) has no way out%s' % (len(seen), ax, az, ' (trigger exits only)' if trig else '')))
    print(len(checked), 'arrivals checked,', len(problems), 'problems')
    for p in problems:
        print('  map %d warp %d -> map %d anchor %d: %s' % p)


if __name__ == '__main__':
    main(sys.argv[1])
