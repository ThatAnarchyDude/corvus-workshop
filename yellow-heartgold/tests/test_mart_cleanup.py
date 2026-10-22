"""Exercise cashier visibility through collection, exit, and full-bag retry."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from mart_cleanup import mart_init, upper_clerk
from parcel_quest import CLERK_STATE, GUIDE_HIDE, PARCEL_STATE, QUEST_INIT
from test_parcel_quest import QuestRun


class MartCleanupTests(unittest.TestCase):
    def test_guide_pending(self):
        r=QuestRun(mart_init(),variables={CLERK_STATE:1},flags={QUEST_INIT,GUIDE_HIDE}).run()
        self.assertNotIn(GUIDE_HIDE,r.flags)
        self.assertEqual(r.variables[CLERK_STATE],1)

    def test_guide_hidden_before_and_after_gift(self):
        for state in [0,2]:
            with self.subTest(state=state):
                r=QuestRun(mart_init(),variables={CLERK_STATE:state,PARCEL_STATE:1},flags={QUEST_INIT}).run()
                self.assertIn(GUIDE_HIDE,r.flags)
                self.assertEqual(r.variables[CLERK_STATE],state)
                self.assertEqual(r.variables[PARCEL_STATE],1)

    def test_repeated_entry_does_not_restore_collected_guide(self):
        r=QuestRun(mart_init(),variables={CLERK_STATE:2,PARCEL_STATE:2},flags={QUEST_INIT}).run()
        again=QuestRun(mart_init(),variables=r.variables,flags=r.flags).run()
        self.assertIn(GUIDE_HIDE,again.flags)
        self.assertEqual(again.variables[PARCEL_STATE],2)

    def test_door_approaches_have_no_auto_read_sign(self):
        import struct
        import ndspy.rom
        import ndspy.narc
        from mart_cleanup import PROJECT, TABLE
        from opening import events_decode
        rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-008.nds'))
        data=rom.loadArm9().sections[0].data
        arc=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/3/2')])
        eid=struct.unpack_from('<H',data,TABLE+50*24+16)[0]
        groups=events_decode(arc.files[eid])
        signs=[struct.unpack('<HHiiiH2x',row) for row in groups[0]]
        self.assertFalse(any(kind==1 and (x,z) in [(1032,263),(1042,254)]
                             for _,kind,x,z,_,_ in signs))
        self.assertTrue(any(script==5 and (x,z)==(1038,254) for script,_,x,z,_,_ in signs))
        self.assertIn((1032,262,501,0,0,0),[struct.unpack('<6H',row) for row in groups[2]])

    def test_only_upper_counter_clerk_uses_shop_script(self):
        import struct
        import ndspy.rom
        import ndspy.narc
        from mart_cleanup import PROJECT, TABLE
        from parcel_quest import split_bank, clerk_talk
        from opening import talk
        from prototype import decode_messages
        rom=ndspy.rom.NintendoDSRom.fromFile(str(PROJECT/'build/yellow-heartgold-prototype-008.nds'))
        data=rom.loadArm9().sections[0].data
        sid,_,tid=struct.unpack_from('<3H',data,TABLE+500*24+6)
        scripts=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/1/2')])
        texts=ndspy.narc.NARC(rom.files[rom.filenames.idOf('a/0/2/7')])
        bank=split_bank(scripts.files[sid]);messages=decode_messages(texts.files[tid])[1]
        self.assertTrue(bank[0].startswith(talk(len(messages)-1)))
        self.assertFalse(any(bank[0][len(talk(len(messages)-1)):]))
        self.assertTrue(bank[1].startswith(upper_clerk()))
        self.assertFalse(any(bank[1][len(upper_clerk()):]))
        self.assertIn(struct.pack('<HH',20,2048),bank[1])

    def test_ball_sales_unlock_only_after_delivery(self):
        for state in [0,1,2]:
            with self.subTest(state=state):
                r=QuestRun(upper_clerk(),variables={PARCEL_STATE:state},flags={QUEST_INIT},bag={459:1}).run()
                self.assertEqual(0x9A in r.flags,state==2)
