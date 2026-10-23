"""Add scripts and messages to a native map without disturbing the ones it already has."""
import struct
import ndspy.narc
from opening import encode_text, events_decode, events_encode
from parcel_quest import append_bank, PH
from prototype import decode_messages, encode_messages
from viridian_tutorial import TABLE


class MapEdit:
    def __init__(self, rom, map_id):
        self.rom, self.at = rom, TABLE + map_id * 24
        self.main = rom.loadArm9()
        self.d = self.main.sections[0].data = bytearray(self.main.sections[0].data)
        self.scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
        self.texts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
        self.events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
        sid, tid = struct.unpack_from('<H', self.d, self.at + 6)[0], struct.unpack_from('<H', self.d, self.at + 10)[0]
        eid = struct.unpack_from('<H', self.d, self.at + 16)[0]
        self.bank = bytes(self.scripts.files[sid])
        self.key, self.rows = decode_messages(self.texts.files[tid])
        self.groups = events_decode(self.events.files[eid])

    def message(self, line):
        """Append one message; returns its index (NPCMsg index byte, so it must stay below 255)."""
        self.rows.extend(decode_messages(encode_text([line], PH))[1])
        assert len(self.rows) < 255
        return len(self.rows) - 1

    def script(self, build):
        """build(add_message) -> script bytes; returns the new script's id."""
        self.bank, first = append_bank(self.bank, [build(self.message)])
        return first + 1

    def save(self):
        self.scripts.files.append(bytes(self.bank))
        self.texts.files.append(encode_messages(self.key, self.rows))
        self.events.files.append(events_encode(self.groups))
        struct.pack_into('<H', self.d, self.at + 6, len(self.scripts.files) - 1)
        struct.pack_into('<H', self.d, self.at + 10, len(self.texts.files) - 1)
        struct.pack_into('<H', self.d, self.at + 16, len(self.events.files) - 1)
        self.rom.files[self.rom.filenames.idOf('a/0/1/2')] = self.scripts.save()
        self.rom.files[self.rom.filenames.idOf('a/0/2/7')] = self.texts.save()
        self.rom.files[self.rom.filenames.idOf('a/0/3/2')] = self.events.save()
        self.rom.arm9 = self.main.save(compress=True)
