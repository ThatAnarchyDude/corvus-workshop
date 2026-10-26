"""Audit: where does each progression item come from? Searches every script bank for 'give item' (opcode 125) with the item id, every event file for ball actors, and shop/pickup helpers' patterns.
Usage: key_item_audit.py <rom>"""
import struct, sys, re
import ndspy.rom, ndspy.narc
from prototype import decode_messages
from opening import encode_text, events_decode
from parcel_quest import PH, split_bank
rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
names = decode_messages(ndspy.narc.NARC(rom.getFileByName('a/0/2/7')).files[222])[1]
def codes(s): return [c for c in decode_messages(encode_text([s], PH))[1][0] if c != 0xFFFF]
def find(s):
    nd = codes(s)[:len(s)]
    return [i for i, w in enumerate(names) if w[:len(nd)] == nd and len(w) <= len(nd) + 1]
WANT = ['S.S. Ticket', 'Bike Voucher', 'Bicycle', 'Poké Flute', 'Poke Flute', 'Silph Scope', 'Card Key', 'Lift Key', 'Secret Key', "Oak's Parcel", 'Oaks Parcel', 'Old Rod', 'Good Rod', 'Super Rod', 'Coin Case',
        'HM01', 'HM03', 'HM04', 'TM70', 'Fresh Water', 'Soda Pop', 'Lemonade', 'Pokédex', 'Town Map', 'Helix Fossil', 'Dome Fossil', 'Old Amber', 'Nugget', 'Rare Candy']
scripts = ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files
blobs = [bytes(s) for s in scripts]
for w in WANT:
    ids = find(w)
    if not ids:
        print(f'{w:14} (no such item name)'); continue
    for item in ids[:3]:
        gives = [i for i, b in enumerate(blobs) if struct.pack('<HH', 125, item) in b]
        print(f'{w:14} id {item:4}  script banks giving it: {gives[:8]}')
