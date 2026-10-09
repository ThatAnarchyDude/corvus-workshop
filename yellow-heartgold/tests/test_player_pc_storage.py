"""Execute compiled PC bytecode to check inventory conservation and failures.

Native display commands are skipped; menu and bag APIs supply player choices.
These checks complement the real emulator UI and normal-save tests.
"""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from player_pc import script,SLOTS,INIT


class StorageRun:
    def __init__(self, choices, *, variables=None, bag=None, selected=0, bag_limit=999):
        self.variables = dict(variables or {})
        self.bag = dict(bag or {})
        self.choices = iter(choices)
        self.selected = selected
        self.bag_limit = bag_limit
        self.messages = []
        self.code = script()
        self.at = 0
        self.cmp = 0
        self.entries = []

    def read(self, fmt='H'):
        v=struct.unpack_from('<'+fmt,self.code,self.at)[0]
        self.at += struct.calcsize('<'+fmt)
        return v

    def value(self, n):
        return self.variables.get(n,0) if n>=0x4000 else n

    def run(self):
        v=self.variables
        for _ in range(4000):
            op=self.read()
            if op==2:return self
            if op in (50,53,96,97,150,175,746,747):continue
            if op==45:self.messages.append(self.read('B'));continue
            if op in (190,191):self.read('B');continue
            if op in (73,156,376,617):
                if op==73:self.read()
                continue
            if op==174:
                for _ in range(4):self.read()
                continue
            if op in (194,198):self.read('B');self.read();continue
            if op in (17,18):
                a,b=self.read(),self.read();left=self.value(a)
                right=self.value(b) if op==18 else b
                self.cmp=(left>right)-(left<right);continue
            if op in (22,28):
                condition=self.read('B') if op==28 else None
                distance=self.read('i')
                if condition is None or [self.cmp<0,self.cmp==0,self.cmp>0,
                    self.cmp<=0,self.cmp>=0,self.cmp!=0][condition]:self.at+=distance
                continue
            if op in (39,40,41,42):
                target,arg=self.read(),self.read()
                value=arg if op==41 else self.value(arg)
                if op==39:value=v.get(target,0)+value
                if op==40:value=v.get(target,0)-value
                v[target]=value&65535;continue
            if op==750:
                for _ in range(4):self.read('B')
                self.result=self.read();self.entries=[];continue
            if op==751:
                self.read();self.read();self.entries.append(self.read());continue
            if op==752:
                choice=next(self.choices)
                assert choice in self.entries or choice==0xfffd,(choice,self.entries)
                v[self.result]=choice;continue
            if op==63:v[self.read()]=next(self.choices);continue
            if op in (572,616,377):v[self.read()]=0;continue
            if op==333:self.read('B');continue
            if op==334:v[self.read()]=self.selected;continue
            if op==130:self.read();v[self.read()]=1;continue
            if op==669:
                item=self.value(self.read());v[self.read()]=self.bag.get(item,0);continue
            if op in (125,126):
                item,qty=self.value(self.read()),self.value(self.read());target=self.read()
                old=self.bag.get(item,0)
                success=(old+qty<=self.bag_limit) if op==125 else (old>=qty)
                v[target]=int(success)
                if success:self.bag[item]=old+qty if op==125 else old-qty
                continue
            raise AssertionError(f'Unhandled native command {op} at {self.at-2}')
        raise AssertionError('PC script did not terminate')


class PlayerStorageTests(unittest.TestCase):
    def test_seeds_once_and_exact_withdrawal_is_allowed(self):
        first=StorageRun([0,0,0,1,0,3,250,1]).run()
        self.assertEqual(first.bag,{50:95})
        self.assertEqual(first.variables[SLOTS[1][1]],0)
        second=StorageRun([1],variables=first.variables,bag=first.bag).run()
        self.assertEqual(second.bag,{50:95})
        self.assertEqual(second.variables[SLOTS[1][1]],0)
        self.assertEqual(second.variables[SLOTS[0][1]],1)

    def test_full_bag_preserves_stored_items(self):
        run=StorageRun([0,0,0,0,1,3,250,1],bag={17:999}).run()
        self.assertEqual(run.variables[SLOTS[0][1]],1)
        self.assertEqual(run.bag[17],999)
        self.assertIn(17,run.messages)

    def test_deposit_conserves_quantity(self):
        run=StorageRun([0,0,1,1,10,3,250,1],bag={50:20},selected=50).run()
        self.assertEqual(run.bag[50],10)
        self.assertEqual(run.variables[SLOTS[1][1]],105)

    def test_stack_limit_rejects_deposit_before_removing_inventory(self):
        vars={INIT:1,SLOTS[0][0]:50,SLOTS[0][1]:999}
        run=StorageRun([0,0,1,1,1,3,250,1],variables=vars,bag={50:1},selected=50).run()
        self.assertEqual(run.bag[50],1)
        self.assertEqual(run.variables[SLOTS[0][1]],999)

    def test_toss_requires_confirmation(self):
        for answer,remaining in [(1,1),(0,0)]:
            run=StorageRun([0,0,2,0,1,answer,3,250,1]).run()
            self.assertEqual(run.variables[SLOTS[0][1]],remaining)
            self.assertEqual(run.bag,{})

    def test_cancelled_bag_selection_preserves_storage(self):
        run=StorageRun([0,0,1,1,3,250,1],selected=0,bag={50:4}).run()
        self.assertEqual(run.bag,{50:4})
        self.assertEqual(run.variables[SLOTS[1][1]],95)
