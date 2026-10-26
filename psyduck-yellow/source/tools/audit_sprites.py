"""Audit: does every project trainer actor use a sprite that HeartGold itself uses for that trainer class?

Usage: audit_sprites.py <project rom> <original HeartGold rom>
Native class->sprite counts come from the original ROM's own trainer actors (script ids 3000+, record class byte 1). A project actor is flagged when its sprite is
never used natively for its class (or used under 10% of the time). Output is a worklist, not a verdict: some project classes are deliberate (Rocket, Rival).
"""
import collections
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode
from viridian_tutorial import TABLE


def actors(rom, limit=None):
    d = rom.loadArm9().sections[0].data
    ev = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    tr = ndspy.narc.NARC(rom.getFileByName('a/0/5/5'))
    recs = [bytes(d[TABLE + m * 24:TABLE + m * 24 + 24]) for m in range(540)] + (ext.records(rom) if limit is None else [])
    for m, r in enumerate(recs):
        eid = struct.unpack_from('<H', r, 16)[0]
        if eid >= len(ev.files):
            continue
        try:
            g = events_decode(ev.files[eid])
        except Exception:
            continue
        for a in g[1]:
            spr, script = struct.unpack_from('<H', a, 2)[0], struct.unpack_from('<H', a, 10)[0]
            if 3000 <= script < 4000 and script - 2999 < len(tr.files):
                yield m, script - 2999, tr.files[script - 2999][1], spr


def main(project, original):
    native = collections.defaultdict(collections.Counter)
    for _, t, c, s in actors(ndspy.rom.NintendoDSRom.fromFile(original), limit=540):
        native[c][s] += 1
    flagged = collections.defaultdict(list)
    for m, t, c, s in actors(ndspy.rom.NintendoDSRom.fromFile(project)):
        n = native.get(c)
        if n and n[s] < 0.1 * sum(n.values()):
            flagged[(c, s)].append((m, t))
    for (c, s), rows in sorted(flagged.items()):
        print(f'class {c} sprite {s}: native {dict(native[c].most_common(4))}; project uses it on {len(rows)} trainer(s), e.g. map/trainer {rows[:5]}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
