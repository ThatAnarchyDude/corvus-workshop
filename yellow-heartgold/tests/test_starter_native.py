"""Execute the actual Thumb hook under ARM emulation, with native API stubs.

Force rare RNG outcomes without changing release odds; real DS playtests
separately check the native encrypted Pokemon format and follower behavior.
"""
import itertools
import struct
import sys
import unittest
from pathlib import Path

import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from starter_properties import patch
from build_rom import PROJECT


@unittest.skipUnless((PROJECT/"build/yellow-heartgold-prototype-003.nds").exists(),
                     "Requires locally supplied HeartGold and prototype 003")
class NativeStarterChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rom = ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-003.nds'))
        cls.main = rom.loadArm9()
        cls.main.sections[0].data = bytearray(cls.main.sections[0].data)
        cls.report = patch(cls.main)

    def execute(self, species, shiny_roll, iv_roll, ability_roll, low=16):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x01FF8000, 0x8000)
        cpu.mem_map(0x02000000, 0x120000)
        cpu.mem_map(0x02300000, 0x20000)
        cpu.mem_write(0x02000000, bytes(self.main.sections[0].data))
        cpu.mem_write(0x01FF8000, bytes(self.main.sections[1].data))
        ctx, fs, save, mon = 0x02300000, 0x02301000, 0x02302000, 0x02304000
        cpu.mem_write(ctx+0x80, struct.pack('<I',fs))
        cpu.mem_write(fs+12, struct.pack('<I',save))
        vals = {5:species, 7:0x1234ABCD, 111:0, 10:6 if species==54 else 50,
                **{70+i:v for i,v in enumerate([0,4,12,31,8,18])}}
        low = 128 if species==54 else low
        rng = iter([shiny_roll,iv_roll,ability_roll,low,0x4321])
        calls = []
        def hook(uc, address, size, _):
            if address==0x020FF000:
                uc.emu_stop();return
            r0,r1,r2=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
            result=None
            if address==0x020403AC:result=1
            elif address==0x02074904:result=0x02303000
            elif address==0x02074644:result=mon
            elif address==0x0206E540:result=vals[r1]
            elif address==0x0201FD44:result=next(rng)
            elif address==0x0207235C:vals[0]=r1
            elif address==0x0206EC40:vals[r1]=int.from_bytes(uc.mem_read(r2,4),'little')
            elif address==0x020722DC:
                vals[10]=({54:(6,13),133:(50,91),175:(55,32)}[species])[vals[0]&1]
            elif address==0x0206E250:calls.append('stats')
            elif address==0x020F2998:
                result=r0//r1;uc.reg_write(UC_ARM_REG_R1,r0%r1)
            else:return
            if result is not None:uc.reg_write(UC_ARM_REG_R0,result)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        cpu.reg_write(UC_ARM_REG_SP,0x0231F000)
        cpu.reg_write(UC_ARM_REG_LR,0x020FF001)
        cpu.reg_write(UC_ARM_REG_R0,ctx)
        cpu.emu_start(int(self.report['starter_hook'],16)|1,0x020FF000,count=10000)
        self.assertEqual(calls,['stats'])
        self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),0)
        self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),0x0231F000)
        return vals

    def test_all_starters_can_be_shiny_perfect_both_or_neither(self):
        for species,shiny,perfect in itertools.product([54,133,175],[False,True],[False,True]):
            with self.subTest(species=species,shiny=shiny,perfect=perfect):
                v=self.execute(species,0 if shiny else 16383,0 if perfect else 1,0)
                pid,ot=v[0],v[7]
                xor=(pid>>16)^(pid&65535)^(ot>>16)^(ot&65535)
                self.assertEqual(xor<8,shiny)
                self.assertEqual([v[i] for i in range(70,76)],
                                 [31]*6 if perfect else [0,4,12,31,8,18])
                self.assertEqual(v[111],0 if species==54 else 1)

    def test_hidden_ability_is_available_independently_of_rare_rolls(self):
        for species,ability in [(54,33),(133,107),(175,105)]:
            for shiny,perfect in itertools.product([0,1],[0,1]):
                with self.subTest(species=species,shiny=shiny,perfect=perfect):
                    v=self.execute(species,shiny,perfect,2)
                    self.assertEqual(v[10],ability)

    def test_togepi_retains_both_possible_genders(self):
        for low,gender in [(0,1),(30,1),(31,0),(255,0)]:
            self.assertEqual(self.execute(175,1,1,2,low)[111],gender)

    def test_both_rare_rolls_are_reachable_with_the_actual_heartgold_rng(self):
        # Enumerate real consecutive LCG outputs, rather than assuming that
        # a stubbed pair of zero rolls can occur in the actual game.
        hits=[]
        multiplier,increment,modulus=0x41C64E6D,0x6073,1<<32
        for high in [0,16384,32768,49152]:
            for low in range(65536):
                state=(high<<16)|low
                next_state=(state*multiplier+increment)&0xffffffff
                if (next_state>>16)&16383==0:
                    seed=((state-increment)*pow(multiplier,-1,modulus))&0xffffffff
                    hits.append(seed)
        self.assertTrue(hits,'No real HG seed can yield shiny plus perfect IVs')
        for seed in hits:
            first=(seed*multiplier+increment)&0xffffffff
            second=(first*multiplier+increment)&0xffffffff
            self.assertEqual((first>>16)&16383,0)
            self.assertEqual((second>>16)&16383,0)

    def test_sdk_code_is_preserved_and_arena_reserves_the_extension(self):
        original=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-003.nds')).loadArm9()
        self.assertEqual(bytes(self.main.sections[1].data[:1568]),bytes(original.sections[1].data))
        self.assertEqual(struct.unpack_from('<I',self.main.sections[0].data,0xD2C68)[0],
                         int(self.report['itcm_end'],16))


if __name__=='__main__':unittest.main()
