"""Johto postgame, step 6c: Red's team is a bit stronger than level 100 (owner 2026-11-02: "boost Red's team's stats ... a bit STRONGER than level 100"; moves and items stay exactly as in vanilla HeartGold;
max IVs; the 508 EV points divided evenly over the six stats; then a little more, "kind of like Megas").
HeartGold's trainer party builder (overlay 131) reads an optional block after the moves, switched on by bit 4 (0x10) of the record's type byte: TWELVE bytes, six IV bytes (each capped at 31: HP, Atk, Def, Spe, SpA, SpD) then six EV bytes (same order).
The ball seal always stays last. Red's record (trainer 260) becomes type 0x13; species, levels (100), abilities, items and moves are copied untouched (checked byte for byte against the oldest build).
The "little more" is carried in the EV bytes: at level 100 every 4 EV points are +1 on that stat, and the engine's stat calculation does not enforce the 510-point total (that cap is only applied when EVs are gained), so the evenly divided 508 (85/85/85/85/84/84)
plus BONUS_EV = 80 on every stat gives +20 on all six stats (EV bytes 165/165/165/165/164/164). Trainer Pokemon are never owned by the player, so no EV rule matters.
Not usable (tried, 2026-11-02, ROM 0155): the builder's bit-7 block of explicit final stats. It does run (traced: SetMonData 0xA3-0xA9 with the right values) but the battle setup recalculates the stats of every party Pokemon (stat routine 0x0206E27C, entered right after the
party is built), which overwrites them; the RAM probe (tools/ram_probe.py) and a scan of the battle's plain stat block both showed the unboosted values. Two earlier slips, caught by the probe: 7 bytes inserted instead of 12, and the probe's dedup hid the live copy.
Usage (from yellow-heartgold, PYTHONPATH=tools): johto_step6_red.py <in.nds> <out.nds>"""
import sys
import ndspy.rom
import tower_scenes as ts

RED = 260
TYPE_IV_EV = 0x10
IV = 31
EVEN_EVS = (85, 85, 85, 85, 84, 84)                              # 508 EV points over HP, Atk, Def, Spe, SpA, SpD
BONUS_EV = 80                                                    # +20 on every stat at level 100
EVS = tuple(ev + BONUS_EV for ev in EVEN_EVS)


def patch(rom):
    book = ts.TrainerBook(rom)
    row, party = bytearray(book.trainers.files[RED]), bytes(book.parties.files[RED])
    assert row[0] == 3 and row[3] == 6, (row[0], row[3])
    size = 18                                                    # [iv, ability, level u16, species u16, item u16, four moves u16, ball seal u16]
    assert len(party) == 6 * size, len(party)
    block = bytes([IV] * 6) + bytes(EVS)
    out = bytearray()
    for i in range(6):
        entry = party[i * size:(i + 1) * size]
        out += entry[:16] + block + entry[16:]                   # between the moves and the ball seal
    row[0] |= TYPE_IV_EV
    book.trainers.files[RED] = bytes(row)
    book.parties.files[RED] = bytes(out)
    book.save()
    return dict(type=row[0], bytes=len(out), evs=EVS)


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
