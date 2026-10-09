"""Offline model tests for the *real assembled* HGSS bedroom-PC script bytes.

The interpreter models just the opcodes used by our two scripts. These tests
are NOT emulator gameplay validation or proof that a patched ROM launches.
"""
from __future__ import annotations

import pathlib
import struct
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from bedroom_pc_script import (
    POTION, RARE_CANDY, POTION_WITHDRAWN_FLAG, CANDIES_WITHDRAWN_FLAG,
    TEXT, CHOICE_VAR, ITEM_RESULT_VAR, pc_bank, item_pc_script, wii_script
)


def read_script(bank, index):
    ptr, = struct.unpack_from("<I", bank, 4*index)
    nextptr, = struct.unpack_from("<I", bank, 4*(index+1))
    start = ptr + 4*index + 4
    end = nextptr + 4*(index+1) + 4
    if not (0 <= start < end <= len(bank)):
        raise ValueError("Bad script-bank pointers")
    return bank[start:end]


def emulate(code, *, answers=(), bag=None, flags=None, fail_items=frozenset()):
    pos = 0
    bag = {} if bag is None else bag
    flags = set() if flags is None else flags
    variables = {}
    outputs = []
    cmp_equal = False
    dialog = iter(answers)
    pending_msg = None
    for _ in range(250):
        op, = struct.unpack_from("<H", code, pos)
        pos += 2
        if op == 2:
            return bag, flags, outputs
        elif op == 22:
            rel, = struct.unpack_from("<i", code, pos)
            pos += 4
            pos += rel
        elif op == 28:
            condition = code[pos]
            rel, = struct.unpack_from("<i", code, pos+1)
            pos += 5
            if condition != 1:
                raise ValueError("Test interpreter only supports equal branch")
            if cmp_equal:
                pos += rel
        elif op == 17:
            var, value = struct.unpack_from("<2H", code, pos)
            pos += 4
            cmp_equal = variables.get(var,0) == value
        elif op == 30:
            flag, = struct.unpack_from("<H", code, pos)
            pos += 2
            flags.add(flag)
        elif op == 32:
            flag, = struct.unpack_from("<H", code, pos)
            pos += 2
            cmp_equal = flag in flags
        elif op == 45:
            pending_msg = code[pos]
            pos += 1
            outputs.append(pending_msg)
        elif op in (50,53,79,96,97):
            pass
        elif op == 63:
            var, = struct.unpack_from("<H", code, pos)
            pos += 2
            variables[var] = 0 if next(dialog) else 1
        elif op in (73,78):
            pos += 2
        elif op == 125:
            item, qty, result = struct.unpack_from("<3H", code, pos)
            pos += 6
            success = item not in fail_items and bag.get(item,0)+qty <= 999
            variables[result] = int(success)
            if success:
                bag[item] = bag.get(item,0)+qty
        else:
            raise ValueError(f"Unexpected script command opcode {op} at {pos-2}")
    raise AssertionError("PC interaction exceeded the maximum instruction count")


class BedroomPcTests(unittest.TestCase):
    def test_two_script_entrypoints_in_bank(self):
        bank = pc_bank()
        self.assertEqual(struct.unpack_from("<H",bank,8)[0],0xFD13)
        self.assertTrue(read_script(bank,0).startswith(wii_script()))
        self.assertTrue(read_script(bank,1).startswith(item_pc_script()))
        self.assertEqual(len(TEXT),7)

    def test_yes_yes_withdraws_each_item_once(self):
        bag,flags,out=emulate(item_pc_script(),answers=(True,True))
        self.assertEqual(bag,{POTION:1,RARE_CANDY:95})
        self.assertEqual(flags,{POTION_WITHDRAWN_FLAG,CANDIES_WITHDRAWN_FLAG})
        self.assertEqual(out,[1,2,3,4])

    def test_second_interaction_does_not_duplicate_items(self):
        bag,flags,_=emulate(item_pc_script(),answers=(True,True))
        b2,f2,out=emulate(item_pc_script(),bag=bag,flags=flags)
        self.assertEqual(b2,{POTION:1,RARE_CANDY:95})
        self.assertEqual(f2,flags)
        self.assertEqual(out,[6])

    def test_declining_potion_preserves_it_for_later(self):
        bag,flags,_=emulate(item_pc_script(),answers=(False,True))
        self.assertEqual(bag,{RARE_CANDY:95})
        self.assertEqual(flags,{CANDIES_WITHDRAWN_FLAG})
        bag,flags,_=emulate(item_pc_script(),answers=(True,),bag=bag,flags=flags)
        self.assertEqual(bag,{POTION:1,RARE_CANDY:95})
        self.assertEqual(flags,{POTION_WITHDRAWN_FLAG,CANDIES_WITHDRAWN_FLAG})

    def test_declining_candies_preserves_them_for_later(self):
        bag,flags,_=emulate(item_pc_script(),answers=(True,False))
        self.assertEqual(bag,{POTION:1})
        self.assertEqual(flags,{POTION_WITHDRAWN_FLAG})
        bag,flags,_=emulate(item_pc_script(),answers=(True,),bag=bag,flags=flags)
        self.assertEqual(bag,{POTION:1,RARE_CANDY:95})
        self.assertEqual(flags,{POTION_WITHDRAWN_FLAG,CANDIES_WITHDRAWN_FLAG})

    def test_full_bag_does_not_consume_items(self):
        bag,flags,_=emulate(item_pc_script(),answers=(True,True),fail_items={POTION,RARE_CANDY})
        self.assertEqual(bag,{})
        self.assertEqual(flags,set())
        bag,flags,_=emulate(item_pc_script(),answers=(True,True),bag=bag,flags=flags)
        self.assertEqual(bag,{POTION:1,RARE_CANDY:95})

    def test_bag_existing_stack_near_cap_keeps_candy(self):
        bag,flags,_=emulate(item_pc_script(),answers=(True,True),bag={RARE_CANDY:990})
        self.assertEqual(bag,{RARE_CANDY:990,POTION:1})
        self.assertEqual(flags,{POTION_WITHDRAWN_FLAG})

    def test_wii_interaction_grants_no_items(self):
        bag,flags,out=emulate(wii_script())
        self.assertEqual(bag,{})
        self.assertEqual(flags,set())
        self.assertEqual(out,[0])


if __name__ == "__main__":
    unittest.main()
