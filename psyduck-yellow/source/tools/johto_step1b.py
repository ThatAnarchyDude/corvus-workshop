"""Johto postgame, step 1b: the first S.S. Aqua trip (owner plan 2026-11-02, JOHTO-POSTGAME-PLAN.md).

HeartGold's ferry in our ROM: the Vermilion port hall sailor (map 386, script 1 of bank 154) refuses on all days except Wednesday and Sunday; the dock sailor (map 387) and the ship (map 307, whose
direction logic depends on the day) are left alone. Changes, all by copying the native hall script behind a short prelude (the native code is kept byte for byte, so its schedule still rules every later trip):
 - before the postgame variable reaches 4 (Oak has handed over the ticket) the sailor refuses: "not in service";
 - after it, until the player has arrived in Johto once (flag ARRIVED): any day; the crossing is a short script (messages, fade, warp to Olivine's dock, map 330 at (27,21)) because the native ride
   would turn the ship around on days it is not scheduled to sail to Johto (checked: it said "en route to Vermilion City");
 - the first arrival at Olivine's dock sets ARRIVED and the postgame variable to 5 and says where the player is (Elm's call is step 2).
The Route 22 gate and the other ways into Johto are closed in johto_step1c.py.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step1b.py <in.nds> <out.nds>"""
import struct
import sys
import ndspy.rom
from flag_alloc import free_flags
from map_edit import MapEdit
from opening import Script, end
from pokemon_tower import _frame_entry
import johto_step1 as s1

HALL, DOCK, OLIVINE_DOCK = 386, 387, 330
NOT_RUNNING_FLAG = 0xEB
HALL_ALLOWED_AT, DOCK_START_AT = 239, 164                         # offsets inside the native script banks (see script_dis.py)


def script_ranges(bank):
    count = next(i for i in range(400) if struct.unpack_from('<H', bank, 4 * i)[0] == 0xFD13)
    starts = [i * 4 + 4 + struct.unpack_from('<I', bank, 4 * i)[0] for i in range(count)]
    ends = []
    for s in starts:
        later = [t for t in starts if t > s]
        ends.append(min(later) if later else len(bank))
    return starts, ends


def sailor(edit, var, arrived):
    """Hall sailor: prelude + the native script copy. Before the ticket (variable < 4): refuses; first trip (variable >= 4, not ARRIVED): a scripted crossing straight to Olivine's dock;
    after that: the native script (Wednesdays and Sundays)."""
    starts, ends = script_ranges(edit.bank)
    assert starts[0] == 41, starts
    block = bytes(edit.bank[starts[0]:ends[0]])

    def build(add):
        s = Script().emit(96).emit(104)
        s.compare(var, 4).jump('closed', 0)
        s.emit(32, arrived).jump('native', 1)
        s.msg(add('Welcome to the S.S. AQUA!\rYour Ticket is...right there.\rPlease come through.'))
        s.msg(add('The S.S. AQUA is departing for OLIVINE CITY in JOHTO!'))
        s.emit(174, 6, 6, 0, 0).emit(175)
        s.emit(176, OLIVINE_DOCK, 0, 27, 21, 1)
        s.emit(174, 6, 6, 1, 0).emit(175)
        end(s)
        s.label('closed').msg(add('The S.S. AQUA is not in service right now.'))
        end(s)
        s.data.extend(b'\0' * (-len(s.data) % 4))
        s.labels['native'] = len(s.data)
        s.data.extend(block)
        return s.finish()
    new_id = edit.script(build)
    row = bytearray(edit.groups[1][0])
    assert struct.unpack_from('<H', row, 10)[0] == 1, 'the sailor is not object 0 / script 1'
    struct.pack_into('<H', row, 10, new_id)
    edit.groups[1][0] = bytes(row)
    return new_id


def add_frame_row(edit, var, value, script_id):
    header_id = struct.unpack_from('<H', edit.d, edit.at + 8)[0]
    edit.scripts.files[header_id] = _frame_entry(edit.scripts.files[header_id], var, value, script_id)


def patch(rom, var, arrived=None):
    arrived = arrived if arrived is not None else free_flags(rom, 1)[0]
    report = dict(arrived=hex(arrived))
    e = MapEdit(rom, HALL)
    report['hall_script'] = sailor(e, var, arrived)
    e.save()
    e = MapEdit(rom, OLIVINE_DOCK)

    def arrival(add):
        s = Script().emit(96).emit(32, arrived).jump('done', 1)
        s.emit(30, arrived).emit(41, var, 5)
        s.msg(add('...\rYou have arrived in OLIVINE CITY, in JOHTO!'))
        s.label('done')
        return end(s).finish()
    add_frame_row(e, var, 4, e.script(arrival))
    e.save()
    return report


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom, 0x4128))                                     # the variable johto_step1.py allocated
    rom.saveToFile(sys.argv[2])
