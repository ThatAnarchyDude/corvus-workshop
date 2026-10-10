"""Bounded Yellow opening: Oak intercept, rival gift/exit battle, safe Route 1."""
import json
import re
import struct
import subprocess
import textwrap

import ndspy.narc
import ndspy.rom

from build_rom import BASE, EXPECTED, PROJECT, sha
from pallet import command
from prototype import decode_messages, encode_messages
from intro import patch_intro

INPUT = PROJECT / 'build/yellow-heartgold-prototype-002.nds'
INPUT_SHA = '4c4cac888ba52d4eb3ecce80e045cd7b3e6cc2060d8328bf0617f1bffe12b6ef'
OAK_STATE = 0x416F
RIVAL_STATE = 0x416E
RIVAL_BATTLE_RESULT = 0x416C
HIDE_TOWN_OAK = 0xB5E
HIDE_LAB_OAK = 0xB5C
HIDE_RIVAL = 0xB5F
POTION_GIVEN = 0xB5B
# The entrance grass occupies world rows 345..351. Stop on the first row
# immediately north of it, before the open path and the next grass patch.
ROUTE_GATE_Z = 344
OBJ_RIVAL = 7


class Script:
    def __init__(self):
        self.data = bytearray()
        self.labels = {}
        self.fixups = []

    def emit(self, op, *args):
        self.data.extend(command(op, *args))
        return self

    def label(self, name):
        if name in self.labels:
            raise ValueError('Duplicate label')
        self.labels[name] = len(self.data)
        return self

    def relative(self, target):
        self.fixups.append((len(self.data), target))
        self.data.extend(b'\0' * 4)

    def jump(self, target, condition=None):
        self.emit(22 if condition is None else 28)
        if condition is not None:
            self.data.append(condition)
        self.relative(target)
        return self

    def compare(self, var, value):
        return self.emit(17, var, value)

    def msg(self, index):
        self.emit(190)
        self.data.append(0)  # Player name in string buffer slot 0.
        self.emit(191)
        self.data.append(1)  # Saved rival name in string buffer slot 1.
        self.emit(45)
        self.data.append(index)
        return self.emit(50).emit(53)

    def movement(self, obj, label):
        self.emit(94, obj)
        self.relative(label)
        return self

    def moves(self, label, entries):
        self.data.extend(b'\0' * (-len(self.data) % 4))
        self.label(label)
        for op, count in entries:
            self.emit(op, count)
        return self.emit(254, 0)

    def finish(self):
        for at, label in self.fixups:
            if label not in self.labels:
                raise ValueError(f'Missing label {label}')
            struct.pack_into('<i', self.data, at, self.labels[label] - at - 4)
        return bytes(self.data)


def script_bank(scripts):
    # Native movement commands contain halfwords. Align both script starts and
    # their movement arrays, rather than relying on bytecode length parity.
    header = bytearray(4 * len(scripts) + 4)
    struct.pack_into('<H', header, 4 * len(scripts), 0xFD13)
    body = bytearray()
    for i, script in enumerate(scripts):
        struct.pack_into('<I', header, i * 4, len(header) + len(body) - i * 4 - 4)
        body.extend(script)
        body.extend(b'\0' * (-len(body) % 4))
    return bytes(header + body)


def events_decode(data):
    groups = []
    at = 0
    for size in (20, 32, 12, 16):
        count, = struct.unpack_from('<I', data, at)
        at += 4
        groups.append([data[at + i * size:at + (i + 1) * size] for i in range(count)])
        at += count * size
    if at != len(data) or any(len(row) != size for group, size in zip(groups, (20, 32, 12, 16)) for row in group):
        raise ValueError('Invalid event archive member')
    return groups


def events_encode(groups):
    data = b''.join(struct.pack('<I', len(group)) + b''.join(group) for group in groups)
    if len(data) >= 0x800:
        raise ValueError('Event bank exceeds field buffer')
    assert events_decode(data) == groups
    return data


def actor(obj, sprite, script, x, z, flag=0, facing=1):
    return struct.pack('<6Hh5h2Hi', obj, sprite, 0, 0, flag, script, facing,
                       0, 0, 0, 0, 0, x, z, 0)


def trigger(script, x, z, width, state, value):
    return struct.pack('<Hhh5H', script, x, z, width, 1, 0, value, state)


def yellow_dialogue():
    return json.loads((PROJECT / 'data/yellow-opening-dialogue.json').read_text())['messages']


def encode_text(lines, placeholder):
    mapping = json.loads((PROJECT / 'tools/text-map.json').read_text())
    mapping["'"] = 0x1B3  # HeartGold right-apostrophe glyph.
    messages = []
    for line in lines:
        output = []
        for p, paragraph in enumerate(line.split('\r')):
            if p:
                output.append(0x25BC)
            wrapped = textwrap.wrap(paragraph, width=30, break_long_words=False, break_on_hyphens=False)
            for i, row in enumerate(wrapped):
                if i:
                    # A scroll leaves the cursor on the bottom line. Every
                    # subsequent line must scroll too; another LF goes off-box.
                    output.append(mapping['\\n'] if i == 1 else 0x25BD)
                for token in re.split(r'(\{PLAYER\}|\{RIVAL\})', row):
                    if token == '{PLAYER}':
                        output.extend(placeholder)
                    elif token == '{RIVAL}':
                        output.extend([65534, 259, 2, 1, 0])
                    else:
                        output.extend(mapping[c] for c in token)
        messages.append(output + [65535])
    encoded = encode_messages(0x1234, messages)
    assert decode_messages(encoded)[1] == messages
    return encoded


def end(s):
    return s.emit(97).emit(2)


def talk(index, heal=False):
    s = Script().emit(96).emit(104).msg(index)
    if heal:
        s.emit(282)
    return end(s).finish()


def intercept():
    s = Script().emit(96).emit(105, 0x4000, 0x4001)
    s.emit(39, 0x4001, 2).emit(31, HIDE_TOWN_OAK).emit(100, 3)
    s.emit(339, 3, 0x4000, 0, 0x4001, 0)
    s.msg(7).movement(3, 'oak_approach').emit(95)
    s.movement(255, 'face_oak').emit(95).msg(8).msg(9)
    s.emit(41, OAK_STATE, 1).emit(30, HIDE_TOWN_OAK).emit(101, 3)
    s.emit(176, 505, 0, 8, 10, 0)
    end(s).moves('oak_approach', [(12, 1)]).moves('face_oak', [(1, 1)])
    return s.finish()


def grant():
    s = Script().emit(96).emit(104).emit(32, 0x6A).jump('heal', 1)
    s.compare(OAK_STATE, 0).jump('outside', 1)
    s.msg(0).msg(1).msg(2).emit(167).emit(30, 0x6A)
    s.emit(605)
    s.data.extend(bytes([1, 0]))
    s.emit(602, 0).emit(608).emit(3, 10, 0x800C).emit(602, 1)
    s.emit(354, 0, 0x4001).emit(131, 0x4001)
    s.emit(291).emit(30, 0x6B).emit(477)
    s.data.append(1)
    s.emit(0x800C).msg(3)
    s.msg(4).msg(5).emit(339, OBJ_RIVAL, 7, 0, 4, 0)
    s.msg(6).msg(7).msg(8).msg(9).msg(10).msg(11)
    # Starter-dependent announcement and matching battle party.
    s.emit(206, 0x800C).compare(0x800C, 25).jump('eevee', 1)
    s.compare(0x800C, 133).jump('togepi', 1)
    s.msg(14).jump('picked')
    s.label('eevee').msg(12).jump('picked')
    s.label('togepi').msg(13)
    s.label('picked').emit(339, OBJ_RIVAL, 10, 0, 10, 2)
    s.emit(41, RIVAL_STATE, 1).emit(41, OAK_STATE, 2)
    end(s)
    s.label('outside').msg(15)
    end(s)
    s.label('heal').msg(16).emit(282)
    end(s)
    return s.finish()


def rival_talk():
    s = Script().emit(96).emit(104).compare(OAK_STATE, 0).jump('absent', 1)
    s.compare(RIVAL_STATE, 1).jump('stronger', 1).msg(18)
    end(s)
    s.label('absent').msg(17)
    end(s)
    s.label('stronger').msg(19)
    return end(s).finish()


def battle(trainers):
    s = Script().emit(96).emit(339, OBJ_RIVAL, 8, 0, 13, 0)
    s.movement(255, 'face_rival').emit(95).msg(20)
    s.emit(206, 0x800C).compare(0x800C, 25).jump('eevee', 1)
    s.compare(0x800C, 133).jump('togepi', 1)
    branches = [('pika', trainers[25]), ('eevee', trainers[133]), ('togepi', trainers[175])]
    for i, (label, trainer) in enumerate(branches):
        s.label(label).emit(213, trainer, 0)
        s.data.extend(bytes([1, 0]))  # Native first-rival battle permits a loss without blackout.
        s.jump('after')
    s.label('after').emit(220, 0x800C).emit(42, RIVAL_BATTLE_RESULT, 0x800C)
    s.compare(0x800C, 1).jump('won', 1)
    s.msg(22).jump('outro')
    s.label('won').msg(21)
    s.label('outro').msg(23).emit(41, RIVAL_STATE, 2).emit(282)
    s.movement(OBJ_RIVAL, 'leave').emit(95).emit(30, HIDE_RIVAL).emit(101, OBJ_RIVAL)
    end(s).moves('face_rival', [(1, 1)]).moves('leave', [(13, 1)])
    return s.finish()


def lab_init():
    s = Script().compare(OAK_STATE, 0).jump('no_oak', 1)
    s.emit(31, HIDE_LAB_OAK).jump('rival')
    s.label('no_oak').emit(30, HIDE_LAB_OAK)
    s.label('rival').compare(RIVAL_STATE, 2).jump('gone', 1)
    s.emit(31, HIDE_RIVAL).emit(2)
    s.label('gone').emit(30, HIDE_RIVAL).emit(2)
    return s.finish()


def gate():
    s = Script().emit(96).msg(4).movement(255, 'back').emit(95)
    end(s).moves('back', [(13, 1)])
    return s.finish()


def starter_exit_guard():
    s = Script().emit(96).msg(25).movement(255, 'back_to_oak').emit(95)
    end(s).moves('back_to_oak', [(12, 1)])
    return s.finish()


def potion():
    s = Script().emit(96).emit(104).emit(32, POTION_GIVEN).jump('again', 1)
    s.msg(0).emit(125, 17, 1, 0x800C).compare(0x800C, 0).jump('no_room', 1)
    s.emit(30, POTION_GIVEN).msg(1)
    s.label('again').msg(2)
    end(s)
    s.label('no_room').msg(5)
    return end(s).finish()


def build():
    original, prior = BASE.read_bytes(), INPUT.read_bytes()
    if sha(original) != EXPECTED or sha(prior) != INPUT_SHA:
        raise ValueError('Expected exact base ROM and released prototype 002')
    rom, pristine = ndspy.rom.NintendoDSRom(prior), ndspy.rom.NintendoDSRom(original)
    original_main = bytes(pristine.loadArm9().sections[0].data)
    table = original_main.index(struct.pack('<3H', 740, 513, 451)) - 6 - 505 * 24
    main = rom.loadArm9()
    data = bytearray(main.sections[0].data)
    paths = ['a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/5/5', 'a/0/5/6', 'a/0/3/7']
    archives = {p: ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    before = {p: list(a.files) for p, a in archives.items()}
    scripts, texts, events, trdata, trpoke, wild = [archives[p] for p in paths]
    _, messages = decode_messages(texts.files[451])
    at = messages[0].index(65534)
    placeholder = messages[0][at:at + 5]
    assert placeholder == [65534, 259, 2, 0, 0]
    intro = patch_intro(rom, texts, encode_text, placeholder)
    trainers = {}
    key, names = decode_messages(texts.files[729])
    if len(names) != len(trdata.files) or len(trdata.files) != len(trpoke.files):
        raise ValueError('Trainer names/data/party counts disagree')
    encoded_rival = decode_messages(encode_text(['RIVAL'], placeholder))[1][0]
    for species, original_id in [(25, 495), (133, 496), (175, 497)]:
        trainers[species] = len(trdata.files)
        trainer = bytearray(before['a/0/5/5'][original_id])
        trainer[1] = 23  # TRAINERCLASS_RIVAL uses the saved rival name in battles.
        trdata.files.append(bytes(trainer))
        trpoke.files.append(before['a/0/5/6'][original_id])
        names.append(encoded_rival)
        assert struct.unpack_from('<2H', trpoke.files[-1], 2) == (5, species)
    texts.files[729] = encode_messages(key, names)
    y = yellow_dialogue()
    town_lines = [y['_PalletTownGirlText'], y['_PalletTownFisherText'],
                  y['_PalletTownSignText'], y['_PalletTownPlayersHouseSignText'],
                  y['_PalletTownOaksLabSignText'], y['_PalletTownRivalsHouseSignText'],
                  'Head north to begin your adventure.', y['_PalletTownOakHeyWaitDontGoOutText'],
                  y['_PalletTownOakThatWasCloseText'], y['_PalletTownOakComeWithMe']]
    town_scripts = [talk(i) for i in range(7)] + [intercept(), command(30, HIDE_TOWN_OAK) + command(2)]
    lab_lines = [y['_OaksLabRivalFedUpWithWaitingText'],
                 'OAK: Hmm? {RIVAL}? Why are you here already?\rI said for you to come by later...\rAh, whatever! Just wait there.',
                 'OAK: Look, {PLAYER}! Choose your partner: PIKACHU, EEVEE, or TOGEPI!',
                 'OAK: Your partner will follow you! Here is your National POKEDEX.',
                 y['_OaksLabRivalWhatAboutMeText'], y['_OaksLabOakBePatientText'],
                 y['_OaksLabRivalTakesText1'], y['_OaksLabRivalTakesText2'],
                 y['_OaksLabRivalTakesText3'], y['_OaksLabRivalTakesText4'],
                 y['_OaksLabRivalTakesText5'], y['_OaksLabRivalMyPokemonLooksStrongerText'],
                 '{RIVAL} chose EEVEE!', '{RIVAL} chose TOGEPI!', '{RIVAL} chose PIKACHU!',
                 'PROF.OAK is outside. Try heading north from PALLET TOWN.',
                 'OAK: Let me heal your POKEMON.', y['_OaksLabRivalGrampsIsntAroundText'],
                 y['_OaksLabRivalIllGetABetterPokemonThanYou'], y['_OaksLabRivalMyPokemonLooksStrongerText'],
                 y['_OaksLabRivalIllTakeYouOnText'], y['_OaksLabRivalIPickedTheWrongPokemonText'],
                 y['_OaksLabRivalAmIGreatOrWhatText'], y['_OaksLabRivalSmellYouLaterText'],
                 y['_OaksLabScientistText'], y['_OaksLabOakDontGoAwayYetText']]
    lab_scripts = [grant()] + [talk(24) for _ in range(10)] + [rival_talk(), battle(trainers), starter_exit_guard(), lab_init()]
    route_lines = [y['_Route1Youngster1MartSampleText'], '{PLAYER} got POTION!',
                   y['_Route1Youngster1AlsoGotPokeballsText'], y['_Route1SignText'],
                   'The path ahead is closed for this PALLET TOWN opening test.',
                   y['_Route1Youngster1NoRoomText'], y['_Route1Youngster2Text']]
    route_scripts = [potion(), talk(6), talk(3), gate()]
    mappings = []
    parked = []
    for map_id, lines, active, init_id in [(49, town_lines, town_scripts, 9),
                                          (505, lab_lines, lab_scripts, 15),
                                          (9, route_lines, route_scripts, None)]:
        record = table + map_id * 24
        old_events, = struct.unpack_from('<H', data, record + 16)
        groups = events_decode(events.files[old_events])
        if map_id == 49:
            # Cameron has no Yellow opening counterpart; retain him only in the original asset.
            groups[1] = [row for row in groups[1] if struct.unpack_from('<H', row)[0] != 2]
            groups[1].append(actor(3, 366, 1, 1038, 354, HIDE_TOWN_OAK, 0))
            groups[3] = [trigger(8, 1024, 352, 32, OAK_STATE, 0)]
        elif map_id == 505:
            oak = bytearray(groups[1][0])
            struct.pack_into('<H', oak, 8, HIDE_LAB_OAK)
            groups[1][0] = bytes(oak)
            # Blue's HeartGold overworld model, independent of his original Kanto events.
            groups[1].append(actor(OBJ_RIVAL, 375, 12, 10, 10, HIDE_RIVAL, 2))
            groups[3] = [trigger(13, 7, 12, 3, RIVAL_STATE, 1),
                         trigger(14, 7, 12, 3, OAK_STATE, 1)]
        else:
            parked = [row.hex() for row in groups[1] if struct.unpack_from('<H', row, 6)[0] == 1]
            assert len(parked) == 4
            # Yellow's two non-battling youngsters replace the HG route actors in this copy.
            groups[1] = [actor(0, 146, 1, 1039, 347), actor(1, 146, 2, 1039, 321)]
            groups[0] = [struct.pack('<HHiiiH2x', 3, 1, 1037, 338, 0, 4)]
            groups[3] = [trigger(4, 1024, ROUTE_GATE_Z, 32, 0x416D, 0)]
        script_id = len(scripts.files)
        scripts.files.append(script_bank(active))
        init = (struct.pack('<BHHB', 2, init_id, 0, 0) + b'\0\0') if init_id else b'\0\0\0\0'
        header_id = len(scripts.files)
        scripts.files.append(init)
        text_id = len(texts.files)
        texts.files.append(encode_text(lines, placeholder))
        event_id = len(events.files)
        events.files.append(events_encode(groups))
        struct.pack_into('<3H', data, record + 6, script_id, header_id, text_id)
        struct.pack_into('<H', data, record + 16, event_id)
        mappings.append(dict(map_id=map_id, script=script_id, init=header_id, text=text_id, event=event_id))
    # Yellow's Route 1 grass table, adapted from 10 Gen-I slots to 12 HG slots.
    # Weighted pairs preserve the original 20/20/15/10/10/10/5/5/4/1 percentages.
    encounters = bytearray(wild.files[111])
    encounters[0] = 25
    levels = [3, 4, 2, 3, 2, 3, 2, 5, 4, 6, 4, 7]
    species = [16, 16, 19, 19, 16, 16, 19, 16, 19, 16, 19, 16]
    encounters[8:20] = bytes(levels)
    for period in range(3):
        struct.pack_into('<12H', encounters, 20 + period * 24, *species)
    struct.pack_into('<2H', encounters, 0x5C, 16, 19)
    struct.pack_into('<2H', encounters, 0x60, 16, 19)
    struct.pack_into('<H', encounters, 0xBC, 16)
    wild.files[111] = bytes(encounters)
    main.sections[0].data = data
    rom.arm9 = main.save(compress=True)
    for path, archive in archives.items():
        allowed = {219, 729} if path == 'a/0/2/7' else ({111} if path == 'a/0/3/7' else set())
        for i, old in enumerate(before[path]):
            if i not in allowed and archive.files[i] != old:
                raise ValueError(f'Original asset changed: {path}/{i}')
        rom.files[rom.filenames.idOf(path)] = archive.save()
    output = rom.save()
    check = ndspy.rom.NintendoDSRom(output)
    assert check.files == rom.files and check.arm9 == rom.arm9
    assert check.arm9OverlayTable == rom.arm9OverlayTable
    assert sha(check.loadArm9Overlays()[53].data) == intro['output_overlay_sha256']
    target = PROJECT / 'build/yellow-heartgold-prototype-003.nds'
    target.write_bytes(output)
    patcher = PROJECT / '.tools/xdelta3'
    subprocess.run([str(patcher), '-f', '-e', '-S', 'none', '-s', str(BASE), str(target), str(target.with_suffix('.xdelta'))], check=True)
    decoded = target.with_suffix('.roundtrip.nds')
    subprocess.run([str(patcher), '-f', '-d', '-s', str(BASE), str(target.with_suffix('.xdelta')), str(decoded)], check=True)
    assert sha(decoded.read_bytes()) == sha(output)
    decoded.unlink()
    report = dict(build='prototype-003', input_sha256=EXPECTED, prior_prototype_sha256=INPUT_SHA,
                  output_sha256=sha(output), output_bytes=len(output), maps=mappings,
                  rival_naming=intro,
                  rival_trainers=trainers, route_1_preserved_trainer_records=parked,
                  boundary_z=ROUTE_GATE_Z, original_events_preserved=True,
                  wild_levels=levels, wild_species=species,
                  saved_state_registry={'oak_intercept':OAK_STATE,'rival_gift_battle':RIVAL_STATE,
                                        'route_boundary':0x416D,'potion_received':POTION_GIVEN,
                                        'first_rival_battle_won':RIVAL_BATTLE_RESULT},
                  limitations=['Pallet and first Route 1 grass only; northward travel blocked',
                               'Oak escort uses a transition to his lab; full Pikachu capture scene not implemented',
                               'Battle portrait retains HG rival presentation; overworld uses Blue',
                               'Three-starter gift chronology differs from Yellow forced Eevee theft',
                               'Existing prototype-002 saves require a new game for the new opening'])
    (target.parent / 'opening-report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert sha(BASE.read_bytes()) == EXPECTED and sha(INPUT.read_bytes()) == INPUT_SHA
    print(json.dumps(report, indent=2))
    return target


if __name__ == '__main__':
    build()
