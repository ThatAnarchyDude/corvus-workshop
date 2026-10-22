"""Sale transaction decisions and preservation of native clinic services."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.narc
import ndspy.rom
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon_center import patch, salesman, SOLD
from opening import events_decode
from parcel_quest import split_bank
from viridian_tutorial import TABLE


def sale(*,money=1000,count=1,yes=True,sold=False,gift_ok=True):
    code=salesman(0);pc=0;variables={};equal=False;given=[];messages=[];flags={SOLD} if sold else set()
    def half():
        nonlocal pc
        v=struct.unpack_from('<H',code,pc)[0];pc+=2;return v
    def word():
        nonlocal pc
        v=struct.unpack_from('<I',code,pc)[0];pc+=4;return v
    for _ in range(200):
        op=half()
        if op==2:return money,given,flags,messages
        elif op in (96,97,104,50,53,79):pass
        elif op in (190,191,45):
            v=code[pc];pc+=1
            if op==45:messages.append(v)
        elif op==32:equal=half() in flags
        elif op==30:flags.add(half())
        elif op==17:
            var,value=half(),half();equal=variables.get(var,0)==value
        elif op==28:
            cond=code[pc];pc+=1;offset=struct.unpack_from('<i',code,pc)[0];pc+=4
            if (cond==1 and equal) or (cond==5 and not equal):pc+=offset
        elif op==63:variables[half()]=0 if yes else 1
        elif op==112:
            out=half();amount=word();variables[out]=int(money>=amount)
        elif op==111:money-=word()
        elif op==332:variables[half()]=count
        elif op==137:
            species,level,item,form,ability,out=[half() for _ in range(6)]
            variables[out]=int(gift_ok)
            if gift_ok:given.append((species,level))
        elif op in (73,78):half()
        else:raise AssertionError(f'Unknown opcode {op}')
    raise AssertionError('Script did not end')


class MtMoonCenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)

    def arc(self,r,p):return ndspy.narc.NARC(r.files[r.filenames.idOf(p)]).files

    def test_successful_sale_charges_once_after_receiving_level_five_magikarp(self):
        money,mons,flags,_=sale()
        self.assertEqual((money,mons,flags),(500,[(129,5)],{SOLD}))
        self.assertEqual(sale(money=500,sold=True)[:2],(500,[]))

    def test_decline_insufficient_money_full_party_or_failed_gift_never_charge(self):
        for options in ({'yes':False},{'money':499},{'count':6},{'gift_ok':False}):
            with self.subTest(options=options):
                money,mons,flags,_=sale(**options)
                self.assertEqual(money,options.get('money',1000));self.assertEqual(mons,[]);self.assertNotIn(SOLD,flags)

    def test_nurse_warps_and_link_staff_remain_native_and_pc_uses_shared_storage(self):
        d=self.old.loadArm9().sections[0].data;rec=TABLE+511*24
        oldsid,oldiid=struct.unpack_from('<2H',d,rec+6);oldev=struct.unpack_from('<H',d,rec+16)[0]
        oldg=events_decode(self.arc(self.old,'a/0/3/2')[oldev]);newg=events_decode(self.arc(self.new,'a/0/3/2')[self.report['event']])
        self.assertEqual(oldg[2],newg[2]);self.assertEqual(oldg[3],newg[3])
        self.assertEqual(oldg[1][1:4],newg[1][1:4])
        bank=split_bank(self.arc(self.new,'a/0/1/2')[self.report['script']])
        nurse=struct.unpack_from('<H',newg[1][0],10)[0]
        self.assertEqual(bank[nurse-1],split_bank(self.arc(self.old,'a/0/1/2')[oldsid])[0])
        self.assertEqual(struct.unpack_from('<H',self.new.loadArm9().sections[0].data,rec+8)[0],oldiid)
        # Native PC root is entry 11, with the same added item-storage code as Viridian.
        oldclinic=struct.unpack_from('<H',d,TABLE+501*24+6)[0]
        self.assertEqual(bank[10],split_bank(self.arc(self.old,'a/0/1/2')[oldclinic])[10])
        self.assertIn(struct.pack('<HHiiiH2x',11,0,11,12,0,0),newg[0])

    def test_only_route_three_center_header_changes_and_archives_are_appended(self):
        a,b=[r.loadArm9().sections[0].data for r in (self.old,self.new)]
        for m in range(540):
            if m!=511:self.assertEqual(a[TABLE+m*24:TABLE+(m+1)*24],b[TABLE+m*24:TABLE+(m+1)*24])
        for path in ('a/0/1/2','a/0/2/7','a/0/3/2'):
            before,after=self.arc(self.old,path),self.arc(self.new,path);self.assertEqual(before,after[:len(before)])
        for path in ('a/0/4/1','a/0/6/5'):self.assertEqual(self.old.files[self.old.filenames.idOf(path)],self.new.files[self.new.filenames.idOf(path)])

if __name__=='__main__':unittest.main()
