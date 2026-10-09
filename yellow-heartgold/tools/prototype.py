"""Build experimental starter/follower/National Dex patch for US HeartGold."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
import ndspy.code
import ndspy.codeCompression
import ndspy.narc
import ndspy.rom
from build_rom import BASE, EXPECTED, PROJECT, sha

STARTERS = (25, 133, 175)
OLD = struct.pack('<3I', 152, 155, 158)
NEW = struct.pack('<3I', *STARTERS)


def replace_once(data, old, new):
    if data.count(old) != 1:
        raise ValueError('Expected exactly one verified patch site')
    return data.replace(old, new)


def thumb_bl(pc, target):
    displacement = target - pc - 4
    if displacement % 2 or not -(1 << 22) <= displacement < (1 << 22):
        raise ValueError('Invalid Thumb branch displacement')
    return struct.pack('<HH', 0xF000 | ((displacement >> 12) & 0x7FF), 0xF800 | ((displacement >> 1) & 0x7FF))


def decode_messages(data):
    count, key = struct.unpack_from('<HH', data)
    messages = []
    for i in range(count):
        mask = (765 * (i + 1) * key) & 65535
        mask |= mask << 16
        offset, length = struct.unpack_from('<II', data, 4 + i * 8)
        offset ^= mask
        length ^= mask
        assert offset + length * 2 <= len(data)
        seed = ((i + 1) * 596947) & 65535
        words = []
        for word in struct.unpack_from('<' + 'H' * length, data, offset):
            words.append(word ^ seed)
            seed = (seed + 18749) & 65535
        messages.append(words)
    return key, messages


def encode_messages(key, messages):
    header = bytearray(struct.pack('<HH', len(messages), key))
    body = bytearray()
    for i, words in enumerate(messages):
        mask = (765 * (i + 1) * key) & 65535
        mask |= mask << 16
        offset = 4 + len(messages) * 8 + len(body)
        header.extend(struct.pack('<II', offset ^ mask, len(words) ^ mask))
        seed = ((i + 1) * 596947) & 65535
        for word in words:
            body.extend(struct.pack('<H', word ^ seed))
            seed = (seed + 18749) & 65535
    return bytes(header + body)


def patch_text(rom):
    file_id = rom.filenames.idOf('a/0/2/7')
    archive = ndspy.narc.NARC(rom.files[file_id])
    key, messages = decode_messages(archive.files[190])
    assert decode_messages(encode_messages(key, messages)) == (key, messages)
    mapping = json.loads((Path(__file__).parent / 'text-map.json').read_text())
    text = [
        'Professor Elm: Touch a Poke Ball to\nsee what Pokemon is inside!',
        'Professor Elm: Choose PIKACHU,\nthe Electric-type Pokemon?',
        'Professor Elm: Choose EEVEE,\nthe Normal-type Pokemon?',
        'Professor Elm: Choose TOGEPI,\nthe Normal-type Pokemon?',
        'PIKACHU, the Electric-type Pokemon,\nis in this Poke Ball!',
        'EEVEE, the Normal-type Pokemon,\nis in this Poke Ball!',
        'TOGEPI, the Normal-type Pokemon,\nis in this Poke Ball!',
    ]
    for i, line in enumerate(text):
        messages[i] = [mapping['\\n'] if c == '\n' else mapping[c] for c in line] + [65535]
    archive.files[190] = encode_messages(key, messages)
    rom.files[file_id] = archive.save()


def patch_scripts(rom):
    file_id = rom.filenames.idOf('a/0/1/2')
    archive = ndspy.narc.NARC(rom.files[file_id])
    # Replace SetFlag(GOT_STARTER) + ScrCmd605(3,2) with same-size Call + Noop.
    original = struct.pack('<HHHBB', 30, 0x6A, 605, 3, 2)
    script = archive.files[843]
    assert script.count(original) == 1
    site = script.index(original)
    destination = len(script)
    subroutine = (original + struct.pack('<3H', 291, 30, 0x6B)
                  + struct.pack('<HBH', 477, 1, 0x800C) + struct.pack('<H', 27))
    call = struct.pack('<HiH', 26, destination - site - 6, 0)
    archive.files[843] = script[:site] + call + script[site + 8:] + subroutine
    assert site + 6 + struct.unpack_from('<i', call, 2)[0] == destination
    # Preserve first-rival branch selection for each new starter.
    script = archive.files[850]
    for old, new in [(152, 25), (155, 133)]:
        script = replace_once(script, struct.pack('<3H', 17, 0x800C, old), struct.pack('<3H', 17, 0x800C, new))
    archive.files[850] = script
    rom.files[file_id] = archive.save()


def build():
    original = BASE.read_bytes()
    if sha(original) != EXPECTED:
        raise ValueError('Wrong base ROM')
    rom = ndspy.rom.NintendoDSRom(original)
    main = rom.loadArm9()
    section = main.sections[0]
    section.data = bytearray(replace_once(bytes(section.data), OLD, NEW))
    # Replace both follower selectors with literal party slot 0. Empty-party guards remain.
    offset = 0x69A34
    expected = bytes.fromhex('281ceaf78ffc002803d1281ceaf7d6fc02e0281ceaf79efc')
    assert section.data[offset:offset + 24] == expected
    # Main path calls Party_GetMonByIndex(party,0); unused old branch space hosts a tail-call helper.
    replacement = (bytes.fromhex('281c0021') + thumb_bl(0x2069A38, 0x2074644)
                   + bytes.fromhex('06e0c046')
                   + bytes.fromhex('0021014b1847c046') + struct.pack('<I', 0x2074645))
    assert len(replacement) == 24
    section.data[offset:offset + 24] = replacement
    assert section.data[0x69B9E:0x69BA2] == bytes.fromhex('eaf7f3fb')
    section.data[0x69B9E:0x69BA2] = thumb_bl(0x2069B9E, 0x2069A40)
    rom.arm9 = main.save(compress=True)
    overlays = rom.loadArm9Overlays()
    overlay = overlays[61]
    overlay.data = bytearray(replace_once(bytes(overlay.data), OLD, NEW))
    rom.files[overlay.fileID] = overlay.save(compress=True)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
    patch_text(rom)
    patch_scripts(rom)
    # Give Togepi a damaging opening move: Tackle at level 1. Without it a level-5 starter cannot attack.
    file_id = rom.filenames.idOf('a/0/3/3')
    archive = ndspy.narc.NARC(rom.files[file_id])
    assert archive.files[175].startswith(bytes.fromhex('2d02cc02'))
    archive.files[175] = struct.pack('<H', (1 << 9) | 33) + archive.files[175]
    rom.files[file_id] = archive.save()
    # First rival uses another one of the prototype starter species, retaining level 5.
    file_id = rom.filenames.idOf('a/0/5/6')
    archive = ndspy.narc.NARC(rom.files[file_id])
    for trainer, old, new in [(495,152,25),(496,155,133),(497,158,175)]:
        team = bytearray(archive.files[trainer])
        assert len(team) == 8 and struct.unpack_from('<H', team, 4)[0] == old
        struct.pack_into('<H', team, 4, new)
        archive.files[trainer] = bytes(team)
    rom.files[file_id] = archive.save()
    output = rom.save()
    verify = ndspy.rom.NintendoDSRom(output)
    assert verify.files == rom.files
    assert verify.arm9 == rom.arm9 and verify.arm9OverlayTable == rom.arm9OverlayTable
    verified_main = verify.loadArm9()
    loaded = verified_main.sections[0].data
    # MainCodeFile.save updates only the compressed-end pointer in this section.
    pointer = main.codeSettingsOffs + 0x14
    assert loaded[:pointer] == section.data[:pointer]
    assert loaded[pointer + 4:] == section.data[pointer + 4:]
    assert struct.unpack_from('<I', loaded, pointer)[0] == rom.arm9RamAddress + len(rom.arm9)
    assert verify.loadArm9Overlays()[61].data == overlay.data
    baseline = ndspy.rom.NintendoDSRom(original)
    changed = [i for i,(a,b) in enumerate(zip(baseline.files,verify.files)) if a != b]
    expected_files = sorted([overlay.fileID] + [rom.filenames.idOf(p) for p in ['a/0/2/7','a/0/1/2','a/0/3/3','a/0/5/6']])
    assert changed == expected_files, (changed, expected_files)
    target = PROJECT / 'build' / 'yellow-heartgold-prototype-001.nds'
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(output)
    patcher = PROJECT / '.tools/xdelta3'
    if patcher.exists():
        patch = target.with_suffix('.xdelta')
        subprocess.run([str(patcher), '-f', '-e', '-S', 'none', '-s', str(BASE), str(target), str(patch)], check=True)
        patched = target.parent / 'patch-roundtrip.nds'
        subprocess.run([str(patcher), '-f', '-d', '-s', str(BASE), str(patch), str(patched)], check=True)
        assert sha(patched.read_bytes()) == sha(output)
        patched.unlink()
    report = dict(build='prototype-001', input_sha256=EXPECTED, output_sha256=sha(output),
                  output_bytes=len(output), changed_file_ids=changed, starters=list(STARTERS),
                  gameplay_verified=False, location='Original HeartGold opening in New Bark Town',
                  limitations=['Yellow Kanto campaign and Johto scaling not implemented',
                               'Stock map/follower restrictions retained',
                               'Only first rival teams/branches adapted; later story teams remain original'])
    (target.parent / 'prototype-report.json').write_text(json.dumps(report, indent=2)+'\n')
    assert sha(BASE.read_bytes()) == EXPECTED
    print(json.dumps(report, indent=2))
    return target


if __name__ == '__main__':
    build()
