"""The League's Champion room shows Champion Blue, not HeartGold's Lance (found 2026-10-23 while playing the room on a test warp).

league.py gave room 305 Yellow's Rival3 team but left HG's Lance everywhere else: the battle read "Champion Lance sent out ...", the person in the room was Lance's sprite
and every line was Lance's. Now:
 - trainer records 244 and 701 (first visit and rematch) take the rival's class and name from the rival template record 742, so the battle is "<RIVAL> sent out ...";
 - the room's trainer actor uses the rival sprite (375, as in the Tower and Silph scenes);
 - the room's text bank (12 rows, its own) gets Yellow's lines: rows 0/1 the rival's intro, 2/3 his defeat and aftermath, 6/7 Oak's congratulations, 9/10 Oak's 'come with me'.
   Mary's interview lines (rows 4, 5, 8, 11) are HG's and stay.

Usage: champion_blue.py <in.nds> <out.nds> <pokeyellow source>
"""
import struct
import sys
import ndspy.narc
import ndspy.rom
import tower_scenes as ts
import yellow_text
from opening import encode_text, events_decode, events_encode
from parcel_quest import PH
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE

ROOM, RECORDS, TEMPLATE, RIVAL_SPRITE = 305, (244, 701), 742, 375


def patch(rom, source):
    t = lambda label: yellow_text.message(source, 'ChampionsRoom', label)
    intro = t('_ChampionsRoomRivalIntroText')
    defeated = yellow_text.message(source, 'ChampionsRoom', '_RivalDefeatedText') + '\r' + t('_ChampionsRoomRivalAfterBattleText')
    congrats = t('_ChampionsRoomOakCongratulatesPlayerText').replace('@', 'your partner')
    come = t('_ChampionsRoomOakComeWithMeText')
    book = ts.TrainerBook(rom)
    cls = book.trainers.files[TEMPLATE][1]
    for tid in RECORDS:
        row = bytearray(book.trainers.files[tid])
        row[1] = cls
        book.trainers.files[tid] = bytes(row)
        book.names[tid] = book.names[TEMPLATE]
    book.save()
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    at = TABLE + ROOM * 24
    eid, tid = struct.unpack_from('<H', d, at + 16)[0], struct.unpack_from('<H', d, at + 10)[0]
    events = ndspy.narc.NARC(rom.getFileByName('a/0/3/2'))
    g = events_decode(events.files[eid])
    actor = bytearray(g[1][0])
    assert struct.unpack_from('<H', actor, 2)[0] == 364, 'room actor 0 is not the Lance sprite'
    struct.pack_into('<H', actor, 2, RIVAL_SPRITE)
    g[1][0] = bytes(actor)
    events.files.append(events_encode(g))
    struct.pack_into('<H', d, at + 16, len(events.files) - 1)
    rom.setFileByName('a/0/3/2', events.save())
    texts = ndspy.narc.NARC(rom.getFileByName('a/0/2/7'))
    key, rows = decode_messages(texts.files[tid])
    assert len(rows) == 12, len(rows)
    for index, line in ((0, intro), (1, intro), (2, defeated), (3, defeated), (6, congrats), (7, congrats), (9, come), (10, come)):
        rows[index] = decode_messages(encode_text([line], PH))[1][0]
    texts.files.append(encode_messages(key, rows))
    struct.pack_into('<H', d, at + 10, len(texts.files) - 1)
    rom.setFileByName('a/0/2/7', texts.save())
    rom.arm9 = main.save(compress=True)
    return dict(class_id=cls)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, sys.argv[3]))
    rom.saveToFile(sys.argv[2])
