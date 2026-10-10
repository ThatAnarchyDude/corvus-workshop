"""Execute release Thumb hooks and validate Key Item and PC integration."""
import sys,struct,json,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from shiny_charm import ITEM,LEGENDARIES
from player_pc import script,SLOTS,INIT,EVOLUTION_INIT
from test_player_pc_storage import StorageRun
from test_starter_native import NativeStarterChecks

class CharmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-013.nds'));cls.main=cls.rom.loadArm9();cls.e=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())['engine']
    def cpu(self,owned=False,quantity=1,slot=0):
        c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
        for s in self.main.sections[:2]:c.mem_write(s.ramAddress,bytes(s.data))
        c.mem_write(int(self.e['save_pointer'],16),struct.pack('<I',0x02300000))
        if owned:c.mem_write(0x02301000+660+slot*4,struct.pack('<HH',ITEM,quantity))
        c.reg_write(UC_ARM_REG_SP,0x023F0000);c.reg_write(UC_ARM_REG_LR,0x023E0001)
        return c
    def execute(self,c,entry,stub=lambda c,a:False):
        def hook(cpu,a,size,_):
            if a==0x023E0000:cpu.emu_stop();return
            if a==0x0207879C:cpu.reg_write(UC_ARM_REG_R0,0x02301000)
            elif a==0x0206E250:stub(cpu,a)
            elif not stub(cpu,a):return
            cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
        c.hook_add(UC_HOOK_CODE,hook);c.emu_start(entry|1,0x023E0000,count=10000);self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x023F0000)
    def test_global_shiny_rendering_uses_fixed_4096_threshold(self):
        for xor in [0,7,8,15,16,31,32,4095,65535]:
            c=self.cpu();c.reg_write(UC_ARM_REG_R0,0);c.reg_write(UC_ARM_REG_R1,xor);self.execute(c,0x02070068);self.assertEqual(c.reg_read(UC_ARM_REG_R0),int(xor<16))
    def test_inventory_presence_requires_positive_quantity_in_key_item_pocket(self):
        for owned,qty,slot,wanted in [(False,1,0,0),(True,0,0,0),(True,1,0,1),(True,1,49,1)]:
            c=self.cpu(owned,qty,slot);self.execute(c,int(self.e['owned_hook'],16));self.assertEqual(c.reg_read(UC_ARM_REG_R0),wanted)
    def test_roll_halves_denominator_without_consuming_an_extra_rng_roll(self):
        for owned in [False,True]:
            for rng in [0,2047,2048,4095,4096,65535]:
                c=self.cpu(owned);calls=[]
                def stub(cpu,a):
                    if a!=0x0201FD44:return False
                    calls.append(a);cpu.reg_write(UC_ARM_REG_R0,rng);return True
                self.execute(c,int(self.e['shiny_roll_hook'],16),stub);v=c.reg_read(UC_ARM_REG_R0)&4095
                self.assertEqual(v,rng&(2047 if owned else 4095));self.assertEqual(len(calls),1)
    def test_charm_boost_only_changes_extra_eligible_new_pids(self):
        for owned in [False,True]:
            for xor in [0,7,8,15,16,17,31,32,4095,65535]:
                c=self.cpu(owned);pid=(xor<<16)|128;mon=0x02302000;c.mem_write(mon,struct.pack('<I',pid));c.reg_write(UC_ARM_REG_R0,mon);pids=[];stats=[]
                def stub(cpu,a):
                    if a==0x0206E540:cpu.reg_write(UC_ARM_REG_R0,128);return True
                    if a==0x0207235C:pids.append(cpu.reg_read(UC_ARM_REG_R1));return True
                    if a==0x0206E250:stats.append(cpu.reg_read(UC_ARM_REG_R0));return True
                    return False
                self.execute(c,int(self.e['charm_boost_hook'],16),stub)
                expected=owned and 16<=xor<32
                self.assertEqual(pids,[pid^0x100000] if expected else []);self.assertEqual(stats,[mon] if expected else [])
                if pids:self.assertLess((pids[0]>>16)^(pids[0]&65535)^128,16)
    def test_only_hgss_obtainable_legendaries_receive_guaranteed_ivs(self):
        for species in range(1,494):
            c=self.cpu();c.reg_write(UC_ARM_REG_R0,species);self.execute(c,int(self.e['legendary_hook'],16));self.assertEqual(bool(c.reg_read(UC_ARM_REG_R0)),species in LEGENDARIES)
    def test_constructor_preserves_all_arguments_and_forces_legendary_ivs(self):
        for species in [54,133,175,144,150,489,490,493]:
            c=self.cpu();mon=0x02302000;c.reg_write(UC_ARM_REG_R0,mon);c.reg_write(UC_ARM_REG_R1,species);c.reg_write(UC_ARM_REG_R2,5);c.reg_write(UC_ARM_REG_R3,32);c.mem_write(0x023F0000,struct.pack('<4I',1,0x12345678,0,0xabcdef01));calls=[]
            def stub(cpu,a):
                if a!=int(self.e['generation_trampoline'],16):return False
                calls.append(1);self.assertEqual([cpu.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]],[mon,species,5,31 if species in LEGENDARIES else 32]);self.assertEqual(bytes(cpu.mem_read(cpu.reg_read(UC_ARM_REG_SP),16)),struct.pack('<4I',1,0x12345678,0,0xabcdef01));return True
            self.execute(c,0x0206DE38,stub);self.assertEqual(len(calls),1)
        a=int(self.e['generation_trampoline'],16);raw=self.main.sections[1].data[a-0x1ff8000+12:a-0x1ff8000+16];i=list(Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(raw,a+12))[0];self.assertEqual(i.op_str,'#0x206dce4')
    def test_inheritance_and_combined_iv_setters_cannot_replace_perfect_legendary_ivs(self):
        for species in [133,144,483,487,489,490,493]:
            for field in [70,71,72,73,74,75,175]:
                c=self.cpu();mon=0x02302000;value=0x02303000;c.mem_write(value,struct.pack('<I',7));c.reg_write(UC_ARM_REG_R0,mon);c.reg_write(UC_ARM_REG_R1,field);c.reg_write(UC_ARM_REG_R2,value);values=[]
                def stub(cpu,a):
                    if a==0x0206E540:cpu.reg_write(UC_ARM_REG_R0,species);return True
                    if a==int(self.e['setter_trampoline'],16):values.append(struct.unpack('<I',cpu.mem_read(cpu.reg_read(UC_ARM_REG_R2),4))[0]);return True
                    return False
                self.execute(c,0x0206EC40,stub);self.assertEqual(values,[7 if species not in LEGENDARIES else 0x3fffffff if field==175 else 31])
    def test_pending_generation_is_resolved_once_and_never_reclassifies_existing_pokemon(self):
        for pending in [False,True]:
            c=self.cpu(True);mon=0x02302000;pid=(16<<16)|128;c.mem_write(mon,struct.pack('<IH',pid,8 if pending else 0));c.reg_write(UC_ARM_REG_R0,mon);calls=[]
            def stub(cpu,a):
                if a==0x0206E540:cpu.reg_write(UC_ARM_REG_R0,128);return True
                if a==0x0207235C:calls.append(cpu.reg_read(UC_ARM_REG_R1));return True
                return False
            self.execute(c,int(self.e['pending_hook'],16),stub);self.assertEqual(calls,[pid^0x100000] if pending else []);self.assertEqual(struct.unpack('<H',c.mem_read(mon+4,2))[0]&8,0)
    def test_previously_locked_paths_skip_rejection_for_both_shiny_results(self):
        for site,target in [(0x0206D15A,0x0206D170),(0x0204C05A,0x0204C074),(0x0204B8E2,0x0204B8E4)]:
            for zero in [False,True]:
                c=self.cpu();c.reg_write(UC_ARM_REG_CPSR,c.reg_read(UC_ARM_REG_CPSR)|(1<<30) if zero else c.reg_read(UC_ARM_REG_CPSR)&~(1<<30));c.emu_start(site|1,target,count=1);self.assertEqual(c.reg_read(UC_ARM_REG_PC),target)
        o=self.rom.loadArm9Overlays()[80]
        for site in [0x0222A020,0x022367EA]:
            c=self.cpu();c.mem_write(o.ramAddress,bytes(o.data));c.reg_write(UC_ARM_REG_CPSR,c.reg_read(UC_ARM_REG_CPSR)|(1<<30));c.emu_start(site|1,site+2,count=1);self.assertEqual(c.reg_read(UC_ARM_REG_PC),site+2)
    def test_npc_trade_roll_preserves_gender_and_ordinary_fixed_personality(self):
        for owned in [False,True]:
            for rng in [0,1,2048,4096,65535]:
                c=self.cpu(owned);mon=0x02302000;pid=0x12345678;ot=0xabcdef12;c.mem_write(mon,struct.pack('<I',pid));c.reg_write(UC_ARM_REG_R0,mon);updates=[];rolls=[]
                def stub(cpu,a):
                    if a==0x0201FD44:rolls.append(1);cpu.reg_write(UC_ARM_REG_R0,rng);return True
                    if a==0x0206E540:cpu.reg_write(UC_ARM_REG_R0,ot);return True
                    if a==0x0207235C:updates.append(cpu.reg_read(UC_ARM_REG_R1));return True
                    if a==0x0206E250:return True
                    return False
                self.execute(c,int(self.e['npc_trade_hook'],16),stub);shiny=rng%(2048 if owned else 4096)==0
                self.assertEqual(len(rolls),1);self.assertEqual(len(updates),int(shiny));self.assertEqual(c.reg_read(UC_ARM_REG_R0),0)
                if updates:self.assertEqual(updates[0]&65535,pid&65535);self.assertEqual((updates[0]>>16)^(updates[0]&65535)^(ot>>16)^(ot&65535),0)
    def test_trade_return_identity_accepts_only_original_and_exact_generated_variants(self):
        canonical=0x12345678;ot=0xabcdef12;low=canonical&65535;shiny=((((ot>>16)^(ot&65535)^low)&65535)<<16)|low
        for pid,expected in [(canonical,canonical),(shiny,canonical),(shiny^0x100000,canonical),(shiny^0x200000,shiny^0x200000),(shiny^1,shiny^1)]:
            c=self.cpu();trade=0x02303000;c.mem_write(trade+32,struct.pack('<I',ot));c.mem_write(trade+56,struct.pack('<I',canonical));c.reg_write(UC_ARM_REG_R5,trade)
            def stub(cpu,a):
                if a!=0x0206E540:return False
                cpu.reg_write(UC_ARM_REG_R0,pid);return True
            self.execute(c,int(self.e['trade_identity_hook'],16),stub);self.assertEqual(c.reg_read(UC_ARM_REG_R0),expected);self.assertEqual(c.reg_read(UC_ARM_REG_R5),trade)
    def test_item_is_a_passive_protected_key_item(self):
        d=self.main.sections[0].data;idx=struct.unpack_from('<H',d,0x100194+ITEM*8)[0];a=ndspy.narc.NARC(self.rom.files[self.rom.filenames.idOf('a/0/1/7')]);row=a.files[idx];bits=struct.unpack_from('<H',row,8)[0]
        self.assertEqual((bits>>7)&15,7);self.assertTrue(bits&32);self.assertEqual(row[10:14],bytes(4))
    def test_pc_contains_one_charm_and_upgrades_old_save_without_restocking(self):
        first=StorageRun([1]);first.code=script(evolution_items=True,shiny_charm=True);first.run()
        self.assertEqual([(first.variables.get(i),first.variables.get(q)) for i,q in SLOTS][-1],(ITEM,1));self.assertIn(0xB3B,first.flags)
        again=StorageRun([1],variables=first.variables,flags=first.flags);again.code=script(evolution_items=True,shiny_charm=True);again.run();self.assertEqual(again.variables,first.variables)
    def test_pc_cannot_toss_the_charm(self):
        r=StorageRun([0,0,2,9,0,3,250,1]);r.code=script(evolution_items=True,shiny_charm=True);r.run();self.assertIn(40,r.messages);self.assertEqual((r.variables[SLOTS[9][0]],r.variables[SLOTS[9][1]]),(ITEM,1))

class PlayerOdds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-013.nds')).loadArm9();cls.report={'starter_hook':'0x1ff8620'}
        # The existing harness maps its synthetic save at 02302000. Redirect
        # only the inventory global's storage address into that mapped range.
        e=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())['engine'];old=struct.pack('<I',int(e['save_pointer'],16));cls.main.sections[1].data=bytearray(cls.main.sections[1].data).replace(old,struct.pack('<I',0x02306000))
    execute=NativeStarterChecks.execute
    def test_player_shiny_roll_uses_4096_and_perfect_bonus_remains_independent_16384(self):
        for species in [54,133,175]:
            for shiny,perfect in [(0,0),(4096,16384),(1,0),(4095,16383)]:
                v=self.execute(species,shiny,perfect,0);p,o=v[0],v[7];self.assertEqual(((p>>16)^(p&65535)^(o>>16)^(o&65535))<16,shiny%4096==0);self.assertEqual(all(v[i]==31 for i in range(70,76)),perfect%16384==0)

    def test_player_charm_uses_2048_and_preserves_perfect_bonus(self):
        e=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())['engine'];at=int(e['owned_hook'],16)-0x1ff8000;old=bytes(self.main.sections[1].data[at:at+4]);self.main.sections[1].data[at:at+4]=bytes.fromhex('01207047')
        try:
            for species in [54,133,175]:
                v=self.execute(species,2048,16384,0);p,o=v[0],v[7];self.assertLess((p>>16)^(p&65535)^(o>>16)^(o&65535),16);self.assertEqual([v[i] for i in range(70,76)],[31]*6)
        finally:self.main.sections[1].data[at:at+4]=old
