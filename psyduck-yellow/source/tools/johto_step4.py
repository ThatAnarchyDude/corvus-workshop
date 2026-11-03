"""Johto postgame, step 4a: the JOHTO LEAGUE (owner plan 2026-11-02, JOHTO-POSTGAME-PLAN.md).

The Indigo Plateau rooms (maps 301-306) already host the Kanto league (league.py, champion_blue.py, hof_oak.py). With all 16 badges the same rooms host the Johto league instead:
Will, Koga, Bruno and Karen, then Lance, each with HeartGold's own 16-badge ("rematch") team of SIX Pokemon, every one raised to level 100.
 - lobby (map 300): its map-load script computes the league once per visit: all 16 badges -> variable MODE = 1 and flag JOHTO set / KANTO clear, else MODE = 0 and the reverse. The door guard turns away
   a player who already won a league (HOFN >= 1) but lacks the 16 badges;
 - rooms 301-304: the native "first / rematch record" test (badge count against 8) tests MODE instead; the rematch record id becomes the Johto record (new trainer ids, copies of HeartGold's 701-705 at level 100);
 - Champion room (305): the same record switch, and the four gendered message pairs (Lance's intro, his defeat, Oak's praise, "come with me") switch between Blue's lines and HeartGold's own Lance rows
   (appended to the room's text bank); the trainer actor exists twice (Blue sprite hidden by JOHTO, Lance sprite hidden by KANTO);
 - Hall of Fame (306): Oak's speech for the first win, Lance's HeartGold speech for the first Johto-league win, none after (HOFN: 0 -> 1 -> 2).
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step4.py <in.nds> <out.nds> [original HeartGold .nds]"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import tower_scenes as ts
from build_rom import BASE
from flag_alloc import free_flags
from johto_step1b import script_ranges
from johto_step3 import free_variable
from map_edit import MapEdit
from opening import Script, encode_text, end, events_decode
from parcel_quest import PH
from prototype import decode_messages

LOBBY, CHAMPION, HOF = 300, 305, 306
RED = 260
ROOMS = {301: (702, 'WILL'), 302: (703, 'KOGA'), 303: (704, 'BRUNO'), 304: (705, 'KAREN'), 305: (701, 'LANCE')}   # room: (HeartGold's 16-badge record, name)
LEVEL = 100
LANCE_SPRITE = 364
COMPARE_BADGES = bytes.fromhex('110035410800')                   # compare 0x4135 (badge count), 8
GUARD_COMPARE = bytes.fromhex('110005400100')                    # the door guard's first test: compare 0x4005, 1
LOBBY_FLAGS = bytes.fromhex('1e000b021e000c02')                  # SetFlag 0x20B, SetFlag 0x20C: the first two commands of the lobby's map-load script
MESSAGE_PAIRS = ((0, 1), (2, 3), (6, 7), (9, 10))                # Champion room: intro, defeat, Oak's praise, "come with me" (male row, female row)
SPEECH = (0, 1)


def goto(at, target):
    return struct.pack('<Hi', 0x16, target - (at + 6))


def hook(bank, site, length, build, exits):
    """Replace the first 6 bytes at `site` by a GoTo into a block appended to the bank (the rest of the `length` bytes is never run). build(s) writes the block into a Script and ends every path
    with s.jump('exit_<name>'); exits maps each name to the bank offset the block returns to."""
    assert length >= 6
    bank.extend(bytes(-len(bank) % 4))
    start = len(bank)
    s = Script()
    build(s)
    for name in exits:
        s.label('exit_' + name)
        s.data.extend(bytes(6))
    code = bytearray(s.finish())
    for k, name in enumerate(exits):
        stub = len(code) - 6 * (len(exits) - k)
        code[stub:stub + 6] = goto(start + stub, exits[name])
    bank.extend(code)
    bank[site:site + 6] = goto(site, start)
    return start


def add_trainer(book, row, party, name):
    tid = len(book.trainers.files)
    assert 0x550 + tid < 0xAA0, tid
    book.trainers.files.append(row)
    book.parties.files.append(party)
    book.names.append(decode_messages(encode_text([name], PH))[1][0])
    while len(book.ofs) < 2 * (tid + 1):
        book.ofs.extend(struct.pack('<H', len(book.table)))
    struct.pack_into('<H', book.ofs, tid * 2, len(book.table))
    for kind in range(3):
        book.table.extend(struct.pack('<2H', tid, kind))
        book.lines.extend(decode_messages(encode_text(['...'], PH))[1])
    return tid


def unused_trainers(book, count):
    """Ids of the filler records trainer_alloc.py left in the gaps (one Magikarp, level 2; nothing in the ROM refers to them)."""
    filler = struct.pack('<BB3H4H', 128, 0, 2, 129, 0, 33, 0, 0, 0)
    free = [t for t in range(738, len(book.trainers.files)) if book.parties.files[t] == filler]
    events = [a for raw in book.events.files for g in events_decode(raw) for a in g]
    free = [t for t in free
            if not any(b'\xd5\x00' + struct.pack('<H', t) in raw for raw in book.scripts.files)     # no TrainerBattle names it
            and not any(struct.pack('<H', 3000 + t - 1) in a or struct.pack('<H', 5000 + t - 1) in a for a in events)]   # no sight-battle actor either
    assert len(free) >= count, free
    return free[:count]


def add_trainers(rom, original, reuse=True):
    """HeartGold's own 16-badge records (701-705: six Pokemon, held items, bag, AI) with every level set to 100."""
    book, src = ts.TrainerBook(rom), ts.TrainerBook(original)
    ids = {}
    spare = unused_trainers(book, len(ROOMS)) if reuse else []
    for room, (record, name) in ROOMS.items():
        row, party = bytes(src.trainers.files[record]), bytearray(src.parties.files[record])
        count = row[3]
        assert count == 6 and len(party) == 18 * count, (record, count, len(party))
        for i in range(count):
            struct.pack_into('<H', party, 18 * i + 2, LEVEL)
        if spare:
            tid = spare.pop(0)
            book.trainers.files[tid], book.parties.files[tid] = row, bytes(party)
            book.names[tid] = decode_messages(encode_text([name], PH))[1][0]
            ids[room] = tid
        else:
            ids[room] = add_trainer(book, row, bytes(party), name)
    book.save()
    return ids


def switch_trainer(bank, rematch, johto, mode):
    """The native test (compare the badge count with 8; below: first record, else rematch record) tests MODE instead (below 1 = Kanto: the first record), and the rematch record is the Johto one."""
    assert bank.count(COMPARE_BADGES) == 1
    at = bank.find(COMPARE_BADGES)
    assert bytes(bank[at + 6:at + 13]) == bytes.fromhex('1c00000e000000'), 'unexpected branch'
    assert bytes(bank[at + 13:at + 15]) == bytes.fromhex('d500') and struct.unpack_from('<H', bank, at + 15)[0] == rematch, 'unexpected rematch battle'
    bank[at:at + 6] = struct.pack('<HHH', 17, mode, 1)
    struct.pack_into('<H', bank, at + 15, johto)


def switch_message(bank, pair, johto_pair, mode):
    """`BufferPlayerName 0; <gendered message male,female>` becomes a choice between the Kanto pair (kept) and the Johto pair."""
    old = bytes.fromhex('be000084 00'.replace(' ', '')) + bytes(pair)
    assert bank.count(old) == 1, pair
    site = bank.find(old)

    def build(s):
        s.emit(190)
        s.data.append(0)
        s.compare(mode, 1).jump('johto', 1)
        s.data.extend(struct.pack('<HBB', 0x84, *pair))
        s.jump('exit_back')
        s.label('johto')
        s.data.extend(struct.pack('<HBB', 0x84, *johto_pair))
        s.jump('exit_back')
    hook(bank, site, 7, build, {'back': site + 7})


def lobby(rom, mode, johto_flag, kanto_flag, hofn):
    e = MapEdit(rom, LOBBY)
    bank = bytearray(e.bank)
    starts, _ = script_ranges(bank)
    # map-load script (script 6): decide the league once per visit
    site = starts[5]
    assert bytes(bank[site:site + 8]) == LOBBY_FLAGS, 'unexpected lobby map-load script'

    def decide(s):
        s.emit(30, 0x20B).emit(30, 0x20C)
        for badge in range(16):
            s.emit(294, badge, 0x800C).compare(0x800C, 0).jump('kanto', 1)
        s.emit(41, mode, 1).emit(30, johto_flag).emit(31, kanto_flag).jump('exit_back')
        s.label('kanto')
        s.emit(41, mode, 0).emit(31, johto_flag).emit(30, kanto_flag).jump('exit_back')
    hook(bank, site, 8, decide, {'back': site + 8})
    # door guard (script 9): after winning a league, only the 16-badge Johto league is open
    guard = starts[8] + 8
    assert bytes(bank[guard:guard + 6]) == GUARD_COMPARE and bank.count(GUARD_COMPARE) == 1, 'unexpected door guard'
    gate = e.message('GUARD: The JOHTO LEAGUE only admits Trainers who hold all 16 BADGES.\rCome back when you do!')

    def refuse(s):
        s.compare(hofn, 1).jump('open', 0)
        s.compare(mode, 1).jump('open', 1)
        s.msg(gate)
        end(s)
        s.label('open')
        s.data.extend(GUARD_COMPARE)
        s.jump('exit_back')
    hook(bank, guard, 6, refuse, {'back': guard + 6})
    e.bank = bytes(bank)
    e.save()


def room(rom, number, johto_id, mode):
    e = MapEdit(rom, number)
    bank = bytearray(e.bank)
    switch_trainer(bank, ROOMS[number][0], johto_id, mode)
    e.bank = bytes(bank)
    e.save()


def champion(rom, original, johto_id, mode, johto_flag, kanto_flag):
    e = MapEdit(rom, CHAMPION)
    bank = bytearray(e.bank)
    switch_trainer(bank, ROOMS[CHAMPION][0], johto_id, mode)
    _, lance = decode_messages(ndspy.narc.NARC(original.getFileByName('a/0/2/7')).files[527])
    first = len(e.rows)
    wanted = [row for pair in MESSAGE_PAIRS for row in pair]
    e.rows.extend(lance[row] for row in wanted)
    assert len(e.rows) < 255
    for k, pair in enumerate(MESSAGE_PAIRS):
        switch_message(bank, pair, (first + 2 * k, first + 2 * k + 1), mode)
    trainer = bytearray(e.groups[1][0])
    blue = bytearray(trainer)
    struct.pack_into('<H', blue, 8, johto_flag)          # Blue is hidden in the Johto league
    struct.pack_into('<H', trainer, 2, LANCE_SPRITE)
    struct.pack_into('<H', trainer, 8, kanto_flag)       # Lance is hidden in the Kanto league
    e.groups[1][0] = bytes(blue)
    e.groups[1].append(bytes(trainer))
    e.bank = bytes(bank)
    e.save()


def hall_of_fame(rom, original, mode, hofn):
    e = MapEdit(rom, HOF)
    bank = bytearray(e.bank)
    _, lance = decode_messages(ndspy.narc.NARC(original.getFileByName('a/0/2/7')).files[528])
    first = len(e.rows)
    e.rows.extend(lance[row] for row in SPEECH)
    old = bytes.fromhex('be000084 00'.replace(' ', '')) + bytes(SPEECH) + bytes.fromhex('3500')
    assert bank.count(old) == 1, 'the Hall of Fame speech is not as expected'
    site = bank.find(old)

    def build(s):
        s.emit(190)
        s.data.append(0)
        s.compare(mode, 1).jump('johto', 1)
        s.compare(hofn, 0).jump('quiet', 5)
        s.data.extend(struct.pack('<HBB', 0x84, *SPEECH))
        s.emit(41, hofn, 1).jump('exit_back')
        s.label('johto')
        s.compare(hofn, 1).jump('quiet', 5)
        s.data.extend(struct.pack('<HBB', 0x84, first, first + 1))
        s.emit(41, hofn, 2).jump('exit_back')
        s.label('quiet')
        s.emit(41, hofn, 2).jump('exit_skip')
    hook(bank, site, 9, build, {'back': site + 7, 'skip': site + 9})
    e.bank = bytes(bank)
    e.save()


def red(rom):
    """Red on Mt. Silver (trainer 260, map 465's battle script; the 16-badge entry rule is HeartGold's own): his six Pokemon are level 100 too."""
    book = ts.TrainerBook(rom)
    party, count = bytearray(book.parties.files[RED]), book.trainers.files[RED][3]
    assert count == 6 and len(party) == 18 * count, (count, len(party))
    for i in range(count):
        struct.pack_into('<H', party, 18 * i + 2, LEVEL)
    book.parties.files[RED] = bytes(party)
    book.save()


def patch(rom, original):
    taken = []
    mode = free_variable(rom)
    taken.append(mode)
    hofn = free_variable(rom, taken)
    johto_flag, kanto_flag = free_flags(rom, 2)
    ids = add_trainers(rom, original)
    lobby(rom, mode, johto_flag, kanto_flag, hofn)
    for number in (301, 302, 303, 304):
        room(rom, number, ids[number], mode)
    champion(rom, original, ids[CHAMPION], mode, johto_flag, kanto_flag)
    hall_of_fame(rom, original, mode, hofn)
    red(rom)
    return dict(mode_var=hex(mode), hof_var=hex(hofn), johto_flag=hex(johto_flag), kanto_flag=hex(kanto_flag), trainers=ids)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    original = ndspy.rom.NintendoDSRom.fromFile(sys.argv[3] if len(sys.argv) > 3 else str(BASE))
    print(patch(rom, original))
    rom.saveToFile(sys.argv[2])
