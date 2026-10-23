"""Verify all three gate lanes, the native portrait panel and pose continuity."""
import struct,sys,json,unittest
from collections import deque
from pathlib import Path
import ndspy.rom,ndspy.narc
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_SP,UC_ARM_REG_LR
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from opening_corrections import PROJECT,BARRIER_TILES,GATE_X,GATE_Z,SIDE_X,SIDE_Z,old_man,cells_decode,migration,GATE_MIGRATED
from viridian_tutorial import TUTORIAL_DONE,BLOCKER_HIDE,PASSED_HIDE
from test_viridian_tutorial import EventRun
from parcel_quest import PARCEL_STATE,BOUNDARY
from intro_polish import anim_decode,extract_blue

class GateProgression(unittest.TestCase):
    def test_every_missing_requirement_still_blocks(self):
        for parcel,flags in [(0,set()),(1,set()),(2,set()),(1,{0x6B})]:
            r=EventRun(old_man(12),variables={PARCEL_STATE:parcel},flags=flags,x=GATE_X,z=GATE_Z+1).run()
            self.assertEqual(r.tutorials,0);self.assertEqual(r.messages,[12]);self.assertNotIn(TUTORIAL_DONE,r.flags)
    def test_completed_demo_clears_mode_and_gate_and_does_not_repeat(self):
        r=EventRun(old_man(12),variables={PARCEL_STATE:2},flags={0x6B},x=GATE_X,z=GATE_Z+1).run()
        self.assertEqual(r.tutorials,1);self.assertIn(TUTORIAL_DONE,r.flags);self.assertEqual(r.variables[BOUNDARY],0)
        r=EventRun(old_man(12),variables=r.variables,flags=r.flags).run();self.assertEqual(r.tutorials,0)
    def test_migration_preserves_completed_tutorial(self):
        for flags in [set(),{TUTORIAL_DONE}]:
            r=EventRun(migration()+b'\x02\x00',flags=flags).run()
            self.assertIn(GATE_MIGRATED,r.flags);self.assertEqual(BLOCKER_HIDE in r.flags,TUTORIAL_DONE in flags);self.assertEqual(PASSED_HIDE in r.flags,TUTORIAL_DONE not in flags)

@unittest.skipUnless((PROJECT/'build/opening-corrections-report.json').exists(),'Requires prototype 011')
class BinaryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-010.nds'));cls.new=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-011.nds'));cls.report=json.loads((PROJECT/'build/opening-corrections-report.json').read_text())
    def arc(self,rom,p):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(p)]).files
    def walkable(self,rom):
        m=self.arc(rom,'a/0/4/1')[0];w,h,headers,heights,name=m[:5];at=5+name+w*h*(2*headers+heights);lands=self.arc(rom,'a/0/6/5')
        def read(x,z):return not struct.unpack_from('<H',lands[struct.unpack_from('<H',m,at+2*(z//32*w+x//32))[0]],20+2*((z%32)*32+x%32))[0]&0x8000
        return read
    def can_pass(self,rom,blocked=()):
        walk=self.walkable(rom);start=(GATE_X,238);goal=(GATE_X,232);todo=deque([start]);seen={start};blocked=set(blocked)
        while todo:
            x,z=todo.popleft()
            if (x,z)==goal:return True
            for dx,dz in [(0,-1),(0,1),(-1,0),(1,0)]:
                p=x+dx,z+dz
                if 1000<=p[0]<=1055 and 225<=p[1]<=245 and p not in seen and p not in blocked and walk(*p):seen.add(p);todo.append(p)
        return False
    def test_all_bypass_paths_are_closed_but_the_completed_gate_is_passable(self):
        self.assertTrue(self.can_pass(self.old,[(1032,235)]))
        self.assertFalse(self.can_pass(self.new,[(GATE_X,GATE_Z)]))
        self.assertTrue(self.can_pass(self.new,[(SIDE_X,SIDE_Z)]))
        self.assertTrue(self.walkable(self.new)(GATE_X,GATE_Z))
    def test_collision_changes_are_only_the_seven_barrier_tiles(self):
        before,after=self.walkable(self.old),self.walkable(self.new)
        changed={(x,z) for x in range(992,1056) for z in range(224,256) if before(x,z)!=after(x,z)}
        self.assertEqual(changed,set(BARRIER_TILES))
        old=self.arc(self.old,'a/0/6/5');new=self.arc(self.new,'a/0/6/5');self.assertEqual(old,new[:len(old)])
    def test_blue_is_added_to_the_frame_background_without_overwriting_players(self):
        a,b=self.arc(self.old,'a/1/2/0'),self.arc(self.new,'a/1/2/0');art,pal=extract_blue(PROJECT/'build/firered-source.gba');info=self.report['intro']
        for i in [12,16,17,21,55,56]:self.assertEqual(b[i],a[i])
        self.assertEqual(b[info['blue_character']][48:48+5120],a[32][48:48+5120])
        rendered=b[info['blue_character']][48+5120:]
        palettes={slot:struct.unpack_from('<16H',b[index],40) for slot,index in zip([6,10],info['blue_palettes'])}
        original=struct.unpack('<16H',pal)
        for tile in range(64):
            slot=10 if any(13 in [v&15,v>>4] for v in art[tile*32:(tile+1)*32]) else 6
            for byte in range(32):
                at=tile*32+byte
                for shift in [0,4]:
                    old_index=(art[at]>>shift)&15;new_index=(rendered[at]>>shift)&15
                    self.assertNotEqual(new_index,0)
                    self.assertEqual(palettes[slot][new_index],original[old_index] if old_index else 0x229B)
        for gender,index in enumerate(info['blue_screens']):
            tiles=struct.unpack_from('<1024H',b[index],36)
            for y in range(8):
                for x in range(8):self.assertEqual(tiles[(9+y)*32+4+gender*16+x]&1023,160+y*8+x)
        self.assertEqual(self.arc(self.old,'a/0/3/1'),self.arc(self.new,'a/0/3/1'))
    def test_sparkles_and_final_pose_share_marill_rest_transform(self):
        a,b=self.arc(self.old,'a/1/2/0'),self.arc(self.new,'a/1/2/0');seq=anim_decode(b[66]);self.assertEqual(seq[1],anim_decode(a[66])[1]);self.assertEqual(seq[3],anim_decode(a[66])[3]);self.assertEqual(seq[2][1]&65535,2)
        for element,duration in seq[2][3]:self.assertEqual(struct.unpack_from('<hh',element,4),(-44,70))
        cells=cells_decode(b[65]);self.assertEqual(cells[0][0][1]&511,472);self.assertEqual(cells[0][0][0]&255,184)
        for i in range(3,len(cells)):self.assertEqual(cells[i][:6],cells[0])
    def test_johto_and_lab_scripts_and_models_are_preserved(self):
        for p in ['a/0/1/2','a/0/3/2','a/0/8/1']:
            a,b=self.arc(self.old,p),self.arc(self.new,p);self.assertEqual(a,b[:len(a)])
        self.assertEqual(self.old.arm7,self.new.arm7)
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m!=50:self.assertEqual(a[0xF6BE0+m*24:0xF6BE0+(m+1)*24],b[0xF6BE0+m*24:0xF6BE0+(m+1)*24])
    def test_blue_helper_uses_the_selected_touch_frame_and_sub_bg_palette_for_both_genders(self):
        o=self.new.loadArm9Overlays()[53];native=[0x021E66E8,0x021E80B8,0x020078F0,0x02007914,0x02007938,0x0201BC28]
        for gender in [0,1]:
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x02000000,0x400000);c.mem_write(o.ramAddress,bytes(o.data));ctx,stop=0x02300000,0x023F0000;c.mem_write(ctx,struct.pack('<I',80));c.mem_write(ctx+0x134,struct.pack('<H',gender));c.mem_write(ctx+24,struct.pack('<I',0x02302000));calls=[]
            for at in native:c.mem_write(at,b'\x70\x47')
            def hook(cpu,at,size,data):
                if at==stop:cpu.emu_stop()
                if at in native:calls.append((at,tuple(cpu.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3])))
            c.hook_add(UC_HOOK_CODE,hook);c.reg_write(UC_ARM_REG_R0,ctx);c.reg_write(UC_ARM_REG_SP,0x023E0000);c.reg_write(UC_ARM_REG_LR,stop|1);c.emu_start(int(self.report['intro']['blue_panel'],16)|1,stop+2,count=300)
            self.assertEqual([v for at,v in calls if at==0x02007914],[(120,self.report['intro']['blue_screens'][gender],0x02302000,7)])
            self.assertEqual([v for at,v in calls if at==0x02007938],[(120,self.report['intro']['blue_palettes'][0],4,192),(120,self.report['intro']['blue_palettes'][1],4,320)])
            self.assertEqual([v[1:3] for at,v in calls if at==0x021E66E8],[(1,0)])
            self.assertEqual([v[1] for at,v in calls if at==0x021E80B8],[3])
            self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x023E0000)

    def test_wake_hook_changes_only_the_old_man_and_delegates_other_dummy_modes(self):
        main=self.new.loadArm9();previous=struct.unpack_from('<I',self.old.loadArm9().sections[0].data,0xFAD04)[0]&~1
        for mode in [0,2,5,6,7,8]:
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x01FF8000,0x8000);c.mem_map(0x02000000,0x400000);c.mem_write(main.sections[1].ramAddress,bytes(main.sections[1].data));ctx,fs,obj,stop=0x02300000,0x02301000,0x02302000,0x023F0000;c.mem_write(ctx+128,struct.pack('<I',fs));calls=[]
            for at in [0x020403AC,0x02041C70,0x0205E38C]:c.mem_write(at,b'\x70\x47')
            c.mem_write(previous,b'\x00\x20\x70\x47')
            def hook(cpu,at,size,data):
                if at==stop:cpu.emu_stop()
                elif at==0x020403AC:cpu.reg_write(UC_ARM_REG_R0,mode)
                elif at==0x02041C70:
                    calls.append(('object',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)));cpu.reg_write(UC_ARM_REG_R0,obj)
                elif at==0x0205E38C:calls.append(('sprite',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
                elif at==previous:calls.append(('delegate',cpu.reg_read(UC_ARM_REG_R0)))
            c.hook_add(UC_HOOK_CODE,hook);c.reg_write(UC_ARM_REG_R0,ctx);c.reg_write(UC_ARM_REG_R4,0x12345678);c.reg_write(UC_ARM_REG_SP,0x023E0000);c.reg_write(UC_ARM_REG_LR,stop|1);c.emu_start(int(self.report['wake_hook'],16)|1,stop+2,count=150)
            self.assertEqual(calls,[('object',fs,12),('sprite',obj,330)] if mode==8 else [('delegate',ctx)])
            self.assertEqual(c.reg_read(UC_ARM_REG_R4),0x12345678);self.assertEqual(c.reg_read(UC_ARM_REG_SP),0x023E0000)
