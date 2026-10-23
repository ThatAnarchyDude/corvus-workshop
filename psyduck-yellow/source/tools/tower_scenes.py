"""Pokemon Tower story scenes: 2F rival, 7F Jessie/James and Mr. Fuji's Poke Flute.

Teams and dialogue are Yellow's. Positions are inside the part of each floor the player arrives in
(Bell Tower's land data is only partly understood), so every scene is reachable from the stairs.
"""
import re
import struct
from pathlib import Path
import ndspy.narc
from opening import Script, actor, events_decode, encode_text, end, script_bank
from parcel_quest import PH, split_bank
from prototype import decode_messages, encode_messages
from forest_progression import expanded_common
from progression_cleanup import selected_battle
from escort import music
import blue_properties_shared as shared
import yellow_text

RIVAL_DONE, JJ_HIDE, FUJI_FLAG = 0xA77, 0xA75, 0xA73
RIVAL_STATE, JJ_STATE, GHOST_STATE = 0x4171, 0x4172, 0x4173     # no native script or actor references any of them
GHOST_DONE = 0xA74
SILPH_SCOPE = 874                                # hg-engine already has the item
MAROWAK_ALOLAN = 1143                            # SPECIES_MAROWAK_ALOLAN; the ghost's battle sprite and typing
GHOST_LEVEL = 30
RIVAL_SPRITE, JESSIE_SPRITE, JAMES_SPRITE, FUJI_SPRITE = 375, 221, 222, 317
POKE_FLUTE = 651
PATHS = ('a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/5/5', 'a/0/5/6', 'a/0/5/7', 'a/1/3/1')
RIVAL_ROOM = dict(trigger=(10, 23, 8, 5), rival=(12, 24, 3))          # 2F: the room the stairs arrive in
GHOST_ROOM = dict(trigger=(14, 24, 3, 2), back=3)         # 6F: platform in front of the stairs up to 7F
JJ_ROOM = dict(trigger=(5, 12, 4, 3), jessie=(6, 16), james=(7, 16), fuji=(6, 19))   # 7F: arrival platform and the 2-wide corridor below it


class Yellow:
    """Read-only pret/pokeyellow data."""

    def __init__(self, source):
        self.root = Path(source)
        read = lambda p: (self.root / p).read_text()
        dex = re.findall(r'^\s*const\s+DEX_(\w+)', read('constants/pokedex_constants.asm'), re.M)
        self.species = {n: i + 1 for i, n in enumerate(dex)}
        self.moves = {n: i for i, n in enumerate(re.findall(r'^\s*const\s+(\w+)', read('constants/move_constants.asm'), re.M))}
        assert len(dex) == 151 and self.moves['TACKLE'] == 33
        self.parties, self.evos = read('data/trainers/parties.asm'), read('data/pokemon/evos_moves.asm')

    def mon(self, name, level):
        base = (self.root / 'data/pokemon/base_stats' / (name.lower().replace('_', '') + '.asm')).read_text()
        initial = re.search(r'db\s+([^;\n]+); level 1 learnset', base).group(1)
        learned = [m.strip() for m in initial.split(',') if m.strip() != 'NO_MOVE']
        label = name.title().replace('_', '') + 'EvosMoves'
        learnset = re.search(r'^' + label + r':\s*\n(.*?)(?=^\w+EvosMoves:|\Z)', self.evos, re.M | re.S).group(1).split('; Learnset')[1]
        for lv, move in re.findall(r'^\s*db\s+(\d+),\s*(\w+)', learnset, re.M):
            if int(lv) <= level and move not in learned:
                learned = (learned + [move])[-4:]
        return dict(species=self.species[name], level=level, moves=[self.moves[m] for m in learned] + [0] * (4 - len(learned)))

    def block(self, label):
        return re.search(r'^' + label + r':\s*\n(.*?)(?=^\w+Data:|\Z)', self.parties, re.M | re.S).group(1)

    def class_party(self, label, index):
        """Plain-format class party (`db level, MON, ...`), 1-based index within the class block, with learnset moves."""
        row = [v.strip() for v in re.findall(r'^\s*db\s+([^;\n]+)', self.block(label), re.M)[index - 1].split(',')]
        assert row[0] != '$FF' and row[-1] == '0'
        return [self.mon(n, int(row[0])) for n in row[1:-1]]

    def leader_party(self, label, index=0):
        row = [v.strip() for v in re.findall(r'^\s*db\s+([^;\n]+)', self.block(label), re.M)[index].split(',')]
        assert row[0] == '$FF' and row[-1] == '0'
        return [self.mon(row[i + 1], int(row[i])) for i in range(1, len(row) - 1, 2)]

    def rival_team(self, index):
        row = [v.strip() for v in re.findall(r'^\s*db\s+([^;\n]+)', self.block('Rival2Data'), re.M)[index].split(',')]
        assert row[0] == '$FF' and row[-1] == '0'
        return [(int(row[i]), row[i + 1]) for i in range(1, len(row) - 1, 2)]

    def tower_rockets(self):
        return self.rocket_by_comment('Pok.mon Tower 7F')

    def rocket_by_comment(self, comment):
        row = re.search(r'^\s*db\s+([^;\n]+);\s*' + comment, self.block('RocketData'), re.M).group(1)
        row = [v.strip() for v in row.split(',')]
        assert row[-1] == '0'
        return [self.mon(n, int(row[0])) for n in row[1:-1]]


def _helper(first, extra, address):
    """shared.helper with one more Blue-style trainer range."""
    return shared.assemble(f'''movs r0,r3
ldr r1,old_first
subs r0,r0,r1
cmp r0,#9
bls yes
movs r0,r3
ldr r1,cerulean_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,r3
ldr r1,ship_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,r3
ldr r1,tower_first
subs r0,r0,r1
cmp r0,#3
bls yes
movs r0,#0
bx lr
yes:
movs r0,#1
bx lr
.align 2
old_first: .word 741
cerulean_first: .word 782
ship_first: .word {first}
tower_first: .word {extra}
''', address)


OLD_WRAPPER_BYTES = 368        # the retired Blue wrapper at shared.OLD; later patches reuse its first 108 bytes
FREE_FROM = 108


def _extend_hook(rom, tower_first):
    """Move the Blue eligibility helper into the retired wrapper's still-dead tail and give it a fourth range.

    The helper cannot grow in place (other patches reuse the bytes after it), so it is rebuilt at
    OLD+108 and the guard's BL is repointed. The ITCM length does not change.
    """
    main = rom.loadArm9()
    itcm = main.sections[1]
    assert len(itcm.data) == 32756
    base = itcm.ramAddress
    source = (Path(__file__).resolve().parents[1] / 'asm/blue-starter-properties.s').read_text()
    source = source.replace('bl 0x0201FD44\nlsls r0, r0, #20', 'bl 0x01FFCA64\nlsls r0, r0, #20').replace('cmp r0, #8', 'cmp r0, #16')
    dead = shared.assemble(source, shared.OLD)
    assert len(dead) == OLD_WRAPPER_BYTES
    at = shared.OLD - base
    assert bytes(itcm.data[at:at + len(shared.helper(809))]) == shared.helper(809), 'Blue starter hook is not the expected 0040 helper'
    assert bytes(itcm.data[at + FREE_FROM:at + OLD_WRAPPER_BYTES]) == dead[FREE_FROM:], 'retired wrapper tail is no longer dead'
    target = shared.OLD + FREE_FROM
    new = _helper(809, tower_first, target)
    assert len(new) <= OLD_WRAPPER_BYTES - FREE_FROM
    guard_at = shared.GUARD - base
    old_guard = shared.assemble(f'bl {shared.OLD}\ncmp r0,#0\nbne {shared.ELIGIBLE}\nb {shared.FINISHED}', shared.GUARD)
    assert bytes(itcm.data[guard_at:guard_at + len(old_guard)]) == old_guard
    # Nothing may call or point into the tail being reused.
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    lo, hi = target, shared.OLD + OLD_WRAPPER_BYTES
    blocks = [(s.ramAddress, bytes(s.data)) for s in main.sections] + [(o.ramAddress, bytes(o.data)) for o in rom.loadArm9Overlays().values()]
    for address, raw in blocks:
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        decoder.skipdata = True
        for insn in decoder.disasm(raw, address):
            if lo <= insn.address < hi:
                continue
            if insn.mnemonic in ('bl', 'blx', 'b') and insn.op_str.startswith('#'):
                assert not lo <= int(insn.op_str[1:], 0) < hi, hex(insn.address)
        for offset in (0, 2):
            for n, (value,) in enumerate(struct.iter_unpack('<I', raw[offset:len(raw) - ((len(raw) - offset) % 4)])):
                assert not lo <= value & ~1 < hi or lo <= address + offset + n * 4 < hi, hex(address + offset + n * 4)
    itcm.data = bytearray(itcm.data)
    itcm.data[at + FREE_FROM:at + FREE_FROM + len(new)] = new
    new_guard = shared.assemble(f'bl {target}\ncmp r0,#0\nbne {shared.ELIGIBLE}\nb {shared.FINISHED}', shared.GUARD)
    assert len(new_guard) == len(old_guard)
    itcm.data[guard_at:guard_at + len(new_guard)] = new_guard
    rom.arm9 = main.save(compress=True)
    return dict(helper=hex(target), bytes=len(new))


def _cover_common(rom, last_trainer):
    """Point the trainer-vision/common script aliases (3000/5000 sites) at a bank covering new trainer ids."""
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    sites = []
    for trigger in (3000, 5000):
        matches = [at for at in range(0, len(d) - 6, 2) if struct.unpack_from('<H', d, at)[0] == trigger
                   and struct.unpack_from('<H', d, at + 4)[0] == 40 and struct.unpack_from('<H', d, at + 2)[0] < len(scripts.files)]
        assert len(matches) == 1
        sites.append(matches[0])
    original = struct.unpack_from('<H', d, sites[0] + 2)[0]
    common = len(scripts.files)
    scripts.files.append(expanded_common(scripts.files[original], last_trainer))
    for at in sites:
        struct.pack_into('<H', d, at + 2, common)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.arm9 = main.save(compress=True)


class TrainerBook:
    """Append-only access to the trainer record, party, name, message and message-table archives."""

    def __init__(self, rom):
        self.rom = rom
        self.arcs = [ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in PATHS]
        self.scripts, self.texts, self.events, self.trainers, self.parties, self.trtable, self.offsets = self.arcs
        self.namekey, self.names = decode_messages(self.texts.files[729])
        self.textkey, self.lines = decode_messages(self.texts.files[728])
        self.table, self.ofs = bytearray(self.trtable.files[0]), bytearray(self.offsets.files[0])
        assert len(self.names) == len(self.trainers.files) == len(self.parties.files)

    def assert_unused(self, values):
        for v in values:
            assert not any(struct.pack('<H', v) in raw for raw in self.scripts.files), hex(v)
            assert not any(struct.pack('<H', v) in a for raw in self.events.files for g in events_decode(raw) for a in g), hex(v)

    def new(self, template, party_bytes, dialogue, name, count):
        tid = len(self.trainers.files)
        row = bytearray(self.trainers.files[template])
        row[0], row[3], row[4:12], row[16] = 1, count, bytes(8), 0
        struct.pack_into('<I', row, 12, 1)
        self.trainers.files.append(bytes(row))
        self.parties.files.append(party_bytes)
        self.names.append(name)
        while len(self.ofs) < 2 * (tid + 1):
            self.ofs.extend(struct.pack('<H', len(self.table)))
        struct.pack_into('<H', self.ofs, tid * 2, len(self.table))
        for kind, text in enumerate(dialogue):
            self.table.extend(struct.pack('<2H', tid, kind))
            self.lines.extend(decode_messages(encode_text([text], PH))[1])
        assert 0x550 + tid < 0xB60 and tid < 1000
        return tid

    def save(self):
        self.texts.files[729], self.texts.files[728] = encode_messages(self.namekey, self.names), encode_messages(self.textkey, self.lines)
        self.trtable.files[0], self.offsets.files[0] = bytes(self.table), bytes(self.ofs)
        for path, arc in zip(PATHS, self.arcs):
            self.rom.files[self.rom.filenames.idOf(path)] = arc.save()


def add_trainers(rom, source):
    """Four Blue-style rival records (Psyduck/Eevee x gender) and the Jessie & James record."""
    yellow = Yellow(source)
    book = TrainerBook(rom)
    book.assert_unused((RIVAL_DONE, JJ_HIDE, RIVAL_STATE, JJ_STATE, GHOST_DONE, GHOST_STATE))
    trainers, names, new = book.trainers, book.names, book.new

    t = yellow_text.message
    rival_text = [t(source, 'PokemonTower2F', '_PokemonTower2FRival' + x + 'Text') for x in ('WhatBringsYouHere', 'Defeated', 'Victory', 'HowsYourDex')]
    first, ids = len(trainers.files), {}
    pairs = yellow.rival_team(1)                       # Pokemon Tower 2F; the starter slot is last (Eevee)
    for species in (54, 133):
        for gender, value in (('male', 1), ('female', 2)):
            team = [yellow.mon(n, lv) | dict(gender=0) for lv, n in pairs[:-1]]
            level = pairs[-1][0]
            starter = yellow.mon('PSYDUCK' if species == 54 else 'EEVEE', level) | dict(gender=value)
            starter['species'] = species
            body = b''.join(struct.pack('<BB3H4H', 0, m['gender'], m['level'], m['species'], 0, *m['moves']) for m in team + [starter])
            ids[f'{species}_{gender}'] = new(742, body, [rival_text[0], rival_text[1], rival_text[3]], names[742], len(team) + 1)
    ids[54], ids[133] = ids['54_male'], ids['133_female']
    assert ids['54_male'] == first
    jj_team = yellow.tower_rockets()
    jj_text = [t(source, 'PokemonTower7F', f'_PokemonTowerJessieJamesText{i}') for i in (2, 3, 4)]
    jj_body = b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in jj_team)
    assert trainers.files[777][1] == 129
    jj = new(777, jj_body, jj_text, names[777], len(jj_team))
    book.save()
    _cover_common(rom, jj)
    hook_bytes = _extend_hook(rom, first)
    return dict(rival=ids, rival_first=first, jessie_james=jj, jj_team=jj_team, hook_bytes=hook_bytes, rival_team=pairs)


def _attach(rom, rec, lines, scripts_new):
    """Give the floor a fresh text bank and a script bank = its old scripts + scripts_new. Returns (first entry, bank id)."""
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    texts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    key = decode_messages(texts.files[struct.unpack_from('<H', rec, 10)[0]])[0]
    bank = split_bank(scripts.files[struct.unpack_from('<H', rec, 6)[0]])
    entry = len(bank) + 1
    bank.extend(scripts_new)
    encoded = []
    for line in lines:
        encoded.extend(decode_messages(encode_text([line], PH))[1])
    scripts.files.append(script_bank(bank))
    texts.files.append(encode_messages(key, encoded))
    struct.pack_into('<H', rec, 6, len(scripts.files) - 1)
    struct.pack_into('<H', rec, 10, len(texts.files) - 1)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.files[rom.filenames.idOf('a/0/2/7')] = texts.save()
    return entry


def rival_scripts(trainers):
    s = Script().emit(96)
    music(s, 1088).msg(0)
    selected_battle(s, trainers, 1, 'result')       # owner-approved optional battle: a loss heals the party
    s.label('result').emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.msg(1).jump('outro')
    s.label('lost').msg(2)
    s.label('outro').msg(3)
    music(s, 1089).emit(30, RIVAL_DONE).emit(41, RIVAL_STATE, 1).emit(81, 0).emit(82)
    end(s)
    return [s.finish(), Script().emit(96).emit(104).msg(3).emit(97).emit(2).finish()]


def floor2(rom, rec, g, trainers, source):
    """Rival waits in the arrival room; stepping into it starts the Yellow battle."""
    lines = [yellow_text.message(source, 'PokemonTower2F', '_PokemonTower2FRival' + x + 'Text') for x in ('WhatBringsYouHere', 'Defeated', 'Victory', 'HowsYourDex')]
    entry = _attach(rom, rec, lines, rival_scripts(trainers))
    x, z, facing = RIVAL_ROOM['rival']
    g[1].append(actor(len(g[1]), RIVAL_SPRITE, entry + 1, x, z, 0, facing))
    tx, tz, w, h = RIVAL_ROOM['trigger']
    g[3].append(struct.pack('<Hhh5H', entry, tx, tz, w, h, 0, 0, RIVAL_STATE))
    return dict(entry=entry, actor=(x, z), trigger=RIVAL_ROOM['trigger'])


def jj_scripts(trainer, first_msg):
    m = first_msg
    s = Script().emit(96)
    music(s, 1112).msg(m).msg(m + 1)
    s.emit(213, trainer, 0)
    s.data.extend(bytes(2))
    s.emit(220, 0x800C).compare(0x800C, 1).jump('lost', 5)
    s.emit(36, trainer)
    music(s, 1112).msg(m + 2).msg(m + 3)
    s.emit(30, JJ_HIDE).emit(101, 0).emit(101, 1).emit(41, JJ_STATE, 1).emit(81, 0).emit(82)
    end(s)
    s.label('lost').emit(219)
    end(s)
    stand = Script().emit(96).emit(104).msg(m).emit(97).emit(2).finish()
    return s.finish(), stand


def fuji_script(first_msg):
    m = first_msg
    s = Script().emit(96).emit(104).emit(32, FUJI_FLAG).jump('again', 1)
    s.msg(m).msg(m + 1).emit(125, POKE_FLUTE, 1, 0x800C).compare(0x800C, 0).jump('full', 1)
    s.emit(30, FUJI_FLAG).msg(m + 2).msg(m + 3).emit(97).emit(2)
    s.label('full').msg(m + 4).emit(97).emit(2)
    s.label('again').msg(m + 5).emit(97).emit(2)
    return s.finish()


def floor7(rom, rec, g, trainers, source):
    """Jessie & James hold the corridor below Mr. Fuji; beating them frees him and he gives the Poke Flute."""
    m = lambda f, l: yellow_text.message(source, f, l)
    flute = lambda text: text.replace('# FLUTE', 'POKE FLUTE')
    # Messages: 0 Stop right there, 1 setting him straight, 2 you will regret this, 3 blasting off again.
    lines = [m('PokemonTower7F', '_PokemonTowerJessieJamesText1').rstrip('@')] + [m('PokemonTower7F', f'_PokemonTowerJessieJamesText{i}').rstrip('@') for i in (2, 3, 4)]
    fuji_at = len(lines)
    lines += [
        m('PokemonTower7F', '_PokemonTower7FMrFujiRescueText').rsplit('\r', 1)[0],   # drop the 'follow me home' paragraph
        flute(m('MrFujisHouse', '_MrFujisHouseMrFujiIThinkThisMayHelpYourQuestText')),
        '{PLAYER} received a POKE FLUTE!',
        flute(m('MrFujisHouse', '_MrFujisHouseMrFujiPokeFluteExplanationText')),
        m('MrFujisHouse', '_MrFujisHouseMrFujiPokeFluteNoRoomText'),
        flute(m('MrFujisHouse', '_MrFujisHouseMrFujiHasMyFluteHelpedYouText')),
    ]
    scene, stand = jj_scripts(trainers['jessie_james'], 0)
    entry = _attach(rom, rec, lines, [scene, stand, fuji_script(fuji_at)])
    r = JJ_ROOM
    g[1].extend([actor(0, JESSIE_SPRITE, entry + 1, *r['jessie'], JJ_HIDE, 0), actor(1, JAMES_SPRITE, entry + 1, *r['james'], JJ_HIDE, 0),
                 actor(2, FUJI_SPRITE, entry + 2, *r['fuji'], 0, 0)])
    tx, tz, w, h = r['trigger']
    g[3].append(struct.pack('<Hhh5H', entry, tx, tz, w, h, 0, 0, JJ_STATE))
    return dict(entry=entry, jessie=r['jessie'], james=r['james'], fuji=r['fuji'], trigger=r['trigger'])


def ghost_script():
    """Stepping onto the stairs' platform: the restless soul blocks the way; the Silph Scope unveils it as Marowak."""
    s = Script().emit(96)
    music(s, 1112).msg(0)
    s.emit(128, SILPH_SCOPE, 1, 0x800C).compare(0x800C, 0).jump('blind', 1)
    s.msg(1)
    s.emit(589, MAROWAK_ALOLAN, GHOST_LEVEL)
    s.data.append(0)
    s.emit(220, 0x800C).compare(0x800C, 1).jump('retreat', 5)
    s.msg(3).emit(30, GHOST_DONE).emit(41, GHOST_STATE, 1).emit(81, 0).emit(82)
    end(s)
    s.label('blind').msg(2)
    s.label('retreat').emit(81, 0).emit(82).movement(255, 'back').emit(95)
    end(s)
    s.moves('back', [(12, GHOST_ROOM['back'])])
    return s.finish()


def _name_alolan_marowak(rom):
    """Species-name banks 237 and 238 hold '-----' for the form species; give Alolan Marowak (and Large) Marowak's names."""
    texts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
    for bank in (237, 238):
        key, names = decode_messages(texts.files[bank])
        assert names[MAROWAK_ALOLAN] != names[105] and len(names) > MAROWAK_ALOLAN + 2
        for form in (MAROWAK_ALOLAN, MAROWAK_ALOLAN + 2):
            names[form] = names[105]
        texts.files[bank] = encode_messages(key, names)
    rom.files[rom.filenames.idOf('a/0/2/7')] = texts.save()


def floor6(rom, rec, g, source):
    """The Marowak ghost: no Silph Scope, no passage."""
    _name_alolan_marowak(rom)
    m = lambda l: yellow_text.message(source, 'PokemonTower6F', l)
    lines = [m('_PokemonTower6FBeGoneText'), "SILPH SCOPE unveiled the GHOST's identity!", "Darn! The GHOST can't be ID'd!", m('_PokemonTower6FGhostWasCubonesMotherText')]
    entry = _attach(rom, rec, lines, [ghost_script()])
    tx, tz, w, h = GHOST_ROOM['trigger']
    g[3].append(struct.pack('<Hhh5H', entry, tx, tz, w, h, 0, 0, GHOST_STATE))
    return dict(entry=entry, trigger=GHOST_ROOM['trigger'], species=MAROWAK_ALOLAN, level=GHOST_LEVEL)
