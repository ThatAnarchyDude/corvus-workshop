"""Trainer sprites that did not match their class (found by audit_sprites.py, looked at on screen 2026-10-24).

Sprite 227 is a spiky-haired fighter in orange, not a kid: 9 Bug Catchers (class 6) and 1 Youngster (class 2) used it. Bug Catchers get the straw-hat kid (318, HG's own),
the Youngster the cap boy (317). Hiker trainer 766 used a girl sprite (332) -> the hiker (333). Super Nerd trainer 769 used the Youngster sprite -> the glasses man (338).
Left alone on purpose (plausible variety): Youngster 315, Lass 320, class 68 on 332, class 42 on 348.

Usage: sprite_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode, events_encode
from viridian_tutorial import TABLE

# (trainer class, old sprite) -> new sprite; trainer record class comes from a/0/5/5 byte 1
RULES = {(6, 227): 318, (2, 227): 317, (9, 332): 333, (78, 317): 338}


def patch(rom):
    d = rom.loadArm9().sections[0].data
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    trainers = ndspy.narc.NARC(rom.getFileByName('a/0/5/5'))
    records = [bytes(d[TABLE + m * 24:TABLE + m * 24 + 24]) for m in range(540)] + ext.records(rom)
    seen, changed = set(), []
    for m, r in enumerate(records):
        eid = struct.unpack_from('<H', r, 16)[0]
        if eid in seen or eid >= len(events.files):
            continue
        seen.add(eid)
        try:
            g = events_decode(events.files[eid])
        except Exception:
            continue
        dirty = False
        for i, a in enumerate(g[1]):
            sprite, script = struct.unpack_from('<H', a, 2)[0], struct.unpack_from('<H', a, 10)[0]
            if 3000 <= script < 4000 and script - 2999 < len(trainers.files):
                new = RULES.get((trainers.files[script - 2999][1], sprite))
                if new:
                    b = bytearray(a)
                    struct.pack_into('<H', b, 2, new)
                    g[1][i] = bytes(b)
                    changed.append((m, script - 2999, sprite, new))
                    dirty = True
        if dirty:
            events.files[eid] = events_encode(g)
    rom.setFileByName('a/0/3/2', events.save())
    return changed


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
