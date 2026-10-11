import json,struct,sys,unittest
from pathlib import Path
import ndspy.rom
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
class BlueProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0021-development-2.nds'));cls.main=cls.rom.loadArm9();r=json.loads((PROJECT/'build/0021-development-report.json').read_text())['cerulean']['rival'];cls.report={'hook':r['properties_hook'],'bytes':524}
    def execute(self,trainer,species,gender,rare_flags=None,shiny_roll=0,charm=False):
        c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
        for sec in self.main.sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
        setup,party,mon,save,flags,sp,stop=0x02300000,0x02301000,0x02302000,0x02303000,0x02304000,0x023F0000,0x023E0000
        if charm:
            e=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())['engine'];c.mem_write(int(e['save_pointer'],16),struct.pack('<I',save));c.mem_write(0x02308000+660,struct.pack('<HH',114,1))
        c.mem_write(setup+8,struct.pack('<I',party));c.mem_write(setup+28,struct.pack('<I',trainer));c.mem_write(setup+0x1C0,struct.pack('<I',save));c.mem_write(party+4,struct.pack('<I',4))
        if rare_flags is not None:c.mem_write(flags+0x440,struct.pack('<I',0x56781234));c.mem_write(flags+0x447,bytes([0x10|rare_flags]))
        rng=[0x77777777];initial=iter([0x1234,0x5678,shiny_roll,0]);seeded=[False];values={};pid=[];calls=[]
        def hook(cpu,address,size,_):
            if address==stop:cpu.emu_stop();return
            r0=cpu.reg_read(UC_ARM_REG_R0);r1=cpu.reg_read(UC_ARM_REG_R1);r2=cpu.reg_read(UC_ARM_REG_R2)
            if address==0x02073604:calls.append('native_party');result=0
            elif address==0x02074644:self.assertEqual(r0,party);self.assertEqual(r1,3);result=mon
            elif address==0x0207879C:result=0x02308000
            elif address==0x020503D0:self.assertEqual(r0,save);result=flags
            elif address==0x0201FD2C:result=rng[0]
            elif address==0x0201FD38:rng[0]=r0;seeded[0]=True;result=0
            elif address==0x0201FD44:
                if not seeded[0]:result=next(initial)
                else:rng[0]=(rng[0]*0x41C64E6D+0x6073)&0xffffffff;result=rng[0]>>16
            elif address==0x0206E540:self.assertEqual(r0,mon);result=species if r1==5 else gender
            elif address==0x0206EC40:self.assertEqual(r0,mon);values[r1]=struct.unpack('<I',cpu.mem_read(r2,4))[0];result=0
            elif address==0x0207235C:self.assertEqual(r0,mon);pid.append(r1);result=0
            elif address in [0x020722DC,0x0206E250]:self.assertEqual(r0,mon);result=0
            else:return
            cpu.reg_write(UC_ARM_REG_R0,result);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
        c.hook_add(UC_HOOK_CODE,hook)
        for reg,value in [(UC_ARM_REG_R0,setup),(UC_ARM_REG_R1,1),(UC_ARM_REG_R2,11),(UC_ARM_REG_R4,44),(UC_ARM_REG_R5,55),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,stop|1)]:c.reg_write(reg,value)
        c.emu_start(int(self.report['hook'],16)|1,stop,count=10000)
        for reg,value in [(UC_ARM_REG_R4,44),(UC_ARM_REG_R5,55),(UC_ARM_REG_R6,66),(UC_ARM_REG_R7,77),(UC_ARM_REG_SP,sp)]:self.assertEqual(c.reg_read(reg),value)
        return values,pid,calls,bytes(c.mem_read(flags+0x440,8)),rng[0]
    def test_rare_combinations_gender_and_rng_restore(self):
        for species in [54,133]:
            for gender in [0,1]:
                for rare in [0,32,64,96]:
                    v,pid,calls,saved,rng=self.execute(783,species,gender,rare)
                    p=pid[0];ot=v[7];xor=(p&65535)^(p>>16)^(ot&65535)^(ot>>16);self.assertEqual(xor<16,bool(rare&32));self.assertEqual(v[111],gender)
                    self.assertEqual((p&255)<(127 if species==54 else 31),bool(gender));ivs=[v[i] for i in range(70,76)];self.assertTrue(all(0<=x<=31 for x in ivs));self.assertEqual(all(x==31 for x in ivs),bool(rare&64));self.assertEqual(rng,0x77777777)
    def test_first_roll_can_produce_shiny_and_perfect_and_persists_between_encounters(self):
        v,pid,calls,saved,rng=self.execute(782,54,1,None);self.assertEqual(saved[:4],struct.pack('<I',0x56781234));self.assertEqual(saved[7]&0x70,0x70);self.assertEqual([v[i] for i in range(70,76)],[31]*6)
        later=self.execute(783,54,1,96);self.assertEqual(v,later[0]);self.assertEqual(pid,later[1])
    def test_blue_charm_uses_2048_while_perfect_iv_bonus_stays_independent(self):
        for charm in [False,True]:
            v,pid,calls,saved,rng=self.execute(782,54,0,None,2048,charm);self.assertEqual(bool(saved[7]&32),charm);self.assertTrue(saved[7]&64);self.assertEqual([v[i] for i in range(70,76)],[31]*6)
    def test_other_trainer_parties_are_untouched_and_no_thumb2(self):
        for trainer in [740,751,781,786]:
            v,pid,calls,saved,rng=self.execute(trainer,54,0,0);self.assertEqual(v,{});self.assertEqual(pid,[]);self.assertEqual(calls,['native_party'])
        at=int(self.report['hook'],16);code=self.main.sections[1].data[at-0x1FF8000:at-0x1FF8000+self.report['bytes']-16]
        self.assertFalse([i for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(code,at) if i.mnemonic.endswith('.w')])


if __name__=='__main__':unittest.main()
