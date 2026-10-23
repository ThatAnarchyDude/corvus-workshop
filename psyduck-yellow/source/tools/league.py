"""Indigo Plateau: HG's five Pokemon League rooms (maps 301-305) become Yellow's Lorelei, Bruno, Agatha, Lance and Champion Blue.

Each room has two trainer records (first visit and rematch); both get Yellow's team, moves, name and a class whose battle art
fits. Dialogue is still HG's. Champion Blue is a fixed Rival3 team (his last Pokemon is Jolteon, not the saved starter line).
"""
import struct
import ndspy.narc
import tower_scenes as ts
from opening import encode_text
from parcel_quest import PH
from prototype import decode_messages

# room map: (first-visit record, rematch record, Yellow label, name, class id override or None, $FF row index)
ROOMS = {
    301: (245, 702, 'LoreleiData', 'LORELEI', 88, 0),
    302: (247, 703, 'BrunoData', 'BRUNO', 112, 0),
    303: (418, 704, 'AgathaData', 'AGATHA', 88, 0),
    304: (246, 705, 'LanceData', 'LANCE', 86, 0),
    305: (244, 701, 'Rival3Data', None, None, 0),          # Champion Blue keeps the rival class and name
}


def patch(rom, source):
    yellow = ts.Yellow(source)
    book = ts.TrainerBook(rom)
    report = {}
    for room, (first, again, label, name, cls, index) in ROOMS.items():
        team = yellow.leader_party(label, index)
        body = b''.join(struct.pack('<BB3H4H', 128, 0, m['level'], m['species'], 0, *m['moves']) for m in team)
        for tid in (first, again):
            row = bytearray(book.trainers.files[tid])
            row[0], row[3], row[4:12], row[16] = 1, len(team), bytes(8), 0
            if cls is not None:
                row[1] = cls
            book.trainers.files[tid] = bytes(row)
            book.parties.files[tid] = body
            if name:
                book.names[tid] = decode_messages(encode_text([name], PH))[1][0]
        report[room] = [(m['species'], m['level']) for m in team]
    book.save()
    return report
