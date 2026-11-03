"""Prototype 0157 start-of-game supplies (owner orders 2026-11-03).
 1. The bedroom (map 506) no longer has the Eonite item ball (actor script 5, flag 0xB20): the owner now edits starting items with PKHeX. The Mega ON/OFF switch (script 6) stays.
 2. The bedroom PC starts with 999 of each starting item (the PC holds up to 999): Max Repel (replacing the single Potion) and Rare Candy, and every evolution item it adds later comes in 999 (was 95). The two charms (1 each) are unchanged.
 3. The Viridian Mart's top clerk sells the combined supplies + Poke Ball stock (the second vendor script was attached to the hidden escort cashier, so Viridian sold no Poke Balls).
 4. The Mega Stones are out of the Kanto Mart stock (Vermilion and the six other Marts); the badge-stage stock is unchanged. The supplies vendors are regenerated like johto_step3c.restock but with no extra items.
The bedroom PC script is regenerated from player_pc.script and only replaced when the ROM's current script is byte-identical to the regeneration with the old settings.
Usage (from yellow-heartgold, PYTHONPATH=tools): start_supplies.py <in.nds> <out.nds>"""
import json
import struct
import sys
from pathlib import Path
import ndspy.narc
import ndspy.rom
import johto_step3b as s3b
import player_pc
from kanto_mart_shared import vendor_script
from opening import events_decode, events_encode, script_bank
from parcel_quest import split_bank
from viridian_tutorial import TABLE

BEDROOM = 506
BALL_SCRIPT, BALL_SPRITE = 5, 87
MAX_REPEL, RARE_CANDY = 77, 50
STACK = 999
PRELUDE = bytes.fromhex('4900dc0560006800')
VIRIDIAN = 500                       # its second shop call belongs to the retired escort cashier, so the one working clerk (top) sells the combined stock; the bottom clerk only points to the colleague


def remove_ball(rom):
    main = rom.loadArm9()
    d = main.sections[0].data = bytearray(main.sections[0].data)
    events = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
    at = TABLE + BEDROOM * 24 + 16
    groups = events_decode(events.files[struct.unpack_from('<H', d, at)[0]])
    balls = [row for row in groups[1] if struct.unpack_from('<HH', row)[1] == BALL_SPRITE and struct.unpack_from('<6H', row)[5] == BALL_SCRIPT]
    assert len(balls) == 1, 'expected exactly one item ball in the bedroom'
    groups[1] = [row for row in groups[1] if row is not balls[0] and row != balls[0]]
    events.files.append(events_encode(groups))
    struct.pack_into('<H', d, at, len(events.files) - 1)
    rom.files[rom.filenames.idOf('a/0/3/2')] = events.save()
    rom.arm9 = main.save(compress=True)
    return dict(removed_flag=hex(struct.unpack_from('<6H', balls[0])[4]), actors_left=len(groups[1]))


def stock_pc(rom):
    main = rom.loadArm9()
    d = main.sections[0].data
    sid = struct.unpack_from('<H', d, TABLE + BEDROOM * 24 + 6)[0]
    scripts = ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
    bank = split_bank(scripts.files[sid])
    old = player_pc.script(evolution_items=True, shiny_charm=True, friendship_charm=True)
    assert bank[1].rstrip(b'\0') == old.rstrip(b'\0'), 'the bedroom PC script is not the expected regeneration'
    bank[1] = player_pc.script(evolution_items=True, shiny_charm=True, friendship_charm=True,
                               starting_stacks=((MAX_REPEL, STACK), (RARE_CANDY, STACK)), evolution_quantity=STACK)
    scripts.files.append(script_bank(bank))
    d2 = main.sections[0].data = bytearray(d)
    struct.pack_into('<H', d2, TABLE + BEDROOM * 24 + 6, len(scripts.files) - 1)
    rom.files[rom.filenames.idOf('a/0/1/2')] = scripts.save()
    rom.arm9 = main.save(compress=True)
    return dict(script=len(scripts.files) - 1, old_script=sid)


def restock_without_stones(rom, repo='.'):
    stages = json.loads((Path(repo) / 'data/kanto-mart-inventory.json').read_text())['verified_stages']
    both = s3b.combined(stages)
    main = rom.loadArm9()
    d = bytes(main.sections[0].data)
    fid = rom.filenames.idOf('a/0/1/2')
    arc = ndspy.narc.NARC(rom.files[fid])
    report = {}
    for m in (360,) + s3b.MARTS:
        bank_id = struct.unpack_from('<H', d, TABLE + 24 * m + 6)[0]
        bank = bytearray(arc.files[bank_id])
        if m == 360:
            at = struct.unpack_from('<I', bank, 0)[0] + 4
            assert bank[at:at + 8] == PRELUDE, 'Vermilion entry 0 is not a vendor script'
            bank.extend(bytes(-len(bank) % 4))
            start = len(bank)
            bank.extend(vendor_script(stages, 'supplies', ()))
            struct.pack_into('<I', bank, 0, start - 4)
            report[m] = ('entry 0', start)
        else:
            sites = []
            for p in range(0, len(bank) - 6):
                if struct.unpack_from('<H', bank, p)[0] == 0x16:
                    t = p + 6 + struct.unpack_from('<i', bank, p + 2)[0]
                    if 8 <= t < len(bank) and bank[t - 8:t] == PRELUDE:
                        sites.append(p)
            assert len(sites) in (1, 2), (m, sites)
            single = len(sites) == 1 or m == VIRIDIAN
            bank.extend(bytes(-len(bank) % 4))
            start = len(bank)
            bank.extend(vendor_script(both if single else stages, 'supplies', ()))
            bank[sites[0]:sites[0] + 6] = struct.pack('<Hi', 0x16, start + s3b.PRELUDE - (sites[0] + 6))
            report[m] = (sites[0], start, 'single' if single else 'supplies')
        arc.files[bank_id] = bytes(bank)
    rom.files[fid] = arc.save()
    return report


def patch(rom, repo='.'):
    return dict(ball=remove_ball(rom), pc=stock_pc(rom), marts=restock_without_stones(rom, repo))


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile(sys.argv[1])
    print(patch(rom))
    rom.saveToFile(sys.argv[2])
