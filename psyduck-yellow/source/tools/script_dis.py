"""TEST ONLY: minimal HeartGold script disassembler (opcode table from pret/pokeheartgold asm/macros/script.inc; unknown opcodes stop the listing). Usage: script_dis.py <rom> <script bank file> <script number>"""
import struct,sys,ndspy.rom,ndspy.narc
ARGS={0x182:'H',0x156:'HHH',0xF0:'HHHHH',0x96:'',0xA3:'H',0x9D:'',0xB5:'',0xC6:'Bh',0xC2:'Bh',0xC1:'Bh',0xC5:'Bh',0x81:'HH',0x5D:'H',0x5C:'',0x66:'',0x67:'',0x6C:'',0x6D:'',0x2E:'H',0x2F:'H',0x15:'',0x17:'Hi',0x18:'i',0x19:'i',0x21:'H',0x22:'H',0x23:'H',0x24:'H',0x25:'H',0x26:'H',0x4A:'',0x4B:'',0x51:'',0x52:'',0x53:'',0x56:'',0x57:'H',0x58:'',2:'',0x16:'i',0x1C:'Bi',0x11:'HH',0x12:'HH',0x1E:'H',0x1F:'H',0x20:'H',0x29:'HH',0x27:'HH',0x28:'HH',0x2D:'B',0x2C:'B',0x34:'',0x35:'',0x3F:'H',0x5E:'Hi',0x5F:'',0x60:'',0x61:'',0x62:'',0x63:'',0x64:'H',0x65:'H',0x68:'',0x1E4:'H',0x7D:'HHH',0x7E:'HHH',0x80:'HHH',0x7F:'HHH',0xB0:'HHHHH',0xAE:'HHHH',0xAF:'',0x4E:'H',0x4F:'',0x49:'H',0x1A:'i',0x1B:'',0x1D:'Bi',0x14:'H',0xBE:'B',0xBF:'B',0x2A:'HH',0x2B:'HH',0x69:'HH',0x6A:'HHH',0x3:'H',0x13:'H',0x32:'',0x31:'',0x33:'',0x36:'',0x39:'',0x4C:'H',0x4D:'',0x50:'H',0x54:'H',0x55:'H'}
def explore(b, start, limit=600):
    """Follow GoTo/GoToIf/Call targets; returns {offset: (op, args)} for everything reachable (stops at unknown opcodes)."""
    seen, queue, out = set(), [start], {}
    while queue and len(out) < limit:
        i = queue.pop()
        while i < len(b) and i not in seen:
            seen.add(i)
            op = struct.unpack_from('<H', b, i)[0]; j = i + 2
            a = ARGS.get(op)
            if a is None:
                out[i] = ('?%x' % op, [])
                break
            vals = []
            for c in a:
                sz = struct.calcsize('<' + c); vals.append(struct.unpack_from('<' + c, b, j)[0]); j += sz
            out[i] = ('%x' % op, vals)
            if op in (0x16, 0x1A, 0x1C, 0x1D):
                queue.append(j + vals[-1])
            if op in (2, 0x16, 0x1B):
                break
            i = j
    return out


def dis(b, start, limit=600):
    return [(k, v[0], v[1]) for k, v in sorted(explore(b, start, limit).items())]


if __name__=='__main__':
    rom=ndspy.rom.NintendoDSRom.fromFile(sys.argv[1]); bank=int(sys.argv[2]); n=int(sys.argv[3])
    b=bytes(ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files[bank])
    ptrs=[]; i=0
    while True:
        v=struct.unpack_from('<I',b,i)[0]
        if v&0xffff==0xfd13: break
        ptrs.append(i+4+v); i+=4
    print('scripts',len(ptrs),ptrs[:12])
    for s in dis(b,ptrs[n-1]): print(s)
