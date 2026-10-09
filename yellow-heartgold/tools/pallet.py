"""Build a separate Pallet opening while preserving original Kanto assets."""
import json
import struct
import subprocess

import ndspy.narc
import ndspy.rom

from build_rom import BASE, EXPECTED, PROJECT, sha
from inspect_opening import MAPS
from prototype import decode_messages, encode_messages, replace_once

PREVIOUS = PROJECT / 'build/yellow-heartgold-prototype-001.nds'
PREVIOUS_SHA = 'afee88f4f55266340c5b69f1f65ecbc324ae3a177407f2be7db9415423538378'


def command(op, *args):
    return struct.pack('<' + 'H' * (1 + len(args)), op, *args)


def message(index):
    return command(45) + bytes([index]) + command(50) + command(53)


def script_bank(scripts):
    header_size = len(scripts) * 4 + 2
    header = bytearray()
    body = bytearray()
    for index, script in enumerate(scripts):
        header.extend(struct.pack('<I', header_size + len(body) - index * 4 - 4))
        body.extend(script)
    return bytes(header + command(0xFD13) + body)


def dialogue(index, heal=False):
    return (command(96) + command(104) + message(index)
            + (command(282) if heal else b'') + command(97) + command(2))


def oak_script():
    # CheckFlag + GoToIf(TRUE). Jump offsets are relative to the end of GoToIf.
    start = command(96) + command(104) + command(32, 0x6A)
    grant = (message(0) + command(167) + command(30, 0x6A)
             + command(605) + bytes([1, 0])
             + command(602, 0) + command(608) + command(3, 10, 0x800C)
             + command(602, 1) + command(354, 0, 0x4001) + command(131, 0x4001)
             + command(291)
             + command(30, 0x6B) + command(477) + bytes([1])
             + command(0x800C) + message(1) + command(97) + command(2))
    repeat = message(2) + command(282) + command(97) + command(2)
    return start + command(28) + bytes([1]) + struct.pack('<i', len(grant)) + grant + repeat


def text_bank(lines):
    mapping = json.loads((PROJECT / 'tools/text-map.json').read_text())
    messages = [[mapping['\\n'] if c == '\n' else mapping[c] for c in line] + [65535]
                for line in lines]
    result = encode_messages(0x1234, messages)
    assert decode_messages(result) == (0x1234, messages)
    return result


def build():
    original = BASE.read_bytes()
    previous = PREVIOUS.read_bytes()
    if sha(original) != EXPECTED or sha(previous) != PREVIOUS_SHA:
        raise ValueError('Expected pristine HeartGold and tested prototype 001')
    rom = ndspy.rom.NintendoDSRom(previous)
    main = rom.loadArm9()
    data = bytes(main.sections[0].data)
    needle = struct.pack('<3H', 740, 513, 451)
    if data.count(needle) != 1:
        raise ValueError('Oak map header is not unique')
    table = data.index(needle) - 6 - 505 * 24
    archives = {path: ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)])
                for path in ['a/0/1/2', 'a/0/2/7', 'a/0/3/2']}
    before = {path: list(arc.files) for path, arc in archives.items()}
    scripts, texts, events = [archives[path] for path in archives]
    changes = []
    updated = bytearray(data)
    for name, map_id, script, header, text, event in MAPS:
        at = table + map_id * 24
        if struct.unpack_from('<3H', data, at + 6) != (script, header, text):
            raise ValueError(f'{name} map table binding mismatch')
        if struct.unpack_from('<H', data, at + 16)[0] != event:
            raise ValueError(f'{name} event table binding mismatch')
        if map_id == 505:
            lines = ['Oak: Welcome! Choose your partner.\nPikachu, Eevee, or Togepi!',
                     'Your partner will follow you!\nHere is your National Pokedex.',
                     'Oak: Let me heal your Pokemon.\nThe adventure is still being built.',
                     'This is a Pallet opening test.\nMore story events are coming.']
            active_scripts = [oak_script()] + [dialogue(3) for _ in range(10)]
        elif map_id == 503:
            lines = ['Welcome home! I will heal\nyour Pokemon. Visit Oak nearby.',
                     'Head downstairs and visit Oak\nin the lab south of your house.']
            active_scripts = [dialogue(0, True), dialogue(1)]
        elif map_id == 506:
            lines = ['Your adventure begins in Pallet.\nVisit Professor Oak in his lab.',
                     'Your room. The stairs are\nin the northeast corner.']
            active_scripts = [dialogue(0), dialogue(1)]
        else:
            lines = ['Welcome to Pallet Town!\nProfessor Oak is in his lab.']
            # Keep every original event's script index valid, without invoking late-game logic.
            original_script = before['a/0/1/2'][script]
            entries = 0
            while struct.unpack_from('<H', original_script, entries * 4)[0] != 0xFD13:
                entries += 1
                if entries * 4 >= len(original_script):
                    raise ValueError('Invalid original script table')
            active_scripts = [dialogue(0) for _ in range(entries)]
        # The Johto mother introduction normally unlocks these menu buttons.
        # This independent transition script also works on save/reload in any opening map.
        init_id = len(active_scripts) + 1
        active_scripts.append(b''.join(command(30, flag) for flag in range(0x11B, 0x11F))
                              + command(2))
        init_header = struct.pack('<BHHB', 2, init_id, 0, 0) + b'\x00\x00'
        new_script = len(scripts.files)
        scripts.files.append(script_bank(active_scripts))
        new_header = len(scripts.files)
        scripts.files.append(init_header)
        new_text = len(texts.files)
        texts.files.append(text_bank(lines))
        new_event = len(events.files)
        events.files.append(before['a/0/3/2'][event])
        struct.pack_into('<3H', updated, at + 6, new_script, new_header, new_text)
        struct.pack_into('<H', updated, at + 16, new_event)
        changes.append(dict(name=name, map_id=map_id, original=[script, header, text, event],
                            active=[new_script, new_header, new_text, new_event]))
    updated = replace_once(bytes(updated), struct.pack('<5i', 64, -1, 6, 6, 1),
                           struct.pack('<5i', 506, -1, 6, 6, 1))
    updated = replace_once(updated, struct.pack('<5i', 60, -1, 695, 397, 1),
                           struct.pack('<5i', 49, -1, 1033, 364, 1))
    # Home recovery remains spawn 1, but its destination now uses the Pallet home.
    spawn = struct.pack('<9H', 0x30B, 63, 0x0806, 60, 695, 397, 60, 695, 397)
    relocated = struct.pack('<9H', 0x30B, 503, 0x0806, 49, 1033, 364, 49, 1033, 364)
    updated = replace_once(updated, spawn, relocated)
    main.sections[0].data = bytearray(updated)
    rom.arm9 = main.save(compress=True)
    for path, archive in archives.items():
        if archive.files[:len(before[path])] != before[path]:
            raise ValueError('An original archive member changed')
        rom.files[rom.filenames.idOf(path)] = archive.save()
    # Oak is the professor in this opening's existing starter selection app.
    text_id = rom.filenames.idOf('a/0/2/7')
    archive = ndspy.narc.NARC(rom.files[text_id])
    key, messages = decode_messages(archive.files[190])
    mapping = json.loads((PROJECT / 'tools/text-map.json').read_text())
    old = [mapping[c] for c in 'Professor Elm']
    new = [mapping[c] for c in 'Professor Oak']
    for line in messages:
        if line[:len(old)] == old:
            line[:len(old)] = new
    archive.files[190] = encode_messages(key, messages)
    rom.files[text_id] = archive.save()
    output = rom.save()
    check = ndspy.rom.NintendoDSRom(output)
    assert check.files == rom.files and check.arm9 == rom.arm9
    pristine = ndspy.rom.NintendoDSRom(original)
    for path, original_indices in [('a/0/1/2', [735, 736, 737, 740, 508, 509, 510, 513]),
                                   ('a/0/2/7', [446, 447, 448, 451]),
                                   ('a/0/3/2', [46, 455, 457, 458])]:
        source = ndspy.narc.NARC(pristine.files[pristine.filenames.idOf(path)])
        built = ndspy.narc.NARC(check.files[check.filenames.idOf(path)])
        for index in original_indices:
            assert source.files[index] == built.files[index], (path, index)
    target = PROJECT / 'build/yellow-heartgold-prototype-002.nds'
    target.write_bytes(output)
    patcher = PROJECT / '.tools/xdelta3'
    patch = target.with_suffix('.xdelta')
    subprocess.run([str(patcher), '-f', '-e', '-S', 'none', '-s', str(BASE), str(target), str(patch)], check=True)
    decoded = target.with_suffix('.roundtrip.nds')
    subprocess.run([str(patcher), '-f', '-d', '-s', str(BASE), str(patch), str(decoded)], check=True)
    assert sha(decoded.read_bytes()) == sha(output)
    decoded.unlink()
    report = dict(build='prototype-002', output_sha256=sha(output), maps=changes,
                  original_kanto_opening_assets_preserved=True, gameplay_verified=False,
                  limitations=['First rival battle not yet added to Pallet',
                               'Route 1 encounters and northward story gates not adapted',
                               'Full Yellow story and Johto postgame not implemented'])
    (target.parent / 'pallet-report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert sha(BASE.read_bytes()) == EXPECTED and sha(PREVIOUS.read_bytes()) == PREVIOUS_SHA
    print(json.dumps(report, indent=2))
    return target


if __name__ == '__main__':
    build()
