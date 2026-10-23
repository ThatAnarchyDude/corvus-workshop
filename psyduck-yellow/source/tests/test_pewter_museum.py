"""Museum admission, reward, service retirement and preservation boundaries."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.narc
import ndspy.rom
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from opening import events_decode
from parcel_quest import split_bank
from pewter_museum import patch, TICKET, AMBER, UPSTAIRS, STAIR_X, STAIR_Z
from viridian_tutorial import TABLE

class MuseumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=str(PROJECT/'build/yellow-heartgold-prototype-015.nds')
        cls.old=ndspy.rom.NintendoDSRom.fromFile(source)
        cls.new=ndspy.rom.NintendoDSRom.fromFile(source)
        cls.report=patch(cls.new)

    def arc(self,r,path):return ndspy.narc.NARC(r.files[r.filenames.idOf(path)]).files
    def test_admission_runs_as_interactive_frame_scene_not_synchronous_load_hook(self):
        files=self.arc(self.new,'a/0/1/2');r=self.report
        header=files[r['init']]
        self.assertEqual(header[:6],struct.pack('<BHHB',2,16,0,1))
        self.assertEqual(struct.unpack_from('<3H',header,11),(0x4000,0,15))
        bank=split_bank(files[r['script']])
        self.assertIn(struct.pack('<4H',112,0x800C,50,0),bank[14])
        self.assertIn(struct.pack('<3H',111,50,0),bank[14])
        self.assertIn(struct.pack('<2H',30,TICKET),bank[14])
        self.assertNotIn(struct.pack('<H',104),bank[14])
        self.assertEqual(bank[15].rstrip(b'\0')[-1:],b'\x02')
        for blocking in (45,94,174,176,254):
            self.assertNotIn(struct.pack('<H',blocking),bank[15])
        city=split_bank(files[r['city_script']])
        self.assertEqual(city[-1][:6],struct.pack('<3H',31,TICKET,2))

    def test_old_amber_is_single_reward_and_native_revival_is_not_active(self):
        bank=split_bank(self.arc(self.new,'a/0/1/2')[self.report['script']])
        self.assertIn(struct.pack('<4H',125,103,1,0x800C),bank[0])
        self.assertIn(struct.pack('<2H',32,AMBER),bank[0])
        self.assertIn(struct.pack('<2H',30,AMBER),bank[0])
        # Museum no longer calls HG's fossil species/give-revived-mon scripts.
        self.assertNotIn(struct.pack('<H',137),bank[0])

    def test_original_events_exhibits_warps_maps_and_archives_preserved(self):
        for path in ('a/0/1/2','a/0/2/7','a/0/3/2'):
            old,new=self.arc(self.old,path),self.arc(self.new,path)
            self.assertEqual(old,new[:len(old)])
        e=self.arc(self.new,'a/0/3/2');r=self.report
        old,new=events_decode(e[r['original_event']]),events_decode(e[r['floors']['lower_event']])
        self.assertEqual(old[2],new[2][:len(old[2])])
        self.assertEqual(old[3],new[3])
        self.assertEqual([x[2:] for x in old[0]],[x[2:] for x in new[0]])
        self.assertEqual({struct.unpack_from('<H',x)[0] for x in new[1]},set(range(5)))
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in (51,471,UPSTAIRS):self.assertEqual(a[TABLE+24*m:TABLE+24*(m+1)],b[TABLE+24*m:TABLE+24*(m+1)])
        for path in ('a/0/4/1','a/0/6/5','a/0/4/2','a/0/4/3','a/1/4/8','a/1/0/8'):
            a,b=self.arc(self.old,path),self.arc(self.new,path)
            self.assertEqual(a,b[:len(a)])
        self.assertEqual(self.old.files[self.old.filenames.idOf('a/0/8/1')],self.new.files[self.new.filenames.idOf('a/0/8/1')])

    def test_second_floor_has_reciprocal_native_stairs_and_no_exit_to_street(self):
        r=self.report['floors'];events=self.arc(self.new,'a/0/3/2')
        lower=events_decode(events[r['lower_event']]);upper=events_decode(events[r['upper_event']])
        self.assertEqual(struct.unpack('<6H',lower[2][1]),(STAIR_X,STAIR_Z,UPSTAIRS,0,0,0))
        self.assertEqual([struct.unpack('<6H',row) for row in upper[2]],[(STAIR_X,STAIR_Z,471,1,0,0)])
        self.assertEqual(len(upper[1]),5)
        lands=self.arc(self.new,'a/0/6/5')
        for record in r['geometry']:
            land=lands[record['land']]
            self.assertEqual(struct.unpack_from('<H',land,20+2*(STAIR_Z*32+STAIR_X))[0],0x5E)
            self.assertEqual(struct.unpack_from('<H',land,20+2*(STAIR_Z*32+STAIR_X+1))[0],0x8000)
            ps,bs=struct.unpack_from('<2I',land)
            prop_ids=[struct.unpack_from('<I',land,20+ps+i)[0] for i in range(0,bs,48)]
            self.assertIn(4,prop_ids)
        upstairs=lands[r['geometry'][1]['land']]
        self.assertEqual(struct.unpack_from('<H',upstairs,20+2*(19*32+10))[0],0x8000)

    def test_native_model_texture_and_metadata_tables_are_unchanged(self):
        for path in ('a/0/4/2','a/0/4/3','a/1/4/8','a/1/0/8'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(path)],
                             self.new.files[self.new.filenames.idOf(path)])
        self.assertEqual(self.report['floors']['upper_area'],44)

if __name__=='__main__':unittest.main()
