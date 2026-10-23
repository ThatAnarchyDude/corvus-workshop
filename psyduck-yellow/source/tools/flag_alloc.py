"""Pick persistent flags that no script bank, actor or trigger in the ROM references."""
import struct
import ndspy.narc
from opening import events_decode

LOW, HIGH = 0x950, 0xAA0          # 0xAA0+ are daily flags; 0xB60 is the save bound


def used_flags(rom):
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    seen = set()
    for raw in scripts.files:
        for at in range(0, len(raw) - 1):
            seen.add(struct.unpack_from('<H', raw, at)[0])
    for raw in events.files:
        for group in events_decode(raw):
            for row in group:
                for at in range(0, len(row) - 1, 2):
                    seen.add(struct.unpack_from('<H', row, at)[0])
    return seen


def free_flags(rom, count, reserved=()):
    seen = used_flags(rom) | set(reserved)
    out = [f for f in range(HIGH - 1, LOW - 1, -1) if f not in seen][:count]
    if len(out) < count:
        raise RuntimeError('not enough free persistent flags')
    return out
