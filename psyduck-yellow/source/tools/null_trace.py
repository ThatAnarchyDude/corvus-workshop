"""TEST ONLY: NULL-access tracer (py-desmume). The 3DS (nds-bootstrap) aborts on a read or write at address 0..0xFFF, DeSmuME does not (owner photos 2026-10-29 and 2026-11-02), so every true NULL access
found here is a crash on real hardware.
DeSmuME reports ITCM accesses (the engine's ITCM code and data at 0x01FF8000) masked to 0..0x7FFF, so the hook cannot tell them from NULL accesses by address alone. For every hit this decodes the load or
store at the PC (capstone) and computes its real effective address from the registers; only an effective address below 0x8000 counts as a NULL access.
Boots <rom> (the .dsv next to it is imported as the save), runs the steps and writes the true NULL hits (kind, effective address, PC, LR, registers, count, first frame, last mark) to <out.json>.
Steps (JSON list of strings in <steps.json>): boot | wait N | hold KEY N | pos | tshot name | mark text.  Keys: up down left right a b x y l r start.
Run with a venv that has py-desmume and capstone.  Usage: null_trace.py <rom.nds> <steps.json> <out.json>"""
import json
import os
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, CS_OP_MEM, CS_OP_REG
from desmume.controls import Keys, keymask
from desmume.emulator import DeSmuME

X_ADDR, Z_ADDR = 0x021DA6F6, 0x021DA6FE
LIMIT = 0x8000
MEMORY_OPS = ('ldr', 'str', 'ldm', 'stm', 'swp')
KEYS = {'a': Keys.KEY_A, 'b': Keys.KEY_B, 'x': Keys.KEY_X, 'y': Keys.KEY_Y, 'l': Keys.KEY_L, 'r': Keys.KEY_R, 'start': Keys.KEY_START,
        'up': Keys.KEY_UP, 'down': Keys.KEY_DOWN, 'left': Keys.KEY_LEFT, 'right': Keys.KEY_RIGHT}


def main(rom, steps_file, out):
    emu = DeSmuME()
    emu.open(rom)
    dsv = os.path.splitext(rom)[0] + '.dsv'
    if os.path.exists(dsv):
        assert emu.backup.import_file(dsv), 'save import failed'      # the core does not find the .dsv next to the ROM by itself
        emu.reset()
    mem = emu.memory
    reg = mem.register_arm9
    thumb_dis, arm_dis = Cs(CS_ARCH_ARM, CS_MODE_THUMB), Cs(CS_ARCH_ARM, CS_MODE_ARM)
    for dis in (thumb_dis, arm_dis):
        dis.detail = True
    frame, marks, hits, cache, stats, unknown = [0], [], {}, {}, dict(total=0, itcm=0, unknown=0), {}

    def decode(address, thumb):
        key = (address, thumb)
        if key not in cache:
            raw = bytes(mem.unsigned.read_byte(address + i) for i in range(2 if thumb else 4))     # a Thumb load/store is 16 bits: decoding 4 bytes read a following halfword as a Thumb-2 coprocessor op
            ins = next(iter((thumb_dis if thumb else arm_dis).disasm(raw, address, 1)), None)
            cache[key] = ins
        return cache[key]

    alias = {'ip': 'r12', 'fp': 'r11', 'sb': 'r9', 'sl': 'r10'}

    def value(ins, name, thumb):
        name = alias.get(name, name)
        if name == 'pc':
            return (ins.address + (4 if thumb else 8)) & (~3 if thumb else ~0) & 0xFFFFFFFF
        return getattr(reg, name) & 0xFFFFFFFF

    def effective(ins, thumb):
        """Effective address of a load/store, or None."""
        for op in ins.operands:
            if op.type == CS_OP_MEM:
                base = value(ins, ins.reg_name(op.mem.base), thumb) if op.mem.base else 0
                index = value(ins, ins.reg_name(op.mem.index), thumb) << op.mem.lshift if op.mem.index else 0
                return (base + (-index if op.subtracted else index) + op.mem.disp) & 0xFFFFFFFF
        if ins.mnemonic.startswith(('ldm', 'stm')) and ins.operands and ins.operands[0].type == CS_OP_REG:
            return value(ins, ins.reg_name(ins.operands[0].reg), thumb)          # base; the hook address may be any of the following words
        return None

    def record(kind):
        def cb(address, size):
            try:
                inner(address, size)
            except Exception as error:
                stats['errors'] = stats.get('errors', 0) + 1
                stats.setdefault('first_error', repr(error))

        def inner(address, size):
            stats['total'] += 1
            pc, thumb = reg.r15 & 0xFFFFFFFF, bool(reg.cpsr & 0x20)
            for back in (4 if thumb else 8,):                      # R15 reads instruction + 4 (Thumb) or + 8 (ARM) while the access runs (checked on the known Cerulean hit)
                ins = decode(pc - back, thumb)
                if ins is None or not ins.mnemonic.startswith(MEMORY_OPS):
                    continue
                eff = effective(ins, thumb)
                if eff is None:
                    continue
                if ins.mnemonic.startswith(('ldm', 'stm')):
                    eff += (address - eff) & 0x7FFF if 0 <= ((address - eff) & 0x7FFF) < 4 * len(ins.operands) else 0
                if (eff & 0x7FFF) == address & 0x7FFF:
                    break
            else:
                stats['unknown'] += 1
                unknown[(pc, address & 0x7FFF)] = unknown.get((pc, address & 0x7FFF), 0) + 1
                return
            if eff >= LIMIT:
                stats['itcm'] += 1
                return
            key = (kind, ins.address, eff)
            if key not in hits:
                hits[key] = dict(kind=kind, effective=hex(eff), r15_minus_pc=pc - ins.address, thumb=thumb, pc=hex(ins.address), insn='%s %s' % (ins.mnemonic, ins.op_str), lr=hex(reg.r14 & 0xFFFFFFFF),
                                 regs=[hex(reg[i] & 0xFFFFFFFF) for i in range(13)], first_frame=frame[0], count=0, after=marks[-1] if marks else None)
            hits[key]['count'] += 1
        return cb

    mem.register_read(0, record('read'), LIMIT)
    mem.register_write(0, record('write'), LIMIT)

    def run(n, key=None):
        if key is not None:
            emu.input.keypad_add_key(keymask(KEYS[key]))
        for _ in range(n):
            emu.cycle(False)                                    # with_joystick=True breaks the boot when no joystick was initialised
            frame[0] += 1
        if key is not None:
            emu.input.keypad_rm_key(keymask(KEYS[key]))

    results = []
    for step in json.load(open(steps_file)):
        w = step.split()
        if w[0] == 'wait':
            run(int(w[1]))
        elif w[0] == 'hold':
            run(int(w[2]), w[1])
            run(20)
        elif w[0] == 'boot':                                           # ds_session.boot(): continue from the fixture save and close the menu
            run(900); run(30, 'a'); run(60); run(30, 'a'); run(60); run(30, 'a'); run(120); run(30, 'a'); run(700); run(20, 'b'); run(60)
        elif w[0] == 'pos':
            results.append(['pos', mem.unsigned.read_short(X_ADDR), mem.unsigned.read_short(Z_ADDR)])
        elif w[0] == 'tshot':
            emu.screenshot().save(os.path.join(os.path.dirname(out) or '.', w[1] + '.png'))
        elif w[0] == 'mark':
            marks.append(' '.join(w[1:]))
    json.dump(dict(results=results, hits=list(hits.values()), frames=frame[0], stats=stats, unknown=sorted(((hex(a), hex(b), n) for (a, b), n in unknown.items()), key=lambda t: -t[2])[:30]), open(out, 'w'), indent=1)
    sys.stderr.write('frames %d stats %s true NULL hits %d positions %s\n' % (frame[0], stats, len(hits), results[-3:]))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
