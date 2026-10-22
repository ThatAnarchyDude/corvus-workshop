"""Exercise compiled guard scripts, drink consumption and Kanto resource boundaries."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from saffron_gates import guard_script,patch,GATES,DRINK_GIVEN
from build_rom import PROJECT
from viridian_tutorial import TABLE
import ndspy.rom,ndspy.narc

def execute(code,bag,flags=None,variables=None):
    bag=dict(bag);flags=set(flags or ());variables=dict(variables or {});at=0;equal=False;messages=[];moves=[]
    def value(v):return variables.get(v,0) if v>=0x4000 else v
    for _ in range(1000):
        op=struct.unpack_from('<H',code,at)[0];at+=2
        if op==2:return bag,flags,variables,messages,moves
        if op in (96,97,104,50,53,79,95):continue
        if op in (73,78):at+=2;continue
        if op in (190,191):at+=1;continue
        if op==45:messages.append(code[at]);at+=1;continue
        if op==32:f=struct.unpack_from('<H',code,at)[0];at+=2;equal=f in flags;continue
        if op==30:f=struct.unpack_from('<H',code,at)[0];at+=2;flags.add(f);continue
        if op in (128,126):
            item,n,result=struct.unpack_from('<3H',code,at);at+=6
            have=bag.get(item,0)>=n;variables[result]=int(have)
            if op==126 and have:bag[item]-=n
            continue
        if op in (17,41):
            a,b=struct.unpack_from('<2H',code,at);at+=4
            if op==17:equal=value(a)==value(b)
            else:variables[a]=value(b)
            continue
        if op in (22,28):
            condition=code[at] if op==28 else None
            if op==28:at+=1
            delta=struct.unpack_from('<i',code,at)[0];at+=4
            if condition is None or (condition==1 and equal) or (condition==5 and not equal):at+=delta
            continue
        if op==94:
            obj=struct.unpack_from('<H',code,at)[0];delta=struct.unpack_from('<i',code,at+2)[0];at+=6
            target=at+delta;movement=struct.unpack_from('<2H',code,target);moves.append((obj,*movement));continue
        raise AssertionError(f'Unexpected opcode {op} at {at-2}')
    raise AssertionError('Compiled guard script did not terminate')

class SaffronGates(unittest.TestCase):
    def test_no_drink_blocks_each_route_approach(self):
        for m,rect,direction in GATES:
            bag,flags,variables,messages,moves=execute(guard_script(direction,True),{17:1})
            self.assertNotIn(DRINK_GIVEN,flags);self.assertEqual(messages,[0]);self.assertEqual(moves,[(255,direction,2)])
            self.assertEqual(bag,{17:1})
    def test_each_drink_consumes_one_and_opens_shared_progress(self):
        for item in (30,31,32):
            bag,flags,variables,messages,moves=execute(guard_script(12,True),{item:2})
            self.assertEqual(bag[item],1);self.assertIn(DRINK_GIVEN,flags);self.assertFalse(any(0x4000 <= v < 0x8000 for v in variables))
            self.assertEqual(messages,[1,2]);self.assertEqual(moves,[])
    def test_priority_and_repeat_do_not_consume_more(self):
        result=execute(guard_script(12),{30:2,31:3,32:4});bag,flags,variables,_,_=result
        self.assertEqual(bag,{30:1,31:3,32:4})
        for _,_,direction in GATES:
            after=execute(guard_script(direction),bag,flags,variables)
            self.assertEqual(after[0],bag);self.assertEqual(after[3],[3])
            crossed=execute(guard_script(direction,True),bag,flags,variables)
            self.assertEqual(crossed[3:],([],[]))
    def test_only_kanto_gate_headers_and_appended_archives_change(self):
        before=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/0026-route5-foundation.nds'))
        after=ndspy.rom.NintendoDSRom(before.save());report=patch(after)
        a=before.loadArm9();b=after.loadArm9();allowed=set(range(a.codeSettingsOffs+20,a.codeSettingsOffs+24))
        for m,_,_ in GATES:allowed.update(range(TABLE+m*24,TABLE+(m+1)*24))
        self.assertTrue(all(i in allowed for i,(x,y) in enumerate(zip(a.sections[0].data,b.sections[0].data)) if x!=y))
        for x,y in zip(a.sections[1:],b.sections[1:]):self.assertEqual(x.data,y.data)
        paths=('a/0/1/2','a/0/2/7','a/0/3/2');ids={before.filenames.idOf(p) for p in paths}
        for p in paths:
            old=ndspy.narc.NARC(before.files[before.filenames.idOf(p)]);new=ndspy.narc.NARC(after.files[after.filenames.idOf(p)])
            self.assertEqual(old.files,new.files[:len(old.files)])
        for i,(x,y) in enumerate(zip(before.files,after.files)):
            if i not in ids:self.assertEqual(x,y)
        self.assertEqual(report['changed_map_headers'],[389,390,391,493])
        from opening import events_decode
        arc=ndspy.narc.NARC(after.files[after.filenames.idOf('a/0/3/2')])
        for gate in report['gates']:
            trigger=events_decode(arc.files[gate['event']])[3][0]
            self.assertEqual(struct.unpack_from('<2H',trigger,12),(0,0))


if __name__=='__main__':unittest.main()
