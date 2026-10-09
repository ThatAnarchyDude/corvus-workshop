"""Verify native fixed stock dispatch and unchanged fallback ABI."""
import sys
import struct
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import ndspy.rom
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from yellow_marts import PROJECT, VIRIDIAN_STOCK, SENTINEL
from starter_properties import append_code


class YellowMartTests(unittest.TestCase):
    def execute(self,parameter):
        main=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-008.nds')).loadArm9()
        address,code=append_code(main,(PROJECT/'asm/yellow-mart.s').read_text())
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x01FF0000,0x10000);u.mem_map(0x02000000,0x400000)
        u.mem_write(address,code);ctx=0x02300000;ptr=ctx+0x100;field=ctx+0x200;task=ctx+0x300;stop=0x02310000
        u.mem_write(ctx+8,struct.pack('<I',ptr));u.mem_write(ctx+0x74,struct.pack('<I',task));u.mem_write(ctx+0x80,struct.pack('<I',field));u.mem_write(ptr,struct.pack('<H',0x8004));sp=0x023F0000
        regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6];saved=[0x4444,0x5555,0x6666]
        for reg,val in zip(regs,saved):u.reg_write(reg,val)
        u.reg_write(UC_ARM_REG_R0,ctx);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,stop|1)
        calls=[]
        def callback(uc,pc,size,user):
            if pc==0x0203FE2C:
                p=struct.unpack('<I',uc.mem_read(ctx+8,4))[0];uc.mem_write(ctx+8,struct.pack('<I',p+2));uc.reg_write(UC_ARM_REG_R0,0x8004)
            elif pc==0x020403AC:
                self.assertEqual(uc.reg_read(UC_ARM_REG_R0),field);self.assertEqual(uc.reg_read(UC_ARM_REG_R1),0x8004);uc.reg_write(UC_ARM_REG_R0,parameter)
            elif pc==0x02256D34:
                self.assertEqual([uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R3]],[task,field,0])
                self.assertEqual(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12)),b'\0'*12)
                stock=struct.unpack('<6H',uc.mem_read(uc.reg_read(UC_ARM_REG_R2),12));calls.append(stock)
            elif pc==0x02048060:
                self.assertEqual(uc.reg_read(UC_ARM_REG_R0),ctx);self.assertEqual(uc.reg_read(UC_ARM_REG_SP),sp)
                self.assertEqual(struct.unpack('<I',uc.mem_read(ctx+8,4))[0],ptr)
                calls.append('native');uc.reg_write(UC_ARM_REG_R0,1)
            elif pc==stop:uc.emu_stop();return
            else:return
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,callback);u.emu_start(address|1,stop,count=1000)
        self.assertEqual([u.reg_read(r) for r in regs],saved);self.assertEqual(u.reg_read(UC_ARM_REG_SP),sp);self.assertEqual(u.reg_read(UC_ARM_REG_R0),1)
        return calls

    def test_yellow_fixed_inventory(self):
        self.assertEqual(self.execute(SENTINEL),[tuple(VIRIDIAN_STOCK+[0xFFFF])])

    def test_existing_mart_parameters_preserve_native_handler(self):
        for parameter in [0,1,2,29,30,0x8004]:
            with self.subTest(parameter=parameter):self.assertEqual(self.execute(parameter),['native'])
