"""Cave rewards preserve native hidden-item dispatch, maps and old resources."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.narc
import ndspy.rom
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from mtmoon import patch as patch_cave
from mtmoon_story import patch as patch_story
from mtmoon_items import patch,VISIBLE,HIDDEN
from opening import events_decode
from parcel_quest import split_bank
from forest_progression import pickup
from viridian_tutorial import TABLE


class MtMoonItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-0017.nds'))
        patch_cave(cls.old);patch_story(cls.old)
        cls.new=ndspy.rom.NintendoDSRom(cls.old.save());cls.report=patch(cls.new)

    def arc(self,rom,path):return ndspy.narc.NARC(rom.files[rom.filenames.idOf(path)]).files

    def test_visible_rewards_use_verified_pickup_script_and_unique_saved_flags(self):
        for mapping in self.report['mappings']:
            g=events_decode(self.arc(self.new,'a/0/3/2')[mapping['event']]);bank=split_bank(self.arc(self.new,'a/0/1/2')[mapping['script']])
            oldlines=self.arc(self.old,'a/0/2/7')[mapping['original']['text']]
            from prototype import decode_messages
            msg=len(decode_messages(oldlines)[1])
            for reward in VISIBLE:
                if reward['map']!=mapping['map']:continue
                a=next(row for row in g[1] if struct.unpack_from('<H',row)[0]==reward['actor'])
                flag,entry=struct.unpack_from('<2H',a,8)
                self.assertEqual(flag,reward['flag']);self.assertEqual(struct.unpack_from('<2H',a,24),(reward['x'],reward['z']))
                code=pickup(reward['item'],flag,msg,reward['actor'])
                self.assertEqual(bank[entry-1][:len(code)],code)
                self.assertTrue(all(v==0 for v in bank[entry-1][len(code):]))
                msg+=2
        self.assertEqual(len({r['flag'] for r in VISIBLE}),3)

    def test_hidden_items_have_native_search_events_and_only_their_table_rows_change(self):
        addr=int(self.report['hidden_table'],16);at=addr-self.old.loadArm9().sections[1].ramAddress
        before,after=[bytes(r.loadArm9().sections[1].data) for r in (self.old,self.new)]
        expected=bytearray(before)
        for reward in HIDDEN:
            i=next(i for i in range(at,at+231*8,8) if struct.unpack_from('<H',before,i+6)[0]==reward['script']-8000)
            struct.pack_into('<H',expected,i,reward['item'])
            mapping=next(m for m in self.report['mappings'] if m['map']==reward['map'])
            g=events_decode(self.arc(self.new,'a/0/3/2')[mapping['event']])
            self.assertIn(struct.pack('<HHiiiH2x',reward['script'],2,reward['x'],reward['z'],0,4),g[0])
        self.assertEqual(after,bytes(expected))
        d=self.new.loadArm9().sections[0].data
        self.assertEqual(d.count(struct.pack('<I',addr)),2)
        self.assertEqual([(r['script'],r['flag']) for r in self.report['hidden']],[(8195,995),(8198,998)])

    def test_warps_story_triggers_actors_geometry_and_other_areas_unchanged(self):
        a,b=[r.loadArm9().sections[0].data for r in (self.old,self.new)]
        for m in range(540):
            if m not in (107,448):self.assertEqual(a[TABLE+m*24:TABLE+(m+1)*24],b[TABLE+m*24:TABLE+(m+1)*24])
        for mapping in self.report['mappings']:
            old=events_decode(self.arc(self.old,'a/0/3/2')[mapping['original']['event']]);new=events_decode(self.arc(self.new,'a/0/3/2')[mapping['event']])
            self.assertEqual(new[2:],old[2:]);self.assertEqual(new[1][:len(old[1])],old[1])
        for path in ('a/0/4/1','a/0/6/5','a/0/8/1'):
            self.assertEqual(self.old.files[self.old.filenames.idOf(path)],self.new.files[self.new.filenames.idOf(path)])

if __name__=='__main__':unittest.main()
