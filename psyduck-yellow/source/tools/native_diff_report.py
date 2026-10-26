"""REPORT: every native map (ID < 540) whose header or referenced data differs between a clean HeartGold ROM and a build. argv: clean.nds build.nds"""
import struct, sys
import ndspy.rom, ndspy.narc
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
from viridian_tutorial import TABLE
from prototype import decode_messages
A = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); B = ndspy.rom.NintendoDSRom.fromFile(sys.argv[2])
da, db = A.loadArm9().sections[0].data, B.loadArm9().sections[0].data
N = {p: (ndspy.narc.NARC(A.getFileByName(p)), ndspy.narc.NARC(B.getFileByName(p))) for p in ('a/0/1/2', 'a/0/2/7', 'a/0/3/2', 'a/0/3/7', 'a/0/4/1', 'a/0/4/2', 'a/0/4/4', 'a/0/6/5', 'a/0/5/5', 'a/0/5/6')}
names = decode_messages(N['a/0/2/7'][1].files[279])[1]
def dec(codes):
    out = ''
    for c in codes:
        if c == 65535: break
        if 299 <= c <= 324: out += chr(65 + c - 299)
        elif 325 <= c <= 350: out += chr(97 + c - 325)
        elif 289 <= c <= 298: out += chr(48 + c - 289)
        elif c == 478: out += ' '
        else: out += '.'
    return out
def name(m):
    r = bytes(db[TABLE + m * 24:TABLE + m * 24 + 24]); i = r[18]
    return dec(names[i]) if i < len(names) else '?'
def same(p, i):
    a, b = N[p]
    return i < len(a.files) and bytes(a.files[i]) == bytes(b.files[i])
changed = {}
for m in range(540):
    ra, rb = bytes(da[TABLE + m * 24:TABLE + m * 24 + 24]), bytes(db[TABLE + m * 24:TABLE + m * 24 + 24])
    why = []
    if ra != rb: why.append('header fields %s' % [i for i in range(24) if ra[i] != rb[i]])
    # files referenced by the BUILD's header (post-change pointers) compared with the same index in the clean ROM, and the CLEAN header's files compared in the build
    for label, p, off, w in (('events', 'a/0/3/2', 16, 2), ('script bank', 'a/0/1/2', 6, 2), ('init script', 'a/0/1/2', 8, 2), ('texts', 'a/0/2/7', 10, 2), ('matrix', 'a/0/4/1', 4, 2)):
        ia = struct.unpack_from('<H', ra, off)[0]; ib = struct.unpack_from('<H', rb, off)[0]
        a, b = N[p]
        if ia < len(a.files) and ib < len(b.files) and bytes(a.files[ia]) != bytes(b.files[ia]) and ia == ib: why.append(label + ' file edited in place')
    if ra[0] != 255 or rb[0] != 255:
        wa, wb = ra[0], rb[0]
        if wa < len(N['a/0/3/7'][0].files) and bytes(N['a/0/3/7'][0].files[wa]) != bytes(N['a/0/3/7'][1].files[wa]): why.append('wild table edited in place')
    if why: changed[m] = why
print('native maps with any difference:', len(changed))
for m, w in changed.items(): print(' ', m, name(m), '|', '; '.join(w))
print()
for p, (a, b) in N.items():
    ch = [i for i in range(len(a.files)) if bytes(a.files[i]) != bytes(b.files[i])]
    print(p, 'clean', len(a.files), 'build', len(b.files), 'existing files edited in place:', len(ch))
