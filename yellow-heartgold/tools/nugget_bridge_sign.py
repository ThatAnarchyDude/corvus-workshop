"""Give the retained south-bridge board a correctly placed A-button event."""
import struct
import ndspy.narc
from opening import events_decode, events_encode, script_bank
from parcel_quest import split_bank, PH
from prototype import decode_messages, encode_messages
from opening import encode_text
from field_interaction_fixes import sign
from viridian_tutorial import TABLE

TEXT = 'ROUTE 24\rNUGGET BRIDGE\rFive trainers await your challenge!'
POSITION = (1324, 106)

def patch(rom):
    main = rom.loadArm9();d = main.sections[0].data = bytearray(main.sections[0].data)
    paths = ('a/0/1/2', 'a/0/2/7', 'a/0/3/2')
    scripts, texts, events = arcs = [ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]) for p in paths]
    rec = TABLE + 52*24;sid, iid, tid = struct.unpack_from('<3H', d, rec+6)
    eid = struct.unpack_from('<H', d, rec+16)[0]
    bank = split_bank(scripts.files[sid]);key, lines = decode_messages(texts.files[tid])
    message = len(lines);lines.extend(decode_messages(encode_text([TEXT], PH))[1])
    entry = len(bank)+1;bank.append(sign(message));g = events_decode(events.files[eid])
    assert not any(struct.unpack_from('<2i', r, 4) == POSITION for r in g[0])
    g[0].append(struct.pack('<HHiiiH2x', entry, 0, *POSITION, 0, 4))
    ns, nt, ne = len(scripts.files), len(texts.files), len(events.files)
    scripts.files.append(script_bank(bank));texts.files.append(encode_messages(key, lines));events.files.append(events_encode(g))
    struct.pack_into('<H', d, rec+6, ns);struct.pack_into('<H', d, rec+10, nt);struct.pack_into('<H', d, rec+16, ne)
    for p, a in zip(paths, arcs):rom.files[rom.filenames.idOf(p)] = a.save()
    rom.arm9 = main.save(compress=True)
    return dict(map=52, position=POSITION, text=TEXT, script=ns, text_bank=nt,
                event=ne, entry=entry, message=message, A_button_only=True)
