"""Static audit of the project's persistent flags (0x960-0xB5F): flags a script CHECKS (command 32) but no script ever SETS (command 30), and actor hide flags nothing sets.

A checked-but-never-set flag is either a native HG flag (set by engine code) or a gate that can never open. Reports the flags in the project's range so the owner/next session can judge.

Usage: audit_flags.py <rom.nds>
"""
import re
import struct
import sys
import ndspy.narc
import ndspy.rom
from opening import events_decode

LOW, HIGH = 0x960, 0xB60


def main(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files
    sets, checks = {}, {}
    for i, raw in enumerate(scripts):
        b = bytes(raw)
        for m in re.finditer(rb'\x1e\x00(..)', b, re.S):
            v = struct.unpack('<H', m.group(1))[0]
            if LOW <= v < HIGH:
                sets.setdefault(v, set()).add(i)
        for m in re.finditer(rb'\x20\x00(..)', b, re.S):
            v = struct.unpack('<H', m.group(1))[0]
            if LOW <= v < HIGH:
                checks.setdefault(v, set()).add(i)
    hides = {}
    for i, raw in enumerate(events):
        try:
            g = events_decode(raw)
        except Exception:
            continue
        for a in g[1]:
            v = struct.unpack_from('<H', a, 8)[0]
            if LOW <= v < HIGH:
                hides.setdefault(v, set()).add(i)
    never = sorted(v for v in checks if v not in sets)
    print('checked but never set by a script:', [hex(v) for v in never])
    hide_never = sorted(v for v in hides if v not in sets)
    print('actor hide flags never set by a script:', [hex(v) for v in hide_never])
    print(len(sets), 'flags set,', len(checks), 'checked,', len(hides), 'used by actors')


if __name__ == '__main__':
    main(sys.argv[1])
