"""TEST ONLY: rewrite an NDS ROM with the same files in a different order so the files the field needs sit below 128 MiB.
Why: the 3DS loader (nds-bootstrap) crashes on the owner's 3DS at area changes; HeartGold was 128 MiB, 0110 is 191 MiB and its sound archive starts at 0x8005c00.
Contents of every file stay byte-identical; the FAT, the header's pointers/used size and the header CRC change (ARM7, name table, FAT and banner sit among the files and move too).
Usage: rom_reorder.py <in.nds> <out.nds>   (cold files: pbr/* and a/0/0/4 go last)"""
import struct
import sys
import ndspy.rom

COLD_PREFIX = ('pbr/',)
COLD_NAMES = ('a/0/0/4',)
ALIGN = 0x200


def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def main(src, dst):
    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    names = {}

    def rec(folder, path):
        for name in folder.files:
            names[rom.filenames.idOf(path + name)] = path + name
        for sub, fd in folder.folders:
            rec(fd, path + sub + '/')
    rec(rom.filenames, '')
    raw = bytearray(open(src, 'rb').read())
    fat_off, fat_sz = struct.unpack_from('<II', raw, 0x48)
    fnt_off, fnt_sz = struct.unpack_from('<II', raw, 0x40)
    a7_off, a7_ram = struct.unpack_from('<II', raw, 0x30)
    a7_sz = struct.unpack_from('<I', raw, 0x3C)[0]
    ban_off = struct.unpack_from('<I', raw, 0x68)[0]
    ents = [struct.unpack_from('<II', raw, fat_off + 8 * i) for i in range(fat_sz // 8)]
    first = min(s for s, e in ents)
    # blocks: (key, start, end, cold)
    blocks = [('f%d' % i, s, e, i in names and (names[i].startswith(COLD_PREFIX) or names[i] in COLD_NAMES)) for i, (s, e) in enumerate(ents)]
    blocks += [('arm7', a7_off, a7_off + a7_sz, False), ('fnt', fnt_off, fnt_off + fnt_sz, False), ('fat', fat_off, fat_off + fat_sz, False), ('banner', ban_off, ban_off + 0x840, False)]
    assert all(b[1] >= first or b[0] in () for b in blocks if b[0].startswith('f')), 'file before first'
    blocks.sort(key=lambda b: (b[3], b[1]))
    out = bytearray(raw[:first])
    where = {}
    for key, s, e, cold in blocks:
        out += b'\0' * (-len(out) % ALIGN)
        where[key] = len(out)
        out += raw[s:e]
    for i in range(len(ents)):
        s = where['f%d' % i]
        struct.pack_into('<II', out, where['fat'] + 8 * i, s, s + ents[i][1] - ents[i][0])
    struct.pack_into('<I', out, 0x30, where['arm7'])
    struct.pack_into('<I', out, 0x40, where['fnt'])
    struct.pack_into('<I', out, 0x48, where['fat'])
    struct.pack_into('<I', out, 0x68, where['banner'])
    struct.pack_into('<I', out, 0x80, len(out))
    struct.pack_into('<H', out, 0x15E, crc16(bytes(out[:0x15E])))
    open(dst, 'wb').write(out)
    limit = 0x8000000
    over = [(names.get(int(k[1:]), k) if k.startswith('f') else k) for k, s, e, c in blocks if where[k] + (e - s) > limit]
    print('wrote', dst, len(out), 'bytes; blocks ending above 128 MiB:', len(over), over[:5])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
