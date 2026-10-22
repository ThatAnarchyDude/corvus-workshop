"""Execute the ARM9 level-100 dispatcher with native-service test doubles."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.rom
import ndspy.narc
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_rom import PROJECT
from rare_candy_evolution import patch, DISPATCH, GET_EVOLUTION, GET_MAP_EVOLUTION, TAKE_ITEM


class RareCandyEvolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ndspy.rom.NintendoDSRom.fromFile(str(PROJECT / 'build/yellow-heartgold-prototype-015.nds'))
        cls.report = patch(cls.rom)

    def run_dispatch(self, level=100, evolution=2, egg=False, item=50, bag_ok=True):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        for address, size in ((0x02000000,0x400000),(0x01FF8000,0x8000),(0x027E0000,0x1000)):
            cpu.mem_map(address,size)
        for section in self.rom.loadArm9().sections:
            cpu.mem_write(section.ramAddress,bytes(section.data))
        menu,args,party,bag,mon,field,location = [0x02300000+i*0x2000 for i in range(7)]
        stop = 0x023E0000
        cpu.mem_write(menu+0x654,struct.pack('<I',args))
        cpu.mem_write(menu+0xC65,bytes([3]))
        cpu.mem_write(args,struct.pack('<2I',party,bag))
        cpu.mem_write(args+0x1C,struct.pack('<I',field))
        cpu.mem_write(args+0x28,struct.pack('<H',item))
        cpu.mem_write(field+0x20,struct.pack('<I',location))
        cpu.mem_write(location,struct.pack('<I',538))
        calls=[]
        native=int(self.report['trampoline'],16)
        def hook(c,address,size,data):
            r=[c.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if address==native:
                calls.append(('fallback',));c.reg_write(UC_ARM_REG_R0,5)
            elif address==0x02074644:
                self.assertEqual(r[:2],[party,3]);c.reg_write(UC_ARM_REG_R0,mon)
            elif address==0x0206E540:
                self.assertEqual(r[0],mon)
                c.reg_write(UC_ARM_REG_R0,level if r[1]==161 else int(egg))
            elif address==GET_MAP_EVOLUTION:
                self.assertEqual(r[0],538);c.reg_write(UC_ARM_REG_R0,2)
            elif address==GET_EVOLUTION:
                self.assertEqual(r,[party,mon,0,2])
                p=struct.unpack('<I',c.mem_read(c.reg_read(UC_ARM_REG_SP),4))[0]
                self.assertEqual(p,args+0x40)
                calls.append(('eligibility',))
                c.mem_write(p,struct.pack('<I',1))
                c.reg_write(UC_ARM_REG_R0,evolution)
            elif address==TAKE_ITEM:
                self.assertEqual(r,[bag,50,1,12]);calls.append(('consume',))
                c.reg_write(UC_ARM_REG_R0,int(bag_ok))
            else:return
            c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        cpu.reg_write(UC_ARM_REG_R0,menu)
        cpu.reg_write(UC_ARM_REG_SP,0x023F0000)
        cpu.reg_write(UC_ARM_REG_LR,stop|1)
        cpu.emu_start(DISPATCH|1,stop,count=3000)
        self.assertEqual(cpu.reg_read(UC_ARM_REG_PC),stop)
        return cpu.reg_read(UC_ARM_REG_R0),calls,bytes(cpu.mem_read(args,0x44))

    def test_eligible_level_100_consumes_one_and_uses_cancellable_native_scene(self):
        for species in (2,3,196,197,176):
            with self.subTest(evolution=species):
                state,calls,args=self.run_dispatch(evolution=species)
                self.assertEqual(state,32)
                self.assertEqual(calls,[('eligibility',),('consume',)])
                self.assertEqual(args[0x27],9)
                self.assertEqual(struct.unpack_from('<H',args,0x3C)[0],species)

    def test_ineligible_level_100_does_not_consume(self):
        state,calls,args=self.run_dispatch(evolution=0)
        self.assertEqual(state,5)
        self.assertEqual(calls,[('eligibility',),('fallback',)])
        self.assertEqual(args[0x27],0)

    def test_other_items_levels_and_eggs_use_original_dispatch(self):
        for options in ({'level':99},{'item':17},{'egg':True}):
            with self.subTest(options=options):
                self.assertEqual(self.run_dispatch(**options)[:2],(5,[('fallback',)]))

    def test_missing_candy_cannot_start_evolution(self):
        state,calls,args=self.run_dispatch(bag_ok=False)
        self.assertEqual(state,5)
        self.assertEqual(calls,[('eligibility',),('consume',),('fallback',)])
        self.assertEqual(args[0x27],0)

    def native_evolution(self,species,level=100,friendship=0,night=False,everstone=False,context=0,evo_parameter=0):
        """Execute real GetMonEvolution against the ROM's actual evolution table."""
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for address,size in ((0x02000000,0x400000),(0x01FF8000,0x8000),(0x027E0000,0x1000)):
            cpu.mem_map(address,size)
        for section in self.rom.loadArm9().sections:
            cpu.mem_write(section.ramAddress,bytes(section.data))
        mon,table,result,stop=0x02300000,0x02301000,0x02302000,0x023E0000
        tables=ndspy.narc.NARC(self.rom.files[self.rom.filenames.idOf('a/0/3/4')])
        fields={0:12345,5:species,6:195 if everstone else 0,9:friendship,20:0,112:0,161:level}
        def hook(c,address,size,data):
            r0,r1=[c.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1)]
            if address==0x0206E540:
                self.assertEqual(r0,mon)
                self.assertIn(r1,fields)
                c.reg_write(UC_ARM_REG_R0,fields[r1])
            elif address==0x02077D88:c.reg_write(UC_ARM_REG_R0,64 if everstone else 0)
            elif address==0x0201AA8C:c.reg_write(UC_ARM_REG_R0,table)
            elif address==0x020725C8:
                self.assertEqual(r0,species);c.mem_write(r1,bytes(tables.files[species]))
            elif address==0x02014804:c.reg_write(UC_ARM_REG_R0,int(night))
            elif address!=0x0201AB0C:return
            c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook)
        for register,value in ((UC_ARM_REG_R0,0x02303000),(UC_ARM_REG_R1,mon),
                               (UC_ARM_REG_R2,context),(UC_ARM_REG_R3,evo_parameter),
                               (UC_ARM_REG_SP,0x023F0000),(UC_ARM_REG_LR,stop|1)):
            cpu.reg_write(register,value)
        cpu.mem_write(0x023F0000,struct.pack('<I',result))
        cpu.emu_start(GET_EVOLUTION|1,stop,count=5000)
        self.assertEqual(cpu.reg_read(UC_ARM_REG_PC),stop)
        return cpu.reg_read(UC_ARM_REG_R0)

    def test_actual_native_level_thresholds_and_everstone_at_100(self):
        for species,level,target in ((1,15,0),(1,16,2),(1,100,2),(2,31,0),(2,32,3),(2,100,3),(3,100,0)):
            with self.subTest(species=species,level=level):
                self.assertEqual(self.native_evolution(species,level),target)
        self.assertEqual(self.native_evolution(1,everstone=True),0)

    def test_actual_native_friendship_and_day_night_at_100(self):
        self.assertEqual(self.native_evolution(175,friendship=219),0)
        self.assertEqual(self.native_evolution(175,friendship=220),176)
        self.assertEqual(self.native_evolution(133,friendship=219),0)
        self.assertEqual(self.native_evolution(133,friendship=220),196)
        self.assertEqual(self.native_evolution(133,friendship=220,night=True),197)
        self.assertEqual(self.native_evolution(133,friendship=220,everstone=True),0)

    def test_actual_native_stone_only_evolution_is_not_triggered(self):
        self.assertEqual(self.native_evolution(25),0)  # Pikachu still needs a stone.


if __name__=='__main__':unittest.main()
