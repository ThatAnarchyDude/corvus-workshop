"""Check Yellow conversations and retained native services and archived assets."""
import struct
import sys
import unittest
from pathlib import Path

import ndspy.narc
import ndspy.rom

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_rom import PROJECT
from opening import events_decode, encode_text
from parcel_quest import split_bank, PH
from pewter_interiors import patch, DATA
from prototype import decode_messages
from viridian_tutorial import TABLE


class PewterInteriorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=str(PROJECT/'build/yellow-heartgold-prototype-015.nds')
        cls.old=ndspy.rom.NintendoDSRom.fromFile(source)
        cls.new=ndspy.rom.NintendoDSRom.fromFile(source)
        cls.report=patch(cls.new)

    def arc(self,r,path):return ndspy.narc.NARC(r.files[r.filenames.idOf(path)]).files

    def groups(self,r,m):
        d=r.loadArm9().sections[0].data
        return events_decode(self.arc(r,'a/0/3/2')[struct.unpack_from('<H',d,TABLE+m*24+16)[0]])

    def bank(self,r,m):
        d=r.loadArm9().sections[0].data
        return split_bank(self.arc(r,'a/0/1/2')[struct.unpack_from('<H',d,TABLE+m*24+6)[0]])

    def test_native_clinic_nurse_receptionists_pc_warps_and_init_are_unchanged(self):
        before,after=self.groups(self.old,475),self.groups(self.new,475)
        self.assertEqual(before[0],after[0])
        self.assertEqual(before[2:],after[2:])
        self.assertEqual(self.bank(self.old,475)[0],self.bank(self.new,475)[0])
        old={struct.unpack_from('<H',x)[0]:x for x in before[1]}
        new={struct.unpack_from('<H',x)[0]:x for x in after[1]}
        for obj in (0,1,2,3):self.assertEqual(old[obj],new[obj])
        self.assertNotIn(4,new)
        self.assertEqual(struct.unpack_from('<H',new[6],2)[0],341)
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        self.assertEqual(a[TABLE+475*24+8:TABLE+475*24+10],b[TABLE+475*24+8:TABLE+475*24+10])

    def test_upper_clerk_uses_standard_hg_shop_and_postgame_gifts_are_archived(self):
        code=self.bank(self.new,474)[0]
        self.assertIn(struct.pack('<3H',41,0x8004,1),code)
        self.assertIn(struct.pack('<2H',20,2048),code)
        self.assertNotIn(struct.pack('<2H',20,2067),code)
        self.assertEqual({struct.unpack_from('<H',a)[0] for a in self.groups(self.new,474)[1]},{0,1,2,3})
        self.assertEqual(self.groups(self.old,474)[2],self.groups(self.new,474)[2])

    def test_yellow_child_nerd_and_gentleman_use_corresponding_hg_sprites(self):
        for mapid,obj,sprite in ((472,2,315),(474,2,315),(474,3,317),(475,6,341),(477,1,315)):
            rows={struct.unpack_from('<H',a)[0]:a for a in self.groups(self.new,mapid)[1]}
            self.assertEqual(struct.unpack_from('<H',rows[obj],2)[0],sprite)

    def test_house_dialogue_contains_all_yellow_paragraphs_and_new_boy(self):
        d=self.new.loadArm9().sections[0].data
        tid=struct.unpack_from('<H',d,TABLE+472*24+10)[0]
        messages=decode_messages(self.arc(self.new,'a/0/2/7')[tid])[1]
        expected=decode_messages(encode_text([DATA['_PewterNidoranHouseMiddleAgedManText']],PH))[1][0]
        self.assertEqual(messages[0],expected)
        self.assertEqual(messages[0].count(0x25BC),3)
        self.assertIn(0x25BD,messages[0])
        self.assertEqual({struct.unpack_from('<H',a)[0] for a in self.groups(self.new,472)[1]},{0,1,2})
        self.assertEqual(self.groups(self.old,472)[2],self.groups(self.new,472)[2])

    def test_selection_sound_uses_se_command_and_nidoran_cry_matches_species(self):
        brock=self.bank(self.new,473)[0]
        self.assertEqual(brock[:4],struct.pack('<2H',73,1500))
        self.assertEqual(brock[4:],self.bank(self.old,473)[0][4:])
        self.assertIn(struct.pack('<3H',76,32,0),self.bank(self.new,472)[1])
        self.assertIn(struct.pack('<3H',76,39,0),self.bank(self.new,475)[3])

    def test_original_archives_graphics_and_every_other_map_header_are_preserved(self):
        for path in ('a/0/1/2','a/0/2/7','a/0/3/2'):
            a,b=self.arc(self.old,path),self.arc(self.new,path)
            self.assertEqual(a,b[:len(a)])
        for path in ('a/1/2/0','a/0/3/1','a/0/4/1','a/0/6/5','a/0/8/1','a/0/5/5','a/0/5/6'):
            self.assertEqual(self.arc(self.old,path),self.arc(self.new,path))
        a,b=self.old.loadArm9().sections[0].data,self.new.loadArm9().sections[0].data
        for m in range(540):
            if m not in (472,473,474,475,477):
                self.assertEqual(a[TABLE+24*m:TABLE+24*(m+1)],b[TABLE+24*m:TABLE+24*(m+1)])
        self.assertEqual(self.old.arm9OverlayTable,self.new.arm9OverlayTable)
        self.assertEqual(self.old.arm7,self.new.arm7)


if __name__=='__main__':unittest.main()
