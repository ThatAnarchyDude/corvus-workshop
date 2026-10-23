"""Extend the map header table past ID 539 without moving any existing data.

The header accessors all call one bounds/ID function (ARM9 0x3B268). It is replaced
by a trampoline: IDs below 540 are unchanged; IDs >= 540 are shifted so the unchanged
accessors (T + id*24 + field) read 24-byte records appended to the always-resident
hg-engine overlay 129. ROM-only; no emulator-specific behavior.
"""
import struct
import sys

import ndspy.code
import ndspy.rom

from build_rom import PROJECT

TABLE_ADDR = 0x020F6BE0
FUNC = 0x3B268
OLD_FUNC = bytes.fromhex('08b58721 8900 8842 02d3 eaf753f9 0120 08bd'.replace(' ', ''))
NATIVE_COUNT = 540
OV = 129
OV_ORIGINAL_SIZE = 25428
OV_SLOT_END = 0x023E0000


TRAMPOLINE_CODE = struct.pack('<8H', 0xB508, 0x2187, 0x0089, 0x4288, 0xD300 | 1, 0x4901, 0x1840, 0xBD08)


def default_table_address():
    end = 0x023D8000 + OV_ORIGINAL_SIZE
    return end + (-(end - TABLE_ADDR)) % 24


def table_address(rom=None):
    """Where the extension table starts. The trampoline carries it, so a ROM whose table was moved (reserve_code) says so."""
    if rom is not None:
        d = rom.loadArm9().sections[0].data
        if bytes(d[FUNC:FUNC + 16]) == TRAMPOLINE_CODE:
            return TABLE_ADDR + (struct.unpack_from('<I', d, FUNC + 16)[0] + NATIVE_COUNT) * 24
    return default_table_address()


def capacity(rom=None):
    return (OV_SLOT_END - table_address(rom)) // 24


def trampoline(table=None):
    k = (((table or default_table_address()) - TABLE_ADDR) // 24 - NATIVE_COUNT) & 0xFFFFFFFF
    return TRAMPOLINE_CODE + struct.pack('<I', k)


def reserve_code(rom, nbytes):
    """Move the table up by nbytes (a multiple of 24) and return (address, size) of the freed gap in overlay 129."""
    assert nbytes % 24 == 0
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    old = table_address(rom)
    ovs = rom.loadArm9Overlays()
    o = ovs[OV]
    start = old - o.ramAddress
    data = bytearray(o.data)
    if len(data) < start:
        data.extend(bytes(start - len(data)))
    data[start:start] = bytes(nbytes)
    assert o.ramAddress + len(data) <= OV_SLOT_END, 'overlay 129 would overflow'
    o.data = data
    d[FUNC:FUNC + 20] = trampoline(old + nbytes)
    rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return old, nbytes


def records(rom):
    ovs = rom.loadArm9Overlays({OV})
    o = ovs[OV]
    start = table_address(rom) - o.ramAddress
    return [bytes(o.data[start + 24 * i:start + 24 * i + 24]) for i in range((len(o.data) - start) // 24)] if len(o.data) > start else []


def install(rom, new_records):
    """Append 24-byte header records; return their new map IDs. Installs the trampoline once."""
    assert all(len(r) == 24 for r in new_records)
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    now = bytes(d[FUNC:FUNC + 20])
    table = table_address(rom)
    if now[:16] != TRAMPOLINE_CODE and now[:14] != OLD_FUNC[:14]:
        raise RuntimeError('unexpected header ID function bytes: ' + now.hex())
    d[FUNC:FUNC + 20] = trampoline(table)
    ovs = rom.loadArm9Overlays()
    o = ovs[OV]
    start = table - o.ramAddress
    data = bytearray(o.data)
    if len(data) < start:
        assert len(data) == OV_ORIGINAL_SIZE
        data.extend(bytes(start - len(data)))
    have = (len(data) - start) // 24
    assert have + len(new_records) <= (OV_SLOT_END - table) // 24, 'extension table is full'
    ids = [NATIVE_COUNT + have + i for i in range(len(new_records))]
    data.extend(b''.join(new_records))
    o.data = data
    rom.files[o.fileID] = o.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return ids


def native_record(rom, map_id):
    d = rom.loadArm9().sections[0].data
    return bytes(d[0xF6BE0 + map_id * 24:0xF6BE0 + map_id * 24 + 24])


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    clones = [native_record(rom, int(m)) for m in sys.argv[3:]]
    print('new ids', install(rom, clones), 'capacity', capacity())
    rom.saveToFile(dst)
