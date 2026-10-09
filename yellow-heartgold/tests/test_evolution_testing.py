"""Exercise released Thumb dispatch and saved PC upgrade failure paths."""
import struct
import unittest
from test_player_pc_storage import StorageRun
from player_pc import SLOTS, INIT, EVOLUTION_INIT, EVOLUTION_ITEMS
from evolution_testing import patch_native, RULES
from build_rom import PROJECT
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *


class EvolutionStorageChecks(unittest.TestCase):
    def test_new_game_supplies_once(self):
        first=StorageRun([1],evolution_items=True).run()
        self.assertEqual(first.variables[EVOLUTION_INIT],7)
        self.assertEqual([(first.variables[a],first.variables[b]) for a,b in SLOTS[:9]],
                         [(17,1),(50,95)]+[(item,95) for item in EVOLUTION_ITEMS])
        second=StorageRun([1],variables=first.variables,evolution_items=True).run()
        self.assertEqual(second.variables,first.variables)

    def test_previous_save_keeps_items_and_resumes_when_full(self):
        vars={INIT:1,SLOTS[0][0]:17,SLOTS[0][1]:0,SLOTS[1][0]:50,SLOTS[1][1]:13}
        for i,(a,b) in enumerate(SLOTS[2:]):vars[a]=200+i;vars[b]=9+i
        # One empty slot receives only Thunder Stone; subsequent items wait.
        first=StorageRun([1],variables=vars,evolution_items=True).run()
        self.assertEqual(first.variables[EVOLUTION_INIT],1)
        self.assertEqual(first.variables[SLOTS[1][1]],13)
        self.assertIn(39,first.messages)
        for a,b in SLOTS[2:]:first.variables[a]=0;first.variables[b]=0
        second=StorageRun([1],variables=first.variables,evolution_items=True).run()
        self.assertEqual(second.variables[EVOLUTION_INIT],7)
        self.assertEqual(second.variables[SLOTS[0][1]],95)
        self.assertEqual(second.variables[SLOTS[1][1]],13)

    def test_existing_stone_stack_limit_preserves_inventory(self):
        vars={INIT:1,SLOTS[0][0]:83,SLOTS[0][1]:950}
        run=StorageRun([1],variables=vars,evolution_items=True).run()
        self.assertEqual(run.variables.get(EVOLUTION_INIT,0),0)
        self.assertEqual(run.variables[SLOTS[0][1]],950)
        self.assertIn(39,run.messages)

    def test_all_evolution_supplies_can_be_withdrawn(self):
        for slot,item in enumerate(EVOLUTION_ITEMS,2):
            run=StorageRun([0,0,0,slot,0,3,250,1],evolution_items=True).run()
            self.assertEqual(run.bag,{item:95})
            self.assertEqual(run.variables[SLOTS[slot][1]],0)
            reopened=StorageRun([1],variables=run.variables,bag=run.bag,evolution_items=True).run()
            self.assertEqual(reopened.variables[SLOTS[slot][1]],0)


@unittest.skipUnless((PROJECT/'build/yellow-heartgold-prototype-005.nds').exists(),'Requires local prototype 005')
class NativeEvolutionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-005.nds')).loadArm9()
        cls.main.sections[0].data=bytearray(cls.main.sections[0].data)
        patch_native(cls.main)

    def execute(self,species,item,context,method_pointer=True):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        cpu.mem_map(0x1FF8000,0x8000);cpu.mem_map(0x2000000,0x120000);cpu.mem_map(0x2300000,0x20000)
        cpu.mem_write(0x2000000,bytes(self.main.sections[0].data));cpu.mem_write(0x1FF8000,bytes(self.main.sections[1].data))
        stack=0x231F000;method=0x2301000
        cpu.mem_write(stack,struct.pack('<I',method if method_pointer else 0));cpu.mem_write(method,struct.pack('<I',123))
        registers=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7]
        values=[0x2300100,0x2300200,context,item,0x44,0x55,0x66,0x77]
        for reg,v in zip(registers,values):cpu.reg_write(reg,v)
        cpu.reg_write(UC_ARM_REG_SP,stack);cpu.reg_write(UC_ARM_REG_LR,0x20FF001)
        stopped=[]
        def hook(uc,at,size,data):
            if at==0x206E540:
                self.assertEqual(uc.reg_read(UC_ARM_REG_R0),values[1]);self.assertEqual(uc.reg_read(UC_ARM_REG_R1),5)
                uc.reg_write(UC_ARM_REG_R0,species);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            elif at in (0x2070E3A,0x20FF000):stopped.append(at);uc.emu_stop()
        cpu.hook_add(UC_HOOK_CODE,hook)
        cpu.emu_start(0x2070E35,0x20FF000,count=1000)
        if not stopped:stopped.append(cpu.reg_read(UC_ARM_REG_PC))
        output=[cpu.reg_read(r) for r in registers]
        if stopped==[0x20FF000]:
            self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),stack)
            self.assertEqual(output[1:],values[1:])
        else:
            self.assertEqual(stopped,[0x2070E3A])
            self.assertEqual(output[:6],values[:6]);self.assertEqual(output[7],values[1])
            self.assertEqual(cpu.reg_read(UC_ARM_REG_SP),stack-20-68)
            saved=struct.unpack('<5I',cpu.mem_read(stack-20,20))
            self.assertEqual(saved,(*values[4:],0x20FF001))
        return stopped[0],output[0],struct.unpack('<I',cpu.mem_read(method,4))[0]

    def test_additional_evolutions_in_both_native_item_contexts(self):
        for species,item,target in RULES:
            for context in (2,3):
                for pointer in (True,False):
                    with self.subTest(species=species,item=item,context=context,pointer=pointer):
                        at,result,method=self.execute(species,item,context,pointer)
                        self.assertEqual((at,result),(0x20FF000,target));self.assertEqual(method,0 if pointer else 123)

    def test_unrelated_items_species_and_original_contexts_use_native_function(self):
        for species,item,context in [(133,84,3),(133,83,3),(133,82,3),(133,109,0),(133,108,1),(54,83,3),(175,108,3),(280,109,3),(133,246,0)]:
            self.assertEqual(self.execute(species,item,context)[0],0x2070E3A)


@unittest.skipUnless((PROJECT/'build/yellow-heartgold-prototype-006.nds').exists(),'Requires local prototype 006')
class EvolutionReleaseChecks(unittest.TestCase):
    def test_nevermeltice_native_mapping_use_and_held_effect(self):
        import ndspy.narc
        previous=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-005.nds'))
        release=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-006.nds'))
        data=release.loadArm9().sections[0].data
        index=struct.unpack_from('<H',data,0x100194+246*8)[0]
        file=release.filenames.idOf('a/0/1/7')
        old=ndspy.narc.NARC(previous.files[file]);new=ndspy.narc.NARC(release.files[file])
        self.assertEqual([i for i,(a,b) in enumerate(zip(old.files,new.files)) if a!=b],[index])
        self.assertEqual(new.files[index][:10],old.files[index][:10])
        self.assertEqual(new.files[index][10],new.files[84][10])
        self.assertEqual(new.files[index][12],1)
        self.assertEqual(new.files[index][15]&8,8)
        self.assertEqual(new.files[index][2:4],bytes.fromhex('5114'))
        for path in ('a/0/3/4','a/0/4/6'):
            file=release.filenames.idOf(path)
            self.assertEqual(release.files[file],previous.files[file])
