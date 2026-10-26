"""Actors whose overworld sprite id has no resource in the engine freeze the game (black screen, seen in Vermilion's Pokemon Center, 2026-10-26).

Sprites 542 (Chansey, Vermilion Center), 428/456 (Bulbasaur/Sandshrew, Melanie's house) and 444 (Vermilion house) are not in the sprite table; the table holds the
original trainer/NPC sprites (<428) and the Pokemon sprites 994-1046. They become Pokemon sprites from that range (stand-ins until real art exists).

Usage: sprite_crash_fix.py <in.nds> <out.nds>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import map_header_extension as ext
from opening import events_decode, events_encode
from viridian_tutorial import TABLE

RULES = {542: 1021, 428: 1007, 456: 1012, 444: 1005}


def patch(rom):
    d = rom.loadArm9().sections[0].data
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    records = [bytes(d[TABLE + m * 24:TABLE + m * 24 + 24]) for m in range(540)] + ext.records(rom)
    changed = {}
    for eid in sorted({struct.unpack_from('<H', r, 16)[0] for r in records}):
        if eid >= len(events.files):
            continue
        try:
            g = events_decode(events.files[eid])
        except Exception:
            continue
        hit = []
        for i, a in enumerate(g[1]):
            s = struct.unpack_from('<H', a, 2)[0]
            if s in RULES:
                b = bytearray(a)
                struct.pack_into('<H', b, 2, RULES[s])
                g[1][i] = bytes(b)
                hit.append((i, s, RULES[s]))
        if hit:
            events.files[eid] = events_encode(g)
            changed[eid] = hit
    rom.setFileByName('a/0/3/2', events.save())
    return changed


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
