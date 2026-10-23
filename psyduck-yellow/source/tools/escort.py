"""Prototype 004: visible Oak escort and field-based starter selection.

Append active map assets; retain every earlier event/script and map model.
HeartGold's native starter app is restored for a later Johto introduction.
"""
import json
import struct
import subprocess

import ndspy.code
import ndspy.narc
import ndspy.rom

from build_rom import BASE, EXPECTED, PROJECT, sha
from opening import (Script, actor, command, end, events_decode, events_encode,
                     encode_text, script_bank, talk, OAK_STATE, RIVAL_STATE,
                     HIDE_TOWN_OAK, HIDE_LAB_OAK, HIDE_RIVAL, OBJ_RIVAL,
                     starter_exit_guard, rival_talk, yellow_dialogue)
import opening
from prototype import OLD, NEW, replace_once

INPUT = PROJECT / 'build/yellow-heartgold-prototype-003.nds'
INPUT_SHA = '1cd5dd980e9c9a542783fe261e5b4b9c59df7b1061e1be2d97f6fa2dd9e635db'
HIDE_ESCORT_OAK = 0xB5A
HIDE_WILD_DUCK = 0xB59
HIDE_CAPTURE_BALL = 0xB58
BALL_FLAGS = [0x300, 0x2FF, 0x2FE]
SPECIES = [54, 175, 133]  # Left, centre, right.
RIVAL_CHOICES = [2, 2, 0]


def music(s, track):
    return s.emit(81, 0).emit(80, track)


def escort():
    s = Script().emit(96).emit(105, 0x4000, 0x4001)
    music(s, 1067).msg(7)
    # Oak is introduced twelve tiles south, outside the camera, then walks in.
    s.emit(31, HIDE_TOWN_OAK).emit(100, 3)
    s.movement(3, 'approach').emit(95)
    for x in [1038, 1039, 1041]:
        s.compare(0x4000, x).jump(f'align_{x}', 1)
    s.jump('greet')
    for x in [1038, 1039, 1041]:
        s.label(f'align_{x}').movement(3, f'align_move_{x}').emit(95).jump('greet')
    s.label('greet').movement(255, 'face_south').emit(95).msg(8)
    # An animated field capture: the wild Psyduck walks out of the northern
    # grass, Oak approaches, throws a ball, waits for its shakes, and collects it.
    music(s, 1116)
    s.emit(31, HIDE_WILD_DUCK).emit(100, 4)
    s.movement(4, 'duck_approach').movement(255, 'face_north').emit(95)
    s.emit(76, 54, 0).emit(77).msg(10)
    for x in [1038, 1039, 1040, 1041]:
        s.compare(0x4000, x).jump(f'capture_{x}', 1)
    for x in [1038, 1039, 1040, 1041]:
        s.label(f'capture_{x}').movement(3, f'capture_move_{x}').emit(95).jump('throw')
    s.label('throw').emit(73, 1802).emit(31, HIDE_CAPTURE_BALL).emit(100, 5)
    s.movement(5, 'ball_throw').emit(95).emit(73, 1510)
    s.emit(30, HIDE_WILD_DUCK).emit(101, 4).emit(3, 20, 0x800C)
    for _ in range(3):
        s.emit(73, 1511).movement(5, 'ball_shake').emit(95).emit(3, 20, 0x800C)
    s.emit(78, 1187).msg(11).emit(79)
    s.movement(3, 'collect_ball').emit(95).emit(30, HIDE_CAPTURE_BALL).emit(101, 5)
    s.emit(41, 0x4168, 1)
    for x in [1038, 1039, 1040, 1041]:
        s.compare(0x4000, x).jump(f'capture_return_{x}', 1)
    for x in [1038, 1039, 1040, 1041]:
        s.label(f'capture_return_{x}').movement(3, f'capture_return_move_{x}').emit(95).jump('follow')
    s.label('follow').movement(255, 'face_south').emit(95).msg(9)
    music(s, 1086)
    # Both actors walk the same town path, with the player one step behind.
    s.movement(3, 'south_three').movement(255, 'south_three').emit(95)
    for x in [1038, 1039, 1041]:
        s.compare(0x4000, x).jump(f'path_{x}', 1)
    s.jump('south_path')
    for x in [1038, 1039, 1041]:
        s.label(f'path_{x}').movement(3, f'path_move_{x}')
        s.movement(255, f'path_move_{x}').emit(95).jump('south_path')
    s.label('south_path').movement(3, 'south_nineteen')
    s.movement(255, 'south_nineteen').emit(95)
    s.movement(255, 'south_one').emit(95)
    s.movement(3, 'east_five').movement(255, 'east_four').emit(95)
    s.emit(73, 1540).movement(3, 'north_two').emit(95)
    # Hide only after Oak reaches the lab doorway. The camera follows the player.
    s.emit(30, HIDE_TOWN_OAK).emit(101, 3)
    s.movement(255, 'door_entry').emit(95)
    s.emit(41, OAK_STATE, 3).emit(30, HIDE_LAB_OAK).emit(31, HIDE_ESCORT_OAK)
    s.emit(174, 6, 6, 0, 0).emit(175)
    s.emit(176, 505, 0, 8, 14, 0)
    s.emit(174, 6, 6, 1, 0).emit(175)
    music(s, 1086)
    s.movement(8, 'indoor_walk').movement(255, 'indoor_walk').emit(95)
    s.movement(8, 'face_south').emit(95)
    # Identical Oak models at the same final tile allow stable normal re-entry.
    s.emit(30, HIDE_ESCORT_OAK).emit(101, 8)
    s.emit(31, HIDE_LAB_OAK).emit(100, 0).emit(41, OAK_STATE, 1)
    s.emit(41,0x416B,2).emit(1).emit(41,0x416B,0)
    music(s, 1103).msg(12).msg(13).msg(14)
    end(s)
    moves = {'approach': [(12, 12)], 'face_south': [(1, 1)],
             'south_three': [(13, 3)], 'south_nineteen': [(13, 19)],
             'south_one': [(13, 1)], 'east_five': [(15, 5)],
             'east_four': [(15, 4)], 'north_two': [(12, 2)],
             'door_entry': [(15, 1), (12, 2)], 'indoor_walk': [(12, 7)],
             'face_north': [(0, 1)], 'duck_approach': [(13, 6), (2, 1)],
             'ball_throw': [(55, 1)], 'ball_shake': [(44, 1)],
             'collect_ball': [(15, 1)]}
    for x in [1038, 1039, 1040, 1041]:
        if x == 1039:
            moves[f'capture_move_{x}'] = [(14, 1), (12, 3), (15, 1), (3, 1)]
            moves[f'capture_return_move_{x}'] = [(14, 2), (13, 3), (15, 1), (0, 1)]
        else:
            moves[f'capture_move_{x}'] = [(15 if x < 1039 else 14, abs(x-1039)), (12, 3), (3, 1)]
            moves[f'capture_return_move_{x}'] = [(14, 1), (13, 3), (14 if x < 1039 else 15, abs(x-1039)), (0, 1)]
    for x in [1038, 1039, 1041]:
        moves[f'align_move_{x}'] = [(14 if x < 1040 else 15, abs(1040-x)), (0, 1)]
        moves[f'path_move_{x}'] = [(15 if x < 1040 else 14, abs(1040-x))]
    for label, entries in moves.items():
        s.moves(label, entries)
    return s.finish()


def oak_talk():
    s = Script().emit(96).emit(104).emit(32, 0x6A).jump('heal', 1)
    s.compare(OAK_STATE, 0).jump('outside', 1).msg(2)
    end(s)
    s.label('outside').msg(15)
    end(s)
    s.label('heal').msg(16).emit(282)
    return end(s).finish()


def ball_choice(index, *, grant_dex=True, rival_override=None, after_properties=None):
    species = SPECIES[index]
    s = Script().emit(96).emit(32, 0x6A).jump('taken', 1)
    s.compare(OAK_STATE, 1).jump('allowed', 1).msg(15)
    end(s)
    s.label('allowed').emit(73, 1500).emit(452, species, 1 if species == 133 else 0).emit(76, species, 0)
    # Leave the question open while the native Yes/No menu is displayed.
    s.emit(45)
    s.data.append(26 + index)
    s.emit(77).emit(63, 0x800C).emit(53).emit(453)
    s.compare(0x800C, 0).jump('accept', 1)
    end(s)
    s.label('accept').emit(73, 1501)
    s.emit(137, species, 5, 0, 0, 0, 0x800C)
    s.compare(0x800C, 1).jump('received', 1).msg(30)
    end(s)
    s.label('received').emit(41, 0x416B, 1).emit(1).emit(41, 0x416B, 0)
    if after_properties is not None:after_properties(s)
    s.emit(30, 0x6A).emit(131, species)
    s.emit(30, BALL_FLAGS[index]).emit(101, 4 + index)
    # A field gift does not return from the native starter application, whose
    # map reload ordinarily creates the follower. Initialize it in place.
    s.emit(41, 0x416B, 3).emit(1).emit(41, 0x416B, 0)
    s.emit(605)
    s.data.extend(bytes([1, 0]))
    s.emit(602, 0).emit(608).emit(3, 10, 0x800C).emit(602, 1)
    s.emit(78, 1187).msg(29 + index * 2).emit(79)
    if grant_dex:
        s.emit(291).emit(30, 0x6B).emit(477)
        s.data.append(1)
        s.emit(0x800C)
    s.msg(3).msg(4).msg(5)
    # Rival walks to his chosen ball, then returns to wait near the exit.
    rival_index = RIVAL_CHOICES[index] if rival_override is None else rival_override
    s.movement(OBJ_RIVAL, 'pickup').emit(95)
    s.msg(6).msg(7).msg(8).msg(9).msg(10)
    s.emit(30, BALL_FLAGS[rival_index]).emit(101, 4 + rival_index)
    s.emit(76, SPECIES[rival_index], 0).emit(77).msg(12 + index if rival_override is None else 14 if rival_index == 0 else 13).msg(11)
    s.movement(OBJ_RIVAL, 'return').emit(95)
    s.emit(41, RIVAL_STATE, 1).emit(41, OAK_STATE, 2)
    end(s)
    s.label('taken').msg(19)
    end(s)
    # Table is on the right; approach from the south, without passing through it.
    target_x = 11 + rival_index
    pickup = [(12, 2), (15, target_x-10), (12, 1), (0, 1)]
    back = [(13, 1), (14, target_x-10), (13, 2), (2, 1)]
    s.moves('pickup', pickup).moves('return', back)
    return s.finish()


def lab_init():
    s = Script().compare(OAK_STATE, 3).jump('escort', 1)
    s.emit(30, HIDE_ESCORT_OAK).compare(OAK_STATE, 0).jump('absent', 1)
    s.emit(31, HIDE_LAB_OAK).jump('rival')
    s.label('absent').emit(30, HIDE_LAB_OAK).jump('rival')
    s.label('escort').emit(30, HIDE_LAB_OAK).emit(31, HIDE_ESCORT_OAK)
    s.label('rival').compare(RIVAL_STATE, 2).jump('gone', 1)
    s.emit(31, HIDE_RIVAL).jump('balls')
    s.label('gone').emit(30, HIDE_RIVAL)
    s.label('balls').emit(32, 0x6A).jump('done', 1)
    for flag in BALL_FLAGS:
        s.emit(31, flag)
    s.label('done').emit(2)
    return s.finish()


def rival_battle(trainers, *, battle_emitter=None):
    # Reuse the proven win/loss handling. Eevee faces Psyduck; both others face Eevee.
    s = Script().emit(96)
    music(s, 1088).movement(OBJ_RIVAL, 'challenge').emit(95)
    s.movement(255, 'face_rival').emit(95).msg(20)
    if battle_emitter is not None:battle_emitter(s,trainers,1,'after')
    else:
        s.emit(206, 0x800C).compare(0x800C, 133).jump('psyduck', 1)
        s.emit(213, trainers[133], 0);s.data.extend(bytes([1, 0]));s.jump('after')
        s.label('psyduck').emit(213, trainers[54], 0);s.data.extend(bytes([1, 0]))
    s.label('after').emit(220, 0x800C).emit(42, opening.RIVAL_BATTLE_RESULT, 0x800C)
    s.compare(0x800C, 1).jump('won', 1).msg(22).jump('outro')
    s.label('won').msg(21)
    s.label('outro').msg(23).emit(41, RIVAL_STATE, 2).emit(282)
    s.movement(OBJ_RIVAL, 'leave').emit(95).emit(30, HIDE_RIVAL).emit(101, OBJ_RIVAL)
    s.emit(82)
    end(s).moves('face_rival', [(1, 1)]).moves('leave', [(13, 2)])
    s.moves('challenge', [(13, 3), (14, 2), (0, 1)])
    return s.finish()


def build():
    prior, original = INPUT.read_bytes(), BASE.read_bytes()
    if sha(prior) != INPUT_SHA or sha(original) != EXPECTED:
        raise ValueError('Expected released 003 and pristine HeartGold')
    rom, pristine = ndspy.rom.NintendoDSRom(prior), ndspy.rom.NintendoDSRom(original)
    original_main = bytes(pristine.loadArm9().sections[0].data)
    table = original_main.index(struct.pack('<3H', 740, 513, 451)) - 6 - 505 * 24
    main = rom.loadArm9()
    data = bytearray(replace_once(bytes(main.sections[0].data), NEW, OLD))
    overlays = rom.loadArm9Overlays()
    overlays[61].data = bytearray(replace_once(bytes(overlays[61].data), NEW, OLD))
    rom.files[overlays[61].fileID] = overlays[61].save(compress=True)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
    paths = ['a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/4/1', 'a/0/6/5', 'a/0/5/5', 'a/0/5/6']
    arcs = {p: ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths}
    before = {p: list(a.files) for p, a in arcs.items()}
    scripts, texts, events, matrices, lands, trdata, trpoke = [arcs[p] for p in paths]
    # Original Johto selection UI/species are retained for later postgame scripting.
    source_texts = ndspy.narc.NARC(pristine.files[pristine.filenames.idOf('a/0/2/7')])
    source_scripts = ndspy.narc.NARC(pristine.files[pristine.filenames.idOf('a/0/1/2')])
    source_parties = ndspy.narc.NARC(pristine.files[pristine.filenames.idOf('a/0/5/6')])
    texts.files[190] = source_texts.files[190]
    for index in [843, 850]:
        scripts.files[index] = source_scripts.files[index]
    for index in [495,496,497]:
        trpoke.files[index] = source_parties.files[index]
    from prototype import decode_messages, encode_messages
    placeholder = [65534, 259, 2, 0, 0]
    y = yellow_dialogue()
    town_lines = [y['_PalletTownGirlText'], y['_PalletTownFisherText'],
                  y['_PalletTownSignText'], y['_PalletTownPlayersHouseSignText'],
                  y['_PalletTownOaksLabSignText'], y['_PalletTownRivalsHouseSignText'],
                  'Head north to begin your adventure.', y['_PalletTownOakHeyWaitDontGoOutText'],
                  y['_PalletTownOakThatWasCloseText'], y['_PalletTownOakComeWithMe'],
                  'OAK: A wild PSYDUCK! Stand back, {PLAYER}!',
                  'OAK caught PSYDUCK!', y['_OaksLabRivalFedUpWithWaitingText'],
                  'OAK: Hmm? {RIVAL}? Why are you here already?\rI said for you to come by later...\rAh, whatever! Just wait there.',
                  'OAK: Choose a POKE BALL from the table.\rPSYDUCK, TOGEPI, or EEVEE can be your partner!']
    # ScriptContext retains its original text bank across the scripted door warp.
    lab_lines = [y['_OaksLabRivalFedUpWithWaitingText'],
                 'OAK: Hmm? {RIVAL}? Why are you here already?\rI said for you to come by later...\rAh, whatever! Just wait there.',
                 'OAK: Choose a POKE BALL from the table.\rPSYDUCK, TOGEPI, or EEVEE can be your partner!',
                 'OAK: Your partner will follow you! Here is your National POKEDEX.',
                 y['_OaksLabRivalWhatAboutMeText'], y['_OaksLabOakBePatientText'],
                 y['_OaksLabRivalTakesText1'], y['_OaksLabRivalTakesText2'],
                 y['_OaksLabRivalTakesText3'], y['_OaksLabRivalTakesText4'],
                 y['_OaksLabRivalTakesText5'], y['_OaksLabRivalMyPokemonLooksStrongerText'],
                 '{RIVAL} chose EEVEE!', '{RIVAL} chose EEVEE!', '{RIVAL} chose PSYDUCK!',
                 'PROF.OAK is outside. Try heading north from PALLET TOWN.',
                 'OAK: Let me heal your POKEMON.', y['_OaksLabRivalGrampsIsntAroundText'],
                 y['_OaksLabRivalIllGetABetterPokemonThanYou'], y['_OaksLabRivalMyPokemonLooksStrongerText'],
                 y['_OaksLabRivalIllTakeYouOnText'], y['_OaksLabRivalIPickedTheWrongPokemonText'],
                 y['_OaksLabRivalAmIGreatOrWhatText'], y['_OaksLabRivalSmellYouLaterText'],
                 y['_OaksLabScientistText'], y['_OaksLabOakDontGoAwayYetText'],
                 'OAK: Do you want PSYDUCK, the Water-type POKEMON?',
                 'OAK: Do you want TOGEPI, the Normal-type POKEMON?',
                 'OAK: Do you want EEVEE, the Normal-type POKEMON?',
                 '{PLAYER} received PSYDUCK!', 'Your party is full.',
                 '{PLAYER} received TOGEPI!', 'Your party is full.',
                 '{PLAYER} received EEVEE!']
    town_init = b''.join(command(30,f) for f in [HIDE_TOWN_OAK,HIDE_WILD_DUCK,HIDE_CAPTURE_BALL])+command(2)
    town_active = [talk(i) for i in range(7)] + [escort(), town_init]
    trainers = {}
    name_key,names = decode_messages(texts.files[729])
    for species in [54,133]:
        trainers[species] = len(trdata.files)
        trainer=bytearray(before['a/0/5/5'][738]);trainer[1]=110
        team=bytearray(before['a/0/5/6'][738]);struct.pack_into('<H',team,4,species)
        trdata.files.append(bytes(trainer));trpoke.files.append(bytes(team))
        names.append(decode_messages(encode_text(['BLUE'],placeholder))[1][0])
    assert trainers == {54:741,133:742}
    texts.files[729]=encode_messages(name_key,names)
    lab_active = [oak_talk()] + [talk(24) for _ in range(10)]
    lab_active += [rival_talk(), rival_battle(trainers), starter_exit_guard(), lab_init()]
    lab_active += [ball_choice(i) for i in range(3)]
    lab_active += [command(41,0x416B,2)+command(1)+command(41,0x416B,0)+command(2)]
    # Clone the lab matrix and land member so its original physical assets stay intact.
    matrix = bytearray(matrices.files[250])
    original_land, = struct.unpack_from('<H', matrix, len(matrix)-2)
    assert original_land == 366
    land = bytearray(lands.files[original_land])
    props_at = 20 + struct.unpack_from('<I', land)[0]
    table_prop = props_at + 7*48
    assert struct.unpack_from('<i', land, table_prop)[0] == 95
    z_at = table_prop + 12
    z, = struct.unpack_from('<i', land, z_at)
    struct.pack_into('<i', land, z_at, z - 16 * 4096)
    # Move the table's solid footprint with its visible model.
    for x in range(11, 14):
        for z in range(5, 9):
            if z == 7:
                struct.pack_into('<H', land, 20 + (z*32+x)*2, 0)
            elif z == 5:
                struct.pack_into('<H', land, 20 + (z*32+x)*2, 0x8000)
    new_land = len(lands.files)
    lands.files.append(bytes(land))
    struct.pack_into('<H', matrix, len(matrix)-2, new_land)
    new_matrix = len(matrices.files)
    matrices.files.append(bytes(matrix))
    mappings = []
    from player_pc import script as player_pc_script, TEXT as player_pc_text
    room_lines = player_pc_text
    room_init = b''.join(command(30, flag) for flag in range(0x11B,0x11F))+command(2)
    room_active = [talk(23),player_pc_script(),room_init]
    for map_id, active, lines, init_id in [(49, town_active, town_lines, 9), (505, lab_active, lab_lines, 15),
                                         (506,room_active,room_lines,3)]:
        at = table + map_id*24
        old_event, = struct.unpack_from('<H', data, at+16)
        groups = events_decode(events.files[old_event])
        if map_id == 49:
            groups[1] = [row if struct.unpack_from('<H', row)[0] != 3
                         else actor(3, 366, 1, 1040, 365, HIDE_TOWN_OAK, 0) for row in groups[1]]
            groups[3] = [opening.trigger(8, 1038, 352, 4, OAK_STATE, 0)]
            groups[1].append(actor(4,1010,1,1040,344,HIDE_WILD_DUCK,1))
            groups[1].append(actor(5,87,1,1039,350,HIDE_CAPTURE_BALL,3))
        elif map_id == 505:
            for i in range(3):
                row = bytearray(actor(4+i, 87, 16+i, 11+i, 6, BALL_FLAGS[i], 0))
                struct.pack_into('<i', row, 28, 0)
                groups[1][4+i] = bytes(row)
            groups[1].append(actor(8, 366, 1, 8, 13, HIDE_ESCORT_OAK, 0))
            # Keep assistants clear of the three balls and rival approach.
            row = bytearray(groups[1][2]);struct.pack_into("<2H", row, 24, 5, 8);groups[1][2] = bytes(row)
            row = bytearray(groups[1][3]);struct.pack_into('<2H', row, 24, 5, 12);groups[1][3] = bytes(row)
            struct.pack_into('<H', data, at+4, new_matrix)
            struct.pack_into('<2H', data, at+12, 1103, 1103)
        else:
            # Original BG event 1 is the Wii at (5,3), event 2 is the PC at (6,3).
            assert [(struct.unpack_from('<H',row)[0],struct.unpack_from('<2i',row,4))
                    for row in groups[0]] == [(1,(5,3)),(2,(6,3))]
        ids = [len(scripts.files), len(scripts.files)+1, len(texts.files), len(events.files)]
        scripts.files.append(script_bank(active))
        scripts.files.append((struct.pack('<BHH',2,init_id,0)+struct.pack('<BHH',3,19,0)+b'\0\0')
                             if map_id == 505 else struct.pack('<BHHB',2,init_id,0,0)+b'\0\0')
        texts.files.append(encode_text(lines, placeholder))
        events.files.append(events_encode(groups))
        struct.pack_into('<3H', data, at+6, *ids[:3])
        struct.pack_into('<H', data, at+16, ids[3])
        mappings.append(dict(map_id=map_id, script=ids[0], init=ids[1], text=ids[2], event=ids[3]))
    main.sections[0].data = data
    from starter_properties import patch as patch_starter_properties
    native_hooks = patch_starter_properties(main)
    rom.arm9 = main.save(compress=True)
    for path, archive in arcs.items():
        for i, old in enumerate(before[path]):
            restored = ((path=='a/0/2/7' and i in [190,729])
                        or (path=='a/0/1/2' and i in [843,850])
                        or (path=='a/0/5/6' and i in [495,496,497]))
            if not restored and archive.files[i] != old:
                raise ValueError(f'Preserved asset modified: {path}/{i}')
        rom.files[rom.filenames.idOf(path)] = archive.save()
    from blue_naming import patch as patch_blue_naming
    blue_naming = patch_blue_naming(rom)
    rom.name = b'PSYDUCK YLW'
    banner=bytearray(rom.iconBanner)
    title='Pokemon Psyduck Yellow\nOpening prototype 004\nCorvus Workshop'.encode('utf-16le')
    for at in range(0x240,0x840,0x100):
        banner[at:at+0x100]=title+b'\0'*(0x100-len(title))
    from ndspy import _common
    struct.pack_into('<H',banner,2,_common.crc16(banner[0x20:0x840]))
    rom.iconBanner=bytes(banner)
    target = PROJECT / 'build/yellow-heartgold-prototype-004.nds'
    output = rom.save();target.write_bytes(output)
    patcher = PROJECT / '.tools/xdelta3'
    subprocess.run([str(patcher), '-f', '-e', '-S', 'none', '-s', str(BASE), str(target), str(target.with_suffix('.xdelta'))], check=True)
    report = dict(build='prototype-004', output_sha256=sha(output), maps=mappings,
                  lab_matrix=new_matrix, lab_land=new_land,
                  original_assets_preserved=True, johto_starter_ui_restored=True,
                  native_starter_hooks=native_hooks,rival_trainers=trainers,blue_naming=blue_naming,
                  capture_presentation='Animated field capture; no dedicated Oak battle back sprite',
                  gameplay_verified=False, save_compatibility='New game required for opening tests')
    (target.parent/'escort-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return target


if __name__ == '__main__':
    build()
