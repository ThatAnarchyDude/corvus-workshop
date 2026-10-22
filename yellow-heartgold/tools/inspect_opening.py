"""Record verified opening assets without modifying either ROM.

Asset IDs follow pret/pokeheartgold 9d8b7591f09b65804da2fb2dfd56f320633e0d36.
Run from the repository root with the project virtual environment.
"""
import json
import struct

import ndspy.narc
import ndspy.rom

from build_rom import BASE, EXPECTED, PROJECT, sha
from prototype import decode_messages


MAPS = [
    ('Pallet Town', 49, 735, 508, 446, 46),
    ("Red's house, downstairs", 503, 736, 509, 447, 455),
    ("Red's house, upstairs", 506, 737, 510, 448, 458),
    ("Oak's lab", 505, 740, 513, 451, 457),
]


def inspect():
    original = BASE.read_bytes()
    if sha(original) != EXPECTED:
        raise ValueError('Wrong base ROM: refusing to inspect patch locations')
    rom = ndspy.rom.NintendoDSRom(original)
    archives = {
        name: ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)])
        for name, path in [('scripts', 'a/0/1/2'), ('text', 'a/0/2/7'),
                           ('events', 'a/0/3/2')]
    }
    arm9 = bytes(rom.loadArm9().sections[0].data)
    initial_location = struct.pack('<5i', 64, -1, 6, 6, 1)
    if arm9.count(initial_location) != 1:
        raise ValueError('New-game location is not uniquely identified')
    maps = []
    for name, map_id, script, header, text, event in MAPS:
        entries = {}
        for label, archive, index in [('script', 'scripts', script),
                                      ('init_script', 'scripts', header),
                                      ('messages', 'text', text),
                                      ('events', 'events', event)]:
            data = archives[archive].files[index]
            if not data:
                raise ValueError(f'Missing {name} {label}')
            entries[label] = dict(index=index, bytes=len(data), sha256=sha(data))
        _, messages = decode_messages(archives['text'].files[text])
        entries['messages']['count'] = len(messages)
        maps.append(dict(name=name, map_id=map_id, assets=entries))
    return dict(
        base_sha256=EXPECTED,
        scope='read-only opening asset inspection; no gameplay edits',
        dex_policy=dict(current='National Dex at starter receipt',
                        future='Oak parcel return; deferred by user'),
        new_game_location=dict(
            component='decompressed ARM9 first section',
            offset=arm9.index(initial_location),
            original=[64, -1, 6, 6, 1],
            candidate_map_id=506,
            candidate_coordinates='Must validate collision and stair access in emulator'),
        maps=maps,
        integration_requirements=[
            'Preserve original HeartGold Kanto events and scripts, including Oak VAR_UNK_4131 state checks, for later relocation into the Johto postgame.',
            'Implement the Pallet opening in separate script assets; retain original event logic and dependencies.',
            'Defer destination maps, actor/sprite changes and progression design for preserved Kanto events until Johto postgame implementation.',
            'Keep the National Dex grant at starter receipt in the next opening build.',
            'Initialize the slot-1 follower in Oak lab before exploration resumes.',
            'Provide separate opening home dialogue while preserving existing events; prevent travel with an empty party.',
            'Relocate blackout recovery and home-return backup independently of initial spawn.',
            'Preserve native warp links and validate both directions.',
            'Add first rival battle and starter-dependent rival choices.',
            'Rebalance Route 1 encounters before opening northward progression.',
            'Test fresh saves separately from prototype-001 save data.',
        ],
    )


if __name__ == '__main__':
    report = inspect()
    target = PROJECT / 'opening-assets.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Verified {len(report["maps"])} opening maps; wrote {target}')
