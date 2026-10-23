"""Execute the final ROM's TM dispatch, object refresh and daily flag reset."""
import json, os, struct, sys, unittest
from pathlib import Path
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from yellow_tms import MOVE_ENTRY, INDEX_ENTRY
from starter_properties import CMD_TABLE

class Native(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/os.environ.get('PROTOTYPE0023_ROM','build/yellow-heartgold-prototype-0023.nds')))
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0022.nds'))
        report=json.loads((PROJECT/'build/0023-development-report.json').read_text())
        cls.report=report['route24'];cls.moon=report.get('mtmoon_corrections')

    def cpu(self, rom=None):
        c=Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
        for sec in (rom or self.new).loadArm9().sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
        c.reg_write(UC_ARM_REG_SP,0x023F8000);c.reg_write(UC_ARM_REG_LR,0x023FF001)
        return c

    def test_tm45_dispatch_preserves_every_existing_item_lookup(self):
        for site,wanted in ((MOVE_ENTRY,86),(INDEX_ENTRY,105)):
            old,new=self.cpu(self.old),self.cpu()
            for item in range(537):
                result=[]
                for cpu in (old,new):
                    cpu.reg_write(UC_ARM_REG_R0,item);cpu.reg_write(UC_ARM_REG_LR,0x023FF001)
                    cpu.emu_start(site|1,0x023FF000,count=1000)
                    result.append(cpu.reg_read(UC_ARM_REG_R0))
                self.assertEqual(result[1],wanted if item==122 else result[0],(site,item))

    def test_refresh_chain_only_removes_the_scoped_actor_ids(self):
        reports=[self.report['refresh'],self.report['blue_bridge']['refresh']]
        if self.moon:reports.append(self.moon['refresh'])
        for report in reports:
            cpu=self.cpu();ctx,field,manager=0x02300000,0x02301000,0x02302000
            script=0x02303000;removed=[];asked=[]
            cpu.mem_write(ctx+8,struct.pack('<I',script));cpu.mem_write(ctx+128,struct.pack('<I',field))
            cpu.mem_write(field+60,struct.pack('<I',manager));cpu.mem_write(script,struct.pack('<I',int(report['marker'],16)))
            def hook(c,address,size,_):
                if address==0x0205EE60:
                    self.assertEqual(c.reg_read(UC_ARM_REG_R0),manager)
                    ident=c.reg_read(UC_ARM_REG_R1);asked.append(ident)
                    c.reg_write(UC_ARM_REG_R0,0 if ident==1 else 0x02304000+ident*256)
                elif address==0x0205E3CC:removed.append(c.reg_read(UC_ARM_REG_R0))
                else:return
                c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_R0,ctx)
            entry=struct.unpack_from('<I',self.new.loadArm9().sections[0].data,CMD_TABLE+4)[0]
            cpu.emu_start(entry,0x023FF000,count=2000)
            self.assertEqual(asked,report['removed_ids'])
            self.assertEqual(removed,[0x02304000+i*256 for i in asked if i!=1])
            self.assertEqual(struct.unpack('<I',cpu.mem_read(ctx+8,4))[0],script+4)

    def test_daily_reset_keeps_route24_flags_and_save_trailer(self):
        cpu=self.cpu();flags=0x02300000
        cpu.mem_write(flags,bytes([255])*1100+b'CHECKSUM')
        def hook(c,address,size,_):
            if address==0x020503D0:
                c.reg_write(UC_ARM_REG_R0,flags);c.reg_write(UC_ARM_REG_PC,c.reg_read(UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE,hook);cpu.reg_write(UC_ARM_REG_R0,0x02310000)
        cpu.emu_start(0x02040471,0x023FF000,count=1000)
        expected_flags=self.report['flags']+([self.moon['refresh_flag']] if self.moon else [])
        for flag in expected_flags:
            self.assertTrue(cpu.mem_read(flags+0x2E0+flag//8,1)[0] & (1<<(flag%8)))
        self.assertEqual(bytes(cpu.mem_read(flags+0x2E0+0xAA0//8,12)),bytes(12))
        self.assertEqual(bytes(cpu.mem_read(flags+1100,8)),b'CHECKSUM')

if __name__=='__main__':unittest.main()
