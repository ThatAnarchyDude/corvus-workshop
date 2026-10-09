"""Read-only ROM identification and Nintendo DS filesystem inventory."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def digest(data, algorithm):
    return hashlib.new(algorithm, data).hexdigest()


def inspect(path):
    data = path.read_bytes()
    result = {'file': path.name, 'size': len(data), 'sha1': digest(data, 'sha1'), 'sha256': digest(data, 'sha256')}
    if path.suffix.lower() == '.gbc':
        assert len(data) >= 0x150, 'Truncated Game Boy header'
        result.update(title=data[0x134:0x143].rstrip(b'\0').decode('ascii'), cgb_flag=data[0x143], cartridge_type=data[0x147])
        return result
    assert len(data) >= 512, 'Truncated DS header'
    result.update(title=data[:12].rstrip(b'\0').decode('ascii'), game_code=data[12:16].decode('ascii'), revision=data[30])
    fnt_offset, fnt_size, fat_offset, fat_size = struct.unpack_from('<4I', data, 64)
    assert fat_size % 8 == 0
    assert fnt_offset + fnt_size <= len(data) and fat_offset + fat_size <= len(data)
    fnt = data[fnt_offset:fnt_offset + fnt_size]
    fat = [struct.unpack_from('<2I', data, fat_offset + i) for i in range(0, fat_size, 8)]
    assert all(0 <= start <= end <= len(data) for start, end in fat), 'Invalid file extent'
    files = []
    visited = set()

    def directory(index, prefix):
        assert index not in visited, 'Directory cycle'
        visited.add(index)
        cursor, file_id, _ = struct.unpack_from('<IHH', fnt, index * 8)
        while True:
            marker = fnt[cursor]
            cursor += 1
            if marker == 0:
                return
            length = marker & 127
            name = fnt[cursor:cursor + length].decode('ascii')
            cursor += length
            assert name not in ('.', '..') and '/' not in name
            full = prefix + name
            if marker & 128:
                child = struct.unpack_from('<H', fnt, cursor)[0]
                cursor += 2
                directory(child & 4095, full + '/')
            else:
                start, end = fat[file_id]
                item = {'id': file_id, 'path': full, 'offset': start, 'size': end - start}
                if data[start:start + 4] == b'NARC':
                    block = start + struct.unpack_from('<H', data, start + 12)[0]
                    if data[block:block + 4] == b'BTAF':
                        item['narc_members'] = struct.unpack_from('<H', data, block + 8)[0]
                files.append(item)
                file_id += 1
    directory(0, '')
    result.update(fat_entries=len(fat), named_files=len(files), files=files)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roms', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps([inspect(path) for path in args.roms], indent=2))
