"""Check starter receipt in an emulator RAM dump, independently of ROM edits."""
import json
import struct
import sys
from pathlib import Path


def check(path, species, *, owned=None, dex_enabled=True):
    expected_owned = sorted(set(owned)) if owned is not None else [species]
    ram = Path(path).read_bytes()
    dex = []
    fields = []
    for offset in range(0x100000, len(ram) - 0x340, 4):
        if ram[offset:offset + 4] == bytes.fromhex('fecaefbe'):
            flags = list(ram[offset + 0x334:offset + 0x338])
            if all(x in (0, 1) for x in flags):
                owned = [s for s in range(1, 494)
                         if ram[offset + 4 + (s - 1) // 8] & (1 << ((s - 1) % 8))]
                dex.append(dict(address=hex(0x2000000 + offset), flags=flags, owned=owned))
        location = struct.unpack_from('<I', ram, offset + 0x20)[0] - 0x2000000
        avatar = struct.unpack_from('<I', ram, offset + 0x40)[0] - 0x2000000
        if not (0x100000 < location < len(ram) - 20
                and 0x100000 < avatar < len(ram) - 0x34):
            continue
        map_id = struct.unpack_from('<i', ram, location)[0]
        if map_id not in (9, 49, 50, 500, 501, 503, 505, 506, 527):
            continue
        player = struct.unpack_from('<I', ram, avatar + 0x30)[0] - 0x2000000
        follower = struct.unpack_from('<I', ram, offset + 0xE4)[0] - 0x2000000
        if not (0x100000 < player < len(ram) - 0x70
                and 0x100000 < follower < len(ram) - 0x70):
            continue
        xyz = struct.unpack_from('<3i', ram, player + 0x64)
        if not all(0 <= value < 2000 for value in xyz):
            continue
        save = struct.unpack_from('<I', ram, offset + 0xC)[0] - 0x2000000
        if not (0x100000 < save < len(ram) - 0x2330C):
            continue
        party_header = save + 0x23014 + 2 * 16
        block_id, _, party_offset = struct.unpack_from('<3I', ram, party_header)
        if block_id != 2:
            continue
        party = save + 0x10 + party_offset
        max_count, count = struct.unpack_from('<2I', ram, party)
        if max_count != 6:
            continue
        dex_id, _, dex_offset = struct.unpack_from('<3I', ram, save + 0x23014 + 6 * 16)
        if dex_id != 6:
            continue
        fields.append(dict(
            address=hex(0x2000000 + offset), map_id=map_id, player=list(xyz),
            follower=list(struct.unpack_from('<3i', ram, follower + 0x64)),
            follower_species=struct.unpack_from('<I', ram, offset + 0xF4)[0],
            follower_active=ram[offset + 0xFA], party_count=count,
            active_dex_address=hex(0x2000000 + save + 0x10 + dex_offset)))
    if len(fields) != 1 or fields[0]['follower_species'] != species or fields[0]['follower_active'] != 1:
        raise ValueError(f'Unexpected follower state: {fields}')
    if fields[0]['party_count'] != 1:
        raise ValueError(f'Unexpected party count: {fields}')
    # A normal reload can leave an additional Dex copy in the flash-read buffer.
    # Validate the live save block referenced by FieldSystem, not that cached copy.
    dex = [entry for entry in dex if entry['address'] == fields[0]['active_dex_address']]
    if len(dex) != 1 or dex[0]['flags'][2:] != ([1, 1] if dex_enabled else [0, 0]) or dex[0]['owned'] != expected_owned:
        raise ValueError(f'Unexpected live National Dex state: {dex}')
    return dict(dex=dex[0], field=fields[0],
                note='Follower visibility is verified separately in screenshots, not inferred from active state.')


if __name__ == '__main__':
    print(json.dumps(check(sys.argv[1], int(sys.argv[2])), indent=2))
