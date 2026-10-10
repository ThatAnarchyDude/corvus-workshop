"""Verify prototype 013 quest sequencing, archived data and native EXP ABI."""
import json,struct,sys,unittest
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from progression_cleanup import *
from parcel_quest import BALLS_GIVEN
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
TR={54:747,133:750,'54_male':747,'54_female':748,'133_male':749,'133_female':750}
from test_viridian_tutorial import EventRun

class BattleRun(EventRun):
    def __init__(self,*a,won=True,starter=133,gender=0,**kw):super().__init__(*a,**kw);self.won=won;self.starter=starter;self.gender=gender;self.trainers=[]
    def read(self,fmt='H'):
        v=super().read(fmt)
        if fmt=='H' and v==213:
            self.trainers.append(super().read());super().read();super().read('B');super().read('B');return 1
        if fmt=='H' and v==239:super().read();self.variables[super().read()]=self.gender;return 1
        if fmt=='H' and v==206:self.variables[super().read()]=self.starter;return 1
        if fmt=='H' and v==220:self.variables[super().read()]=int(self.won);return 1
        return v

class Sequencing(unittest.TestCase):
    def test_balls_are_mandatory_in_parcel_scene_and_not_duplicated(self):
        r=EventRun(oak_parcel(34,51,True),variables={PARCEL_STATE:1},flags={0x6A},bag={459:1},x=8,z=7).run()
        self.assertEqual(r.bag[4],5);self.assertIn(BALLS_GIVEN,r.flags);self.assertEqual(r.messages[-2:],[44,45]);self.assertLess(r.commands.index(291),r.commands.index(125))
        again=EventRun(oak_parcel(34,51,True),variables=r.variables,flags=r.flags,bag=r.bag,x=8,z=7).run();self.assertEqual(again.bag[4],5)
    def test_early_rival_requires_delivery_and_only_wins_complete_event(self):
        for parcel,done,won in [(0,False,True),(1,False,True),(2,True,True),(2,False,True),(2,False,False)]:
            flags={R22_DONE} if done else set();r=BattleRun(rival_scene(TR),variables={PARCEL_STATE:parcel},flags=flags,won=won,x=982,z=266).run();eligible=parcel==2 and not done
            self.assertEqual(r.trainers,[747] if eligible else []);self.assertEqual(R22_DONE in r.flags,done or eligible and won);self.assertEqual(R22_HIDE in r.flags,eligible and won)
    def test_route22_keeps_the_saved_lab_choice_for_all_starters(self):
        for starter,trainer in [(133,747),(54,750),(175,750)]:
            r=BattleRun(rival_scene(TR),variables={PARCEL_STATE:2},starter=starter,x=982,z=266).run();self.assertEqual(r.trainers,[trainer])
    def test_saved_random_species_and_opposite_gender_select_consistent_teams(self):
        for duck in [False,True]:
            for female in [False,True]:
                flags={RIVAL_PICKED}|({RIVAL_DUCK} if duck else set())|({RIVAL_FEMALE} if female else set())
                r=BattleRun(rival_scene(TR),variables={PARCEL_STATE:2},flags=flags,starter=175,x=982,z=266).run();species=54 if duck else 133;self.assertEqual(r.trainers,[TR[f'{species}_{"female" if female else "male"}']])
    def test_random_choice_records_only_after_received_and_uses_actual_togepi_gender(self):
        code=random_togepi_choice();needle=command(30,RIVAL_PICKED);at=code.index(needle);last=code.index(command(30,0x6A),at)
        for gender in [0,1]:
            r=BattleRun(code[at:last]+command(2),gender=gender).run();self.assertIn(RIVAL_PICKED,r.flags);self.assertNotIn(RIVAL_DUCK,r.flags);self.assertEqual(RIVAL_FEMALE in r.flags,gender==0)
        self.assertIn(command(239,0,0x800B),code);self.assertNotIn(command(239,0,0x800E),code)
        self.assertIn(command(380,0x800A,2),code);self.assertGreater(at,code.index(command(137,175,5,0,0,0,0x800C)))
    def test_long_lines_scroll_at_bottom_and_paragraphs_reset(self):
        words=decode_messages(encode_text(['One two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo twentythree twentyfour.'],PH))[1][0]
        self.assertGreater(words.count(0x25BD),2);first=words.index(0x25BD);self.assertNotIn(0xE000,words[first:]);self.assertEqual(repair_scroll([0xE000,0x25BD,0xE000,0x25BC,0xE000]),[0xE000,0x25BD,0x25BD,0x25BC,0xE000])

class Binary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-012.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-013.nds'));cls.report=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())
    def arc(self,rom,p):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]).files
    def test_original_hg_events_and_graphics_are_preserved(self):
        for p in ['a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6']:
            old,new=self.arc(self.old,p),self.arc(self.new,p);self.assertEqual(old,new[:len(old)])
        for p in ['a/1/2/0','a/0/3/1','a/0/6/5','a/0/8/1']:self.assertEqual(self.arc(self.old,p),self.arc(self.new,p))
        self.assertEqual(self.old.arm7,self.new.arm7)
    def test_route22_is_yellows_fixed_early_team(self):
        for key,trainer in self.report['rival_trainers'].items():
            species=int(key.split('_')[0]);override=2 if key.endswith('female') or key=='133' else 1
            row=self.arc(self.new,'a/0/5/5')[trainer];self.assertEqual((row[0],row[1],row[3]),(0,110,2));self.assertEqual(self.arc(self.new,'a/0/5/6')[trainer],struct.pack('<4H',0,9,21,0)+struct.pack('<BB3H',0,override,8,species,0))
    def test_only_authorized_map_headers_and_experience_overlay_change(self):
        old,new=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in [27,50,299,500,504,505,506]:self.assertEqual(old[TABLE+m*24:TABLE+(m+1)*24],new[TABLE+m*24:TABLE+(m+1)*24])
        a,b=self.old.loadArm9Overlays(),self.new.loadArm9Overlays()
        for i in a:
            if i not in [12,23,80]:self.assertEqual(a[i].data,b[i].data)
    def test_east_gate_triggers_before_guard_and_pushes_right(self):
        m=next(v for v in self.report['mappings'] if v['map']==299);g=events_decode(self.arc(self.new,'a/0/3/2')[m['event']]);self.assertEqual(struct.unpack('<Hhh5H',g[3][0]),(1,15,8,1,4,0,0,BOUNDARY));bank=split_bank(self.arc(self.new,'a/0/1/2')[m['script']]);self.assertIn(struct.pack('<2H',15,1),bank[0]);self.assertEqual(len(g[1]),3)
    def test_exp_hook_awards_exact_remaining_exp_and_preserves_other_battles(self):
        main=self.new.loadArm9();entry=int(self.report['experience']['hook'],16)
        for species,target in [(54,216),(133,216),(175,172)]:
            for trainer,slot,current in [(741,0,125 if species!=175 else 100),(742,0,140),(747,0,125),(744,0,100),(746,0,100),(741,1,125),(741,0,1000)]:
                c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
                for sec in main.sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
                mon,work,battle,sp,stop=0x02300000,0x02301000,0x02302000,0x023F0000,0x023E0000
                c.mem_write(work,struct.pack('<I',battle));c.mem_write(battle+0xA2,struct.pack('<H',trainer));c.mem_write(sp+0x38,struct.pack('<I',77))
                calls=[]
                def hook(cpu,address,size,_):
                    if address==stop:cpu.emu_stop();return
                    if address==0x0206E540:
                        field=cpu.reg_read(UC_ARM_REG_R1);self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),mon);result=current if field==8 else species;calls.append(field)
                    elif address==0x0206FD00:self.assertEqual(cpu.reg_read(UC_ARM_REG_R0),species);self.assertEqual(cpu.reg_read(UC_ARM_REG_R1),6);result=target
                    else:return
                    cpu.reg_write(UC_ARM_REG_R0,result);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
                c.hook_add(UC_HOOK_CODE,hook)
                for reg,value in [(UC_ARM_REG_R0,mon),(UC_ARM_REG_R1,8),(UC_ARM_REG_R2,0),(UC_ARM_REG_R4,work),(UC_ARM_REG_R5,slot),(UC_ARM_REG_R6,mon),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,stop|1)]:c.reg_write(reg,value)
                c.emu_start(entry|1,stop,count=500)
                eligible=741<=trainer<=746 and slot==0;self.assertEqual(struct.unpack('<I',c.mem_read(sp+0x38,4))[0],max(target-current,0) if eligible else 77)
                self.assertEqual(c.reg_read(UC_ARM_REG_R0),current)
                for reg,value in [(UC_ARM_REG_R4,work),(UC_ARM_REG_R5,slot),(UC_ARM_REG_R6,mon),(UC_ARM_REG_SP,sp)]:self.assertEqual(c.reg_read(reg),value)


class BlueProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-013.nds'));cls.main=cls.rom.loadArm9();cls.report=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())['blue_properties']
    def execute(self,trainer,species,gender,rare_flags=None,shiny_roll=0,charm=False):
        c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000)
        for sec in self.main.sections[:2]:c.mem_write(sec.ramAddress,bytes(sec.data))
        setup,party,mon,save,flags,sp,stop=0x02300000,0x02301000,0x02302000,0x02303000,0x02304000,0x023F0000,0x023E0000
        if charm:
            e=json.loads((PROJECT/'build/progression-cleanup-report.json').read_text())['engine'];c.mem_write(int(e['save_pointer'],16),struct.pack('<I',save));c.mem_write(0x02308000+660,struct.pack('<HH',114,1))
        c.mem_write(setup+8,struct.pack('<I',party));c.mem_write(setup+28,struct.pack('<I',trainer));c.mem_write(setup+0x1C0,struct.pack('<I',save));c.mem_write(party+4,struct.pack('<I',1 if trainer<747 else 2))
        if rare_flags is not None:c.mem_write(flags+0x440,struct.pack('<I',0x56781234));c.mem_write(flags+0x447,bytes([0x10|rare_flags]))
        rng=[0x77777777];initial=iter([0x1234,0x5678,shiny_roll,0]);seeded=[False];values={};pid=[];calls=[]
        def hook(cpu,address,size,_):
            if address==stop:cpu.emu_stop();return
            r0=cpu.reg_read(UC_ARM_REG_R0);r1=cpu.reg_read(UC_ARM_REG_R1);r2=cpu.reg_read(UC_ARM_REG_R2)
            if address==0x02073604:calls.append('native_party');result=0
            elif address==0x02074644:self.assertEqual(r0,party);self.assertEqual(r1,0 if trainer<747 else 1);result=mon
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
                    v,pid,calls,saved,rng=self.execute(748,species,gender,rare)
                    p=pid[0];ot=v[7];xor=(p&65535)^(p>>16)^(ot&65535)^(ot>>16);self.assertEqual(xor<8,bool(rare&32));self.assertEqual(v[111],gender)
                    self.assertEqual((p&255)<(127 if species==54 else 31),bool(gender));ivs=[v[i] for i in range(70,76)];self.assertTrue(all(0<=x<=31 for x in ivs));self.assertEqual(all(x==31 for x in ivs),bool(rare&64));self.assertEqual(rng,0x77777777)
    def test_first_roll_can_produce_shiny_and_perfect_and_persists_between_encounters(self):
        v,pid,calls,saved,rng=self.execute(744,54,1,None);self.assertEqual(saved[:4],struct.pack('<I',0x56781234));self.assertEqual(saved[7]&0x70,0x70);self.assertEqual([v[i] for i in range(70,76)],[31]*6)
        later=self.execute(748,54,1,96);self.assertEqual(v,later[0]);self.assertEqual(pid,later[1])
    def test_blue_charm_uses_2048_while_perfect_iv_bonus_stays_independent(self):
        for charm in [False,True]:
            v,pid,calls,saved,rng=self.execute(744,54,0,None,2048,charm);self.assertEqual(bool(saved[7]&32),charm);self.assertTrue(saved[7]&64);self.assertEqual([v[i] for i in range(70,76)],[31]*6)
    def test_other_trainer_parties_are_untouched_and_no_thumb2(self):
        for trainer in [740,751]:
            v,pid,calls,saved,rng=self.execute(trainer,54,0,0);self.assertEqual(v,{});self.assertEqual(pid,[]);self.assertEqual(calls,['native_party'])
        at=int(self.report['hook'],16);code=self.main.sections[1].data[at-0x1FF8000:at-0x1FF8000+self.report['bytes']-16]
        self.assertFalse([i for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(code,at) if i.mnemonic.endswith('.w')])

if __name__=='__main__':unittest.main()
