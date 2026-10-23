"""Fossil quest decisions, native teams, movement and archive preservation."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.narc
import ndspy.rom
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon import patch as foundation
from mtmoon_story import patch, DATA, STAGE, CHOICE, FOSSILS, battle_script, fossil_script
from opening import events_decode
from parcel_quest import split_bank
from viridian_tutorial import TABLE


def run_script(code, *, stage=1, choice=0, yes=True, room=True, win=True, x=17, z=21):
    """Interpret script decisions only; native battle/movement have service doubles."""
    variables={STAGE:stage,CHOICE:choice,0x4000:x,0x4001:z};flags=set();items=[];hidden=[];moves=[];messages=[]
    pc=0;equal=False
    def half():
        nonlocal pc
        v=struct.unpack_from('<H',code,pc)[0];pc+=2;return v
    for _ in range(500):
        op=half()
        if op==2:return variables,items,hidden,moves,messages,flags
        elif op in (96,97,104,50,53,79,95,82):pass
        elif op in (190,191,45):
            v=code[pc];pc+=1
            if op==45:messages.append(v)
        elif op==17:
            var,value=half(),half();equal=variables.get(var,0)==value
        elif op==28:
            cond=code[pc];pc+=1;offset=struct.unpack_from('<i',code,pc)[0];pc+=4
            if (cond==1 and equal) or (cond==5 and not equal):pc+=offset
        elif op==22:
            offset=struct.unpack_from('<i',code,pc)[0];pc+=4;pc+=offset
        elif op==41:
            var,value=half(),half();variables[var]=value
        elif op==63:variables[half()]=0 if yes else 1
        elif op==125:
            item,qty,out=half(),half(),half();variables[out]=int(room)
            if room:items.append((item,qty))
        elif op==105:
            variables[half()]=x;variables[half()]=z
        elif op in (30,36):flags.add(half())
        elif op==101:hidden.append(half())
        elif op in (78,80,81):half()
        elif op==213:
            half();half();pc+=2
        elif op==220:variables[half()]=int(win)
        elif op==219:return variables,items,hidden,moves,messages,flags
        elif op==94:
            obj=half();offset=struct.unpack_from('<i',code,pc)[0];pc+=4;at=pc+offset;entries=[]
            while True:
                move,count=struct.unpack_from('<2H',code,at);at+=4
                if move==254:break
                entries.append((move,count))
            moves.append((obj,entries))
        else:raise AssertionError(f'Unexpected opcode {op} at {pc-2}')
    raise AssertionError('Script did not terminate')


class MtMoonStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        foundation(cls.old)
        cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)

    def arc(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def test_super_nerd_has_exact_yellow_team_and_moves(self):
        team=self.arc(self.new,'a/0/5/6')[self.report['trainer']]
        rows=list(struct.iter_unpack('<BB3H4H',team))
        self.assertEqual([(r[3],r[2]) for r in rows],[(88,12),(100,12),(109,12)])
        self.assertEqual([r[5:] for r in rows],[tuple(p['moves']) for p in DATA['fossil_boss']['team']])

    def test_both_choices_are_exclusive_and_bag_full_does_not_commit(self):
        for f in FOSSILS:
            with self.subTest(fossil=f['name']):
                code=fossil_script(f,0)
                variables,items,hidden,moves,messages,flags=run_script(code,x=f['x'])
                self.assertEqual(items,[(f['item'],1)])
                self.assertEqual((variables[STAGE],variables[CHOICE]),(2,f['choice']))
                self.assertEqual(set(hidden),{22,23})
                self.assertEqual(flags,{f['hide_flag'] for f in FOSSILS})
                # After choice, even direct interaction with the other object awards nothing.
                other=next(o for o in FOSSILS if o!=f)
                self.assertEqual(run_script(fossil_script(other,0),stage=2,choice=f['choice'])[1],[])
                for options in ({'room':False},{'yes':False},{'stage':0}):
                    result=run_script(code,x=f['x'],**options)
                    self.assertEqual(result[1:3],([],[]))
                    self.assertEqual(result[0][CHOICE],0)
                    self.assertEqual(result[0][STAGE],options.get('stage',1))

    def test_boss_win_commits_progress_loss_and_repeat_do_not(self):
        code=battle_script(self.report['trainer'],0)
        result=run_script(code,stage=0,win=True,x=12,z=20)
        self.assertEqual(result[0][STAGE],1)
        self.assertEqual(result[3][0],(21,[(14,3),(3,1)]))
        self.assertEqual(result[3][1],(21,[(15,3),(2,1)]))
        self.assertEqual(run_script(code,stage=0,win=False,x=12,z=20)[0][STAGE],0)
        self.assertEqual(run_script(code,stage=1)[3],[])

    def test_nerd_collects_other_fossil_with_visible_movement(self):
        for f in FOSSILS:
            result=run_script(fossil_script(f,0),x=f['x'],z=21)
            self.assertEqual(result[3][0],(255,[(13,1)]))
            other=next(o for o in FOSSILS if o!=f)
            self.assertEqual(result[3][1],(21,[(13,1),(15,other['x']-16),(0,1)]))
            # Right-side interaction need not move the player.
        self.assertEqual(run_script(fossil_script(FOSSILS[1],0),x=19,z=20)[3][0][0],21)

    def test_warps_geometry_other_maps_and_old_archives_are_preserved(self):
        oldd,newd=[r.loadArm9().sections[0].data for r in (self.old,self.new)]
        for m in range(540):
            if m not in (107,448):self.assertEqual(oldd[TABLE+m*24:TABLE+(m+1)*24],newd[TABLE+m*24:TABLE+(m+1)*24])
        for m in (107,448):
            a,b=[struct.unpack_from('<I',d,TABLE+m*24+20)[0] for d in (oldd,newd)]
            self.assertEqual(b>>20&31,9)
            self.assertEqual(a & ~(31<<20),b & ~(31<<20))
        self.assertEqual(oldd[TABLE+448*24:TABLE+448*24+20],newd[TABLE+448*24:TABLE+448*24+20])
        for path in ('a/0/1/2','a/0/3/2','a/0/5/5','a/0/5/6'):
            a,b=self.arc(self.old,path),self.arc(self.new,path);self.assertEqual(a,b[:len(a)])
        for path in ('a/0/4/1','a/0/6/5','a/0/8/1','a/0/3/7'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(path)],self.new.files[self.new.filenames.idOf(path)])
        oldg=events_decode(self.arc(self.old,'a/0/3/2')[self.report['original']['event']])
        newg=events_decode(self.arc(self.new,'a/0/3/2')[self.report['event']])
        self.assertEqual(newg[2],oldg[2]);self.assertEqual(newg[0],oldg[0])
        self.assertEqual(bytes(self.old.loadArm9().sections[1].data),bytes(self.new.loadArm9().sections[1].data))

    def test_entry_and_exit_are_story_checks_not_terrain_barriers(self):
        groups=events_decode(self.arc(self.new,'a/0/3/2')[self.report['event']])
        triggers=[struct.unpack('<Hhh5H',t) for t in groups[3]]
        self.assertEqual(triggers,[(self.report['boss_entry'],10,20,4,1,0,0,STAGE),
                                  (self.report['exit_entry'],20,22,5,2,0,0,STAGE),
                                  (self.report['exit_entry'],20,22,5,2,0,1,STAGE)])
        # Each Route 4 warp approach lies inside the conditional story region.
        self.assertTrue(20<=22<25 and 22<=23<24)

if __name__=='__main__':unittest.main()
