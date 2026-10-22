"""Execute the added TM lookups and preserve native teaching data and bag IDs."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.narc
import ndspy.rom
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R7,UC_ARM_REG_LR
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon_tms import patch,TMS
from bulk_rare_candy import patch as patch_candy
from yellow_tms import ITEM_TABLE,MOVE_ENTRY,INDEX_ENTRY


class MtMoonTMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        patch_candy(cls.old)
        cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)

    def cpu(self,rom):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB);cpu.mem_map(0x01FF8000,0x8000);cpu.mem_map(0x02000000,0x400000)
        for section in rom.loadArm9().sections[:2]:cpu.mem_write(section.ramAddress,bytes(section.data))
        return cpu

    def lookup(self,cpu,site,item):
        cpu.reg_write(UC_ARM_REG_R0,item);cpu.reg_write(UC_ARM_REG_LR,0x023E0001)
        cpu.emu_start(site|1,0x023E0000,count=150)
        return cpu.reg_read(UC_ARM_REG_R0)

    def arc(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def test_all_existing_item_lookups_preserved_and_added_moves_and_indices_correct(self):
        old,new=self.cpu(self.old),self.cpu(self.new)
        for site,field in ((MOVE_ENTRY,'move'),(INDEX_ENTRY,'index')):
            for item in range(537):
                tm=next((t for t in TMS if t['item']==item),None)
                wanted=tm[field] if tm else self.lookup(old,site,item)
                self.assertEqual(self.lookup(new,site,item),wanted,(site,item))
        self.assertEqual(self.lookup(new,MOVE_ENTRY,115),117)
        self.assertEqual(self.lookup(new,MOVE_ENTRY,339),269) # Native TM12 Taunt.
        self.assertEqual(self.lookup(new,MOVE_ENTRY,328),264) # Native TM01 Focus Punch.

    def test_native_items_and_all_other_compatibility_bits_preserved(self):
        before,after=[self.arc(r,'a/0/0/2') for r in (self.old,self.new)]
        for species,(a,b) in enumerate(zip(before,after)):
            expected=bytearray(a)
            for tm in TMS:
                if species in self.report['compatible_species'][tm['key']]:expected[40]|=1<<(tm['index']%8)
            self.assertEqual(b,bytes(expected))
        self.assertTrue(after[54][40]&32);self.assertTrue(after[55][40]&32)
        self.assertTrue(after[54][40]&64)
        self.assertFalse(after[133][40]&64);self.assertFalse(after[133][40]&32)
        self.assertTrue(after[122][40]&64) # Mr. Mime's Yellow compatibility.
        before,after=[self.arc(r,'a/0/1/7') for r in (self.old,self.new)]
        self.assertEqual(before,after[:len(before)])
        oldd,newd=[r.loadArm9().sections[0].data for r in (self.old,self.new)]
        for item in range(537):
            if item not in (116,117):self.assertEqual(oldd[ITEM_TABLE+item*8:ITEM_TABLE+(item+1)*8],newd[ITEM_TABLE+item*8:ITEM_TABLE+(item+1)*8])
        self.assertEqual(newd[0x825B4:0x825B8],bytes.fromhex('c046c046'))

    def test_display_changes_numbers_only_and_preserves_working_registers_and_bag(self):
        for i,entry in enumerate(self.report['display_hooks']):
            cpu=self.cpu(self.new)
            for item in (115,116,117,328,339,361,427):
                cpu.mem_write(0x02301000,struct.pack('<HH',item,1))
                for reg,value in ((UC_ARM_REG_R0,105 if i==0 else 82),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x02301000),(UC_ARM_REG_R7,0x02301000 if i==0 else 0),(UC_ARM_REG_LR,0x023E0001)):cpu.reg_write(reg,value)
                cpu.emu_start(int(entry['hook'],16)|1,0x023E0000,count=150)
                self.assertEqual(cpu.reg_read(UC_ARM_REG_R1),{115:361,116:339,117:328}.get(item,item))
                self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),420 if i==0 else 328)
                self.assertEqual(cpu.reg_read(UC_ARM_REG_R2),0x12345678);self.assertEqual(cpu.reg_read(UC_ARM_REG_R3),0x02301000)
                self.assertEqual(bytes(cpu.mem_read(0x02301000,4)),struct.pack('<HH',item,1))

if __name__=='__main__':unittest.main()
