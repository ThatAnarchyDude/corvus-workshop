"""TEST ONLY: find which code asks for a row of a message bank (found the VS banner's name source this way, 2026-10-27).

patch: hooks the two message getters GetString (ARM9 0x0200BB6C) and GetNewStrbuf (0x0200BBA0). Every call whose loader belongs to the given bank (default 729, the trainer names)
is appended to a 16-entry log in overlay 129's code gap: row, LR, loader pointer and seven stack words. The stack words hold the saved registers and return addresses of the
callers, so the chain of callers can be read off them.
run: boots a fixture ROM the way ds_session.boot() does, but stops right after the Continue presses so the first seconds of a scripted battle (fixture_party.py --trainer N) are
still ahead, then prints the log every second.

Usage: msg_row_trace.py patch <in.nds> <out.nds> [bank]          prints LOGBUF <address>
       DS_ROM=<out.nds> DS_OUT=<dir> msg_row_trace.py run <address> [seconds]     (the fixture .dsv must sit next to the ROM)
Example (the VS banner): fixture_party.py 0105.nds t.nds 25 0 50 --trainer 244; msg_row_trace.py patch t.nds tr.nds; ... run 0x23df678
  -> row 244 from LR 0x207342B (battle setup copies the name) and one row from LR 0x200C39D, return 0x225F19D (overlay 115's name builder; the stack holds its record pointer).
Never part of a release ROM. Temporary ROM copies are 200 MB each: delete them after each run (the scratch disk is a small tmpfs).
"""
import struct
import sys

ENTRIES, STRIDE, STACKW = 16, 40, 7
HOOKS = [        # (site, the four displaced instructions, address to continue at)
    (0x200BB6C, 'push {r3, r4, lr}\nsub sp, #4\nadds r4, r0, #0\nldrh r0, [r4]', 0x200BB74),
    (0x200BBA0, 'push {r3, lr}\nadds r3, r0, #0\nldrh r0, [r3]\nadds r2, r1, #0', 0x200BBA8),
]


def patch(rom, bank=729):
    import ndspy.code
    import map_header_extension as ext
    from mega_starter import Gap
    address, size = ext.reserve_code(rom, 24 * 46)
    ovs = rom.loadArm9Overlays()
    perm = ovs[129]
    perm.data = bytearray(perm.data)
    gap = Gap(perm, address, size)
    buf = gap.put(bytes(4 + ENTRIES * STRIDE))
    main = rom.loadArm9()
    sec = main.sections[0]
    sec.data = bytearray(sec.data)
    stack = ''.join(f'ldr r2, [sp, #{8 + 4 * k}]\nstr r2, [r3, #{12 + 4 * k}]\n' for k in range(STACKW))
    for site, displaced, ret in HOOKS:
        tramp = gap.code(f'''
push {{r2, r3}}
ldr r2, [r0, #4]
ldr r3, bank
cmp r2, r3
bne skip
ldr r2, buf
ldr r3, [r2]
cmp r3, #{ENTRIES}
bhs skip
movs r2, #{STRIDE}
muls r3, r2
ldr r2, buf
adds r3, r3, r2
adds r3, #4
str r1, [r3, #0]
mov r2, lr
str r2, [r3, #4]
str r0, [r3, #8]
{stack}
ldr r2, buf
ldr r3, [r2]
adds r3, #1
str r3, [r2]
skip:
pop {{r2, r3}}
{displaced}
push {{r4}}
ldr r4, back
mov ip, r4
pop {{r4}}
bx ip
.align 2
bank: .word {(bank << 16) | 0x1B}
buf: .word {buf}
back: .word {ret | 1}
''')
        expect = bytes(gap.ks.asm(displaced, addr=site)[0])
        at = site - sec.ramAddress
        assert bytes(sec.data[at:at + 8]) == expect, (hex(site), bytes(sec.data[at:at + 8]).hex())
        sec.data[at:at + 8] = bytes.fromhex('004b1847') + struct.pack('<I', tramp | 1)      # ldr r3,[pc]; bx r3; .word tramp
    rom.files[perm.fileID] = perm.save(compress=False)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.arm9 = main.save(compress=True)
    return buf


def run(address, seconds=12):
    sys.path.insert(0, __file__.rsplit('/', 1)[0])
    import ds_session as d
    base = address - 0x02000000
    d.run(900); d.run(30, 8); d.run(60); d.run(30, 8); d.run(60); d.run(30, 8); d.run(120); d.run(30, 8)
    counts = []
    for _ in range(seconds):
        d.run(60)
        counts.append(struct.unpack_from('<I', d.ram(), base)[0])
    print('log count after each second:', counts)
    ram = d.ram()
    for i in range(min(counts[-1], ENTRIES)):
        w = struct.unpack_from('<10I', ram, base + 4 + i * STRIDE)
        print(i, 'row', w[0], 'lr %#x' % w[1], 'loader %#x' % w[2], 'stack', ' '.join('%#x' % x for x in w[3:10]))


if __name__ == '__main__':
    if sys.argv[1] == 'patch':
        import ndspy.rom
        rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[2])
        print('LOGBUF', hex(patch(rom, int(sys.argv[4]) if len(sys.argv) > 4 else 729)))
        rom.saveToFile(sys.argv[3])
    else:
        run(int(sys.argv[2], 16), int(sys.argv[3]) if len(sys.argv) > 3 else 12)
