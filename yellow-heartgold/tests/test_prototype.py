import sys
import struct
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import prototype
import ndspy.rom
import ndspy.narc
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

class PrototypeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ndspy.rom.NintendoDSRom((prototype.PROJECT / 'build/yellow-heartgold-prototype-001.nds').read_bytes())

    def archive(self,path):
        return ndspy.narc.NARC(self.rom.files[self.rom.filenames.idOf(path)])

    def test_starters_match_display_and_creation(self):
        self.assertEqual(self.rom.loadArm9().sections[0].data.count(prototype.NEW),1)
        self.assertEqual(self.rom.loadArm9Overlays()[61].data.count(prototype.NEW),1)
        _,text=prototype.decode_messages(self.archive('a/0/2/7').files[190])
        mapping=__import__('json').loads((prototype.PROJECT/'tools/text-map.json').read_text())
        for i,name in enumerate(['PIKACHU','EEVEE','TOGEPI'],1):
            needle=[mapping[c] for c in name]
            self.assertTrue(any(text[i][p:p+len(needle)]==needle for p in range(len(text[i]))))

    def test_national_dex_call_keeps_existing_command_locations(self):
        base=ndspy.rom.NintendoDSRom(prototype.BASE.read_bytes())
        before=ndspy.narc.NARC(base.files[base.filenames.idOf('a/0/1/2')]).files[843]
        after=self.archive('a/0/1/2').files[843]
        old=struct.pack('<HHHBB',30,0x6A,605,3,2)
        at=before.index(old)
        self.assertEqual(after[:at],before[:at])
        self.assertEqual(after[at+8:len(before)],before[at+8:])
        self.assertEqual(struct.unpack_from('<H',after,at)[0],26)
        dest=at+6+struct.unpack_from('<i',after,at+2)[0]
        self.assertEqual(dest,len(before))
        self.assertEqual(after[dest:],old+struct.pack('<3H',291,30,107)+struct.pack('<HBH',477,1,0x800C)+struct.pack('<H',27))

    def test_follower_slot_zero_machine_code(self):
        data=self.rom.loadArm9().sections[0].data
        cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
        init=list(cs.disasm(data[0x69A34:0x69A3E],0x2069A34))
        self.assertEqual([(x.mnemonic,x.op_str) for x in init],[('adds','r0, r5, #0'),('movs','r1, #0'),('bl','#0x2074644'),('b','#0x2069a4c')])
        helper=list(cs.disasm(data[0x69A40:0x69A46],0x2069A40))
        self.assertEqual([(x.mnemonic,x.op_str) for x in helper],[('movs','r1, #0'),('ldr','r3, [pc, #4]'),('bx','r3')])
        self.assertEqual(struct.unpack_from('<I',data,0x69A48)[0],0x2074645)
        call=next(cs.disasm(data[0x69B9E:0x69BA2],0x2069B9E))
        self.assertEqual(call.op_str,'#0x2069a40')

    def test_togepi_can_attack_at_level_five(self):
        moves=self.archive('a/0/3/3').files[175]
        decoded=[(x>>9,x&511) for x in struct.unpack('<'+'H'*(len(moves)//2),moves) if x!=65535]
        self.assertIn((1,33),decoded)

    def test_first_rival_teams_and_branch_choices(self):
        parties=self.archive('a/0/5/6')
        for trainer,species in [(495,25),(496,133),(497,175)]:
            self.assertEqual(struct.unpack_from('<2H',parties.files[trainer],2),(5,species))
        script=self.archive('a/0/1/2').files[850]
        for species in [25,133]:self.assertEqual(script.count(struct.pack('<3H',17,0x800C,species)),1)

    def test_patch_sites_fail_closed(self):
        for bad in [b'',prototype.OLD*2]:
            with self.assertRaises(ValueError):prototype.replace_once(bad,prototype.OLD,prototype.NEW)
        with self.assertRaises(ValueError):prototype.thumb_bl(0,1)

if __name__=='__main__':unittest.main()
